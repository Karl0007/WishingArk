---
name: ark-deep-think
description: Multi-round deep thinking via a sub-Agent. Sends a question with context to a thinking agent, pushes it deeper twice, then returns a structured summary. Use when user says "think deeply", "deep think", "think harder", "analyze this thoroughly", or invokes /ark:deep-think.
---

# Deep Think

Send a question + context to a sub-Agent. Push it deeper 2 more rounds (3 total responses), then return a structured summary.

## Process

1. Collect the user's question + relevant context (files, code, prior decisions)
2. Spawn sub-Agent with the initial prompt below
3. After each of the first 2 responses, send: "Think deeper."
4. After the 3rd response, send the summary prompt
5. Return the structured summary to user

## Sub-Agent prompt (initial)

```
Think carefully and deeply about the following question. Don't settle for the first answer that comes to mind — push past the obvious.

CONTEXT:
{context}

QUESTION:
{question}
```

## Push prompt (same each round)

```
Think deeper.
```

## Summary prompt

```
Summarize your thinking across all 3 rounds. Each round may have contributed something different — don't collapse them into just the final conclusion.

1. **Per-round value** — what did each round uniquely contribute?
2. **Synthesis** — one sentence integrating the full trajectory
3. **Remaining uncertainties** — what you're still not sure about
```

## Output to user

Return the structured summary. If user wants detail, show all 3 responses + summary verbatim.
