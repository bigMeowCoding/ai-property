# 运营 App Bridge API 全表（App 侧权威口径）

来源：`busyming-operation-app` 接入指南，App 基线 `feature/cwc_2.1.2`，更新时间 2026-08-10。
H5 消费参考：`busyming-operation-vue-h5 / feature/cwc_top300`。

**总原则：以 App 真实代码为准；H5 必须做能力检测，不得只看 User-Agent，
也不得假设所有 App 版本具备相同 Bridge（除生命周期外，公共 Bridge 没有统一版本号）。**

## 1. App 侧打开 H5 的入口参数

```ts
navigation.navigate('WebViewScreen', {
  url: 'https://fe.busyming.com/subapp/example-h5/page',
  mode: 'start',
  id: 'example_h5_' + Date.now(),
})
```

| 字段 | 必填 | 说明 |
|---|---|---|
| `url` | 是 | H5 完整地址，推荐 HTTPS |
| `mode` | 建议 | 新业务页面用 `start`；退出时清理对应 WebView 实例 |
| `id` | 建议 | WebView 实例标识；并行打开多个页面时必须唯一 |
| `needSafeArea` | 否 | `true` 时 App 在 WebView 外包一层 `SafeAreaView` |
| `needNavBar` | 否 | 强制显示原生导航栏（**路由层实际读取的就是这个拼写**） |
| `narbarTitle` | 否 | 原生导航栏标题（**当前代码实际拼写为 `narbarTitle`**） |
| `ignoreToken` | 否 | 不注入 `__APP_TOKEN__` |
| `ignoreCity` | 否 | 不注入 `__APP_CITY__` |
| `ignoreLocation` | 否 | 不注入 `__APP_GEO__` |
| `appContext` | 否 | **路由专用上下文；传入后会覆盖默认三项公共上下文，新 H5 不应自行传入** |

公共上下文的生成时机（未显式传 `appContext` 且 App 用户信息已就绪时）：
获取/复用统一门户 Token → 取设备信息 → 读当前战区及负责人 → 上下文就绪后才挂载
WebView → H5 首次业务脚本即可读到 `window.__APP_CONTEXT__`。

统一门户 Token 刷新、用户或战区上下文版本变化时，**App 会重建上下文并重建 WebView**。
H5 不能假设页面内存状态可跨 Token / 战区切换保留。

URL 与域名：推荐完整 HTTPS；History / Hash 路由均可；当前 `originWhitelist` 为 `*`
且允许混合内容（这不是安全承诺）；H5 地址必须由可信配置或可信接口下发；
未经 App 侧确认，不要把统一门户 Token 注入第三方域名。

## 2. 环境判定

```ts
export function isOperationAppWebView(): boolean {
  return (
    window.__BUSYMING_OPERATION_APP__ === true
    && typeof window.ReactNativeWebView?.postMessage === 'function'
  )
}

export function hasBridge(name: keyof Window): boolean {
  return typeof window[ name ] === 'function'
}
```

- `window.__BUSYMING_OPERATION_APP__ === true` 是当前 App WebView 的标识。
- `window.__APP__` 的实际值是**字符串** `'SITESTORE'`，不是 Bridge 对象。
- 即使确认在 App 内，每个具体能力仍要 `typeof window.__APP_XXX__ === 'function'` 判断。

## 3. 三类认证信息（不可互换）

| 认证信息 | H5 获取方式 | 用途 |
|---|---|---|
| App 主登录 Token（原业务 / 人资认证体系） | `window.__APP_TOKEN__` | App 现有业务后端，App 普通请求的主凭证 |
| 人资 / 业务中台 TokenInfo | `await window.__APP_GET_TOKEN_AUTHINFO__(args)` | 明确要求 `BizMidPlatform` 凭证的系统 |
| 统一门户 Token | `window.__APP_CONTEXT__.unifiedPortal.accessToken` | 统一门户 / 统一网关接口 |

**三者不是同一个 Token 的不同名称。** 后端文档只写「传 Token」时不要盲猜，
必须先确认接口归属、请求域名、认证头、是否需要验签。
也不要为三类 Token 建一个共用字符串变量，用
`appBusinessToken` / `hrPlatformTokenInfo` / `unifiedPortalToken` 这类可区分命名。

### 3.1 `__APP_TOKEN__`（App 主登录 Token）

链路：用户在 App 内登录 → App 把 `data.token` 写入 MobX `authStore` 与
`AsyncStorage['token']` → App 普通请求注入 `Authorization: Bearer <token>` →
`WebViewScreen` 在 H5 首次脚本执行前注入 `window.__APP_TOKEN__` →
存活期内变化时 App 重新赋值并尝试调用 `window.onAppToken(token)`。

它**不是已废弃字段**，不要称为「旧 Token」。禁止：写入 URL / 路由 query / 分享链接；
上报到日志、埋点、Sentry、截图；用于统一门户接口；在 `ignoreToken: true` 的
WebView 里假设它一定存在。

### 3.2 `__APP_GET_TOKEN_AUTHINFO__`（人资 / 中台 TokenInfo）

内部调 App 的 `/personnel/web/token/replace/hr-platform` 兑换 `tokenInfo`。

```ts
const tokenInfo = await window.__APP_GET_TOKEN_AUTHINFO__?.({
  bizType: 'BizMidPlatform',
  brand: 'LSHM',
})

if (!tokenInfo || typeof tokenInfo !== 'object') throw new Error('人资平台 TokenInfo 获取失败')
```

- `bizType` 当前有效分支为 `BizMidPlatform`（其他值走默认分支，**不要依赖这个宽松行为**）。
- `brand` 默认 `LSHM`。
- 成功返回后端 `data.tokenInfo` 对象；失败或结构不符时返回**空字符串 `''`，当前不会 reject**。
- `tokenInfo` 内部字段由人资平台合同决定，不要自行假设固定结构。
- 只有后端明确要求时才调用，普通业务接口不需要先调它。

### 3.3 Token 更新、登录失效、账号切换

- App 主 Token 变化 → 重新注入 `__APP_TOKEN__` 并调用已注册的 `window.onAppToken`。
- 统一门户 Token 变化 → 重建 `__APP_CONTEXT__` 并重建 WebView，H5 应从新上下文启动。
- App 主登录态确实失效时可调 `window.__APP_GO_LOGIN__()`；
  它会**清理整个 App 登录态**，禁止用于一般网络异常。
- 退出登录 / 账号切换后，不得复用上一个用户的 Token、用户信息、战区、本地缓存。

## 4. `window.__APP_CONTEXT__`（公共默认形态）

通用 `WebViewScreen` 默认注入以下三项：

```ts
interface OperationH5AppContext {
  unifiedPortal: {
    accessToken: string
    userInfo: Record<string, unknown>
  }

  deviceInfo: {
    id: string
    type: 'APP'
    platform: 'IOS' | 'AND' | 'WEB'
    appVersion: string
    systemVersion: string
    model: string
    deviceName: string
  } | null

  zoneOwnerInfo: {
    zoneUserId: string | null
    zoneUserCode: string | null
    selectedZoneInfo: Record<string, unknown> | null
  }
}
```

- `unifiedPortal.accessToken` 是统一门户 Token，**不是** App 主登录 Token。
- `unifiedPortal.userInfo` 字段由统一门户响应决定，App 已剔除 Token 与设备字段。
- `deviceInfo` 获取失败时为 `null`。
- Android 的 `platform` 固定为 `'AND'`，**不是 `'ANDROID'`**。
- 选中战区时 `selectedZoneInfo` 为战区扁平字段并补 `zoneUserId` / `zoneUserCode`；
  未选战区时这两个 id 回退当前登录用户，`selectedZoneInfo` 为 `null`。

读取封装：

```ts
export function getOperationAppContext(): OperationH5AppContext | null {
  if (typeof window === 'undefined') return null

  const value = window.__APP_CONTEXT__

  if (!value || typeof value !== 'object') return null

  return value
}
```

不要：生产日志打印完整上下文；把 `accessToken` 写进 URL；把上下文整体持久化到长期
`localStorage`；把统一门户 Token 当 App 主 Token 用；缺少上下文时永久 Loading
（应显示「请在最新版门店运营 App 内重新打开」这类明确错误）。

### 4.1 统一门户请求边界（重要）

`__APP_CONTEXT__` **只**提供 `unifiedPortal` / `deviceInfo` / `zoneOwnerInfo`，
**不**提供 MSE App Secret、默认 `X-Operate-Info`、统一门户资源树、
任意接口的 `permissionCode` 映射。因此：

- 只需 Bearer Token 的接口，可按后端合同直接用 `accessToken`。
- 需要 MSE 验签的接口，不能只靠 `accessToken` + `deviceInfo` 就认为已接通。
- **浏览器 H5 不应内置生产 `APP_SECRET`。**
- 需要 MSE 或权限树时，优先让 H5 调自己的后端代理，或由 App 新增受控 Bridge。
- 后端若明确允许浏览器签名，也必须单独确认签名规范、设备头、`X-Operate-Info`、
  401 刷新协议。
- 不要把 `permissionCode`、`dataScopes` 等前端内部字段直接透传为后端请求头。

## 5. 注入到 window 的运行时数据字段

| 字段 | 实际类型 | 说明 |
|---|---|---|
| `__APP__` | `'SITESTORE'` | 历史容器标识，字符串 |
| `__BUSYMING_OPERATION_APP__` | `true` | 当前运营 App 标识 |
| `__APP_TOKEN__` | `string` | App 主登录 Token |
| `__APP_CITY__` | `string` | 当前城市行政区划编码 |
| `__APP_GEO__` | `string` | `latitude,longitude`；无定位时为空字符串 |
| `__APP_STATUS_BAR_HEIGHT__` | **数字字符串** | 使用时需 `Number(...)` |
| `__APP_PLATFORM__` | `'ios' \| 'android'` | RN 平台值（注意与 `deviceInfo.platform` 的 `AND` 口径不同） |
| `__APP_PLATFORM_ANDROID_BRAND__` | `string` | Android 设备品牌；iOS 为空 |
| `__APP_LIFECYCLE_BRIDGE_VERSION__` | `number` | 当前生命周期协议版本为 `1` |
| `__APP_LIFECYCLE_STATE__` | `AppLifecyclePayload` | 最近一次前后台状态快照 |
| `ReactNativeWebView` | 对象 | 底层消息通道；业务优先用封装好的 `__APP_*` |

### 5.1 App 主动回调 H5（H5 注册函数）

```ts
window.onAppToken = token => updateBusinessToken(token)   // App 主 Token 更新
window.onAppCity = adcode => { /* 城市编码更新 */ }
window.onAppGeo = geo => {
  const [ latitude, longitude ] = String(geo || '').split(',')
}
window.onReactNativeSafeAreaInsetsChange = insets => { /* { top,right,bottom,left } */ }
```

### 5.2 战区同步

App 把当前战区写入 `localStorage['common-select-store']`，变化时触发事件：

```ts
window.addEventListener('appZoneChanged', event => {
  const selectedZone = (event as CustomEvent).detail
})
```

`common-select-store` 是 operation-h5 的**兼容协议**；新 H5 优先用
`__APP_CONTEXT__.zoneOwnerInfo`，只有需要和 operation-h5 共用选择器时才复用它。

### 5.3 App 生命周期（唯一有版本号的 Bridge）

```ts
interface AppLifecyclePayload {
  version: 1
  sequence: number
  state: 'background' | 'active'
  changedAt: number
  backgroundAt: number | null
  activeAt: number | null
}
```

消费方必须同时做三件事：① 首次读 `window.__APP_LIFECYCLE_STATE__`；
② 监听 `appLifecycleChange`；③ 用 `sequence` 去重，避免重复处理同一状态。

## 6. Bridge 调用通用规范

- **调用前必须检测**：`typeof window.__APP_XXX__ !== 'function'` 时走浏览器 / 企微 /
  旧版 App 的降级逻辑，不要抛错。
- **底层消息格式**（封装内部行为，业务不要自行调用）：

  ```ts
  window.ReactNativeWebView.postMessage(
    JSON.stringify({ action: 'getAppVersion', params: { callbackId: 'Bridge自动生成' } }),
  )
  ```

  业务 H5 不应自行生成 `callbackId`，也不应直接调 App 内部 action。
- **三种返回值形态**：
  - 「无返回值」方法：发送消息后立即返回 `undefined`（**不要 await**）；
  - 「Promise」方法：App 通过动态 `window[callbackId](result, error)` 回传；
  - 「事件流」方法：相机 / 相册旧协议通过固定回调 + `window.receiveRNData` 回传。
- **关键 Promise 建议 H5 侧再包一层超时**：

  ```ts
  export function withTimeout<T>(task: Promise<T>, timeout = 45000): Promise<T> {
    return new Promise<T>((resolve, reject) => {
      const timer = window.setTimeout(() => reject(new Error('App Bridge 调用超时')), timeout)

      task.then(
        value => { window.clearTimeout(timer); resolve(value) },
        error => { window.clearTimeout(timer); reject(error) },
      )
    })
  }
  ```

## 7. 导航与 WebView 容器

| 方法 | 参数 | 返回 | App 行为 |
|---|---|---|---|
| `__APP_ROUTER_BACK__()` | 无 | void | 有网页历史则后退，否则关闭当前 Native 页面 |
| `__APP_GO_HOME_TAB__()` | 无 | void | 关闭当前及上层 WebView，回 App TabBar 首页 |
| `__APP_OPEN_NEW_WINDOW__(url, needSafeArea?, needNarBar?, narBarTitle?)` | 完整 URL + 展示配置 | void | Native push 一个新 `WebViewScreen` |
| `__OPEN_APP_WEBVIEW__(isShowBack?, title?)` | 是否显示原生返回栏、标题 | void | 动态控制当前容器顶部原生栏 |
| `__APP_GO_LOGIN__()` | 无 | void | 清除 App 本地主登录 Token 并跳登录页 |
| `__APP_ORIENTATION__(orientation?)` | `landscape` / `portrait`（其他值按竖屏） | void | 锁定屏幕方向并同步状态栏 |

边界：

- `__APP_OPEN_NEW_WINDOW__` 是 **Native push，不是 H5 Router**。新 WebView 不继承当前
  H5 的内存状态、Redux / Pinia 状态和页面栈。同一 H5 内部跳转必须用自身路由。
  重复创建 WebView 会导致状态丢失、返回栈变深、iOS 内存压力 / 白屏、
  多页面持有不同 Token / 战区快照。
- 当前 App 分支中，Bridge 传的是 `needNarBar` / `narBarTitle`，
  但目标 WebView 读的是 `needNavBar` / `narbarTitle`
  → **`__APP_OPEN_NEW_WINDOW__` 的「强制导航栏 / 标题」参数当前不是稳定能力**，
  需要原生栏时在新页面加载后调 `__OPEN_APP_WEBVIEW__`。
- `__APP_GO_LOGIN__` 改变整个 App 登录态，只允许认证失效流程调用。

## 8. 系统与设备：版本、安全区、定位、权限、扫码

| 方法 | 参数 | 返回 | 说明 |
|---|---|---|---|
| `__APP_GET_VERSION__()` | 无 | `Promise<string>` | App 版本号（注意 operation-h5 老声明把它写成字符串，是错的） |
| `__APP_GET_SAFE_AREA__()` | 无 | JSON 字符串 | `JSON.parse` 后得 `top/right/bottom/left` |
| `__APP_GET_CURRENT_LOCATION__(timeout?)` | 超时毫秒，默认 40000 | `Promise<string>` | 成功返回 `latitude,longitude`；失败 / 超时返回空字符串 |
| `__APP_GET_CURRENT_ADDRESS__(timeout?)` | 接受 `timeout`（当前实现未使用） | `Promise<string>` | 返回 App 用户地址或空字符串 |
| `__APP_GET_PERMISSION_LOCATION__()` | 无 | `Promise<string>` | **只检查**定位权限，不申请 |
| `__APP_NOTIFICATION_PERMISSION__()` | 无 | `Promise<string>` | **只检查**通知权限，不申请 |
| `__APP_CHECK_OR_REQUEST_PERMISSION__(args)` | 见下 | `Promise<string>` | 通用权限检查或申请 |
| `__APP_OPEN_SETTING__()` | 无 | void | 打开本 App 的系统设置页 |
| `__APP_SCAN_CODE__(args?)` | 当前可不传 | `Promise<ScanResult>` | 原生扫码 |
| `__APP_REGISTER_KEYBOARD_LISTENER__(cb)` | `cb({ visible, height })` | void | 键盘监听 |

权限状态来自 `react-native-permissions`：
`'unavailable' | 'denied' | 'blocked' | 'granted' | 'limited'`。

```ts
const status = await window.__APP_CHECK_OR_REQUEST_PERMISSION__?.({
  permission: 'CAMERA',   // CAMERA | LOCATION | PHOTO | MICROPHONE | CONTACTS，必须大写
  requestDirectly: true,  // false 只检查；true 直接申请
})
```

iOS / Android 的 `denied`、`blocked` 行为不同：不要凭一次返回值假设系统一定会再弹框，
`blocked` 时应引导用户去系统设置。

定位消费示例（含空值与非数字防御）：

```ts
const value = await window.__APP_GET_CURRENT_LOCATION__?.(40000)

if (!value) return null

const [ latitude, longitude ] = value.split(',').map(Number)

if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) return null
```

扫码返回**同时可能是字符串或对象**，取消 / 失败通常返回 `{ success: false }`，
消费方要兼容多个字段，不要只读一个：

```ts
interface ScanResultObject {
  success?: boolean
  data?: string | Record<string, unknown>
  result?: string
  qrCode?: string
  content?: string
  text?: string
}

type ScanResult = string | ScanResultObject
```

键盘监听：**当前只有注册、没有注销**。不要在组件重复渲染时反复注册，
建议应用根组件注册一次再经自己的事件总线分发。

## 9. 通用系统功能、文件与预览

| 方法 | 参数 | 返回 | 说明 |
|---|---|---|---|
| `__APP_CALL_PHONE__(phone)` | 号码字符串 | void | 调起系统拨号 |
| `__APP_COPY_TEXT__(text)` | 文本 | void | 写剪贴板，App 自带提示 |
| `__APP_PHOTO_DOWNLOAD__(url)` | 图片 URL | void | 下载保存到系统相册 |
| `__APP_OPEN_FILE__(url)` | HTTP(S) 文件地址 | void | 用系统能力打开文件链接 |
| `__APP_DOCUMENT_VIEW__({ url, type, title })` | 文件信息 | **声明为 Promise 但永不 settle** | doc/xls 走外部应用，其他类型进 App 文档预览页；**禁止 await** |
| `__APP_PREVIEW_IMAGE__({ urls, current })` | URL 数组 + 当前索引/URL | void | App 图片预览 |
| `__APP_PREVIEW_VIDEO__({ url })` | 视频 URL | void | App 视频预览 |
| `__APP_OPEN_MAP__({ params })` | 见下 | void | 调起百度 / 高德 / 腾讯 / 苹果地图 |
| `__APP_IMAGE_TO_DATA_URL__(url)` | 图片 URL | `Promise<string>` | App 下载图片返回 data URL，用于规避 iOS WebView 远程图截图空白 |

```ts
window.__APP_OPEN_MAP__?.({
  params: {
    map: 'amap', // baidu | amap | qqmap | apple
    from: { lat: 28.123, lng: 112.987, name: '我的位置' },
    to: { lat: 28.456, lng: 113.123, name: '目标门店' },
  },
})
```

## 10. 媒体与文件：相机 / 相册 / 录像 / 上传

App 同时保留「事件流旧协议」和「Promise 新协议」。
**新 H5 优先用 Promise 新协议**；只有需要上传进度、多文件逐条回调或兼容旧 App 时才接旧协议。

### 10.1 Promise 新协议（推荐）

| 方法 | 说明 |
|---|---|
| `__APP_OPEN_PICKER_WITH_RESULT__(args)` | 相册选择并由 App 上传 |
| `__APP_GO_TO_CAMERA_WITH_RESULT__(args)` | 打开 App 相机，拍摄后上传 |
| `__APP_OPEN_TRANSCRIBE_WITH_RESULT__(args)` | 打开 App 录像，录制后上传 |

```ts
interface MediaBridgeArgs {
  uuid?: string
  count?: number
  number?: number
  mediaType?: 'photo' | 'video' | 'any'
  fileSizeLimit?: number      // 单位 MB
  proName?: string            // 水印项目 / 门店名
  brand?: string              // 水印品牌
  cameraPosition?: 'front' | 'back' | string
  cameraTip?: { title?: string; content?: string }
}

interface UploadedFile {
  name: string
  url: string
  path: string
  fileUrl: string
  fileSize: number
  contentType: string
  fileExtension: string
  key: string
  status: 'success' | 'error'
  error?: string
}

interface MediaBridgeResult {
  success: boolean
  data: UploadedFile[]
  error?: string   // cancel、picker_failed、文件超限等
}
```

```ts
const result = await window.__APP_OPEN_PICKER_WITH_RESULT__?.({
  count: 3,
  mediaType: 'photo',
  fileSizeLimit: 20,
})

if (!result?.success) {
  if (result?.error !== 'cancel') console.error('选择图片失败', result?.error)

  return
}
```

### 10.2 事件流旧协议

| 方法 | 参数要求 | 说明 |
|---|---|---|
| `__APP_GO_TO_CAMERA__(jsonString)` | 推荐 `JSON.stringify(args)` | 打开相机 |
| `__APP_OPEN_PICKER__(jsonString)` | 推荐 `JSON.stringify(args)` | 打开相册 |
| `__APP_OPEN_TRANSCRIBE__(jsonString)` | **必须** JSON 字符串 | 打开录像 |
| `__APP_OPEN_FILE_PICKER__(jsonString)` | **必须** JSON 字符串 | 系统文件 / 目录选择器 |
| `__APP_CANCEL_REQUEST__(key)` | 上传文件的 `key` | 取消对应上传请求 |

旧协议参数：`uuid`（业务批次标识，回调原样携带）、`count`、`number`（已有文件数）、
`mediaType`、`fileSizeLimit`（MB）、`cameraPosition`、`cameraTip`、
`watermark` / `needWatermark` / `addWatermark`（相册图片水印，`boolean | 0 | 1 | string`）、
`proName`、`brand`、`dir`（文件选择器选目录）、`type`（允许的 MIME / 文档类型）。

H5 必须**在 App 回调前**注册固定回调：

```ts
type LegacyOpenStatus = boolean | 'true' | 'false'

const isBridgeOpenSuccess = (value: LegacyOpenStatus) => value === true || value === 'true'

window.onOpenCameraCallback = value => { /* 仅表示 Native 是否接受并打开入口 */ }
window.onOpenPickerCallback = value => { /* 上传结果仍以 receiveRNData 为准 */ }
window.onOpenTranscribeCallback = value => { /* 同上 */ }
window.receiveRNData = data => { /* 上传进度 / 成功 / 取消 / 失败 */ }
```

**App 实际回传的是字符串 `'true'` / `'false'`，不是布尔值。禁止 `if (value)` 判断，
因为字符串 `'false'` 也是 truthy。**

`__APP_OPEN_FILE_PICKER__` 的 `dir: true` 分支**没有形成完整的文件数组回调链**，
不要依赖目录选择，只用经真机验证的文件选择模式。

`receiveRNData` 数据结构：

```ts
interface LegacyUploadMessage {
  name?: string
  url?: string
  path?: string
  contentType?: string
  fileExtension?: string
  fileSize?: number
  fileUrl?: string
  eventType?: 'cameraCallback' | 'pickerCallback' | 'transcribeCallback' | 'video' | string
  status?: 'progress' | 'success' | 'error' | 'cancel' | string
  error?: string
  uuid?: string
  key?: string
  rnProgress?: number
  totalFileCount?: number
}
```

operation-h5 的消费方式：HTML 入口提前定义 `window.receiveRNData` → 转发到应用级事件总线
→ 上传组件按 `uuid` / `key` / `eventType` 更新进度和文件列表 → 删除文件时调
`__APP_CANCEL_REQUEST__(key)`。

相册水印**仅**在三个条件同时满足时生效：`mediaType === 'photo'`、
水印参数为 `true` / `1` / 对应字符串、App 能成功生成水印视图。

### 10.3 手写签名

```ts
interface SignatureArgs {
  penColor?: string       // 默认 #000000
  penWidth?: number       // 默认 4
  placeholder?: string    // 默认「请在空白区域内横向书写」
  returnBase64?: boolean  // 默认 false
  title?: string          // 默认「手写签名」
}

interface SignatureResult {
  success: boolean
  fileUrl?: string
  base64?: string
  localFilePath?: string
  reason?: 'cancelled' | 'timeout' | string
}

const result = await window.__APP_OPEN_SIGNATURE__?.({ title: '门店签名' })
```

App 内部超时 5 分钟；取消 / 失败 / 超时通过 `success: false` 返回，**不会 reject**。

## 11. 业务专用 Bridge（非通用能力）

以下能力与 App 内部业务 / Store / Map 状态强耦合，只有复用对应业务时才用，
不要当通用能力使用。

### 11.1 报告分享

`__APP_OPEN_REPORT_SHARE__(args)`，参数：`imageUrl`（已生成图片地址）、
`requestId`（延迟生成时必填）、`title`（企微卡片标题）、`fileName`、
`shareUrl`（企微分享必填）、`description`、`thumbUrl`（公网 HTTP(S) 缩略图，不支持 Base64）。

延迟生成图片协议：H5 生成唯一 `requestId` → 注册
`window.__H5_GENERATE_REPORT_SHARE_IMAGE__(requestId)` → 调
`__APP_OPEN_REPORT_SHARE__({ requestId, ... })` → 用户点「保存为图片」→ App 回调 H5 的
生成函数 → H5 生成并上传 → H5 调 `__APP_REPORT_SHARE_IMAGE_READY__({ requestId, success, imageUrl })`
→ App 保存并提示。**`requestId` 必须与打开面板时一致，否则 App 忽略结果。**

### 11.2 巡店

`__APP_PATROL_START_INSPECTION__(opts)` / `__APP_PATROL_CONTINUE_INSPECTION__(opts)`
封装了定位、进行中记录判断、到店打卡、排班检查、建单和巡店页面跳转。

```ts
interface PatrolBridgeCallOptions {
  autoNavigate?: boolean
  needSafeArea?: boolean
  needNarBar?: boolean
  narBarTitle?: string
  closeTarget?: 'APP_HOME' | 'SOURCE_WEBVIEW' | 'SOURCE_H5_ROUTE' | 'SOURCE_H5_RELAUNCH'
  closeRoute?: string
  entrySource?: string
}

type PatrolBridgeCode =
  | 'OPEN_WEBVIEW' | 'SIGN_IN_CLOCK' | 'SCHEDULE_REMINDER'
  | 'CANCELLED' | 'TOAST' | 'USER_NOT_READY' | 'ERROR'

interface PatrolBridgeCallbackResult {
  success: boolean
  code: PatrolBridgeCode
  url?: string
  recordId?: string | number
  message?: string
  appToastShown?: boolean
}
```

`autoNavigate` 默认 `true`（App 直接 push 新 WebView）；需要保留当前 H5 内存状态时用
`false`，拿到 URL 后自行路由。`appToastShown === true` 表示 App 已提示，H5 不要重复 Toast。

### 11.3 选址 / 地图

`__APP_ACTION__(target, action, id)`（`target`: `shopcircle` / `point`）获取商圈或点位详情并
打开 App 地图页；`__APP_LOCATION__(params)`（需含 `target: 'location'`、经纬度、城市编码等）
设置 App 地图上下文并打开地图页。

选择器确认走 App 内部 action `onSelectorConfirm`，**没有注入同名公共 window 方法**，
未经 App 团队确认不要自行 `postMessage` 调用。列表页返回时 App 可能调
`window.onAppUpdateList`；局部「全部战区」选择完成可能触发 `appLocalZoneChanged`
——都属于现有选址 / 看板协议，不是新 H5 的通用依赖。

App 内部还有 `openPage`、`showAlert`、`onSelectorConfirm`、`list`、`uniPages` 等
action handler，但**没有对应的稳定公共 window 方法，不属于接入方 API**。

## 12. 推荐的 TypeScript window 声明

放入 `src/types/global.d.ts`。**不要照抄 operation-h5 现有 `global.d.ts` 的旧类型**
（例如它把 `__APP_GET_VERSION__` 声明成字符串，实际是 Promise 方法）。

```ts
export {}

declare global {
  interface Window {
    ReactNativeWebView?: { postMessage(data: string): void }

    __BUSYMING_OPERATION_APP__?: boolean
    __APP__?: 'SITESTORE' | string
    __APP_CONTEXT__?: OperationH5AppContext
    __APP_TOKEN__?: string
    __APP_CITY__?: string
    __APP_GEO__?: string
    __APP_STATUS_BAR_HEIGHT__?: string | number
    __APP_PLATFORM__?: 'ios' | 'android' | string
    __APP_PLATFORM_ANDROID_BRAND__?: string

    __APP_LIFECYCLE_BRIDGE_VERSION__?: number
    __APP_LIFECYCLE_STATE__?: AppLifecyclePayload

    onAppToken?: (token: string) => void
    onAppCity?: (adcode: string) => void
    onAppGeo?: (geo: string) => void
    onReactNativeSafeAreaInsetsChange?: (insets: Record<string, number>) => void

    __APP_ROUTER_BACK__?: () => void
    __APP_GO_HOME_TAB__?: () => void
    __APP_OPEN_NEW_WINDOW__?: (
      url: string, needSafeArea?: boolean, needNarBar?: boolean, narBarTitle?: string,
    ) => void
    __OPEN_APP_WEBVIEW__?: (isShowBack?: boolean, title?: string) => void
    __APP_GO_LOGIN__?: () => void
    __APP_ORIENTATION__?: (orientation?: 'landscape' | 'portrait') => void

    __APP_GET_CURRENT_LOCATION__?: (timeout?: number) => Promise<string>
    __APP_GET_CURRENT_ADDRESS__?: (timeout?: number) => Promise<string>
    __APP_GET_PERMISSION_LOCATION__?: () => Promise<string>
    __APP_OPEN_SETTING__?: () => void
    __APP_NOTIFICATION_PERMISSION__?: () => Promise<string>
    __APP_CHECK_OR_REQUEST_PERMISSION__?: (args: {
      permission: 'CAMERA' | 'LOCATION' | 'PHOTO' | 'MICROPHONE' | 'CONTACTS'
      requestDirectly?: boolean
    }) => Promise<string>
    __APP_GET_SAFE_AREA__?: () => string
    __APP_GET_VERSION__?: () => Promise<string>
    __APP_SCAN_CODE__?: (args?: Record<string, unknown>) => Promise<ScanResult>

    __APP_CALL_PHONE__?: (phone: string) => void
    __APP_COPY_TEXT__?: (text: string) => void
    __APP_PHOTO_DOWNLOAD__?: (url: string) => void
    __APP_OPEN_FILE__?: (url: string) => void
    __APP_DOCUMENT_VIEW__?: (args: { url: string; type?: string; title?: string }) => Promise<never>
    __APP_PREVIEW_IMAGE__?: (args: {
      urls: string[] | string; current?: number | string
    }) => void
    __APP_PREVIEW_VIDEO__?: (args: { url: string }) => void
    __APP_OPEN_MAP__?: (args: {
      params: {
        map: 'baidu' | 'amap' | 'qqmap' | 'apple'
        from: { lat: number; lng: number; name?: string }
        to: { lat: number; lng: number; name?: string }
      }
    }) => void
    __APP_IMAGE_TO_DATA_URL__?: (url: string) => Promise<string>

    __APP_OPEN_PICKER_WITH_RESULT__?: (args?: MediaBridgeArgs) => Promise<MediaBridgeResult>
    __APP_GO_TO_CAMERA_WITH_RESULT__?: (args?: MediaBridgeArgs) => Promise<MediaBridgeResult>
    __APP_OPEN_TRANSCRIBE_WITH_RESULT__?: (args?: MediaBridgeArgs) => Promise<MediaBridgeResult>
    __APP_GO_TO_CAMERA__?: (args: string) => void
    __APP_OPEN_PICKER__?: (args: string) => void
    __APP_OPEN_TRANSCRIBE__?: (args: string) => void
    __APP_OPEN_FILE_PICKER__?: (args: string) => void
    __APP_CANCEL_REQUEST__?: (key: string) => void

    onOpenCameraCallback?: (success: boolean | 'true' | 'false') => void
    onOpenPickerCallback?: (success: boolean | 'true' | 'false') => void
    onOpenTranscribeCallback?: (success: boolean | 'true' | 'false') => void
    receiveRNData?: (data: LegacyUploadMessage) => void

    __APP_OPEN_SIGNATURE__?: (args?: SignatureArgs) => Promise<SignatureResult>
    __APP_REGISTER_KEYBOARD_LISTENER__?: (
      callback: (status: { visible: boolean; height: number }) => void,
    ) => void

    __APP_GET_TOKEN_AUTHINFO__?: (args?: {
      bizType?: 'BizMidPlatform' | string
      brand?: string
    }) => Promise<Record<string, unknown> | ''>

    __APP_OPEN_REPORT_SHARE__?: (args: Record<string, unknown>) => void
    __APP_REPORT_SHARE_IMAGE_READY__?: (args: {
      requestId: string; success: boolean; imageUrl?: string; message?: string
    }) => void
    __H5_GENERATE_REPORT_SHARE_IMAGE__?: (requestId: string) => Promise<void> | void

    __APP_PATROL_START_INSPECTION__?: (
      args?: PatrolBridgeCallOptions,
    ) => Promise<PatrolBridgeCallbackResult>
    __APP_PATROL_CONTINUE_INSPECTION__?: (
      args?: PatrolBridgeCallOptions,
    ) => Promise<PatrolBridgeCallbackResult>

    __APP_ACTION__?: (
      target: 'shopcircle' | 'point', action: string, id: string | number,
    ) => void
    __APP_LOCATION__?: (args: Record<string, unknown>) => void
  }
}
```

## 13. 联调检查清单

**App 入口**：正确环境的 HTTPS 地址 / 用 `WebViewScreen` 打开 / `id` 唯一 /
没有误传 `appContext` 覆盖公共三项 / 返回、手势、原生导航栏符合预期。

**H5 初始化**：`__BUSYMING_OPERATION_APP__ === true` /
已按后端合同确认用哪一类 Token / 用 App 主 Token 时 `__APP_TOKEN__` 存在且未进日志与 URL /
只在接口要求时调 `__APP_GET_TOKEN_AUTHINFO__` 并处理空字符串失败 /
`__APP_CONTEXT__` 存在且 `unifiedPortal.accessToken` 未进日志与 URL /
`deviceInfo.platform` 兼容 `AND` / 无战区时正确回退登录用户 /
缺失上下文时有明确错误页而非无限 Loading。

**Bridge**：每次调用前 `typeof === 'function'` / Promise 方法处理取消、失败、超时 /
无返回值方法没有被错误 await / H5 内部页面没有误用 `__APP_OPEN_NEW_WINDOW__` /
上传旧协议提前注册固定回调与 `receiveRNData` / 键盘监听没有重复注册。

**生命周期与战区**：首次读 `__APP_LIFECYCLE_STATE__` / 正确监听并移除
`appLifecycleChange` / 监听 `appZoneChanged` 或接受 WebView 重建 /
Token 刷新后使用最新上下文 / 账号切换后不复用旧用户数据。

**真机验证**：iOS + Android 真机 / 首次权限申请、拒绝、blocked、去设置后返回 /
前后台切换与锁屏 / WebView 返回栈 / 相机相册视频扫码文件预览 / Token 过期刷新 /
战区切换后重新进入 / 弱网断网与加载失败。

## 14. 当前实现依据

App 侧协议源：`src/components/LoginPage.tsx`、`src/api/client.ts`、
`src/api/endpoints/auth.ts`、`src/components/WebViewScreen.tsx`、
`src/config/bridgeConfig.ts`、`src/components/webViewAppContext.ts`、
`src/components/webViewAppLifecycle.ts`、`src/api/unifiedPortal/auth.ts`、
`src/api/unifiedPortal/buildOperationH5AppContext.ts`、
`src/components/NewHomeScreen/patrol/patrolBridgeHandlers.ts`。

H5 消费参考（`busyming-operation-vue-h5`）：`bridge/bridge.ts`、
`hooks/useAppCameraBridge.ts`、`hooks/useFileOpen.ts`、`utils/storeOperation.ts`、
`pages/clockIn/utils/scanCode.ts`、`pages/storInspection/utils/patrolBridge.ts`、
`pages/storInspection/utils/appLifecycleBridge.ts`、
`pages/storInspection/utils/reportShareImage.ts`。

App 若修改 `WebViewScreen` 注入脚本、`bridgeConfig`、统一门户上下文结构或回调格式，
需同步更新本文件并在 iOS / Android 真机重新验收。
