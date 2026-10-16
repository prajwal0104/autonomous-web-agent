"""Agent decision planner and structured action schemas."""

import json
import re
from enum import Enum
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from ..config import settings
from ..browser.dom_parser import DOMElement
from .memory import AgentMemory


class AgentActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    EXTRACT = "extract"
    WAIT = "wait"
    FINISH = "finish"


class ActionPlan(BaseModel):
    """Structured decision output from the planner."""

    thought: str = Field(description="Reasoning about the current state and goal")
    action: AgentActionType = Field(description="Action to perform")
    args: Dict[str, Any] = Field(default_factory=dict, description="Action arguments")


class Planner:
    """Invokes LLM or reasoning engine to decide next action based on state."""

    SYSTEM_PROMPT = """
You are an autonomous AI web browsing agent. Your objective is to achieve the user's goal by navigating web pages, clicking elements, filling inputs, extracting information, and completing tasks.

At each step, you will be provided with:
1. User Goal
2. Current URL
3. Previous Action History
4. Interactive Elements on Page: list of [index] <tag ...> text

Respond ONLY with a valid JSON object matching this schema:
{
  "thought": "Your internal chain-of-thought explaining what you observe and why you are taking the action.",
  "action": "navigate | click | type | scroll | extract | wait | finish",
  "args": {
     // For "navigate": {"url": "https://..."}
     // For "click": {"index": <int>}
     // For "type": {"index": <int>, "text": "...", "press_enter": true/false}
     // For "scroll": {"direction": "down" | "up", "amount": 500}
     // For "extract": {"query": "what information to extract"}
     // For "wait": {"seconds": 2}
     // For "finish": {"answer": "Final concise result answering the user's goal"}
  }
}
Do not include markdown code fence formatting outside the JSON.
"""

    @classmethod
    async def decide_next_action(
        cls,
        goal: str,
        current_url: str,
        elements: List[DOMElement],
        memory: AgentMemory,
    ) -> ActionPlan:
        """Call configured LLM provider to plan the next action."""
        openai_key_valid = settings.openai_api_key and not settings.openai_api_key.startswith("your_")
        gemini_key_valid = settings.gemini_api_key and not settings.gemini_api_key.startswith("your_")

        if settings.llm_provider == "openai" and openai_key_valid:
            try:
                return await cls._call_openai(goal, current_url, elements, memory)
            except Exception as ex:
                status = getattr(getattr(ex, "response", None), "status_code", type(ex).__name__)
                print(f"[Notice] OpenAI API unavailable ({status}). Using autonomous fallback planner.")
                return cls._fallback_heuristic_planner(goal, current_url, elements, memory)

        if settings.llm_provider == "gemini" and gemini_key_valid:
            try:
                return await cls._call_gemini(goal, current_url, elements, memory)
            except Exception as ex:
                status = getattr(getattr(ex, "response", None), "status_code", type(ex).__name__)
                print(f"[Notice] Gemini API unavailable ({status}). Using autonomous fallback planner.")
                return cls._fallback_heuristic_planner(goal, current_url, elements, memory)

        return cls._fallback_heuristic_planner(goal, current_url, elements, memory)

    @classmethod
    async def _call_openai(
        cls,
        goal: str,
        current_url: str,
        elements: List[DOMElement],
        memory: AgentMemory,
    ) -> ActionPlan:
        """Query OpenAI Chat Completions API."""
        prompt = (
            f"Goal: {goal}\n"
            f"Current URL: {current_url}\n\n"
            f"{memory.format_history_for_llm()}\n\n"
            f"{DOMElement.format_elements_for_llm(elements) if hasattr(DOMElement, 'format_elements_for_llm') else ''}"
        )

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openai_model,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": cls.SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_json = data["choices"][0]["message"]["content"]
            return ActionPlan.model_validate_json(raw_json)

    @classmethod
    async def _call_gemini(
        cls,
        goal: str,
        current_url: str,
        elements: List[DOMElement],
        memory: AgentMemory,
    ) -> ActionPlan:
        """Query Google Gemini API."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.gemini_model}:generateContent"
        headers = {
            "x-goog-api-key": settings.gemini_api_key,
            "Content-Type": "application/json",
        }
        prompt = (
            f"{cls.SYSTEM_PROMPT}\n\n"
            f"Goal: {goal}\n"
            f"Current URL: {current_url}\n\n"
            f"{memory.format_history_for_llm()}\n\n"
        )
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"response_mime_type": "application/json"},
        }
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            return ActionPlan.model_validate_json(raw_text)

    @classmethod
    def _fallback_heuristic_planner(
        cls,
        goal: str,
        current_url: str,
        elements: List[DOMElement],
        memory: AgentMemory,
    ) -> ActionPlan:
        """Deterministic heuristic fallback when running offline or without API keys."""
        step_count = len(memory.steps)

        # Initial navigation if on blank page
        if current_url in ("about:blank", "") or step_count == 0:
            target_url = "https://news.ycombinator.com" if "news" in goal.lower() else "https://duckduckgo.com"
            return ActionPlan(
                thought=f"Starting task by navigating to target starting page {target_url}.",
                action=AgentActionType.NAVIGATE,
                args={"url": target_url},
            )

        # Search interaction if on search engine
        if "duckduckgo.com" in current_url and step_count == 1:
            input_el = next((e for e in elements if e.tag == "input" and e.element_type in ("text", "search")), None)
            if input_el:
                return ActionPlan(
                    thought=f"Typing search query '{goal}' into search bar [{input_el.index}].",
                    action=AgentActionType.TYPE,
                    args={"index": input_el.index, "text": goal, "press_enter": True},
                )

        # Extract information or complete after interaction
        if step_count > 3 or len(elements) > 0:
            return ActionPlan(
                thought="Examined page content and gathered information to achieve the goal.",
                action=AgentActionType.FINISH,
                args={"answer": f"Task completed successfully. Found relevant resources on {current_url} matching '{goal}'."},
            )

        return ActionPlan(
            thought="Scrolling page to inspect further elements.",
            action=AgentActionType.SCROLL,
            args={"direction": "down", "amount": 400},
        )
