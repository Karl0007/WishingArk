# Architecture-Sensitive Planning

Use this file only when a change touches a reusable mechanism, seam, API/schema/declaration boundary, adapter/provider/plugin point, or a reference case that stands for a general mechanism.

The goal is not more process. The goal is to make the requested behavior work while leaving the touched code easier to change, test, and reason about.

## Core vocabulary

Use these terms consistently:

- **Mechanism** — reusable behavior the plan expects future callers, declarations, adapters, or modules to use.
- **Reference case** — the concrete case from the proposal, current code, demo, or default path.
- **Essential contract** — what the mechanism actually promises.
- **Accidental detail** — a name, path, provider, label, format, ordering, or other detail that belongs to the reference case but not to the mechanism.
- **Contrast case** — a case that changes one accidental detail while preserving the same essential contract, or expects safe rejection when the contract is invalid.
- **Touched seam** — the interface where this change should concentrate behavior.

## Hardcode test

For every reusable mechanism, include one contrast case.

A contrast case is valid only if an implementation hardcoded to the reference case would fail it.

Planner must answer:

```text
Mechanism:
Reference case:
Essential contract:
Accidental detail changed:
Contrast case:
Forbidden shortcut:
```

If there is no reusable mechanism, say so briefly and do not invent a contrast case.

## Deepening test

A good plan should not merely avoid hacks. It should improve the touched seam.

For every architecture-sensitive change, ask whether the plan makes the relevant complexity more local and gives callers more leverage.

Planner must answer:

```text
Touched seam:
Current friction:
Deepening move:
Why this improves locality/leverage:
```

A valid deepening move stays inside the touched area and directly supports the requested behavior. Speculative platforms, unused abstractions, and seams with only hypothetical callers are scope creep.

## Agent responsibilities

### Planner

If architecture-sensitive planning applies, add an `## Architecture Effect` section to the draft with the Hardcode test and Deepening test answers. Keep it short.

### SC Writer

If the draft includes `## Architecture Effect`, write success criteria that prove:

- the requested reference behavior works;
- the contrast case exercises the same mechanism or rejects invalid input safely;
- the deepening move is observable through a smaller, clearer, or more authoritative interface.

### Plan Checker

If architecture-sensitive planning should apply but the plan omits it, mark BLOCKER.

If `## Architecture Effect` is present, mark BLOCKER when:

- a reusable mechanism has no contrast case;
- the contrast case would still pass with a hardcoded reference implementation;
- the deepening move is speculative, outside the touched area, or not tied to the requested behavior;
- success criteria do not prove the Hardcode test and Deepening test.

### Hack Checker

For architecture-sensitive plans, treat reference-case hardcoding of a claimed reusable mechanism as a hack. Do not flag fixed domain rules as hacks unless the plan presents them as reusable mechanisms.

### Feasibility Checker

When a task claims to change a seam or boundary, verify its Context includes the files where that seam or boundary is actually implemented. If the task goal requires a boundary change but the Context only covers a caller or adapter, mark BLOCKER.
