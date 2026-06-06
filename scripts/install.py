#!/usr/bin/env python3
"""Install or update WishingArk skills into a project-local .claude/skills directory."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _available_skills(skills_dir: Path) -> list[str]:
    if not skills_dir.exists():
        raise SystemExit(f"Missing skills directory: {skills_dir}")
    return sorted(
        child.name
        for child in skills_dir.iterdir()
        if child.is_dir() and (child / "SKILL.md").is_file()
    )


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def install(project: Path, selected: list[str] | None, dry_run: bool) -> int:
    root = _repo_root()
    source_dir = root / "skills"
    available = _available_skills(source_dir)
    names = selected or available

    unknown = sorted(set(names) - set(available))
    if unknown:
        raise SystemExit(
            "Unknown skill(s): " + ", ".join(unknown) + "\n"
            "Available: " + ", ".join(available)
        )

    project = project.resolve()
    target_dir = project / ".claude" / "skills"
    source_dir_resolved = source_dir.resolve()
    target_dir_resolved = target_dir.resolve()
    if _is_relative_to(target_dir_resolved, source_dir_resolved):
        raise SystemExit("Refusing to install into the source skills directory.")

    actions: list[str] = []
    for name in names:
        src = source_dir / name
        dest = target_dir / name
        actions.append(f"{src} -> {dest}")
        if dry_run:
            continue
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dest)

    for action in actions:
        print(action)
    print(f"Installed {len(names)} skill(s) into {target_dir}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Install/update WishingArk skills into a project-local .claude/skills directory."
    )
    parser.add_argument(
        "--project",
        type=Path,
        default=Path.cwd(),
        help="Project root to install into. Defaults to the current directory.",
    )
    parser.add_argument(
        "--skill",
        action="append",
        dest="skills",
        help="Install one skill by name. Repeat for multiple. Defaults to all skills.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned copies without modifying files.",
    )
    args = parser.parse_args(argv)
    return install(args.project, args.skills, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
