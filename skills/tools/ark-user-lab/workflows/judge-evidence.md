<workflow>
<objective>
Turn screenshots, videos, terminal captures, or artifact previews into bounded evidence by asking specific acceptance questions and preserving the answers.
</objective>

<required_reading>
- Current scenario file
- Relevant evidence index entries
- `references/multimodal-judge.md`
- `templates/judgment.md`
</required_reading>

<process>
1. **Extract acceptance conditions.** Convert the scenario's Then clauses and UX risks into visible yes/no conditions. Do not ask broad description questions.

2. **Choose judge type.** Use direct inspection when the current model can inspect the artifact. If it cannot, seek a capable vision/video model or tool. If no capable judge exists for a required condition, mark the condition UNKNOWN.

3. **Ask closed questions.** Each question must allow only YES, NO, or UNKNOWN and must name the artifact and time window when relevant.

4. **Save judgment.** Copy `templates/judgment.md` to `judgments/<scenario-id>-<artifact-slug>.md`. Store every question, answer, artifact path, time window, and acceptance condition.

5. **Interpret narrowly.** YES supports only the specific condition. NO refutes it. UNKNOWN means missing evidence, not success.

6. **Update scenario.** Link the judgment file from the scenario. If a required condition is NO, create or update a finding. If a required condition is UNKNOWN and no better artifact can be captured, mark the scenario LIMITED.
</process>

<question_rules>
Good question: "Between 00:02 and 00:05, does the character visibly move right within one second after right input begins?"

Bad question: "Describe what happens in the video."
</question_rules>

<acceptance>
Every visual/video-dependent claim has closed-question evidence or an explicit UNKNOWN limitation. The final verdict is not delegated to the auxiliary model.
</acceptance>
</workflow>
