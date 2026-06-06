---
name: ark-ontology
description: Build and maintain a project's concept ontology from specs and code. Extracts cross-module concepts, relationships, disambiguation, and state machines. Use when user says "ontology", "build ontology", "concept map", "domain model", or invokes /ark:ontology. Also triggered after a full /ark:explore completes.
---

# /ark:ontology

Build the project's concept model — what concepts exist, how they relate, where they conflict across modules.

**Prerequisite:** `docs/specs/index.md` must exist. If it doesn't, tell the user to run `/ark:explore` first and stop. Do NOT attempt to build ontology without specs — you need the team's module structure as a starting point.

---

## When to use

- After `/ark:explore` completes (all modules explored)
- When project has high concept density (games, finance, medical, legal)
- When multiple modules use the same terms differently
- Before a large cross-module change (to map impact)

---

## Routing

| Command | What it does |
|---------|-------------|
| `/ark:ontology` | Full build — scan all specs + code, build ontology |
| `/ark:ontology review` | Review existing ontology against current specs/code for drift |
| `/ark:ontology <concept>` | Deep-dive a single concept — trace across all modules |

---

## Full Build Process

### Phase 1 — Harvest concepts from specs

Read every file in `docs/specs/`. For each, extract:
- Named entities (things with identity: User, Order, Transaction)
- Named processes (things that happen: Checkout, Authentication, Rendering)
- Named states (lifecycle stages: pending, active, expired)

**Do NOT read code yet.** Specs are the starting point — they tell you what the project team considers important.

**Output:** Internal candidate list. Do not present yet.

### Phase 2 — Cross-reference and detect conflicts

For each candidate concept:
1. Does it appear in multiple modules' specs?
2. If yes — is the definition consistent or conflicting?
3. Does it have relationships to other concepts (owns, triggers, is-a, part-of)?
4. Does it have a lifecycle/state machine?

**Focus on conflicts.** A concept that appears in one module with one clear meaning is less valuable to document than one that appears in three modules with subtly different meanings.

**Stop when:** You can answer "which concepts would cause an agent to make a cross-module mistake if it only read one module's spec?" If you can't identify any, the project may not need a formal ontology — tell the user.

### Phase 3 — Verify against code

For every concept with a conflict or cross-module relationship:
- Find the actual code that implements it (classes, types, database schemas, API contracts)
- Confirm that the spec's description matches what the code does
- Note where code reveals relationships or constraints that specs missed

**Do NOT skip this phase.** Specs may have inherited the author's assumptions. Code is truth.

**Do NOT trust spec wording over code behavior.** If spec says "User is an account holder" but code shows User is a thin auth wrapper with no account data, the code wins.

### Phase 4 — Present to user

Present your findings in one message. Structure:

```
"Here's what I found across your project's concepts:

**Cross-module concepts (appear in 2+ modules):**
- User — in auth: credential holder; in billing: account owner; in game: player character
- Transaction — in billing: financial event; in auth: DB transaction (DIFFERENT concept, same word!)

**Concept relationships I inferred:**
- Order has-many Transaction
- Refund is-a Transaction
- Character has-many Item; Weapon is-a Item

**State machines I found:**
- Order: draft → confirmed → shipped → delivered | cancelled
- Transaction: pending → processing → completed | failed

**Constraints that cross module boundaries:**
- Amount is always cents (integer) — enforced in billing, but payment module receives float from external API and converts

**Things I'm uncertain about:**
- Is 'Plan' (pricing) related to 'Subscription', or are they independent concepts?

What's wrong? What am I missing? Any concepts I should add or remove?"
```

**Do NOT write ontology without presenting first (interactive mode).**
**Do NOT skip uncertain items — they are the most valuable part of this conversation.**

### Phase 5 — Write ontology

After user confirms/corrects, write to `docs/specs/ontology.md` (or `docs/specs/ontology/` if 50+ concepts).

Use the format defined in [FORMAT.md](FORMAT.md).

---

## AFK Mode (--afk)

Skip Phase 4 presentation. Write directly with confidence tags:
- Definitions and relationships clearly evidenced in code → write normally
- Conflicts and disambiguation → always write (this is the core value)
- Uncertain relationships → mark `<!-- NEEDS CONFIRMATION: [specific question] -->`

---

## Review Mode (`/ark:ontology review`)

Compare existing `docs/specs/ontology.md` against current specs and code:
1. Are there new concepts in specs that aren't in ontology?
2. Are there concepts in ontology whose code has changed?
3. Are there new cross-module conflicts?

Present drift to user. Update after confirmation.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "I'll document every class/type I find" | Only concepts that cross module boundaries or cause confusion within a module. Single-module internal types with one clear meaning don't belong here. |
| "I'll just summarize the specs" | Go to code. Specs may be wrong or incomplete. Phase 3 exists for a reason. |
| "This project doesn't seem to need ontology" | Tell the user. Not every project needs one. Better to say so than produce a useless glossary. |
| "I'll skip the uncertain items" | Uncertain items are WHERE THE BUGS LIVE. Always surface them. |
| "I'll write the ontology without presenting" | The human correction is the most valuable part. Do NOT skip Phase 4. |
