# Coding Agent from Scratch

A small research project inspired by [SWE-agent](https://arxiv.org/abs/2405.15793). The goal is to implement an Agent-Computer Interface (ACI) from scratch and study how interface design turns a lightweight local LLM into a coding agent.

## Goals

The agent should be able to:

- inspect and search a code repository;
- edit source files;
- run commands and tests;
- iterate using tool feedback;
- produce a final Git patch;
- record its trajectory, runtime, token usage, and result.

## Main Experiment

Run the same local model on an RTX 4090 and compare:

1. **Shell baseline** — the model works through a general-purpose shell.
2. **Structured ACI** — the model receives dedicated tools for inspecting, searching, editing, testing, and submitting code.

Keeping the model and inference budget fixed will help isolate the effect of the interface.

## Model

The initial model is served locally through Ollama:

| Property | Value |
|---|---|
| Ollama model | `qwen3.8` |
| Architecture | Qwen 3.5 (`qwen35`) |
| Parameters | 27.3B |
| Quantization | Q4_K_M |
| Maximum context length | 262,144 tokens |
| Embedding length | 5,120 |
| Capabilities | Completion, vision, tools, thinking |
| Minimum Ollama version | 0.32.12 |

The project may use a smaller configured context window than the model's maximum in order to control KV-cache memory use and inference latency.

## Tool Contracts

```text
open(path, line_number)
goto(line_number)
scroll_down()
scroll_up()
search_file(search_term, file)
search_dir(search_term, dir)
find_file(file_name, dir)
edit(start_line, end_line, replacement_text)
create(filename)
bash(command)
submit()
```

These interfaces are defined, but their concrete implementations are still in
progress.

## Running Tests

Run commands from the repository root. Because the project uses a `src/`
layout and is not required to be installed during development, include `src`
on `PYTHONPATH`:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

Compile all source and test modules to catch syntax errors:

```bash
python -m compileall -q src tests
```

Check patches for whitespace errors before committing:

```bash
git diff --check
```

## Evaluation

For each run, record:

- task success;
- number of agent steps;
- token usage and runtime;
- invalid actions and failed edits;
- number of test executions;
- final patch and full trajectory.

The model, prompt, sampling settings, step limit, and token budget should remain fixed when comparing interfaces.

## References

- [SWE-agent paper](https://arxiv.org/abs/2405.15793)
- [SWE-agent repository](https://github.com/SWE-agent/SWE-agent)
- [SWE-bench](https://github.com/SWE-bench/SWE-bench)
