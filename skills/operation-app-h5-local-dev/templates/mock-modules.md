# Mock 模块族模板

参考项目 `busyming-store-opening-h5` 的 `mock/` 目录模块模板。文件名**不含**
`.mock.`（避免被插件当作 mock 定义收集）。

## §1 helpers.ts（带日志 defineMock + ok + paginate）

```ts
/**
 * Mock 共用工具（dev 专用，由 vite-plugin-mock-dev-server 随 mock 文件加载）
 * 文件名刻意不含 `.mock.`，避免被插件当作 mock 定义收集
 */
import { createDefineMock } from 'vite-plugin-mock-dev-server'

import type { MockHttpItem, MockRequest } from 'vite-plugin-mock-dev-server'

/**
 * 带请求日志的 defineMock：用法与官方 defineMock 完全一致
 * 每条 mock 命中时自动打印请求参数与响应体，便于 dev 联调排查
 */
export const defineMock = createDefineMock((mock) => {
  const httpMock = mock as MockHttpItem

  if (typeof httpMock.body !== 'function') return

  const { url } = httpMock
  const originalBody = httpMock.body

  httpMock.body = (req: MockRequest) => {
    const startAt = Date.now()
    const payload = req.body ?? req.query ?? {}
    const print = (res: unknown) => {
      // eslint-disable-next-line no-console -- mock 日志用途，仅 dev 环境生效
      console.log(
        `[mock] ${req.method} ${url} · ${Date.now() - startAt}ms`,
        '\n  request:',
        payload,
        '\n  response:',
        res
      )
    }

    const result = originalBody(req)

    if (result instanceof Promise) {
      return result.then((res) => {
        print(res)

        return res
      })
    }

    print(result)

    return result
  }
})

/** 网关业务成功包体：与 src/utils/request.ts 的 isBizSuccess 判定对齐（code 200/0 为成功） */
export function ok<T>(data: T) {
  return { code: 200, msg: 'success', data }
}

/**
 * 模拟分页切片，与后端契约一致：
 * - pageNo 从 1 开始，缺省视为第 1 页；pageSize 缺省 20
 * - 调用方按「返回数量 < pageSize 视为无更多」判定分页终止
 */
export function paginate<T>(list: T[], pageNo?: number, pageSize?: number): T[] {
  const currentPage = pageNo && pageNo > 0 ? pageNo : 1
  const size = pageSize && pageSize > 0 ? pageSize : 20
  const start = (currentPage - 1) * size

  return list.slice(start, start + size)
}
```

接口定义骨架（前缀必须在 vite.config 的 mock `prefix` 内）：

```ts
/**
 * xxx 接口 Mock（dev 专用，契约口径以 src/service/xxx/types.ts 为准）
 *
 * - pnpm dev（VITE_APP_MOCK=true）时由 vite-plugin-mock-dev-server 加载；
 *   未定义的业务接口由本地兜底返回 501，不透传真实网关。
 * - 联调真实接口使用 pnpm dev:real / pnpm dev:realTest，无需删除本文件。
 */
import { defineMock, ok } from './helpers'

export default defineMock([
  {
    url: '/store-activity/web/ae/app/activity/home/badge',
    method: 'POST',
    body: () => ok({ count: 2 })
  }
])
```

## §2 mock user-auth 双接口（权限资源接口化）

Mock 模式没有真实用户，但权限引导应与真实模式走**同一代码路径**：user-auth
双接口实时求交（`resolveOwnedPermissionCodes`），只需 mock 掉这两个接口，不再
本地合成权限上下文（hr-h5 已按本模板落地：fixture 数据只作为 mock 接口的返回数据源；
参考项目当前 `devMockPermissionContext.ts` 为过渡形态）。

双接口契约（以 `src/service/permission/types.ts` 为准）：

| 接口                                              | 请求体            | 响应 `data`                                   |
| ------------------------------------------------- | ----------------- | --------------------------------------------- |
| `POST /user-auth/web/app/resource/tree/by/app/id` | `{ appCode }`     | 应用全量资源树 `PermissionResourceTreeNode[]` |
| `POST /user-auth/web/user/resource/list/by/app`   | `{ id, appCode }` | `{ resourceIds: Array<number                  | string> }` |

```ts
/**
 * user-auth 权限双接口 Mock（dev 专用）。
 *
 * 与真实模式同代码路径：权限引导走接口通道求交，Mock 模式只需合成身份
 * （authToken / userId）让接口通道前置校验通过，权限码由本文件返回的
 * 资源树 × resourceIds 求交得出。
 */
import { PAGE_PERMISSION, BUTTON_PERMISSION } from '@/service/activity/permissionCodes'
import { defineMock, ok } from './helpers'

// 合成资源树必须是合法权限树：页面 type=2 挂按钮 type=3，
// resourceIds 与树节点 id 一致（经 resolveOwnedPermissionCodes 求交）
const MOCK_RESOURCE_TREE = [
  {
    id: 990000,
    code: PAGE_PERMISSION.home, // 权限码：permissionCodes 常量，与权限系统建档码逐字一致
    name: '[DEV MOCK] 首页',
    type: 2,
    uri: '/subapp/store-opening-h5',
    appId: 990040,
    children: Object.entries(BUTTON_PERMISSION.home).map(([buttonName, code], i) => ({
      id: 991000 + i,
      code,
      name: `[DEV MOCK] ${buttonName}`,
      type: 3,
      appId: 990040
    }))
  }
  // ...按目标项目页面补齐
]
const MOCK_RESOURCE_IDS = MOCK_RESOURCE_TREE.flatMap((page) => [
  page.id,
  ...(page.children ?? []).map((child) => child.id)
])

export default defineMock([
  {
    url: '/user-auth/web/app/resource/tree/by/app/id',
    method: 'POST',
    body: () => ok(MOCK_RESOURCE_TREE)
  },
  {
    url: '/user-auth/web/user/resource/list/by/app',
    method: 'POST',
    body: () => ok({ resourceIds: MOCK_RESOURCE_IDS })
  }
])
```

配套改造要点：

- **合成身份**：接口通道前置校验要求 `authToken` 与合法 `userId`（见
  [local-login-modules.md](local-login-modules.md) §4.3）。Mock 模式只注入 mock 身份
  （token / userId / 设备），**不本地合成权限**：mock 身份满足接口通道前置后，经
  user-auth 双接口实时求交（mock 路由表拦截，与 dev:real 同代码路径）。
- **mock 身份开关 4d 形态**：注入入口用 `VITE_APP_DEV_MOCK_AUTH` 门控（`env.isDev &&
env.devMockAuth`），vite.config 在 mock 模式启动时强制置位
  （`if (mockEnabled) process.env.VITE_APP_DEV_MOCK_AUTH = 'true'`）——test mode 复用
  mock 同样生效，不依赖开发者手工配置 `.env`。
- 权限码必须从 `permissionCodes.ts` 常量导入拼接（与权限系统建档码逐字一致，见
  [../reference/permission-consumption.md](../reference/permission-consumption.md) §1），
  不手写字符串。
