"""JSON-facing argument schemas for the available tools."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArgumentSpec:
    accepted_types: tuple[type, ...]
    required: bool


@dataclass(frozen=True)
class ToolSpec:
    arguments: dict[str, ArgumentSpec]


TOOL_SPECS: dict[str, ToolSpec] = {
    "open": ToolSpec(
        arguments={
            "path": ArgumentSpec((str,), required=True),
            "line_number": ArgumentSpec(
                (int, type(None)),
                required=False,
            ),
        }
    ),
    "goto": ToolSpec(
        arguments={
            "line_number": ArgumentSpec((int,), required=True),
        }
    ),
    "scroll_down": ToolSpec(arguments={}),
    "scroll_up": ToolSpec(arguments={}),
    "search_file": ToolSpec(
        arguments={
            "search_term": ArgumentSpec((str,), required=True),
            "file": ArgumentSpec((str, type(None)), required=False),
        }
    ),
    "search_dir": ToolSpec(
        arguments={
            "search_term": ArgumentSpec((str,), required=True),
            "dir": ArgumentSpec((str, type(None)), required=False),
        }
    ),
    "find_file": ToolSpec(
        arguments={
            "file_name": ArgumentSpec((str,), required=True),
            "dir": ArgumentSpec((str, type(None)), required=False),
        }
    ),
    "edit": ToolSpec(
        arguments={
            "start_line": ArgumentSpec((int,), required=True),
            "end_line": ArgumentSpec((int,), required=True),
            "replacement_text": ArgumentSpec((str,), required=True),
        }
    ),
    "create": ToolSpec(
        arguments={
            "filename": ArgumentSpec((str,), required=True),
        }
    ),
    "submit": ToolSpec(arguments={}),
    "bash": ToolSpec(
        arguments={
            "command": ArgumentSpec((str,), required=True),
        }
    ),
}
