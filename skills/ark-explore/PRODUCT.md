# Product Explore

Deep investigation of the product dimension. Write `docs/specs/<scope>/product.md`.

**Triggered by:** `/ark:explore <module> product` or `/ark:explore . product` (root-level)

---

## Output

`docs/specs/<module>/product.md` (or `docs/specs/product.md` for root). Same template for both — fill sections as relevant, omit empty ones.

Template from `docs/specs/ark-specs.md § product.md Structure`:

```markdown
# Product — {{ scope }}

## Identity
{{ What this is. Who it's for. Core value. }}

## What This Is NOT
{{ Identity boundaries — what this deliberately is not }}

## Target Users
{{ User profiles, experience level, usage context }}

## User Journeys
{{ Core flows from user's perspective: "User does X → sees Y → does Z" }}

## Experience Goals
{{ What the experience should feel like — fast? calm? powerful? simple? }}

## Value Hierarchy (first wins on conflict)
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

## Interactive Mode

### Phase 1 — Observe deeply

Don't just read the README and stop. Build a deep understanding of **who this is for and why it exists.**

**What to read:**
- User-facing code: UI, API endpoints, CLI commands, error messages — what does the user actually see and touch?
- Existing specs (index.md, README, any docs/) — what does the team say this is?
- Tests — what scenarios are tested? These reveal what behaviors the team considers important.
- Config and defaults — what comes out of the box? What requires setup? This reveals experience priorities.
- Issues/PRs/changelogs if accessible — what are users asking for? What's being rejected?

**What to notice:**
- Where does the product spend its complexity budget? (That's where its value is.)
- What's conspicuously absent? (Deliberate exclusion or oversight?)
- What would a new user's first 5 minutes look like?
- Where does the product say "no" — through errors, missing features, or explicit messages?

### Phase 2 — Infer product understanding

Go beyond surface observations. Ask yourself the hard questions:

- **Identity:** If I had to explain this to someone in 10 seconds, what would I say? What would I NOT say? The gap between these is the identity boundary.
- **Users:** Not just "who" but "what level of expertise do they have?" and "what are they doing right before and after using this?" Context shapes expectations.
- **Values:** When the code made a tradeoff (e.g., simpler API vs. more powerful API), which side won? Do this 3-4 times across different areas — the pattern reveals the value hierarchy.
- **Experience:** What's the emotional texture? Is this a tool you use quickly and leave, or one you live in all day? The answer shapes hundreds of small decisions.
- **Exclusions:** What's a "reasonable feature" that this product clearly doesn't have? Is that intentional? The things a product refuses to be are as defining as what it is.
- **Open questions:** Where does the product feel unfinished or inconsistent? These are likely areas where decisions haven't been made yet.

**Before moving to Phase 3, reflect:** "If someone asked me 'what would this product refuse to become, even if users asked for it?', could I answer confidently? And could I explain WHY for each answer?" If not, your understanding of the product's identity and values is still shallow — go back and look for more evidence.

**Then push deeper:** "What tension exists between this product's stated values? Where do value #1 and value #2 conflict — and which one actually wins in the code?" If you can't identify at least one real tension, your value hierarchy is probably a guess, not evidence-based.

### Phase 3 — Present to user

Present your inferences in one message:

```
"Here's my understanding of [scope] from a product perspective:

**Identity:** This is [what], for [whom], delivering [value].

**Not:** [boundaries]

**Users:** [who, what level, what context]

**Core journey:** User does X → sees Y → does Z

**Experience feels like:** [adjectives]

**Values (my guess at priority):**
1. [first]
2. [second]
3. [third]

**Exclusions I noticed:** [things that seem deliberately absent]

**Uncertain:** [things I can't tell from code/docs alone]

What's wrong? What am I missing?"
```

Wait for corrections.

### Phase 4 — Write spec

Compile confirmed understanding into `docs/specs/<module>/product.md` using the template.

**Do NOT write product.md without presenting inferences to the user first (interactive mode).** The human correction is the most valuable part.

---

## AFK Mode

Write all sections, split by confidence:
- Sections the agent is confident about → written normally
- Sections that need human judgment → marked `<!-- NEEDS CONFIRMATION: [specific question] -->`

Example:
```markdown
## Value Hierarchy
<!-- NEEDS CONFIRMATION: Is correctness really #1, or is speed more important for this module? -->
1. Correctness
2. Speed
3. Simplicity
```

---

## When to create product.md

product.md is a **deeper investigation**, not a required file. Create it when:
- The module has complex user-facing behavior that index.md can't capture in a few lines
- Product decisions (what to build, for whom, what tradeoffs) are non-obvious
- Multiple agents might make different product-level choices without guidance

Do NOT create it "for completeness" — if index.md's Boundary section is sufficient, product.md adds no value.
