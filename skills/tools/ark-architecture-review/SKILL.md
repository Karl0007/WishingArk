---
name: ark-architecture-review
description: Surface architectural friction and propose deepening opportunities that turn shallow modules into deep ones. Use when asked to improve architecture, find refactoring opportunities, increase testability, improve AI-navigability, review module boundaries/seams, or identify shallow/pass-through modules.
---

# Ark Architecture Review

Surface architectural friction and propose **deepening opportunities**: refactors that put more behaviour behind smaller, clearer interfaces. The aim is testability, AI-navigability, locality, and leverage.

This skill is an architecture review, not an implementation plan. Do not design final interfaces or write code unless the user explicitly moves into a planning/execution skill.

## Vocabulary

Use these terms exactly in every suggestion:

- **Module** — anything with an interface and an implementation: function, class, package, or slice.
- **Interface** — everything a caller must know to use the module correctly: types, invariants, ordering, errors, config, performance. Not just the type signature.
- **Implementation** — the code inside a module.
- **Depth** — leverage at the interface: a lot of behaviour behind a small interface.
- **Deep** — high leverage; callers learn little and get much.
- **Shallow** — interface nearly as complex as the implementation.
- **Seam** — where an interface lives; behaviour can be altered without editing in place. Use this, not "boundary".
- **Adapter** — a concrete thing satisfying an interface at a seam.
- **Leverage** — what callers get from depth.
- **Locality** — what maintainers get from depth: change, bugs, knowledge, and verification concentrated in one place.

Principles:

- **Deletion test** — imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across callers, it was earning its keep.
- **Variation test** — some modules look Deep only because they serve one dominant case. Imagine one plausible second variation: another Adapter, backend, storage target, UI surface, resource type, workflow shape, permission mode, or recovery path. If support would spread across many callers, the current Seam is still Shallow or names the wrong concept.
- **The Interface is the test surface.** If tests must reach past the Interface, the Module may be the wrong shape.
- **One Adapter = hypothetical Seam. Two Adapters = real Seam.** Do not invent speculative abstractions, but do test whether the first Adapter is masquerading as the domain concept.

## Process

### 1. Load language and decisions

Read the project's domain glossary/specs and ADRs in the area being reviewed first.

If the project has `CONTEXT.md`, specs, ADRs, or architecture decision docs, use that vocabulary for domain concepts. If they are missing, infer vocabulary from product/spec docs and mark it as inferred in your reasoning, not in every output line.

Do not re-litigate accepted ADRs. If real friction is strong enough to revisit one, mark the conflict clearly.

### 2. Explore current friction

Use an Explore agent for non-trivial codebases. Keep the prompt short but shaped:

```text
# Target
[area/files/modules to inspect]

# Goal
Find Modules that are Shallow, leak seams, or make tests depend on implementation details.

# Constraints
Read-only. Use the architecture vocabulary exactly. Do not propose final interfaces or implementation plans.

# Taste
Prefer opportunities that improve Locality and Leverage without speculative abstraction.

# Method
Use the Deletion test. For seams with one dominant case, also use the Variation test.

# Acceptance
Return candidates with Files, Problem, Deletion test result, Variation test when relevant, Seam reality, and testability impact.
```

Explore organically. Look for:

- Understanding one concept requires bouncing between many small Modules.
- A Module is Shallow: its Interface is nearly as complex as its Implementation.
- Pure helpers were extracted for testability but real bugs hide in orchestration, ordering, or caller obligations.
- Coupled Modules leak across their Seams.
- Tests are hard to write through the Interface, or must inspect internal state.
- An implementation detail may be standing in for a broader domain concept. Apply the Variation test.
- A future second Adapter would force changes across spec/runtime/storage/routes/read-model/tests instead of concentrating behind one Seam.

### 3. Synthesize before listing

Before presenting candidates, check whether multiple candidates point at one missing foundation concept. If yes, surface that foundation candidate first and state what it unlocks.

Avoid first-case deepening: do not merely wrap the current Implementation more neatly when the Interface names only the first Adapter instead of the real domain concept.

### 4. Present candidates

Present a numbered list. For each candidate include:

- **Files** — files/Modules involved.
- **Problem** — why the current architecture causes friction.
- **Deletion test** — would deleting the Module remove complexity or scatter it?
- **Variation test** — include only when it changes the recommendation; name the plausible second variation and what would currently change.
- **Solution** — plain-English direction, not an interface design.
- **Benefits** — explain in terms of Locality, Leverage, and how tests improve.

Use project domain vocabulary plus the architecture vocabulary above. Do not drift into "component", "service", "API", or "boundary" when one of the required terms applies.

Do not propose final interfaces yet. End by asking: **"Which of these would you like to explore?"**

### 5. Grilling loop

When the user picks a candidate, walk the design tree with them:

- What concept should the deeper Module name?
- What belongs behind the Seam?
- What remains outside the Seam?
- What must callers no longer know?
- What tests should survive refactors because they target the Interface?
- If the Variation test mattered, should the Seam support only the current case or the broader concept?

Side effects during grilling:

- If the chosen Module needs a new domain term, add it to `CONTEXT.md` or the project's equivalent domain glossary. Create the file lazily if none exists and the project conventions allow it.
- If the user rejects a candidate for a durable architectural reason, offer to record an ADR so future reviews do not re-suggest it.
- If the user wants the change written up, hand off to `ark-propose`: capture What, What-NOT, constraints, and architecture intent. Do not skip the proposal step for L2/L3 architecture changes.

## Anti-patterns

- **First-case deepening** — proposing to deepen the current Implementation without checking whether the Interface names the real concept or just the first case.
- **Checklist architecture** — listing generic best practices instead of concrete Locality/Leverage gains.
- **Speculative abstraction** — inventing Seams with no plausible second variation or caller pain.
- **Pass-through preservation** — keeping wrappers that fail the Deletion test.
- **Parallel systems** — proposing a new path instead of converging on the project’s accepted architecture.
- **Interface design too early** — designing signatures before the user chooses a candidate and constraints are grilled.

## Output contract

The first response after exploration must be a candidate list, not an implementation plan.

Each candidate should be self-contained enough that a downstream proposal can be written without re-reading the whole investigation. If evidence is inferred rather than observed, mark it as `[INFERENCE]`.
