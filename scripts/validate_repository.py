#!/usr/bin/env python3
"""Validate the repository's AI asset layout with no third-party dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening YAML frontmatter delimiter")

    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration as exc:
        raise ValueError("missing closing YAML frontmatter delimiter") from exc

    metadata: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip("'\"")
    return metadata


def validate_skills(errors: list[str]) -> None:
    for skill_dir in sorted((ROOT / "skills").iterdir()):
        if not skill_dir.is_dir():
            continue
        if not KEBAB_CASE.fullmatch(skill_dir.name):
            errors.append(f"{skill_dir.relative_to(ROOT)}: directory name must be kebab-case")
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_dir.relative_to(ROOT)}: missing SKILL.md")
            continue
        try:
            metadata = parse_frontmatter(skill_file)
        except ValueError as exc:
            errors.append(f"{skill_file.relative_to(ROOT)}: {exc}")
            continue
        for field in ("name", "description"):
            if not metadata.get(field):
                errors.append(f"{skill_file.relative_to(ROOT)}: missing {field!r}")
        if metadata.get("name") != skill_dir.name:
            errors.append(
                f"{skill_file.relative_to(ROOT)}: name must match directory {skill_dir.name!r}"
            )


def validate_plugins(errors: list[str]) -> None:
    for plugin_dir in sorted((ROOT / "plugins").iterdir()):
        if not plugin_dir.is_dir():
            continue
        manifest = plugin_dir / ".codex-plugin" / "plugin.json"
        if not manifest.is_file():
            errors.append(f"{plugin_dir.relative_to(ROOT)}: missing .codex-plugin/plugin.json")
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{manifest.relative_to(ROOT)}: invalid JSON ({exc})")
            continue
        if data.get("name") != plugin_dir.name:
            errors.append(f"{manifest.relative_to(ROOT)}: name must match directory")


def main() -> int:
    errors: list[str] = []
    validate_skills(errors)
    validate_plugins(errors)
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
