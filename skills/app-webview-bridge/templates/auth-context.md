# 模板：App 免登上下文（appBridge）

拷贝到 `src/helpers/appBridge.ts` 后按实际字段裁剪。
本项目入口已定为 App 内嵌免登（注入 `__APP_CONTEXT__`）+ URL 参数 `authToken` 兜底，
接入前要确认的是 **App 侧实际下发的字段**（以真机控制台打印的 `__APP_CONTEXT__` 为准）。

`__APP_CONTEXT__` 有两种形态，模板已同时兼容（见 `readAuthFromContext`）：

- **形态 A（App 公共默认，新 H5 大概率是这种）**：
  `{ unifiedPortal: { accessToken, userInfo }, deviceInfo, zoneOwnerInfo }`；
- **形态 B（路由专用 `appContext`，参考项目是这种）**：
  `{ unifiedTokenResp: { data: { accessToken, deviceInfo, ... } }, ... }`。

真机确认属于哪种后，删掉另一种的声明与分支，不要长期保留双形态。
口径细节见 [app-bridge-api.md](../reference/app-bridge-api.md) §4。

```ts
/**
 * App 免登上下文桥接。
 *
 * 背景：App 跳转到本 H5 时（URL 带 fromApp=operationApp），会在 WebView 加载文档前
 * 通过 injectedJavaScriptBeforeContentLoaded 把统一门户的登录结果注入
 * window.__APP_CONTEXT__。H5 在渲染前同步消费这份上下文直接完成登录。
 */

import { useGlobalState } from '@/store'
import { logFormat } from '@/utils/common'

/** App 来源标识：URL 上 fromApp 的取值 */
export const FROM_APP_FLAG = 'operationApp'

/** sessionStorage key：记录「本会话来自 App」，SPA 内跳转 / 刷新后仍可判定 */
const FROM_APP_STORAGE_KEY = 'from_app_flag'

/** App 注入到 window 上的全局对象 key */
const APP_CONTEXT_KEY = '__APP_CONTEXT__'

/** 统一门户 token 接口返回的 data（仅声明 H5 关心的字段） */
export interface UnifiedTokenData {
  /** 统一门户登录 token */
  accessToken?: string;
  /** 设备信息，部分网关用于 x-Device-Info 头 / 验签 */
  deviceInfo?: Record<string, any> | string | null;
  [key: string]: any;
}

/** App 注入的上下文结构：真机确认形态后裁掉不用的那一支 */
export interface AppContext {
  /** 形态 A：App 公共默认注入的统一门户登录结果 */
  unifiedPortal?: { accessToken?: string; userInfo?: Record<string, any> } | null;
  /** 形态 A：设备信息，获取失败时 App 传 null；platform 安卓值为 'AND' 而非 'ANDROID' */
  deviceInfo?: Record<string, any> | null;
  /** 形态 A：战区负责人与所选战区 */
  zoneOwnerInfo?: {
    zoneUserId?: string | null;
    zoneUserCode?: string | null;
    selectedZoneInfo?: Record<string, any> | null;
  } | null;
  /** 形态 B：路由专用 appContext 里的统一门户 token 接口返回 */
  unifiedTokenResp?: { data?: UnifiedTokenData; [key: string]: any } | null;
  /** 点击进入时所选门店信息 */
  selectStoreInfo?: Record<string, any> | null;
  [key: string]: any;
}

/**
 * 兼容两种上下文形态读取鉴权信息。
 * 只在这一个函数里做形态判断，业务与请求层都不感知差异。
 */
export const readAuthFromContext = (ctx: AppContext | null) => {
  const legacy = ctx?.unifiedTokenResp?.data

  return {
    token: ctx?.unifiedPortal?.accessToken || legacy?.accessToken || '',
    deviceInfo: ctx?.deviceInfo ?? legacy?.deviceInfo ?? null,
    userInfo: ctx?.unifiedPortal?.userInfo ?? legacy ?? null
  }
}

/** 读取 App 注入的上下文，未注入返回 null */
export const getAppContext = (): AppContext | null => {
  try {
    const ctx = (window as any)[APP_CONTEXT_KEY]

    if (ctx && typeof ctx === 'object') return ctx as AppContext
  } catch (error) {
    logFormat({
      tip: '[appBridge] 读取 window.__APP_CONTEXT__ 失败',
      style: 'color: white; background: red;',
      data: error
    })
  }

  return null
}

/**
 * 是否来自 App。
 * 优先看 URL 的 fromApp，命中后写 sessionStorage，
 * 之后 SPA 内跳转或刷新（URL 参数可能已被清理）仍可判定。
 */
export const isFromApp = (): boolean => {
  try {
    const fromApp = new URLSearchParams(window.location.search).get('fromApp')

    if (fromApp === FROM_APP_FLAG) {
      sessionStorage.setItem(FROM_APP_STORAGE_KEY, '1')

      return true
    }

    return sessionStorage.getItem(FROM_APP_STORAGE_KEY) === '1'
  } catch {
    return false
  }
}

/**
 * 把 App 上下文写入 store。
 * 字段口径差异（如 App 的 avatarType 与 H5 的 storeBrand）在这里一次性映射，
 * 不要下沉到业务页面各自适配。
 * @returns 是否解析出可用 token
 */
const hydrateFromContext = (ctx: AppContext): boolean => {
  const { token, userInfo } = readAuthFromContext(ctx)
  const data = (userInfo || {}) as UnifiedTokenData

  logFormat({
    tip: '[appBridge] window.__APP_CONTEXT__ 原始数据',
    style: 'color: #fff; background: #000;',
    data: ctx
  })

  useGlobalState.getState().setAuthToken(token)

  // 切换用户时要覆盖掉上一个用户的信息，否则持久化 store 会让新用户命中旧数据
  useGlobalState.getState().setCurrentUserInfo({
    userId: data.userId ?? '',
    userName: data.userName ?? '',
    isGrayUser: data.isGrayUser === true || data.isGrayUser === 'true'
  })

  logFormat({
    tip: '[appBridge] 写入后 store 当前值',
    style: 'color: #fff; background: #000;',
    data: {
      authToken: useGlobalState.getState().authToken,
      userInfo: useGlobalState.getState().userInfo
    }
  })

  return !!token
}

/**
 * App 免登初始化：必须在 createRoot 之前同步调用（本项目放 setupApp 内）。
 * @returns true 表示本次由 App 完成免登，调用方应跳过 URL 参数 / 授权跳转分支
 */
export const initAppContext = (): boolean => {
  if (!isFromApp()) return false

  const ctx = getAppContext()

  // 来自 App 但读不到上下文：仍然短路授权跳转（App 内跳授权页会白屏），
  // token 为空由请求层统一提示
  if (!ctx) {
    logFormat({
      tip: '[appBridge] 来自 App 但未读到 window.__APP_CONTEXT__',
      style: 'color: white; background: red;',
      data: window.location.href
    })

    return true
  }

  hydrateFromContext(ctx)

  return true
}

/**
 * 请求层兜底：来自 App 但 store 里 token 缺失（WebView 刷新、持久化被清空）时，
 * 只从 window 补回鉴权必需项。
 *
 * 刻意不整包重水合业务上下文 —— 页面可能已经改过这些值，整包覆盖会把页面的修改打回默认值。
 * @returns 当前是否已具备可用 token
 */
export const rehydrateAppContextIfNeeded = (): boolean => {
  const { authToken } = useGlobalState.getState()

  if (authToken) return true
  if (!isFromApp()) return false

  const { token } = readAuthFromContext(getAppContext())

  if (!token) return false

  useGlobalState.getState().setAuthToken(token)

  return true
}
```

## 接入点

`src/helpers/setupApp.ts`：

```ts
const setupApp = () => {
  initArms()
  initVConsoleHandler()

  // App 免登优先：命中则跳过 URL 参数分支
  if (!initAppContext()) initGlobalState()
}
```

`src/utils/request.ts` 请求拦截器首行：

```ts
instance.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  rehydrateAppContextIfNeeded()

  const authToken = resolveAuthToken()
  // ...
})
```

## 登录失效响应

请求层要把 HTTP 401 和 HTTP 200 + 业务码 `401` / `'401'` 收敛到同一入口：

```ts
function rejectUnauthorized(options: RequestErrorOptions): Promise<never> {
  useGlobalState.getState().clearToken()
  showReLoginDialog()

  return Promise.reject(new RequestError(options))
}

// 成功响应分支：rawResponse 必须优先，保持原样透传契约
if (requestConfig.rawResponse) return Promise.resolve(response.data)

if (Number(response.data?.code) === 401) {
  return rejectUnauthorized({
    code: response.data.code,
    message: pickBizMessage(response.data),
    httpStatus: response.status,
    payload: response.data
  })
}

// Axios 错误分支
if (error.response?.status === 401) {
  return rejectUnauthorized({
    code: 401,
    message: HttpStatusMessage[401],
    httpStatus: 401,
    payload: error.response.data
  })
}
```

恢复引导使用模块级标志收敛并发 401；`hideErrorMessage` 不抑制该引导。
用户确认后按以下顺序降级：

```ts
if (typeof window.__APP_GO_LOGIN__ === 'function') {
  window.__APP_GO_LOGIN__()
} else if (isWxMini) {
  wxMiniSwitchTab('/pages/home/index')
} else if (isDev) {
  window.location.replace(withAppBase('/no-auth'))
}
```

`__APP_GO_LOGIN__` 会清理整个 App 登录态，只允许明确鉴权失效时调用；普通网络异常、
HTTP 5xx、业务校验失败不得触发。在 `src/types/global.d.ts` 声明：

```ts
interface Window {
  __APP_GO_LOGIN__?: () => void
}
```

## 注意

- **这里拿到的是统一门户 Token**，只用于统一门户 / 统一网关接口。App 主登录 Token 在
  `window.__APP_TOKEN__`，人资中台 TokenInfo 要 `await __APP_GET_TOKEN_AUTHINFO__()`，
  三者不可互换，也不要共用一个 `token` 变量名。
- `deviceInfo` 只是设备信息，**不等于具备 MSE 验签能力**。上下文不下发 App Secret、
  默认 `X-Operate-Info`、资源树和 `permissionCode`，验签仍由 H5 自己按本项目方案做
  （KEY/SECRET 走云效流水线注入，不写进仓库）。
- 上下文缺失时不要永久 Loading，给「请在最新版门店运营 App 内重新打开」这类明确提示。
- 三段调试日志只在开发 / 测试环境打，**不要把完整上下文上报 ARMS 或埋点**，
  也不要把 `accessToken` 拼进 URL 或持久化到长期 `localStorage`。
- 统一门户 Token 刷新或战区切换时 App 会**重建 WebView**，页面内存状态不会保留；
  相反，App 主 Token 变化不重建 WebView，需要时可注册
  `window.onAppToken = token => { /* 更新业务 token */ }`。
- 账号切换后必须清掉上一个用户的派生缓存（持久化 store、按 `empNo` 的本地缓存等）。
