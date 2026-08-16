# Coding Agent from Scratch

A small research project inspired by [SWE-agent](https://arxiv.org/abs/2405.15793). The goal is to implement an Agent-Computer Interface (ACI) from scratch and study how interface design turns a lightweight local LLM into a coding agent.

Target completion date: **September 1, 2026**.

## Goals

The agent should be able to:

- inspect and search a code repository;
- edit source files;
- run commands and tests;
- iterate using tool feedback;
- produce a final Git patch;
- record its trajectory, runtime, token usage, and result.

## Main Experiment

Run the same 7B or 14B code model locally on an RTX 4090 and compare:

1. **Shell baseline** — the model works through a general-purpose shell.
2. **Structured ACI** — the model receives dedicated tools for inspecting, searching, editing, testing, and submitting code.

Keeping the model and inference budget fixed will help isolate the effect of the interface.

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

## First Milestone

Build one complete working loop:

```text
problem -> inspect -> edit -> test -> submit patch
```

Start with three small toy bugs before moving to real benchmark tasks.

## Evaluation

For each run, record:

- task success;
- number of agent steps;
- token usage and runtime;
- invalid actions and failed edits;
- number of test executions;
- final patch and full trajectory.

The model, prompt, sampling settings, step limit, and token budget should remain fixed when comparing interfaces.

## Roadmap

- [ ] Define model, tool, and environment interfaces
- [ ] Connect a local LLM
- [ ] Implement the minimal agent loop
- [ ] Add shell execution and patch submission
- [ ] Add structured repository tools
- [ ] Add safety limits and trajectory logging
- [ ] Create reproducible benchmark tasks
- [ ] Run baseline, ACI, and ablation experiments
- [ ] Publish results and a short demo

## References

- [SWE-agent paper](https://arxiv.org/abs/2405.15793)
- [SWE-agent repository](https://github.com/SWE-agent/SWE-agent)
- [SWE-bench](https://github.com/SWE-bench/SWE-bench)
