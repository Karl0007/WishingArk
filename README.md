# WishingArk

Version-controlled distribution for the Ark skill set.

## Quickstart

Install with the standard skills installer:

```bash
npx skills@latest add Karl0007/WishingArk
```

Pick the Ark skills you want to install. For a full Ark workflow, install the whole set and run `/ark:init` in the target project.

## Contents

Ark skills are grouped by role under `skills/`.

### Workflow skills

These implement the Ark change lifecycle:

- `ark-autoexec`
- `ark-exec`
- `ark-explore`
- `ark-feedback`
- `ark-init`
- `ark-learn`
- `ark-merge`
- `ark-ontology`
- `ark-plan`
- `ark-propose`
- `ark-test-baseline`
- `ark-verify`

### Tool skills

These are general-purpose helpers, not the core workflow pipeline:

- `ark-architecture-review`
- `ark-deep-think`
- `ark-doc-review`
- `ark-meta-prompt`
- `ark-sprint`
- `ark-user-lab`

The standard installer reads `.claude-plugin/plugin.json`.

`ark-skills.json` records the packaged skill groups, flat skill list, and repository version for humans and simple automation.

## Local development

List packaged skills:

```bash
scripts/list-skills.sh
```

Link all skills into your local Claude skills directory while developing this repository:

```bash
scripts/link-skills.sh
```

The link script writes symlinks under:

```text
~/.claude/skills/
```

For normal users, prefer `npx skills@latest add Karl0007/WishingArk` instead of linking.

## Update flow

Update the source repository, then reinstall through the standard installer:

```bash
git -C /path/to/WishingArk pull
npx skills@latest add Karl0007/WishingArk
```

## Release rule

Bump `VERSION`, `ark-skills.json.version`, and review `.claude-plugin/plugin.json` whenever changing the packaged skill set or skill behavior.
