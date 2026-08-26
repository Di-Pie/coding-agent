# Step 2: Model Layer

## What We Built

Step 2 establishes the boundary between the future agent and a language-model
provider:

```text
Agent -> Model.generate(messages) -> ModelResponse
```

The future agent communicates only through the provider-independent `Model`
interface: it sends chat messages and receives a normalized `ModelResponse`.
It does not need to know how Ollama formats HTTP requests or names response
fields.

`OllamaModel` sits on the provider side of the boundary. It translates the
shared input into an Ollama `/api/chat` request, then translates Ollama's raw
response back into `ModelResponse`. This isolates provider-specific behavior
from the future agent and allows another compatible model implementation to be
substituted later.

Mocked tests verify this translation boundary without requiring Ollama, a GPU,
or a loaded model. This step does not define the agent loop, message-history
policy, actions, tools, ACI, context management, or termination behavior.

## File Layout

```text
src/lm_infra/models.py       Model, ModelResponse, OllamaModel
src/lm_infra/__init__.py     Public exports for the model package
src/coding_agent/config.py   ModelConfig
tests/test_models.py         Mocked Ollama adapter tests
```

`Model` and `ModelResponse` define the provider-independent boundary, while
`OllamaModel` implements that boundary for Ollama. They currently share
`models.py` because the model layer is small and can be understood in one file.
If more providers are added, the shared types and provider adapters may be
separated into different modules.

## Core Types

The following types are defined in `src/lm_infra/models.py`:

```python
@dataclass(frozen=True)
class ModelResponse:
    """Normalized text and token counts returned by a language model."""

    text: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class Model(Protocol):
    """Interface the agent uses without depending on a model provider."""

    def generate(self, messages: list[dict[str, str]]) -> ModelResponse:
        """Generate the next response from a chat history."""
        ...
```

## Design

`Model` describes the capability the agent needs instead of one provider. The
agent can therefore use `OllamaModel`, another provider, or a deterministic
fake without changing its own code.

Because `Model` is a `Protocol`, compatibility is based on having a compatible
`generate` method rather than explicit inheritance. This is structural typing.

`messages` is an ordered conversation history:

```python
[
    {"role": "system", "content": "You are a coding agent."},
    {"role": "user", "content": "Fix the bug."},
]
```

A list preserves order. Each dictionary contains a role and text and closely
matches Ollama's chat API.

`dict[str, str]` is simple but cannot enforce required keys or valid roles, and
cannot represent structured tool calls. A provider-neutral `TypedDict` or
dataclass remains an open option.

`ModelResponse` normalizes different provider formats into one output type:

- `text`: model-generated content;
- `prompt_tokens`: input tokens processed for this call, or `None` if unknown;
- `completion_tokens`: new tokens generated for this call, or `None` if unknown.

`prompt_tokens` and `completion_tokens` help monitor context limits, estimate
compute or API cost, detect excessive input/output, and compare agent
efficiency.

Ollama's `message.content`, `prompt_eval_count`, and `eval_count` map to these
fields, keeping Ollama-specific keys out of future agent code.

`ModelResponse` normalizes the provider response envelope; it does not validate
whether the generated `text` follows a future action format.
