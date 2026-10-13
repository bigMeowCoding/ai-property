# Harness SDD 2.0 — installable Agent Skill

A low-documentation, verification-driven workflow for Codex and Claude Code.

## Install

Copy the **entire `harness-sdd-2.0` directory** to an Agent Skills discovery location supported by your client (rename directory to `harness-sdd` if preferred). For example, project-local `.agents/skills/harness-sdd/` for a compatible Codex configuration. Claude Code skill discovery may use `.claude/skills/harness-sdd/`; follow the host version's current location and command conventions.

The directory must contain `SKILL.md`, `references/`, `assets/`, and `scripts/`. Installing does **not** change your repository's root `AGENTS.md`.

Invoke through a natural request like: `Use harness-sdd to implement ...`; whether `/harness-sdd` is available depends on the client.

## Local helper commands

```bash
node scripts/detect-project.mjs --project /path/to/repo
node scripts/verify.mjs --project /path/to/repo --checks lint,typecheck,test,build --output /path/to/repo/.sdd/work/TASK-001/verification.json
node scripts/cleanup.mjs --project /path/to/repo --task TASK-001 --confirm-delivered --evidence /path/to/repo/.sdd/work/TASK-001/delivery.json
```

**Do not execute unknown package scripts blindly**. Review them first. `verify.mjs` does not install dependencies and does not run absent scripts. `cleanup.mjs` will refuse without a valid delivery manifest, confirmed delivery, required AC completion, current-worktree evidence, and an owned-file list. See `scripts/cleanup.mjs --help`.

## Task worktree

Create `.sdd/work/TASK-ID/spec.md` from `assets/spec-template.md` for Standard/Advanced tasks. Use `.git/info/exclude` for local ignore or an approved `.gitignore` change. All temp files remain local until delivery; for collaborative workflows, hand over the task spec through an Issue or PR before relying on cleanup.

## Run tests

```bash
node --test tests/*.test.mjs
```

## Limitations

- A Skill cannot ensure actual independent subagents exist; report when review is not independent.
- `verify.mjs` evaluates available engineering checks, not business ACs or physical-device scenarios.
- `cleanup.mjs` deliberately does not delete the whole task directory or files that are not explicitly owned.
- No automatic global-rule edits, merge, push, deployment, or destructive Git operations.
