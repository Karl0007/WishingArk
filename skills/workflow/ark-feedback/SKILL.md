---
name: ark-feedback
description: Write user feedback into progress.yaml for the reviewer to consume. Two modes — quick (write directly) or deep (analyze context first). Use when user says "feedback", "I want to tell the reviewer", or invokes /ark:feedback.
---

# /ark:feedback

Write user feedback to the current in-progress task's `user_feedback` field in progress.yaml. The reviewer (Step F) reads this before evaluating.

**Input:** `/ark:feedback [message]` — quick mode. `/ark:feedback deep [message]` — deep mode.

---

## Step 1: Locate state

1. If no change path given, find most recently modified `docs/changes/**/progress.yaml`.
2. Read progress.yaml, find the task with `status: in_progress`.
3. If no in-progress task → HALT: "No in-progress task found."

## Step 2: Determine mode

- If first argument is `deep` → deep mode. Rest of args = user's problem description.
- Otherwise (with or without message) → ask the user: quick or deep?
  - If user picks quick → write the message to `user_feedback`. If no message was given, ask for it.
  - If user picks deep → enter deep mode with the message as initial problem description.

---

## Quick Mode

Write the user's message directly to the task's `user_feedback` field in progress.yaml. Done.

If `user_feedback` already has content, append with a separator:
```
previous feedback | new feedback
```

Output: "Feedback written to Task {N}."

---

## Deep Mode

### 2a. Gather context

Read (you do this yourself — no sub-agent):
1. `docs/changes/{name}/proposal.md` — understand the intent
2. `docs/changes/{name}/plan.md` — find the current task's SC and Constraints
3. Run `git diff {checkpoint}` — see what was implemented
4. Run `git diff {test_checkpoint}` — see what test files exist vs what changed

### 2b. Analyze with user

Present a summary to the user:
```
Task {N}: {name}
SC coverage: {which SC appear satisfied, which look problematic}
Test concerns: {any test modifications, missing coverage, wrong assumptions}
Implementation concerns: {any visible issues in the diff}
```

Ask the user: "What specifically feels wrong?" (they may have already said it in the initial message).

### 2c. Generate structured feedback

Based on the user's concern + your analysis, write a structured feedback:
```
[User concern]: {original user input}
[Analysis]: {what the diff shows about this concern}
[Recommendation]: {specific action — fix test X, change implementation of Y, add test for Z}
[Affected SC]: {which SC are impacted}
```

### 2d. Write and confirm

Write the structured feedback to `user_feedback` in progress.yaml.
Show the user what was written. Done.

---

## Rules

- Never modify code files. This skill only writes to progress.yaml.
- Never run the pipeline. Just write feedback for the next exec run.
- Deep mode reads code but does NOT make judgments about PASS/FAIL — that's the reviewer's job. It only helps the user articulate their concern precisely.
