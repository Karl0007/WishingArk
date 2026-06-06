# Ontology Format

Optimized for AI search and retrieval. Every field uses a fixed prefix — agent can grep to locate any concept or relationship type.

---

## Single-file layout (`docs/specs/ontology.md`)

Use when < 50 concepts.

```markdown
# Ontology

## Disambiguation

| Term | In [module A] | In [module B] | In [module C] |
|------|--------------|--------------|--------------|
| user | credential holder | account owner | — |

## [Concept Name]

- **def:** One-sentence definition
- **home:** Primary module where this concept's main type/class/schema is defined
- **also-in:** Other modules where this concept appears
- **is-a:** Parent concept (inheritance)
- **has-many:** Child concepts (composition)
- **belongs-to:** Parent in ownership hierarchy
- **triggers:** What this concept causes to happen
- **triggered-by:** What causes this concept to be created/changed
- **states:** state-a → state-b → state-c | state-d
  - `→` = transition (state-a can move to state-b)
  - `|` = alternative from same predecessor (state-b can move to state-c OR state-d)
  - Chain reads left-to-right; branch point is the state before `|`
- **constraint:** Rules that aren't obvious from code
- **disambig:** How this term differs from similar terms or same term in other modules
```

---

## Multi-file layout (`docs/specs/ontology/`)

Use when 50+ concepts. Split by domain.

```
docs/specs/ontology/
├── index.md        ← disambiguation table + concept list with home modules
├── billing.md      ← concepts homed in billing
├── auth.md         ← concepts homed in auth
├── combat.md       ← concepts homed in combat (game example)
└── inventory.md    ← concepts homed in inventory
```

`index.md` contains:
1. Disambiguation table (all cross-module term conflicts)
2. Concept inventory:

```markdown
| Concept | Def | Home | File |
|---------|-----|------|------|
| Transaction | Recorded financial event | billing | [billing.md](billing.md) |
| Order | Purchase intent with lifecycle | orders | [billing.md](billing.md) |
| Character | Player or AI entity in game world | core | [combat.md](combat.md) |
```

Domain files contain the full concept entries.

---

## Field reference

All fields are optional. Only include fields that carry information.

| Field | When to include | When to skip |
|-------|----------------|-------------|
| **def** | Always | Never skip this |
| **home** | Always | Never skip this |
| **also-in** | Concept appears in 2+ modules | Single-module concept |
| **is-a** | Clear inheritance relationship | No parent concept |
| **has-many** | Owns a collection of children | No children |
| **belongs-to** | Owned by a parent | Top-level concept |
| **triggers** | Causes side effects in other modules | No cross-module effects |
| **triggered-by** | Created/changed by external events | Self-contained lifecycle |
| **states** | Has a lifecycle/state machine | Stateless concept |
| **constraint** | Invisible rule that agent would violate | Rule obvious from code |
| **disambig** | Same word means different things somewhere | Unambiguous term |

---

## What belongs in ontology vs. spec

| Information | Where it goes | Why |
|---|---|---|
| "Transaction is a recorded financial event" | ontology | Concept definition — project-wide |
| "Transactions retry 3x with exponential backoff" | spec (billing/index.md) | Module behavior — implementation detail |
| "Order has-many Transactions" | ontology | Cross-module relationship |
| "PaymentService.process() → Repo.save() → EventBus.emit()" | spec (billing/index.md) | Call chain — module-specific architecture |
| "'user' means different things in auth vs billing" | ontology | Disambiguation — cross-module confusion |
| "All amounts are in cents, never float" | BOTH | Ontology: constraint on Amount concept. Spec: repeated in relevant modules because agent needs it at point of use |

---

## Example: game project

```markdown
# Ontology

## Disambiguation

| Term | In combat | In inventory | In economy |
|------|----------|-------------|-----------|
| item | thing that can be used in combat | thing in a slot | thing with a price |
| damage | calculated combat result | durability loss | — |

## Character

- **def:** A player-controlled or AI-controlled entity that exists in the game world
- **home:** core
- **also-in:** combat, inventory, social
- **has-many:** Item, Buff, Skill
- **states:** idle → in-combat → dead → respawning → idle
- **constraint:** Max 1 Character per Player. Character persists across sessions.

## Item

- **def:** An object that a Character can own, equip, use, or trade
- **home:** inventory
- **also-in:** combat, economy
- **belongs-to:** Character
- **has-many:** Modifier
- **states:** unowned → owned → equipped → destroyed
- **constraint:** Equipped items affect combat stats. Destroying an equipped item must unequip first.
- **disambig:** In combat, "item" usually means "usable item" (subset). In economy, "item" includes non-usable items like materials.

## Weapon

- **def:** An Item that deals damage when equipped and used in combat
- **home:** combat
- **is-a:** Item
- **triggers:** DamageCalculation (on attack)
- **constraint:** Weapon.damage is base value; actual damage = (Weapon.damage + Character.ATK - Target.DEF) * ElementMultiplier. This formula lives in combat/DamageCalculator, NOT on the Weapon itself.

## Buff

- **def:** A temporary modifier applied to a Character that changes stats or behavior
- **home:** combat
- **belongs-to:** Character
- **triggers:** StatRecalculation (on apply/expire)
- **states:** active → expired
- **constraint:** Buffs stack additively unless tagged [UNIQUE]. Max 10 active buffs per Character.
```
