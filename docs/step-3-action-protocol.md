# Step 3: Action Protocol

## What We Built

Step 3 defines the boundary between model-generated text and future tool
execution:

```text
ModelResponse.text -> parse_action(text) -> Action -> future dispatcher
```

The model must produce exactly one JSON action per response. `parse_action`
parses the text, validates the tool name and arguments, and returns an `Action`.
It does not execute the action.

This step also defines the JSON-facing contracts for the ten specialized tools
from the SWE-agent paper plus general Bash execution. The tool functions remain
skeletons; dispatch, execution, observations, prompting, retry behavior, and
the agent loop are not part of this step.

## File Layout

```text
src/agent_protocol/data_models.py   Action data model
src/agent_protocol/parser.py        JSON parsing and action validation
src/tools/specs.py                  Tool names and argument schemas
src/tools/viewer.py                 File-viewer tool skeletons
src/tools/search.py                 Search tool skeletons
src/tools/editor.py                 Editing tool skeletons
src/tools/shell.py                  Bash tool skeleton
src/tools/task.py                   Submit tool skeleton
tests/test_parser.py                Parser and validation tests
```

## Core Types

`Action` is defined in `src/agent_protocol/data_models.py`:

```python
@dataclass(frozen=True)
class Action:
    """One tool invocation parsed from a model's JSON response."""

    tool: str
    arguments: dict[str, object]
```

The JSON-facing schema types are defined in `src/tools/specs.py`:

```python
@dataclass(frozen=True)
class ArgumentSpec:
    accepted_types: tuple[type, ...]
    required: bool


@dataclass(frozen=True)
class ToolSpec:
    arguments: dict[str, ArgumentSpec]
```

The parser interface is defined in `src/agent_protocol/parser.py`:

```python
class ActionParseError(ValueError):
    """Raised when model output cannot be converted into a valid action."""


def parse_action(text: str) -> Action:
    """Parse and validate one JSON action from a model response."""
```

## JSON Contract

Every model response uses the same nested structure, including Bash:

```json
{
  "tool": "open",
  "arguments": {
    "path": "src/main.py",
    "line_number": 50
  }
}
```

```json
{
  "tool": "bash",
  "arguments": {
    "command": "pytest -q"
  }
}
```

`tool` identifies the operation. `arguments` contains only that tool's inputs.
The nested format separates protocol-level data from tool-specific data.

The complete response must be valid JSON with no prose or Markdown fences
outside it. Surrounding whitespace is accepted. Additional top-level fields
are ignored, but `tool` and `arguments` are required.

## Validation

`parse_action` validates three layers before constructing an `Action`:

1. The response is valid JSON and its top-level value is an object.
2. `tool` is a string and `arguments` is an object.
3. The tool exists and its required, optional, and supplied arguments match
   `TOOL_SPECS`.

Unknown tools, missing required arguments, unknown arguments, and incorrect
argument types raise `ActionParseError`. Optional arguments may be omitted or
explicitly set to JSON `null`, which becomes Python `None`.

Argument validation uses exact runtime types because values come from
`json.loads()`. This correctly rejects JSON `true` as an integer even though
Python otherwise treats `bool` as a subclass of `int`.

Error messages are concise enough to be returned to the model later. The
parser only reports the error; whether the future agent retries, terminates, or
adds the error to history remains an agent-policy decision.

## Tool Set

The specialized tools are `open`, `goto`, `scroll_down`, `scroll_up`,
`search_file`, `search_dir`, `find_file`, `edit`, `create`, and `submit`.
`bash` provides general shell-command execution.

The file viewer has a 100-line maximum window, following the SWE-agent paper.
Our action syntax intentionally differs from the paper: all actions, including
Bash, use the common JSON envelope.

The schemas are explicit rather than derived through function introspection.
This makes the model-facing ACI contract easy to inspect and produces precise
validation errors, but duplicates information in Python function signatures.
Tests should prevent those definitions from drifting apart as implementations
are added.
