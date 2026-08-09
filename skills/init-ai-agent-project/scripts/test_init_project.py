#!/usr/bin/env python3
"""Integration tests for profile detection and document composition."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("init_project.py")
CLEANUP_SCRIPT = Path(__file__).with_name("cleanup-legacy-docs.sh")
STACKS = ("generic", "react", "vue", "wechat-miniprogram", "node", "python")
PROJECT_TYPES = (
    "generic",
    "admin",
    "mobile",
    "consumer-web",
    "api-service",
    "library",
)


class InitProjectTests(unittest.TestCase):
    def run_init(self, target: Path, *args: str, succeeds: bool = True) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(target), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        if succeeds and result.returncode != 0:
            self.fail(result.stderr or result.stdout)
        if not succeeds and result.returncode == 0:
            self.fail("initializer unexpectedly succeeded")
        return result

    def write_package(self, target: Path, data: dict[str, object]) -> None:
        (target / "package.json").write_text(json.dumps(data), encoding="utf-8")

    def assert_profiles(self, target: Path, stack: str, project_type: str) -> None:
        agents = (target / ".ai" / "AGENTS.md").read_text(encoding="utf-8")
        constitution = (target / ".ai" / "CONSTITUTION.md").read_text(encoding="utf-8")
        self.assertIn(f"技术栈：`{stack}`", agents)
        self.assertIn(f"项目形态：`{project_type}`", agents)
        self.assertNotIn("UI-SPEC", agents + constitution)
        self.assertFalse((target / ".ai" / "UI-SPEC.md").exists())

    def test_react_admin_auto_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "sales-admin"
            target.mkdir()
            self.write_package(
                target,
                {
                    "name": "sales-admin",
                    "private": True,
                    "dependencies": {"react": "latest"},
                    "scripts": {"test": "vitest run"},
                },
            )
            (target / "pnpm-lock.yaml").touch()
            self.run_init(target)
            self.assert_profiles(target, "react", "admin")
            agents = (target / ".ai" / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("render 保持纯净", agents)
            self.assertIn("权限同时检查", agents)
            self.assertIn("`pnpm test`", agents)
            constitution = (target / ".ai" / "CONSTITUTION.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("渲染纯度", constitution)
            self.assertIn("授权在服务端成立", constitution)
            spec = next((target / ".ai" / "specs").glob("*.spec.md"))
            spec_text = spec.read_text(encoding="utf-8")
            self.assertNotIn("sdd-spec-writer", spec_text)
            self.assertIn("## 8. 测试矩阵", spec_text)
            self.assertIn("## 11. 发布与回滚", spec_text)

    def test_vue_mobile_explicit_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_package(target, {"dependencies": {"vue": "latest"}})
            self.run_init(target, "--project-type", "mobile")
            self.assert_profiles(target, "vue", "mobile")

    def test_mobile_detection_names_the_actual_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_package(
                target, {"dependencies": {"vue": "latest", "vant": "latest"}}
            )
            self.run_init(target)
            agents = (target / ".ai" / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("mobile dependency: vant", agents)

    def test_wechat_miniprogram_mobile_auto_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "project.config.json").write_text("{}", encoding="utf-8")
            (target / "app.json").write_text("{}", encoding="utf-8")
            self.run_init(target)
            self.assert_profiles(target, "wechat-miniprogram", "mobile")

    def test_python_api_auto_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "requirements.txt").write_text("fastapi==1.0\n", encoding="utf-8")
            self.run_init(target)
            self.assert_profiles(target, "python", "api-service")

    def test_explicit_consumer_web_profile(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_package(target, {"dependencies": {"react": "latest"}})
            self.run_init(target, "--project-type", "consumer-web")
            self.assert_profiles(target, "react", "consumer-web")

    def test_ambiguous_stack_requires_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            self.write_package(
                target, {"dependencies": {"react": "latest", "vue": "latest"}}
            )
            result = self.run_init(target, succeeds=False)
            self.assertIn("multiple stack signals", result.stderr)
            self.assertIn("--stack", result.stderr)

    def test_explicit_profiles_resolve_ambiguous_signals(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "dashboard-library"
            target.mkdir()
            self.write_package(
                target,
                {
                    "name": "dashboard-library",
                    "dependencies": {"react": "latest", "vue": "latest"},
                    "exports": "./index.js",
                },
            )
            self.run_init(target, "--stack", "react", "--project-type", "library")
            self.assert_profiles(target, "react", "library")

    def test_wechat_miniprogram_root_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / "project.config.json").write_text(
                json.dumps({"miniprogramRoot": "client/"}), encoding="utf-8"
            )
            (target / "client").mkdir()
            (target / "client" / "app.json").write_text("{}", encoding="utf-8")
            self.run_init(target)
            self.assert_profiles(target, "wechat-miniprogram", "mobile")

    def test_existing_rules_are_preserved_without_force(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".ai").mkdir()
            agents = target / ".ai" / "AGENTS.md"
            agents.write_text("custom\n", encoding="utf-8")
            self.run_init(target, "--stack", "react", "--project-type", "admin")
            self.assertEqual(agents.read_text(encoding="utf-8"), "custom\n")
            self.run_init(
                target, "--stack", "react", "--project-type", "admin", "--force"
            )
            self.assertIn("技术栈：`react`", agents.read_text(encoding="utf-8"))

    def test_every_explicit_profile_combination_renders(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            for stack in STACKS:
                for project_type in PROJECT_TYPES:
                    with self.subTest(stack=stack, project_type=project_type):
                        self.run_init(
                            target,
                            "--stack",
                            stack,
                            "--project-type",
                            project_type,
                            "--force",
                        )
                        self.assert_profiles(target, stack, project_type)

    def test_cleanup_preserves_project_ui_documents(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            (target / ".ai").mkdir()
            (target / ".ai" / "AGENTS.md").write_text("rules\n", encoding="utf-8")
            (target / "AGENTS.md").write_text("pointer\n", encoding="utf-8")
            ui_spec = target / "ui-spec.md"
            ui_spec.write_text("project-owned design rules\n", encoding="utf-8")
            result = subprocess.run(
                ["bash", str(CLEANUP_SCRIPT), str(target)],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(ui_spec.is_file())
            self.assertTrue((target / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()
