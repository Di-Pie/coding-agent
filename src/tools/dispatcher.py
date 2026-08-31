"""Dispatch validated actions to concrete tool implementations."""

import tools

from agent_protocol import Action, Observation

TOOL_MAP = {
    "open": tools.open_file,
    "goto": tools.goto,
    "scroll_up": tools.scroll_up,
    "scroll_down": tools.scroll_down,
    "search_file": tools.search_file,
    "search_dir": tools.search_dir,
    "find_file": tools.find_file,
    "edit": tools.edit,
    "create": tools.create,
    "submit": tools.submit,
    "bash": tools.bash,
}


def execute_tool(action: Action) -> Observation:
    """Execute a validated action and return the tool's observation."""
    tool_func = TOOL_MAP[action.tool]
    return tool_func(**action.arguments)
