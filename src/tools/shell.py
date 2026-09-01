"""Skeleton for general Bash command execution."""

from agent_protocol import Observation

from .context import ToolContext


def bash(context: ToolContext, command: str) -> Observation:
    """Execute a command through Bash."""
    raise NotImplementedError
