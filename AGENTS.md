# AGENTS.md

## Scope

These instructions apply to the entire WishingArk repository.

## Skill maintenance

When adding, renaming, moving, or deleting a skill, update every registry that exposes skills.

Required files to keep in sync:

- `skills/<group>/<skill-name>/SKILL.md` — the skill implementation. It must include YAML frontmatter with `name` and `description`.
- `ark-skills.json` — add the skill name to the correct `groups.<group>` array and to the top-level `skills` array.
- `.claude-plugin/plugin.json` — add the relative skill path to the `skills` array, for example `./skills/tools/ark-meta-prompt`.

Do not update only one registry. A skill directory without both registry entries is incomplete.

## Validation before handoff

After changing skill registries, run JSON validation for every changed JSON registry:

```text
python -m json.tool ark-skills.json
python -m json.tool .claude-plugin/plugin.json
```

Also run:

```text
git diff --check -- <changed files>
```

Before declaring the work done, verify `git status --short` and report whether the working tree is clean.

## Prompt skill guidance

For meta-prompt or dispatcher-prompt skills, prefer concise guidance that shapes agent judgment instead of long rule lists.

A good agent-facing prompt should include:

- bounded target;
- deliverable and optimization direction;
- constraints that prevent the obvious bad shortcut;
- task-specific taste guidance;
- one high-leverage judgment move;
- concrete acceptance evidence and blocker conditions.

Keep high-level quality words when they help taste, but anchor them with evidence.
