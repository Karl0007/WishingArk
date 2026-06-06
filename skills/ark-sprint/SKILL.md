---
name: ark-sprint
description: Execute a user-provided roadmap step by step — dispatch agents to implement, then zero-context agents to review. Use when user says "sprint", "run this", or invokes /ark:sprint.
---

# /ark:sprint

Read the roadmap. For each step:

1. **Dispatch a sub-agent to implement it.** Pass the step description. Don't write code yourself.
2. **Dispatch a new sub-agent to review the diff.** Zero context sub-agent. Pass the step description. Don't review code yourself.
3. **Commit and move on.**