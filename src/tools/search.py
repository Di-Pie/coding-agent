"""Skeletons for repository search tools."""

from agent_protocol import Observation

from .context import ToolContext


def search_file(
    context: ToolContext,
    search_term: str,
    file: str | None = None,
) -> Observation:
    """Search a file, or the currently open file, for a term."""
    raise NotImplementedError


def search_dir(
    context: ToolContext,
    search_term: str,
    dir: str | None = None,
) -> Observation:
    """Search files under a directory, or the current directory, for a term."""
    raise NotImplementedError


def find_file(
    context: ToolContext,
    file_name: str,
    dir: str | None = None,
) -> Observation:
    """Find matching file names under a directory or the current directory."""
    raise NotImplementedError
