<workflow>
<objective>
Execute exactly one scenario through the closest real user surface, capture evidence, and update durable run state without loading unrelated scenarios.
</objective>

<required_reading>
- `run-manifest.md`
- `state.json`
- The current `scenarios/<id>.md`
- `references/evidence-policy.md`
- The modality-specific reference for this scenario.
</required_reading>

<process>
1. **Reconfirm the promise.** Read the scenario's Given/When/Then, forbidden shortcuts, and required evidence. If the scenario cannot prove a user-visible claim, mark it LIMITED and explain why.

2. **Prepare the surface.** Start or connect to the real app, command, emulator, desktop window, game build, or artifact viewer. Use controlled data only when disclosed. Do not mock behavior or mutate hidden state.

3. **Operate at user level.** Drive the product with normal user inputs: clicks, typing, keys, touch, commands, mouse/gamepad, waits, navigation, resize, or replayed input script. Automation is acceptable only when it sends user-level inputs.

4. **Capture artifacts.** Save evidence under the run directory with scenario-prefixed names, for example:

```text
evidence/screenshots/001-start.png
evidence/screenshots/001-final.png
evidence/videos/004-run-02.mp4
evidence/terminal/002-command.txt
evidence/artifacts/003-report.pdf
```

5. **Update the evidence index.** Add each artifact path, the claim it supports/refutes, capture context, and whether visual/video judgment is required.

6. **Judge immediately when the artifact is simple.** If the current model can directly inspect the artifact and the condition is obvious, record the observation in the scenario file. If visual/video capability is missing or the claim needs independent judgment, load `workflows/judge-evidence.md`.

7. **Write scenario result.** Update the scenario status: PASS, FAIL, LIMITED, or BLOCKED. Add concise observed result, evidence links, and any finding IDs created.

8. **Update state.** Update `state.json` and `run-manifest.md` with scenario status, current verdict, and next pending scenario.
</process>

<context_control>
Execute one scenario per context window. Do not load all artifacts or all scenario files. Large artifacts stay on disk; reports reference paths.
</context_control>

<acceptance>
The scenario file, evidence index, manifest, and state are updated. Any captured artifact has a path and a stated purpose. The scenario verdict is evidence-based or explicitly LIMITED/BLOCKED.
</acceptance>
</workflow>
