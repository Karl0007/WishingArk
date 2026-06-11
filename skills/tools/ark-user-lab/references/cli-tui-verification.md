# CLI and TUI Verification

Use this reference for command-line tools, terminal workflows, curses/Ink/Blessed/Ratatui-style interfaces, prompts, installers, generators, and developer-facing tools.

## CLI verification

Record:

- exact command;
- working directory when relevant;
- environment variables or config files used, without secrets;
- input files;
- terminal output;
- exit behavior;
- produced artifacts.

Verify what a user experiences:

- help text explains the task;
- required arguments and errors are understandable;
- progress is visible for slow operations;
- failures tell the user how to recover;
- output files are created where the user expects;
- reruns are safe or warnings are clear;
- destructive actions require explicit confirmation when appropriate.

Do not verify a CLI only by importing its functions. Public function tests can supplement, but the user surface is the command.

## TUI verification

Record:

- terminal size;
- key sequence;
- starting state;
- focus location;
- screens visited;
- final state.

Check:

- keyboard navigation is discoverable and consistent;
- focus is visible;
- selection and active state are distinguishable;
- resize/redraw does not corrupt the screen;
- escape/back/cancel behavior is understandable;
- confirmation/error states do not disappear too quickly;
- long operations do not look frozen.

Use screenshots or terminal recording when layout, focus, redraw, or animation matters. Transcript alone is insufficient for visual TUI layout claims.

## Prompt and interactive command flows

For prompts, verify:

- defaults are visible;
- invalid input recovers without losing context;
- secrets are not echoed;
- cancellation works;
- final summary matches choices;
- generated files or changes are listed clearly.

## Evidence

Acceptable evidence:

- terminal transcript;
- terminal screenshot;
- terminal recording;
- produced artifact preview;
- exact key/input sequence.

For PASS, the transcript must show the user-level command or key sequence, not only internal function calls.
