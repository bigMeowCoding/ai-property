# Mock 体系细节

参考项目 `busyming-store-opening-h5` 的 Mock 体系实测口径。命令开关与挂载方式见
[../templates/vite-config-snippets.md](../templates/vite-config-snippets.md)，模块模板见
[../templates/mock-modules.md](../templates/mock-modules.md)。

## 1. 插件行为：vite-plugin-mock-dev-server v1

- **无 enabled 选项**：关闭 Mock 靠不挂载插件（`useMock` 条件展开），不是传 `enabled: false`。
- **prefix 必须显式指定**：`server.proxy` 各项均带 `ws: true`，插件会将其归入 ws 通道，
  导致默认推导的 http 前缀为空而**静默穿透**（插件 v1.8.4 源码 `ensureProxies` 行为）。
  hr-h5 的 prefix 由 `src/config/devServerPrefixes.ts` 单一来源派生（`MOCK_PREFIXES` =
  `BUSINESS_PREFIXES` + `/api`）。
- **集中单入口 + 关闭默认日志**：挂载采用 `include: ['mock/index.mock.ts']` 只加载集中
  路由入口，并配 `log: false`（路由入口自己只输出 method/path/耗时，避免插件默认打印
  完整请求体）。
- **helper 子路径导入坑**：mock 编译产物的 renamePlugin 会把对插件**主入口**的导入
  改写为 external 的 helper 子路径（`vite-plugin-mock-dev-server/helper`）；若经
  vite.config 被插件 default import 污染的模块（如前缀清单）在 Node 直接 import 时
  可能抛 SyntaxError；主入口导入被改写为无 default export 的 helper 子路径会导致
  mock 整体失效（仅表现为 404）。前缀清单必须保持**纯常量模块零 import**，mock 文件
  内直接 import `vite-plugin-mock-dev-server/helper`。
- 插件先匹配集中路由表内已登记接口；未命中时由路由表内的 501 兜底路由处理（见 §2）。

## 2. 拦截与 501 兜底语义

Mock 模式下（`mockEnabled = env.VITE_APP_MOCK === 'true'`）：

- **已登记接口**：mock 集中路由表拦截，返回 mock 数据，控制台有 `[mock]` 日志。
- **未登记接口**：集中路由表内 `createFallbackRoutes` 生成 501 兜底路由（前缀 × 全
  HTTP method，`status: 501`，包体 `code: 'MOCK_NOT_IMPLEMENTED'`），**不透传真实
  网关**。Mock 模式本就未挂业务 proxy，若透传会打到无代理路径或错误环境，静默联真
  数据反而掩盖缺 mock 问题。
- **登录框前缀**（`MOCK_EXCLUDED_PREFIXES` 显式排除的 `/admin/api`、`/admin/user`）：
  不在 mock 拦截与 501 兜底范围，登录网关 proxy 无条件挂载、始终走真实登录网关。

兜底路由与 mock 定义**同处维护**（同一集中路由表），集中路由表同时作为 HTTP 行为
契约测试的公开契约（501 兜底行为可被契约测试覆盖）。

前缀清单收敛为 `src/config/devServerPrefixes.ts` **单一来源**：`BUSINESS_PREFIXES`
（业务前缀，dev proxy 与 mock 插件 prefix 的派生源）、`MOCK_PREFIXES`（=
`BUSINESS_PREFIXES` + `/api`，插件 prefix）、`MOCK_EXCLUDED_PREFIXES`（登录专用前缀，
显式排除在 mock 拦截与 501 兜底之外）。纯常量模块零 import，dev proxy、mock 插件
prefix 与 501 兜底路由全部由该清单派生，**结构性消除双口径漂移**（不再存在
「两个清单手动同步」问题）。

排查响应来源：

- 控制台 `[mock] METHOD /path · Nms` 日志 → mock 数据；
- 响应体 `code: 'MOCK_NOT_IMPLEMENTED'` + HTTP 501 → 未登记接口本地兜底；
- Network 面板出现对真实网关的请求 → 前缀漏配或兜底逻辑被破坏。

## 3. 权限接口 mock

- **mock user-auth 双接口**（hr-h5 已落地形态）：权限资源接口化，dev:mock 只 mock
  `POST /user-auth/web/app/resource/tree/by/app/id` 与
  `POST /user-auth/web/user/resource/list/by/app`，与真实模式同代码路径（mock 身份
  就绪即接口求交）。合成资源树（页面 type=2 + 按钮 type=3）与 resourceIds 严格对应，
  经 `resolveOwnedPermissionCodes` 求交得到完整权限码集合——合成的是**合法权限输入**，
  不是绕过权限系统。fixture 数据（如 `devMockPermissionContext`）只作为 mock 接口的
  **返回数据源**，不直写权限上下文。模板见 [../templates/mock-modules.md](../templates/mock-modules.md) §2
  （参考项目当前为 `devMockPermissionContext.ts` 本地合成，过渡形态）。

## 4. 带日志 defineMock 与 StrictMode

- `mock/helpers.ts` 的 `defineMock` 是 `createDefineMock` 包装：每条 mock 命中自动
  打印请求参数与响应体（`[mock]` 前缀），联调排查响应来源的第一手段。
- `ok()` 包体 code 200 与 `request.ts` 的 `isBizSuccess` 对齐；`paginate()` 模拟分页
  切片（pageNo 从 1 开始，返回数量 < pageSize 视为无更多）。
- **StrictMode 双挂载**：React 18 StrictMode 下组件双挂载会使 mock 日志 / 请求打两遍，
  属预期（React 双跑），与「业务重复请求」要区分；初始化类副作用放模块级单次执行。

## 5. Mock 契约口径

- 契约口径以 `src/service/**/types.ts` 为准；mock 文件头注明「未定义接口本地 501、
  联调真实接口切 dev:real / dev:realTest、无需删除 mock 文件」。
- 列表按钮组等下发口径与设计稿/后端不一致时，在 mock 文件内注释裁定依据（findings
  编号或日期），避免后续误改。
