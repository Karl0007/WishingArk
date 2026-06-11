# Evidence Policy

The verdict must follow from observed user-visible evidence. Tests, code reading, logs, and internal API responses can support investigation, but they cannot replace the user artifact for a user-facing claim.

## Evidence minimums

### UI surfaces

PASS requires at least one artifact before/during interaction and one artifact of the final state.

Acceptable artifacts:

- screenshot;
- video;
- accessibility snapshot for semantic/focus claims;
- browser trace when paired with visual evidence;
- desktop/mobile/game capture.

### CLI and TUI

PASS requires terminal evidence:

- exact command or key sequence;
- terminal transcript or terminal screenshot/recording;
- produced files or output preview when the command generates artifacts;
- observed exit behavior if success/failure status matters.

### Generated artifacts

PASS requires opening or previewing the artifact in a user-facing way:

- rendered PDF/document/image/report;
- generated page served in browser;
- file contents only when the user-facing artifact is textual.

File existence alone is not enough.

### API-only and library surfaces

Use public consumer evidence:

- public endpoint request/response for API services;
- example consumer code and observed output for libraries.

Do not label this UX verification unless a real user-facing interface is exercised.

## Mock policy

Forbidden for PASS:

- mocked services standing in for product behavior;
- fake UI states not reachable by users;
- Storybook/component-only evidence for an integrated product claim;
- direct localStorage/database edits;
- direct internal API calls used to bypass the user flow;
- debug commands that create a success state the user could not create.

Allowed when disclosed:

- test accounts;
- seeded data;
- local dev server;
- staging environment;
- user-accessible demo mode;
- synthetic but realistic files supplied as user input;
- game test map or debug build only when it still runs the real interaction logic and the limitation is reported.

Rule of thumb: controlled data is allowed; mocked behavior is not.

## Verdict rules

### PASS

Use only when all are true:

- the closest available real user surface was exercised;
- required visual/terminal/artifact evidence was captured;
- no mocked behavior was used for the claim;
- the named user promise is visible in the final state;
- relevant comprehension/recovery/trust issues do not materially undermine the task.

### FAIL

Use when evidence shows a user-visible break:

- user cannot complete the task;
- success/failure state is misleading or invisible;
- important action is blocked, hidden, disabled, or obscured;
- error handling does not allow recovery;
- visual/layout/responsiveness break materially affects task completion or trust;
- motion/timing/control behavior fails the scenario.

### LIMITED

Use when some evidence exists but does not support the full claim:

- only desktop was tested for a mobile claim;
- screenshots were captured but the claim depends on motion/timing;
- only a lower-fidelity preview was available;
- environment differs materially from target;
- role/permissions/data coverage is incomplete;
- multimodal answers include UNKNOWN for a required condition.

### BLOCKED

Use when verification cannot produce meaningful user evidence:

- app cannot run;
- no credentials or required device;
- no way to capture necessary artifact;
- no capable model/tool for required visual/video judgment;
- only mock or implementation shortcut path is available.

## Severity guidance

Report findings only when they affect user outcomes:

- **Critical** — prevents task completion or risks destructive user action.
- **High** — likely blocks a common user path, corrupts trust, or hides important state.
- **Medium** — causes confusion, recovery difficulty, or platform mismatch but has a workaround.
- **Low** — visible quality issue that does not block the task but harms confidence.

Avoid subjective styling comments unless tied to readability, hierarchy, affordance, accessibility, or trust.
