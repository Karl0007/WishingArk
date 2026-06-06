---
name: ark-merge
description: Archive change docs, distill research into docs/specs/ADRs, update affected specs (fix drift proactively), merge terminology, rebase onto main, run merge review via sub-agent, and land with user confirmation. Use when user says "merge", "land this", "merge to main", or invokes /ark:merge.
---

# /ark:merge

Rebase → content work → review → land. The knowledge consolidation checkpoint.

**Merge is not "push code to main."** It's the phase where ephemeral change knowledge (research, decisions, terminology) gets consolidated into permanent project knowledge (specs, ADRs, CONTEXT.md), and only THEN does the code land on main.

**Input:**
- `/ark:merge [change-path]` — merge a specific change (interactive)
- `/ark:merge --afk` — automatic prep, stop at user confirmation
- `/ark:merge` (no args) — detect active change on current branch, interactive mode

---

## Entry Behavior

### No arguments

1. Check current branch — extract change name from `change/<name>` pattern
2. If on main → HALT: "Not on a feature branch. Which change to merge?"
3. If branch matches → use corresponding `docs/changes/<name>/`

### With arguments

- `/ark:merge feature-x` → merge `docs/changes/feature-x/` (verify branch matches)
- `/ark:merge feature-x --afk` → AFK mode

### Entry Conditions

All must be true:

- `progress.yaml` shows `execute: done` (or `review: done` if review phase exists)
- On branch `change/<name>` matching the change
- Working tree clean (`git status --porcelain` is empty)

If not met → tell user what's missing and which command to run.

---

## State Detection (Idempotent Resume)

Read `progress.yaml` merge section and resume from current state:

| State | Detected by | Action |
|---|---|---|
| No merge section | `phases.merge` absent or `pending` | → Phase 1: Rebase |
| Rebase done, content pending | `merge.rebase: done` | → Phase 2: Content Work |
| Content done, review pending | `merge.archived: done` | → Phase 3: Review |
| Review done, not landed | `merge.review: pass` | → Phase 4: Land |
| Landed | `merge.merged: true` | DONE |

Re-running always picks up from current state. Never redoes completed work.

---

## Phase 1: Rebase

### 1.1 Fetch and rebase

```bash
git fetch origin main
git rebase origin/main
```

Record `main_sha_at_rebase` in progress.yaml (used in Phase 4 to detect if main moved).

### 1.2 Conflict resolution

**No conflicts** → proceed to 1.3.

**Conflicts detected:**

Interactive mode:
```
## Rebase Conflict: [change-name]

Conflicting files:
- [file list]

Conflict type:
- Code: [files] — AI will propose resolution, you verify
- Specs/docs: [files] — will take main's version, redo our updates in Phase 2
- CONTEXT.md — auto-resolve (append-only, keep both sides)

Show conflict details? (y/n)
```

AI-assisted resolution strategy by file type:

| File type | Strategy |
|---|---|
| Code (`src/`, `lib/`, etc.) | AI proposes resolution → test must pass → if test fails, escalate to user |
| Specs (`docs/specs/`) | Accept main's version (ours will be rewritten in Phase 2 with current context) |
| CONTEXT.md | Keep both additions (append-only invariant makes this safe) |
| Config / package.json | AI proposes → user verifies (config conflicts are high-risk) |

AFK mode:
- Attempt auto-resolution using strategies above
- Run tests after each resolved file
- If ANY test fails post-resolution → HALT: "Rebase conflict resolution failed tests. Manual intervention needed."
- Max 1 re-attempt with different resolution approach before HALT

### 1.3 Post-rebase test gate

Run full test suite after rebase:

```bash
# Type-check + lint + tests (same as exec pre-flight)
```

- PASS → record in progress.yaml, proceed to Phase 2
- FAIL → rebase introduced a regression. Options:
  - A) Show failing tests, help user debug
  - B) Abort rebase (`git rebase --abort`), escalate

**Why test here?** If code conflicts were resolved incorrectly, catch it NOW before building content work on top of broken code.

---

## Phase 2: Content Work

All content work happens on the rebased branch, seeing current main state. Each sub-step produces a commit.

### 2.1 Research Distillation

**Skip if:** no `research.md` exists in the change directory.

Read `research.md` and extract:

1. **Key findings** — facts discovered that affect future work
2. **Decisions made** — with rationale (ADR candidates)
3. **Rejected approaches** — with why (prevents re-exploration)

**ADR creation:** If a finding meets the ADR threshold (defined in `ark.md § ADR Threshold`), create `docs/adr/NNN-<title>.md`. Otherwise, findings flow into spec updates (2.2).

Read the change's `research.md` file. Watch for contradictions — flag them in the summary.

### 2.2 Spec Updates (Proactive Review)

This is NOT "only add what this change introduced." This is a **spec health pass** on every spec file touched by or related to this change.

For each module affected by the change:

1. Read the relevant `docs/specs/[module]/` files
2. Read the actual current code
3. **Supplement**: add documentation for new behavior introduced by this change
4. **Fix drift**: correct ANY outdated descriptions you find — even if they predate this change
5. **Improve**: add missing "How to Add/Change" recipes, update Best Practices if the change revealed better patterns

Scope boundary: only review specs for modules THIS change touched. Don't go hunting across the whole tree.

**Output:** Updated spec files with clear commit message noting what was supplemented vs. what was drift-fixed.

Interactive mode: show diff of each spec update, allow user to tweak.
AFK mode: auto-apply, flag `UNCERTAIN` items in progress.yaml for post-merge review.

### 2.2.1 Lesson Consolidation

**Skip if:** `docs/changes/{name}/lessons.md` does not exist (user skipped /ark:learn).

If lessons.md exists, consolidate each lesson into its target spec:

1. Read `docs/changes/{name}/lessons.md`
2. For each lesson:
   a. Read the `target_spec` file
   b. Find or create a `## Lessons` section in that spec
   c. Write the lesson in this format:

   ```markdown
   <!-- LESSON_KEYWORD: keyword1, keyword2, keyword3 -->
   - **Rule**: {actionable_rule}
   - **Why**: {evidence — one line}
   ```

   The `LESSON_KEYWORD` comment enables agents to grep across all specs:
   ```bash
   grep -r "LESSON_KEYWORD.*cancel" docs/specs/
   ```

**Interactive mode (not AFK):** present each lesson to the user before applying:
```
Lesson L1: "{summary}"
Rule: "{actionable_rule}"
Target: {target_spec}

Apply this lesson? (y/n/edit)
```
- y → apply
- n → skip (lesson is NOT applied, stays only in archive)
- edit → user provides revised wording, apply that instead

**AFK mode:** apply all lessons automatically. Record in progress.yaml:
```yaml
merge.content.lessons_applied: [L1, L2]
merge.content.lessons_skipped: []
```

Do NOT delete lessons.md — it gets archived with the rest of the change directory in step 2.4.

### 2.3 Terminology Merge

Read the change directory for new terms (in `research.md`, `proposal.md`, code comments, or explicit `terms` section in progress.yaml).

Update `CONTEXT.md`:
- Append new terms to the appropriate section
- **Cross-check**: if a term already exists with a different definition → flag as conflict, ask user (interactive) or record in `merge.term_conflicts` (AFK)
- Never delete existing terms
- Never redefine existing terms without user approval

### 2.4 Archive

Create archive entry:

```
docs/archive/YYYY-MM/<change-name>/
└── summary.md
```

**summary.md template:**

```markdown
# [Change Name]

## What
[1-3 sentences: what was done and why]

## Key Decisions
- [decision]: [rationale]
- ...

## Modules Affected
- [module]: [what changed]

## ADRs Produced
- docs/adr/NNN-title.md (if any)

## Artifacts
- [N] commits on branch change/[name]
- Specs updated: [list]
- Terms added: [list]
```

After archive is written, **remove** the change directory: `docs/changes/<name>/` → deleted. Git history preserves everything. The archive summary is the permanent record.

**Commit:** single commit for all Phase 2 work:
```
ark(<change-name>): merge prep — specs updated, research distilled, archived
```

---

## Phase 3: Merge Review

Spawn a **sub-agent reviewer** with zero prior context. It receives:

### Reviewer Input

```
You are a merge reviewer. Determine if this branch is ready to land on main.

## Change Summary
{from docs/archive/summary.md — just written in Phase 2}

## Checks to perform

### 1. Doc-Code Drift (most important)
For each spec file updated in Phase 2:
- Read the spec
- Read the corresponding code
- Verify: does the spec accurately describe what the code does?
- Flag: any behavior in code not covered by spec? Any spec claims not true in code?

### 2. Test Regression
- Run full test suite
- Compare test count: now vs checkpoint_zero (from exec phase)
- Flag: any tests removed? Any coverage decrease?

### 3. History Hygiene
- Check commit messages follow project convention (read docs/specs/tech.md § Commit Format)
- Flag: WIP commits, debug leftovers, TODO(merge) markers
- Flag: files that shouldn't be committed (.env, large binaries, temp files)

### 4. Completeness
- Archive exists at docs/archive/YYYY-MM/<name>/summary.md
- CONTEXT.md was updated (if new terms exist)
- Specs were updated for affected modules
- No orphaned references (spec links to deleted files, imports from removed modules)

## Output format

For each check:
  PASS | FAIL | WARN
  [details if not PASS]

Overall: READY | NOT_READY
[blocking issues list if NOT_READY]
```

### Handling Review Results

- **All PASS** → proceed to Phase 4
- **Any FAIL** → show to user (interactive) or HALT (AFK)
  - Doc-code drift FAIL → loop back to 2.2, fix the spec, re-review
  - Test regression FAIL → escalate to user (this shouldn't happen if exec worked correctly)
  - Hygiene FAIL → auto-fix if trivial (remove debug log), escalate if not
  - Completeness FAIL → loop back to relevant Phase 2 step
- **WARN only** → show warnings, proceed (interactive) / record and proceed (AFK)

**Max review iterations:** 2. If still FAIL after 2 fix-review cycles → HALT, escalate.

---

## Phase 4: Land

### 4.1 Fast-forward check

```bash
git fetch origin main
# Check: has main moved since our rebase?
if [ $(git rev-parse origin/main) != $main_sha_at_rebase ]; then
  # Main moved — need to re-rebase
fi
```

**If main moved:**
1. Re-rebase (Phase 2 content commits usually land cleanly since they touch different files)
2. Run tests
3. Re-run Phase 3 review (lightweight — only re-check, not redo content)
4. Max 2 re-rebase attempts. After that: "Main is moving too fast. Coordinate with team or retry later."

**If main hasn't moved:** proceed.

### 4.2 User Confirmation (MANDATORY — even in AFK)

```
## Merge Ready: [change-name]

Pipeline: propose ✓ → plan ✓ → execute ✓ → merge prep ✓ → review ✓

Summary:
- Commits: [N] (feature) + [1] (merge prep)
- Specs updated: [list]
- ADRs created: [list or "none"]
- Terms added: [N] new terms
- Archive: docs/archive/YYYY-MM/[name]/summary.md

Review result: READY
[any WARNs listed here]

Merge into main? (y/n)
```

- **y** → proceed to 4.3
- **n** → ask what's wrong, park

**Why always require confirmation?** Merging to main is an irreversible shared-state mutation. `--afk` means "don't bother me with intermediate decisions," not "do whatever you want to main."

### 4.3 Merge

```bash
git checkout main
git merge --ff-only change/<name>
```

If `--ff-only` fails (shouldn't, since we just rebased) → abort, re-rebase path.

### 4.4 Cleanup

```bash
git branch -d change/<name>           # delete local feature branch
git push origin --delete change/<name> # delete remote (if exists)
```

### 4.5 Update State

```yaml
# progress.yaml (now in archive, but update before moving)
phases:
  merge: { status: done }
status: done
```

### Completion Message

```
## Merged: [change-name]

Pipeline complete: propose ✓ → plan ✓ → execute ✓ → merge ✓ → done ✓

Branch change/[name] merged into main and deleted.
Archive: docs/archive/YYYY-MM/[name]/summary.md

Knowledge consolidated:
- [N] spec files updated
- [N] ADRs created
- [N] terms added to CONTEXT.md
```

---

## Edge Cases

| Situation | Handling |
|---|---|
| Empty change (execution found nothing needed) | No code diff. Skip rebase test gate (nothing to regress). Archive with disposition: `abandoned`. Record WHY in summary. |
| Docs-only change | No code tests to run. Drift check is inverted: does code match the new docs? Rebase conflicts more likely on shared doc files. |
| Change modifies ark framework itself | Warn: "This change modifies the workflow framework. Spec-update and drift-check may be unreliable. Extra manual review recommended." |
| Extremely stale branch (main diverged 50+ commits) | Detect via `git rev-list --count HEAD..origin/main`. If >50: warn user, suggest manual rebase review. Proceed but with extra caution. |
| Archive path collision | Change names are unique (enforced at proposal time). Month boundary collision is impossible for same change. |
| Previous merge attempt partially completed | Idempotent: state machine resumes from last completed step. Phase 2 sub-steps overwrite (not duplicate) partial work. |
| Remote branch doesn't exist | Skip `git push origin --delete`. Local cleanup only. |
| User says "no" at confirmation | Park. User can fix issues and re-run `/ark:merge` (resumes from Phase 4). |
| Tests pass locally but CI will fail | Not merge's problem — CI is downstream. But warn if `.github/workflows/` exists and user hasn't pushed. |

---

## State Schema

Addition to `progress.yaml` during merge:

```yaml
phases:
  merge:
    status: in_progress        # pending | in_progress | done
    pre_merge_sha: abc1234     # escape hatch: branch HEAD before any merge work
    rebase:
      status: done             # pending | in_progress | conflict | done
      main_sha: def5678        # main HEAD at rebase time (detect drift in Phase 4)
      attempts: 1
    tests_post_rebase: pass    # pending | pass | fail
    content:
      research_distilled: done # pending | in_progress | done | skipped
      specs_updated: done      # pending | in_progress | done
      terms_merged: done       # pending | in_progress | done
      archived: done           # pending | in_progress | done
    review:
      status: pass             # pending | in_progress | pass | fail
      iterations: 1            # max 2
      warnings: []             # non-blocking issues
    user_confirmed: false
    merged: false
```

---

## What Merge Does NOT Do

- **Execute code** — all code was written in /ark:exec. Merge consolidates knowledge and lands.
- **Create proposals or plans** — those are inputs, not outputs of merge.
- **Fix failing tests** — if tests fail post-rebase, the conflict resolution was wrong. Escalate, don't silently patch.
- **Force merge on conflicts** — conflicts require resolution (AI or human). Never `--force`.
- **Skip user confirmation** — even `--afk` stops at "merge into main?" Every time.
- **Delete git history** — docs/archive/summary.md is a human-readable index. Full history is always in git.
- **Update specs for unrelated modules** — proactive drift fixing is scoped to modules THIS change touched.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll merge without rebasing, rebase is optional" | Rebase ensures clean history and catches integration issues. Never skip. |
| "I'll auto-merge in AFK mode without user confirmation" | Merge to main ALWAYS requires user confirmation. Non-negotiable. |
| "Spec update is just adding what this change did" | Also fix outdated descriptions you find. Proactive spec health, not just changelog. |
| "I'll skip archive since git has the history" | Archive provides human-navigable summaries. Git history is raw, not indexed. |
| "Tests failed post-rebase but I'll fix them in a new commit" | That means conflict resolution was wrong. Abort and redo, don't pile fixes on top. |
| "I'll do content work before rebase to save time" | Content written against stale main = self-inflicted rebase conflicts. Always rebase first. |
| "Review found drift but it's minor, I'll skip fixing" | Drift compounds. Fix now or never. Loop back to Phase 2. |
| "I'll merge without running the reviewer" | Reviewer catches spec contradictions and drift. Worth the cost for L2+ changes. |
| "CONTEXT.md conflict — I'll pick our version" | Append-only: keep BOTH sides' additions. Never discard terms from main. |
| "I'll skip spec review for the change's modules" | The whole point of merge is knowledge consolidation. Specs must reflect current reality. |

---

## Guardrails

- **Rebase first, content after** — all knowledge work sees current main state
- **Post-rebase test gate** — catch broken conflict resolution before building on it
- **Proactive spec health** — fix ALL drift found in touched modules, not just current change
- **Sub-agent review** — independent verification of merge readiness
- **User confirmation mandatory** — even AFK mode stops before merging to main
- **Idempotent state machine** — re-running resumes from last completed step
- **Bounded retries** — max 2 re-rebases, max 2 review iterations, then escalate
- **Pre-merge escape hatch** — `pre_merge_sha` allows full rollback of merge attempt
- **Append-only terms** — CONTEXT.md grows, never shrinks during merge
- **Archive before delete** — summary.md written before change directory is removed
