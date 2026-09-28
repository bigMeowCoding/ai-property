# vite 配置可复制片段

与参考项目 `busyming-store-opening-h5` 一致的本地开发配置片段，按目标项目结构调整
变量名与路径后可直接使用。

## §1 命令与端口释放脚本

`package.json` 脚本（`dev` 默认等价 dev:mock，命令内联注入值优先于 `.env`）：

```json
{
  "scripts": {
    "dev": "pnpm dev:mock",
    "dev:mock": "node scripts/free-dev-port.mjs && VITE_APP_MOCK=true vite",
    "dev:real": "node scripts/free-dev-port.mjs && VITE_APP_MOCK=false vite",
    "dev:realTest": "node scripts/free-dev-port.mjs && VITE_APP_MOCK=false vite --mode test"
  }
}
```

`scripts/free-dev-port.mjs`：`strictPort: true` 固定端口时端口冲突只能释放占用方
（占用方通常是上一轮未正常退出的 vite 实例），不能换端口。脚本先探测端口占用
（IPv6 双栈 + IPv4 双地址族，避免旧 vite 监听 `*:port` 产生假阴性），再用 `lsof`
定位占用 PID（过滤自身**完整祖先链**：脚本由 pnpm/vite 作为子进程拉起，只排除一层
父进程会漏杀 pnpm 导致启动失败），SIGTERM 温和终止 → 3s 内未释放再 SIGKILL：

```js
#!/usr/bin/env node
import { execSync } from 'node:child_process'
import net from 'node:net'

const port = Number(process.argv[2] || 8090)
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

function tryListen(targetPort, host) {
  return new Promise((resolve) => {
    const server = net.createServer()

    server.once('error', () => resolve(false))
    server.once('listening', () => server.close(() => resolve(true)))
    server.listen(targetPort, host)
  })
}

async function isPortInUse(targetPort) {
  for (const host of ['::', '0.0.0.0']) {
    if (!(await tryListen(targetPort, host))) return true
  }

  return false
}

function getOccupyingPids(targetPort) {
  try {
    return execSync(`lsof -ti tcp:${targetPort} -sTCP:LISTEN`, { encoding: 'utf8' })
      .trim()
      .split('\n')
      .filter(Boolean)
      .map(Number)
  } catch {
    return []
  }
}

function getSelfAndAncestorPids() {
  const pids = new Set([process.pid])
  let current = process.ppid

  // 完整 while 祖先链遍历：脚本由 pnpm/vite 作为子进程拉起，只取一层 ppid 会
  // 漏杀 pnpm 等父进程导致启动失败
  while (current && current > 1 && !pids.has(current)) {
    pids.add(current)

    try {
      current = Number(execSync(`ps -p ${current} -o ppid=`, { encoding: 'utf8' }).trim())
    } catch {
      break
    }
  }

  return pids
}

function describeProcess(pid) {
  try {
    return execSync(`ps -o command= -p ${pid}`, { encoding: 'utf8' }).trim().slice(0, 80)
  } catch {
    return 'unknown'
  }
}

function killProcess(pid, signal) {
  try {
    process.kill(pid, signal)
  } catch {
    /* 进程已退出 */
  }
}

async function main() {
  if (!(await isPortInUse(port))) return

  const selfChain = getSelfAndAncestorPids()
  const pids = getOccupyingPids(port).filter((pid) => !selfChain.has(pid))

  if (!pids.length) {
    console.warn(`⚠️  端口 ${port} 被占用但未能定位占用进程，请手动检查：lsof -i :${port}`)
    process.exit(1)
  }

  console.log(`⚠️  端口 ${port} 被占用，自动释放占用进程：`)
  pids.forEach((pid) => console.log(`  - PID ${pid}: ${describeProcess(pid)}`))

  pids.forEach((pid) => killProcess(pid, 'SIGTERM'))

  for (let i = 0; i < 10; i += 1) {
    if (!(await isPortInUse(port))) {
      console.log(`✅ 端口 ${port} 已释放`)
      return
    }

    await wait(300)
  }

  pids.forEach((pid) => killProcess(pid, 'SIGKILL'))
  await wait(500)

  if (await isPortInUse(port)) {
    console.error(`❌ 端口 ${port} 释放失败，请手动处理：lsof -i :${port}`)
    process.exit(1)
  }

  console.log(`✅ 端口 ${port} 已释放`)
}

main()
```

## §2 固定端口、来源头改写与业务代理

网关按来源头（`Origin` 与 `Referer` 双重）路由，只认恒定开发来源
`http://localhost:<端口>`，端口必须恒定（`strictPort`）。`changeOrigin` 只改写 Host
头、不改写浏览器真实来源头，而真机/局域网 IP 访问时浏览器发出的 `Origin`/`Referer`
为 IP 形态（GET 请求不带 `Origin` 头但必带 IP 形态 `Referer`），不改写会被登录网关
拒收 500、业务网关拒收 403 Invalid CORS request。因此所有 proxy 转发必须在 `proxyReq`
阶段把来源头改写为恒定开发 Origin（hr-h5 实测口径，见下方 `rewriteSourceHeaders`）。
业务前缀代理**仅真实模式挂载**（Mock 模式绝不代理业务请求，mock 插件已全量拦截）；
`/proxy-pdf` 等非业务资源恒挂载。登录框专用前缀 `/admin/api`、`/admin/user` 在
`MOCK_EXCLUDED_PREFIXES` 显式排除、**无条件挂载**（登录链路始终走真实登录网关，
mock 模式同样生效），地址抽 `LOCAL_LOGIN_PROXY_TARGET` 常量（与业务网关隔离，不随
业务环境切换）。前缀清单全部派生自 `src/config/devServerPrefixes.ts` 单一来源。

```ts
// vite.config.ts
import type { ClientRequest } from 'node:http'
import type { ProxyOptions } from 'vite'
// 前缀清单单一来源：纯常量模块零 import（不得导入插件主入口，renamePlugin 会把
// 主入口导入改写为 external helper 子路径，Node 直接 import 抛 SyntaxError）
import { BUSINESS_PREFIXES, MOCK_EXCLUDED_PREFIXES, MOCK_PREFIXES } from './src/config/devServerPrefixes'

const devPort = 8090
// 恒定开发 Origin：网关按来源头（Origin 与 Referer 双重）路由，仅认可 localhost
// 来源（实测局域网 IP 会被登录网关拒收 500、业务网关拒收 403 Invalid CORS request）。
const DEV_ORIGIN = `http://localhost:${devPort}`
// 登录链路专用网关：与业务网关隔离，不随业务环境切换（包升级不影响宿主代理地址）
const LOCAL_LOGIN_PROXY_TARGET = 'https://test-digital.hnlshm.com/gateway'
const mockEnabled = command === 'serve' && env.VITE_APP_MOCK === 'true'

/**
 * 把来源头（Origin/Referer）的 host 改写为恒定开发 Origin，保留原路径与查询串。
 * 网关同时按 Origin 与 Referer 校验来源：真机/局域网 IP 访问时浏览器发出的
 * Referer 为 IP 形态（GET 请求不带 Origin 头），不改写会被登录网关拒收 500。
 */
function rewriteSourceHeaders(proxyReq: ClientRequest): void {
  proxyReq.setHeader('Origin', DEV_ORIGIN)

  const referer = proxyReq.getHeader('Referer')
  if (typeof referer === 'string') {
    try {
      const url = new URL(referer)
      proxyReq.setHeader('Referer', `${DEV_ORIGIN}${url.pathname}${url.search}`)
    } catch {
      proxyReq.setHeader('Referer', DEV_ORIGIN)
    }
  }
}

/** 带来源头改写的代理配置工厂（业务代理与登录代理共用）。 */
function createProxyOptions(target: string, extra: Partial<ProxyOptions> = {}): ProxyOptions {
  return {
    target,
    changeOrigin: true, // 只改写 Host 头，不改写浏览器真实 Origin/Referer，来源头须显式改写
    configure: (proxy) => {
      proxy.on('proxyReq', (proxyReq) => {
        rewriteSourceHeaders(proxyReq)
      })
    },
    ...extra
  }
}

const BIZ_MID_SERVICE_PROXY_CONFIG = createProxyOptions(
  env.VITE_APP_PROXY_SERVE_URL || 'https://dev-gateway.busyming.com',
  { secure: false, ws: true }
)

export default defineConfig(({ mode, command }: ConfigEnv): UserConfig => {
  return {
    server: {
      host: '0.0.0.0',
      port: devPort,
      open: false,
      cors: true,
      strictPort: true, // 端口必须固定，网关按来源头路由依赖此值
      proxy: {
        // 业务前缀与 /api 仅真实模式挂载：mock 模式下这些前缀被 mock 插件全量拦截
        // （已登记返数据、未登记 501 兜底，见 mock/index.mock.ts），proxy 规则不被
        // 消费，挂载纯冗余且会掩盖「未登记接口静默穿透真实网关」隐患。
        ...(!mockEnabled
          ? {
              ...Object.fromEntries(BUSINESS_PREFIXES.map((prefix) => [prefix, BIZ_MID_SERVICE_PROXY_CONFIG])),
              // 负向断言仅属 proxy 侧（mock 插件 prefix 不支持负向断言），
              // 不进入 BUSINESS_PREFIXES 清单
              '^/api/(?!gateway)': BIZ_MID_SERVICE_PROXY_CONFIG
            }
          : {}),
        // 本地登录链路：无条件挂载（登录前缀不在 mock 拦截范围，mock 模式同样生效），
        // 走恒定登录网关地址（LOCAL_LOGIN_PROXY_TARGET）。登录链路同样受来源头路由
        // 约束，必须复用 createProxyOptions（带来源头改写）。
        ...Object.fromEntries(
          MOCK_EXCLUDED_PREFIXES.map(
            (prefix) => [prefix, createProxyOptions(LOCAL_LOGIN_PROXY_TARGET)] as [string, ProxyOptions]
          )
        ),
        '/proxy-pdf': {
          target: 'https://inv.jss.com.cn',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/proxy-pdf/, '')
        }
      }
    }
  }
})
```

## §3 501 兜底（mock 路由表 + 前缀清单单一来源）与 localDebug 构建边界插件

### 501 兜底（mock 集中路由表内 createFallbackRoutes）

业务前缀内未登记 mock 的接口**本地失败**，不跌入网关代理（Mock 模式本就未挂业务
proxy，若请求透传出去会打到无代理的 404 或被全局转发到错误环境）。hr-h5 已落地形态：
兜底路由与 mock 定义**同处维护**（同一集中路由表，可被契约测试覆盖），由前缀清单
单一来源派生（登录专用前缀显式排除）：

```ts
// src/config/devServerPrefixes.ts —— 纯常量模块零 import（不得导入 vite.config、
// 插件主入口或任何运行时依赖：renamePlugin 会把主入口导入改写为 external 的 helper
// 子路径，Node 直接 import 会抛 SyntaxError）。dev proxy、mock 插件 prefix 与 501
// 兜底路由全部由本清单派生。
export const BUSINESS_PREFIXES = ['/store-activity', '/web', '/user-auth', '/target-okr'] as const
export const MOCK_EXCLUDED_PREFIXES = ['/admin/api', '/admin/user'] // 登录专用前缀，始终走真实网关
export const MOCK_PREFIXES: string[] = [...BUSINESS_PREFIXES, '/api']
```

```ts
// mock/index.mock.ts —— 集中路由表内的 501 兜底路由：前缀 × 全 HTTP method，
// 未登记请求显式 501（包体 code: 'MOCK_NOT_IMPLEMENTED'），避免静默透传真实网关。
// 登录专用前缀（MOCK_EXCLUDED_PREFIXES）显式排除，保证登录链路始终走真实代理。
export const HTTP_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'TRACE', 'OPTIONS']

function createFallbackRoutes(prefixes: readonly string[]): MockHttpItem[] {
  return prefixes
    .filter((prefix) => !MOCK_EXCLUDED_PREFIXES.includes(prefix))
    .map((prefix) => ({
      url: `${prefix}/(.*)`,
      method: HTTP_METHODS,
      status: 501,
      statusText: 'Not Implemented',
      body: async (request: MockRequest) => ({
        code: 'MOCK_NOT_IMPLEMENTED',
        message: `本地 Mock 未实现 ${String(request.method)} ${String(request.url).split('?')[0]}`
      })
    }))
}

export const MOCK_ROUTES = defineSafeMock([
  // ...已登记接口定义
  ...createFallbackRoutes(MOCK_PREFIXES)
])
```

### localDebug 加载器边界（local-debug-loader-boundary，可选辅助）

> 仅在保留 localDebug 链路时需要；以登录框为主通道的项目无需此插件。

`localDebugLoader.ts` 用 `import.meta.glob` 间接引用 `localDebug.ts`（直接 import 会
被静态分析打进产物）。边界插件在 Mock 与生产构建阶段把加载器替换为空模块（避免读取
真实凭证），并在 `generateBundle` 兜底检查构建产物不包含 `localDebug.ts`：

```ts
/** Mock 与构建阶段把调试配置加载器替换为空模块，避免读取真实凭证。 */
function localDebugLoaderBoundaryPlugin(command: ConfigEnv['command'], useMock: boolean): Plugin {
  return {
    name: 'local-debug-loader-boundary',
    enforce: 'pre',
    transform(_code, id) {
      if ((command === 'build' || useMock) && id.split('?')[0].endsWith('/src/config/localDebugLoader.ts')) {
        return 'export default undefined'
      }

      return null
    },
    generateBundle(_options, bundle) {
      if (command !== 'build') return

      const hasLocalDebugModule = Object.values(bundle).some(
        (output) =>
          output.type === 'chunk' && Object.keys(output.modules).some((id) => id.endsWith('/src/config/localDebug.ts'))
      )

      if (hasLocalDebugModule) this.error('生产构建意外包含本地联调配置')
    }
  }
}
```

## §4 Mock 插件挂载

`vite-plugin-mock-dev-server` v1 无 `enabled` 选项，关闭时直接不挂载。`prefix` 必须
显式指定（由 `MOCK_PREFIXES` 单一来源派生）：`server.proxy` 各项均带 `ws: true`，
插件会将其归入 ws 通道，导致默认推导的 http 前缀为空而静默穿透（插件 v1.8.4 源码
`ensureProxies` 行为）。Mock 模式下插件先匹配集中路由表已登记接口，未命中由路由表内
501 兜底路由本地失败。挂载采用**集中单入口 `include` + `log: false`**（路由入口只
输出 method/path/耗时，避免插件默认打印完整请求体）：

```ts
plugins: [
  // 仅保留 localDebug 链路时挂载；登录框为主通道的形态无需
  localDebugLoaderBoundaryPlugin(command, mockEnabled),
  react(),
  // 本地接口 Mock：集中单入口加载路由入口；未登记业务接口由路由表内 501 兜底本地失败。
  ...(mockEnabled ? [mockDevServerPlugin({ prefix: MOCK_PREFIXES, include: ['mock/index.mock.ts'], log: false })] : []),
  subappBaseRedirectPlugin(appBase)
]
```

## §5 环境变量

`.env.development` 关键声明（命令注入值优先于本文件）：

```bash
# 本地接口 Mock 开关；pnpm dev 默认开启，未定义的业务接口本地返回 501，不透传网关。
# 真实接口联调使用 pnpm dev:real 或 pnpm dev:realTest，命令注入值优先于本文件。
VITE_APP_MOCK=true

# dev 下 request.ts 的 baseURL 恒为空、走 vite.config.ts 的 proxy，
# 此处的值仅用于 vite proxy 的 target
VITE_APP_PROXY_SERVE_URL=https://dev-gateway.busyming.com

VITE_APP_SHOW_VCONSOLE=true
VITE_APP_BASE_NAME=/subapp/store-opening-h5
```

`dev:realTest` 使用的 `.env.test` 声明 test 网关：

```bash
VITE_APP_PROXY_SERVE_URL=https://test-gateway.busyming.com
```
