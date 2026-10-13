# Host adapters

Keep the canonical skill portable; use client-specific install locations rather than duplicating workflow rules. Codex commonly discovers project skills under `.agents/skills/`; Claude Code commonly uses `.claude/skills/`. Verify command invocation semantics against your installed client version. Task-delivery helpers use plain Node.js; repository-governance helpers use standard Python 3 and Bash. None depends on an agent host.
