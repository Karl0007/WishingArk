---
name: ark-verify
description: Post-exec human review and targeted fix loop. Collects user feedback on completed implementation, executes focused fixes, and verifies correctness. Use when user says "verify", "review the result", "check what was built", or invokes /ark:verify.
---

# /ark:verify

A lightweight fix loop after exec completes. User inspects the result, points out problems, Agent fixes them one by one.

**Input:** `/ark:verify [change-path]` — if omitted, uses most recently modified `docs/changes/**/progress.yaml`.

---

## Precondition

Read progress.yaml. Exec phase must be complete (`phases.execute.status: done` or post-completion steps I/J/K passed). If exec is still running or failed → HALT: "Exec not complete. Run /ark:exec first."

---

## Flow

```
1. Present summary
2. Collect feedback
3. Fix (per finding: test-if-testable → fix → run tests → retry-or-commit)
4. Loop or exit
```

### Step 1: Present Summary

Show the user what was built. Run these commands and present a concise overview:

```bash
git log --oneline {checkpoint_zero}..HEAD
git diff {checkpoint_zero}..HEAD --stat
```

Present:
- Task list with status (from progress.yaml)
- Files changed (from --stat)
- Commit history (from log)

Then ask: **"Anything to fix?"**

Do NOT read code files yourself. Do NOT analyze quality. The user decides what's wrong.

### Step 2: Collect Feedback

User provides feedback in natural language. For each piece of feedback, you record:

```yaml
# progress.yaml → phases.verify.findings[]
- id: 1
  feedback: "{user's words verbatim}"
  status: pending
```

User can provide one or multiple findings at once. Record all, then fix sequentially.

If user says nothing wrong → mark `phases.verify.status: approved`. Done.

### Step 3: Fix (per finding)

For each finding with `status: pending`:

1. **Checkpoint:** `git rev-parse HEAD` → store as finding's `pre_fix_ref`

2. **Determine if testable:** Can this feedback be expressed as a failing test? Heuristic:
   - Describes a behavior ("X should return Y", "crashes when Z") → testable
   - Describes style/naming/structure ("too confusing", "rename this") → not testable

3. **If testable → write failing test first:**

   Dispatch test agent:
   ```
   You are writing ONE test that proves a bug exists.

   User feedback: "{feedback verbatim}"
   Current code: the implementation is on disk. Read what you need.
   Existing test files: check what test framework and patterns are already in use.
   E2E framework available: {yes/no, from toolchain.e2e in progress.yaml}

   First: read `docs/specs/test-conventions.md` if it exists. Follow its conventions
   for fixtures, isolation, wait strategy, and anti-patterns.

   Rules:
   - Write exactly one test (or one describe block) that FAILS with the current code.
   - The test must directly encode the user's expectation.
   - PREFER E2E over unit test when the feedback describes user-facing behavior, a cross-module interaction, or an integration boundary. Only fall back to unit test when the feedback is purely about an isolated function's internal logic.
   - Do NOT write a unit test as a shortcut to avoid E2E setup. If E2E framework exists and the behavior is observable end-to-end, write E2E.
   - Do NOT fix the implementation. Only write the test.
   - When done, report: DONE: {test file}:{test name} (type: unit|e2e)
   - If this feedback is not expressible as a test, report: NOT_TESTABLE: {why}
   ```

   On DONE → run the test. It MUST fail (red). If it passes → the test is wrong or the issue doesn't exist. Report to user and skip this finding.

   On NOT_TESTABLE → proceed to fix without test (same as non-testable path).

4. **Dispatch fix agent:**

   ```
   You are fixing one specific issue in an existing implementation.

   User feedback: "{feedback verbatim}"
   Change context: read docs/changes/{name}/proposal.md for intent.
   Plan context: read docs/changes/{name}/plan.md for task structure.
   Current code: the implementation is on disk. Read what you need.
   {If test was written: "A failing test has been written: {test_file}:{test_name}. Make it pass."}

   Rules:
   - Fix ONLY what the user described. Do not refactor unrelated code.
   - If existing tests need updating to match the fix, update them.
   - Do NOT rewrite large sections. Minimal targeted change.
   - When done, report: DONE: {one-line summary of what changed}
   - If you cannot fix it, report: BLOCKED: {why}
   ```

5. **On DONE → run tests:**

   ```bash
   {toolchain.typecheck}
   {toolchain.lint}
   {toolchain.test}
   ```

   - **All pass** → commit:
     ```bash
     git add -A
     git commit -m "ark-verify({change_name}): fix #{finding_id} — {summary}"
     ```
     Mark finding `status: fixed`, record `fix_commit`.

   - **Failure** → dispatch fixer (one retry):
     ```
     Tests are failing after your fix. Fix the regression.
     Failing tests: {test names + error messages only}
     Do NOT modify the new test written for this finding.
     Do NOT revert the fix — adjust it to pass all tests.
     Report: DONE or BLOCKED.
     ```
     Run tests again after fixer. If pass → commit. If still failing → revert all uncommitted changes, mark `status: fix_failed, reason: {failure}`.

6. **On BLOCKED:** record `status: blocked, reason: {why}`. Continue to next finding.

### Step 4: Loop or Exit

Present results to user:
- Fixed findings (with commit refs + one-line summary)
- Blocked findings (with reasons)
- Failed findings (with failure info — what broke and why)

Ask: **"Anything else?"**

- User has more feedback → back to Step 2 (new round, increment round counter)
- User satisfied → mark `phases.verify.status: approved`. Done.
- Same finding fails 2 times across rounds → suggest: "This may need a redesign. Consider /ark:propose."

---

## State in progress.yaml

```yaml
phases:
  verify:
    status: in_progress | approved
    rounds:
      - round: 1
        findings:
          - id: 1
            feedback: "empty array throws instead of returning []"
            testable: true
            test_file: "src/parser.test.ts"
            status: fixed
            pre_fix_ref: abc123
            fix_commit: def456
          - id: 2
            feedback: "variable naming is confusing in parser"
            testable: false
            status: fixed
            pre_fix_ref: def456
            fix_commit: ghi789
          - id: 3
            feedback: "concurrent writes can corrupt state"
            testable: true
            test_file: "src/store.test.ts"
            status: fix_failed
            pre_fix_ref: ghi789
            reason: "fix caused 3 other tests to fail, retry also failed"
```

---

## Rules

- **You are NOT a reviewer.** Do not judge the implementation. Do not proactively find issues. The user tells you what's wrong.
- **One commit per finding.** Each fix is independently revertable.
- **Never roll back exec work.** Only revert verify-phase commits on test failure.
- **Toolchain is already configured.** Read it from progress.yaml. Do not re-detect.
- **Git is the audit trail.** Commit refs in progress.yaml = traceability. Don't rely on agent self-reporting.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I see other issues too, I'll fix those" | Only fix what the user asked. You are not a reviewer. |
| "The tests pass so the fix must be correct" | Tests passing is necessary but not sufficient. Show the user the diff. |
| "This fix is too big, I'll restructure" | Minimal change. If it needs restructuring, tell the user → new proposal. |
| "I'll skip the test run, it's a small change" | Always run tests. Small changes break things. |
| "The user's feedback is vague, I'll interpret" | Ask the user to clarify. Do NOT guess intent. |
| "A unit test is enough, E2E is overkill" | If the behavior is user-facing or cross-module and E2E exists, write E2E. Unit test is not a shortcut. |

---

## Integration with Pipeline

```
/ark:propose → /ark:plan → /ark:exec → /ark:verify → /ark:merge
                                              ↑
                                         you are here
                                         (lightweight, iterative)
```

Verify sits between exec and merge. It does NOT replace L3/L4 verification (those already ran in exec). It adds the human judgment layer that automation cannot provide.
