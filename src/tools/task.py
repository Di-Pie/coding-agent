"""Skeleton for task-level tools."""

from agent_protocol import Observation

from .context import ToolContext


def submit(context: ToolContext) -> Observation:
    """Submit the current repository changes and end the task."""
    raise NotImplementedError
