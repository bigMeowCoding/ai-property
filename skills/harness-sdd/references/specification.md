# Single ephemeral Spec contract

- Fast: keep goal, intended change and proof in conversation unless the task grows.
- Standard/Advanced: one task-local spec with `Goal`, `Scope`, `Design / Contracts`, `Acceptance`, `Risks`, `Execution`.
- No supplementary plan/tasks/findings Markdown. The spec may use checkboxes or concise AC status when recovery is needed.
- Every AC must name an observable outcome, its verifier, and whether real device/manual validation is necessary.
- Prefer small behavior examples (Given / When / Then) for ambiguous conditions; don't require ceremony for simple cases.
- The verifier must be independent of implementation claims; don't let coding agents weaken tests to manufacture success.
- Pilot an independent slice first for risky repetitive migrations, then update the single spec if assumptions change.
- Never treat a non-runnable test or an unperformed device check as passed.
