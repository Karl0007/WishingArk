---
name: ark-test-baseline
description: Detect missing test infrastructure (unit + e2e), install frameworks, write config, and verify green baseline. Integrates with /ark:exec pre-flight. Use when user says "test baseline", "set up tests", "add testing", or invokes /ark:test-baseline.
---

# /ark:test-baseline

Detect test gaps, fill them, verify green. Ensures /ark:exec pre-flight will pass.

**This skill ensures a project has runnable unit tests AND end-to-end tests.** It detects what's already there, reports findings, asks the user what scope to cover, then fills the gaps — nothing more.

---

## Entry Behavior

### No arguments (interactive)

Auto-detect project state and present findings:

```
## Test Baseline Report

Detected stack: [from docs/specs/tech.md or package.json/Cargo.toml/etc.]

Unit tests:    [✓ found | ✗ missing]  [framework if found]
E2E tests:     [✓ found | ✗ missing]  [framework if found]
Test command:  [✓ runnable | ✗ not found]

Gaps:
- [list what's missing]

What scope should I cover?
A) Infrastructure only — install frameworks, config, one hello-world test per layer (Recommended)
B) Infrastructure + seed tests — also write 2-3 example tests against existing code
C) Infrastructure + CI — also add GitHub Actions / CI pipeline config

[Your call:]
```

### With arguments

- `/ark:test-baseline unit` — only set up unit test layer
- `/ark:test-baseline e2e` — only set up e2e test layer
- `/ark:test-baseline --check` — report only, no changes (dry run)
- `/ark:test-baseline --auto` — non-interactive: use scope A + stack defaults, no user prompts (used by `/ark:autoexec --afk`)

### Non-interactive mode (--auto)

When invoked with `--auto` or from an AFK pipeline:
- Scope = A (infrastructure only)
- Framework = stack defaults from table below
- Do NOT prompt user for any decisions
- If defaults don't fit (stack not in table) → HALT with reason, don't guess

---

## Detection Logic

### Step 1: Read project context

Check these sources (read ALL that exist, don't stop at first hit — later sources may reveal e2e even if unit was found in step 1):

1. `docs/specs/tech.md` → Testing section (most authoritative for naming/commands)
2. `docs/specs/*/tech.md` → module-level testing info
3. Package manifest (`package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, etc.)
4. Config files (`jest.config.*`, `vitest.config.*`, `playwright.config.*`, `cypress.config.*`, `.mocharc.*`, `pytest.ini`, etc.)
5. Engine-specific test markers:
   - Unity: `Assets/Tests/` directory, `.asmdef` with `testAssemblies`, `manifest.json` containing `com.unity.test-framework`
   - Unreal: `Source/*/Tests/` directory, `.Build.cs` with test module references
   - Godot: `res://test/` or `addons/gut/` directory, `gut_config.json`
6. Existing test directories (`__tests__/`, `tests/`, `test/`, `spec/`, `e2e/`, `cypress/`)

### Step 2: Classify what exists

| Layer | Detected by | Status |
|-------|------------|--------|
| Unit | Test runner config OR test files importing a test framework OR `test` script in manifest OR engine test assembly (Unity `.asmdef` / UE test module / GUT plugin) | Present / Missing |
| E2E | Browser automation config (Playwright/Cypress/Selenium) OR e2e directory with test files OR engine Play Mode tests (Unity) / Gauntlet config (UE) / GUT headless scenes (Godot) | Present / Missing |
| Test command | `npm test` / `cargo test` / `pytest` / engine CLI equivalent exits 0 | Runnable / Broken / Missing |

### Step 3: Determine gaps

Only gaps get filled. If unit tests exist and work, skip them entirely — even if they use a framework you wouldn't choose.

---

## Gap Filling

### Framework Selection

Do NOT ask the user which framework to use if the project already has signals:

| Signal | Action |
|--------|--------|
| Existing unit tests use Jest | Add more Jest config, not Vitest |
| Project uses Vite | Recommend Vitest for unit (native Vite integration, no extra transform config) |
| Project has `playwright.config.*` | E2E = Playwright, done |
| Project has `.uproject` file | Unreal project → use engine defaults |
| Project has `ProjectSettings/` + `Assets/` | Unity project → use engine defaults |
| Project has `project.godot` | Godot project → use engine defaults |
| No signals at all | Use stack defaults (see table below) |

**Stack defaults** (used when no existing framework signals exist):

| Stack | Unit | E2E | Rationale |
|-------|------|-----|-----------|
| TypeScript / React / Next.js | Vitest | Playwright | Vitest: native ESM + Vite transform. Playwright: cross-browser + auto-wait. |
| TypeScript / Node (backend) | Vitest | Playwright (API mode) | Same toolchain. API mode = no browser overhead. |
| Python | pytest | pytest + httpx (API) or Playwright (UI) | pytest: standard. httpx: async-native HTTP client for API e2e. |
| Rust | built-in (`cargo test`) | — (skip unless web) | No extra dep needed. |
| Go | built-in (`go test`) | — (skip unless web) | No extra dep needed. |
| Unity (C#) | Unity Test Framework (Edit Mode) | Unity Test Framework (Play Mode) | Built-in. Play Mode tests run full scenes as e2e. |
| Unreal (C++) | Automation System (unit spec) | Gauntlet | Engine-native. Gauntlet runs full game sessions headless. |
| Godot (GDScript/C#) | GUT | GUT (headless mode: `--headless`) | Single framework covers both layers. Headless = CI-friendly. |

If stack is not in this table and no signals exist:
- Interactive mode → ask user which frameworks to use
- `--auto` mode → HALT: "Stack [X] has no default test framework. Run `/ark:test-baseline` interactively."

### Installation Steps

For each missing layer:

1. **Install dependencies** — dev dependencies only
2. **Write config file** — only required fields + test directory path. No custom reporters, no coverage config, no path aliases beyond what the project already uses.
3. **Create directory structure** — follow project conventions if visible, else standard (`__tests__/`, `e2e/`)
4. **Write one hello-world test** — proves the setup works (see requirements below)
5. **Verify green** — run the test command, confirm exit 0 with at least 1 test passing

### Hello-world test requirements

The hello-world test must:
- Actually import something from the project (not just `expect(1+1).toBe(2)`)
- Exercise the test framework's core features (describe/it/expect or equivalent)
- Pass on first run without manual intervention
- Demonstrate the pattern for writing future tests in this project

For e2e hello-world:
- Start the dev server (or document in a comment at the top of the test file: `// Prerequisite: dev server running at http://localhost:PORT`)
- Navigate to `http://localhost:<port>` (the app's local dev URL)
- Assert something meaningful renders (a heading, a button, a response body)

For game engine e2e hello-world:
- **Unity:** Play Mode test that loads a scene, waits N frames, asserts a GameObject exists
- **Unreal:** Gauntlet test that launches a map, ticks N frames, asserts an Actor is spawned
- **Godot:** GUT test with `yield(get_tree(), "idle_frame")` that loads a scene and asserts a node exists

---

## Scope: Seed Tests (Option B)

When user picks "Infrastructure + seed tests":

1. Identify 2-3 core modules using this heuristic: find files imported by the most other files (check import/require statements across `src/`). Pick the top 2-3 by import count.
2. Write one test per module covering the primary happy path
3. Each test should be a good example of "how to write tests in this project" — test behavior through public interfaces, not internal implementation details
4. Follow the project's existing test patterns if any exist (naming, structure, assertion style)

Do NOT attempt comprehensive coverage. Seed tests exist to demonstrate patterns.

---

## Scope: CI (Option C)

When user picks "Infrastructure + CI":

1. Detect existing CI (`.github/workflows/`, `.gitlab-ci.yml`, `Jenkinsfile`, etc.)
2. If CI exists → add test step to existing pipeline
3. If no CI → create minimal GitHub Actions workflow:
   - Trigger: push to main + PR
   - Steps: install → build → test (unit) → test (e2e)
   - Cache: dependencies
4. Verify workflow file is valid YAML

---

## Integration with ark-exec

`/ark:exec` pre-flight checks whether a test command exists and exits 0. This skill guarantees a stronger condition:

- **ark-exec pre-flight minimum:** test command exists and exits 0 (zero tests is acceptable)
- **ark-test-baseline guarantee:** test command exits 0 AND at least 1 unit test passes AND at least 1 e2e test passes (if applicable)

After `ark-test-baseline` completes successfully, `/ark:exec` pre-flight will never halt on "No test infrastructure detected."

---

## Integration with docs/specs/tech.md

After completing setup, update `docs/specs/tech.md` Testing section (or `docs/specs/<module>/tech.md`) **only if the file already exists**:

```markdown
## Testing

Unit: [framework] — `[command]`
E2E: [framework] — `[command]`
Config: [config file paths]
```

Do NOT create `docs/specs/tech.md` — that's `/ark:explore tech`'s job.

---

## Verification

After all installation:

1. Run unit test command → must exit 0 with >=1 test passing
2. Run e2e test command → must exit 0 with >=1 test passing
3. Run full test command (if composite, e.g., `npm test`) → must exit 0

**If any verification fails:**
1. Show the error output
2. Attempt one targeted fix (config typo, missing dependency, wrong path)
3. Re-run verification
4. If still failing → **do NOT declare done.** Present error to user and wait for guidance. The skill is incomplete until tests pass.

---

## Extract Test Conventions

After verification passes, scan the project's existing test files and extract a conventions document:

1. **Skip if** `docs/specs/test-conventions.md` already exists (user-authored takes priority)
2. Read 3-5 representative test files (unit + e2e if both exist). Look for:
   - Shared fixtures, helpers, utilities — where they live and how tests import them
   - Isolation strategy — how tests avoid sharing state (fresh process, temp dirs, DB transactions, etc.)
   - Wait/async strategy — how tests wait for readiness (selectors, events, polling — vs. hardcoded delays)
   - Setup/teardown patterns — per-test vs. per-suite, cleanup responsibilities
   - Naming and file structure conventions
3. Write findings to `docs/specs/test-conventions.md` using this skeleton:

```markdown
# Test Conventions

## Fixtures & Helpers
[Paths and one-line purpose of each shared utility. How to import.]

## Isolation
[How tests avoid state leakage. Per-test process? Temp directories? DB reset?]

## Wait Strategy
[Preferred async wait approach. What to avoid.]

## Setup / Teardown
[Who creates state, who cleans it up. Framework-managed vs. manual.]

## Anti-patterns
[Observed patterns to avoid — with reason.]
```

4. Only document what actually exists in the codebase. Do not invent conventions.
5. **Hard limit: ≤50 lines.** Every line costs context in the executing agent. Bullet points, not paragraphs. No examples longer than one line.

---

## Commit

After verification passes, commit the test infrastructure:

```bash
git add -A
git commit -m "chore: add test baseline ({unit_framework} + {e2e_framework})"
```

This ensures test infrastructure survives session disconnects and is available for `/ark:exec` pre-flight.

---

## What This Skill Does NOT Do

- **Write comprehensive test suites** — that's the executor's job during `/ark:exec`, guided by plan.md
- **Choose test philosophy** — that's the `tdd` skill's domain
- **Create docs/specs/tech.md** — that's `/ark:explore tech`
- **Fix pre-existing test failures** — only ensures NEW setup is green; existing broken tests are user's problem
- **Force framework migrations** — if Jest exists and works, do not migrate to Vitest

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll install both Jest and Vitest for unit tests" | One framework per layer. Follow existing signals. |
| "I'll write tests for every module" | Hello-world (scope A) or 2-3 seeds (scope B). Not comprehensive. |
| "Project already has unit tests but I'll set them up again my way" | Respect existing. Only fill genuine gaps. |
| "I'll skip verification because install succeeded" | Always verify. Install success != tests run. |
| "E2e isn't needed for this backend project" | Ask user, don't assume. API testing is e2e too. |
| "I'll create docs/specs/tech.md while I'm here" | Not your job. Only update if it already exists. |
| "The verification failed but it's probably fine" | NOT done. Fix or escalate. Never declare success with failing tests. |

---

## Guardrails

- **Detect before act** — always report findings before making changes
- **Respect existing** — never replace, override, or reconfigure working test infrastructure
- **Verify green** — skill is NOT complete until tests pass. No exceptions.
- **One framework per layer** — never install competing frameworks
- **Dev dependencies only** — test frameworks are never production dependencies
- **Non-interactive = defaults only** — `--auto` mode uses stack defaults, never guesses beyond the table
