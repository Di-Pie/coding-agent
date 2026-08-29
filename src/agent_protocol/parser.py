import json

from agent_protocol import Action
from tools import TOOL_SPECS


class ActionParseError(ValueError):
    """Raised when model output cannot be converted into a valid action."""


def parse_action(text: str) -> Action:
    """Parse and validate one JSON action from a model response."""
    try:
        data = json.loads(text)
    except json.JSONDecodeError as error:
        raise ActionParseError("Model response is not valid JSON.") from error

    if not isinstance(data, dict):
        raise ActionParseError("Action must be a JSON object.")

    if "tool" not in data:
        raise ActionParseError('Action is missing required field "tool".')
    tool_name = data["tool"]
    if not isinstance(tool_name, str):
        raise ActionParseError('Action field "tool" must be a string.')

    if "arguments" not in data:
        raise ActionParseError('Action is missing required field "arguments".')
    arguments = data["arguments"]
    if not isinstance(arguments, dict):
        raise ActionParseError('Action field "arguments" must be an object.')

    tool_spec = TOOL_SPECS.get(tool_name)
    if tool_spec is None:
        raise ActionParseError(f'Unknown tool "{tool_name}".')

    expected_names = set(tool_spec.arguments)
    provided_names = set(arguments)

    missing = {
        name
        for name, spec in tool_spec.arguments.items()
        if spec.required and name not in arguments
    }

    unknown = provided_names - expected_names

    if missing:
        names = ", ".join(sorted(missing))
        raise ActionParseError(
            f'Invalid action for "{tool_name}": missing required arguments: {names}.'
        )

    if unknown:
        names = ", ".join(sorted(unknown))
        raise ActionParseError(
            f'Invalid action for "{tool_name}": unknown arguments: {names}.'
        )

    for name, value in arguments.items():
        argument_spec = tool_spec.arguments[name]
        if type(value) not in argument_spec.accepted_types:
            expected_types = " or ".join(
                _json_type_name(expected_type)
                for expected_type in argument_spec.accepted_types
            )
            actual_type = _json_type_name(type(value))
            raise ActionParseError(
                f'Invalid action for "{tool_name}": argument "{name}" must be '
                f"{expected_types}, but received {actual_type}."
            )

    return Action(tool=tool_name, arguments=arguments)


def _json_type_name(value_type: type) -> str:
    """Return a concise JSON-oriented name for a Python runtime type."""
    names = {
        str: "a string",
        int: "an integer",
        float: "a number",
        bool: "a boolean",
        list: "an array",
        dict: "an object",
        type(None): "null",
    }
    return names.get(value_type, value_type.__name__)
