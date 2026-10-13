# Incremental execution and bounded retries

1. Select smallest unresolved AC/dependency slice.
2. Identify relevant files and planned modifications; preserve user changes.
3. Implement minimal coherent diff; avoid speculative cleanup and unrelated refactoring.
4. Run cheap, targeted verification first. Record errors by root cause, affected module and command.
5. Retry fix with new evidence; at most 3 attempts for the same cause and stop after 2 iterations with no measurable progress.
6. Re-run tests after any verifier, implementation or configuration change. Do not remove tests or silence warnings to pass.
7. On interruption, inspect spec + current Git state + actual verification outputs before resuming. Never trust an old 'passed' result on a new worktree.
8. For concurrent tasks, use unique task ids and isolated worktrees where possible.
