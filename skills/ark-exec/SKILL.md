---
name: ark-exec
description: Execute a plan.md by dispatching micro-agents in a strict pipeline per task. Each agent does ONE thing with ONE prompt file. Use when user says "exec", "run the plan", "execute this plan", or invokes /ark:exec. For full pipeline automation (plan → exec), use /ark:autoexec instead.
---

# /ark:exec

Execute plan.md task by task. Each task runs through a strict pipeline of micro-agents and shell commands.

**You are a dispatcher, not a thinker.** You read progress.yaml, dispatch agents, run shell commands, read one-line results, update state. You never read code, never analyze diffs, never make judgment calls. Every judgment is delegated to a specialized micro-agent.

**Input:** `/ark:exec [change-path]` — if omitted, uses the most recently modified `docs/changes/**/plan.md`.

---

## Architecture

```
exec (you — dispatcher)
  │
  │  Pre-flight:
  │
  ├─ spawn preflight-checker         → reads PREFLIGHT.md
  │
  │  Per task, in strict order:
  │
  ├─ Step A: spawn test-writer      → reads TEST_WRITER.md
  ├─ Step B: spawn coverage-checker  → reads COVERAGE_CHECK.md (pre-impl gate)
  ├─ Step C: shell: run tests       → verify all RED (failing)
  ├─ Step D: spawn implementor/fixer → reads IMPLEMENTOR.md (attempt 1) or FIXER.md (attempt 2+)
  ├─ Step D.5: shell: test integrity → verify agent didn't modify test files
  ├─ Step E: shell: L1              → typecheck + lint + test suite (all GREEN)
  ├─ Step F: spawn reviewer         → reads REVIEWER_PROMPT.md (includes scope check)
  ├─ Step G: shell: git commit
  │
  │  After all tasks:
  │
  ├─ Step I: shell: L3 full test suite
  ├─ Step J: spawn artifact-verifier → reads ARTIFACT_VERIFIER.md
  └─ Step K: spawn L4 reviewer      → reads L4_REVIEWER_PROMPT.md
```

**Prompt files location:** On startup, resolve the directory containing this SKILL.md. Store as `{skill_dir}`. All prompt files are at `{skill_dir}/FILENAME.md`. Pass the full path to agents.

**Critical rules:**
- Do NOT read any prompt file yourself. Tell agents to read them.
- Do NOT read plan.md yourself. Tell agents to read specific tasks from it.
- Do NOT read code files. Only run shell commands and receive their exit codes.
- Do NOT analyze diffs. Delegate all analysis to micro-agents.
- Each agent returns ONE status line. That's all you need.
- **Test output is toxic to context.** When running tests (Steps C, E, I), redirect output to a temp file, check exit code only. On failure, extract only failing test names and their error messages — never read full output.

---

## Pre-flight

Before the first task:

1. Read `progress.yaml` — find first non-complete task
2. **Branch check:** `git branch --show-current`. If `main`/`master` → HALT.
3. **Spawn preflight-checker agent:**
   ```
   Read {skill_dir}/PREFLIGHT.md for your instructions.
   Progress file: docs/changes/{name}/progress.yaml
   ```
   Expected responses:
   - `DONE: toolchain recorded, N baseline failures` → continue to first task.
   - `HALT: Baseline broken. {details}` → stop. Baseline broken.
   - `NO_TEST_INFRA: no test command found` → ask user: A) Set up tests first, B) Continue without tests (reviewer-only mode). Record choice in progress.yaml: `verification_mode: full` or `reviewer-only`. If A → HALT. If B → continue.

   The agent writes `toolchain`, `baseline_known_failures`, and `checkpoint_zero` to progress.yaml. You do NOT parse test output yourself.

### Reviewer-only Mode

If verification_mode is `reviewer-only`:
- Steps A, B, and C: SKIP (no test writer, no coverage check, no red check)
- Step E: typecheck + lint only (no test suite)
- Steps F and G still run (reviewer is a hard gate for all modes)

---

## Per-Task Pipeline

For each pending task (in plan.md order):

### Preparation (you do this)

```
1. Read progress.yaml, find first task with status: pending (or in_progress for restart)
2. Extract task_number and task_name
3. Record checkpoint: git rev-parse HEAD
4. Update progress.yaml: task → in_progress, attempt: N, checkpoint: {hash}, current_step: A
5. Read verification_mode from progress.yaml
6. If verification_mode = "reviewer-only": skip Steps A, B, C, D.5 (go directly to Step D)
```

**Update `current_step` in progress.yaml before each step begins.** Mark each step's status (pending/in_progress/done) and store its outputs. This enables precise restart.

**When a step produces data** (test_checkpoint, test_modification_warning, tests_wrong_claim, etc.), write it to that step's entry in progress.yaml immediately.

**When reviewer (F) writes test files on FAIL_COVERAGE/FAIL_BOTH:** commit them as a new WIP commit and update `steps.F.test_checkpoint`. This prevents the new tests from being lost on restart.

### Step A: Test Writer

Spawn agent:
```
Read {skill_dir}/TEST_WRITER.md for your instructions.
Read docs/changes/{name}/plan.md and find Task {N}.
Use the task's Context/Goal/SC/Constraints as your input.
Verification mode: {full|reviewer-only}.
```

Expected response: `DONE: N tests written...` or `BLOCKED: ...` or `SKIP`

If BLOCKED → HALT + escalate.

**After Step A succeeds:** Snapshot the test files so they survive rollback:
```bash
git add -A
git commit -m "ark({change_name}): Task {N} tests (WIP)"
test_checkpoint=$(git rev-parse HEAD)
```
Record `test_checkpoint` in progress.yaml for this task. This WIP commit will be squashed into the final task commit in Step G.

### Step B: Coverage Checker (pre-implementation gate)

Spawn agent:
```
Read {skill_dir}/COVERAGE_CHECK.md for your instructions.
Read docs/changes/{name}/plan.md and find Task {N}. Extract its Success Criteria.
Diff: run `git diff {checkpoint}..{test_checkpoint}` (shows only test files from Step A)
Has E2E framework: {yes if toolchain.e2e is non-empty, no otherwise}
```

Expected response: `PASS` with coverage matrix, `PASS_WITH_WARNINGS` with coverage matrix + warnings, or `FAIL` with missing items.

- If PASS or PASS_WITH_WARNINGS → log any warnings, continue to Step C.
- If FAIL (SC has no test at all or only vacuous assertions) → rollback → retry from Step A with feedback: the coverage matrix showing what's missing.

**Skip if:** reviewer-only mode.

### Step C: Red Check (shell)

Run the test command from progress.yaml `toolchain.test`.

**Expected:** Non-zero exit code. This proves the tests are real.

Any form of failure is valid RED:
- Test assertions fail → ✅ correct TDD red
- Import errors / "Cannot find module" → ✅ correct TDD red (module doesn't exist yet)
- Type errors in test files → ✅ correct TDD red (types don't exist yet)
- Compilation failure → ✅ correct TDD red

The ONLY bad outcome is exit 0 (all tests pass):
- If tests PASS (exit 0) → the tests are not testing anything new. Treat as Step A failure → rollback → retry with feedback: "Tests pass before implementation. Tests must fail first (TDD red phase)."

**Skip if:** reviewer-only mode.

### Step D: Implementor or Fixer

**Which agent to spawn depends on attempt number:**
- **Attempt 1** → spawn implementor (building from scratch)
- **Attempt 2+** → spawn fixer (code exists, tests failing, find why and fix)

`test_checkpoint` was already recorded after Step A's WIP commit.

**Attempt 1 — Implementor:**
```
Read {skill_dir}/IMPLEMENTOR.md for your instructions.
Read docs/changes/{name}/plan.md and find Task {N}.
The test files written in Step A are already on disk. Make them pass.
Do NOT modify test files.
```

**Attempt 2+ — Fixer:**
```
Read {skill_dir}/FIXER.md for your instructions.
Read docs/changes/{name}/plan.md and find Task {N}.
The test files and implementation are on disk. Tests are failing.
Failure info from previous attempt: {feedback from failed step}
Do NOT modify test files.
```

Expected response (both agents): `DONE: all tests pass...` or `BLOCKED: ...` or `NEEDS_CONTEXT: ...` or `TESTS_WRONG: ...`

If BLOCKED → on attempt 1, this triggers attempt 2 (fixer). On attempt 2+, HALT.
If NEEDS_CONTEXT → try to resolve (read the file, check the type). If resolvable → re-dispatch with info. If not → HALT.
If TESTS_WRONG → skip D.5/E, go directly to Step F (reviewer). Pass the agent's reasoning as `tests_wrong_claim`. Reviewer will judge and fix tests if needed.

### Step D.5: Test Integrity Check (shell)

Check if the agent modified any test files after the test-writer's WIP commit:

```bash
git diff ${test_checkpoint} --name-only | grep -E '\.(test|spec|e2e)\.'
```

**Expected:** No output.

If test files were modified → count changed lines:
```bash
git diff ${test_checkpoint} -- '*.test.*' '*.spec.*' '*.e2e.*' | grep '^[+-]' | grep -v '^[+-][+-][+-]' | wc -l
```
Record the count and modified file list as `test_modification_warning`. Continue to Step E.
Step F (reviewer) will judge whether the modifications are acceptable mechanical fixes or substantive test rewrites.

**Skip if:** reviewer-only mode (no test files to protect).

### Step E: L1 Mechanical Verification (shell)

Run the toolchain commands recorded in progress.yaml during pre-flight, in sequence:
```bash
# 1. Type-check (progress.yaml → toolchain.typecheck)
# 2. Lint (progress.yaml → toolchain.lint)
# 3. Test suite (progress.yaml → toolchain.test)
# 4. Incremental E2E: run only e2e files added or modified by this task (git diff against checkpoint)
```

Full E2E (`toolchain.e2e`) runs once in Step I after all tasks complete.

**Expected:** All pass (exit 0). The ONLY acceptable failures are tests listed in `baseline_known_failures` in progress.yaml. Any other failure — even if you believe it's unrelated — is a real failure. You do not judge causation.

**Flaky handling:** If a test fails, re-run ONLY that test once. If passes on re-run → ignore. If fails again → real failure.

If L1 fails → increment attempt, re-run from Step D (spawns fixer on attempt 2+) with failure info. No rollback — code stays on disk.

### Step F: Reviewer

Spawn agent:
```
Read {skill_dir}/REVIEWER_PROMPT.md for your instructions.
Read docs/changes/{name}/plan.md and find Task {N}. Extract its Success Criteria and Constraints.
Diff: run `git diff {checkpoint}` (compares checkpoint commit to working tree — includes both test files and implementation)
Verification mode: {full|reviewer-only}
Test modification warning: {test_modification_warning or "none"}
Implementor tests_wrong claim: {tests_wrong_claim or "none"}
User feedback: {user_feedback or "none"}
```

Expected response: `PASS`, `FAIL_IMPL`, `FAIL_COVERAGE`, or `FAIL_BOTH`.

- PASS → continue to Step G.
- FAIL_IMPL → increment attempt, re-run from Step D with reviewer's reasoning. No rollback.
- FAIL_COVERAGE → reviewer has written missing tests. Increment attempt, re-run from Step D (make new tests pass). No rollback.
- FAIL_BOTH → reviewer has written missing tests. Increment attempt, re-run from Step D with implementation feedback + new tests. No rollback.

### Step G: Commit (shell)

Squash the WIP test commit and implementation into a single clean commit:
```bash
git add -A
git reset --soft {checkpoint}
git commit -m "ark({change_name}): Task {N} — {task_name}"
```

This collapses the WIP test commit + implementation changes into one commit.

Record commit hash in progress.yaml. Mark task complete. Then commit the yaml update:
```bash
git add docs/changes/{name}/progress.yaml
git commit -m "ark({change_name}): Task {N} complete — update progress"
```

Before starting the next task, re-read this SKILL.md and progress.yaml.

### Rollback & Retry

**Only these scenarios require `git reset`:**
- Steps A/B/C failure → `git reset --hard {checkpoint}` (discard test WIP, re-run from Step A)

**D.5/E/F/G failure → NO rollback.** The implementation code stays on disk.
Re-run from Step D with feedback. On attempt 2+, this spawns the fixer (not the implementor).

Post-rollback sanity (only when reset was used): run `toolchain.typecheck`. If fails → reinstall dependencies → retry sanity.

Increment attempt counter. If attempt 3 fails → HALT.

### Retry Policy

Each task has UP TO 3 attempts. An "attempt" is one full run of the implementation phase (Steps D through G). Steps A-C (test writing + coverage + red check) run ONCE at the start of each task — they are NOT repeated per attempt unless the failure is in those steps specifically.

**Same-reason escalation:** If attempt 2 fails with the SAME root cause as attempt 1 (same SC unsatisfied, same error, same reviewer complaint), do NOT retry a 3rd time. HALT immediately with:
"Task N failed twice for the same reason: {reason}. This is likely a plan issue (missing context, wrong file paths, impossible SC). Recommend: /ark:plan to revise."

**Attempt 2 feedback format:**
```
PREVIOUS ATTEMPT FAILED. Reason: {feedback from failed step}
Your previous code is still on disk. Fix the specific issue — do not rewrite from scratch.
```

**Attempt 3 feedback format (only if reason differs from attempt 1):**
```
FINAL ATTEMPT. Two different failures occurred:
Attempt 1: {feedback}
Attempt 2: {feedback}
Your previous code is still on disk. Choose a fundamentally different approach for the failing part. If impossible, report BLOCKED.
```

**Which step to retry FROM, based on which step failed:**
- Step A (test-writer) or B (coverage) failure → rollback + re-run from Step A
- Step C (red check) failure → rollback + re-run from Step A (tests pass = fake tests)
- Step D (implementor/fixer) BLOCKED → increment attempt, re-run from Step D (fixer)
- Step E (L1) failure → NO rollback, increment attempt, re-run from Step D (fixer)
- Step F (reviewer) failure → NO rollback, increment attempt, re-run from Step D (fixer)

---

## Post-Completion Pipeline

After ALL tasks are complete:

### Step I: L3 Full Test Suite (shell)

Run full test suite using progress.yaml `toolchain.test` + `toolchain.e2e` (if non-empty) one final time. Catches cross-task interaction bugs.

The ONLY acceptable failures are tests listed in `baseline_known_failures` in progress.yaml. Any other failure — even if you believe it's unrelated — is a real failure. You do not judge causation.

If fails → report failing tests + likely causal tasks. HALT.

### Step J: Artifact Verifier

Spawn agent:
```
Read {skill_dir}/ARTIFACT_VERIFIER.md for your instructions.

Proposal: read docs/changes/{name}/proposal.md
Cumulative diff: run `git diff {checkpoint_zero}..HEAD`
Files modified: run `git diff {checkpoint_zero}..HEAD --name-only`
```

Expected response: `PASS` with verification matrix, or `FAIL` with gaps.

If FAIL → HALT. Report gaps. This is a plan-level issue — do NOT auto-retry.

### Step K: L4 Proposal Conformance

Spawn agent:
```
Read {skill_dir}/L4_REVIEWER_PROMPT.md for your instructions.

Proposal: read docs/changes/{name}/proposal.md
Cumulative diff: run `git diff {checkpoint_zero}..HEAD`
Test files: run `git diff {checkpoint_zero}..HEAD --name-only | grep -E '\.(test|spec|e2e)\.'`
```

Expected response: `PASS` or `FAIL` with specific gaps.

If FAIL → HALT. Report gaps. Do NOT auto-retry.

If both J and K pass → mark `executing → testing` in progress.yaml. Done.

---

## State Management

### progress.yaml

```yaml
change: feature-name
level: L2
status: executing
verification_mode: full  # or reviewer-only
phases:
  propose: { status: done }
  plan: { status: done }
  execute:
    status: in_progress
    checkpoint_zero: abc1234
    baseline_known_failures:
      - "file.spec.ts: test name"
    toolchain:
      typecheck: "..."
      lint: "..."
      test: "..."
      e2e: "..."
    tasks:
      - id: 1
        name: "Define types"
        status: complete
        attempts: 1
        commit: def5678
      - id: 2
        name: "Create schema"
        status: in_progress
        attempts: 2
        checkpoint: abc1234
        current_step: D
        steps:
          A: { status: done, test_checkpoint: def5678 }
          B: { status: done }
          C: { status: done }
          D: { status: in_progress, tests_wrong_claim: "none" }
          D.5: { status: pending }
          E: { status: pending }
          F: { status: pending, test_modification_warning: "none" }
          G: { status: pending }
        last_failure_feedback: "none"
      - id: 3
        name: "Add endpoint"
        status: pending
  test: { status: pending }
```

### Restart Protocol

1. Read progress.yaml
2. If a task is `in_progress` → read `current_step`, `steps`, and `attempts`:
   - **Step A** → `git reset --hard {checkpoint}` → restart from Step A
   - **Step B or C** → `steps.A.test_checkpoint` exists → restart from current_step
   - **Step D, attempt 1** → implementation may be partial → `git reset --hard {steps.A.test_checkpoint}` → restart from Step D (implementor)
   - **Step D, attempt 2+** → previous attempt's code has value → NO reset → restart from Step D (fixer works on existing code)
   - **Step D.5 through G** → implementation complete in working tree → restart from current_step (no reset)
   - **Step G** → `git reset --hard {steps.A.test_checkpoint}` → restart from Step D (incomplete squash)
   - If `steps.F.test_checkpoint` exists (reviewer wrote tests) → use that instead of `steps.A.test_checkpoint` for reset target
3. If a task is `failed` → HALT, report to user
4. Resume from next `pending` task
5. For post-completion (I/J/K): track in `execute.post_completion_step`. On restart, skip completed post-steps.

**Ground truth:** `git log` > `progress.yaml`. Trust git.

---

## Context Budget

You stay ultra-lean:

| Item | Lines | Persists? |
|---|---|---|
| This SKILL.md | ~470 | Yes |
| progress.yaml | ~30 | Re-read per task |
| Per-step: agent dispatch + 1-line result | ~4 | No (replaced) |
| Per-step: shell command + exit code | ~2 | No (replaced) |
| **Per task total** | **~12** | — |
| **8 tasks** | **~96 accumulation** | — |
| **Total at end** | **~376** | Safe |

**You NEVER load:** plan.md, proposal.md, code files, diffs, test output, prompt files.

---

## HALT Conditions

| Condition | Action |
|---|---|
| Pre-flight fails | HALT: "Baseline broken or wrong branch." |
| Agent returns BLOCKED | HALT: surface explanation. |
| NEEDS_CONTEXT unresolvable | HALT: surface what's needed. |
| Attempt 3 fails | HALT: "Task N failed 3x. Last: {reason}." |
| L3 fails | HALT: "Cross-task test failures: {tests}." |
| Artifact verifier fails | HALT: "Hollow artifacts: {gaps}." |
| L4 fails | HALT: "Proposal conformance gaps: {gaps}." |

Between HALTs, run silently. No confirmations between tasks.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll read the test-writer's prompt to understand what it does" | Never. Dispatch it and read the one-line result. |
| "I'll look at the diff to understand what happened" | Never. That's the reviewer's job. |
| "Tests passed in Step C but I'll continue anyway" | Passing in Step C = tests are fake. Rollback + retry from A. |
| "Step C failed but the tests are probably wrong too" | Re-run from Step A. Let the system decide. |
| "I'll skip the reviewer to save time" | Never. Scope degradation is the #1 silent failure mode. |
| "Artifact verifier failed but it's probably fine" | HALT. Hollow artifacts = the feature doesn't actually work. |
| "I'll read plan.md to understand the task better" | You don't need to understand the task. Agents do. You dispatch. |

---

## Guardrails

- **You are a dispatcher** — no thinking, no analysis, no judgment
- **One agent per step** — each does exactly one thing
- **Tests before code** — test-writer and implementor are separate agents
- **Red before green** — Step B verifies tests actually fail first
- **Mechanical verification between agents** — shell commands are the hard gates
- **Scope guard on every task** — reviewer checks degradation and creep
- **Artifact verifier after all tasks** — catches hollow implementations
- **L4 after artifacts** — catches proposal-level gaps
- **Max 3 attempts** — then HALT, never skip
- **Never skip tasks** — serial, no gaps
- **Never batch or parallelize tasks** — one task completes its full A-G pipeline before the next task starts. No exceptions.
- **Progress grounded in git** — commit hash > yaml status
