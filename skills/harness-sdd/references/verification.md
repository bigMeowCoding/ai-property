# Deterministic Judge + review evidence

- Preferred gates: lint, typecheck, targeted tests, build; choose from existing package scripts, do not invent commands.
- `verify.mjs` reports each gate as `passed`, `failed`, `unavailable`, or `skipped`; overall status is `failed`, `incomplete`, or `passed` only when all requested gates ran and succeeded.
- Verification results include start/end time, cwd, Git HEAD and dirty fingerprint, duration, exit code and truncated output.
- **Security**: explicit project opt-in to commands; do not use untrusted package scripts in unknown repos without review. Tool does not install dependencies.
- AC coverage requires both executable evidence and human/agent inspection of the actual acceptance map. A green build alone proves no user flow.
- Browser/device integration, WebView, user permissions, network failure and rollback may require manual evidence.
- CI should re-run gates on the exact merged revision; local success is not deployment proof.
