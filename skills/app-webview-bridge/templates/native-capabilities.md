# 模板：常用原生能力

按项目实际使用的部分复制。方法签名和完整类型以
[权威文档附录 A](../reference/app-bridge-api.md) 为准；调用前仍需检测目标安装包中的具体方法。

## 公共调用工具

```ts
export function requireBridge<K extends keyof AppBridgeMethods>(name: K): AppBridgeMethods[K] {
  if (typeof window === 'undefined' || typeof window[name] !== 'function') {
    throw Object.assign(new Error(`当前页面不支持 ${name}`), {
      code: 'BRIDGE_UNAVAILABLE',
    })
  }

  return window[name] as AppBridgeMethods[K]
}

export function withBridgeTimeout<T>(task: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => reject(Object.assign(
      new Error('App 操作等待超时'),
      { code: 'BRIDGE_TIMEOUT' },
    )), timeoutMs)

    task.then(value => {
      window.clearTimeout(timer)
      resolve(value)
    }, error => {
      window.clearTimeout(timer)
      reject(error)
    })
  })
}
```

H5 超时只结束等待，不会关闭原生页面、相机或上传任务。超时后不要自动再次调用交互桥。

## 安全区

`__APP_GET_SAFE_AREA__()` 当前同步返回 JSON 字符串。App 旋转后通过
`onReactNativeSafeAreaInsetsChange` 推送对象；两者都要接。若原生入口已设置
`needSafeArea: true`，避免 H5 再叠加同一边距。

```ts
const SAFE_AREA_VARS = {
  top: '--app-safe-top',
  right: '--app-safe-right',
  bottom: '--app-safe-bottom',
  left: '--app-safe-left',
} as const

function toInset(value: unknown): number | null {
  const number = Number(value)

  return Number.isFinite(number) && number >= 0 ? number : null
}

function applySafeArea(insets: Partial<AppInsets>): void {
  for (const edge of Object.keys(SAFE_AREA_VARS) as Array<keyof AppInsets>) {
    const value = toInset(insets[edge])

    if (value !== null) {
      document.documentElement.style.setProperty(SAFE_AREA_VARS[edge], `${value}px`)
    }
  }
}

export function initAppSafeArea(): void {
  try {
    if (typeof window.__APP_GET_SAFE_AREA__ === 'function') {
      const raw = window.__APP_GET_SAFE_AREA__()
      applySafeArea(JSON.parse(raw) as AppInsets)
    } else if (window.__APP_STATUS_BAR_HEIGHT__ != null) {
      applySafeArea({ top: Number(window.__APP_STATUS_BAR_HEIGHT__) })
    }
  } catch {
    // 保留 CSS env() 默认值，不输出原始 Bridge 数据。
  }

  const previous = window.onReactNativeSafeAreaInsetsChange

  window.onReactNativeSafeAreaInsetsChange = insets => {
    applySafeArea(insets)
    previous?.(insets)
  }
}
```

```css
:root {
  --app-safe-top: env(safe-area-inset-top, 0px);
  --app-safe-right: env(safe-area-inset-right, 0px);
  --app-safe-bottom: env(safe-area-inset-bottom, 0px);
  --app-safe-left: env(safe-area-inset-left, 0px);
}
```

## 返回和导航

`__APP_ROUTER_BACK__()` 已由 App 处理“网页有历史则后退、无历史则交给宿主或关闭原生页”的
顺序。业务不要把它描述成必定关闭 WebView。

```ts
export function goBackFromH5(browserFallback: () => void): void {
  if (typeof window.__APP_ROUTER_BACK__ === 'function') {
    window.__APP_ROUTER_BACK__()
    return
  }

  browserFallback()
}
```

其他导航选择：

- 同一 H5 的列表到详情：使用 H5 Router。
- 回 App 主容器的运营指导工作台：`__APP_GO_HOME_TAB__()`，不接受 Tab 参数。
- 打开独立可信页面：`__APP_OPEN_NEW_WINDOW__(fullHttpsUrl, needSafeArea, needNarBar, narBarTitle)`。
- 修改当前容器顶部栏：`__OPEN_APP_WEBVIEW__(isShowBack, title)`，它不会新开页面。
- 打开工作台抽屉：仅在 `__APP_OPEN_WORKBENCH_DRAWER__` 存在时显示入口。

不要把 Token 放进新页面 URL。新 WebView 不继承当前组件状态、内存缓存或 H5 路由栈，需重新
初始化上下文。

## Promise 媒体协议（新项目优先）

相册、相机和录像由 App 完成选择/拍摄及上传。顶层 `success: true` 仍可能包含单文件失败，
必须逐项检查 `status` 与 `fileUrl`。

```ts
export interface AcceptedMediaResult {
  files: UploadedFile[]
  failed: UploadedFile[]
  cancelled: boolean
}

export function acceptMediaResult(result: MediaBridgeResult): AcceptedMediaResult {
  if (!result.success) {
    if (result.error === 'cancel') {
      return { files: [], failed: [], cancelled: true }
    }

    throw new Error('媒体操作失败，请重试')
  }

  const files = result.data.filter(file => file.status === 'success' && Boolean(file.fileUrl))
  const failed = result.data.filter(file => file.status !== 'success' || !file.fileUrl)

  return { files, failed, cancelled: false }
}

export async function pickPhotos(): Promise<AcceptedMediaResult> {
  // 交互可能包含用户选择和多文件上传，不设置机械的 5 秒/15 秒超时。
  const result = await requireBridge('__APP_OPEN_PICKER_WITH_RESULT__')({
    count: 3,
    mediaType: 'photo',
    fileSizeLimit: 20,
  })

  return acceptMediaResult(result)
}

export async function takeStorePhoto(): Promise<AcceptedMediaResult> {
  const result = await requireBridge('__APP_GO_TO_CAMERA_WITH_RESULT__')({
    count: 1,
    number: 0,
    cameraPosition: 'back',
    fileSizeLimit: 20,
    cameraTip: {
      title: '拍摄门店正面',
      subtitle: '请保持门头完整、文字清楚',
    },
  })

  return acceptMediaResult(result)
}

export async function recordStoreVideo(): Promise<AcceptedMediaResult> {
  const result = await requireBridge('__APP_OPEN_TRANSCRIBE_WITH_RESULT__')({
    fileSizeLimit: 100,
  })

  return acceptMediaResult(result)
}
```

调用按钮应有单实例忙碌状态。取消不是成功附件，部分失败应明确提示，上传成功也不等于业务表单
已保存。新相册协议当前不保证旧水印链路生效。

## 手写签名

```ts
export async function requestSignature(): Promise<string | null> {
  const result = await requireBridge('__APP_OPEN_SIGNATURE__')({
    title: '门店确认签名',
    penColor: '#000000',
    penWidth: 4,
    returnBase64: false,
  })

  if (!result.success) {
    if (result.reason === 'cancelled') return null
    throw new Error('签名未完成，请重试')
  }

  if (!result.fileUrl) throw new Error('签名未返回可保存的文件地址')

  return result.fileUrl
}
```

不要并发打开多个签名页，不打印 Base64 或本地文件路径。原生 5 分钟超时通常通过
`{ success: false, reason: 'timeout' }` 返回。

## 旧媒体/文件事件流（仅兼容时使用）

旧桥返回 `void`，打开状态回调经 `onOpen…Callback`，上传进度/结果经 `receiveRNData`。
它们不是可以保证 settle 的 Promise。用业务 `uuid` 关联批次、用回调里的 `key` 关联文件或取消；
不要自造底层 `callbackId` 或 `__requestId`。

```ts
const LEGACY_EVENT = 'app-legacy-upload'
let legacyReceiverInstalled = false

export function installLegacyUploadReceiver(): void {
  if (legacyReceiverInstalled) return

  legacyReceiverInstalled = true
  const previous = window.receiveRNData

  window.receiveRNData = data => {
    window.dispatchEvent(new CustomEvent<LegacyUploadMessage>(LEGACY_EVENT, {
      detail: data,
    }))
    previous?.(data)
  }
}

export function openLegacyCamera(uuid: string): void {
  requireBridge('__APP_GO_TO_CAMERA__')(JSON.stringify({
    uuid,
    count: 1,
    number: 0,
    cameraPosition: 'back',
    fileSizeLimit: 20,
  }))
}
```

在根模块先安装接收器，并精确比较打开回调值：`value === true || value === 'true'`；
`Boolean('false')` 是 `true`，不能使用。监听事件时至少处理 `progress`、`success`、`error`、
`cancel`，旧视频成功还可能拼写为 `complated`。旧文件选择取消不保证统一结束事件，UI 必须允许
用户手动退出忙碌状态。

一次用户操作不要同时调用新旧两套媒体协议。只有需要上传进度、逐文件回调或兼容缺少
`*_WITH_RESULT__` 的目标安装包时才进入本节。

## 生命周期与键盘

生命周期消费必须读取 `__APP_LIFECYCLE_STATE__` 初始快照、监听 `appLifecycleChange`，并按
`sequence` 去重。键盘桥没有注销函数，只在根模块注册一次，再经应用自己的状态层分发。

完整示例及其他能力（定位、权限、扫码、文件预览、地图、报告分享、巡店）直接使用权威文档中
对应章节，避免复制一份会漂移的二级说明。
