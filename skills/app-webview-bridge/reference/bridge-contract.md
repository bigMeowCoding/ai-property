# App ↔ H5 桥接契约（参考项目实测）

来源：`busyming-store-information-h5` 的历史定制接入（运营 App 内嵌）。
以下仅描述该旧项目当时真机跑通的行为。新接入不得把本文件当成当前公共 Bridge 契约。

> **本文件是「某个已接入 H5 的实测切片」，不是 App 侧完整口径。**
> App 侧权威接入指南（基线 `feature/cwc_2.1.5`、提交 `34310b6`）见
> [app-bridge-api.md](app-bridge-api.md)。两者冲突时**以 App 侧口径为准**，
> 差异见本文件 §8。

## 0. 该旧项目的同步注入时机

该旧项目依赖 `injectedJavaScriptBeforeContentLoaded` 注入同步对象，因此：

- H5 的**第一行 JS** 执行时，注入的全局已经存在，可以同步读，不需要轮询等待。
- 注入只在 WebView 加载文档前发生一次；SPA 内部路由跳转不会重新注入，
  但 WebView 内 `location.reload()` 会重新注入。
- URL 上会带 `fromApp=operationApp` 作为来源标识。

这些保证不适用于当前公共异步上下文桥。新 H5 应等待 `__APP_GET_CONTEXT__`，桥晚到时监听
`app-context-bridge-ready`，详见权威文档第一部分。

## 1. 免登上下文 `window.__APP_CONTEXT__`（参考项目形态）

App 在跳转前已经完成统一门户登录，把结果整体注入，H5 消费后直接进入已登录态，
跳过自身的 OAuth2 / URL token 流程。**后续接口的验签（MSE）仍由 H5 自己逐请求做。**

⚠️ 下面的字段结构是 **App 侧为该 H5 定制的「路由专用 `appContext`」**（`WebViewScreen`
的 `route.params.appContext`），**不等于新 H5 通过异步桥拿到的公共五组上下文**
（`unifiedPortal` / `personnel` / `portalAuthObj` / `deviceInfo` / `zoneOwnerInfo`，
见 app-bridge-api.md 第一部分 2 与第二部分 8）。
`busyming-store-opening-h5` 已根据真机口径冻结为混合形态：登录信息读
`unifiedPortal`，设备信息读 `unifiedTokenResp.data.deviceInfo`，字段不存在时兼容顶层
`deviceInfo`，并消费 `defaultOperateInfo`。其他新 H5 仍必须真机确认自己拿到的形态，
不得直接照抄本项目或参考项目的映射。

字段结构（参考实现 `src/utils/appBridge.ts`）：

```ts
interface AppContext {
  /** /third-part-info/find-unified-token 的完整返回 */
  unifiedTokenResp?: {
    data?: {
      /** 统一门户登录 token */
      accessToken?: string
      /** 设备信息，用于 x-Device-Info 头 / 验签 */
      deviceInfo?: Record<string, any> | string | null
      [key: string]: any
    }
    [key: string]: any
  } | null
  /** X-Operate-Info 默认值（对象，H5 负责 stringify） */
  defaultOperateInfo?: Record<string, any> | string | null
  /** /tree/by/app/id 的返回，供页面按需选取 resource 节点 */
  operateTree?: any
  /** 战区负责人 id / code */
  zoneUserId?: string | number | null
  zoneUserCode?: string | number | null
  /** 当前所选战区完整信息 */
  selectedZoneInfo?: Record<string, any> | null
  /** 点击进入时所选门店 item */
  selectStoreInfo?: Record<string, any> | null
  [key: string]: any
}
```

消费规则：

1. `token = unifiedTokenResp.data.accessToken`，为空时**仍视为「来自 App」**，
   只标记鉴权流程结束，不跳授权页，由请求层兜底提示。
2. 数值型 id（`zoneUserId` / `zoneUserCode`）统一 `String()` 归一，页面不再各自转换。
3. App 与 H5 的字段口径差异在**写入 store 前一次性映射**，不要下沉到业务页面。
   实测案例：App 传 `selectStoreInfo.avatarType`（`red` / `yellow`），
   H5 内部统一用 `storeBrand`（`ZYM` / `LSHM`）。
4. 写入时必须清除「上一个用户的派生缓存」（参考实现清 `empNo`），
   否则持久化 store 会让新用户命中旧数据。
5. 排错只记录字段是否存在、权限数组长度和脱敏错误码；不打印原始上下文、Token、用户资料或
   资源树。旧项目若仍保留完整日志，应先移除或做严格脱敏。

「来自 App」判定：

```ts
const fromApp = new URLSearchParams(window.location.search).get('fromApp')
// 命中后写 sessionStorage，SPA 跳转 / 参数被清理后仍可判定
if (fromApp === 'operationApp') sessionStorage.setItem('from_app_flag', '1')
```

请求层兜底（参考实现 `src/utils/request.ts` 请求拦截器首行调用
`rehydrateAppContextIfNeeded()`）：

- 触发条件：来自 App 且 store 里 `token` 或 `deviceInfo` 缺失。
- 只从 `window.__APP_CONTEXT__` 补 `token` / `deviceInfo`，
  **刻意不重置** `operateInfo` / `operateTree` / `zoneUserId` —— 这些可能已被页面覆盖。
- 完整刷新场景由入口初始化负责，两者职责不重叠。

## 2. 安全区

```ts
window.__APP_GET_SAFE_AREA__?: () => string | { top?: number; bottom?: number; left?: number; right?: number }
window.__APP_STATUS_BAR_HEIGHT__?: number | string
window.onReactNativeSafeAreaInsetsChange?: (insets: RawInsets) => void  // 由 H5 赋值，App 调用
```

- `__APP_GET_SAFE_AREA__()` 的返回**可能是 JSON 字符串也可能是对象**，两种都要兼容。
- 解析失败或函数不存在时退化为只用 `__APP_STATUS_BAR_HEIGHT__` 作为 `top`。
- 两者都拿不到即判定为纯浏览器，不写 CSS 变量，沿用样式里的 `env(safe-area-inset-*)` 默认值。
- 数值校验：只接受 `Number.isFinite(n) && n >= 0` 的值，避免 App 传 `-1`/`null` 把布局顶坏。
- `onReactNativeSafeAreaInsetsChange` 由 H5 挂到 window，App 在安全区变化（如旋转）时回调，
  H5 收到后更新 CSS 变量并通知订阅者。
- 参考实现 `src/utils/safeArea.ts`：写 `:root` 的 `--app-safe-top` / `--app-safe-bottom`，
  另外暴露 `getSafeAreaInsets()` 与 `subscribeSafeArea(cb)` 供需要数值的场景使用。

## 3. 返回 / 关闭 WebView

```ts
window.__APP_ROUTER_BACK__?: () => void   // 关闭 WebView，回到 App 页面
```

参考实现 `src/hooks/useAppBack.ts` 的三级决策：

| 条件 | 行为 |
|---|---|
| `window.history.state?.idx > 0`（本会话内有 push） | `navigate(-1)` |
| 无路由栈且存在 `__APP_ROUTER_BACK__` | 调它关闭 WebView |
| 纯浏览器 | `navigate(-1)` 兜底 |

`idx` 由 react-router 的 `createBrowserRouter` 维护，是「本会话是否有可返回历史」的可靠依据。

## 4. 原生能力调用（请求-回调模型）

注入函数与回调事件的对应关系（参考实现 `src/hooks/useAppCameraBridge.ts`）：

| 类型 | 注入函数 | 回调 eventType |
|---|---|---|
| 拍照 | `__APP_GO_TO_CAMERA__` | `cameraCallback` |
| 相册 | `__APP_OPEN_PICKER__` | `pickerCallback` |
| 录像 | `__APP_OPEN_TRANSCRIBE__` | `transcribeCallback` |

发起：

```ts
const reqId = `${Date.now()}_${Math.random().toString(36).slice(2, 9)}`
const argStr = JSON.stringify({ ...params, __requestId: reqId })
const fn = window[bridgeName]

if (typeof fn === 'function') fn(argStr)
else window[bridgeName] = argStr        // 少数 App 版本用「赋值」而非「调用」传参
```

回调配对（三级降级，缺一不可）：

1. `payload.__requestId` / `requestId` / `request_id` 命中在途记录 → 精确配对；
2. 否则按 `payload.eventType` / `event` 找同类型的在途记录；
3. 否则若只有一个在途调用 → 直接兑现它。

其他约束：

- 超时 10s，超时后删除在途记录并以 `{ success: false, error: 'xx响应超时' }` 兑现。
- 桥不存在时立即返回 `{ success: false, error: 'xx功能不可用' }`。
- 在途记录用模块级 `Map` 存放（跨组件实例共享），不要放进组件 state。

## 5. App → H5 统一入口 `receiveRNData`

```ts
window.receiveRNData = (payload: string | object) => boolean
```

App 侧所有回传都调这个函数。参考实现（`src/App.tsx` 模块顶层，非组件内）做四件事：

1. 幂等安装：`window.__APP_RECEIVE_INSTALLED__` 标记，避免 HMR / 多次执行重复包装；
2. 保存旧的 `receiveRNData` 并在最后链式调用，不吞掉其他模块的监听；
3. payload 是字符串时 `JSON.parse`，失败则原样透传；
4. 按 `payload.eventType || payload.event` 派发同名 `CustomEvent(detail: parsed)`，
   业务侧只用 `window.addEventListener(eventType, handler)` 消费。

安装位置必须早于任何业务监听，且不能放在 React 组件的 effect 里（StrictMode 会双跑，
且组件卸载后会摘掉全局能力）。

## 6. 本地调试（模拟注入）

参考实现 `src/utils/debugAppContext.ts`（纯 DOM，可整文件拷贝）：

- `sessionStorage.__debug_app_context__` 只存人工构造的脱敏 Mock JSON；
- `applyDebugAppContext()` 在免登初始化**之前**把它写回 `window.__APP_CONTEXT__`
  并置 `from_app_flag='1'`，使后续链路与真机完全一致；
- 只在「非真机 App WebView」环境挂载悬浮按钮，判定依据是注入函数是否存在
  （`__APP_ROUTER_BACK__` / `__APP_GET_SAFE_AREA__` / `__APP_STATUS_BAR_HEIGHT__`），
  **不能用 `__APP_CONTEXT__` 判定**，因为它自己就会注入这个字段；
- JSON 非法时提示解析错误并清掉缓存，不要静默失败。不要从真机复制真实 Token、用户资料或
  完整资源树到浏览器、源码、文档和截图。

## 7. 相关但不同源：微信小程序 WebView

`src/utils/miniProgramBridge.ts` 走的是 `wx.miniProgram`（`weixin-js-sdk`）而非 App 注入：
`getEnv` 判环境（失败时退化用 UA 里的 `micromessenger` + `miniprogram`）、
`navigateTo` 跳小程序页面。本项目已有 `src/helpers/wxMiniHelper.ts` 承担同类职责，
与 App 桥接属于两条独立链路，不要混在同一模块里。

## 8. 与 App 侧公共口径的已知差异

参考项目跑通的行为不等于 App 侧默认行为。已确认的差异：

| 主题 | 参考项目实测 | App 侧公共口径（app-bridge-api.md） |
|---|---|---|
| 上下文形态 | `unifiedTokenResp.data.accessToken` 等定制同步字段 | `__APP_GET_CONTEXT__()` 异步返回 `unifiedPortal` / `personnel` / `portalAuthObj` / `deviceInfo` / `zoneOwnerInfo` 五组 |
| 环境判定 | URL 的 `fromApp=operationApp` + 注入函数探测 | `__BUSYMING_OPERATION_APP__ === true` + `ReactNativeWebView.postMessage` |
| 业务 Token | 未使用 | 另有 `__APP_TOKEN__`（App 主登录）与 `__APP_GET_TOKEN_AUTHINFO__`（人资中台），与统一门户 Token 三者不可互换 |
| 相机 / 相册 / 录像 | 事件流旧协议 + `receiveRNData`，带项目自定义配对封装 | 已提供 `__APP_*_WITH_RESULT__` Promise 新协议，新 H5 优先用它；旧协议按 `uuid`/`key` 与真实事件处理，不把自定义 `__requestId` 当公共保证 |
| 安全区 | `__APP_GET_SAFE_AREA__` 返回字符串或对象都兼容 | 声明为 JSON 字符串；`__APP_STATUS_BAR_HEIGHT__` 是数字字符串 |

参考项目未涉及、但 App 已提供的能力（导航、权限、扫码、定位、文件预览、签名、
键盘、生命周期、战区同步、报告分享等），一律查 [app-bridge-api.md](app-bridge-api.md)，
不要按本文件的模式自行推测。
