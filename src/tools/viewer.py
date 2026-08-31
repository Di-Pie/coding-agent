"""Skeletons for the stateful file-viewer tools."""

from agent_protocol import Observation

DEFAULT_WINDOW_SIZE = 100


def open_file(path: str, line_number: int | None = None) -> Observation:
    """Open a file and display at most 100 lines around an optional line number."""
    raise NotImplementedError


def goto(line_number: int) -> Observation:
    """Move the current file window to include a line number."""
    raise NotImplementedError


def scroll_down() -> Observation:
    """Move the current file window down by 100 lines."""
    raise NotImplementedError


def scroll_up() -> Observation:
    """Move the current file window up by 100 lines."""
    raise NotImplementedError
