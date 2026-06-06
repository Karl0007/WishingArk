---
name: ark-plan
description: Transform proposal.md into an executable plan.md. Dispatches 5 micro-agents in sequence — planner (scan + decompose), SC writer (reverse-engineer criteria), plan checker (text audit), hack checker (framework bypass detection), feasibility checker (logical consistency). Use when user says "plan", "break this down", "create plan", or invokes /ark:plan.
---

# /ark:plan

Transform a proposal into an executable plan. You are a dispatcher — you spawn agents, relay results, and manage the loop.

**You do NOT plan.** You do NOT write SC. You do NOT review the plan. Each of those is a separate agent.

**Input:** `/ark:plan [change-path]` — if omitted, uses the most recently modified `docs/changes/**/proposal.md`.

---

## Architecture

```
plan (you — dispatcher)
  │
  ├─ Step 1: spawn planner        → writes docs/changes/{name}/draft.md
  ├─ Step 1b: [handle discoveries if any]
  ├─ Step 2: spawn sc-writer      → writes docs/changes/{name}/sc-draft.md
  ├─ Step 3: assemble plan.md     (shell: merge draft.md + sc-draft.md → plan.md)
  ├─ Step 4: spawn plan-checker   → text audit (hard gate, max 2 rounds)
  ├─ Step 5: spawn hack-checker   → framework bypass detection (soft limit, max 2 rounds → warning)
  ├─ Step 6: spawn feasibility-checker → logical consistency (hard gate, max 2 rounds)
  ├─ Step 7: [if FAIL → feed blockers back, re-run pipeline; rounds counted per checker independently]
  ├─ Step 8: present to user for confirmation
  └─ Step 9: cleanup (shell: rm draft.md sc-draft.md)
```

**Prompt files location:** Same directory as this SKILL.md file.

**Critical rules:**
- Do NOT read the codebase yourself. Planner scans it.
- Do NOT write SC yourself. SC-writer writes them.
- Do NOT review the plan yourself. Plan-checker reviews it.
- Do NOT read prompt files yourself. Tell agents to read them.
- **All intermediate artifacts go to disk, not your context.** You dispatch agents that write files. You never hold plan content in your conversation.

---

## File Flow

All intermediate files are written to `docs/changes/{name}/`:

| File | Written by | Read by | Lifetime |
|---|---|---|---|
| `draft.md` | planner (Step 1) | sc-writer (Step 2) | Deleted after final plan.md written |
| `sc-draft.md` | sc-writer (Step 2) | assemble step (Step 3) | Deleted after final plan.md written |
| `plan.md` | assemble step (Step 3) | checkers (Step 4-6), user (Step 8) | Permanent |

**Why files instead of context?** Each iteration of planner+sc-writer+checker produces ~300 lines. With 2 rounds that's ~600 lines of stale content in your context. Writing to disk keeps your context at ~200 lines regardless of iteration count.

---

## Entry Conditions

- `docs/changes/<name>/proposal.md` exists
- Doc-review has passed (or user explicitly skipped)

If missing → tell user to run `/ark:propose` first.

---

## State Management

Plan tracks its progress in `docs/changes/{name}/progress.yaml` so it can resume after interruption.

### Plan phase states

```yaml
phases:
  plan:
    status: in_progress        # pending | in_progress | done
    step: checking             # current step (see below)
    rounds:                    # independent counters per checker
      plan_checker: 1          # 1 or 2
      hack_checker: 0          # 0 = not yet run
      feasibility_checker: 0
    checker_blockers: |        # last checker feedback (if any)
      [SC Quality] Task 2: vacuous SC "works correctly"
      [File Paths] Task 1: src/foo.ts does not exist
```

**Step values:** `drafting` → `sc_writing` → `assembling` → `checking` → `hack_checking` → `feasibility_checking` → `revising` → `confirmed`

### Resume Protocol

On every invocation, read `progress.yaml` first:

| State found | Files on disk | Action |
|---|---|---|
| No plan phase / status: pending | — | Start from Step 1 |
| step: drafting | draft.md exists | Skip Step 1, go to Step 2 (SC-writer) |
| step: drafting | draft.md missing | Re-run Step 1 (planner crashed) |
| step: sc_writing | sc-draft.md exists | Skip Step 2, go to Step 3 (assemble) |
| step: sc_writing | sc-draft.md missing | Re-run Step 2 (sc-writer crashed) |
| step: assembling | plan.md exists | Skip Step 3, go to Step 4 (plan checker) |
| step: checking | plan.md exists | Re-run Step 4 (plan checker crashed mid-run) |
| step: hack_checking | plan.md exists | Re-run Step 5 (hack checker crashed mid-run) |
| step: feasibility_checking | plan.md exists | Re-run Step 6 (feasibility checker crashed mid-run) |
| step: revising | checker_blockers present, relevant round < 2 | Feed blockers to Step 1 or 2, then assemble + re-check |
| step: revising | checker_blockers present, relevant round = 2 | Present to user with known issues (that checker exhausted) |
| step: confirmed | plan.md exists | Already done. Tell user: "Plan already confirmed." |

**Ground truth hierarchy:** Files on disk > progress.yaml. If progress says `sc_writing` but `plan.md` already exists, trust the file.

### State Updates

Update progress.yaml at each step transition:

```
Before Step 1 (planner):     step: drafting
After Step 1 completes:      step: sc_writing      (draft.md confirmed on disk)
After Step 2 completes:      step: assembling       (sc-draft.md confirmed on disk)
After Step 3 completes:      step: checking         (plan.md confirmed on disk)
After Step 4 (checker PASS): step: hack_checking
After Step 4 (checker FAIL): step: revising, rounds.plan_checker: N, checker_blockers: {blockers}
After Step 5 (hack PASS):    step: feasibility_checking
After Step 5 (hack FAIL, round < 2): step: revising, rounds.hack_checker: N, checker_blockers: {blockers}
After Step 5 (hack FAIL, round = 2): step: feasibility_checking (soft limit — hacks become warnings)
After Step 6 (feas PASS):    step: confirmed (but first go through Step 7 to persist any warnings)
After Step 6 (feas FAIL):    step: revising, rounds.feasibility_checker: N, checker_blockers: {blockers}
```

---

## Step 1: Planner

Spawn agent:
```
Read PLANNER.md (same directory as this skill) for your instructions.
Read docs/changes/{name}/proposal.md as the proposal.
Scan the codebase and produce a plan draft.
Write your output to docs/changes/{name}/draft.md.
```

Expected response: `DONE: draft written to docs/changes/{name}/draft.md` or a Discovery Brief.

**Do NOT ask for the draft content.** The planner writes it to disk. You only need the status line.

If BLOCKED → HALT + escalate.

### Handling Discoveries

If the planner returns a Discovery Brief (inline, not in the file):
1. Present it to the user exactly as-is (do NOT summarize or editorialize)
2. Wait for user decision (A/B/C/D)
3. If A (accept expanded scope) → re-dispatch planner with: "Discovery resolved: user chose option A. Proceed with expanded scope. Write to docs/changes/{name}/draft.md."
4. If B (reduce scope) → re-dispatch with: "Discovery resolved: user chose option B. Skip the affected part. Write to docs/changes/{name}/draft.md."
5. If C (split) → HALT: "User chose to split. Run /ark:propose for the prerequisite change first."
6. If D (rethink) → HALT: "User chose to rethink. Run /ark:propose to revise the approach."

---

## Step 2: SC Writer

(Step 1b — Handling Discoveries — is documented within Step 1 above.)

Spawn agent:
```
Read SC_WRITER.md (same directory as this skill) for your instructions.
Read docs/changes/{name}/proposal.md — use the What and What-NOT sections.
Read docs/changes/{name}/draft.md — this is the plan draft with tasks (no SC yet).
Write your SC output to docs/changes/{name}/sc-draft.md.
```

Expected response: `DONE: SC written to docs/changes/{name}/sc-draft.md` + any warning flags.

**Do NOT ask for SC content.** The SC-writer writes it to disk.

If SC-writer flags warnings → note the warning text (one line) for later.

---

## Step 3: Assemble plan.md

Run shell command to merge the two files:
```bash
# Read draft.md, for each "### Task N:" section, insert the corresponding SC
# from sc-draft.md after the Goal line and before the Constraints line.
# Write result to docs/changes/{name}/plan.md
```

This is a mechanical merge. If the formats are clean, you can do it with a simple script or by spawning a lightweight agent:
```
Read docs/changes/{name}/draft.md and docs/changes/{name}/sc-draft.md.
Merge them: insert each task's SC (from sc-draft.md) into the corresponding task
in draft.md, after **Goal:** and before **Constraints:**.
Write the merged result to docs/changes/{name}/plan.md.
Do NOT modify any content. Just merge.
```

**Do NOT read the merged file yourself.** Plan-checker reads it.

---

## Step 4: Plan Checker

Spawn agent:
```
Read PLAN_CHECKER.md (same directory as this skill) for your instructions.
Read docs/changes/{name}/proposal.md as the proposal.
Read docs/changes/{name}/plan.md as the plan to verify.
Read CONTEXT.md at project root (if it exists).
Return your verification table and verdict.
```

Expected response: verification table with PASS/FAIL verdict + blockers/warnings (returned inline — this is the one piece of content you DO read, because you need to route the blockers).

If FAIL → go to Step 7 (handle checker result). **Clear all other checker state** (reset `rounds.hack_checker` and `rounds.feasibility_checker` to 0). Do NOT run hack/feasibility checkers on a plan that failed text audit.

---

## Step 5: Hack Checker

Only runs after Plan Checker passes.

Spawn agent:
```
Read HACK_CHECKER.md (same directory as this skill) for your instructions.
Read docs/changes/{name}/proposal.md as the approved proposal.
Read docs/changes/{name}/plan.md as the plan to verify.
Scan framework code referenced in the plan's Scan Report as needed.
Return your verdict.
```

Expected response: PASS/FAIL verdict + hacks found (inline).

If FAIL (round < 2) → route to Step 1 (planner) with feedback:
"Hack checker found framework bypasses: {hacks}. Use the framework's native mechanism instead. Overwrite docs/changes/{name}/draft.md."
**Clear all other checker state** (reset `rounds.plan_checker` and `rounds.feasibility_checker` to 0) since the plan has been rewritten.
Then re-run Step 2 (SC-writer), Step 3 (assemble), and re-run from Step 4 (Plan Checker).

If FAIL (round = 2) → **soft limit**: record hacks as warnings, set step to `feasibility_checking`, and proceed to Feasibility Checker. Hacks will be appended to plan.md's `## Plan Check` section if the plan ultimately passes.

---

## Step 6: Feasibility Checker

Only runs after Hack Checker passes or exhausts its 2 rounds (soft limit).

Spawn agent:
```
Read FEASIBILITY_CHECKER.md (same directory as this skill) for your instructions.
Read docs/changes/{name}/plan.md as the plan to verify.
Scan code files referenced in the plan's Scan Report as needed.
Return your verdict.
```

Expected response: PASS/FAIL verdict + blockers (inline).

If FAIL → route to Step 1 (planner) — the planner must revise the Goal or Constraints to resolve the contradiction. **Clear all upstream checker state** (reset `rounds.plan_checker` and `rounds.hack_checker` to 0) since the plan has been rewritten and previous verdicts are stale.

Max 2 feasibility-check rounds. If planner cannot resolve contradictions after 2 rounds, present to user with known issues.

---

## Step 7: Handle Checker Result

All three checkers (Step 4, 5, 6) route through here after their final verdict in a given pipeline run.

### If all checkers PASS (or hack checker exhausted as soft limit):
If there are any warnings (including hack checker soft-limit warnings), append a `## Plan Check` section to plan.md with the warnings (so exec agents can see them). Then proceed to Step 8 (user confirmation).

### If FAIL (round < 2 for that checker):
Read the blockers from checker's response. Determine which agent needs to fix what:

- **Proposal Coverage blocker** → re-run Step 1 (planner) with feedback:
  "Plan checker found coverage gaps: {blockers}. Add tasks to cover these proposal items. Overwrite docs/changes/{name}/draft.md."
- **SC Quality blocker** → re-run Step 2 (SC-writer) with feedback:
  "Plan checker found weak SC: {blockers}. Rewrite these SC to be concrete and testable. Overwrite docs/changes/{name}/sc-draft.md."
- **File Path blocker** → re-run Step 1 (planner) with feedback:
  "Plan checker found phantom files: {blockers}. Verify all paths against codebase. Overwrite docs/changes/{name}/draft.md."
- **Scope Reduction blocker** → re-run Step 1 (planner) with feedback:
  "Plan checker found scope reduction: {blockers}. Do NOT downgrade these requirements. Overwrite docs/changes/{name}/draft.md."
- **Self-Containment blocker** → re-run Step 1 (planner) with feedback:
  "Plan checker found cross-task references: {blockers}. Each task must stand alone. Overwrite docs/changes/{name}/draft.md."
- **Context Compliance blocker** → re-run Step 1 (planner) with feedback:
  "Plan checker found context violations: {blockers}. Respect locked decisions. Overwrite docs/changes/{name}/draft.md."
- **Multiple types** → re-run Step 1 (planner) with all blockers. After planner writes revised draft.md,
  re-run Step 2 (SC-writer) on the new draft. Then re-run Step 3 (assemble) and Step 4 (checker).

Note: on each re-run, the agent overwrites the same file. Previous versions are gone — no stale data in your context or on disk.

**Stale state rule:** When any checker fails and the planner rewrites draft.md, reset ALL other checker round counters to 0 (not just downstream — upstream too). The rewritten plan invalidates all previous verdicts.

### If FAIL (round = 2 for Plan Checker or Feasibility Checker):
Present plan summary to user WITH the remaining blockers noted.
(Hack Checker round = 2 is handled as soft limit in Step 5 — it does NOT escalate here.)
```
## Plan Ready (with known issues)

The plan checker found issues that couldn't be resolved in 2 rounds:

{remaining blockers from checker's response — the only content you hold}

Options:
A) Approve anyway — proceed with these known issues
B) Edit — tell me what to change
C) Reject — rethink the approach
```

---

## Step 8: User Confirmation

Present a summary (do NOT paste the full plan — it's on disk, user can read it):
```
## Plan Ready: [change-name]

File: docs/changes/{name}/plan.md
Tasks: N tasks, key files: [list from checker's output or task names]

Plan checker: PASS ✓ (or: PASS with N warnings)

Approve and execute? (y/n/edit)
```

- **y** → update progress.yaml, proceed to Step 9 (cleanup)
- **n** → ask what's wrong, determine which agent to re-run
- **edit** → user specifies changes. Do NOT edit plan.md yourself. Re-run Step 1 (planner) with user's feedback, then Step 2 (SC-writer), Step 3 (assemble), Step 4 (Plan Checker), Step 5 (Hack Checker), Step 6 (Feasibility Checker). Re-present.

---

## Step 9: Cleanup

After user approves:

```bash
rm -f docs/changes/{name}/draft.md docs/changes/{name}/sc-draft.md
```

Then commit: `git add docs/changes/{name}/plan.md docs/changes/{name}/progress.yaml && git commit`

---

## Context Budget

You stay ultra-lean because all artifacts go to disk:

| Item | Lines | Persists? |
|---|---|---|
| This SKILL.md | ~380 | Yes |
| Planner status line | ~1 | No (replaced) |
| SC-writer status line | ~1 | No (replaced) |
| Checker verdict + blockers | ~30 | Replaced each round |
| **Total at any point** | **~412** | — |

**What you NEVER hold in context:**
- Plan draft content (planner writes to `draft.md`)
- SC content (sc-writer writes to `sc-draft.md`)
- Assembled plan (written to `plan.md`)
- Codebase files, CONTEXT.md (agents read these)
- Prompt files (agents read these)

**2-round iteration budget:** Still ~412 lines. The old approach would be ~960 lines after 2 rounds.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll scan the codebase to understand the project" | Planner scans it. You dispatch. |
| "The SC look weak, I'll improve them" | Plan-checker catches weak SC. Don't editorialize. |
| "I'll add a constraint the planner missed" | Re-run planner with feedback. Don't edit the plan yourself. |
| "Checker found issues, I'll fix them myself" | Re-run the responsible agent with feedback. |
| "The plan is probably fine, I'll skip the checker" | Never. Checker is a hard gate. No exceptions. |
| "Checker failed twice, I'll fix it myself on round 3" | Present to user with known issues. Let them decide. Each checker gets max 2 rounds independently. |

---

## Guardrails

- **You are a dispatcher** — spawn agents, relay results, manage the loop
- **Planner produces tasks without SC** — clean separation of concerns
- **SC-writer reverse-engineers from proposal** — not from task Goals
- **Plan-checker is adversarial** — assumes plan will fail until proven otherwise
- **Max 2 rounds per checker** — each checker has its own independent counter, then escalate to user
- **File paths mechanically verified** — checker checks filesystem, not just text
- **Scope reduction is a BLOCKER** — not a warning, not acceptable
- **Each agent reads its own prompt file** — you never read prompt files
- **Discovery halts the pipeline** — user must decide before planning continues
