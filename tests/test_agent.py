"""Unit tests for agent modules, DOM parser, and planner."""

import pytest
from src.browser.dom_parser import DOMElement, DOMParser
from src.agent.memory import AgentMemory, StepRecord
from src.agent.planner import ActionPlan, AgentActionType, Planner


def test_dom_element_summary():
    """Verify DOMElement renders clean summary string."""
    el = DOMElement(
        index=1,
        tag="button",
        text="Submit Order",
        selector='[data-agent-idx="1"]',
    )
    summary = el.summary()
    assert "[1] <button>" in summary
    assert "Submit Order" in summary


def test_agent_memory():
    """Verify memory accurately records steps and renders history."""
    mem = AgentMemory(goal="Search for flight prices")
    step = StepRecord(
        step_number=1,
        url="https://example.com",
        action_type="navigate",
        action_args={"url": "https://example.com"},
        thought="Navigating to homepage",
        observation="Loaded successfully",
        success=True,
    )
    mem.add_step(step)
    assert len(mem.steps) == 1
    history = mem.format_history_for_llm()
    assert "Step 1: [NAVIGATE]" in history
    assert "Navigating to homepage" in history


def test_planner_fallback_action():
    """Verify fallback planner yields deterministic action plan."""
    mem = AgentMemory(goal="Read tech news")
    plan = Planner._fallback_heuristic_planner(
        goal="Read tech news",
        current_url="about:blank",
        elements=[],
        memory=mem,
    )
    assert plan.action == AgentActionType.NAVIGATE
    assert "news.ycombinator.com" in plan.args["url"]


def test_action_plan_json_serialization():
    """Verify ActionPlan validates properly."""
    data = {
        "thought": "Clicking the login button",
        "action": "click",
        "args": {"index": 3},
    }
    plan = ActionPlan.model_validate(data)
    assert plan.action == AgentActionType.CLICK
    assert plan.args["index"] == 3
