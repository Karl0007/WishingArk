# Mobile, Desktop, and Generated Artifact Verification

Use this reference for mobile apps, responsive experiences, desktop apps, generated documents, reports, images, exports, and other non-browser artifacts.

## Mobile

Prefer real device or emulator when the claim depends on mobile behavior. Browser mobile viewport is acceptable for responsive web layout when native device APIs are not involved.

Record:

- device/emulator or viewport;
- OS/browser/app version when relevant;
- orientation;
- input mode;
- permissions state;
- network condition if relevant.

Check:

- touch targets are reachable;
- primary action is not hidden by keyboard, safe area, sticky bars, or browser chrome;
- orientation changes preserve state when expected;
- permission prompts are understandable;
- gestures work without accidental destructive action;
- loading/error/offline states are recoverable.

Use video for gestures, scrolling, drag/drop, animation, camera/location permission flows, and any claim involving timing.

## Desktop apps

Record:

- app build/version;
- OS/window size;
- input mode;
- account/data state;
- opened windows/dialogs.

Check:

- first usable screen appears;
- menus/buttons/dialogs are discoverable;
- window resize does not break layout;
- file open/save flows use expected platform conventions;
- errors and permissions are visible;
- background tasks show progress and completion.

Capture screenshots or video of the actual app window. Config files and logs can explain but cannot replace the window artifact.

## Generated artifacts

For generated documents, reports, exports, images, or code artifacts, verify the artifact as the user consumes it.

Examples:

- open generated HTML in browser;
- render PDF/document and inspect pages;
- preview image/export;
- open report dashboard;
- run generated project if the artifact is executable.

Check:

- the artifact opens without special internal knowledge;
- important content is present and readable;
- formatting/layout is not broken;
- links/assets resolve;
- file names and locations match user expectation;
- errors are reported if generation fails.

File existence alone is not evidence of user success.

## Evidence

Capture:

- app/device/artifact screenshot;
- video for motion/timing/gesture;
- generated artifact path plus opened preview;
- exact input files and settings used.
