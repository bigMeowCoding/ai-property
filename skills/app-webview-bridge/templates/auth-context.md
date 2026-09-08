# 模板：等待 App 上下文后启动 H5

适用于接入公共异步上下文桥的新 H5。先从
[权威文档附录 A](../reference/app-bridge-api.md) 复制全局 TypeScript 声明为
`app-bridge.d.ts`，并确保被 `tsconfig.json` 包含。

本模板不依赖 Vue 或 React，也不轮询。它不把旧 `window.__APP_CONTEXT__` 当成新桥的
就绪证明。

## `app-context.ts`

```ts
export function getAppContext(timeoutMs = 15000): Promise<ReadyAppContext> {
  if (typeof window === 'undefined') {
    return Promise.reject(Object.assign(new Error('请在客户端获取 App 上下文'), {
      code: 'BRIDGE_UNAVAILABLE',
    }))
  }

  return new Promise((resolve, reject) => {
    let started = false
    let settled = false

    const cleanup = () => {
      window.clearTimeout(timer)
      window.removeEventListener('app-context-bridge-ready', start)
      window.removeEventListener('pagehide', leave)
    }

    const finish = (value: ReadyAppContext | null, error?: unknown) => {
      if (settled) return

      settled = true
      cleanup()

      if (error) reject(error)
      else if (value) resolve(value)
      else reject(new Error('App 未返回上下文'))
    }

    const start = () => {
      if (started || settled || typeof window.__APP_GET_CONTEXT__ !== 'function') return

      started = true

      try {
        window.__APP_GET_CONTEXT__().then(
          context => finish(context),
          error => finish(null, error),
        )
      } catch (error) {
        finish(null, error)
      }
    }

    const leave = () => finish(null, Object.assign(new Error('页面已离开'), {
      code: 'PAGE_CHANGED',
    }))

    const timer = window.setTimeout(() => finish(null, Object.assign(
      new Error('获取 App 上下文超时，请重试或确认 App 版本'),
      { code: 'CONTEXT_TIMEOUT' },
    )), timeoutMs)

    window.addEventListener('app-context-bridge-ready', start)
    window.addEventListener('pagehide', leave)
    start()
  })
}
```

`timeoutMs` 只限制 H5 的总等待，不会改变 App 内部的构建和桥等待时限。

## 启动入口

`business-entry.ts` 由接入方实现，并导出 `mount(context)`。延迟导入可以避免业务模块在
上下文就绪前把空 Token 缓存在模块顶层。

```ts
import { getAppContext } from './app-context'

function showInitFailure(): void {
  const panel = document.createElement('div')
  const message = document.createElement('p')
  const retry = document.createElement('button')

  message.textContent = '初始化失败，请确认 App 版本、网络和页面接入配置后重试。'
  retry.textContent = '重新加载'
  retry.onclick = () => window.location.reload()

  panel.append(message, retry)
  document.body.appendChild(panel)
}

async function start(): Promise<void> {
  try {
    const context = await getAppContext()

    // 仅兼容仍读取同步字段的旧业务；这不是持续订阅。
    window.__APP_CONTEXT__ = context

    const { mount } = await import('./business-entry')
    await mount(context)
  } catch (error) {
    const code = (error as { code?: string })?.code

    if (code === 'PAGE_CHANGED') return

    // 只记录脱敏错误码，不输出完整 error 或上下文。
    showInitFailure()
  }
}

void start()
```

在 `mount` 内按语义分别配置客户端和权限：

```ts
export async function mount(context: ReadyAppContext): Promise<void> {
  const businessToken = context.personnel.accessToken.trim()
  const portalToken = context.unifiedPortal.accessToken.trim()

  if (!businessToken) throw new Error('缺少原业务认证')
  if (!portalToken) throw new Error('缺少统一门户认证')

  configureBusinessClient({ Authorization: `Bearer ${businessToken}` })
  configurePortalClient({ Authorization: `Bearer ${portalToken}` })

  const canUsePersonnel = (code: string) => context.personnel.permissionCodes.includes(code)
  const canUsePortal = (code: string) => context.portalAuthObj.portalAuthCodes.includes(code)
  const ownsPortalResource = (id: string | number) => (
    context.portalAuthObj.resourceIds.some(owned => String(owned) === String(id))
  )

  await initializeBusiness({ context, canUsePersonnel, canUsePortal, ownsPortalResource })
  mountFrameworkApp()
}
```

上例只展示如何选认证头；若统一门户接口还要求 MSE、设备头或 `X-Operate-Info`，必须按
该后端合同补全，不能把拿到 Token 解释为已具备完整签名能力。

## 错误与重试

- `BRIDGE_UNAVAILABLE`：确认 App 环境、安装包版本和桥安装时机。
- `CONTEXT_TIMEOUT` / `AUTH_TIMEOUT` / `NETWORK_ERROR`：显示重试，不能清 App 登录态。
- `UNTRUSTED_PAGE`：核对最终地址及可信路径配置，不能绕过校验。
- `UNSUPPORTED_CONTEXT`：这是专用 `route.params.appContext` 入口，继续用其专用协议。
- `SESSION_CHANGED` / `APP_USER_CONTEXT_MISSING` / `PERSONNEL_TOKEN_MISSING`：停止使用旧快照，
  按约定重新打开或登录。
- `AUTH_FORBIDDEN` 或正常空权限：展示无权限，不轮询权限数组。
- 门户 401：最多重新取一次上下文检查快照；不要假设这是强制刷新 Token，也不要自动重放
  有副作用的请求。

确认原业务登录确实失效后，可用模块级标志收敛并发跳转：

```ts
let loginRequested = false

export function requestAppRelogin(): void {
  if (loginRequested) return

  if (typeof window.__APP_GO_LOGIN__ !== 'function') {
    throw new Error('当前环境不能唤起 App 登录，请返回 App 重新登录')
  }

  loginRequested = true
  window.__APP_GO_LOGIN__()
}
```

`__APP_GO_LOGIN__()` 会清用户相关登录缓存并把 App 重置到登录页；不要用于一般网络失败，
也不要承诺登录后自动回到原 H5。

## 开发环境

普通浏览器使用单独、脱敏的 Mock 对象调用 `mount(mockContext)`。不要复制真实 Token、
用户资料、资源树或完整上下文到源码、长期存储、日志、截图和文档。
