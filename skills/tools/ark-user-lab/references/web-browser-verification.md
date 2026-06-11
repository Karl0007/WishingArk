# Web and Browser Verification

Use this reference for websites, web apps, admin panels, docs sites, browser extensions, and web-based product surfaces.

## Setup

Record:

- URL/route;
- browser;
- viewport/device scale;
- account/role;
- data state;
- build/environment;
- whether any seed/demo data was used.

Prefer the real app route. Component previews can support investigation, but cannot prove integrated product behavior unless the preview is the product surface.

## Interaction rules

Operate through user-level actions:

- click;
- type;
- tab/shift-tab;
- keyboard shortcuts users know;
- scroll;
- resize;
- drag/drop;
- browser back/forward/refresh;
- route navigation through visible links.

Avoid:

- setting DOM state directly;
- directly calling internal APIs;
- editing localStorage/sessionStorage/cookies except for documented user setup;
- forcing React/Vue/Svelte component state;
- bypassing auth unless the scenario is specifically unauthenticated.

## Required checks for common flows

For forms:

- initial affordance is clear;
- required fields and constraints are discoverable;
- invalid input produces visible, local, recoverable errors;
- submission has loading/disabled feedback;
- final success/failure state is visible and trustworthy;
- keyboard-only path can reach and submit controls when relevant.

For navigation:

- current location is understandable;
- back/forward/refresh do not lose critical state unexpectedly;
- empty or unauthorized states explain what to do;
- links/buttons have distinct affordances.

For responsive/mobile claims:

- verify the claimed viewport, not only desktop;
- check no horizontal scroll, clipped controls, covered sticky elements, or unreachable primary action;
- use touch-like interaction when gesture behavior matters.

For visual changes:

- screenshot before/after when possible;
- inspect layout, hierarchy, text clipping, contrast-affecting backgrounds, overlap, and scroll position;
- report only issues tied to task completion, comprehension, trust, or obvious quality regression.

## Accessibility-adjacent user checks

This skill is not a full WCAG audit. Use the accessibility skill for that.

Still check user-level accessibility when it affects the scenario:

- can the flow be completed with keyboard;
- is focus visible and not trapped incorrectly;
- does modal focus start in a sensible place and return after close;
- do controls expose meaningful labels in the accessibility tree;
- does dynamic success/error state become visible and understandable.

## Evidence

Capture:

- start state screenshot;
- key transition screenshot for loading/error/empty/modal states;
- final state screenshot;
- accessibility snapshot if semantic/focus claims matter;
- video for drag/drop, animation, long loading, media playback, or realtime behavior.

Console/network logs may explain failures but cannot replace visual evidence.
