"""Dispatch validated actions to concrete tool implementations."""

from .context import ToolContext
from .editor import create, edit
from .search import find_file, search_dir, search_file
from .shell import bash
from .task import submit
from .viewer import goto, open_file, scroll_down, scroll_up

from agent_protocol import Action, Observation

TOOL_MAP = {
    "open": open_file,
    "goto": goto,
    "scroll_up": scroll_up,
    "scroll_down": scroll_down,
    "search_file": search_file,
    "search_dir": search_dir,
    "find_file": find_file,
    "edit": edit,
    "create": create,
    "submit": submit,
    "bash": bash,
}


def execute_tool(action: Action, context: ToolContext) -> Observation:
    """Execute a validated action and return the tool's observation."""
    tool_func = TOOL_MAP[action.tool]
    return tool_func(context, **action.arguments)
