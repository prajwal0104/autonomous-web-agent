"""Agent memory and action observation history."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class StepRecord(BaseModel):
    """Details of a single execution step taken by the agent."""

    step_number: int
    url: str
    action_type: str
    action_args: Dict[str, Any] = Field(default_factory=dict)
    thought: str = ""
    observation: str = ""
    success: bool = True
    screenshot_path: Optional[str] = None


class AgentMemory(BaseModel):
    """Keeps state and context history across execution steps."""

    goal: str
    steps: List[StepRecord] = Field(default_factory=list)
    extracted_data: List[str] = Field(default_factory=list)

    def add_step(self, step: StepRecord) -> None:
        """Record completed step into memory."""
        self.steps.append(step)

    def format_history_for_llm(self, max_recent: int = 5) -> str:
        """Summarize recent steps taken for LLM context injection."""
        if not self.steps:
            return "No previous actions taken yet. This is the initial step."

        recent = self.steps[-max_recent:]
        lines = ["--- Previous Steps Taken ---"]
        for s in recent:
            status = "✓ Succeeded" if s.success else "✗ Failed"
            lines.append(
                f"Step {s.step_number}: [{s.action_type.upper()}] {s.thought} -> {status}. "
                f"Observation: {s.observation}"
            )
        return "\n".join(lines)
