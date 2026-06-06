# Tech Explore

Deep investigation of the technical dimension. Write `docs/specs/<scope>/tech.md`.

**Triggered by:** `/ark:explore <module> tech` or `/ark:explore . tech` (root-level)

---

## Output

`docs/specs/<module>/tech.md` (or `docs/specs/tech.md` for root). Same template for both — fill sections as relevant, omit empty ones.

Template from `docs/specs/ark-specs.md § tech.md Structure`:

```markdown
# Technical — {{ scope }}

## Stack
{{ language, framework, runtime, key libraries }}

## Project Structure
{{ brief description of source layout }}

## Build & Run
{{ commands to build, run, test }}

## Best Practices
{{ Recommended patterns and idioms — the "how we do things here" }}

## How to Add / Change
{{ How to add a new feature, endpoint, module. Which files to create, where to register, what boilerplate. }}

## Coding Standards
{{ formatting, naming conventions }}

## Commit Format
{{ Conventional Commits, Angular, project-specific }}

## Testing
{{ test framework, coverage expectations, how to write tests here }}

## Technical Constraints
{{ Rules that code alone doesn't make obvious }}

## Direction
{{ What's stable vs. migrating. What's deprecated. Where new code should go. }}
```

---

## Interactive Mode

### Phase 1 — Observe deeply

Don't just grep for patterns and stop. Build a deep understanding of **how things are built here and why.**

**What to read:**
- Multiple examples of the same operation (e.g., 3+ API endpoints, 3+ services) — the pattern emerges from repetition, not from one instance
- Build system and CI/CD — what's automated? What's manual? This reveals what the team trusts.
- Test setup and test patterns — how are tests structured? What's mocked? What's integration-tested?
- Config files (linters, formatters, tsconfig, Makefile) — these encode standards the team cares about
- Git history of a few files — how do commits look? How do PRs flow? What's the review culture?
- Error handling — how does the codebase handle failures? Is there a consistent strategy?

**What to notice:**
- What's the "golden path" for adding something new? (Trace what files a recent feature touched.)
- Where are the consistency gaps? (Old code does X, new code does Y — migration in progress?)
- What would a new developer get wrong on day one? (These become constraints and best practices.)
- What's enforced by tooling vs. enforced by convention alone? (Convention-only rules are fragile and need to be documented.)

### Phase 2 — Infer technical understanding

Go beyond listing patterns. Ask yourself the hard questions:

- **Best practices:** If I were adding a new feature tomorrow, what would the "right" way look like? Can I describe the steps without guessing? If not, that's a gap that needs documenting.
- **Constraints:** What would silently break if I violated a convention? (These are the invisible rules that code alone doesn't enforce.)
- **Direction:** I see old patterns and new patterns coexisting — which one wins? The one with more recent usage? The one in the config? Ask yourself what evidence suggests the direction.
- **Inconsistencies:** Not all inconsistencies are bad — some are deliberate (legacy compatibility, performance hotpath). Which are intentional vs. which are debt?
- **How-to-change:** Can I describe "add a new X" as a reproducible recipe? If the steps are unclear, that's exactly what tech.md should capture.

**Before moving to Phase 3, reflect:** "If a new developer on day one asked me 'how do I add a new endpoint/feature/module here?', could I give them a step-by-step answer without saying 'I think' or 'probably'?" If not, your understanding of the project's conventions and patterns is still incomplete — go read more examples.

**Then push deeper:** "What's the non-obvious constraint that would make my step-by-step recipe silently produce broken code? What ordering dependency, registration step, or naming convention would I miss if I only followed the happy path?" If you can't identify at least one such trap, you haven't found the real constraints yet.

### Phase 3 — Present to user

Present inferences in one message:

```
"Here's my understanding of [scope]'s technical conventions:

**Stack:** [language, framework, key libs]

**Patterns I see:**
- [pattern 1 — with example file]
- [pattern 2 — with example file]

**How to add a new [feature/endpoint/etc]:**
1. Create file at [path]
2. Register in [config]
3. Add tests at [path]

**Constraints I inferred:**
- [rule] (deliberate or accidental?)
- [rule] (consistent ~100% of the time)

**Direction:**
- [old thing] → [new thing] (migration in progress?)
- [deprecated?] (no recent commits)

**Uncertain:** [things I can't tell]

What's wrong? What am I missing?"
```

Wait for corrections.

### Phase 4 — Write spec

Compile confirmed understanding into `docs/specs/<module>/tech.md` using the template.

**Do NOT write tech.md without presenting inferences to the user first (interactive mode).** The human correction is the most valuable part.

---

## AFK Mode

Write all sections, split by confidence:
- Sections the agent is confident about → written normally
- Sections that need human judgment → marked `<!-- NEEDS CONFIRMATION: [specific question] -->`

Example:
```markdown
## Direction
- src/api/v1/ appears deprecated (no commits in 6 months)
  <!-- NEEDS CONFIRMATION: Is v1 actively deprecated or just stable? -->
- New endpoints being added to src/api/v2/
```

---

## When to create tech.md

tech.md is a **deeper investigation**, not a required file. Create it when:
- The module has complex technical patterns that index.md's Architecture section can't capture
- There are non-obvious "how to do things" rules new developers would miss
- Best practices and recommended change patterns would save significant time

Do NOT create it "for completeness" — if index.md's Architecture + Constraints sections are sufficient, tech.md adds no value.
