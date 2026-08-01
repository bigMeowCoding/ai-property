---
name: codex-troubleshooter
description: Diagnose and fix local Codex problems. Use when Codex Desktop, CLI, IDE extension, skills, plugins, MCP, app-server, new thread startup, thread resume, "Reconnecting .../5", "request timed out", WebSocket, proxy, config.toml, LaunchAgent, or SKILL.md/frontmatter issues are mentioned. Also use when asked to make Codex startup faster or stop repeated reconnects.
---

# Codex Troubleshooter

Use this skill to diagnose local Codex runtime issues before changing repo code. Prefer reversible user-scope fixes under `~/.codex` or `~/Library/LaunchAgents`; do not edit auth tokens or destructive state unless the user explicitly asks.

## Workflow

1. Inspect the symptom and scope.
   - Determine whether the issue happens on new thread start, thread resume, every prompt, tool startup, plugin sync, or only one repository.
   - If an image shows "Reconnecting .../5" or "request timed out", prioritize network/proxy/WebSocket checks.

2. Read local guidance and configuration.
   - Read the active repo `AGENTS.md` and delegated `.ai/AGENTS.md` if present.
   - Read `~/.codex/config.toml`, but do not print or edit `~/.codex/auth.json`.
   - Check skill/plugin files only after the logs point there.

3. Query recent Codex logs.
   - Use SQLite logs first: `~/.codex/logs_2.sqlite`.
   - Look for `ERROR`, `WARN`, `thread/start`, `thread/resume`, `session_init`, `responses_retry`, `websocket`, `skill`, `plugin`, `MCP`, and exact user-visible text.
   - Keep log queries narrow to avoid dumping large prompts or secrets.

4. Classify common failures.
   - Skill load failure: fix malformed `SKILL.md` YAML frontmatter. It must start with `---`, include only required metadata such as `name` and `description`, then close with `---`.
   - Plugin manifest warning: fix invalid `interface.defaultPrompt` length, missing assets, or stale plugin cache only if logs show startup impact.
   - WebSocket/request timeout: run `codex doctor`; compare with and without proxy env vars.
   - MCP startup timeout: check `mcp_servers` in `config.toml`, command existence, startup timeout, and server stderr.
   - Config parse failure: validate TOML before saving and keep a timestamped backup.

5. Apply the smallest reversible fix.
   - Make timestamped backups before editing `~/.codex` files.
   - Use `apply_patch` for manual file edits.
   - For macOS GUI proxy inheritance, set `launchctl` env vars and optionally add a user LaunchAgent; remind the user to fully restart Codex App.

6. Verify.
   - Run `codex doctor` and summarize only relevant lines.
   - If fixing a skill, run the Skill Creator validator on the skill folder.
   - If fixing network/proxy, confirm WebSocket shows `HTTP 101 Switching Protocols` or explain the remaining network blocker.
   - Query recent logs again for the exact fixed error count.

## References

Read `references/diagnostic-playbook.md` when you need concrete commands, known log patterns, or the prior proxy/WebSocket fix sequence.
