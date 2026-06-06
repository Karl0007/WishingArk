# Project Ark — Workflow Rules

> Workflow and process rules for the Ark framework.
> For spec structure and templates, see `ark-specs.md`.
> **Entry file** = the tool-specific config file loaded at session start. It indexes into this file.
> Skills reference specific sections by `§` heading.

---

## § Core Truth Rule

> **When documentation and code contradict each other, code is the truth.**

Specs describe intent and constraints. Code is the actual implementation. When they diverge:
- The code's behavior is what the system actually does — treat it as fact.
- The spec may be outdated, aspirational, or simply wrong — do NOT assume it reflects reality.
- Before acting on any spec claim, verify it against code if the claim affects your work.
- If you find a contradiction: follow the code, and flag the spec as needing update.

---

## § Commit Rule

> **Commit once at the end of each skill/phase.** Not per-file — per completion.

Examples: init completes → commit all created files. Explore finishes a module → commit that spec. Propose writes proposal.md → commit. Plan writes plan.md → commit. Execute completes a task → commit code + tests.

Uncommitted files are lost if the session ends. Each commit is a recovery point.

---

## § Change Pipeline

> All changes flow through the pipeline. Docs and code are **atomic** products of the same change — committed together, no half-done state exists.

### Change Levels (L = Level of complexity)

| Level | Scope | Flow |
|-------|-------|------|
| **L0** | Config/typo, no behavior change | Direct commit → batch PR |
| **L1** | 1 module, simple logic | proposal → plan → execute → PR |
| **L2** | Multi-module or design decision | propose → plan → **autoexec** → merge |
| **L3** | Architecture / cross-system | Same as L2 — propose → plan → autoexec → merge (planner handles large scope with more tasks) |

> **autoexec** is a single command (`/ark:autoexec`) that orchestrates three sub-phases internally: execute → test → review. It is NOT a phase itself — it's a runner.

### Change Folder Structure

```
docs/changes/<change-name>/
├── proposal.md        ← why + what + context field (required for all)
├── plan.md            ← atomic tasks + GWT tests (required for all)
├── design.md          ← technical approach (if needed)
├── progress.yaml      ← machine-readable state
├── research.md        ← investigation notes (optional)
└── verification.md    ← verification results
```

> **GWT** = Given-When-Then. Each task must have at least one testable scenario:
> `Given [precondition], When [action], Then [expected outcome]`
> Example: Given a user with valid payment method, When they submit an order, Then a pending payment record is created and the payment gateway is called.

### proposal.md Spec

```markdown
# [Change Name]

## Level
L1 | L2 | L3

## Why
(Self-contained. Never reference conversation history.)

## What
What to do. What NOT to do.

## Context
Spec files to load:
- docs/specs/tech.md
- docs/specs/[module]/index.md

## Constraints
Known constraints and limitations.
```

### progress.yaml Spec

```yaml
change: <name>
level: L2
status: proposing | planning | executing | testing | reviewing | merging | done
phases:
  propose:  { status: done, output: proposal.md }
  plan:     { status: done, output: plan.md }
  execute:  { status: in_progress, current_task: 2/5 }
  test:     { status: pending }
  review:   { status: pending }
  merge:    { status: pending }
context:
  - docs/specs/tech.md
  - docs/specs/combat/skill/index.md
```

### Phase Gate Conditions

```
propose → plan:    proposal.md exists + context field non-empty + zero-context test passed
plan → execute:    plan.md exists + ≥1 task + each task has GWT scenario + user confirmed
execute → test:    all tasks done in progress.yaml + code committed
test → review:     all GWT scenarios passed + test suite passed
review → merge:    no blocking issues
merge → done:      feature branch rebased onto main + merge review clean (no test regression, no doc-code drift) + docs archived + specs updated
```

---

## § Quality Assurance

Three-layer defense. No layer is optional for L2+.

### Layer 1: Task Isolation
- One task dispatched at a time to execution agent
- Each task → commit → update progress → next task

### Layer 2: Independent Verification (aka "Double Check")
- Verification agent has zero context from execution agent
- Input: task description + GWT + code diff
- Verdict: does code actually satisfy GWT?
- **Scope:** L2/L3 mandatory by default; L0/L1 skipped by default (enable via proposal.md `## Constraints`)

### Layer 3: Mechanical Verification
- Tests exist and pass (not AI judgment — program output)
- Coverage does not regress
- Expected files were modified

### Zero-Context Document Test

> Dispatch a zero-context agent with ONLY the produced document + declared spec files.
> If it can raise questions → document is not self-contained → **FAIL**.
> Feed questions back to author → revise → re-test.
> **PASS** = zero-context agent has no questions left to ask.

---

## § ADR Threshold

> When does a decision become an ADR? When all three conditions are met.

A finding from research or a decision made during a change becomes a formal ADR (`docs/adr/NNN-<title>.md`) when ALL THREE conditions are true:

1. **Irreversible or costly to reverse** — switching later would require significant rework (new library, architectural pattern, data model shape)
2. **Non-obvious** — someone without context would be surprised by this choice (if everyone would make the same decision, it doesn't need documenting)
3. **Real trade-offs exist** — there were viable alternatives with genuine pros/cons, not a single obvious answer

If only 1-2 conditions are met → capture in the relevant spec file (tech.md, index.md) instead. Specs are editable; ADRs are append-only records of decisions-at-a-point-in-time.

**ADR format:** `docs/adr/NNN-<title>.md` where NNN is sequential. Minimum fields: Status (accepted/superseded), Context, Decision, Consequences.

---

## § Context Loading

### Layer Model

```
Layer 0 (always):    entry file + CONTEXT.md                      ≈ 200 lines
Layer 1 (framework): docs/specs/ark.md OR docs/specs/ark-specs.md   ≈ 200 lines
Layer 2 (by view):   docs/specs/[product|tech|art].md              ≈ 150 lines
Layer 3 (by module): docs/specs/[module]/index.md + perspectives    ≈ 100 lines
Layer 4 (by task):   docs/changes/[name]/proposal.md + plan.md      ≈ 150 lines
─────────────────────────────────────────────────────────────────
Target budget per session                                          ≈ 600 lines
```

**Framework file loading:**
- Working on a change (propose/plan/execute/merge) → load `docs/specs/ark.md` (workflow rules)
- Writing or reviewing specs (explore/organize) → load `docs/specs/ark-specs.md` (spec guide)
- Never load both unless the task genuinely needs both

### Loading Rules
1. Always read entry file + CONTEXT.md
2. Read proposal.md `context` field → load declared specs
3. Read index.md → decide whether to descend into children
4. **Never load**: other changes' files, docs/archive/, undeclared specs

### Who Decides What to Load
- `proposal.md context field` — explicit declaration at proposal time
- Entry file loading rules — fallback
- Agent judgment — can follow index chain if more context needed

---

## § Parallel Development

- Each change on independent feature branch
- Same person, multiple sessions → different worktrees
- Different people, different changes → natural isolation

### Conflict Resolution
- **First to merge wins**
- Late merger rebases (AI-assisted)
- **TDD safety net**: both sides' tests must pass post-merge
- Trace design intent via proposals if conflict is ambiguous

### CONTEXT.md Maintenance
- New terms recorded inside change during work
- Merged into CONTEXT.md at merge time
- Append-only updates to reduce conflict probability

---

## § Cross-Session Recovery

```
Open session
  → read entry file + CONTEXT.md
  → /ark:resume or manually enter change
  → read progress.yaml → find next incomplete task
  → load proposal.md + plan.md + context-declared specs
  → continue from breakpoint
```

**Guarantees:**
- Atomic commits → no "half-done" state exists
- progress.yaml → exact current position
- All decisions in files → no dependency on chat history

---

## § Skills

### High-Level Commands (user-facing)

| Command | Purpose |
|---------|---------|
| `/ark:init` | Bootstrap project into Ark framework |
| `/ark:explore` | Build project/module understanding, write specs |
| `/ark:propose` | Create change proposal (brainstorm → discuss → grill → proposal.md) |
| `/ark:plan` | Create execution plan (research → tasks → GWT → verify → confirm) |
| `/ark:autoexec` | Execute + test + review (orchestrator) |
| `/ark:merge` | Archive + update specs + rebase + merge review → merge |
| `/ark:status` | Show current change state |
| `/ark:resume` | Resume interrupted change from progress.yaml |
| `/ark:organize` | Restructure spec tree (manual trigger, AI can suggest) |

### Design Principles
- Each skill has explicit Entry/Exit Conditions (for future engine)
- Input/output are serializable
- Low-level skills can be used independently or orchestrated
- High-level commands hide complexity, guide by phase
