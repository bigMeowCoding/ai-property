# Host adapters

Keep the canonical skill portable; use client-specific install locations rather than duplicating workflow rules. Codex commonly discovers project skills under `.agents/skills/`; Claude Code commonly uses `.claude/skills/`. Verify command invocation semantics against your installed client version. All local helper scripts work with plain Node.js and do not depend on an agent host.
