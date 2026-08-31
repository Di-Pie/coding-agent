# Step 1: Project Foundation

## What We Built

Step 1 created the Python project structure and configuration boundary used by
later components. It separates model-provider settings from future agent
runtime settings and loads both from one local JSON file:

```text
configs/local-qwen.json -> load_config() -> ModelConfig + AgentConfig
```

This step provides configuration values only. It does not implement the model
adapter, tools, agent loop, context management, or enforcement of runtime
limits.

## File Layout

```text
pyproject.toml                  Package metadata and src-layout discovery
.python-version                 Python 3.13 development version
src/coding_agent/config.py      Configuration data models and JSON loader
src/coding_agent/__init__.py    Marks coding_agent as a Python package
configs/local-qwen.json         Local Ollama and agent settings
```

The project uses a `src/` layout, so importable packages live under `src`
instead of the repository root. `pyproject.toml` configures setuptools to find
packages there. The project currently uses only the Python standard library.

## Core Types

The configuration types are defined in `src/coding_agent/config.py`:

```python
@dataclass(frozen=True)
class ModelConfig:
    name: str
    base_url: str
    temperature: float = 0.2
    context_length: int = 32_768


@dataclass(frozen=True)
class AgentConfig:
    max_steps: int = 30
    command_timeout: int = 120
    max_output_chars: int = 12_000
```

`ModelConfig` contains values needed to call the model provider. `AgentConfig`
contains future runtime limits. Keeping them separate prevents provider
configuration from becoming mixed with agent policy.

The dataclasses are frozen so a loaded run configuration cannot be mutated
accidentally. `load_config(path)` reads JSON and constructs both typed values;
unknown fields or missing required fields fail immediately instead of being
silently ignored, while omitted fields with defaults use those defaults.

## Local Configuration

`configs/local-qwen.json` selects the local Ollama model `qwen3.8`, served at
`http://127.0.0.1:11434`, with temperature `0.2` and a configured context
window of 32,768 tokens.

The model supports a maximum context length of 262,144 tokens, but the project
starts with a smaller configured window to reduce KV-cache memory use and
inference latency. The initial agent settings are 30 maximum steps, a
120-second command timeout, and a 12,000-character output limit. Later steps
must explicitly implement and enforce these limits.
