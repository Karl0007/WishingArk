# Go Sequence

Compile conversation into proposal.md. Triggered when user says "go", "write it", "compile", "ship it", or when grill naturally concludes.

**Write for downstream agents (plan/execute/review) who will act on this proposal without asking the user again.** If they'd need to guess, you haven't been specific enough.

---

## Step 1: Compile

Read these files from `docs/changes/<name>/` (if they exist):
- `draft.md` — the discuss output (What / What-NOT / Constraints)
- `grill.md` — decisions and constraints added during grill

These are your primary sources. Use conversation context only to fill gaps not captured in the files.

Walk through the files + conversation. Extract:
- All decisions made (explicit + accepted assumptions)
- Requirements stated in user messages
- What-NOT items (things explicitly excluded — boundaries that prevent scope creep)
- Constraints surfaced during discussion

## Step 2: Reconcile

If the conversation contradicts itself (early decision vs. late decision):
- Later wins (unless user explicitly preserved the earlier version)
- Surface reconciliations: "You said X early on but later changed to Y. Using Y."

## Step 3: Surface Blockers

If there are:
- Unresolved choices (user never picked)
- Critical information gaps (can't write a section without it)

→ List them in one message. Wait for response. Return to Step 1.
→ If no blockers → proceed.

## Step 4: Determine Level

Based on compiled content, assess change complexity (see docs/specs/ark.md § Change Pipeline for full definitions):
- L1: single module, simple logic
- L2: multi-module or design decisions needed
- L3: architecture / cross-system

Present your assessment with one-line reasoning. User can override.

## Step 5: Show Compiled Proposal

Present the full proposal. Format:

```markdown
# [Change Name]

## Level
L1 | L2 | L3

## Why
(Self-contained. Never reference conversation history.)

## What
What to do.

## What NOT
What is explicitly out of scope, and why.

## Context
Spec files to load:
- docs/specs/...

## Constraints
Known constraints and limitations.
```

### Phase tagging

If decompose ran and the user accepted a phase split:
- Add `Phase 1 of N` after the Level line
- Add a `## Deferred Phases` section at the bottom listing remaining phases (name + one-line summary each)
- What / What-NOT must reflect Phase 1 scope only — deferred items belong in What-NOT with "(deferred to Phase N)"

### Proposal Failures

If you see any of these in your output, fix before showing the user:

- "TBD", "TODO", "to be determined" — decide now or move to Constraints as an open question
- "we could do X or Y" — pick one, put the other in What-NOT or note the tradeoff in Constraints
- Why section that only makes sense with conversation context — rewrite self-contained
- What section that describes HOW (file paths, function signatures, migration steps) instead of WHAT the system should do
- Empty or single-item What-NOT — you haven't thought hard enough about boundaries
- Context field listing more than 5-6 spec files — probably over-loading, trim to minimum viable set

## Step 6: Confirm + Write

- User says "good" → write to `docs/changes/<name>/proposal.md`, then run doc-review
- User corrects → apply corrections to the draft, show only affected sections, re-confirm
- User says "let me think" → save summary to `docs/changes/<name>/notes.md`, freeze

## Step 7: Doc Review (automatic, silent)

Use `/ark:doc-review` (separate skill) to verify the written proposal.md is self-contained. This spawns a lightweight agent with no conversation history — it reads ONLY proposal.md + listed context specs and checks for ambiguity.

**Calibration:** Only flag issues that would cause a downstream agent to build the wrong thing or ask a question this proposal should have answered. Ignore: minor wording preferences, section length imbalance, stylistic choices.

**Behavioral clarity check:** Can the reader determine expected system behavior for each feature? If "What" is too abstract to derive test scenarios from, the proposal needs more specificity — either inline detail or a separate Acceptance Scenarios section.

- **Pass** → report success
- **Fail** (writing clarity issues) → AI auto-fixes and re-verifies
- **Max 2 rounds.** If still failing after 2 fix attempts, accept and move on — do not loop indefinitely.
- User is never bothered with this step

## Step 8: Commit + Done

Commit all files created during this propose session (proposal.md, draft.md, grill.md, progress.yaml, notes.md if any) in one commit.

```
## Proposal Complete

**Change:** <name>
**Level:** L<n>
**Written to:** docs/changes/<name>/proposal.md

Next: /ark:plan (create execution plan)
```
