---
name: harness-sdd
description: Establish or calibrate repository AI governance, and deliver software changes through temporary verification-driven task specifications. Use when initializing `.ai/` rules and project profiles, migrating legacy workflow documents, or implementing features, fixes, refactors, migrations, and cross-module changes with risk-based planning, deterministic checks, bounded repair, review, and safe cleanup.
metadata:
  version: 3.1.0
---

# Harness SDD

Use the smallest evidence-backed workflow that fits the request. This skill has two related modes: persistent repository governance and task-scoped software delivery.

## Route the request

| Request | Mode | Persistent output |
| --- | --- | --- |
| Initialize or standardize an AI-assisted repository, create `.ai/` governance, select stack/product profiles, or migrate legacy Agent documents | **Repository governance** | `AGENTS.md`, `.ai/AGENTS.md`, and `.ai/CONSTITUTION.md` |
| Implement, fix, refactor, migrate, or review code in an already usable repository | **Task delivery** | Code/tests; any task Spec is temporary |
| Standardize a repository and implement a change | **Combined** | Establish the governance baseline first, then run task delivery against a real requirement |

For repository governance, read [project workflow](references/project-workflow.md). Read [profile selection](references/profile-selection.md) when choosing or extending stack and project-type profiles. Do not create example requirements as project facts.

For task delivery, use the workflow below and load only the referenced guidance needed for the current step.

## Shared principles

1. **Observed behavior and intended behavior are distinct.** Code and tests are the source of truth for current behavior. The current user request and acceptance contract define intended behavior; stale documents do not override observation.
2. **Judge first.** Define observable acceptance criteria and verification before editing. Missing evidence is `unverified`, never `passed`.
3. **Specs are temporary.** Delivery uses at most one `.sdd/work/<task-id>/spec.md`, and Fast work may keep the acceptance contract in conversation. Do not create long-lived `.ai/specs`, parallel plans, findings, or review documents.
4. **Context on demand.** Read applicable project instructions and relevant code, tests, callers, and dependency paths. Do not recursively load unrelated documentation.
5. **Small changes and bounded feedback.** Implement a focused increment, verify, diagnose, and repair. Stop after 3 attempts on the same root cause or 2 iterations without measurable progress.
6. **Evidence over claims.** Record executed checks, exit codes, revision/worktree fingerprint, acceptance evidence, and unverified conditions.
7. **Risk controls follow impact.** High-risk changes require a design checkpoint, wider regression checks, and independent fresh-context review when available.
8. **Curate persistent rules.** Prefer tests, types, lint rules, and concise reusable guidance. Change repository governance only when requested or explicitly approved; do not accumulate task history in global instructions.
9. **Protect developer control.** Do not deploy, merge, push, weaken tests, overwrite user work, or delete project files without scope and authorization. Cleanup may remove only known owned temporary files, or explicitly approved legacy documents after their content is migrated.

## Task delivery modes

- **Fast**: local, reversible, low-risk fix with clear acceptance. Keep the contract in conversation unless the task grows.
- **Standard**: feature or multi-file change. Use one temporary task Spec containing goal, scope, design/contracts, acceptance, risks, and execution state.
- **Advanced**: authentication, authorization, money/data integrity, shared libraries, cross-runtime/WebView, deployment, migration, or uncertain dependency work. Require a design checkpoint, focused pilot when useful, independent review, and wider regression checks.

Small diff size does not imply low risk. Honor a user-requested higher safeguard level.

## Task delivery workflow

### 1. Explore

Read applicable `AGENTS.md`, inspect Git status without changing it, and discover available checks with:

```bash
node <skill-dir>/scripts/detect-project.mjs --project <repo>
```

Inspect relevant entrypoints, types, tests, callers, and dependency paths. Treat pre-existing changes as user-owned. Read [exploration](references/exploration.md) as needed.

### 2. Specify

For Standard or Advanced work, create `.sdd/work/<task-id>/spec.md` from [the task template](assets/spec-template.md). Keep it untracked using `.git/info/exclude`, or edit `.gitignore` only with approval. Give each `AC-#` an observable outcome and a verification method; mark manual-only and unknown items. Read [specification](references/specification.md).

If the repository already contains requirement documents, use them as inputs without creating or maintaining a parallel `.ai/specs` archive. Keep the temporary task Spec limited to execution state, acceptance mapping, and evidence.

### 3. Execute

Work in small independently verifiable increments, preserve unrelated edits, and do not expand scope silently. Keep progress in the existing task Spec or tool state, not another Markdown file. Read [execution](references/execution.md).

### 4. Verify and repair

Run only reviewed project checks. The deterministic helper can record evidence:

```bash
node <skill-dir>/scripts/verify.mjs --project <repo> --checks lint,typecheck,test,build --output <task-dir>/verification.json
```

Treat absent scripts as `unavailable`. Never manufacture success by skipping assertions or weakening tests. Re-run affected checks after implementation, test, verifier, or configuration changes. Read [verification](references/verification.md).

### 5. Review and converge

Map every `AC-#` to observed evidence, inspect the final diff for regressions, failure paths, security, compatibility, and unintended changes, and disclose manual or unavailable checks. Advanced work needs an independent reviewer when supported; otherwise label the review non-independent. Read [review](references/review.md).

### 6. Handoff, distill, and clean up

Report changed files, acceptance evidence, checks passed/failed/unavailable, manual follow-up, and remaining risks. Distill durable lessons to code/tests/lint first, then propose focused governance updates when warranted. After explicit delivery confirmation and successful applicable checks, clean only owned temporary files with `cleanup.mjs`. Read [distillation](references/distillation.md).

## Helper scripts

All task-delivery `.mjs` scripts use built-in Node.js modules. Run `node <skill-dir>/scripts/<name>.mjs --help` before use.

Repository-governance helpers are documented in [project workflow](references/project-workflow.md). Their stable entry point is:

```bash
bash <skill-dir>/scripts/init.sh /path/to/repo
```

## Stop conditions

Stop and report instead of inventing a pass when required evidence cannot run, credentials or devices are missing, observed behavior contradicts a critical requirement, a required high-risk checkpoint is unresolved, or verification became stale after further changes.
