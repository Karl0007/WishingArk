<workflow>
<objective>
Start a user-lab run with bounded scope, durable state, and enough structure that another agent can resume without reading the whole conversation.
</objective>

<required_reading>
- `references/modality-router.md`
- `references/evidence-policy.md`
- The modality reference needed for the selected surface.
</required_reading>

<process>
1. **Define the mission.** Choose one mode: targeted feature, exploratory simulation, release acceptance, or realtime/game. State the user promise and what evidence would prove or disprove it.

2. **Create a run directory.** Use `.user-lab/<YYYY-MM-DD>-<short-slug>/` unless the user gives another path. Create only the subdirectories the run needs:

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
  final-report.md
```

3. **Write the manifest.** Copy `templates/run-manifest.md` and fill mission, surface, environment, scope, mock policy, modality decision, scenario list, and resume pointer.

4. **Write machine state.** Copy `templates/state.json` and keep it small: run id, status, current scenario, scenario statuses, provisional verdict.

5. **Create scenarios.** Copy `templates/scenario.md` once per scenario. Keep each scenario independently executable. A targeted run may have one scenario; exploratory/release runs should use representative scenarios, not an unbounded checklist.

6. **Create evidence index.** Copy `templates/evidence-index.md`. Add artifact rows as evidence is captured. Do not inline screenshots, videos, traces, or long transcripts into the conversation.

7. **Stop planning and execute the next scenario.** Load `workflows/execute-scenario.md` and only the first pending scenario.
</process>

<context_control>
Do not keep the whole run in conversation context. Persist state to files. At any point, the active context should be: manifest summary, `state.json`, current scenario, relevant reference, and current evidence/judgment files.
</context_control>

<acceptance>
A started run has a run directory, manifest, machine state, scenario files, evidence index, and a clear next scenario. It does not claim verification yet.
</acceptance>
</workflow>
