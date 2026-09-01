"""Skeletons for the stateful file-viewer tools."""

from agent_protocol import Observation

from .context import ToolContext


def open_file(
    context: ToolContext,
    path: str,
    line_number: int | None = None,
) -> Observation:
    """Open a file and display a configured window around an optional line."""
    raise NotImplementedError


def goto(context: ToolContext, line_number: int) -> Observation:
    """Move the current file window to include a line number."""
    raise NotImplementedError


def scroll_down(context: ToolContext) -> Observation:
    """Move the current file view down by one configured window."""
    raise NotImplementedError


def scroll_up(context: ToolContext) -> Observation:
    """Move the current file view up by one configured window."""
    raise NotImplementedError
