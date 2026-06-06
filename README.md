# WishingArk

Version-controlled distribution for the Ark skill set.

## Contents

Ark skills live under `skills/`:

- `ark-autoexec`
- `ark-deep-think`
- `ark-doc-review`
- `ark-exec`
- `ark-explore`
- `ark-feedback`
- `ark-init`
- `ark-learn`
- `ark-merge`
- `ark-ontology`
- `ark-plan`
- `ark-propose`
- `ark-sprint`
- `ark-test-baseline`
- `ark-verify`

`ark-skills.json` records the packaged skill list and repository version.

## Install or update skills in a project

From this repository root:

```powershell
python scripts/install.py --project F:\path\to\project
```

This installs every skill into:

```text
F:\path\to\project\.claude\skills\
```

Install one skill only:

```powershell
python scripts/install.py --project F:\path\to\project --skill ark-plan
```

Preview without writing:

```powershell
python scripts/install.py --project F:\path\to\project --dry-run
```

## Update flow

```powershell
git -C F:\Wishing\WishingArk pull
python F:\Wishing\WishingArk\scripts\install.py --project F:\path\to\project
```

The installer replaces project-local copies of installed skills with the version from this repository. Keep project-specific skill changes in the source repository, not in each installed copy.

## Release rule

Bump `VERSION` and `ark-skills.json.version` when changing skill behavior.
