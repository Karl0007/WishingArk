---
name: ark-init
description: Initialize a project into the Project Ark framework. Creates directory skeleton, deploys framework files (ark.md, ark-specs.md), generates entry file and CONTEXT.md. Does NOT create product.md or tech.md — those come from /ark:explore. Use when user says "ark init", "initialize project", "onboard project", or invokes /ark:init.
---

# /ark:init

Bootstrap a project into the Project Ark framework.

**Input:** `/ark:init` — optional: project root path (defaults to cwd).

```
Init creates: skeleton + framework files + entry file + CONTEXT.md
Init does NOT create: product.md, tech.md, module specs (those come from /ark:explore)
```

After init, run `/ark:explore` to build project understanding (modules + product + tech).

---

## Steps

### 1. Detect environment

- **Existing Ark?** If `docs/specs/ark.md` or `docs/specs/ark-specs.md` exists → ask: re-init or abort?
- **Entry file?** Write the entry file to whatever path YOUR tool natively uses as its instruction file. Do NOT hardcode `CLAUDE.md` — that is only for Claude Code. If you are unsure what your tool's entry file is, ask the user.
- **Tech stack?** Scan for package.json, Cargo.toml, go.mod, etc. → language, framework, test runner
- **No code?** Skip scanning, proceed to step 2

### 2. Create directory skeleton

```
docs/
  specs/         ← project truth (only dir always created)
  adr/           ← architecture decision records
  changes/       ← active changes
```

Do NOT create `content/` or `docs/archive/` — these are created by other skills when first needed.

### 3. Deploy framework files

Copy both files from this skill's directory to the target project:
- `ark.md` → `docs/specs/ark.md` (workflow rules)
- `ark-specs.md` → `docs/specs/ark-specs.md` (spec guide + templates)

These are the **single source of truth** for Ark behavior. After deployment, the project team owns them and may customize.

### 4. Generate entry file + CONTEXT.md

**Ask the user** to confirm:
- Project name + one-line description
- Tech stack summary
- Perspective files to declare — viewpoint-specific docs used in this project (default: `product.md` for product constraints, `tech.md` for technical conventions; ask if they want others like `art.md`, `ux.md`)

Generate entry file from `ENTRY_FILE_TEMPLATE` in [REFERENCE.md](REFERENCE.md). Fill in the `{{ }}` placeholders with user-confirmed info, then write to entry file path.

Generate `CONTEXT.md` from `CONTEXT_TEMPLATE`.

> Rules live in `docs/specs/ark.md`. Entry file only contains project identity + routing.

### 5. Verify + report

Check before reporting success:
- [ ] `docs/specs/ark.md` and `docs/specs/ark-specs.md` exist
- [ ] Entry file exists
- [ ] CONTEXT.md exists

Then display:

```
## Ark Initialized

Project: <name>
Files created:
  ✓ docs/specs/ark.md (workflow rules)
  ✓ docs/specs/ark-specs.md (spec guide + templates)
  ✓ <entry file> (project identity + routing)
  ✓ CONTEXT.md (domain glossary)

Next step: Run /ark:explore to discover modules and build project specs (product.md, tech.md, module index files).
```

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll create module specs during init" | All specs come from /ark:explore — init only creates framework skeleton |
| "I'll write product.md or tech.md during init" | These require deep project understanding. /ark:explore writes them. |
| "I'll put the full Ark rules in the entry file" | Entry file only routes to docs/specs/ark.md |
| "I'll create empty placeholder files" | Only create files with real content |
| "I'll overwrite the existing entry file" | Always ask before overwriting |

## Guardrails

- **Never overwrite** existing files without user confirmation
- **Lazy creation** — only create files/dirs when they will have real content
- **< 100 lines** per generated file
- **Templates from REFERENCE.md** — fill in `{{ }}` placeholders with actual values, then write the result
- **docs/specs/ark.md = workflow rules** (change pipeline, QA, context loading). **docs/specs/ark-specs.md = spec guide** (directory structure, templates, how to write specs). **REFERENCE.md = init templates** (entry file, context, scanning).
