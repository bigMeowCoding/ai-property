# Distill without documentation growth

At finish, sort each lesson:

1. **One-off**: discard the temporary note after fixing.
2. **Machine-checkable**: prefer tests, TS types, lints, CI gates, invariant assertions.
3. **Project durable**: propose a targeted correction to current AGENTS.md or existing architecture guidance, avoiding duplicate rules. Keep AGENTS.md an index and brief core contract, not a history log.
4. **Cross-project reusable process**: suggest an opt-in update to a specialist Skill; do not auto-edit the global Skill.

Only recommend a rule when it addresses a repeatable root cause, is valid beyond this task, has a clear scope, and can be kept current. Merge, replace or delete obsolete rules. Explicit approval is required for persistent policy changes.

Cleanup prerequisites: user confirms delivery; required AC complete or exceptions explicitly accepted; recorded check results correspond to current worktree; no blockers; work path is a recognized `.sdd/work/<task-id>` directory; only manifest-owned files may be removed. If not met, keep task intact and report why.
