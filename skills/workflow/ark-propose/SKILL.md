---
name: ark-propose
description: Turn ideas into bounded change proposals. Routes through brainstorm (diverge), discuss (clarify), decompose (phase-split L3 changes), and grill (stress-test) sub-flows based on idea maturity. Outputs proposal.md. Use when user says "propose", "I want to do", "let's build", "change request", or invokes /ark:propose.
---

# /ark:propose

Route an idea through the right thinking process, then compile into proposal.md.

For changes that touch a reusable mechanism, seam, API/schema/declaration boundary, adapter/provider/plugin point, or other architecture-sensitive area, capture the architecture intent without designing the implementation: what touched code should become easier to change, test, or reason about.

**Input:**
- `/ark:propose <idea>` — AI routes to appropriate sub-flow
- `/ark:propose --brainstorm` — force brainstorm mode
- `/ark:propose --discuss` — force discuss mode
- `/ark:propose --grill` — force grill mode
- `/ark:propose` (no args) — ask user what's on their mind, then route

---

## Routing

Assess the user's input and route:

| Signal | Route to |
|---|---|
| Problem without clear cause ("tests are slow", "users complain about X", "something feels wrong") | **brainstorm** (investigate first, then ideate) |
| Exploratory, no direction ("how should we...", "what if...", "I want something cool for...") | **brainstorm** (ideate directly) |
| Has direction, needs clarification ("A or B?", "I want X but not sure about scope") | **discuss** |
| Clear requirement ("fix bug X", "change flow from A to B", "add feature Y") | **grill** |

If `--flag` is provided, skip assessment and enter that sub-flow directly.

If the signal is ambiguous (could be brainstorm or discuss), ask the user: "You have an idea — want to explore more options first, or nail down the details of this one?"

**Each sub-flow has its own prompt file.** Read and follow the relevant one:
- [brainstorm.md](brainstorm.md) — divergent thinking partner
- [discuss.md](discuss.md) — convergent draft-correct editor
- [decompose.md](decompose.md) — phase splitting for L3 changes
- [grill.md](grill.md) — pressure test against project reality
- Architecture-sensitive proposals should carry intent forward, not implementation detail: name the touched seam and desired effect on locality/leverage, then let `/ark:plan` design the work.

---

## Transitions

Each sub-flow can lead to the next. When you detect the transition condition, **offer** (don't force):

```
brainstorm → discuss:  User converges on a specific idea
  Offer: "Sounds like you have a direction. Want to flesh it out?"

discuss → decompose:  What / What-NOT / constraints are clear AND scope looks L3
  discuss writes draft.md, then decompose reads it and suggests phase split.

discuss → grill:  What / What-NOT / constraints are clear AND scope is L1/L2
  discuss writes draft.md, then grill reads it.

decompose → grill:  User accepts or rejects split
  decompose updates draft.md (scoped to Phase 1, or unchanged). Grill reads it.

grill → Go Sequence:  User says "enough" or shared understanding reached
  Read and follow [go-sequence.md](go-sequence.md) to compile proposal.md.
```

**Allow backward transitions.** If grill reveals the idea is wrong, go back to discuss or brainstorm. If discuss reveals the direction is unclear, go back to brainstorm. Follow the user's lead.

---

## What You Don't Have To Do

- Follow all three sub-flows for every idea. A clear requirement goes straight to grill.
- Ask the user which sub-flow to use. Route silently based on signals.
- Be neutral. Have opinions. Recommend defaults. The user wants a thinking partner, not a form.
- Preserve every idea from brainstorm. Convergence means killing options — that's fine.
- Make the proposal perfect on first compile. Show → correct → show is faster than agonize → present.

---

## Change Directory

- **Create when first writing to disk** — typically when discuss writes draft.md, or at Go Sequence Step 6 if discuss was skipped
- **Naming:** AI proposes a kebab-case name from the content; user confirms or renames

---

## Cross-Session Recovery

If user pauses mid-propose ("save this", "I'll come back", or session ending with unfinished work):
- Save a conversation summary to `docs/changes/<name>/notes.md`
- Next `/ark:propose` in that change directory picks up from the summary

---

## Red Flags

| If you're doing this... | Stop. Do this instead. |
|---|---|
| Routing everything to grill because it's "faster" | Respect the input signal. Underbaked ideas need brainstorm or discuss first. |
| Skipping What-NOT section | This is propose's signature output. Every proposal needs explicit boundaries. |
| Writing implementation details (file changes, code) | Propose is What and Why, never How. That's /ark:plan's job. |
| Asking "do you approve?" | Say "Override anything above, or 'go' to write." Default is forward motion. |
| Listing every spec in Context field | Minimum viable set. If an agent loaded ONLY these, would they have enough without noise? |
| Compiling a proposal that only makes sense with conversation context | Self-contained test: a stranger reads this cold in 3 months. Does it stand alone? |
| Architecture-sensitive change has no architecture intent | Add a short intent: touched seam, desired improvement, and explicit non-goals. Do not write implementation steps. |
| Refusing to route because the topic isn't engineering | Never refuse an explicit invocation. Brainstorm, discuss, and grill work on any topic. Only Go Sequence requires an engineering change. |
