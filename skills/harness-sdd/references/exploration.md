# Explore and context policy

- Run detector; review git status and project root config. Treat pre-existing uncommitted changes as user-owned.
- Read current project `AGENTS.md` and nested rules only when editing paths under their scope; respect native host behavior.
- Record a **small architecture map**: major entrypoints, directories and responsibilities, request/auth boundaries, test commands. Do not auto-write a directory snapshot or list all files.
- Locate affected code by names, imports, routes, and tests. Expand only where dependencies demand it.
- If code contradicts rules, document the discrepancy and ask on critical contracts; do not silently override existing behavior.
- Need to persist a new directory convention? Suggest a concise correction to `AGENTS.md`, subject to developer approval.
