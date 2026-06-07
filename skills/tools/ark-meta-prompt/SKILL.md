---
name: ark-meta-prompt
description: Design high-quality prompts for dispatching work to other agents. Use when writing, reviewing, or improving sub-agent task prompts, workflow prompts, skill prompts, reviewer prompts, or any instruction that another AI agent must execute independently.
---

# Ark Meta Prompt

Write prompts that help another agent make good decisions without you supervising every step.

A good dispatch prompt is not a longer task description. It sets direction, taste, boundaries, method, and evidence.

## Core philosophy

```
Abstract goal sets direction.
Taste guides tradeoffs.
Minimal anchors prevent drift.
Evidence closes the loop.
```

Do not replace judgment with a long checklist. Do not rely on vague quality words alone.

## Process

### 1. Identify the failure mode

Before writing the prompt, ask:

```
How is this agent most likely to do the wrong thing?
```

Common failures:

- only passes the happy path;
- hardcodes the example instead of implementing the mechanism;
- over-abstracts and ships something that does not run;
- expands scope;
- fixes the symptom instead of the source;
- ignores existing seams or project language;
- produces output the next agent cannot consume.

The prompt's acceptance criteria must block the most likely failure.

### 2. Write the prompt shape

Use this structure unless the task is trivial:

```
# Target
Exact scope: files, modules, document, question, or diff to handle.

# Goal
The deliverable and the optimization direction behind it.

# Constraints
What must not be broken, expanded, skipped, or reinterpreted.

# Taste
1-3 task-specific preferences for a good solution.
Examples: prefer boring local changes, reuse existing seams, concentrate related rules, avoid speculative abstraction, keep downstream output easy to consume.

# Method
One high-leverage judgment move that addresses the likely failure mode.

# Acceptance
Concrete evidence of completion, output format/path, tests or checks, and blocker conditions.
```

### 3. Choose one judgment move

Pick one primary move. Do not make the agent run every test below.

- **Hardcode test** — If the implementation hardcoded the reference case, would a contrast case fail?
- **Deepening test** — Does this change concentrate related complexity behind a clearer interface, or spread it across callers?
- **Deletion test** — If this module disappeared, would complexity vanish or scatter into more places?
- **Source-of-truth test** — Where is the single source for this behavior? Is the prompt preventing duplicated rules?
- **Consumer test** — Can the next agent or user consume the output without asking follow-up questions?

Use other judgment moves when they fit better. The point is to give the agent one concrete way to think, not a rule encyclopedia.

### 4. Preserve high-level taste words

Words like "architecture health", "maintainability", "locality", "leverage", and "clarity" are useful. They give the agent taste.

But anchor them:

```
Weak: Keep architecture healthy.
Better: Keep architecture healthy by making the touched seam clearer and concentrating the rule in one place; show the touched seam and the evidence.
```

### 5. Require blocker behavior

A dispatch prompt should say when the agent must stop and report a blocker instead of improvising.

Good blocker triggers:

- required files or context cannot be found;
- the task conflicts with an explicit project decision;
- the requested output cannot be verified;
- the only apparent solution violates a constraint;
- the agent cannot produce output consumable by the next step.

## Self-check before dispatch

Before sending the prompt, verify:

- Target is bounded.
- Goal includes both deliverable and optimization direction.
- Constraints prevent the obvious bad shortcut.
- Taste is specific to this task, not generic filler.
- Method names one judgment move.
- Acceptance would catch the likely failure mode.
- Output shape is clear enough for the next agent to consume.

## Anti-patterns

These are weak only when they stand alone:

- "Implement X and keep architecture healthy."
- "Review this using best practices."
- "Research this thoroughly."
- "Improve the prompt."

Keep the high-level intent, then add anchors:

```
Implement X while keeping the touched seam easier to change.
Do not expand scope beyond Y.
Use the Deepening test.
Return changed files, verification output, and any blocker.
```
