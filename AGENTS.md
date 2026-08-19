I am building a minimal coding agent from scratch, inspired by SWE-agent, to understand how coding-agent systems actually work.  

You may help me implement boilerplate, tests, Docker infrastructure, logging, CLI code, refactoring, debugging, and repetitive engineering work.

However, do not make the core architectural decisions for me. In particular, do not decide the agent-loop architecture, Agent-Computer Interface (ACI) / tool design, context-management strategy, prompting/policy, termination policy, experiment design, or evaluation methodology.

For those core areas, you may explain possible approaches, tradeoffs, and relevant concepts, but ask me to make the final design decision before implementing it.

Do not introduce LangChain, LangGraph, or another agent framework unless I explicitly request it. I want to implement the fundamental agent machinery myself, primarily in Python.

Before making substantial changes, explain what you intend to implement, which files you will modify, and how the implementation follows the design decisions I have already made.
