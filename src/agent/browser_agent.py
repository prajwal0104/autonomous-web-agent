"""Autonomous Browser Agent core execution loop."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from rich.console import Console
from rich.panel import Panel

from ..config import settings
from ..browser.controller import BrowserController
from ..tools.extractor import DataExtractor
from .memory import AgentMemory, StepRecord
from .planner import ActionPlan, AgentActionType, Planner

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()


class AutonomousBrowserAgent:
    """End-to-end agent orchestrator for goal-driven web automation."""

    def __init__(self, goal: str, headless: Optional[bool] = None):
        self.goal = goal
        self.browser = BrowserController(headless=headless)
        self.memory = AgentMemory(goal=goal)
        self.final_answer: Optional[str] = None

    async def run(self, max_steps: Optional[int] = None) -> str:
        """Run the autonomous agent loop until the goal is achieved or steps exhausted."""
        steps_limit = max_steps or settings.max_steps
        console.print(
            Panel.fit(
                f"[bold cyan]Goal:[/bold cyan] {self.goal}\n"
                f"[bold green]Provider:[/bold green] {settings.llm_provider}\n"
                f"[bold yellow]Headless Mode:[/bold yellow] {self.browser.headless}",
                title="[bold blue]Autonomous Web Agent[/bold blue]",
            )
        )

        try:
            await self.browser.start()

            for step_idx in range(1, steps_limit + 1):
                current_url = self.browser.page.url
                elements = await self.browser.refresh_elements()

                console.print(f"\n[bold magenta]─── Step {step_idx}/{steps_limit} ───[/bold magenta] [dim]({current_url})[/dim]")

                # Plan next action
                plan: ActionPlan = await Planner.decide_next_action(
                    goal=self.goal,
                    current_url=current_url,
                    elements=elements,
                    memory=self.memory,
                )

                console.print(f"[bold yellow][Thought]:[/bold yellow] {plan.thought}")
                console.print(f"[bold green][Action]:[/bold green] [bold]{plan.action.value.upper()}[/bold] {plan.args}")

                # Execute action
                observation = ""
                success = True
                screenshot_file = None

                try:
                    if plan.action == AgentActionType.NAVIGATE:
                        url = plan.args.get("url", "")
                        await self.browser.navigate(url)
                        observation = f"Navigated to {self.browser.page.url}"

                    elif plan.action == AgentActionType.CLICK:
                        idx = int(plan.args.get("index", 1))
                        await self.browser.click_element(idx)
                        observation = f"Clicked element [{idx}]"

                    elif plan.action == AgentActionType.TYPE:
                        idx = int(plan.args.get("index", 1))
                        text = plan.args.get("text", "")
                        press_enter = plan.args.get("press_enter", False)
                        await self.browser.type_text(idx, text, press_enter=press_enter)
                        observation = f"Typed '{text}' into element [{idx}] (enter={press_enter})"

                    elif plan.action == AgentActionType.SCROLL:
                        direction = plan.args.get("direction", "down")
                        amount = int(plan.args.get("amount", 500))
                        await self.browser.scroll(direction=direction, amount=amount)
                        observation = f"Scrolled {direction} by {amount}px"

                    elif plan.action == AgentActionType.WAIT:
                        secs = int(plan.args.get("seconds", 2))
                        await asyncio.sleep(secs)
                        observation = f"Waited {secs} seconds"

                    elif plan.action == AgentActionType.EXTRACT:
                        target = str(plan.args.get("target", "all")).lower()
                        html = await self.browser.get_page_html()
                        page_text = await self.browser.get_page_text()

                        extracted: Dict[str, Any] = {}
                        if target in ("tables", "all"):
                            tables = DataExtractor.extract_tables(html)
                            if tables:
                                extracted["tables"] = tables
                        if target in ("links", "all"):
                            links = DataExtractor.extract_links(html, base_url=current_url)
                            if links:
                                extracted["links"] = links[:25]

                        extracted["text_summary"] = page_text[:500] if page_text else ""
                        self.memory.extracted_data.append(extracted)

                        num_tables = len(extracted.get("tables", []))
                        num_links = len(extracted.get("links", []))
                        observation = (
                            f"Extracted structured content: {num_tables} tables, "
                            f"{num_links} links, {len(page_text)} text chars"
                        )

                    elif plan.action == AgentActionType.FINISH:
                        self.final_answer = plan.args.get("answer", "Task completed.")
                        observation = "Goal marked as completed by agent."
                        console.print(Panel(f"[bold green][Result]:[/bold green]\n{self.final_answer}", title="Goal Achieved"))
                        break

                except Exception as ex:
                    success = False
                    observation = f"Action execution error: {str(ex)}"
                    console.print(f"[bold red][Error]:[/bold red] {observation}")

                # Capture step screenshot if enabled
                if settings.save_screenshots:
                    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = settings.screenshot_dir / f"step_{step_idx}_{ts}.png"
                    await self.browser.take_screenshot(filename)
                    screenshot_file = str(filename)

                # Record step into memory
                self.memory.add_step(
                    StepRecord(
                        step_number=step_idx,
                        url=current_url,
                        action_type=plan.action.value,
                        action_args=plan.args,
                        thought=plan.thought,
                        observation=observation,
                        success=success,
                        screenshot_path=screenshot_file,
                    )
                )

            if not self.final_answer:
                self.final_answer = "Max steps limit reached before task completion."

            return self.final_answer

        finally:
            await self.browser.close()
