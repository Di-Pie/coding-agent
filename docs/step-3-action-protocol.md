# Step 3: Action Protocol

## What We Built

Step 3 defines the boundary between model-generated text and future tool
execution:

```text
ModelResponse.text -> parse_action(text) -> Action + ToolContext
                                             -> execute_tool() -> Observation
```

The model must produce exactly one JSON action per response. `parse_action`
parses the text, validates the tool name and arguments, and returns an `Action`.
`execute_tool` maps that action to a tool implementation, injects shared
execution context, and returns its structured `Observation`.

This step also defines the JSON-facing contracts for the ten specialized tools
from the SWE-agent paper plus general Bash execution. `ToolContext` defines the
state shared across actions. The tool functions remain skeletons; their actual
behavior, runtime state transitions, observation formatting, prompting, retry
behavior, and the agent loop are not part of this step.

## File Layout

```text
src/agent_protocol/data_models.py   Action and Observation data models
src/agent_protocol/parser.py        JSON parsing and action validation
src/tools/context.py                Shared tool state and execution limits
src/tools/specs.py                  Tool names and argument schemas
src/tools/dispatcher.py             Action-to-tool mapping and dispatch
src/tools/viewer.py                 File-viewer tool skeletons
src/tools/search.py                 Search tool skeletons
src/tools/editor.py                 Editing tool skeletons
src/tools/shell.py                  Bash tool skeleton
src/tools/task.py                   Submit tool skeleton
tests/test_parser.py                Parser and validation tests
tests/test_data_models.py           Observation invariant tests
tests/test_context.py               Context initialization and boundary tests
tests/test_dispatcher.py            Dispatch contract tests
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

`Observation` is also defined in `src/agent_protocol/data_models.py`:

```python
@dataclass(frozen=True)
class Observation:
    """Structured result of executing one action."""

    output: str
    success: bool
    truncated: bool
    terminal: bool
    exit_code: int | None = None
    error: str | None = None
```

The model eventually receives `output` as text, while the runtime can inspect
structured status and metadata without parsing that text. `__post_init__`
rejects inconsistent observations: success cannot include an error, failure
must include one, terminal results must succeed, and a provided process exit
code must agree with `success`.

`ToolContext` is defined in `src/tools/context.py`:

```python
@dataclass
class ToolContext:
    repository_root: Path
    working_directory: Path
    open_file: Path | None = None
    window_start: int = 1
    window_size: int = 100
    command_timeout: int = 120
    max_output_chars: int = 12_000
```

One context belongs to one agent run. It is mutable because `open`, scrolling,
editing, creation, and standalone `cd` may update persistent execution state.
Keeping state in an explicit per-run object avoids module globals and allows
separate agents and tests to use isolated contexts.

`ToolContext.__post_init__` resolves paths, rejects missing or invalid initial
paths, prevents the working directory and initial open file from resolving
outside the repository, and validates positive limits. These checks validate
initial state only. Tools must still validate every model-provided path before
using it or changing context state.

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

## Dispatch

`TOOL_MAP` in `src/tools/dispatcher.py` maps all 11 JSON tool names to their
Python functions. `execute_tool(action, context)` injects the context, forwards
the validated model arguments, and returns the tool's `Observation` unchanged:

```text
Action(tool="open", arguments={...}) + ToolContext(...)
    -> TOOL_MAP["open"](context, **arguments)
    -> Observation(...)
```

`ToolContext` is a Python-only dependency and does not appear in the JSON tool
schemas. All tool functions accept it as their first argument to keep dispatch
uniform, even when a particular tool does not currently use every field.

The dispatcher assumes the action was already validated. Expected operational
failures should become `Observation(success=False, ...)` inside tool
implementations; unexpected programming exceptions propagate during v0.1
development. A test ensures `set(TOOL_SPECS) == set(TOOL_MAP)` so the parser
and dispatcher cannot silently support different tool sets.

## Tool Set

The specialized tools are `open`, `goto`, `scroll_down`, `scroll_up`,
`search_file`, `search_dir`, `find_file`, `edit`, `create`, and `submit`.
`bash` provides general shell-command execution.

The file viewer uses a 100-line window by default, following SWE-agent. For
`goto(line_number)`, the requested line is neither the first line nor the
center of the window. It appears approximately one-sixth of the way down:

```text
window_start = line_number - window_size / 6
```

The start is clamped at the beginning and end of the file. For example, with a
100-line window, `goto(50)` starts at line 33, so line 50 appears as the 18th
displayed line. The context stores `window_start`; `line_number` is only
used to calculate it. Our action syntax intentionally differs from the paper:
all actions, including Bash, use the common JSON envelope.

The schemas are explicit rather than derived through function introspection.
This makes the model-facing ACI contract easy to inspect and produces precise
validation errors, but duplicates information in Python function signatures.
Tests should prevent those definitions from drifting apart as implementations
are added.
