"""Skeletons for the stateful file-viewer tools."""

DEFAULT_WINDOW_SIZE = 100


def open_file(path: str, line_number: int | None = None) -> str:
    """Open a file and display at most 100 lines around an optional line number."""
    raise NotImplementedError


def goto(line_number: int) -> str:
    """Move the current file window to include a line number."""
    raise NotImplementedError


def scroll_down() -> str:
    """Move the current file window down by 100 lines."""
    raise NotImplementedError


def scroll_up() -> str:
    """Move the current file window up by 100 lines."""
    raise NotImplementedError
