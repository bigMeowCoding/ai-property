---
name: integrate-busy-arms-rum
description: Use when adding, migrating, reviewing, or troubleshooting Alibaba Cloud ARMS RUM in a team H5/Web project that uses @busy-fe/monitor-web, including Vite, Vue, React, application versions, user binding, API evaluation, custom reporting, CSP, or frontend-to-backend tracing.
---

# Integrate Busy ARMS RUM

Apply the team's `@busy-fe/monitor-web` contract, not generic ARMS or legacy `alife-logger` patterns.

## Required reference

Read [references/arms-rum-guide.md](references/arms-rum-guide.md) completely before changing code, reviewing an integration, or diagnosing an issue. It contains wrapper-specific behavior that cannot be inferred from the upstream SDK.

## Workflow

1. Inspect the package manager, bundler, app entry, router mode, environment conventions, authentication flow, existing monitoring code, CSP, and API origins. Preserve project conventions.
2. Determine the task: new integration, migration, runtime reporting, tracing, or diagnosis. Change only the requested scope.
3. Confirm `endpoint` and `pid` provisioning and the Busy registry. Treat them as runtime configuration; do not hardcode environment-specific values.
4. Install only required packages. Use `@busy-fe/monitor-app-version` for a production-grade release dimension.
5. Centralize monitoring in one module. Call `initMonitor` once, before app mount. Skip `local` by default and use `env` for other environments.
6. Preserve wrapper defaults unless the requirement explicitly changes them. In particular, use `sessionConfig.sampleRate`; do not use top-level `sampleRate` for web session sampling.
7. Bind login data after initialization is `READY`. Set `user.name` and `user.tags`; never overwrite SDK-generated `user.id`.
8. For tracing, distinguish same-origin `tracing: true` from cross-origin object configuration. Check the installed wrapper's declarations before writing object configuration because `@busy-fe/monitor-web@0.0.9` has a known `tracing?: boolean` type/runtime mismatch. Verify backend propagation, CORS headers, gateway forwarding, sampling cost, and protocol compatibility.
9. Prefer `parseResourceName` when only URL normalization is needed. Treat custom `evaluateApi` as a full replacement of the wrapper default and restore failure reporting explicitly if required.
10. Verify in browser DevTools and ARMS: initialization status, network/CSP, PV, API/error data, version, user fields, filters, and trace linkage.

## Output contract

When implementing, provide focused diffs that match the repository. When advising, give copy-ready configuration plus prerequisites and verification steps. When diagnosing, report evidence and root cause before proposing changes.

Do not claim success without runtime or build evidence. If ARMS console access, backend tracing, CSP, or CI variables are outside the workspace, state the exact external verification still required.
