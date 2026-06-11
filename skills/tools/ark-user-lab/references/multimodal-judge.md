# Multimodal Judge Protocol

Use this reference when screenshot or video judgment is required and the main model cannot inspect the artifact, or when an independent visual check would materially reduce uncertainty.

## Principle

A vision/video model is a bounded judge, not a narrator. Ask it specific acceptance questions. Answers must be YES, NO, or UNKNOWN.

Do not ask:

```text
What is in this screenshot?
Describe this video.
Does this look good?
```

Ask:

```text
Answer only YES, NO, or UNKNOWN.
In the screenshot, is the primary "Save" button visible, enabled, and unobscured?
```

## Question shape

Each question should include:

- artifact path or URL;
- time window for video when relevant;
- the exact visible condition;
- constraints that avoid subjective interpretation;
- allowed answers: YES, NO, UNKNOWN.

Template:

```text
You are judging a user-verification artifact.
Answer only YES, NO, or UNKNOWN.

Artifact: <path>
Time window, if video: <start-end>
Question: <closed visible condition>
UNKNOWN means the artifact does not provide enough visual evidence.
```

## Good screenshot questions

```text
Answer only YES, NO, or UNKNOWN.
In the screenshot, is there a visible success message confirming that the profile was saved?
```

```text
Answer only YES, NO, or UNKNOWN.
Is the error text adjacent to the invalid email field and does it state what the user must fix?
```

```text
Answer only YES, NO, or UNKNOWN.
At 390px-wide mobile viewport, is the primary checkout button fully visible without horizontal scrolling?
```

```text
Answer only YES, NO, or UNKNOWN.
Is keyboard focus visibly on the modal's first actionable control after the modal opens?
```

## Good video questions

```text
Answer only YES, NO, or UNKNOWN.
Between 00:02 and 00:05, does the character visibly move left within one second after the left input begins?
```

```text
Answer only YES, NO, or UNKNOWN.
Between 00:08 and 00:12, after the projectile touches the enemy, does the enemy visibly react, take damage, or disappear within one second?
```

```text
Answer only YES, NO, or UNKNOWN.
During the drag operation from 00:03 to 00:06, does the dragged item remain attached to the cursor/finger without jumping away?
```

```text
Answer only YES, NO, or UNKNOWN.
After the loading indicator appears, does a usable screen replace it before 00:10?
```

## Interpreting answers

- YES supports that specific condition only.
- NO is evidence for FAIL when the condition is required.
- UNKNOWN is not neutral success. Treat it as missing evidence and return LIMITED or ask a better question/capture a better artifact.

Do not let the auxiliary model choose the final verdict. The main agent owns the verdict by combining scenario intent, steps, artifacts, closed answers, and limitations.

## When frames are enough

Extract representative frames only when the claim is static or final-state based:

- layout;
- text visibility;
- button state;
- success/error message;
- final generated scene.

Use video-capable judgment when the claim involves:

- timing;
- animation;
- responsiveness;
- game control;
- collision;
- drag/drop;
- audio/video playback;
- loading duration;
- multiplayer/state synchronization.

If video judgment is required and unavailable, do not PASS. Return LIMITED if other evidence exists, otherwise BLOCKED.
