# Project Ark — Spec Guide

> How to structure and write specs. Companion to `ark.md` (workflow rules).
> Skills reference specific sections by `§` heading.

---

## § Directory Structure

Four top-level directories. All other structure grows organically.

```
project-root/
├── <entry file>                ← tool-specific (indexes ark.md)
├── CONTEXT.md                  ← domain glossary
├── docs/
│   ├── specs/                  ← project truth — recursive tree
│   │   ├── index.md            ← project map: module list + relationships
│   │   ├── ark.md              ← workflow rules
│   │   ├── ark-specs.md        ← THIS FILE: spec guide
│   │   ├── product.md          ← project-level product understanding
│   │   ├── tech.md             ← project-level technical understanding
│   │   └── [module]/           ← module nodes (organic growth)
│   │       ├── index.md        ← module overview (four-layer)
│   │       ├── product.md      ← deeper product understanding (optional)
│   │       └── tech.md         ← deeper technical understanding (optional)
│   ├── adr/                    ← architecture decision records
│   ├── changes/                ← active changes (workspace)
│   └── archive/                ← historical archive
├── content/                    ← instance data (Instance)
└── src/
```

**Rules:**
- `index.md` is the only required node file; **perspective files** (product.md, tech.md, or project-defined views like art.md/ux.md) are optional
- Split a file at ~150 lines (guideline, not hard limit); merge if only 1-2 lines
- Lazy creation: never create empty placeholder files

---

## § Spec Nodes

Every node in docs/specs/ has the same shape (self-similar — children have the same file structure as parents, recursively):

```
any-module/
├── index.md           ← required: module overview (four-layer, breadth)
├── product.md         ← optional: deeper product understanding (depth)
├── tech.md            ← optional: deeper technical understanding (depth)
├── [custom].md        ← optional: project-defined perspectives
└── sub-module/        ← optional: child nodes
```

**Relationship between files:**
- `index.md` = **breadth** — quick overview of what this module is, how it works, where to start reading
- `product.md` = **depth** — deeper product investigation (users, journeys, experience, constraints)
- `tech.md` = **depth** — deeper technical investigation (best practices, how-to-change, constraints)
- product.md and tech.md are NOT splits of index.md — they are independent deeper explorations
- Lazy creation: only create product.md / tech.md when a deeper investigation is needed

---

## § index.md Structure

Recommended: **20-50 lines.** Each layer serves a distinct purpose:

```markdown
# [Module Name]

## Boundary & Constraints (prevents wrong decisions)
- Responsible for: ...
- NOT responsible for: ... (that belongs to [other module])
- Rules: [invariants that code alone doesn't make obvious]
- Direction: [what's stable vs. what's changing/migrating]

## Behavior (what the system should do)
- [Core flows, expected behaviors, edge cases]
- [Business rules that are scattered across files when reading code]

## Architecture (how it works — saves re-tracing)
- [Call chains, data flow, module collaboration]
- [The "shape" of execution that spans multiple files]

## Entry Points (where to start reading)
- path/to/MainService.ts — [one-line role]
- path/to/config.yaml — [what it controls]
```

**Writing standard for each line:**
- Constraint layer: "Does this prevent a class of wrong decisions?" — if not, cut it.
- Behavior layer: "Is this scattered/expensive to reconstruct from code?" — if not, cut it.
- Architecture layer: "Would an agent have to trace 5+ files to figure this out?" — if not, cut it.
- Entry points: minimal. 2-4 files max.

---

## § product.md Structure

Same structure for root-level and module-level. Fill sections as relevant; omit empty sections.

```markdown
# Product — {{ scope: project name or module name }}

## Identity
{{ What this is. Who it's for. Core value. }}

## What This Is NOT
{{ Identity boundaries — what this deliberately is not }}

## Target Users
{{ User profiles, experience level, usage context }}

## User Journeys
{{ Core flows from the user's perspective — step-by-step: "User does X → sees Y → does Z" }}

## Experience Goals
{{ What the experience should feel like — fast? calm? powerful? simple? }}

## Value Hierarchy (first wins on conflict)
{{ When two good things conflict (e.g. simplicity vs power), which wins? Order matters. }}
1. {{ most important }}
2. {{ second }}
3. {{ third }}

## Experience Axioms
- ALWAYS: {{ invariant }}
- NEVER: {{ invariant }}

## Deliberate Exclusions
{{ Features considered and rejected, with reasons }}

## Open Questions
{{ Undecided — agents should not assume answers here }}
```

---

## § tech.md Structure

Same structure for root-level and module-level. Fill sections as relevant; omit empty sections.

```markdown
# Technical — {{ scope: project name or module name }}

## Stack
{{ language, framework, runtime, key libraries }}

## Project Structure
{{ brief description of source layout }}

## Build & Run
{{ commands to build, run, test }}

## Best Practices
{{ Recommended patterns and idioms used in this project — the "how we do things here" }}

## How to Add / Change
{{ Step-by-step: how to add a new feature, endpoint, module. Which files to create, where to register, what boilerplate to follow. }}

## Coding Standards
{{ formatting, naming conventions }}

## Commit Format
{{ e.g., Conventional Commits, Angular, project-specific }}

## Testing
{{ test framework, coverage expectations, how to write tests here }}

## Technical Constraints
{{ Rules that code alone doesn't make obvious }}

## Direction
{{ What's stable vs. migrating. What's deprecated. Where new code should go. }}
```

---

## § ADR (Architecture Decision Records)

Location: `docs/adr/`

**Create an ADR when ALL three conditions are met** (use judgment if only two apply):
1. Decision is hard to reverse
2. A person without context would be surprised
3. Real trade-offs exist

---

## § Archive

```
docs/archive/
└── YYYY-MM/
    └── <change-name>/
        └── summary.md    ← what was done + key decisions + affected modules + ADRs
```

Archived after merge phase completes. Process files (proposal.md, plan.md, etc.) are deleted from docs/changes/ but preserved in git history for traceability.
Essential conclusions have already been promoted to docs/specs/ during merge.
