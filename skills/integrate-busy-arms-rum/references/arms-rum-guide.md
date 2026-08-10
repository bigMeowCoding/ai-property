# Busy ARMS RUM Reference

## Contents

- Architecture and prerequisites
- Installation and initialization
- Wrapper-specific semantics
- Version reporting
- User binding
- Tracing
- API evaluation
- Runtime reporting
- Vue and React placement
- Migration and troubleshooting
- Verification checklist

## Architecture and prerequisites

The browser app calls `@busy-fe/monitor-web`, which wraps and installs `@arms/rum-browser`; it reports to Alibaba Cloud ARMS RUM by `endpoint` and `pid`. Do not add `alife-logger` or install the upstream SDK separately. `@busy-fe/monitor-app-version` optionally injects and reads the release version.

Before integration, confirm:

- ARMS Web/H5 application exists and provides non-empty `endpoint` and `pid`.
- The project can reach the Busy registry, commonly `https://npm.hnlshm.com/`.
- production clients can reach the endpoint domain.
- CSP `connect-src` permits the reporting domain.

Use upstream Alibaba Cloud Web/H5 SDK documentation only for fields not specifically described here. The wrapper rules below take precedence for wrapper behavior.

## Installation and initialization

```ini
# .npmrc
registry=https://npm.hnlshm.com/
```

```bash
pnpm add @busy-fe/monitor-web
pnpm add @busy-fe/monitor-app-version
```

Call `initMonitor` globally once in the app entry before mounting the root component. A production baseline is:

```ts
import { getMonitorAppVersion } from "@busy-fe/monitor-app-version";
import { initMonitor } from "@busy-fe/monitor-web";

const appEnv = import.meta.env.VITE_APP_ENV ?? "prod";
const endpoint = import.meta.env.VITE_ARMS_ENDPOINT;
const pid = import.meta.env.VITE_ARMS_PID;
const shouldInit =
  appEnv !== "local" &&
  import.meta.env.VITE_ENABLE_ARMS !== "false" &&
  Boolean(endpoint && pid);

if (shouldInit) {
  initMonitor({
    endpoint,
    pid,
    env: appEnv,
    version: getMonitorAppVersion(),
    spaMode: "history",
    sessionConfig: { sampleRate: 1 },
    filter: { ignoreErrors: ["ResizeObserver loop limit exceeded"] },
    extraTags: { biz_line: "retail" },
    tracing: true,
    debug: import.meta.env.DEV,
  });
}
```

Match `spaMode` to the router (`history` or `hash`). Default to no initialization and no reporting in `local`; use `daily`, `pre`, `gray`, and `prod` as event `env` values. For short local validation, temporarily initialize with `debug: true`, then disable it again.

Recommended variables:

| Variable | Requirement | Meaning |
|---|---:|---|
| `VITE_ARMS_ENDPOINT` | required | ARMS reporting endpoint |
| `VITE_ARMS_PID` | required | ARMS application PID |
| `VITE_APP_ENV` | recommended | `local`, `daily`, `pre`, `gray`, or `prod` |
| `VITE_BUSY_MONITOR_APP_VERSION` | production recommended | Stable release/tag |
| `VITE_ENABLE_ARMS` | optional | Exact string `false` skips initialization |

## Wrapper-specific semantics

- Default collectors: `api`, `jsError`, `consoleError`, and `action` enabled.
- Default `reportConfig`: `flushTime: 0`, `maxEventCount: 10`.
- With `remoteConfig.enable: true`, missing values default to `mode: "launch-first"` and `cacheTimeout: 3600000`.
- Top-level `sampleRate` neither skips web initialization nor passes directly to ARMS. Use `sessionConfig.sampleRate` in the `0..1` range.
- Missing `evaluateApi` selects the built-in default and connects `sendException` for API failure supplementation.
- `properties` is formed as `{ ...config.properties, ...normalizeTags(extraTags) }`; `extraTags` wins on duplicate keys. Prefer tag keys beginning with lowercase letters and containing lowercase letters, digits, or underscores.
- `filter.ignoreErrors` and `filters.exception` append to built-in `GLOBAL_IGNORE_ERRORS`; callers cannot replace global rules.
- When filters or a business `beforeReport` exist, exception filters run first and return `false` on a match; the business hook runs afterward.
- `tracing` passes through unchanged to upstream initialization.

Initialization states are `UNINIT`, `INITING`, `READY`, and `ERROR`. Repeated calls during `INITING` warn and return; successful initialization reaches `READY`; inspect failures with `getInitError()`. Active reporting APIs guard readiness and throw in `UNINIT`, `INITING`, or `ERROR`. Design calls that may run in disabled environments accordingly.

## Version reporting

Use one stable version string per release. For Vite:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { vitePluginBusyMonitorAppVersion } from "@busy-fe/monitor-app-version/vite";

export default defineConfig({
  plugins: [vitePluginBusyMonitorAppVersion()],
  // Or pass { explicit: process.env.RELEASE_TAG }.
});
```

At runtime, pass `version: getMonitorAppVersion()` to `initMonitor`.

`getMonitorAppVersion()` resolves:

1. `import.meta.env.VITE_BUSY_MONITOR_APP_VERSION`
2. `process.env.BUSY_MONITOR_APP_VERSION`
3. caller fallback
4. current UTC date as `YYYY-MM-DD`

The date fallback is unsafe as a production release identity: long-lived tabs or builds can split one release across multiple versions. CI must inject a semver, Git tag, or pipeline release identifier. Add `/// <reference types="@busy-fe/monitor-app-version/client" />` or the equivalent `tsconfig` type entry when needed.

For non-Vite bundlers, call `resolveMonitorAppVersionForBuild({ explicit })` during the build and inject the result. Its resolution order is `explicit`, `BUSY_MONITOR_APP_VERSION`, `VITE_BUSY_MONITOR_APP_VERSION`, then UTC date.

Runtime `setConfig({ version })` is reserved for rare no-refresh release switches. Prefer a refresh and new initialization at release boundaries to avoid mixed versions in one session.

## User binding

Team convention uses `user.tags` for the phone number and `user.name` for display name. Confirm applicable privacy policy before transmitting personal data. Never set `user.id`; the SDK-generated value supports UV counting.

Known at initialization:

```ts
initMonitor({ endpoint, pid, user: { name: "张三", tags: "13800138000" } });
```

After login:

```ts
import { updateUserConfig } from "@busy-fe/monitor-web";

function bindMonitorUser(profile: { realName: string; phone: string }) {
  if (!profile.phone) return;
  updateUserConfig({ user: { name: profile.realName, tags: profile.phone } });
}
```

`updateUserConfig` merges user configuration before calling upstream `setConfig`; it does not replace other existing user fields. Ensure initialization is `READY`, especially when local or feature-flagged environments skip initialization.

## Tracing

Tracing injects trace context into automatically collected API requests, enabling correlation with backend ARMS or OpenTelemetry traces. It creates additional trace volume and possible cost; coordinate sampling with backend/operations.

Prerequisites:

- backend is instrumented and parses the selected propagation protocol;
- gateway preserves propagation headers;
- cross-origin servers include headers such as `traceparent` and `tracestate` in `Access-Control-Allow-Headers`;
- frontend and backend propagation protocols agree.

For same-origin APIs and standard W3C/OpenTelemetry propagation, use `tracing: true`. It is equivalent to an enabled, 100% sampled, tracestate-enabled configuration with no cross-origin allowlist. Cross-origin requests are not injected by default.

Before adding cross-origin object configuration, inspect the installed `@busy-fe/monitor-web` declaration. The published `0.0.9` runtime passes tracing objects through and the bundled upstream SDK accepts them, but its public `WebConfig` incorrectly declares `tracing?: boolean`. Prefer upgrading to a wrapper release that exports the documented `TracingConfig`. If `0.0.9` cannot be upgraded, keep the compatibility cast local and label it for removal; do not weaken project-wide types.

For cross-origin or non-default protocols on a release with corrected types:

```ts
initMonitor({
  endpoint,
  pid,
  tracing: {
    enable: true,
    sample: 100,
    tracestate: true,
    baggage: false,
    allowedUrls: [
      {
        match: "https://api.example.com",
        propagatorTypes: ["tracecontext"],
      },
    ],
  },
});
```

Temporary `0.0.9` compatibility form:

```ts
const crossOriginTracing = {
  enable: true,
  sample: 100,
  tracestate: true,
  baggage: false,
  allowedUrls: [
    {
      match: "https://api.example.com",
      propagatorTypes: ["tracecontext"],
    },
  ],
};

initMonitor({
  endpoint,
  pid,
  // Remove the cast after upgrading to a release with TracingConfig support.
  tracing: crossOriginTracing as unknown as boolean,
});
```

`sample` is `0..100`. `allowedUrls[].match` accepts a string prefix, regular expression, or `(url) => boolean`. Propagators include `tracecontext`, `b3`, `b3multi`, `jaeger`, and `sw8`. Keep the allowlist limited to trusted business APIs. Runtime `setConfig` can update tracing with upstream semantics.

Verify request headers in DevTools, CORS preflight, protocol agreement, gateway forwarding, and navigation from a RUM API event to its backend trace.

## API evaluation

The wrapper's default `evaluateApi`:

- keeps the original URL as `name`;
- sets `success: 0` for an error or HTTP status `0`/`>=400`;
- creates one root-level `JSON.stringify` snapshot containing params, response, request headers, and response headers;
- supplements failed API events with exceptions.

If only dynamic URL segments need normalization, preserve the default and use:

```ts
initMonitor({
  endpoint,
  pid,
  parseResourceName(url) {
    return url.replace(/\/\d+/g, "/:id");
  },
});
```

Passing `evaluateApi` completely replaces the default and disables its automatic failure supplementation. A custom implementation must calculate `name`, `success`, and `snapshots`, and explicitly call `sendException` when failure supplementation remains required. Keep it fast and truncate snapshots to about 5000 characters.

To extend the default, install `@busy-fe/monitor-core`, call `createDefaultEvaluateApi(options, response, error)`, then return a shallow override. Calling this default directly does not automatically restore wrapper registration of failure supplementation; call `sendException` explicitly when `base.success === 0` if required.

## Runtime reporting

```ts
import {
  getConfig,
  getInitError,
  getStatus,
  sendCustom,
  sendException,
  sendResource,
  sendView,
  setConfig,
} from "@busy-fe/monitor-web";

sendCustom({
  type: "行为",
  name: "点击支付",
  group: "结算页",
  properties: { 页面: "/checkout" },
});

sendException({
  name: "下单失败",
  message: "支付接口返回错误",
  properties: { 订单号: "xxx" },
});

sendResource({
  name: "order/create",
  type: "fetch",
  duration: 320,
  url: "https://api.example.com/order/create",
});

sendView({ type: "custom", t1: 1, t2: 2, t3: 3 });
setConfig({ env: "gray" });
void getConfig();
console.log(getStatus(), getInitError());
```

`sendCustom` requires `type` and `name`; optional fields include `group`, `value`, and `properties`. `sendException` requires `name` and `message`; optional fields include `file`, `stack`, `line`, `column`, and `properties`. ARMS object payloads are preferred; business field values may be Chinese. `sendView` also depends on peer implementation support.

Use exported types such as `ArmsSendCustomPayload` and `ArmsSendExceptionPayload`.

## Vue and React placement

Create a central `src/monitor.ts` (or project-equivalent) exporting setup and user-binding functions. In Vue 3, call setup before `createApp(...).mount(...)`; bind after the user store resolves. In React, call setup before `createRoot(...).render(...)`; bind from the authentication flow. Account for React Strict Mode and hot reload by keeping initialization outside component render/effect paths.

## Migration and troubleshooting

Migration from `alife-logger`:

1. Remove the dependency and `window.__bl` usage.
2. Replace `BrowserLogger.singleton({ pid, ... })` with centralized `initMonitor({ endpoint, pid, ... })`.
3. Replace username/uid `setConfig` patterns with `updateUserConfig({ user: { name, tags } })` without changing `user.id`.
4. Add stable version injection.
5. Confirm data under the new PID before retiring the old ARMS application configuration.

| Symptom | Checks |
|---|---|
| `getStatus() === "ERROR"` | `getInitError()`, empty endpoint/PID |
| `READY` but no console data | network/CSP, `beforeReport === false`, wrong ARMS app/PID |
| repeated init has no effect | initialization is intentionally singleton; inspect call sites |
| SPA route changes lack PV | `spaMode` must match history/hash router |
| API names are noisy | use `parseResourceName`; use `evaluateApi` only for full control |
| trace headers absent/cross-origin fails | `allowedUrls`, CORS allow-headers, backend protocol, gateway forwarding |
| one release has multiple versions | date fallback was used; inject stable CI release value |
| new version absent in console | confirm deployment and that runtime version equals CI value |

## Verification checklist

1. Build/typecheck/tests pass according to repository conventions.
2. Initialization occurs once before mount and reaches `READY` in an enabled environment.
3. `local` and `VITE_ENABLE_ARMS=false` produce no reporting or unsafe active API calls.
4. ARMS receives page views, route transitions, API resources, and a controlled test exception.
5. CSP and endpoint network requests succeed.
6. ARMS events contain expected `env`, stable CI `version`, and normalized tags.
7. Login updates `user.name`/`user.tags` without replacing `user.id`.
8. Filters suppress only intended exceptions and preserve global rules.
9. Cross-origin tracing produces headers without CORS errors and links to backend traces.
10. Sampling and tracing cost have owner approval when production volume matters.
