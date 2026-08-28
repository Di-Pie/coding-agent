"""Skeletons for file-editing tools."""


def edit(start_line: int, end_line: int, replacement_text: str) -> str:
    """Replace an inclusive line range in the currently open file."""
    raise NotImplementedError


def create(filename: str) -> str:
    """Create a file and make it the currently open file."""
    raise NotImplementedError
