#!/usr/bin/env python3
"""Generate profile-aware AI project rules using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
TEMPLATES = SKILL_DIR / "templates"
STACKS = ("generic", "react", "vue", "wechat-miniprogram", "node", "python")
PROJECT_TYPES = ("generic", "admin", "mobile", "consumer-web", "api-service", "library")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize .ai/ with rules composed for the repository stack and project type."
    )
    parser.add_argument("target", nargs="?", default=".", help="target repository")
    parser.add_argument("--stack", choices=("auto", *STACKS), default="auto")
    parser.add_argument(
        "--project-type", choices=("auto", *PROJECT_TYPES), default="auto"
    )
    parser.add_argument(
        "--force", action="store_true", help="replace generated AGENTS and constitution files"
    )
    parser.add_argument(
        "--list-profiles", action="store_true", help="list supported profiles and exit"
    )
    return parser.parse_args()


def load_package_json(target: Path) -> dict[str, object]:
    path = target / "package.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise SystemExit(f"error: cannot read {path}: {exc}") from exc
    return data if isinstance(data, dict) else {}


def package_dependencies(package: dict[str, object]) -> set[str]:
    result: set[str] = set()
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        values = package.get(key, {})
        if isinstance(values, dict):
            result.update(str(name).lower() for name in values)
    return result


def python_dependencies(target: Path) -> set[str]:
    """Extract dependency names conservatively from common Python metadata files."""
    result: set[str] = set()
    paths = [target / "pyproject.toml", *sorted(target.glob("requirements*.txt"))]
    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for name in re.findall(r"(?im)^\s*[\"']?([a-z0-9][a-z0-9._-]*)\s*(?:[<>=!~\[\"']|$)", text):
            result.add(name.lower().replace("_", "-"))
    return result


def has_wechat_app(target: Path) -> bool:
    config_path = target / "project.config.json"
    if not config_path.is_file():
        return False
    roots = [target]
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        config = {}
    if isinstance(config, dict) and isinstance(config.get("miniprogramRoot"), str):
        candidate = (target / str(config["miniprogramRoot"])).resolve()
        if candidate == target or target in candidate.parents:
            roots.insert(0, candidate)
    return any((root / "app.json").is_file() for root in roots)


def detect_stack(target: Path, dependencies: set[str]) -> tuple[str, list[str]]:
    matches: list[tuple[str, str]] = []
    if has_wechat_app(target):
        matches.append(("wechat-miniprogram", "project.config.json + app.json"))
    if "react" in dependencies:
        matches.append(("react", "react dependency"))
    if "vue" in dependencies:
        matches.append(("vue", "vue dependency"))
    if (target / "pyproject.toml").is_file() or any(target.glob("requirements*.txt")):
        matches.append(("python", "Python project metadata"))
    if (target / "package.json").is_file() and not matches:
        matches.append(("node", "package.json without React/Vue"))
    unique = {stack for stack, _ in matches}
    if len(unique) > 1:
        details = ", ".join(f"{stack} ({reason})" for stack, reason in matches)
        raise SystemExit(
            f"error: multiple stack signals found: {details}; rerun with --stack <profile>"
        )
    if matches:
        return matches[0][0], [matches[0][1]]
    return "generic", ["no supported stack marker found"]


def detect_project_type(
    target: Path, package: dict[str, object], dependencies: set[str], stack: str
) -> tuple[str, list[str]]:
    name = str(package.get("name", target.name)).lower()
    path_hint = f"{target.name} {name}"
    candidates: list[tuple[str, str]] = []

    if re.search(r"(^|[-_ ])(admin|dashboard|backoffice)([-_ ]|$)", path_hint):
        candidates.append(("admin", "repository/package name indicates an admin console"))

    mobile_dependencies = {
        "react-native",
        "expo",
        "@dcloudio/uni-app",
        "@tarojs/taro",
        "vant",
        "@nutui/nutui",
    }
    matched_mobile = sorted(dependencies & mobile_dependencies)
    if stack == "wechat-miniprogram":
        candidates.append(("mobile", "wechat-miniprogram stack"))
    elif matched_mobile:
        candidates.append(
            ("mobile", f"mobile dependency: {', '.join(matched_mobile)}")
        )

    api_dependencies = {
        "express",
        "@nestjs/core",
        "fastapi",
        "django",
        "flask",
        "koa",
        "hono",
    }
    matched_api = sorted(dependencies & api_dependencies)
    if matched_api:
        candidates.append(("api-service", f"API dependency: {', '.join(matched_api)}"))

    exports = package.get("exports") or package.get("main") or package.get("module")
    if exports and package.get("private") is not True:
        candidates.append(("library", "package exposes publishable entry points"))

    unique = {project_type for project_type, _ in candidates}
    if len(unique) > 1:
        details = ", ".join(
            f"{project_type} ({reason})" for project_type, reason in candidates
        )
        raise SystemExit(
            "error: multiple project-type signals found: "
            f"{details}; rerun with --project-type <profile>"
        )
    if candidates:
        return candidates[0][0], [candidates[0][1]]
    return "generic", ["no reliable product-shape marker found"]


def package_manager(target: Path, stack: str) -> str:
    markers = (
        ("pnpm-lock.yaml", "pnpm"),
        ("yarn.lock", "yarn"),
        ("bun.lockb", "bun"),
        ("bun.lock", "bun"),
        ("package-lock.json", "npm"),
        ("uv.lock", "uv"),
        ("poetry.lock", "Poetry"),
        ("Pipfile.lock", "Pipenv"),
    )
    for filename, manager in markers:
        if (target / filename).exists():
            return manager
    if stack in {"react", "vue", "wechat-miniprogram", "node"}:
        return "npm（未发现锁文件，请确认）"
    if stack == "python":
        return "pip/venv（未发现锁文件，请确认）"
    return "未识别"


def command_lines(package: dict[str, object], manager: str) -> str:
    scripts = package.get("scripts", {})
    if not isinstance(scripts, dict) or not scripts:
        return "- 未从项目元数据识别；执行前读取仓库配置，不得臆造命令。"
    runner = {
        "pnpm": "pnpm",
        "yarn": "yarn",
        "bun": "bun run",
    }.get(manager, "npm run")
    return "\n".join(
        f"- `{runner} {name}`：`{command}`" for name, command in sorted(scripts.items())
    )


def source_lines(target: Path) -> str:
    candidates = (
        "src",
        "app",
        "apps",
        "packages",
        "pages",
        "components",
        "miniprogram",
        "server",
        "backend",
        "tests",
    )
    found = [name for name in candidates if (target / name).exists()]
    if not found:
        return "- 尚未识别；初始化后根据仓库实际结构补充。"
    return "\n".join(f"- `{name}/`" for name in found)


def render(path: Path, values: dict[str, str]) -> str:
    text = path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    unresolved = sorted(set(re.findall(r"{{([A-Z_]+)}}", text)))
    if unresolved:
        raise SystemExit(f"error: unresolved placeholders in {path}: {', '.join(unresolved)}")
    return text.rstrip() + "\n"


def profile_fragment(kind: str, profile: str, document: str) -> str:
    path = TEMPLATES / "profiles" / kind / profile / f"{document}.md"
    if not path.is_file():
        raise SystemExit(f"error: profile template missing: {path}")
    return path.read_text(encoding="utf-8").strip()


def write_file(path: Path, content: str, force: bool = False) -> None:
    existed = path.exists()
    if existed and not force:
        print(f"skip (exists): {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"{'updated' if existed else 'created'}: {path}")


def copy_file(source: Path, destination: Path) -> None:
    if destination.exists():
        print(f"skip (exists): {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    print(f"created: {destination}")


def main() -> int:
    args = parse_args()
    if args.list_profiles:
        print("stacks: " + ", ".join(STACKS))
        print("project types: " + ", ".join(PROJECT_TYPES))
        return 0

    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        raise SystemExit(f"error: target directory does not exist: {target}")

    package = load_package_json(target)
    dependencies = package_dependencies(package) | python_dependencies(target)
    if args.stack == "auto":
        stack, stack_evidence = detect_stack(target, dependencies)
    else:
        stack, stack_evidence = args.stack, []
    if args.project_type == "auto":
        project_type, type_evidence = detect_project_type(
            target, package, dependencies, stack
        )
    else:
        project_type, type_evidence = args.project_type, []
    manager = package_manager(target, stack)

    evidence = stack_evidence + type_evidence
    if args.stack != "auto":
        evidence.append(f"stack explicitly selected: {stack}")
    if args.project_type != "auto":
        evidence.append(f"project type explicitly selected: {project_type}")

    values = {
        "PROJECT_NAME": str(package.get("name", target.name)),
        "STACK": stack,
        "PROJECT_TYPE": project_type,
        "PACKAGE_MANAGER": manager,
        "COMMANDS": command_lines(package, manager),
        "SOURCE_DIRS": source_lines(target),
        "EVIDENCE": "\n".join(f"- {item}" for item in evidence),
        "DATE": date.today().isoformat(),
    }

    base_agents = render(TEMPLATES / "base" / "AGENTS.md", values)
    agents = "\n\n".join(
        (
            base_agents.rstrip(),
            profile_fragment("stacks", stack, "AGENTS"),
            profile_fragment("project-types", project_type, "AGENTS"),
        )
    ) + "\n"
    base_constitution = render(TEMPLATES / "base" / "CONSTITUTION.md", values)
    constitution = "\n\n".join(
        (
            base_constitution.rstrip(),
            profile_fragment("stacks", stack, "CONSTITUTION"),
            profile_fragment("project-types", project_type, "CONSTITUTION"),
        )
    ) + "\n"

    ai_dir = target / ".ai"
    write_file(target / "AGENTS.md", render(TEMPLATES / "root-AGENTS.md", values))
    write_file(ai_dir / "AGENTS.md", agents, force=args.force)
    write_file(ai_dir / "CONSTITUTION.md", constitution, force=args.force)
    copy_file(TEMPLATES / "specs-README.md", ai_dir / "specs" / "README.md")
    example = ai_dir / "specs" / f"{date.today().isoformat()}-example-feature.spec.md"
    copy_file(TEMPLATES / "spec.example.md", example)

    print()
    print(f"profiles: stack={stack}, project-type={project_type}")
    print("Review the evidence and generated rules before implementation begins.")
    print("Use --stack/--project-type for corrections; use --force only after preserving custom rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
