# Global Explore

Identify the project's module structure, write `docs/specs/index.md`, and guide root-level product/tech specs.

**Triggered by:** `/ark:explore` (no module argument)

---

## Steps

### 1. Deep observation

Read code deeply enough to understand the project's **functional structure and internal mechanics** — not just directory names:
- Entry points (main/index files, package.json scripts)
- Follow core import chains to understand how code clusters into responsibilities
- Identify recurring patterns, shared infrastructure, and functional boundaries
- For each potential module, build a mental model of: what it does, how it does it (key flows), what it talks to, what it doesn't touch
- Read into each module enough to understand its core behavior — not just its name, but what actually happens when its code runs

**Stop when:** you can (1) explain each proposed module's responsibility in one sentence, (2) describe how it relates to the others, AND (3) sketch its core internal flow (entry → processing → output). If you can only name modules but can't describe their internal behavior, you haven't read deep enough.

**Then push deeper:** "For each module, what's the one thing that would surprise a competent developer who only read the module's name and entry file?" If you can't identify at least one non-obvious behavior per module, your observation is still at the surface.

### 2. Propose module list with understanding

Present proposed modules **with evidence of your understanding** — not just names:

```
"Based on reading the code, I think your project has these modules:

1. auth — handles authentication (JWT) and authorization (role-based)
   Boundary: owns token lifecycle; does NOT own user creation (that's in users/)
   Talks to: payment (validates tokens), notification (sends login alerts)

2. payment — payment processing, refunds, gateway integration
   Boundary: owns payment state machine; does NOT own pricing logic
   Talks to: auth (token verification), notification (payment confirmations)

3. notification — email and push delivery
   Boundary: only delivers; does NOT decide when to send (triggered by others)
   Talks to: nothing directly (receives events from others)

4. (uncertain) scheduling — there's a cron/ directory with job definitions,
   but it might be infrastructure rather than a module. Is this a distinct
   responsibility or just a deployment mechanism?

Module relationships:
  auth → payment → notification
  scheduling → (triggers jobs in auth and payment?)

Correct? Add/remove/rename/merge?"
```

This way the user can correct your **understanding** (not just your naming). If your boundary or relationship is wrong, the user catches it here before you write specs.

**If you can't identify clear modules** (monolith, very small, or tangled codebase), offer options:
1. Write a single top-level `docs/specs/index.md` covering the whole project
2. Help sketch ideal module boundaries (what *should* be separate, even if code doesn't enforce it yet)
3. Just explore a specific area the user points you to

### 3. Write docs/specs/index.md

After user confirms the module list, write `docs/specs/index.md` — the project map:

```markdown
# [Project Name]

## Modules
- [auth](auth/) — authentication and authorization
- [payment](payment/) — payment processing and refunds
- [notification](notification/) — email/push delivery

## Module Relationships
- auth → payment (payment verifies auth tokens)
- payment → notification (sends payment confirmations)
```

### 4. Write root product.md / tech.md

Write root-level specs before diving into modules — they provide project-wide context that informs module exploration.

**Important:** Step 1 gave you broad structural understanding, but product and tech specs require **their own deep investigation**. Follow each sub-skill's full Phase 1-2-3-4 process — do NOT skip their deep observation phases just because you already did Step 1.

**Product** (follow [PRODUCT.md](PRODUCT.md) — execute its full Phase 1→2→3→4):
1. Do PRODUCT.md Phase 1: deep observation of user-facing code, tests, config, error messages
2. Do PRODUCT.md Phase 2: infer product understanding (identity, users, values, exclusions)
3. **Present to user and wait for corrections** before writing anything
4. After confirmation, write `docs/specs/product.md`

**Tech** (follow [TECH.md](TECH.md) — execute its full Phase 1→2→3→4):
1. Do TECH.md Phase 1: deep observation of patterns (3+ examples), CI/CD, test setup, git history
2. Do TECH.md Phase 2: infer technical understanding (best practices, constraints, direction, how-to-change)
3. **Present to user and wait for corrections** before writing anything
4. After confirmation, write `docs/specs/tech.md`

**Do NOT write either file without presenting inferences first (interactive mode).**
**Do NOT skip the sub-skill's deep observation — Step 1's broad scan is NOT sufficient for product/tech depth.**

In AFK mode: write both with confidence tags, skip the presentation step.

If user wants to skip either: respect that.

### 5. Write initial index.md for each module

Based on your understanding from Step 1-2, write `docs/specs/<module>/index.md` for each confirmed module. Use the four-layer structure (Boundary & Constraints, Behavior, Architecture, Entry Points). Write as much as your current understanding allows — if you need to read more code to fill a section properly, do so.

Present all initial index files to user for confirmation:
```
"Here are initial specs for each module:

[show each module's draft index.md]

Want me to deep-explore any of these modules for more detailed specs
(overwrite index with deeper version + add product + tech)?

1. Deep-explore all modules (recommended, can run in parallel)
2. Deep-explore specific modules → which ones?
3. This is enough for now — I'll deep-explore later as needed"
```

**Do NOT skip presenting these drafts.** Write them, show them, get confirmation.

### 6. Deep-explore modules (recommended default)

**Default recommendation: deep-explore all modules.** The initial index.md from Step 5 captures broad understanding, but each module benefits from the focused deep reading that MODULE.md + PRODUCT.md + TECH.md provide.

If user agrees (or doesn't object):
- Dispatch sub-agents for each chosen module (parallel with `--afk`, sequential otherwise)
- Each sub-skill does its own deep reading — the initial index.md from Step 5 will be **overwritten** with the deeper version

**Critical: do NOT transfer your understanding.** When dispatching sub-agents, pass ONLY the module name and skill invocation. Do NOT include your Step 1-5 analysis, mental model, or observations as context. Sub-agents that receive pre-digested understanding will treat it as ground truth and skip their own deep observation (MODULE.md Phase 1). Each sub-agent must build understanding from scratch by reading the code itself.

**Dispatch prompt template:**
```
Run /ark:explore {module}. Build your own understanding from code — do NOT rely on any prior context or summary.
```

If user explicitly says "this is enough": stop here. Modules can be deep-explored later individually.

---

## § What Is a Module

**IS a module:**
- Has a distinct responsibility in one sentence
- "The part that handles X"
- May span multiple directories

**Is NOT a module:**
- `utils/`, `helpers/`, `common/`, `shared/` — infrastructure glue
- `types/`, `constants/`, `config/` — cross-cutting support
- `tests/` — not independent functionality
- A directory that exists only for file organization

When uncertain: include it in the proposal but mark it "(uncertain)" — let the user decide.
