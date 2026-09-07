# 模板：原生能力（安全区 / 返回 / 相机相册 / App 回传）

四项与登录态无耦合，可独立接入。代码风格已对齐本项目 ESLint（无分号、单引号）。

## 1. 安全区 → `src/helpers/safeArea.ts`

```ts
/**
 * 安全区（刘海屏 / 状态栏 / 底部 home indicator）适配。
 *
 * 纯浏览器可用 CSS env(safe-area-inset-*)，但 App（RN WebView）内 env() 取不到值，
 * 必须用 App 注入的：
 *  - window.__APP_GET_SAFE_AREA__()  -> JSON 字符串或对象 { top, bottom, left, right }
 *  - window.__APP_STATUS_BAR_HEIGHT__ -> 仅顶部的退化值
 *  - window.onReactNativeSafeAreaInsetsChange(insets) -> App 实时回传（旋转等）
 *
 * 结果写入 :root 的 CSS 变量，页面统一用 var(--app-safe-top) / var(--app-safe-bottom) 消费。
 */

export interface SafeAreaInsets {
  top: number;
  bottom: number;
}

type RawInsets = {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
}

const TOP_VAR = '--app-safe-top'
const BOTTOM_VAR = '--app-safe-bottom'

let current: SafeAreaInsets = { top: 0, bottom: 0 }
let initialized = false
const listeners = new Set<(insets: SafeAreaInsets) => void>()

/** 只接受有限非负数，避免 App 传 -1 / null 把布局顶坏 */
const toNumber = (value: unknown): number | undefined => {
  const n = typeof value === 'string' ? Number(value) : (value as number)

  return Number.isFinite(n) && n >= 0 ? n : undefined
}

/** 读取 App 注入的安全区；纯浏览器返回 null */
const readInjectedInsets = (): RawInsets | null => {
  const w = window as unknown as {
    __APP_GET_SAFE_AREA__?: () => string | RawInsets;
    __APP_STATUS_BAR_HEIGHT__?: number | string;
  }

  try {
    if (typeof w.__APP_GET_SAFE_AREA__ === 'function') {
      const raw = w.__APP_GET_SAFE_AREA__()
      const insets = typeof raw === 'string' ? JSON.parse(raw) : raw

      if (insets && typeof insets === 'object') return insets as RawInsets
    }
  } catch {
    /* 解析失败走下面的退化逻辑 */
  }

  const top = toNumber(w.__APP_STATUS_BAR_HEIGHT__)

  if (top !== undefined) return { top }

  return null
}

const applyInsets = (raw: RawInsets) => {
  const root = document.documentElement
  const top = toNumber(raw.top)
  const bottom = toNumber(raw.bottom)

  if (top !== undefined) {
    root.style.setProperty(TOP_VAR, `${top}px`)
    current = { ...current, top }
  }

  if (bottom !== undefined) {
    root.style.setProperty(BOTTOM_VAR, `${bottom}px`)
    current = { ...current, bottom }
  }

  listeners.forEach((cb) => cb(current))
}

/**
 * 初始化安全区（在 setupApp 里调用一次）。
 * 纯浏览器不覆盖 CSS 变量，沿用样式里的 env(safe-area-inset-*) 默认值。
 */
export const initSafeArea = (): void => {
  if (initialized) return
  initialized = true

  const insets = readInjectedInsets()

  if (insets) applyInsets(insets)

  // App 在安全区变化（如旋转）时回调
  ;(window as unknown as {
    onReactNativeSafeAreaInsetsChange?: (i: RawInsets) => void
  }).onReactNativeSafeAreaInsetsChange = (next: RawInsets) => {
    if (next && typeof next === 'object') applyInsets(next)
  }
}

/** 获取当前安全区数值（px） */
export const getSafeAreaInsets = (): SafeAreaInsets => current

/** 订阅安全区变化，返回取消订阅函数 */
export const subscribeSafeArea = (cb: (insets: SafeAreaInsets) => void): (() => void) => {
  listeners.add(cb)

  return () => listeners.delete(cb)
}
```

配套样式（`src/styles/index.scss`）：

```scss
:root {
  --app-safe-top: env(safe-area-inset-top, 0px);
  --app-safe-bottom: env(safe-area-inset-bottom, 0px);
}
```

## 2. 返回 → `src/hooks/useAppBack.ts`

```ts
import { useCallback } from 'react'

import { useNavigate } from 'react-router-dom'

/**
 * 通用返回（App 内嵌感知）。
 *
 * - H5 本会话内有过 push → 返回上一页；
 * - 无路由栈（App 跳入的入口页）→ 调 window.__APP_ROUTER_BACK__() 关闭 WebView 回到 App；
 * - 纯浏览器无桥 → navigate(-1) 兜底。
 *
 * 判定依据：react-router 的 createBrowserRouter 在 window.history.state.idx 维护栈索引，
 * idx > 0 表示本会话内有可返回的历史。顺序不能反 —— 直接调 App back 会关掉整个 WebView，
 * 丢掉 H5 内部的多级历史。
 */
export function useAppBack(): () => void {
  const navigate = useNavigate()

  return useCallback(() => {
    const idx = (window.history.state?.idx as number | undefined) ?? 0

    if (idx > 0) {
      navigate(-1)

      return
    }

    const appBack = (window as unknown as {
      __APP_ROUTER_BACK__?: () => void
    }).__APP_ROUTER_BACK__

    if (typeof appBack === 'function') {
      appBack()

      return
    }

    navigate(-1)
  }, [ navigate ])
}

export default useAppBack
```

## 3. 原生能力调用 → `src/hooks/useAppBridgeCall.ts`

```ts
import { useEffect, useState } from 'react'

/**
 * App 原生能力调用（请求-回调模型）。
 *
 * 发起：调 App 注入的函数并传 JSON 字符串（含 __requestId）；
 * 回调：App 调 window.receiveRNData，由 installAppMessageReceiver 转成同名 CustomEvent。
 */

export enum AppBridgeTypeEnum {
  CAMERA = 'camera',
  ALBUM = 'album',
  VIDEO = 'video'
}

/** 类型 → 注入函数名 */
const BRIDGE_NAME_MAP: Record<AppBridgeTypeEnum, string> = {
  [AppBridgeTypeEnum.CAMERA]: '__APP_GO_TO_CAMERA__',
  [AppBridgeTypeEnum.ALBUM]: '__APP_OPEN_PICKER__',
  [AppBridgeTypeEnum.VIDEO]: '__APP_OPEN_TRANSCRIBE__'
}

/** 类型 → App 回调的 eventType */
const CALLBACK_EVENT_MAP: Record<AppBridgeTypeEnum, string> = {
  [AppBridgeTypeEnum.CAMERA]: 'cameraCallback',
  [AppBridgeTypeEnum.ALBUM]: 'pickerCallback',
  [AppBridgeTypeEnum.VIDEO]: 'transcribeCallback'
}

/** 类型 → 文案 */
const LANG_MAP: Record<AppBridgeTypeEnum, string> = {
  [AppBridgeTypeEnum.CAMERA]: '相机',
  [AppBridgeTypeEnum.ALBUM]: '相册',
  [AppBridgeTypeEnum.VIDEO]: '视频'
}

interface CallBridgeResult {
  success: boolean;
  error?: string;
  duration?: number;
  data?: any;
}

interface PendingCall {
  resolve: (res: CallBridgeResult) => void;
  timeoutId: number | null;
  callbackEvent: string;
}

/** 在途调用必须放模块级 Map（跨组件实例共享），不能放组件 state */
const pendingCalls = new Map<string, PendingCall>()

const settle = (id: string, entry: PendingCall, data: any) => {
  pendingCalls.delete(id)

  if (entry.timeoutId) window.clearTimeout(entry.timeoutId)

  entry.resolve({ success: true, data })
}

/** 三级配对降级：requestId → eventType → 唯一在途调用 */
const handleIncoming = (payload: any): boolean => {
  let parsed = payload

  try {
    if (typeof payload === 'string') parsed = JSON.parse(payload)
  } catch {
    parsed = payload
  }

  const reqId = parsed?.__requestId ?? parsed?.requestId ?? parsed?.request_id ?? null

  if (reqId && pendingCalls.has(reqId)) {
    settle(reqId, pendingCalls.get(reqId)!, parsed)

    return true
  }

  const eventType = parsed?.eventType || parsed?.event || null

  if (eventType) {
    const hit = Array.from(pendingCalls.entries())
      .find(([ , entry ]) => entry.callbackEvent === eventType)

    if (hit) {
      settle(hit[0], hit[1], parsed)

      return true
    }
  }

  if (pendingCalls.size === 1) {
    const [ [ id, entry ] ] = Array.from(pendingCalls.entries())

    settle(id, entry, parsed)

    return true
  }

  return false
}

/** 注入的桥可能是函数，也可能是需要赋值的对象 */
const hasBridge = (bridgeName: string): boolean => {
  try {
    const bridge = (window as any)[bridgeName]

    return typeof bridge === 'function' || typeof bridge === 'object'
  } catch {
    return false
  }
}

export function useAppBridgeCall(options: {
  type: AppBridgeTypeEnum;
  timeout?: number;
}) {
  const { type, timeout = 10 * 1000 } = options
  const typeLang = LANG_MAP[type]
  const bridgeName = BRIDGE_NAME_MAP[type]
  const callbackEvent = CALLBACK_EVENT_MAP[type]

  const [ isCalling, setIsCalling ] = useState(false)

  useEffect(() => {
    const handleEvent = (ev: any) => {
      handleIncoming(ev?.detail ?? ev)
      setIsCalling(false)
    }

    window.addEventListener(callbackEvent, handleEvent as EventListener)

    return () => {
      window.removeEventListener(callbackEvent, handleEvent as EventListener)
      setIsCalling(false)
    }
  }, [ callbackEvent ])

  const callBridge = (params: Record<string, any> = {}): Promise<CallBridgeResult> => {
    // 桥不存在（纯浏览器 / 低版本 App）时返回不可用，不抛错
    if (!hasBridge(bridgeName)) {
      return Promise.resolve({ success: false, error: `${typeLang}功能不可用` })
    }

    return new Promise<CallBridgeResult>((resolve) => {
      const start = Date.now()
      const reqId = `${Date.now()}_${Math.random().toString(36).slice(2, 9)}`

      // 必须有超时兜底：用户在原生页面点取消时 App 可能不回调，否则 Promise 永挂
      const timeoutId = window.setTimeout(() => {
        pendingCalls.delete(reqId)
        setIsCalling(false)
        resolve({
          success: false,
          error: `${typeLang}响应超时`,
          duration: Date.now() - start
        })
      }, timeout)

      pendingCalls.set(reqId, { resolve, timeoutId, callbackEvent })
      setIsCalling(true)

      try {
        // 注入函数只接受字符串参数
        const argStr = JSON.stringify({ ...params, __requestId: reqId })
        const bridge = (window as any)[bridgeName]

        if (typeof bridge === 'function') bridge(argStr)
        else (window as any)[bridgeName] = argStr
      } catch (error) {
        pendingCalls.delete(reqId)
        window.clearTimeout(timeoutId)
        setIsCalling(false)
        resolve({
          success: false,
          error: `${typeLang}调用异常`,
          duration: Date.now() - start
        })
      }
    })
  }

  return { isCalling, callBridge }
}

export default useAppBridgeCall
```

## 4. App → H5 消息入口 → `src/helpers/installAppMessageReceiver.ts`

```ts
/**
 * 安装 App 回传数据的统一入口 window.receiveRNData，把 payload 转成同名 CustomEvent，
 * 业务侧只用 window.addEventListener(eventType, handler) 消费。
 *
 * 必须在 setupApp 中模块级安装：放进组件 effect 会被 StrictMode 双跑，
 * 且组件卸载后会摘掉全局能力。
 */

const INSTALLED_FLAG = '__APP_RECEIVE_INSTALLED__'

export const installAppMessageReceiver = (): void => {
  const w = window as any

  // 幂等：HMR / 多次调用不重复包装
  if (w[INSTALLED_FLAG]) return

  // 保留已存在的实现并链式调用，避免吞掉其他模块的回调
  const origin = w.receiveRNData

  w.receiveRNData = (payload: any) => {
    let parsed = payload

    try {
      if (typeof payload === 'string') parsed = JSON.parse(payload)
    } catch {
      parsed = payload
    }

    const eventType = parsed?.eventType || parsed?.event || null

    if (eventType && typeof eventType === 'string') {
      window.dispatchEvent(new CustomEvent(eventType, { detail: parsed }))
    }

    if (typeof origin === 'function') origin(payload)

    return true
  }

  w[INSTALLED_FLAG] = true
}

export default installAppMessageReceiver
```

## 5. 类型声明补充 → `src/types/global.d.ts`

现有文件只有 `declare const __BUILD_TIME__`（无 import/export，属全局脚本），
补充 `Window` 时包在 `declare global` 里可以与之共存：

```ts
declare global {
  interface Window {
    /** App 注入的免登上下文 */
    __APP_CONTEXT__?: Record<string, any>;
    /** 关闭 WebView 返回 App */
    __APP_ROUTER_BACK__?: () => void;
    /** 安全区，返回 JSON 字符串或对象 */
    __APP_GET_SAFE_AREA__?: () => string | Record<string, number>;
    /** 状态栏高度（安全区的退化值） */
    __APP_STATUS_BAR_HEIGHT__?: number | string;
    /** App 回传数据的统一入口 */
    receiveRNData?: (payload: any) => boolean;
    /** 安全区变化回调，由 H5 赋值、App 调用 */
    onReactNativeSafeAreaInsetsChange?: (insets: Record<string, number>) => void;
  }
}

export {}
```

上面只声明了本模板用到的字段。**完整的 window 声明见
[app-bridge-api.md](../reference/app-bridge-api.md) §12**，按本项目实际用到的能力挑选，
不要整段照抄 operation-h5 的旧声明（其中 `__APP_GET_VERSION__` 被写成字符串，实际是
`Promise<string>`）。

## 6. 与 App 侧 Promise 新协议的关系

§3 的「请求-回调」模型对应的是 App 的**事件流旧协议**。App 侧已提供 Promise 新协议，
新接入 H5 优先用后者：

| 能力 | 事件流旧协议（§3 模型） | Promise 新协议（优先） |
|---|---|---|
| 相册 | `__APP_OPEN_PICKER__` + `pickerCallback` | `__APP_OPEN_PICKER_WITH_RESULT__(args)` |
| 拍照 | `__APP_GO_TO_CAMERA__` + `cameraCallback` | `__APP_GO_TO_CAMERA_WITH_RESULT__(args)` |
| 录像 | `__APP_OPEN_TRANSCRIBE__` + `transcribeCallback` | `__APP_OPEN_TRANSCRIBE_WITH_RESULT__(args)` |

新协议直接 `await` 得到 `{ success, data: UploadedFile[], error }`，不需要自己维护在途
`Map`、requestId 配对和三级降级。

仍需要旧协议的情况只有三种：需要上传进度（`onUploadProgressCallback`）、
需要多文件逐条回调、或必须兼容没有新协议的旧 App 版本。此时注意：

- 旧协议的打开状态回调（`onOpenCameraCallback` 等）App 实际回传的是**字符串**
  `'true'` / `'false'`，**禁止 `if (value)`** —— `'false'` 是真值。
- 两套协议不要对同一次用户操作同时发起，否则会重复拉起原生页。

判定顺序：先探 `__APP_*_WITH_RESULT__`，不存在再退旧协议，都不存在退 `<input type="file">`。
