# Game and Realtime Verification

Use this reference when the software behaves in real time: games, simulations, animation-heavy experiences, media playback, realtime collaboration, or interaction where timing and control responsiveness matter.

## Core loop

Use the record-review-iterate loop:

1. Define the player/user scenario.
2. Write or configure a user-level input script.
3. Run the scenario and record video.
4. Ask closed video questions tied to the scenario.
5. Revise the input script only if it failed to exercise the scenario.
6. Record again.
7. Decide PASS/FAIL/LIMITED/BLOCKED from video evidence.

## Scenario shape

State:

- goal;
- starting screen/level/state;
- allowed inputs;
- expected visible outcome;
- timing tolerance if relevant;
- what would count as failure.

Example:

```text
Goal: Verify the player can jump over the first obstacle and continue moving.
Inputs: hold right, press jump at the obstacle, continue right.
Expected: player clears obstacle, lands, remains controllable, and camera continues following.
Failure: player clips into obstacle, input is ignored, camera loses player, or control does not resume within 1 second.
```

## Allowed automation

Allowed:

- keyboard/mouse/gamepad input;
- touch input;
- wait/timing control;
- camera/viewport movement through normal controls;
- restarting level through user-visible menus;
- selecting user-accessible test map or demo mode when disclosed.

Forbidden for PASS:

- teleporting the player;
- setting health, score, inventory, flags, or position directly;
- disabling AI/collision/physics;
- skipping animation through internals;
- invoking victory/failure state directly;
- debug API shortcuts unless the debug tool itself is under test.

## Video evidence

Record video when verifying:

- control responsiveness;
- movement;
- collision;
- combat/projectile behavior;
- animation transitions;
- camera follow;
- hit reactions;
- timing windows;
- loading duration;
- realtime sync;
- audio/video playback.

Screenshots alone are acceptable only for static menus, final state, layout, or visual asset placement.

## Closed video questions

Ask questions with time windows:

```text
Answer only YES, NO, or UNKNOWN.
Between 00:02 and 00:05, does the character visibly move right within one second after right input begins?
```

```text
Answer only YES, NO, or UNKNOWN.
Between 00:06 and 00:09, does the character clear the obstacle without clipping into it?
```

```text
Answer only YES, NO, or UNKNOWN.
After landing, does the character visibly respond to movement input again within one second?
```

UNKNOWN means the recording did not prove the condition. Improve the recording or return LIMITED/BLOCKED.

## Iteration rules

Iterate the script to improve scenario coverage, not to cheat the outcome.

Good iteration:

- adjust wait time because level loads slower;
- move aim target because the first script missed the enemy;
- restart from menu to get a clean run;
- record at higher resolution or with clearer camera.

Bad iteration:

- alter game state to place player past obstacle;
- disable enemy attacks;
- reduce gravity;
- force success state;
- hide visual bug from camera.

## Report additions

Include:

- input script or exact input sequence;
- recording path;
- time-windowed observations;
- closed questions and answers;
- script iterations and why they were made;
- final verdict tied to video evidence.
