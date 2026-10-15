import asyncio
import sys
from typing import Optional
import typer
from rich.console import Console
from rich.prompt import Prompt

from .config import settings
from .agent.browser_agent import AutonomousBrowserAgent

if sys.platform == "win32":
    try:
        if sys.stdout and hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr and hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()
app = typer.Typer(
    name="web-agent",
    help="Autonomous AI agent for goal-driven web automation and navigation.",
    add_completion=False,
)


@app.command()
def run(
    goal: Optional[str] = typer.Option(
        None,
        "--goal",
        "-g",
        help="Goal for the agent to achieve (e.g. 'Search for latest AI news on Hacker News')",
    ),
    headless: bool = typer.Option(
        False,
        "--headless",
        help="Run browser in headless background mode (default: visible browser window)",
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider",
        "-p",
        help="LLM provider: openai, gemini, ollama, or mock",
    ),
    max_steps: int = typer.Option(
        20,
        "--max-steps",
        "-s",
        help="Maximum interaction steps before terminating",
    ),
):
    """Run the Autonomous Web Agent on a specific objective."""
    if not goal:
        goal = Prompt.ask("\n[bold cyan]Enter goal for Autonomous Web Agent[/bold cyan]")

    if provider:
        settings.llm_provider = provider

    agent = AutonomousBrowserAgent(goal=goal, headless=headless)
    result = asyncio.run(agent.run(max_steps=max_steps))
    console.print(f"\n[bold green]Final Outcome:[/bold green] {result}\n")


def cli():
    """Package entrypoint."""
    app()


if __name__ == "__main__":
    cli()
