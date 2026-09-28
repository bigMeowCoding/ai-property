# 本地登录框接入模板（busyming-operation-app-h5-login）

本地登录调试链路已收敛为 npm 包 `busyming-operation-app-h5-login`（hr-h5 依赖
`^0.1.2`，参考项目 `^0.1.0`），宿主项目只保留**薄包装页 + setupApp 适配**。以下模板按包 README 与
`busyming-store-opening-h5` 实测整理；登录框仅用于 **DEV 路由**（`/devtool/local-login`），
**不可作为生产登录通道**。

定位：浏览器真实模式（非 Mock）的**主身份来源**。浏览器内手机号 + 验证码实时登录，
token 由登录链路动态签发且自带登录签发设备（无 localDebug 快照的过期/设备错配问题）。
在身份来源优先级链中排在 App Context 之后；若目标项目同时保留 localDebug 快照，
两者互斥且登录框优先——会话命中时 localDebug 不生效并跳过其校验。

## 1. 安装与入口

```bash
pnpm add busyming-operation-app-h5-login
```

| 入口                                    | 消费内容                                        | 需要的 peer                                        |
| --------------------------------------- | ----------------------------------------------- | -------------------------------------------------- |
| `busyming-operation-app-h5-login`       | core：登录服务 / 会话存取 / MSE 签名 / 密码哈希 | 无（axios / crypto-es 为硬依赖）                   |
| `busyming-operation-app-h5-login/react` | antd-mobile 登录框                              | react / react-dom / antd-mobile >= 5 / ahooks >= 3 |
| `busyming-operation-app-h5-login/vue`   | vant 登录框                                     | vue >= 3.4 / vant >= 4                             |

core 入口关键导出（完整清单以包 `dist/index.d.ts` 为准）：

```ts
export { RequestError } from './core/requestError'
export { applyMseSignature } from './core/mseSignature' // MSE 签名单一真源，业务链也复用
export type { MseSignatureOptions } from './core/mseSignature'
export { hashLoginPassword } from './core/passwordHash'
export { createLocalLoginSessionStore, DEFAULT_LOCAL_LOGIN_SESSION_STORAGE_KEY } from './core/session'
export type { LocalLoginSession, LocalLoginSessionStore } from './core/session'
export {
  fetchLocalUnifiedToken,
  localLoginByPassword,
  localLoginByVerificationCode,
  sendLocalVerificationCode
} from './service/localLogin'
export { setLocalLoginToast, showLocalLoginToast } from './core/toast'
```

会话类型：`LocalLoginSession = { accessToken; userInfo: { userId; userName }; deviceInfo }`。
`deviceInfo` 必须是**登录签发设备**（find-unified-token 响应 `data.deviceInfo`）：
user-auth 网关校验 token 与设备绑定，换任何其他设备都会被判「登录已失效」。

## 2. vite 代理

登录链路接口需代理到 App 测试网关（`/admin/api`、`/admin/user`），在
`MOCK_EXCLUDED_PREFIXES` 显式排除（mock 拦截与 501 兜底不覆盖它们），**无条件挂载**
（登录前缀不在 mock 拦截范围，mock 模式同样生效）；地址抽 `LOCAL_LOGIN_PROXY_TARGET`
常量（与业务网关隔离、不随业务环境切换）。登录代理同样受网关来源头（`Origin` 与
`Referer` 双重）路由约束，必须复用带来源头改写的 `createProxyOptions`（见
[vite-config-snippets.md](vite-config-snippets.md) §2）——真机/局域网 IP 访问不改写
来源头会被登录网关拒收 500：

```ts
// vite.config.ts server.proxy（无条件挂载，位于 !mockEnabled 条件之外）
...Object.fromEntries(
  MOCK_EXCLUDED_PREFIXES.map(
    (prefix) => [prefix, createProxyOptions(LOCAL_LOGIN_PROXY_TARGET)] as [string, ProxyOptions]
  )
)
```

凭证（App Key / App Secret）放 `.env.local`（gitignore 排除，不进仓库）：

```bash
VITE_UNIFIED_APP_KEY=basic-test
VITE_UNIFIED_APP_SECRET=xxx
```

## 3. React 薄包装页 + DEV 路由

宿主页只做接线：凭证解析（`import.meta.env` 运行时读取）、会话保存、整页跳转。
登录框本体来自包 `/react` 入口：

> 登录框交互由包内实现（0.1.2 起）：发送验证码 60s 倒计时阻断；登录按钮请求中
> 展示 loading 并禁用阻断重复点击（React 版为组件自包含 CSS 动画点，不依赖
> antd-mobile DotLoading 与组件 CSS 文件，根因见 SKILL.md 避坑清单「MSE 签名与
> 登录包」）。

```tsx
/**
 * 本地开发登录框薄包装页（仅 DEV 路由 /devtool/local-login）。
 * 登录框本体来自 busyming-operation-app-h5-login/react；本页只做宿主接线：
 * 凭证解析（import.meta.env 运行时读取）+ 会话保存 + 整页跳转首页。
 */
import { createLocalLoginSessionStore, DEFAULT_LOCAL_LOGIN_SESSION_STORAGE_KEY } from 'busyming-operation-app-h5-login'
import { LocalLoginPreview } from 'busyming-operation-app-h5-login/react'

import { withAppBase } from '@/utils/env'

/** 本地登录会话仓库（与 setupApp 消费端 storageKey 一致） */
const localLoginSessionStore = createLocalLoginSessionStore(DEFAULT_LOCAL_LOGIN_SESSION_STORAGE_KEY)

function LocalLoginPreviewPage() {
  return (
    <LocalLoginPreview
      storageKey={DEFAULT_LOCAL_LOGIN_SESSION_STORAGE_KEY}
      resolveCredentials={() => ({
        appKey: import.meta.env.VITE_UNIFIED_APP_KEY || '',
        appSecret: import.meta.env.VITE_UNIFIED_APP_SECRET || ''
      })}
      onSuccess={(session) => {
        // 保存会话（含登录签发设备）后整页跳转首页：setupApp 重新识别会话注入身份与权限。
        localLoginSessionStore.save(session)
        window.location.replace(withAppBase('/'))
      }}
    />
  )
}

export default LocalLoginPreviewPage
```

路由仅 DEV 注册（懒加载，devtool 一族管理）：

```tsx
// src/router/routes.ts
const LocalLoginPreview = lazy(() => import('@/pages/devtool/LocalLoginPreview'))

// 本地开发登录框（仅 DEV 注册）：浏览器内手机号 + 验证码登录，走 App HR 登录链路
// 换统一门户 token，是真实联调（dev:real / dev:realTest）的主身份来源。
...(import.meta.env.DEV
  ? [{ id: 'devtool-local-login', path: '/devtool/local-login', Component: LocalLoginPreview }]
  : [])
```

## 4. setupApp 适配（三处改动）

1. **登录页短路**（放在最前）：登录页自身不需要身份，也不应触发 user-auth 请求，
   否则残留会话 / 过期 token 触发 401 弹「重新登录」、落点回登录页形成死循环：

   ```ts
   const isLocalLoginPage = import.meta.env.DEV && window.location.pathname === withAppBase('/devtool/local-login')

   if (isLocalLoginPage) {
     localLoginSessionStore.clear()
     useGlobalState.getState().clearAll()

     return null
   }
   ```

2. **会话识别与注入**（App 免登未命中、真实模式下）：会话命中时跳过 localDebug
   校验链路（仅保留 localDebug 时适用），注入会话自带设备（登录签发设备），
   localDebug 不得覆盖：

   ```ts
   const localLoginSession = !useMock && browserWithoutAppContext ? localLoginSessionStore.load() : null
   const hasLocalLoginSession = localLoginSession !== null

   if (localLoginSession) {
     useGlobalState.getState().setAuthToken(localLoginSession.accessToken)
     useGlobalState.getState().setCurrentUserInfo({
       userId: localLoginSession.userInfo.userId,
       userName: localLoginSession.userInfo.userName,
       isGrayUser: false
     })
     useGlobalState.getState().setDeviceInfo(localLoginSession.deviceInfo)
   } else {
     // 未命中会话（登录包真源已删/从未登录）必须清掉持久化副本再落无鉴权分支：
     // persist 在 store 创建时已同步恢复旧 token（早于启动链路），不清会让路由
     // 守卫误判已登录、跳过登录框引导（「真源已删、副本复活」伪登录态）。
     // App 免登命中即先于此处 return，persist 旧 token 对旧版 App 的容错不受影响。
     await clearDevLoginCache({ redirect: false })
   }
   ```

   会话读取（消费端）hr-h5 已落地形态——动态 import + `import.meta.env.DEV` 门禁：

   ```ts
   export async function loadLocalLoginSession(): Promise<LocalLoginSession | null> {
     if (!import.meta.env.DEV) return null

     const { createLocalLoginSessionStore, DEFAULT_LOCAL_LOGIN_SESSION_STORAGE_KEY } =
       await import('busyming-operation-app-h5-login')

     return createLocalLoginSessionStore(DEFAULT_LOCAL_LOGIN_SESSION_STORAGE_KEY).load()
   }
   ```

   生产构建 `import.meta.env.DEV` 常量折叠为 false 后，会话读取代码零进包（验收：
   dist grep 登录会话读取标识零匹配）；薄包装页静态 import（保存会话）与消费端动态
   import 构成双通道。签名 core 静态进生产主 chunk 属预期（见
   [../reference/real-gateway-debug.md](../reference/real-gateway-debug.md) §5）。

3. **权限引导走 user-auth 接口通道（接口调用为主）**：会话命中且无 App Context 时，
   权限从 user-auth 双接口实时求交（资源树 × 用户 resourceIds），异步落定；失败
   fail-closed 空权限。`bootstrapPermissions` 第四参 `hasLocalLoginSession` 传入该
   标记，不传本地合成 / 快照上下文：

   ```ts
   bootstrapPermissions(undefined, undefined, undefined, hasLocalLoginSession)
   ```

   接口通道实现骨架（前置校验 + 双接口并发求交 + fail-closed，可复制到
   `src/helpers/permissionBootstrap.ts`）：

   ```ts
   /** 权限接口封装：静默失败、5s 超时、跳过权限资源等待避免自等待死锁 */
   const PERMISSION_REQUEST_CONFIG = { hideErrorMessage: true, timeout: 5000, skipPageResourceContext: true }

   export function getResourceTreeByAppCode(appCode: string) {
     return commonRequest.post('/user-auth/web/app/resource/tree/by/app/id', { appCode }, PERMISSION_REQUEST_CONFIG)
   }

   export function getUserResourceIdsByApp(id: number, appCode: string) {
     return commonRequest.post('/user-auth/web/user/resource/list/by/app', { id, appCode }, PERMISSION_REQUEST_CONFIG)
   }

   /** 登录态就绪（authToken + 合法 userId）→ user-auth 双接口实时求交 */
   export async function resolvePermissionContextFromApi() {
     const { authToken, userInfo } = useGlobalState.getState()
     const userId = resolvePermissionUserId(userInfo?.userId) // 非空字符串再 Number 归一，非法返回 null

     if (!authToken || userId === null) {
       logFormat({ tip: '[permission] 登录态不齐（缺 authToken 或合法 userId），跳过 user-auth 接口，按无权限处理' })

       return null
     }

     try {
       const [tree, idsResp] = await Promise.all([
         getResourceTreeByAppCode(PERMISSION_APP_CODE),
         getUserResourceIdsByApp(userId, PERMISSION_APP_CODE)
       ])

       return {
         permissionKeys: resolveOwnedPermissionCodes(tree, idsResp?.resourceIds),
         resources: flattenPermissionResources(tree)
       }
     } catch (error) {
       logFormat({ tip: '[permission] user-auth 接口引导失败，按无权限处理', data: error })

       return null
     }
   }
   ```

   接口通道分支在 `bootstrapPermissions` 内：`hasLocalLoginSession && !appContext`
   时调用上述函数，成功提交求交结果（来源 `local-login`），失败提交空集合
   （来源 `none`），并始终置 `permissionReady` 防路由守卫永久等待。

   求交纯函数 `resolveOwnedPermissionCodes` / `flattenPermissionResources` 见
   [../reference/permission-consumption.md](../reference/permission-consumption.md) §4；
   双接口请求/响应契约与 dev:mock 的接口 mock 见
   [mock-modules.md](mock-modules.md) §2。

## 5. 避坑

- **设备绑定 401**：user-auth 网关按「token 与 x-Device-Info 设备绑定」校验，请求
  必须带登录签发设备。同一 token 带登录返回的 PC 设备（如 `ops-sso`）返回 200，
  带其他设备（localDebug 快照 / mse WEB 兜底）返回 401「登录已失效」或 400
  「设备ID不能为空!」。
- **登录页死循环**：setupApp 不短路登录页时，残留会话 / 过期 token 触发 user-auth
  401 → 弹「重新登录」→ 落点回登录页 → 旧会话再加载，永远无法登录。
- **跨账号混用**：身份来源切换（Mock ↔ 真实 ↔ App）必须清持久化 store 与会话，
  否则上一个账号的 token / 设备混入本次会话。
- **会话静默丢弃留痕**：sessionStorage 属跨系统边界，读取必须逐字段校验形态，
  解析失败 / 形态非法返回 null（按无会话处理）并留痕，不能静默回退 localDebug 过期 token。
- **进产物口径**：误以为「登录包整体必须零进包」→ 静态 import `applyMseSignature` 后
  登录包 core 进生产主 chunk 属预期；验收口径是「DEV 门控登录页/路由/会话读取标识
  dist grep 零匹配 + `x-ca-signature`/`HmacSHA256` 命中主 chunk」（见
  [../reference/real-gateway-debug.md](../reference/real-gateway-debug.md) §5）。
- **axios 版本类型断言**：登录包 axios 与宿主版本不一致时 `AxiosHeaders` 类型不兼容，
  传 `InternalAxiosRequestConfig` 需带注释类型断言；包内仅做 config.headers 普通字段
  读写、跨版本安全，宿主升级 axios 对齐后删除断言（见
  [../reference/real-gateway-debug.md](../reference/real-gateway-debug.md) §5）。
- **凭证不进仓库**：`VITE_UNIFIED_APP_KEY/SECRET` 放 `.env.local`；登录框路由仅 DEV
  注册，生产构建不可达。
