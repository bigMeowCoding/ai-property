---
name: app-webview-bridge
description: >-
  H5 内嵌到运营 App（RN WebView）时的原生桥接落地规范，沉淀自参考项目
  busyming-store-information-h5 的实测实现。覆盖：App 免登上下文
  window.__APP_CONTEXT__ 的消费与请求层兜底、安全区（刘海屏/状态栏/底部
  indicator）适配、返回键与关闭 WebView、拍照/相册/录像等原生能力的
  「请求-回调」调用模型、App→H5 的统一消息入口 receiveRNData 事件分发、
  以及浏览器本地模拟 App 上下文的调试方式。另收录 App 侧权威接入口径：
  三类不可互换的认证凭证（__APP_TOKEN__ / __APP_GET_TOKEN_AUTHINFO__ /
  unifiedPortal.accessToken）、公共上下文三项、导航与容器、定位权限扫码、
  文件预览与签名、媒体 Promise 新协议、键盘 / 生命周期 / 战区同步、MSE 验签边界。
  当需要实现或排查以下内容时使用：App 跳 H5 免登、token/deviceInfo 从 App 取、
  fromApp 判定、是否在 App WebView 内、该用哪个 token、401 或验签失败、
  安全区顶部/底部留白、点返回退出到 App、调起相机相册扫码定位、上传进度回调、
  App 回传数据收不到、真机白屏或误跳企微授权。
---

# App 内嵌 H5 原生桥接（app-webview-bridge）

本 skill 描述**运营 App（RN WebView）与内嵌 H5 的交互契约**，以及在本项目
（`busyming-store-opening-h5`）落地时的适配要求。

### 两个信息源，冲突时以 App 侧为准

| 来源 | 文件 | 性质 |
|---|---|---|
| **App 侧接入指南**（`busyming-operation-app`，基线 `feature/cwc_2.1.2`） | [reference/app-bridge-api.md](reference/app-bridge-api.md) | **权威口径**，Bridge 全表 / 三类 Token / 公共上下文 / 已知限制 / 联调清单 |
| 参考项目 `busyming-store-information-h5` 真机实测 | [reference/bridge-contract.md](reference/bridge-contract.md) | 单个已接入 H5 的切片，含可直接照抄的工程做法，但**不代表 App 默认行为** |

两者差异见 `bridge-contract.md` §8。查某个能力「有没有 / 什么签名 / 什么坑」→ 先看
`app-bridge-api.md`；查「怎么在 React 项目里落地」→ 看 `bridge-contract.md` 和模板。

代码骨架：

- 免登：[templates/auth-context.md](templates/auth-context.md)
- 安全区 / 返回 / 相机相册 / 消息入口：[templates/native-capabilities.md](templates/native-capabilities.md)

## App → H5 的传参通道

底层只有 **2 类机制**：URL 传参，以及 RN WebView 的 JS 注入
（`injectedJavaScriptBeforeContentLoaded` 启动前注入 / `injectJavaScript` 运行期执行）。
落到 H5 侧表现为 **5 种形式**：

| # | 形式 | 具体载体 | 时机 | 适用数据 |
|---|---|---|---|---|
| 1 | URL query 参数 | `?authToken=&userId=&userName=&isGrayUser=`，来源标识 `fromApp=operationApp` | 打开 WebView 时 | 短小标量；本项目当前唯一已实现的一条 |
| 2 | 启动注入全局对象（push，同步） | `window.__APP_CONTEXT__` | H5 首行 JS 前 | 登录态与业务上下文大对象 |
| 3 | 启动注入全局常量（push，同步） | `__APP_TOKEN__`、`__APP_CITY__`、`__APP_GEO__`、`__APP_STATUS_BAR_HEIGHT__`、`__APP_PLATFORM__`、`__APP_LIFECYCLE_STATE__` | H5 首行 JS 前 | 标量容器态，**注意都是字符串** |
| 4 | 注入函数供 H5 主动取（pull） | `__APP_GET_SAFE_AREA__()`、`__APP_GET_VERSION__()`、`__APP_GET_CURRENT_LOCATION__()`、`__APP_GET_TOKEN_AUTHINFO__()` | H5 需要时 | 设备 / 权限 / 凭证，可随时重取；同步返回或 Promise |
| 5 | 运行期 App 调 H5（push，异步） | `window.receiveRNData(payload)`、`onAppToken`、`onAppCity`、`onAppGeo`、`onReactNativeSafeAreaInsetsChange`、`appZoneChanged` / `appLifecycleChange` 事件 | 页面运行期任意时刻 | 变化数据与原生能力回调 |

形式 3/4/5 的字段与签名全表见 [app-bridge-api.md](reference/app-bridge-api.md) §5 / §7~§11。

**注入时机保证**：形式 2/3 在 H5 第一行 JS 执行前就已存在，可同步读、不需轮询；
SPA 内部路由跳转不重新注入，WebView 内 `location.reload()` 会重新注入。
统一门户 Token 刷新或战区切换时 **App 会重建 WebView**，页面内存状态不跨切换保留。

不属于 App 传参但常被混谈的两条：

- **企微 OAuth2**（`isAutoLogin=1` → 授权回跳换 token）：H5 自己换登录态，
  **App 内不可用**（跳授权页会白屏），本项目不实现该链路。
- **微信小程序 web-view**：URL 参数 + `wx.miniProgram`（本项目 `src/helpers/wxMiniHelper.ts`），
  与 App 注入是两条独立链路，不要写在同一模块里。

## 使用前必读：本项目已落地状态与仍需联调的事项

**方案已定，不需再确认：** 本项目入口就是运营 App（RN WebView）内嵌免登，
登录态取形式 2 注入的 `window.__APP_CONTEXT__`，
URL 参数 `authToken`（形式 1）保留作兜底，**不实现企微 OAuth2 跳转**。

**当前代码已落地（2026-08-18 核对）：**

1. **`__APP_CONTEXT__` 映射已冻结。** 登录 token / 用户读
   `unifiedPortal.accessToken` / `unifiedPortal.userInfo`；设备信息优先读
   `unifiedTokenResp.data.deviceInfo`，字段完全不存在时才回退顶层 `deviceInfo`；
   `defaultOperateInfo` 写入 store。不要把参考项目的
   `unifiedTokenResp.data.accessToken` 当成本项目登录 token。
2. **接口该用哪个凭证。** 统一门户 / 统一网关接口用 `unifiedPortal.accessToken`；
   App 现有业务后端用 `window.__APP_TOKEN__`；明确要求 `BizMidPlatform` 的系统要
   `await __APP_GET_TOKEN_AUTHINFO__()`。**三者不是同一个 Token 的别名**，
   后端只说「传 token」时必须先问清接口归属、域名、认证头、是否验签。
3. **MSE 验签边界已落地。** `__APP_CONTEXT__` **不下发** App Secret、
   资源树、`permissionCode`。所以「拿到 accessToken + deviceInfo」≠ 已接通。
   本项目由 H5 逐请求生成 MSE 签名，`X-Operate-Info` 由请求层根据 App 默认值和当前页面资源按需生成；
   KEY/SECRET 走云效流水线经 `scripts/ci-build.mjs`
   注入（`.env` 只留空占位行），**不把生产 APP_SECRET 写进仓库或浏览器包**。
   详见 [app-bridge-api.md](reference/app-bridge-api.md) §3、§4.1。

**本项目当前链路：**

| | 参考项目 | 本项目现状 |
|---|---|---|
| 登录态来源 | `window.__APP_CONTEXT__` 注入（App）+ OAuth2（浏览器） | `window.__APP_CONTEXT__` 主链路 + URL `authToken` 兜底，不实现 OAuth2 |
| 状态容器 | `useStore`（zustand 单 store） | `useGlobalState`（`@/store`，zustand + persist 分模块） |
| 入口初始化 | `src/main.tsx` 内联 | `src/helpers/setupApp.ts` 在 `createRoot` 前调 `initAppContext()` |
| 请求兜底 | 缺 token 时从注入上下文回填 | `request.ts` 每请求调 `rehydrateAppContextIfNeeded()`，只回填 token |
| 登录失效 | 依项目实现 | HTTP 401 与业务码 `401` / `'401'` 统一引导，确认后调 `__APP_GO_LOGIN__()` |

维护或迁移时：

1. 保留 `unifiedPortal` / `unifiedTokenResp.data.deviceInfo` 的已冻结映射；App 字段口径变化时先用真机脱敏日志确认，不凭推测兼容。
2. 保留 URL 参数链路作为兜底；`resolveAuthToken` 按 URL → store 逐请求求值。
3. 安全区、返回、相机/相册、`receiveRNData` 这四项与登录态无关，**与传参通道无耦合**，
   按需独立接入即可。

## 桥接能力总表

App 在 `injectedJavaScriptBeforeContentLoaded` 阶段把下列全局挂到 `window`，
即 H5 首行代码执行时它们已存在，可同步读取。

| 能力 | H5 侧接口 | 方向 | 回调 |
|---|---|---|---|
| 免登上下文 | `window.__APP_CONTEXT__`（对象） | App → H5 | 无，同步读 |
| 安全区 | `window.__APP_GET_SAFE_AREA__()` → JSON 字符串或对象 `{top,bottom,left,right}` | H5 → App | `window.onReactNativeSafeAreaInsetsChange(insets)` 由 App 主动调 |
| 状态栏高度（退化） | `window.__APP_STATUS_BAR_HEIGHT__`（number/string） | App → H5 | 无 |
| 关闭 WebView 返回 App | `window.__APP_ROUTER_BACK__()` | H5 → App | 无 |
| 拍照 | `window.__APP_GO_TO_CAMERA__(argStr)` | H5 → App | `eventType: 'cameraCallback'` |
| 相册选择 | `window.__APP_OPEN_PICKER__(argStr)` | H5 → App | `eventType: 'pickerCallback'` |
| 录像 | `window.__APP_OPEN_TRANSCRIBE__(argStr)` | H5 → App | `eventType: 'transcribeCallback'` |
| App 回传数据统一入口 | `window.receiveRNData(payload)` | App → H5 | H5 转发为同名 `CustomEvent` |

App 还提供以下能力（本项目按需接，全表与签名见
[app-bridge-api.md](reference/app-bridge-api.md)）：

| 分类 | 代表能力 | 本项目取舍 |
|---|---|---|
| 认证 | `__APP_TOKEN__`、`__APP_GET_TOKEN_AUTHINFO__()`、`__APP_GO_LOGIN__()` | 按接口归属选凭证；`__APP_GO_LOGIN__` 只允许认证确实失效时调，它会清整个 App 登录态 |
| 导航容器 | `__APP_GO_HOME_TAB__()`、`__APP_OPEN_NEW_WINDOW__(url,…)`、`__OPEN_APP_WEBVIEW__(isShowBack,title)`、`__APP_ORIENTATION__()` | H5 内部跳转一律用自身路由；`__APP_OPEN_NEW_WINDOW__` 是 Native push，会丢内存状态 |
| 设备权限 | `__APP_GET_VERSION__()`(Promise)、`__APP_CHECK_OR_REQUEST_PERMISSION__()`、`__APP_GET_CURRENT_LOCATION__()`、`__APP_OPEN_SETTING__()` | 需要定位/相机前先探权限，`blocked` 引导去系统设置 |
| 扫码 | `__APP_SCAN_CODE__()` | 返回**可能是字符串也可能是对象**，多字段兼容 |
| 通用功能 | `__APP_CALL_PHONE__`、`__APP_COPY_TEXT__`、`__APP_PREVIEW_IMAGE__/VIDEO__`、`__APP_OPEN_MAP__`、`__APP_DOCUMENT_VIEW__` | `__APP_DOCUMENT_VIEW__` 声明是 Promise 但**永不 settle，禁止 await** |
| 媒体上传 | `__APP_OPEN_PICKER_WITH_RESULT__` / `__APP_GO_TO_CAMERA_WITH_RESULT__` / `__APP_OPEN_TRANSCRIBE_WITH_RESULT__` | **优先用这套 Promise 新协议**，只有要上传进度或兼容旧 App 才用事件流旧协议 |
| 容器状态 | `__APP_LIFECYCLE_STATE__` + `appLifecycleChange`、`zoneOwnerInfo` + `appZoneChanged`、`__APP_REGISTER_KEYBOARD_LISTENER__` | 生命周期要用 `sequence` 去重；键盘监听**只有注册没有注销**，根组件注册一次 |

### 环境判定分两层

```ts
// 第一层：是否在运营 App 的 WebView 内（App 侧权威口径）
const isOperationApp = () =>
  (window as any).__BUSYMING_OPERATION_APP__ === true
  && typeof (window as any).ReactNativeWebView?.postMessage === 'function'

// 第二层：这个具体能力在当前 App 版本里存不存在
const hasBridge = (name: string) => typeof (window as any)[ name ] === 'function'
```

- 除生命周期外，公共 Bridge **没有统一版本号**，所以第二层的逐个探测不能省。
- `window.__APP__` 的实际值是字符串 `'SITESTORE'`，不是 Bridge 对象，别当对象用。
- **不要用 User-Agent 判环境。**
- 判定「是否**真机**（用于隐藏调试工具）」不能看 `__APP_CONTEXT__` —— 调试工具自己会注入它，
  要看注入函数：

```ts
const isRealAppWebView = () => {
  const w = window as any

  return typeof w.__APP_ROUTER_BACK__ === 'function'
    || typeof w.__APP_GET_SAFE_AREA__ === 'function'
    || w.__APP_STATUS_BAR_HEIGHT__ != null
}
```

判定「本次会话来自 App」用 URL 参数 + sessionStorage 双写：
URL 上 `fromApp=operationApp` 命中后写 `sessionStorage.from_app_flag='1'`，
之后 SPA 内跳转 / 刷新（URL 参数可能已被清理）仍可判定。

## 落地步骤

### 1. 免登上下文（本项目已落地）

- 按 `templates/auth-context.md` 落到 `src/helpers/appBridge.ts`，按 `useGlobalState` 的字段裁剪。
- 在 `src/helpers/setupApp.ts` 的 `initGlobalState` **之前**调用 `initAppContext()`；
  返回 `true` 表示已由 App 完成免登，跳过 URL 参数分支即可。
  本项目 `setupApp()` 本就在 `createRoot` 之前同步执行，天然满足「渲染前消费」。
- 新增字段必须在 `GlobalState` 接口里声明，并同步补 `clearAll`，
  否则切换用户后会残留上一个用户的数据（参考项目为此专门清空 `empNo`）。
- 请求层兜底：WebView 刷新或持久化被清空时 store 可能没有 token，
  在 `request.ts` 请求拦截器里调 `rehydrateAppContextIfNeeded()`，
  **只补 token 一类鉴权必需项，不整包覆盖业务上下文** —— 页面可能已经改过这些值，
  整包重水合会把页面的覆盖值打回默认值。

### 2. 登录失效（本项目已落地）

- 同时识别 HTTP 状态 401 与 HTTP 200 包体 `code: 401` / `code: '401'`；后者用
  `Number(data.code) === 401` 归一，不要只处理 Axios 错误分支。
- `rawResponse: true` 是显式逃生舱，必须在业务码判定之前原样透传；该模式下由调用方自行处理 401。
- 统一失效入口立即 `clearToken()`，弹出不可点遮罩关闭的单实例“重新登录”引导，
  并保持原请求 reject `RequestError`；`hideErrorMessage` 不得抑制恢复引导。
- 用户确认后按能力优先级恢复：
  `typeof window.__APP_GO_LOGIN__ === 'function'` → 微信小程序首页 → development `/no-auth`。
  Bridge 缺失时不得抛错，也不得用 UA 推测。
- 用模块级标志收敛并发 401，避免多个请求同时弹框/多次拉起登录页；确认回调释放标志。
- 将 `__APP_GO_LOGIN__?: () => void` 声明在 `src/types/global.d.ts`，不用 `(window as any)` 掩盖契约。
- 测试至少覆盖：HTTP 401、数字/字符串业务码 401、并发收敛、Bridge 优先级、
  Bridge 缺失降级、`rawResponse` 不触发登录引导。

### 3. 安全区

- 按 `templates/native-capabilities.md` §1 落到 `src/helpers/safeArea.ts`，在 `setupApp()` 里首先调用 `initSafeArea()`。
- App 内 CSS `env(safe-area-inset-*)` 取不到值，必须用注入值；
  模块把结果写进 `:root` 的 `--app-safe-top` / `--app-safe-bottom`，
  页面统一用 `padding-top: var(--app-safe-top)` 消费，不要各页面各读一遍。
- 在 `src/styles/index.scss` 里给这两个变量兜默认值（浏览器下回退到 `env()`）：

  ```scss
  :root {
    --app-safe-top: env(safe-area-inset-top, 0px);
    --app-safe-bottom: env(safe-area-inset-bottom, 0px);
  }
  ```

- 本项目已有 `src/components/common/FooterButtonWrap.tsx`，底部按钮区留白改用 `--app-safe-bottom`。

### 4. 返回 / 关闭 WebView

- 按 `templates/native-capabilities.md` §2 落到 `src/hooks/useAppBack.ts`，所有自定义返回按钮统一用它。
- 顺序必须是「先 H5 路由栈，再 App back」：直接调 `__APP_ROUTER_BACK__()` 会关掉整个 WebView，
  丢掉 H5 内部的多级历史。判定依据是 `window.history.state?.idx > 0`
  （react-router 的 `createBrowserRouter` 维护该索引）。
- 纯浏览器无桥时兜底 `navigate(-1)`。

### 5. 原生能力调用（相机 / 相册 / 录像等）

调用模型是「注入函数发起 + `receiveRNData` 回调」，见 `templates/native-capabilities.md` §3：

- 参数必须 `JSON.stringify` 后传字符串，注入函数不接受对象。
- 每次调用生成 `__requestId` 一并传下去，回调按 `__requestId` 配对；
  App 未回传 id 时退化为按 `eventType` 配对，只有一个在途调用时再退化为直接兑现。
- 必须带超时（参考项目 10s）并清理在途记录，否则用户取消原生页面时 Promise 永挂。
- 调用前用 `typeof window[bridgeName] === 'function'` 探测，缺失时返回「功能不可用」而不是抛错。

### 6. App → H5 消息入口

- 按 `templates/native-capabilities.md` §4 落到 `src/helpers/installAppMessageReceiver.ts`，在 `setupApp()` 中安装一次。
- 安装时要：幂等（`__APP_RECEIVE_INSTALLED__` 标记）、**保留并链式调用已存在的 `receiveRNData`**、
  兼容 payload 是字符串或对象、按 `eventType`/`event` 派发同名 `CustomEvent`。
- 业务侧只监听 `window.addEventListener(eventType, handler)`，不直接改写 `receiveRNData`，
  避免互相覆盖。
- 注入函数的类型声明补到 `src/types/global.d.ts`（现有内容只有 `__BUILD_TIME__`，
  新增 `Window` 接口需写在 `declare global { }` 内），见 `templates/native-capabilities.md` §5。
- 注意本项目入口是 `StrictMode`，任何在 effect 里做的桥接注册都会双跑，必须幂等；
  优先放在 `setupApp()` 这种模块级一次性初始化中。

### 7. 生命周期 / 战区 / 键盘（按需）

- **前后台**：`appLifecycleChange` 是唯一有版本号的 Bridge（`__APP_LIFECYCLE_BRIDGE_VERSION__ === 1`）。
  消费必须三件齐全：首次读 `__APP_LIFECYCLE_STATE__` 快照 → 监听 `appLifecycleChange`
  → 用 `sequence` 去重。只在需要「回前台刷新数据 / 暂停轮询」时才接。
- **战区**：新 H5 优先读 `__APP_CONTEXT__.zoneOwnerInfo`；只有要和 operation-h5 共用战区
  选择器时才复用 `localStorage['common-select-store']` + `appZoneChanged` 这套兼容协议。
  战区切换 App 会重建 WebView，不要指望页面状态还在。
- **键盘**：`__APP_REGISTER_KEYBOARD_LISTENER__(cb)` **只有注册没有注销**，
  必须在根组件注册一次后经自己的事件总线分发，不能在组件里反复注册。

## 本地调试

浏览器里拿不到 App 注入数据，用参考项目的「粘贴上下文」方案复现免登链路：

- 真机/模拟器控制台里复制 `[appBridge] 读取 window.__APP_CONTEXT__ =>` 后面的 JSON。
- 悬浮按钮把 JSON 存进 `sessionStorage.__debug_app_context__` 并置 `from_app_flag`，
  刷新后写回 `window.__APP_CONTEXT__`，走的是完全真实的免登链路。
- 该按钮在**真机 App WebView 内必须不显示**（用上文 `isRealAppWebView` 判定），
  浏览器下（含生产域名）可显示，便于线上排查。
- 完整实现可参考 `busyming-store-information-h5/src/utils/debugAppContext.ts`（纯 DOM），
  但必须按本项目已冻结的上下文映射裁剪；本项目的 `src/pages/devtool/` 已删除，不要重建 demo 页。

## 避坑清单

**认证类**

- 三类 Token 混用 → 401 或验签失败。统一门户接口传 `__APP_TOKEN__`、
  或反过来，都是常见事故；别给它们共用一个 `token` 变量名。
- 以为拿到 `accessToken` + `deviceInfo` 就能过 MSE → 上下文不下发 Secret 与
  `X-Operate-Info`，验签仍要 H5 自己做。
- 把生产 `APP_SECRET` 打进浏览器包 / 提交进仓库 → 走云效注入。
- 把 token 拼进 URL、分享链接，或上报到日志 / 埋点 / ARMS / 截图。
- 账号切换后复用上一个用户的 token、用户信息、战区、本地缓存。
- 一般网络异常就调 `__APP_GO_LOGIN__()` → 会清掉整个 App 的登录态。
- 只处理 HTTP 401，忽略 HTTP 200 + 业务码 `401` / `'401'` → 网关实际的 token 过期响应无恢复路径。
- 业务码 401 先于 `rawResponse` 处理 → 破坏调用方明确要求原样包体的契约。
- 并发 401 每个都弹框或调 Bridge → 重复导航；使用单实例引导标志收敛。

**上下文与环境**

- 照抄参考项目的 `unifiedTokenResp.data.accessToken` → 公共形态里根本没这个路径。
- 用 `__APP_CONTEXT__` 判断是否在 App 内 → 调试注入会误判，只能用注入函数判定。
- 用 User-Agent 判环境，或假设所有 App 版本 Bridge 一致 → 必须逐能力探测。
- 把 `__APP_STATUS_BAR_HEIGHT__` 当 number 直接参与运算 → 它是数字字符串，要 `Number()`。
- 把 `deviceInfo.platform` 判成 `'ANDROID'` → 实际是 `'AND'`。
- 上下文缺失时永久 Loading → 应给「请在最新版门店运营 App 内重新打开」这类明确提示。
- 免登在渲染后异步做 → 会先闪一下未登录态甚至误跳授权页，必须渲染前同步消费。
- 来自 App 但读不到上下文 → 仍要标记「鉴权流程结束」并跳过授权跳转，
  由请求层统一提示，不能放任它跳企微 OAuth2（App 内跳转会白屏）。

**调用与回调**

- 旧协议回调用 `if (value)` 判断 → App 回传的是字符串 `'true'` / `'false'`，`'false'` 是真值。
- `await __APP_DOCUMENT_VIEW__()` → 它声明 Promise 但永不 settle，页面会永挂。
- 桥接参数传对象 / 不带 requestId → 回调无法配对，并发调用会串。
- 原生调用不设超时 → 用户取消后页面 loading 永不结束（签名内部 5 分钟超时且不 reject）。
- 覆盖 `receiveRNData` 不链式调用旧实现 → 其他模块的回调静默丢失。
- 自行生成 `callbackId` 或直接调 App 内部 `action` → 走封装好的 `__APP_*`。
- 同一次用户操作同时发起新旧两套媒体协议 → 重复拉起原生页。
- 依赖 `__APP_OPEN_NEW_WINDOW__` 的导航栏参数 → App 侧拼写不一致，当前不是稳定能力；
  需要原生栏在新页加载后调 `__OPEN_APP_WEBVIEW__`。
- 依赖 `__APP_OPEN_FILE_PICKER__` 的 `dir: true` → 回调链不完整。

**样式与交互**

- 在 App 内依赖 `env(safe-area-inset-*)` → 取不到值，顶部内容被状态栏遮挡。
- 返回按钮直接调 `__APP_ROUTER_BACK__` → 多级页面一键退出到 App。
- 用 `__APP_OPEN_NEW_WINDOW__` 做 H5 内部跳转 → 状态丢失、返回栈变深、iOS 白屏。

## 验证

- 静态：`pnpm lint`（本项目确定性验证命令，见 `.ai/config.md`）。
- 真机自检（App 内打开 H5）：
  1. 首屏无未登录闪烁、无授权跳转，接口带上正确 `authorization`；
  2. WebView 内刷新页面后接口仍鉴权成功（验证兜底水合 / URL 参数保留）；
  3. 顶部不被状态栏遮挡、底部按钮不被 home indicator 压住，横竖屏切换后仍正确；
  4. 入口页点返回退回 App，二级页点返回回到上一级 H5 页面；
  5. 调起相机/相册后取消，页面 loading 正常结束、无卡死；
  6. 控制台打印一次 `__APP_CONTEXT__`，确认形态（`unifiedPortal` 还是 `unifiedTokenResp`）
     与实际字段，据此裁剪模板；
  7. iOS 与 Android 各跑一遍（权限行为、`platform` 口径、键盘高度都不同）；
  8. App 内切换账号 / 切换战区后重新进入，确认没有上一个用户的残留数据；
  9. 弱网 / 断网 / 加载失败有明确提示而非白屏。
- 浏览器自检：无任何注入函数时，上述能力全部走兜底分支且不报错。
