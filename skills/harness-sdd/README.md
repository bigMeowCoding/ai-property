# Harness SDD 3.1 — installable Agent Skill

A verification-driven software delivery workflow with an optional repository-governance mode.

## Install

Copy the entire `harness-sdd` directory to an Agent Skills discovery location supported by your client, such as `.agents/skills/harness-sdd/`. The installed directory must keep `SKILL.md`, `agents/`, `references/`, `assets/`, `templates/`, `scripts/`, and `tests/` together.

Installing the Skill alone does not modify a repository. Invoke it with a natural request such as `Use harness-sdd to initialize this repository workflow` or `Use harness-sdd to implement this feature`.

## Repository governance

The initializer inspects repository evidence and composes stack and project-type profiles into `AGENTS.md` and `.ai/` governance:

```bash
bash scripts/init.sh /path/to/repo
bash scripts/init.sh /path/to/repo --stack react --project-type admin
bash scripts/init.sh --list-profiles
```

It preserves existing governance files by default. Review generated evidence before implementation and use `--force` only after preserving custom rules. Legacy cleanup scripts must be run only after confirming that useful content has been migrated.

## Task delivery helpers

```bash
node scripts/detect-project.mjs --project /path/to/repo
node scripts/verify.mjs --project /path/to/repo --checks lint,typecheck,test,build --output /path/to/repo/.sdd/work/TASK-001/verification.json
node scripts/cleanup.mjs --project /path/to/repo --task TASK-001 --confirm-delivered --evidence /path/to/repo/.sdd/work/TASK-001/delivery.json
```

Review package scripts before executing them. `verify.mjs` does not install dependencies or run absent scripts. `cleanup.mjs` refuses cleanup without delivery confirmation, completed required acceptance, current-worktree evidence, no blockers, and an explicit owned-file list.

For Standard or Advanced work, create `.sdd/work/TASK-ID/spec.md` from `assets/spec-template.md`. Keep temporary task files local with `.git/info/exclude`, or change `.gitignore` only with approval. Do not create a long-lived `.ai/specs/` archive; remove owned temporary task files after confirmed delivery.

## Run tests

```bash
node --test tests/*.test.mjs
python3 scripts/test_apply_workflow.py
```

## Limitations

- Independent review depends on host support; disclose when review is not independent.
- Automated checks do not prove business flows or physical-device scenarios by themselves.
- No automatic merge, push, deployment, global-rule rewrite, or destructive Git operation.
