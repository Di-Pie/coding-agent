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

## Planned Tools

```text
list_files(path, depth)
open_file(path, line_start, line_end)
search(query, path)
apply_patch(patch)
run(command, timeout)
git_diff()
submit()
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
