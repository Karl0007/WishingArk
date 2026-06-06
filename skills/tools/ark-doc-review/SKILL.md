---
name: ark-doc-review
description: Spawn a zero-context lightweight Agent to review a document for ambiguity, unstated assumptions, and curse-of-knowledge issues. The reviewer can search the repo like a real new team member. Use when user says "review doc", "doc review", "zero context test", "check this doc", or after writing any important document.
---

# Doc Review

Simulate a zero-context reader to catch gaps the author can't see (curse of knowledge).

## Process

1. Select PASS standard: `intent` (proposal/design), `execute` (plan/task), or `decide` (spec/reference). If unclear, ask user.
2. Select lens (main agent decides before spawning): if target doc is agent-facing (skill, prompt, workflow), apply `agent-executable` lens **on top of** base rules. Otherwise, base rules only.
3. Spawn lightweight Agent (cheapest/fastest model available) — NO conversation history, only target doc + repo read access
4. Reviewer outputs all issues in one pass
5. Main Agent triages:
   - **Self-fix**: obvious answer / already in repo / no trade-off → fix, then batch-summarize to user
   - **Escalate**: genuine ambiguity / needs human judgment → ask user one at a time, highest severity first
6. Offer re-review. Repeat until PASS or user stops.

## PASS standard

| Type | PASS standard | Meaning |
|------|--------------|---------|
| Proposal / design | `intent` | "I understand the intent and constraints" |
| Plan / task | `execute` | "I can execute without asking the author" |
| Spec / reference | `decide` | "I can make correct decisions from this" |

## Review Lenses

Lenses add domain-specific checks on top of the base 6 rules. Apply automatically based on document type.

| Lens | Auto-apply when | Extra checks |
|------|----------------|--------------|
| `agent-executable` | Target is a skill, agent prompt, or workflow instruction | 7-13 below |

### `agent-executable` lens

Apply when target doc is meant to be **executed by an AI agent** (skills, prompts, workflow definitions, runbooks for agents).

Additional checks (numbered 7-13 to extend base rules):

7. **Cross-file reference as execution instruction** — doc says "follow X.md" or "see Y for details" where the referenced content is critical to correct execution. An agent may not follow the link.
8. **Positive instruction without prohibition** — doc says "do X first" but never says "Do NOT skip X." A rushing executor may treat it as optional.
9. **Example mistaken for hard requirement** — doc uses "e.g." or shows one example, but reader could interpret it as the only valid approach.
10. **"Repeat/same as above" without self-contained steps** — doc says "repeat for Y" or "same process." If reader lost prior context, they can't execute independently.
11. **Quality requirement without measurable stop condition** — doc says "read deeply" or "understand thoroughly" without defining how the executor knows they're done.
12. **Assumed reader identity or runtime context** — doc assumes reader knows what tool they're running in, what environment they have, or what prior steps happened.
13. **Depth-dampening language contradicts quality expectation** — doc requires deep execution in one place but uses softening words elsewhere ("lightweight", "broad understanding is sufficient", "without additional reading", "just use what you already know") that signal the agent to cap effort. The agent follows the dampener, not the depth requirement.

## Reviewer prompt

```
You are a new developer. ZERO prior context — no history, no meetings.
You may search/read files in the repo as a real new hire would.
Keep searches brief (max 10 lookups). If a term seems like general industry knowledge, don't search — just judge from context.

PASS standard: {intent | execute | decide}
{lens_block}

Find every place where:
1. Term used without definition (not findable in repo)
2. Decision stated without "why"
3. Sentence has multiple interpretations
4. Writer assumes knowledge the document doesn't provide
5. Reference not locatable in the repo
6. Content is redundant, verbose, or could be cut without losing meaning

Format:
### [N]. [title]
**Where**: [quote/section]  **Severity**: high | medium | low
**Question**: [what you'd ask the author]

Stop when you can say PASS.

---

DOCUMENT:

{content}
```

### lens_block (injected when lens applies)

```
Lens: agent-executable
This document will be executed by an AI agent. Also check:
7. Cross-file reference that agent might not follow
8. Positive instruction without explicit "Do NOT skip" prohibition
9. Example that could be mistaken for the only valid approach
10. "Repeat/same as" without self-contained steps
11. Quality requirement without measurable stop condition
12. Assumed reader identity or runtime context
13. Depth-dampening language that contradicts a quality expectation elsewhere in the doc
```
