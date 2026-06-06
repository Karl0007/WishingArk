# Module Explore

Write or update a module's `docs/specs/<module>/index.md` — the four-layer overview.

**Triggered by:** `/ark:explore <module>`

---

## Output

`docs/specs/<module>/index.md` — recommended 20-50 lines (not a hard limit).

```markdown
# [Module Name]

## Boundary & Constraints
- Responsible for: ...
- NOT responsible for: ... (belongs to [other module])
- Rules: [invariants code doesn't make obvious]
- Direction: [what's stable / what's migrating]

## Behavior
- [Core flows: when X happens, the system does Y then Z]
- [Business rules scattered across multiple files]
- [Edge cases not obvious from a single file]

## Architecture
- [Call chain: A → B → C → D]
- [Data flow: how requests/events move through]
- [Integration points with other modules]

## Entry Points
- path/to/MainFile.ts — [one-line role]
- path/to/config.yaml — [what it controls]
```

---

## Interactive Mode (default)

### Phase 1 — Observe silently

Read code **deeply** into this module. Don't output anything yet.

**How deep:** Don't just read the entry file and stop. Follow the full call chain from entry point to the deepest implementation detail. Read the actual function bodies, not just signatures. Understand what happens at each step, what error cases are handled, what edge cases exist.

**What to read:**
- Entry points → follow every significant code path inward
- Internal helpers and utilities this module uses
- Config files, constants, types that shape behavior
- Tests — they reveal intended behavior and edge cases the code handles
- Related modules at the boundary (how does data come in? how does it go out?)

**What to notice:**
- Patterns and conventions (what's consistent across this module?)
- Anomalies (what breaks the pattern? why might this be different?)
- Data flow (trace a real request/event from entry to exit)
- Internal structure (what's the public interface vs. internal implementation?)
- Hidden rules (what would break if you changed it naively?)

**Stop when:** You can explain the module's internal mechanics in detail — not just "what it does" but "how it does it, step by step, and what constraints govern each step." If you can only give a surface-level summary, you haven't read deep enough.

**Before moving to Phase 2, reflect:** "If a new developer asked me 'why is it done this way and not another way?', could I answer for every major design choice in this module?" If not, go back and read more.

**Then push deeper:** "What's the second-order consequence? If someone changed the most obvious thing to change in this module, what would break that ISN'T in the same file?" If you can't answer, you've understood the module in isolation but not its hidden coupling.

### Phase 2 — Infer constraint layer

Internally form your understanding of the **invisible rules and boundaries** — things a future agent would get wrong without knowing. Include anomalies ("X breaks the pattern — intentional?").

### Phase 3 — Infer cognitive layer

Internally form your understanding of **how the system works** — flows and architecture that span multiple files.

### Present Phase 2+3 together

Present both layers to the user **in one message**. Use ASCII diagrams if it helps the human visualize complex flows (diagrams are for presentation only, not for the spec file). Only ask the user once:

```
"Based on reading the code, here's my understanding of [module]:

**Constraints:**
  Boundary:
  - Responsible for: X, Y, Z
  - NOT responsible for: A (that's [other]'s job)
  Rules:
  - All database access goes through Repository classes (deliberate or accidental?)
  - External APIs are wrapped in adapters/ (deliberate isolation?)
  Direction:
  - I see both OldPattern and NewPattern — which should new code follow?
  Anomalies:
  - File X breaks the pattern — intentional?

**Behavior:**
  Key behaviors:
  - Failed payments retry 3x with exponential backoff, then mark as failed
  - Refunds are partial (amount ≤ original) and create a separate transaction record

**Architecture:**
  Core flow:
  - Request → Controller.validate() → Service.process() → Repo.save() → EventBus.emit()
  Structure:
  - PaymentService is the only public interface; everything else is internal
  - Webhook handler runs async, updates state, then notifies downstream

**Entry Points:**
- src/payment/PaymentService.ts — main interface
- config/payment.yaml — configuration

What's wrong? What am I missing?"
```

Wait for corrections.

### Phase 4 — Write spec

Compile confirmed understanding into `docs/specs/<module>/index.md` using the four-layer template.

Show the draft to user. User says "looks good" or gives corrections → apply → commit.

If user is unsure about a section, mark with `<!-- uncertain -->`.

---

## AFK Mode (--afk)

All four layers, but constraints are split by confidence:

```markdown
# [Module Name]

## Boundary & Constraints
- Responsible for: X, Y, Z
- NOT responsible for: A (belongs to [other])

### High Confidence (from clear code patterns)
- All database access goes through Repository classes (~100% consistent)
- External APIs wrapped in adapters/ (consistent pattern, likely deliberate)

### Needs Confirmation
- Is the 1-hour token expiry a hard security rule or just a default?
- src/legacy-pay/ appears deprecated — confirm?

## Behavior
[Agent's best understanding]

## Architecture
[Agent's best understanding]

## Entry Points
[Key files]
```

**Why split by confidence?** Interactive mode asks the human directly — no need to guess. AFK has no human in the loop, so it writes what it's confident about and flags what needs confirmation.

**Parallel:** Multiple AFK agents can explore different modules simultaneously. Human reviews all drafts afterward.

---

## What NOT to write

- ❌ "This module uses TypeScript" — obvious from file extensions
- ❌ "PaymentService has a `charge()` method" — agent can read the file
- ❌ "Tests are in `__tests__/`" — standard convention
- ✅ "All amounts are in cents (integer), never floating point" — invisible rule
- ✅ "Webhook → PaymentService.confirm() → EventBus → NotificationService" — 4-file trace
- ✅ "src/legacy-pay/ is deprecated; new code uses src/payment/" — code can't tell the future

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "Every directory with code should be a module" | Modules are functional, not physical |
| "I'll write constraints without presenting first" | Interactive: present for confirmation. AFK: tag confidence. |
| "This is obvious from reading the code" | Don't write it. Specs are for non-obvious things only. |
| "I'll skip presenting and just write the spec" | The human correction IS the value. |
| "The existing spec says X, so I'll assume that's true" | Code is truth, not docs. Verify any spec claim against code before relying on it. |
