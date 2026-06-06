---
name: ark-autoexec
description: Full pipeline automation — detect state, plan, confirm, execute. Orchestrates /ark:plan and /ark:exec as sub-steps, handles dependency checking between proposals, and supports --afk mode for zero-interaction runs. Use when user says "autoexec", "run everything", "auto", or invokes /ark:autoexec.
---

# /ark:autoexec

Full pipeline orchestrator: detect state → plan → confirm → execute.

**Autoexec drives the full change lifecycle.** Given a proposal, it plans, confirms with user, checks dependencies, and executes — delegating to `/ark:plan` and `/ark:exec` internally. It's the "just make it happen" command.

**Input:**
- `/ark:autoexec [change-path]` — run a specific change
- `/ark:autoexec --afk` — skip all confirmations (plan auto-approved, no dependency prompts)
- `/ark:autoexec` (no args) — ask user which change to run + what mode

---

## Entry Behavior

### No arguments provided

Ask the user:

```
Which change to run?
[list active changes from docs/changes/*/proposal.md that don't have status: done]

Mode?
A) Interactive — I'll confirm plan before executing (Recommended)
B) AFK — plan + execute without stopping. Only halt on failure.
```

### With arguments

- `/ark:autoexec feature-x` → interactive mode on `docs/changes/feature-x/`
- `/ark:autoexec feature-x --afk` → AFK mode on `docs/changes/feature-x/`

---

## State Detection

Read the change directory and determine current phase:

| State | Detected by | Action |
|---|---|---|
| No proposal.md | Directory empty or missing | HALT: "No proposal found. Run /ark:propose first." |
| proposal.md exists, no plan.md | proposal present, plan absent | → Step 1: Plan |
| plan.md exists, not confirmed | plan present, progress.yaml shows `plan: pending` | → Step 2: Confirm |
| plan.md confirmed, exec incomplete | progress.yaml shows `execute: in_progress` or `pending` | → Step 3: Execute |
| exec complete | progress.yaml shows `execute: done` | DONE: "Execution complete. Ready for /ark:merge." |

This makes autoexec **idempotent** — re-running picks up from wherever it left off.

---

## Step 1: Plan

### Dependency Check

Before planning, scan for cross-change dependencies:

1. Read current proposal's `## Constraints` for "Depends on: [other-change]"
2. Scan sibling proposals in `docs/changes/` for any that list THIS change as a dependency
3. Check if dependent changes are complete (progress.yaml status: done)

If dependencies are unmet:

```
⚠ Dependency check:

This change depends on:
- docs/changes/auth-refactor/ — status: executing (NOT complete)

Options:
A) Wait — come back after auth-refactor is done
B) Proceed anyway — I understand the risk
C) Show dependency details

[Your call:]
```

In AFK mode: proceed if the dependency's relevant outputs (files/types) already exist in the codebase. Otherwise halt.

### Run Plan

Spawn a sub-agent to run `/ark:plan` flow (isolates plan's heavy codebase reading from autoexec's context):

The plan agent will:
1. Load context (proposal + specs + CONTEXT.md)
2. Scan codebase
3. Decompose into tasks
4. Derive success criteria
5. Self-review
6. Doc-review audit

All plan skill rules apply. Output: `plan.md` written to the change directory.

**Do NOT run plan inline.** Plan reads many files and builds deep understanding — this would pollute autoexec's context. Always spawn as a sub-agent.

---

## Step 2: Confirm

### Interactive mode (default)

Present the plan to user:

```
## Plan Ready: [change-name]

[plan overview — task count, key files touched]

Tasks:
1. [name] — [goal summary]
2. [name] — [goal summary]
...

Approve and execute? (y/n/edit)
```

- **y** → mark plan confirmed in progress.yaml, proceed to Step 3
- **n** → ask what's wrong, loop back to planning
- **edit** → user specifies changes, apply, re-show

### AFK mode (--afk)

Skip confirmation. Plan is auto-approved. Proceed to Step 3.

**Doc-review in AFK mode:** Doc-review still runs (inside the plan sub-agent) as a quality check, but its result does NOT block execution:
- Pass → continue silently
- Fail → record issues in progress.yaml `afk_notes`, but still approve and continue. Do NOT stop to show the user.

**Discovery handling in AFK mode:** If plan's codebase scan emits a Discovery Brief (contradiction between proposal and code reality), auto-accept option A (expanded scope). Record in progress.yaml:

```yaml
afk_discoveries:
  - title: "Discovery title"
    impact: "How it affected the plan"
    auto_resolved: A  # accepted expanded scope
```

This ensures the user can review what was auto-decided after execution completes. If the Discovery is catastrophic (approach fundamentally impossible, not just expanded scope), plan will fail doc-review → HALT even in AFK mode.

---

## Step 2.5: Branch

After plan is confirmed (or auto-approved in AFK), ensure execution happens on the correct feature branch:

1. **Check current branch** — if already on `change/<name>` → skip (idempotent)
2. **Check working tree** — if there are uncommitted changes → HALT: "Uncommitted changes on current branch. Commit or stash before running autoexec."
3. **Check if branch exists** —
   - `change/<name>` already exists → `git checkout change/<name>` (resume previous progress)
   - Does not exist → `git checkout main && git checkout -b change/<name>` (create from main)
4. **Verify** — `git branch --show-current` matches expected name

Where `<name>` is the change directory name (e.g., `docs/changes/reference-lookup/` → `change/reference-lookup`).

**Why here?** Proposal and plan are written on main (they're documentation, shared knowledge). Code execution happens on a feature branch (isolates WIP, enables parallel changes, clean merge later).

---

## Step 3: Execute

**Spawn a sub-agent** to run `/ark:exec` flow (isolates execution loop from autoexec's context):

```
Run /ark:exec on docs/changes/{name}/.
Read .claude/skills/ark-exec/SKILL.md for your instructions.

The plan is confirmed and branch is ready.
Report back with: DONE (all tasks pass) or HALT (with reason).
```

**Do NOT run exec inline.** Exec manages a multi-task loop with retries — running inline would accumulate all task dispatches and results in autoexec's context. Always spawn as a sub-agent.

The exec agent will internally:
1. Pre-flight (verify baseline)
2. Task loop (spawn task-runners → verify → commit → repeat)
3. Final verification (L3: full test suite)
4. Proposal conformance review (L4: cumulative diff vs proposal.md)

All exec skill rules apply. Autoexec monitors for HALT or DONE result.

### On completion

```
## Autoexec Complete: [change-name]

Pipeline: proposal ✓ → plan ✓ → execute ✓ → conformance ✓
Tasks: N/N complete
Commits: [list]
L4 Conformance: PASS

Next: /ark:merge (when ready to integrate)
```

### On HALT (from exec)

Present 3 options to user:

```
## Autoexec Halted: [change-name]

Stopped at: Task N — [name]
Reason: [from exec HALT]

Options:
A) Retry — fix the issue and re-run from Task N
B) Revise plan — /ark:plan [change-path] to restructure
C) Abort — stop this change entirely

Resume: /ark:autoexec [change-path] (will continue from Task N)
```

- **A (Retry)** → user fixes manually, re-runs `/ark:autoexec` which resumes from current state
- **B (Revise plan)** → user runs `/ark:plan` to redo the plan, then re-runs `/ark:autoexec`
- **C (Abort)** → exit cleanly, display progress summary

---

## What Autoexec Does NOT Do

- **Propose** — autoexec starts from an existing proposal. Use `/ark:propose` first.
- **Merge** — autoexec stops after execution. Use `/ark:merge` to integrate.
- **Override plan failures** — if plan-checker fails 2x during planning, halt and ask user.
- **Ignore dependencies** — cross-change dependencies are checked, not silently skipped.
- **Run multiple changes in parallel** — one change at a time. For parallel, use separate sessions.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll run plan inline instead of spawning a sub-agent" | Plan reads many codebase files. Running inline pollutes your context. Always spawn. |
| "I'll run exec inline instead of spawning a sub-agent" | Exec manages a multi-task loop with retries. Running inline accumulates all task history in your context. Always spawn. |
| "I'll read plan.md to track progress during execution" | Read progress.yaml instead — it's the state file. plan.md is for sub-agents. |
| "I'll stop and ask the user about doc-review results in AFK mode" | AFK means no stops except HALT. Doc-review issues get logged, not presented. |
| "I'll skip dependency check to save time" | Dependencies exist for a reason. Missing types/APIs = exec failures. |
| "Plan failed doc-review but it's probably fine" | In interactive mode, fix the plan. In AFK mode, log and continue. |
| "User said --afk so I'll skip ALL checks" | AFK skips confirmations, not safety checks. Pre-flight and dependency checks still run. |
| "I'll auto-propose too" | Propose requires human intent. Autoexec automates execution, not ideation. |

---

## Guardrails

- **Idempotent** — re-running always picks up from current state, never re-does completed work
- **All heavy work in sub-agents** — plan (sub-agent), exec (sub-agent). Autoexec only manages state + user interaction
- **Dependency-aware** — checks cross-change dependencies before planning
- **Confirmation by default** — plan shown to user before execution (unless --afk)
- **AFK = no confirmations, not no safety** — pre-flight, dependency checks, and HALT conditions still apply
- **No proposal creation** — autoexec starts from existing proposal.md, never creates one
