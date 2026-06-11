<workflow>
<objective>
Produce the final user-lab report from persisted run artifacts without reloading every raw artifact into context.
</objective>

<required_reading>
- `run-manifest.md`
- `state.json`
- Scenario status summaries
- `evidence-index.md`
- Relevant `judgments/*.md`
- `findings/*.md`
- `templates/final-report.md`
</required_reading>

<process>
1. **Check completeness.** Ensure every in-scope scenario is PASS, FAIL, LIMITED, or BLOCKED. Pending/running scenarios prevent final PASS.

2. **Derive verdict.** Use evidence policy:
   - FAIL if any in-scope required user promise fails materially.
   - BLOCKED if verification could not produce meaningful user evidence.
   - LIMITED if evidence exists but does not cover the full claim.
   - PASS only if all required claims passed with user-visible evidence and no mocked behavior.

3. **Summarize by scenario.** Include each scenario's status, steps summary, evidence links, and finding IDs. Do not paste full transcripts or visual descriptions unless they are short and decisive.

4. **Summarize findings.** Include severity, user impact, reproduction, expected, actual, and evidence path. Keep subjective commentary out unless tied to completion, comprehension, recovery, trust, accessibility-relevant usability, or platform fit.

5. **State limits.** Call out untested roles/devices/surfaces, UNKNOWN multimodal answers, partial environments, or controlled data.

6. **Write `final-report.md`.** Use `templates/final-report.md`. Update manifest and state to final status.
</process>

<context_control>
The final report is an index and judgment summary, not a dump of the whole run. Reference artifact paths instead of inlining large evidence.
</context_control>

<acceptance>
The report lets another human or agent repeat the scenarios, inspect the artifacts, understand user impact, and see why the verdict follows from evidence.
</acceptance>
</workflow>
