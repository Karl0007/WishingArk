# Reference — ark-init

Templates and tool detection for `/ark:init`.

> **Entry file** = the tool-specific instruction file loaded at session start (e.g., CLAUDE.md, .cursorrules). Each tool knows its own.

---

## § Tool Detection

```
Tool knows its own entry file path?
  ├─ YES → use it directly
  └─ NO  → ask user
```

> **Do NOT hardcode tool-to-file mappings.** Each tool knows its own conventions. If that changes, the tool adapts — this document should not be a source of stale mappings.

**Resolution order:**
1. Tool self-identifies → use native entry file path
2. User specifies → use their choice
3. Neither → ask user

---

## § ARK_MD_SOURCE

Two framework files are bundled alongside this skill. During init, copy both to `docs/specs/`:

```
.claude/skills/ark-init/ark.md       →  <project>/docs/specs/ark.md        (workflow rules)
.claude/skills/ark-init/ark-specs.md →  <project>/docs/specs/ark-specs.md  (spec guide + templates)
```

After deployment, the project team owns both files and may customize them.

---

## ENTRY_FILE_TEMPLATE

Target: **< 60 lines**. Content is tool-agnostic.

```markdown
# {{ project_name }}

## Project Identity
{{ 3-5 lines: what this project is, core user value, tech stack summary }}

## Agent Rules
- When documentation and code contradict, code is the truth. Verify spec claims against code before acting on them.
- Avoid the curse of knowledge: documents must be self-contained for a zero-context reader
- Code changes must have corresponding test coverage
- Atomic commits: each minimal task ends with a commit
- Lazy creation: only create files when they have real content
- Split files at ~150 lines; merge when only 1-2 lines

## Perspective Files
{{ list, e.g.: }}
- product.md — product constraints and design direction
- tech.md — technical conventions and architecture constraints

## Context Loading
- Always load: the entry file + CONTEXT.md
- Working on changes: + docs/specs/ark.md (workflow rules)
- Writing/reviewing specs: + docs/specs/ark-specs.md (spec guide)
- Technical tasks: + docs/specs/tech.md
- Product design: + docs/specs/product.md
- Specific modules: per proposal.md context field

## Workflow
Project Ark framework. Full rules: **docs/specs/ark.md**
Commands: /ark:init, /ark:explore, /ark:propose, /ark:plan, /ark:autoexec, /ark:merge, /ark:status, /ark:resume
```

---

## CONTEXT_TEMPLATE

Target: **< 100 lines**.

```markdown
# Domain Glossary

## Core Concepts
{{ list domain-specific terms }}
- **{{ Term }}** — {{ one-line definition }}

## Project Conventions
- **Change** — an atomic modification to the project, containing both docs and code
- **Spec** — a document in docs/specs/. Two types: **index.md** (module overview, always present) and **perspective files** (product.md, tech.md — viewpoint-specific, created when a module's index.md outgrows a single file)
- **L0-L3** — change complexity levels (see docs/specs/ark.md § Change Pipeline)
```

---

## § Scanning Heuristics

Used in ark-init Step 1 to detect project type for CONTEXT.md and entry file tech stack summary.

| Signal | Inference |
|--------|-----------|
| `package.json` | Node.js; check `scripts`, `dependencies` |
| `tsconfig.json` | TypeScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml` / `setup.py` | Python |
| `*.csproj` / `*.sln` | .NET/C# |
| `pom.xml` / `build.gradle` | Java/Kotlin |
| `.github/workflows/` | Has CI/CD |
| `Dockerfile` | Containerized |

### Skip Always

`node_modules/`, `dist/`, `build/`, `.git/`, `vendor/`, `__pycache__/`, `.next/`, `target/`
