# localDebug 模块族模板（可选辅助，非必选）

> **定位**：真实联调的主通道是本地登录框（npm 包 `busyming-operation-app-h5-login`，
> 见 [local-login-modules.md](local-login-modules.md)）。localDebug 仅在「不想走短信
> 验证码」时作为快捷替代，只提供身份三件套（authToken / userInfo / deviceInfo），
> 权限统一走接口（不携带资源快照）——但它要求目标项目额外引入配置单文件 +
> 校验门禁 + vConsole 复制插件 + 构建边界插件一整套模块族，改造成本高于登录框，且
> 快照 token 短期过期需反复复制。以登录框为主通道的精简形态**不需要**本模板。

真实联调（`dev:real` / `dev:realTest`）在纯浏览器拿不到 App 注入的身份，需要一套
本地联调配置链路。参考项目模块族：**配置单文件 → 间接引用加载器 → 校验与请求门禁
→ vConsole 复制工具 → setupApp 注入**。

## 1. src/config/localDebug.ts（受跟踪配置单文件）

含 token 等敏感值但受跟踪（依据工程原则窄例外：只允许短期有效、非生产环境的本地
联调 Token）。文件头注明来源与约束：

```ts
/**
 * 本地联调配置（受跟踪单文件）。依据工程原则 v1.7.1 的窄例外，仅允许短期有效、
 * 非生产环境的本地联调 Token；禁止生产 Token、密钥或 App Secret。
 * 只提供身份三件套（token / 用户 / 设备），权限统一走 user-auth 接口，不含资源快照。
 * 在目标环境 App vConsole「本地联调」复制配置后粘贴到本文件并刷新页面。
 */
const localDebugConfig = {
  /** 统一门户登录 token（Bearer 后的部分，或带 Bearer 前缀均可） */
  authToken: 'PASTE_FROM_VCONSOLE',

  /** 用户信息（可选，部分页面可能依赖） */
  userInfo: {
    userId: 9008,
    userName: '刘军',
    isGrayUser: false
  },

  /** 设备信息（可选，MSE 验签需要，留空则走 mse.ts 的默认值） */
  deviceInfo: {
    id: 'd623fb26f7d942df',
    type: 'APP',
    platform: 'AND',
    appVersion: '2.1.8',
    systemVersion: '16',
    model: 'VOL-AL00',
    deviceName: 'Android'
  }
}

export default localDebugConfig
```

## 2. src/config/localDebugLoader.ts（间接引用加载器）

`import.meta.glob` 间接引用：直接 `import localDebugConfig from './localDebug'` 会被
静态分析、Mock/构建阶段无法排除；glob 引用让 `localDebugLoaderBoundaryPlugin`
（见 [vite-config-snippets.md](vite-config-snippets.md) §3）在 Mock 与构建阶段把
本文件替换为空模块。

```ts
/** 仅真实接口开发服务器读取公共入口；Mock 与生产构建会替换为空模块。 */
import type { LocalDebugConfig } from '@/helpers/localDebugContext'

const modules = import.meta.glob<{ default: LocalDebugConfig }>('/src/config/localDebug.ts', { eager: true })

export default modules['/src/config/localDebug.ts']?.default
```

`.gitignore` 只排除个人私有配置（公共快照受跟踪）：

```gitignore
# 个人本地联调凭据（含 token，仅本机使用；加载器只读 localDebug.ts，该文件无代码引用）
src/config/localDebug.private.ts
```

## 3. src/helpers/localDebugContext.ts（字段校验 + 请求门禁）

校验只返回字段名不返回输入值；校验不过不留下可用 token，请求层直接阻断。

```ts
/** 浏览器真实联调配置的边界校验与请求门禁；不打印原始上下文。 */
import type { AppDeviceInfo } from '@/helpers/appBridge'

export interface LocalDebugConfig {
  authToken?: string
  userInfo?: { userId?: string | number; userName?: string; userPhone?: string; isGrayUser?: boolean }
  deviceInfo?: AppDeviceInfo | null
}

let localDebugIssue: string[] | null = null
let localDebugToken = ''

/** 校验本地真实联调所需的同账号上下文；仅返回字段名，不返回任何输入值。 */
export function getMissingLocalDebugFields(raw: unknown): string[] {
  const config = raw && typeof raw === 'object' ? (raw as LocalDebugConfig) : {}
  const missing: string[] = []

  if (typeof config.authToken !== 'string' || !config.authToken.trim()) missing.push('authToken')

  if (!config.userInfo || !String(config.userInfo.userId ?? '').trim()) missing.push('userInfo.userId')

  if (!config.userInfo || typeof config.userInfo.userName !== 'string' || !config.userInfo.userName.trim()) {
    missing.push('userInfo.userName')
  }

  if (
    !config.deviceInfo ||
    typeof config.deviceInfo !== 'object' ||
    Array.isArray(config.deviceInfo) ||
    Object.keys(config.deviceInfo).length === 0
  ) {
    missing.push('deviceInfo')
  }

  return missing
}

/** 初始化阶段同步建立请求门禁；无效配置不会留下可用 token。 */
export function validateLocalDebugConfig(raw: unknown): string[] {
  const missing = getMissingLocalDebugFields(raw)

  localDebugIssue = missing.length ? missing : null
  localDebugToken = missing.length ? '' : (raw as LocalDebugConfig).authToken!.trim()

  return missing
}

/** 请求层只读取当前已通过校验的本地 token；App 与 Mock 模式会清空本状态。 */
export function getLocalDebugToken(): string {
  return localDebugToken
}

/** 返回需要阻断请求的缺失字段，null 表示当前没有本地配置错误。 */
export function getLocalDebugIssue(): string[] | null {
  return localDebugIssue
}

/** 切换为 App/Mock 来源时清除本地凭证与诊断。 */
export function resetLocalDebugSession(): void {
  localDebugIssue = null
  localDebugToken = ''
}
```

`src/utils/request.ts` 请求拦截器接入（DEV 下配置缺失直接阻断，不留旧 token）：

```ts
const localDebugIssue = getLocalDebugIssue()

if (import.meta.env.DEV && localDebugIssue) {
  throw new RequestError({ message: `本地真实联调配置缺失：${localDebugIssue.join(', ')}` })
}

// token 解析：本地联调 token（已校验）> URL authToken > store authToken
const resolveAuthToken = () =>
  getLocalDebugToken() ||
  new URLSearchParams(window.location.search).get('authToken') ||
  useGlobalState.getState().authToken
```

## 4. src/helpers/appContextDebugConfig.ts + vConsole 复制插件

真机 App 内一键把 `__APP_CONTEXT__` 快照转成 localDebug 配置文本，避免手工拼 token。
缺失字段只暴露字段名，不打印原始上下文。

```ts
/** 从一次 App 注入快照生成本地联调配置；不持久化、不记录原始上下文。 */
import { resolveDeviceInfo, type AppContext, type AppDeviceInfo } from './appBridge'

import type { LocalDebugConfig } from './localDebugContext'

/** 边界校验失败只暴露字段名，避免调试提示意外携带凭证。 */
export function buildLocalDebugConfig(ctx: AppContext | null): { config?: LocalDebugConfig; missingFields: string[] } {
  const missingFields: string[] = []
  const token = ctx?.unifiedPortal?.accessToken
  const user = ctx?.unifiedPortal?.userInfo
  const rawDevice = ctx ? resolveDeviceInfo(ctx) : null
  let device: AppDeviceInfo | null = null

  if (typeof rawDevice === 'string') {
    try {
      const parsed: unknown = JSON.parse(rawDevice)

      if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) device = parsed as AppDeviceInfo
    } catch {
      // App 可预序列化设备；无法解析时按缺项处理，不混用其他来源。
    }
  } else {
    device = rawDevice
  }

  if (typeof token !== 'string' || !token.trim()) missingFields.push('unifiedPortal.accessToken')
  if (!user || (typeof user.id !== 'number' && typeof user.id !== 'string') || !String(user.id).trim()) {
    missingFields.push('unifiedPortal.userInfo.id')
  }

  if (!user || typeof user.nickName !== 'string' || !user.nickName.trim()) {
    missingFields.push('unifiedPortal.userInfo.nickName')
  }

  if (!device || !Object.keys(device).length) missingFields.push('deviceInfo')

  if (missingFields.length) return { missingFields }

  return {
    config: {
      authToken: token!.trim(),
      userInfo: { userId: user!.id, userName: user!.nickName },
      deviceInfo: device
    },
    missingFields
  }
}
```

`src/helpers/vConsole.ts` 注册「本地联调」插件（只在已确认的 App WebView 提供）：

```ts
const DEBUG_PLUGIN_ID = 'local-debug-config'

/** 只在已确认的 App WebView 中提供含个人凭证的主动复制入口。 */
const canCopyAppDebugConfig = () =>
  import.meta.env.MODE !== 'prod' &&
  window.__BUSYMING_OPERATION_APP__ === true &&
  typeof window.ReactNativeWebView?.postMessage === 'function'

/** 用户显式操作后才生成完整文本；失败提示只含字段名或固定文案。 */
export async function copyAppDebugConfig(): Promise<string> {
  if (!canCopyAppDebugConfig()) return '仅非生产 App WebView 可复制联调配置'

  const { config, missingFields } = buildLocalDebugConfig(getAppContext())

  if (!config) return `缺少字段：${missingFields.join('、')}`

  try {
    const text = `export default ${JSON.stringify(config, null, 2)}\n`

    if (typeof window.__APP_COPY_TEXT__ === 'function') {
      window.__APP_COPY_TEXT__(text)
    } else if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
    } else {
      return '当前 App 不支持复制，请升级 App'
    }

    return '已复制，请粘贴到 src/config/localDebug.ts 并刷新本地页面'
  } catch {
    return '复制失败，请检查 App 版本或上下文数据'
  }
}
```

## 5. src/helpers/setupApp.ts 注入骨架（仅保留 localDebug 链路时需要）

身份链：登录页短路 → App 免登 → URL 参数兜底 → 本地登录会话（主通道）→ localDebug
校验链路（可选回退）。localDebug 仅在「DEV + 非 Mock + 无 App Context + 无登录会话」
生效，校验通过才写入 store：

```ts
const useLocalDebug = import.meta.env.DEV && !useMock && browserWithoutAppContext

// 会话命中时跳过 localDebug 校验链路（会话即完整身份）
const missingFields = !hasLocalLoginSession && useLocalDebug ? validateLocalDebugConfig(localDebugConfig) : []

// localDebug 是可选回退：仅无会话且配置完整时写入，不得覆盖会话身份
const useLocalDebugFallback = useLocalDebug && missingFields.length === 0 && !hasLocalLoginSession

if (useLocalDebugFallback && localDebugConfig) {
  useGlobalState.getState().setAuthToken(localDebugConfig.authToken!.trim())
  useGlobalState.getState().setCurrentUserInfo({
    userId: localDebugConfig.userInfo!.userId!,
    userName: localDebugConfig.userInfo!.userName!,
    userPhone: localDebugConfig.userInfo!.userPhone,
    isGrayUser: localDebugConfig.userInfo!.isGrayUser === true
  })
  useGlobalState.getState().setDeviceInfo(localDebugConfig.deviceInfo!)
}

// 权限引导：接口通道为主（登录态就绪即 user-auth 双接口求交，fail-closed）；
// localDebug 只注入身份三件套，不提供权限快照与调试覆盖
bootstrapPermissions(undefined, undefined, undefined, hasLocalLoginSession)
```

## 6. 与本地登录框的关系

登录框已取代 localDebug 成为浏览器真实联调的主通道：

- 本地登录框：浏览器内手机号 + 验证码真实登录，token 由登录链路动态签发（带登录
  签发设备），是主通道；接入成本低（npm 包 + 薄包装页 + 代理），见
  [local-login-modules.md](local-login-modules.md)。
- localDebug：粘贴 App 快照（仅身份三件套，权限统一走接口），适合快速恢复某个
  账号的上下文；token 短期过期后需重新复制。仅在目标项目选择同时保留两条链路时
  引入，且登录框会话命中时 localDebug 不生效并跳过校验。
