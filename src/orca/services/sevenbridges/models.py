from pydantic import validator
from pydantic.dataclasses import dataclass
from sevenbridges.models.enums import TaskStatus as TaskState


@dataclass(kw_only=False)
class TaskStatus:
    """Task status and whether it's done."""

    state: str

    @validator("state")
    def ensure_valid_state(cls, value: str) -> str:
        """Check that the task state is a valid value"""
        if getattr(TaskState, value, None) is None:
            message = f"State '{value}' is not a valid value."
            raise ValueError(message)
        return value

    @property
    def is_done(self) -> bool:
        """Whether the workflow is done irrespective of success."""
        return self.state in TaskState.terminal_states
