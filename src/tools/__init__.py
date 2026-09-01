"""Tool skeletons exposed through the agent-computer interface."""

from tools.context import ToolContext, ToolPathError
from tools.editor import create, edit
from tools.search import find_file, search_dir, search_file
from tools.shell import bash
from tools.specs import TOOL_SPECS
from tools.task import submit
from tools.viewer import goto, open_file, scroll_down, scroll_up

__all__ = [
    "ToolContext",
    "ToolPathError",
    "TOOL_SPECS",
    "bash",
    "create",
    "edit",
    "find_file",
    "goto",
    "open_file",
    "scroll_down",
    "scroll_up",
    "search_dir",
    "search_file",
    "submit",
]
