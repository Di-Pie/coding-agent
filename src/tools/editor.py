"""Skeletons for file-editing tools."""

from agent_protocol import Observation

from .context import ToolContext


def edit(
    context: ToolContext,
    start_line: int,
    end_line: int,
    replacement_text: str,
) -> Observation:
    """Replace an inclusive line range in the currently open file."""
    raise NotImplementedError


def create(context: ToolContext, filename: str) -> Observation:
    """Create a file and make it the currently open file."""
    raise NotImplementedError
