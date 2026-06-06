# Grill

Pressure-test the proposed change until shared understanding is reached. Challenge assumptions, find gaps, surface edge cases.

---

## Entry

Read `docs/changes/<name>/draft.md` before starting (if it exists). This is the current state of What / What-NOT / Constraints.
If decompose ran, draft.md may be scoped to Phase 1 with deferred phases noted.
If discuss was skipped (direct-to-grill routing), draft.md won't exist — work from conversation context instead.
Ground your challenges in the draft — don't rely on conversation memory for what's in scope.

---

## Stance

Interview the user relentlessly about every aspect of this change until reaching shared understanding. Walk down each branch of the decision tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time, waiting for feedback before continuing.

If a question can be answered by exploring the codebase or specs, explore them instead of asking.

## Anchors

Ground your challenges in project reality:
- Read `docs/specs/` to check if the proposal contradicts existing constraints
- Read code to verify assumptions about current behavior
- Cross-reference with `CONTEXT.md` for terminology consistency
- Check if adjacent modules would be affected (scope creep detection)

## Challenge Techniques

- **Assumption flip** — "You're assuming X. What if X is wrong?"
- **Failure scenarios** — "What happens when Y fails mid-operation?"
- **Terminology conflict** — "CONTEXT.md defines 'X' as A, but you seem to mean B — which is it?"
- **Code-narrative contradiction** — "The code does X, but you just said Y — which is right?"
- **Scope creep probe** — "This touches module A. Does it also affect B?"
- **Core need** — "What's the user actually trying to accomplish? Is this the most direct path?"
- **Experience test** — "Walk me through what the user sees step-by-step. Where does it feel wrong?"
- **Design intent** — "Why this approach over the simpler alternative?"
- **Architecture feasibility** — Read the code structures involved. Can the current architecture support the proposed behavior? Surface data model mismatches, framework constraints, schema limitations.

## What NOT To Do

- Don't limit your questions to proposal.md fields — challenge ANY aspect
- Don't be a checklist — follow interesting threads, go deep where it matters
- Don't accept vague answers — push for specifics
- Don't make decisions for the user — challenge and recommend, but they decide

## Exit: Write grill.md

When shared understanding is reached (naturally or user says "enough"):

1. Write `docs/changes/<name>/grill.md` with decisions made during grill:

```markdown
# Grill Record: [Change Name]

## Decisions
- [Question asked] → [Decision reached]

## Constraints Added
- [New constraint surfaced during grill]

## Scope Changes
- [Anything added to or removed from What/What-NOT during grill]
```

2. Proceed to the Go Sequence defined in SKILL.md.
