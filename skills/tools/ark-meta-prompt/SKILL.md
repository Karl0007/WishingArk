---
name: ark-meta-prompt
description: Design high-quality prompts for dispatching work to other agents. Use when writing, reviewing, or improving sub-agent task prompts, workflow prompts, skill prompts, reviewer prompts, or any instruction that another AI agent must execute independently.
---

# Ark Meta Prompt

Write dispatch prompts that help another agent make good decisions without you supervising every step.

A good dispatch prompt is not a longer task description. It sets direction, taste, boundaries, method, and evidence. For hard tasks, it also gives the receiving agent ownership to discover what the prompt writer did not enumerate.

## Core philosophy

```text
Abstract goal sets direction.
Taste guides tradeoffs.
Minimal anchors prevent drift.
Evidence closes the loop.
Ownership unlocks discovery.
```

Do not replace judgment with a long checklist. Do not rely on vague quality words alone.

The best prompt gives the agent the fewest anchors needed to understand:

- what outcome it owns;
- what must not be broken;
- how to think when the task is underspecified;
- what evidence proves the work is consumable by the next person or agent.

## Choose the prompt mode

Use the lightest mode that fits the risk.

### Direct mode

Use when the task is narrow and the risks are already clear.

```text
Implement X while preserving Y.
Use the existing Z seam.
Return changed files and verification output.
```

### Discovery-first mode

Use when the task touches architecture, APIs, persistence, runtime behavior, security, workflow orchestration, important docs, or any boundary where the named issue may be only a symptom.

The prompt should keep known non-negotiable constraints explicit. Do not try to enumerate every speculative edge case; make the agent responsible for finding adjacent failures inside the touched boundary and directly connected seams.

```text
You are not just completing the listed task; you own the underlying outcome.
Ownership is bounded by the prompt's Target, Goal, and Constraints. Do not expand implementation scope without reporting a blocker or asking for a new task.
Before acting, identify the rule, decision, claim, or invariant that makes the work correct.
Search for adjacent ways it could fail inside the touched boundary and directly connected seams.
Do the smallest clean work.
Before finishing, review your own output as if another agent produced it.
Report what you discovered, what you changed, how you verified it, and any blocker.
```

## Prompt shape

Use this structure unless the task is trivial:

```text
# Target
Exact scope: files, modules, document, question, or diff to handle.

# Goal
The deliverable and the optimization direction behind it.

# Constraints
What must not be broken, expanded, guessed, skipped, or reinterpreted.

# Taste
1-3 task-specific preferences for a good solution.
Examples: prefer boring local changes, reuse existing seams, concentrate related rules, avoid speculative abstraction, keep downstream output easy to consume.

# Method
One high-leverage judgment move or discovery loop that addresses the likely failure mode.

# Acceptance
Concrete evidence of completion, output format/path, tests or checks, discovered risks, and blocker conditions.
```

Keep sections short. If the prompt becomes a long checklist, keep known non-negotiables explicit and replace speculative edge-case lists with a discovery instruction.

## Failure-mode step

Before writing the prompt, ask:

```text
How is this agent most likely to do the wrong thing?
```

Common failures:

- only passes the happy path;
- hardcodes the example instead of implementing the mechanism;
- over-abstracts and ships something that does not run;
- expands scope;
- fixes the symptom instead of the source;
- ignores existing seams or project language;
- accepts hidden assumptions as facts;
- produces output the next agent cannot consume.

For narrow work, block that failure directly in acceptance.

For uncertain or load-bearing work, ask the receiving agent to discover the failure modes too:

```text
The listed cases are symptoms, not the full boundary. Derive the underlying rule and search for sibling paths inside the touched boundary and directly connected seams that violate it.
```

## Judgment moves

Pick one primary move. The point is to give the agent a concrete way to think, not a rule encyclopedia.

Core moves:

- **Hardcode test** — If the implementation hardcoded the reference case, would a contrast case fail?
- **Deepening test** — Does this change concentrate related complexity behind a clearer interface, or spread it across callers?
- **Source-of-truth test** — Where is the single source for this behavior? Is the prompt preventing duplicated rules?
- **Consumer test** — Can the next agent or user consume the output without asking follow-up questions?
- **Invariant discovery test** — What rule, decision, claim, or invariant is the named issue evidence for? Where else can it fail inside the touched boundary or directly connected seams?

Advanced moves for load-bearing work:

- **Naive-patch failure test** — What is the obvious small patch, and why would it still be wrong?
- **Mutation-order test** — For durable systems, what writes happen here? Are invalid states rejected before files, artifacts, branches, checkpoints, journals, or resumes are mutated?
- **Fallback quarantine test** — If legacy behavior remains, is it isolated from the normal path and tested as compatibility only?
- **Deletion test** — If this abstraction disappeared, would complexity vanish or scatter into callers?

Use other judgment moves when they fit better. Choose one primary move; add an advanced move only when the task's risk needs it.

## Tiny reusable patterns
Use these as ingredients, not full prompts to paste blindly. Keep only the lines that matter for the task.

### General ownership pattern

```text
You are not just completing the listed task; you own the underlying outcome.

Before acting, identify the rule, decision, claim, or invariant that makes the work correct, then look for adjacent failures inside the touched boundary and directly connected seams.

Do the smallest useful work. Avoid hardcoding the example, hiding assumptions, or leaving the normal path dependent on fallback behavior.

Before finishing, review your own output as if another agent produced it.

Report what you discovered, what you changed, how you verified it, and any blocker.
```

### Load-bearing implementation pattern

```text
You are not just fixing the listed bug; you own this boundary.

Before editing, derive the invariant, search for adjacent violations inside the touched boundary and directly connected seams, and explain why the naive patch is insufficient.

Implement the smallest clean fix. Do not hardcode the example, let fallback remain the normal path, or mutate durable state before validation.

Before finishing, hostile-review your own diff and fix any issue found.

Report the invariant, sibling paths searched, discovered issues, fixes, negative tests/checks, and verification output.
```

## Acceptance writing

Acceptance should require evidence, not ceremony.

Weak:

```text
Implement X and keep architecture healthy.
```

Better:

```text
Implement X while making the touched seam easier to change.
Use the Source-of-truth test.
Return changed files, verification output, and any blocker.
```

For discovery-first work, acceptance should also require the discoveries that changed the implementation, verification, or blocker decision:

```text
Report the underlying rule, adjacent failures that affected the work, naive patch rejected if relevant, tests/checks added from discovery, and verification output.
```

For review-only tasks, require findings that explain the violated rule or risk, not style commentary.

For document tasks, require the Consumer test: what can the next agent or reader do after reading this without asking follow-up questions?

## Blocker behavior

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
- Method names one judgment move or discovery loop.
- Acceptance would catch the likely failure mode.
- For hard tasks, the prompt gives ownership rather than only chores.
- Output shape is clear enough for the next agent to consume.

## Anti-patterns

These are weak when they stand alone:

- "Implement X and keep architecture healthy."
- "Review this using best practices."
- "Research this thoroughly."
- "Fix these issues" without asking for adjacent failures.
- Long checklist with no ownership.

Keep the high-level intent, then add anchors:

```text
Implement X while keeping the touched seam easier to change.
Do not expand scope beyond Y.
Use the Deepening test.
Return changed files, verification output, and any blocker.
```
