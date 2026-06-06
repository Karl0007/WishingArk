---
name: ark-explore
description: Explore a project or module to build understanding and write specs. Intelligently routes based on project state and arguments. Supports interactive and AFK modes. Use when user says "explore", "understand this module", "write specs for", or invokes /ark:explore.
---

# /ark:explore

Build understanding of a project or module. Read code → form inferences → present to human → record as specs.

---

## Smart Routing

### `/ark:explore` (no arguments)

Check project state and route:

```
docs/specs/index.md exists?
  ├─ NO  → run GLOBAL.md (first-time: discover modules, write project map)
  └─ YES → ask user:
           "Project already explored. What would you like to do?
            1. Explore a specific module → which one?
            2. Re-explore globally (re-scan module structure)
            3. Deep-dive: product / tech / all for a module or root"
```

### `/ark:explore <module>` — what is a module?

`<module>` is a **functional name** (e.g., `auth`, `payment`, `notification`) — NOT a file path or directory name. A module is a cohesive unit of responsibility. See [GLOBAL.md § What Is a Module](GLOBAL.md) for the full definition.

### Explicit commands

| Command | Dispatches to | What it does |
|---------|--------------|--------------|
| `/ark:explore` | Smart route (above) | Auto-detect or ask |
| `/ark:explore <module>` | [MODULE.md](MODULE.md) + [PRODUCT.md](PRODUCT.md) + [TECH.md](TECH.md) | Full explore: index + product + tech |
| `/ark:explore <module> index` | [MODULE.md](MODULE.md) only | Only write/update index.md |
| `/ark:explore <module> product` | [PRODUCT.md](PRODUCT.md) only | Only product deep-dive |
| `/ark:explore <module> tech` | [TECH.md](TECH.md) only | Only tech deep-dive |
| `/ark:explore .` | [PRODUCT.md](PRODUCT.md) + [TECH.md](TECH.md) (root) | Root product.md + tech.md |
| `/ark:explore . product` | [PRODUCT.md](PRODUCT.md) (root-level) | Root product.md only |
| `/ark:explore . tech` | [TECH.md](TECH.md) (root-level) | Root tech.md only |

> **Default is full explore** (index + product + tech). Use `index`, `product`, or `tech` argument to narrow scope.
> `.` (dot) = root-level scope (docs/specs/product.md, docs/specs/tech.md).

### Flags (apply to all sub-skills)

- `--afk` — No human interaction. Write with confidence tags. Multiple agents can run in parallel.

---

## Audience & Goal

**Reader:** AI agent about to modify code — has no project context.

**Specs must provide what code alone doesn't reveal:** invisible rules, product intent, cross-file coupling, which pattern is current.

**Reader's goal:** Make a correct change on the first attempt.

---

## Shared Principles (all sub-skills follow these)

- **Specs use structured text** — ASCII diagrams only for presenting to humans, not in spec files
- **Each line must pass the test** — prevents wrong decision? Saves expensive re-trace? If neither → cut it.
- **Code in specs: short only** — signatures, 1-3 line patterns, config snippets. Never paste implementation blocks — reference `file:line` instead. Specs that duplicate code become stale lies.
- **Constraint layer requires human confirmation** (interactive) — agent infers constraints from code → presents to user in Phase 3 → user confirms/corrects → agent writes to spec. In AFK mode, tag confidence instead: `[HIGH]` / `[MEDIUM]` / `[LOW]`
- **Module = function, not directory** — see [GLOBAL.md § What Is a Module](GLOBAL.md)
- **Full explore by default** — `/ark:explore <module>` writes index + product + tech. Use explicit `index`/`product`/`tech` argument to narrow scope.

---

## Key Terms

- **Constraint layer** — information that prevents wrong decisions. Test: "Would a competent agent, reading only the code, get this wrong?" Maps to **Boundary & Constraints** in index.md.
- **Cognitive layer** — information that saves expensive re-tracing (reading 5+ files to piece together). Maps to **Behavior** + **Architecture** + **Entry Points** in index.md.
- **Module** — a cohesive unit of functionality (not a directory). Has a distinct responsibility expressible in one sentence.
- **Spec** — a Markdown file in `docs/specs/`. Types: `index.md` (breadth), `product.md` (product depth), `tech.md` (technical depth).
