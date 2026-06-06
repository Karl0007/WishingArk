---
name: ark-learn
description: Extract reusable lessons from the current change. Main agent proposes lessons, reviewer agent validates. Output lands in docs/changes/{name}/lessons.md for merge to consolidate into specs. Use when user says "learn", "extract lessons", "what did we learn", or invokes /ark:learn.
---

# /ark:learn

Propose reusable lessons from your current context. A reviewer agent validates them.

**Input:** `/ark:learn [change-path]` — if omitted, uses most recently modified `docs/changes/**/progress.yaml`.

---

## Flow

```
1. Propose lessons (you)
2. Review lessons (sub-agent → reads REVIEWER.md)
3. Write lessons.md
```

---

### Step 1: Propose Lessons

Review your current context — what went wrong, what was harder than expected, what would you tell the next agent working on similar tasks?

Draft lessons freely:

```yaml
- id: L1
  type: test_gap | impl_pattern | spec_gap | convention_missing | plan_gap
  summary: "What agents should do differently"
  target_spec: "docs/specs/{module}/..."
  actionable_rule: "Concrete rule that would prevent recurrence"
  keywords: [keyword1, keyword2, keyword3]  # for LESSON_KEYWORD grep search
```

**Proposing rules:**
- Each lesson MUST have a concrete `actionable_rule`. Be shot and clear.
- Each lesson MUST have `keywords` — 3-6 lowercase terms an agent would grep for when working on related tasks.
---

### Step 2: Review Lessons

Spawn reviewer agent:

```
Read {skill_dir}/REVIEWER.md for your instructions.
Proposed lessons: {yaml from Step 1}
Change context: docs/changes/{name}/proposal.md
```

Expected response: `APPROVED: [L1, L3] | DROPPED: [L2: reason] | SHARPENED: [L1: new wording]`

- KEEP → include as-is
- SHARPEN → update `actionable_rule` with reviewer's wording
- DROP → exclude

If ALL dropped → "No reusable lessons survived review." Done.

---

### Step 3: Write lessons.md

Append approved lessons to `docs/changes/{name}/lessons.md`:

```markdown
# Lessons: {change-name}

## L1: {summary}

- **Type**: {type}
- **Rule**: {actionable_rule}
- **Target**: `{target_spec}`
- **LESSON_KEYWORD**: {keyword1}, {keyword2}, {keyword3}
```

Commit:
```bash
git add docs/changes/{name}/lessons.md
git commit -m "ark-learn({change_name}): extract {N} lessons"
```

---

## Rules

- **Fewer is better.** 2 sharp lessons > 5 vague ones.
- **Lessons target specs, not code.** They change how future agents are instructed.
- **Reviewer is the gate.** Reviewer decides what's reusable vs one-off. Dropped = dropped.
- **Additive.** Running multiple times appends, never overwrites.

---

## Red Flags

| If you're thinking... | Stop. Instead: |
|---|---|
| "The rule is: don't make mistakes" | Not actionable. What specific check prevents this? |
| "I'll skip the reviewer" | Never. Reviewer filters one-offs and catches duplication. |
| "This lesson targets the code" | Lessons change specs/conventions, not current code. |
