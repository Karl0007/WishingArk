<workflow>
<objective>
Resume an interrupted user-lab run from durable files while loading the least context needed to continue safely.
</objective>

<required_reading>
- `.user-lab/<run-id>/run-manifest.md`
- `.user-lab/<run-id>/state.json`
- Current or next pending scenario file
</required_reading>

<process>
1. **Locate the run.** Use the user-provided run path, or the most relevant `.user-lab/<run-id>/` path from the current task. Do not invent prior results.

2. **Read only state first.** Load manifest and `state.json`. Identify status, current scenario, pending scenarios, and provisional verdict.

3. **Check staleness.** If product code, environment, or scenario files changed after evidence capture, mark affected scenario evidence stale and rerun those scenarios.

4. **Continue the next unit.** Load only the current or next pending scenario and the reference required for its modality. Use `workflows/execute-scenario.md`.

5. **Finalize when complete.** If no scenarios remain pending/running, use `workflows/finalize-report.md`.
</process>

<context_control>
Never reload all screenshots, videos, transcripts, or all scenario files during resume. Use paths and summaries. Open a raw artifact only when its specific judgment is under review.
</context_control>

<acceptance>
The run resumes from persisted state, not memory. The next action is either one scenario execution or final report generation.
</acceptance>
</workflow>
