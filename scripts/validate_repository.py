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


def parse_agent_metadata(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    for field in ("name", "description", "sandbox_mode"):
        match = re.search(rf'^\s*{field}\s*=\s*"([^"\n]*)"\s*$', text, re.MULTILINE)
        if match:
            metadata[field] = match.group(1)

    instructions = re.search(
        r'^\s*developer_instructions\s*=\s*"""(.*?)"""\s*$',
        text,
        re.MULTILINE | re.DOTALL,
    )
    if instructions:
        metadata["developer_instructions"] = instructions.group(1).strip()
    return metadata


def validate_agents(errors: list[str]) -> None:
    agents_dir = ROOT / "agents"
    if not agents_dir.is_dir():
        return

    seen_names: set[str] = set()
    for agent_file in sorted(agents_dir.glob("*.toml")):
        data = parse_agent_metadata(agent_file)

        for field in ("name", "description", "developer_instructions"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{agent_file.relative_to(ROOT)}: missing {field!r}")

        name = data.get("name")
        if not isinstance(name, str) or not name:
            continue
        expected_name = agent_file.stem.replace("-", "_")
        if name != expected_name:
            errors.append(
                f"{agent_file.relative_to(ROOT)}: name must match {expected_name!r}"
            )
        if name in seen_names:
            errors.append(f"{agent_file.relative_to(ROOT)}: duplicate agent name {name!r}")
        seen_names.add(name)

        if "review" in name and data.get("sandbox_mode") != "read-only":
            errors.append(
                f"{agent_file.relative_to(ROOT)}: review agents must use sandbox_mode = 'read-only'"
            )


def main() -> int:
    errors: list[str] = []
    validate_skills(errors)
    validate_plugins(errors)
    validate_agents(errors)
    if errors:
        print("Repository validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
