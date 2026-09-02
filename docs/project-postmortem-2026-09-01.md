# Project Postmortem: Missed September 1 Deadline

Date: September 1, 2026

## Outcome

The project did not meet its original September 1 deadline. Development began
on August 16, leaving roughly 16 days. At the deadline, the project has a solid
foundation but not a runnable coding agent.

Estimated v0.1 completion: **38%**.

Completed:

- Python project structure and configuration.
- Ollama model adapter and provider-independent model interface.
- JSON action format, parser, and explicit schemas for 11 tools.
- `Action`, `Observation`, tool dispatch, and shared execution context.
- Repository-safe path resolution.
- `open_file()` with windowing, errors, truncation, and tests.
- 47 passing tests and design documentation.

Not completed:

- The remaining viewer, search, editor, shell, and submission tools.
- Prompt and observation formatting.
- Message-history and context-management behavior.
- The agent loop, retry behavior, and termination policy.
- CLI, trajectory logging, and end-to-end Ollama execution.
- The shell-versus-ACI experiment and evaluation.

## What Went Well

- The project now has explicit, testable boundaries between the model, action
  protocol, dispatcher, tool state, and observations.
- Important decisions are understood rather than hidden behind an agent
  framework.
- Tests caught subtle behavior around types, paths, state, and file windows.
- The learning-oriented `AGENTS.md` clarified ownership: the developer owns
  core architecture and Codex supports explanation, review, and repetitive
  engineering.
- Difficult topics such as structural typing, provider normalization, token
  accounting, path safety, and half-open indexing were studied in depth.

This work was valuable. The failure was not that time was spent learning; it
was that the learning scope and delivery scope were not planned against the
available time.

## What Went Wrong

### 1. The deadline was a label, not an operating constraint

The date was initially written in the README and later removed because the
README should not track progress. No replacement tracker, weekly milestones,
or deadline review was created. As a result, the date stopped influencing
scope and daily decisions.

### 2. There was no precise v0.1 definition of done

"Reproduce SWE-agent" can include the ACI, model integration, agent loop,
prompting, sandboxing, evaluation, and experimental comparison. Without a
small acceptance test, it was impossible to tell which work was required by
September 1 and which work could wait.

The README also describes a shell-versus-structured-ACI experiment. That is a
second milestone after building a functional agent, not part of the same
short implementation milestone.

### 3. Development was horizontal rather than end-to-end

The project built clean layers in sequence, but never created a minimal
vertical path such as:

```text
task -> model -> one action -> one tool -> observation -> next model call
```

Consequently, integration risks remain untested even though several individual
layers are well designed.

### 4. Core decisions were discovered late and serially

Step 3 expanded as decisions emerged about:

- one versus multiple actions per model response;
- direct Bash versus JSON for all actions;
- exact tool names and argument schemas;
- `Observation` fields and failure semantics;
- dispatcher exception behavior;
- persistent `ToolContext` state;
- standalone `cd` behavior;
- repository-safe paths;
- exact SWE-agent viewer formatting and positioning.

These were legitimate decisions, but they were not identified as a decision
checklist at the start of the milestone. Each new decision interrupted
implementation and caused nearby code or documentation to be revisited.

### 5. Avoidable rework occurred early

Codex initially made broad changes without approval, which conflicted with the
learning goal and led to a revert and a stricter step-by-step process. There
was also confusion between `/data/projects/agent/coding-agent` and
`/data/projects/coding-agent`, plus repeated README and documentation rewrites.

Several explanations were introduced in the wrong order or used ambiguous
terms such as "model layer" and "agent-provider coupling." This caused extra
clarification cycles instead of building understanding efficiently.

### 6. Reviews sometimes exposed one issue at a time

The `open_file()` indexing review is the clearest example. The review should
have begun with one coordinate convention, a complete boundary table, and
invariants. Instead, individual off-by-one problems were surfaced over several
iterations. The final understanding was strong, but the route was inefficient
and frustrating.

### 7. Learning depth and delivery speed were not explicitly balanced

The project deliberately requires the developer to implement core agent
machinery. That is appropriate, but it makes a 16-day deadline aggressive.
There was no timebox for how long to study a concept before recording the
decision, implementing it, and moving on.

### 8. The schedule had no integration or contingency buffer

Git history shows work from August 16 through September 1, including a gap in
committed progress between August 18 and August 26. The schedule did not reserve
time for local-model integration, debugging, evaluation, or unexpected issues.

## How to Improve the Next Project

### Define one executable acceptance test first

Before designing components, write a short definition of done. For example:

> Given a local repository and a task, the CLI runs Qwen through Ollama,
> executes JSON tool actions, stops on `submit`, and saves a trajectory and
> patch.

Anything not required for that test is a later milestone.

### Separate build milestones from experiment milestones

Use distinct deliverables:

1. Functional minimal agent.
2. Reliable tool behavior and integration tests.
3. Shell-versus-ACI pilot experiment.
4. Larger evaluation and analysis.

### Build a walking skeleton early

After defining the first model and action interfaces, connect a deliberately
minimal end-to-end loop. It may initially support only a fake model and one
safe tool. This reveals integration problems while the architecture is still
cheap to change.

### Front-load a decision checklist

At the beginning of each milestone, list unresolved semantic decisions. Resolve
them in one design session before implementation. Keep the chosen answers in a
short decision log.

### Timebox learning loops

For each core concept:

1. Spend a fixed period studying it.
2. Explain it back in your own words.
3. Record the decision and invariants.
4. Implement the smallest version.
5. Test it and move on.

Return for deeper study only if tests or integration reveal a real gap.

### Review from contracts and invariants

Before reviewing code, write the complete behavioral contract, boundary cases,
and invariants. Review all of them in one pass instead of reporting one local
symptom at a time.

### Use scheduled progress checks outside the README

Keep the README stable. Track milestones in a project plan or issue list and
review progress at least twice per week. At each review, compare completed
acceptance tests—not lines of code—with the remaining calendar.

### Preserve developer ownership without requiring manual repetition

The developer should continue to own architecture, semantics, and the first
implementation of learning-critical components. Codex can handle repetitive
tests, fixtures, formatting, documentation cleanup, and mechanical refactors
after the design is understood.

## Revised Scope and Deadline

New v0.1 deadline: **October 31, 2026**.

This plan assumes approximately 7-10 focused hours per week. The deadline
includes a functional local agent and a small pilot comparison, not a
statistically meaningful reproduction of the full SWE-agent paper.

### Definition of Done for October 31

- The local Ollama model can participate in a complete agent trajectory.
- The model emits exactly one JSON action per response.
- All 11 defined tools execute with repository-safe behavior.
- Tool observations are returned to the model through an explicit history
  representation.
- The loop has explicit malformed-action, step-limit, timeout, and termination
  behavior.
- A CLI runs a task against a selected repository.
- Each run records messages, actions, observations, token usage, runtime, and
  final patch.
- Automated unit and integration tests pass.
- At least three end-to-end tasks run successfully enough to support failure
  analysis.
- A small shell-versus-structured-ACI pilot is completed with fixed model and
  inference settings.

## Recovery Plan

### September 2-8: Complete navigation

- Add `window_overlap` semantics.
- Implement and test `goto`, `scroll_down`, and `scroll_up`.
- Implement and test `search_file`, `search_dir`, and `find_file`.

Exit criterion: the agent-facing interface can inspect and navigate a
repository without unrestricted shell commands.

### September 9-15: Complete mutation tools

- Decide exact `edit` and `create` semantics.
- Implement atomic writes and clear failure observations.
- Test boundaries, missing files, indentation preservation, and failed edits.

Exit criterion: files can be created and modified safely through the ACI.

### September 16-22: Complete execution tools

- Finalize Bash working-directory, timeout, output-limit, and standalone-`cd`
  behavior.
- Implement `bash` and `submit`.
- Add dispatcher-level integration tests for every tool.

Exit criterion: the complete tool surface works without an agent loop.

### September 23-29: Design prompt and history

- Decide the message representation and observation serialization.
- Define the system prompt, tool instructions, and JSON correction feedback.
- Decide what history is retained for v0.1 and how context overflow is
  prevented.

Exit criterion: a complete prompt can be inspected and explained before it is
sent to the model.

### September 30-October 6: Implement the agent loop

- Define the `Agent` responsibility and loop state.
- Implement model call, parse, dispatch, observation, and repeat.
- Implement step limits, parse-error feedback, and termination.
- Test with a deterministic fake model.

Exit criterion: a scripted fake-model trajectory completes end to end.

### October 7-13: CLI, logging, and Ollama integration

- Add CLI plumbing and run configuration.
- Save trajectories, token counts, runtime, and patches.
- Run the first complete task using local Qwen through Ollama.

Exit criterion: one real local-model trajectory runs from CLI invocation to
saved result.

### October 14-20: Reliability pass

- Run at least three small repository tasks.
- Classify failures in parsing, navigation, editing, looping, and termination.
- Fix implementation bugs without redesigning from isolated anecdotes.

Exit criterion: the agent completes multiple trajectories and failures are
recorded systematically.

### October 21-27: Pilot experiment

- Freeze model, prompt budget, sampling settings, and task set.
- Run shell-only and structured-ACI variants.
- Compare success, steps, tokens, runtime, invalid actions, and failed edits.

Exit criterion: produce a small results table and written failure analysis.

### October 28-31: Buffer and v0.1 closure

- Resolve critical integration issues.
- Verify setup from a clean environment.
- Update architecture and usage documentation.
- Explain the full system from task input to final patch.

Exit criterion: all October 31 definition-of-done items are checked explicitly.

## Schedule Control

Review the plan every Wednesday and Sunday. If a weekly exit criterion is
missed, do not silently move every later milestone. Reduce optional scope or
move the final date explicitly.

The first scope to cut is the comparative pilot experiment. The functional
agent, tests, trajectory logging, and understanding of the architecture remain
the v0.1 priority.
