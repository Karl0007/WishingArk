---
name: ark-user-lab
description: Verify software like a real user through live interaction, screenshots, video, terminal captures, and closed-question multimodal judgment. Use when asked to verify like a user, run human QA, check UX, test a flow, validate a game or interactive surface, review screenshots/video, or prove user-facing behavior beyond code tests.
---

<objective>
Verify lived user experience, not implementation. Operate the real user surface, persist evidence to a run directory, and judge whether the promised experience actually works.
</objective>

<core_philosophy>
```text
User boundary beats implementation boundary.
Evidence beats confidence.
Closed questions beat vague visual descriptions.
Durable state beats conversation memory.
Automation drives inputs; it never replaces observation.
```

Do not turn this into a bigger test suite. The skill exists to answer the question a human user would ask: "Can I actually complete this task, understand what happened, and trust the result?"
</core_philosophy>

<non_negotiables>
- A PASS requires user-visible evidence: screenshot, video, terminal capture, generated artifact preview, public response, or another artifact a real user could inspect.
- Do not use mocked behavior to prove a real product path. Controlled accounts, seed data, local dev, staging, and user-accessible demo modes are allowed only when disclosed.
- Use code only to operate the product through user-level inputs. Do not verify by reading source, asserting DOM state, calling internal APIs, mutating storage/databases, or forcing component/game state.
- If visual or video judgment is required and the current model cannot perform it, seek a capable model/tool. Ask only closed YES/NO/UNKNOWN questions tied to acceptance conditions.
- UNKNOWN is missing evidence, not success.
- Persist long runs to files. Do not keep scenario state, evidence, or visual judgments only in conversation context.
</non_negotiables>

<routing>
Start with the lightest mode that fits the user's risk:

- **Quick proof** — one narrow promise, one real path, minimal run files. Use when the user asks to verify a specific feature or fix.
- **Targeted feature lab** — one feature with happy path plus contrast/recovery paths. Use when a feature is user-facing and failure modes are plausible.
- **Exploratory simulation** — representative user tasks across the product. Use when the user asks to try the product from a user's perspective. Do not claim exhaustive coverage.
- **Release acceptance** — broader pre-ship pass with multiple personas, devices, roles, and recovery cases.
- **Realtime/game loop** — timing, movement, animation, collision, game feel, audio/video, realtime collaboration, or media playback. Requires recording and video judgment when motion matters.

If the run may exceed one short scenario, use `workflows/start-run.md` before interacting with the product.

If continuing a previous run, use `workflows/resume-run.md` first.
</routing>

<workflow_index>
- `workflows/start-run.md` — create `.user-lab/<run-id>/`, manifest, machine state, scenarios, and evidence index.
- `workflows/execute-scenario.md` — run exactly one scenario through the real user surface and update state.
- `workflows/judge-evidence.md` — ask closed multimodal questions and persist answers.
- `workflows/finalize-report.md` — produce the final report from persisted summaries and evidence paths.
- `workflows/resume-run.md` — recover an interrupted run without reloading every artifact.
</workflow_index>

<reference_index>
- `references/modality-router.md` — choose the user surface and evidence type.
- `references/evidence-policy.md` — verdict rules, mock policy, and severity.
- `references/multimodal-judge.md` — screenshot/video judgment protocol.
- `references/web-browser-verification.md` — browser, responsive, keyboard, and accessibility-adjacent checks.
- `references/cli-tui-verification.md` — CLI and terminal UI checks.
- `references/mobile-desktop-generated.md` — mobile, desktop, and generated artifacts.
- `references/game-realtime-verification.md` — scripted input, recording, closed video questions, and iteration.
</reference_index>

<runtime_structure>
For any non-trivial run, create this structure under `.user-lab/<YYYY-MM-DD>-<short-slug>/`:

```text
.user-lab/<run-id>/
  run-manifest.md
  state.json
  scenarios/
  evidence/
    screenshots/
    videos/
    terminal/
    artifacts/
  judgments/
  findings/
  evidence-index.md
  final-report.md
```

Use templates from `templates/` for every persisted document. The run directory is the source of truth; the conversation is only the control surface.
</runtime_structure>

<judgment_moves>
Pick one primary move before running scenarios:

- **User-promise test** — What exact visible outcome would prove the user's promise true?
- **Hardcode test** — If the implementation only satisfied the obvious happy path, what contrast case would expose it?
- **Recovery test** — When the user makes a mistake or hits an error, can they understand and recover?
- **Boundary test** — Which role, device, input mode, viewport, timing window, or artifact viewer is closest to where this could fail?
- **Evidence test** — What artifact would convince a skeptical human who did not watch the run?
</judgment_moves>

<verdicts>
**PASS** — The closest real user path was exercised, required user-visible evidence was captured, no mocked behavior proved the claim, and the named promise holds.

**FAIL** — Evidence shows a user-visible break: blocked completion, misleading state, unrecoverable error, material layout/platform issue, broken timing/control, or loss of trust.

**LIMITED** — Real evidence exists but does not cover the full claim: wrong device, partial environment, missing video ability, restricted role, incomplete data, lower-fidelity surface, or UNKNOWN required condition.

**BLOCKED** — Meaningful verification cannot proceed: app cannot run, required credentials/device/model/tool is unavailable, artifacts cannot be captured, or the only path requires mocks or implementation shortcuts.
</verdicts>

<context_control>
Long runs must be resumable:

- Load only the manifest, state, current scenario, relevant reference, and current evidence/judgment files.
- Execute one scenario per context window.
- Store screenshots, videos, traces, transcripts, and generated artifacts as files; reference paths instead of inlining content.
- Save every multimodal question and answer in `judgments/`.
- Update `state.json` and `run-manifest.md` after each scenario.
</context_control>

<output_contract>
Final output must include:

```text
Verdict: PASS | FAIL | LIMITED | BLOCKED
Run directory: .user-lab/<run-id>/ or "quick proof only"
User promise: ...
Surface verified: ...
Scenarios: status summary
Evidence: artifact paths and what each proves
Closed multimodal judgments: questions/answers or "not used"
Findings: severity, user impact, reproduce, expected, actual, evidence
Limits/blockers: ...
```
</output_contract>

<anti_patterns>
- Long checklist with no ownership of the user promise.
- "Looks fine" without artifact-backed evidence.
- Treating lint, unit tests, DOM assertions, source inspection, or internal API responses as human verification.
- Broad visual prompts such as "describe this screenshot" or "does this look good".
- Game/realtime scripts that cheat by teleporting, changing stats, disabling systems, or invoking success states.
- Exploratory runs that wander without mission, scope, or durable notes.
</anti_patterns>

<success_criteria>
A successful use of this skill leaves a skeptical human or future agent able to repeat the scenario, inspect the same artifacts, understand the user impact, and see why the verdict follows from evidence rather than implementation confidence.
</success_criteria>
