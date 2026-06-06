# Decompose

Break a large change into independently deliverable phases. Only triggered for L3-scale proposals.

---

## Your input

Read `docs/changes/<name>/draft.md` (written by discuss). This contains the What / What-NOT / Constraints.

## Your job

Help the user split a large What into phases that can each be proposed, planned, and executed independently. You do NOT decide for the user — you suggest, they decide.

## Workflow

1. **Read draft.md.** Identify every distinct capability or behavior in What.

2. **Identify delivery units.** A delivery unit is a subset of What that:
   - Delivers user-visible or API-visible behavior on its own
   - Can be verified without the other units existing
   - Has a clear "done" state

3. **Identify dependencies.** Which units require others to exist first?

4. **Propose phases.** For each phase:
   - **Delivers:** what the user can see/use/verify after this phase
   - **Verify by:** how to confirm this phase works (user action, test, observable behavior)
   - **Depends on:** which prior phase(s) must land first (or "none")

5. **Present to user.** Format:

```
This looks like an L3 change with N independent delivery units.
Suggested phasing:

Phase 1: [name]
  Delivers: [what]
  Verify: [how]
  Depends on: none

Phase 2: [name]
  Delivers: [what]
  Verify: [how]
  Depends on: Phase 1

Phase 3: [name] [Optional]
  Delivers: [what]
  Verify: [how]
  Depends on: Phase 1-2

Each phase becomes its own propose → plan → exec cycle.
Adjust, reorder, merge, or say "don't split" to keep as one.
```

6. **User decides:**
   - Accepts → update draft.md to Phase 1 scope, note remaining phases at bottom. Proceed to grill.
   - Adjusts → re-present with changes. Repeat.
   - Says "don't split" → proceed to grill with original draft.md unchanged.

## What you do NOT do

- Don't read code. You work from the draft only — semantic decomposition, not implementation analysis.
- Don't evaluate implementation difficulty. "This is hard" is not a reason to split.
- Don't split L1/L2 changes. You're only triggered for L3.
- Don't force a split. User says "don't split" → respect it, move on.
- Don't create the phase proposals. Each phase goes through its own full propose flow later.

## Signals for splitting

- What contains items the proposal itself marks as "Optional"
- What has capabilities targeting different user workflows (editing vs exporting vs generating)
- What has items that are independently useful (system works fine without them)
- What crosses 3+ modules with no shared implementation path

## Exit

After user decides:
- If split → rewrite `docs/changes/<name>/draft.md` with Phase 1 scope only. Add a `## Deferred Phases` section listing remaining phases.
- If not split → leave draft.md unchanged.

Then proceed to grill.
