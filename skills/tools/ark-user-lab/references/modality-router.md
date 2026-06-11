# Modality Router

Choose the surface a real user would touch. The goal is not maximum automation; it is the shortest path to evidence that represents the user's lived experience.

## Mission modes

### Targeted feature verification

Use when the request names a specific feature, bug fix, or user promise.

- Identify the exact actor, entry point, action, and visible success condition.
- Run the primary path and one contrast/recovery path if the claim can otherwise be hardcoded.
- Do not broaden into unrelated product areas.

### Exploratory user simulation

Use when the user asks to try the product from a user perspective.

- Pick 2-5 representative tasks from the product's obvious entry points.
- Include first-time comprehension and one mistake/recovery path.
- Report coverage honestly; do not imply the whole product was exhausted.

### Release acceptance pass

Use before shipping a user-facing change.

- Use multiple personas that expose different failure modes: first-time, repeat/power, constrained input/device, low-permission, bad-data/error path.
- Cover happy path, empty/loading/error states, navigation/back/refresh, and a contrast case.
- Prefer fewer high-signal scenarios over a shallow matrix.

### Realtime/game verification

Use when correctness depends on timing, motion, responsiveness, collision, animation, audio/video, or game feel.

- Use scripted user-level input.
- Record video.
- Ask closed questions about time windows and events.
- Iterate the script when the recording does not exercise the scenario.

## Surface decision table

| Surface | Primary evidence | Notes |
|---|---|---|
| Web app/admin/docs | Browser interaction, screenshots, accessibility snapshot when relevant | Use real routes and user-level clicks/typing. |
| Browser extension | Installed extension UI plus affected page interaction | Capture both extension surface and page result. |
| CLI | Terminal transcript, produced files, exit behavior | Verify messages and artifacts a user sees. |
| TUI | Terminal recording/screenshot and key sequence | Verify focus, navigation, redraws, and recoverability. |
| Mobile/responsive | Emulator/device or mobile viewport screenshots/video | Use touch/viewport when the claim depends on it. |
| Desktop app | Window interaction screenshots/video | Prefer actual app window over config files. |
| Game/realtime | Input script, gameplay recording, video judgment | Never teleport or mutate game state to pass. |
| Generated report/file/image | Opened artifact preview, not just file existence | Inspect the output in the user-facing viewer. |
| API-only service | Public contract request/response | Do not claim UX verification unless there is a user surface. |
| Library | Consumer example run/output | Verify how a caller experiences the public interface. |

## Secondary modalities

Add a second modality when the primary cannot catch the risk:

- Browser flow + screenshots for visual/layout changes.
- Browser flow + accessibility tree for forms, focus, navigation, or screen-reader-relevant semantics.
- CLI transcript + artifact preview for generators.
- Mobile viewport + video for drag, scroll, gestures, or motion.
- Game recording + frame snapshots when both timing and final state matter.

## Blocker conditions

Return BLOCKED when the closest real surface cannot be reached and no lower-fidelity surface can support the claim:

- app/build cannot run;
- credentials, license, device, emulator, display, audio, or input hardware is unavailable;
- visual/video judgment is required and no capable model/tool can inspect the artifact;
- the only possible path requires mocked behavior or implementation shortcuts.
