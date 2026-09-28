---
name: operation-app-h5-local-dev
description: >-
  运营 App（busyming-operation-app）内嵌 H5 的浏览器本地开发模式落地规范，沉淀自
  参考项目 busyming-store-opening-h5 的实测实现。覆盖 dev:mock / dev:real /
  dev:realTest 多模式命令分离、固定端口与网关代理、vite-plugin-mock-dev-server
  本地 Mock 体系（已登记接口返数据、未登记业务前缀本地 501 失败）、真实联调主通道
  「本地登录框 npm 包 busyming-operation-app-h5-login 接入」（薄包装页 + DEV 路由 +
  登录代理 + setupApp 会话注入）、localDebug 可选辅助身份快照链路（受跟踪配置文件 +
  校验门禁 + vConsole 复制插件，非必选）、权限来源三级收敛（权限上下文判源防御路径 >
  user-auth 双接口正式来源 > fail-closed 空权限，dev:mock 只 mock 接口、localDebug 只带
  身份，减少本地配置化；hr-h5 实测回写口径）、按钮权限消费范式（权限码命名硬约束、
  usePermission/AuthButton、后端 buttons[] 数组驱动）、身份来源优先级与安全边界。
  适用于为新 H5 搭建本地开发环境、把存量 H5 改造为浏览器内可开发调试、或排查
  本地 Mock 未生效 / 登录框 401 / 端口冲突等问题；不覆盖 App↔H5 桥接契约本身
  （见 app-webview-bridge skill）。
---

# 运营 App 内嵌 H5 本地开发模式

内嵌在运营 App 的 H5 依赖 App 注入 `window.__APP_CONTEXT__` 完成免登（桥接契约见
`app-webview-bridge` skill），在纯浏览器里拿不到这些数据。本 skill 描述如何让这类 H5
**在浏览器里独立开发调试**，并把模式沉淀为可复制的工程结构，供其他 H5 改造落地。

参考实现：`busyming-store-opening-h5`（vite 6 + react 18 + pnpm，本 skill 所有文件路径
均指该项目的相对路径，改造时按目标项目结构平移）。`busyming-store-hr-h5`（hr-h5）已按
本 skill 完整落地本地开发模式，并在实测中形成多处更优口径（权限三级收敛、501 路由表
兜底与前缀清单单一来源、MSE 签名单一真源连带、日志脱敏规则废止等）；本 skill 已按
hr-h5 实测回写，各条目标注适用形态，参考项目的过渡形态表述保留为对照。

## 模式总览

| 模式             | 命令                                     | 数据来源                                                           | 适用阶段                    |
| ---------------- | ---------------------------------------- | ------------------------------------------------------------------ | --------------------------- |
| 本地 Mock        | `pnpm dev:mock`（`VITE_APP_MOCK=true`）  | `mock/` 集中路由表（已登记返数据、未登记 501 兜底）+ 权限接口 mock | 页面开发、UI 验收、前端自测 |
| 真实联调（dev）  | `pnpm dev:real`（`VITE_APP_MOCK=false`） | dev 真实网关 + 本地登录框会话身份（localDebug 为可选辅助）         | 前后端联调、契约验证        |
| 真实联调（test） | `pnpm dev:realTest`（`--mode test`）     | test 真实网关 + 本地登录框会话身份（localDebug 为可选辅助）        | 联调测试环境数据            |

- `pnpm dev` 不带注入值，以 `.env.development` 的 `VITE_APP_MOCK` 为准（参考项目默认
  `true`，即等价 dev:mock）。
- 三种模式共用同一套代码与 `mock/` 目录，切换命令即可，**不需要删除任何 mock 文件**。
- 所有 dev 命令前置 `node scripts/free-dev-port.mjs`：端口被占用时自动释放占用进程再
  启动，见 [templates/vite-config-snippets.md](templates/vite-config-snippets.md) §1。

## 核心决策（改造时必须遵守）

1. **命令分离**：`dev:mock` / `dev:real` / `dev:realTest` 是独立 pnpm script，靠环境
   变量 `VITE_APP_MOCK` 与 `--mode` 切换；命令内联注入值优先于 `.env` 文件。
2. **固定端口 + 严格端口**：`strictPort: true` 且端口恒定（参考项目 8090），因为
   网关按来源头（`Origin` 与 `Referer` 双重）路由且只认恒定开发来源
   `http://localhost:<端口>`，端口变化会导致网关找不到应用；端口被占用时只能释放占用方，
   不能换端口（free-dev-port.mjs 完成自动释放）。
3. **Mock 拦截语义 = 已定义拦截 + 未命中本地失败**：mock 插件 `prefix` 由
   `src/config/devServerPrefixes.ts` 单一来源派生（`MOCK_PREFIXES` = `BUSINESS_PREFIXES`
   - `/api`），已定义接口被 dev server 拦截；业务前缀内未定义的接口由 mock 集中路由表
     内的 `createFallbackRoutes` 501 兜底路由本地失败（前缀 × 全 HTTP method），
     **绝不透传真实网关**（缺 mock 不静默联真数据）；登录框专用前缀 `/admin/api`、
     `/admin/user` 在 `MOCK_EXCLUDED_PREFIXES` 显式排除，登录网关 proxy 无条件挂载、
     始终走真实登录网关。
4. **本地登录框是 npm 包接入（真实联调主通道）**：`busyming-operation-app-h5-login`
   （登录框组件、会话存取、发码/登录服务、MSE 签名核心单一真源），宿主只写薄包装页
   - DEV 路由 + `/admin/api`、`/admin/user` 代理。浏览器内手机号 + 验证码实时登录，
     token 由登录链路动态签发且自带登录签发设备，是浏览器真实联调（`dev:real` /
     `dev:realTest`）的主身份来源。见
     [templates/local-login-modules.md](templates/local-login-modules.md)。
5. **身份来源优先级固定**：App Context（免登）> 本地登录会话（登录框落定，真实模式
   主通道）> devMock 身份（仅 Mock 模式：只注入 token/userId/设备，权限不本地合成）；
   localDebug（可选辅助身份快照）仅保留该链路时在登录会话未命中后生效。URL 参数
   兜底已按 hr-h5 实测删除（474d4ab）。登录页自身短路跳过身份注入，防止 401 死循环。
   来源切换时清持久化残留状态；本地登录会话**未命中**（登录包真源已删/从未登录）时
   同样清 persist 旧 token 副本，防「真源已删、副本复活」伪登录态（见避坑清单）。
6. **localDebug 为可选辅助快照（非必选）**：`localDebug.ts`（受跟踪单文件）→
   `localDebugLoader.ts`（`import.meta.glob` 间接引用，Mock 与生产构建替换为空模块）→
   `localDebugContext.ts`（字段校验 + 请求门禁）→ `setupApp` 注入。它依赖 App vConsole
   「本地联调」复制插件产出的静态快照，token 短期过期需反复复制，改造成本高于登录框。
   它只提供身份三件套（authToken / userInfo / deviceInfo），权限统一走接口
   （不携带权限快照与调试覆盖；这两类设施已按工程裁决移除）；仅在「不想走短信验证码」
   时按需引入；以登录框为主通道的精简形态**不需要**该链路。见
   [templates/local-debug-modules.md](templates/local-debug-modules.md)。
7. **权限来源优先级收敛为三级（hr-h5 已落地口径）**：store 权限上下文判源（防御路径，
   当前无运行时写入源）> user-auth 双接口（正式来源：token + userId 齐备的所有真实身份
   统一走接口，含 App 免登与生产）> fail-closed 空权限。App 不注入权限字段
   （portalAuthObj 仅作诊断日志）；dev:mock 只 mock 双接口、只注入身份不本地合成权限
   （hr-h5 已落地；参考项目 devMockPermissionContext 为过渡形态）；localDebug 只带
   身份三件套、不携带权限快照与调试覆盖；URL `?permissionKeys=` 调试通道与开发旁路
   已按工程裁决删除。参考项目多来源过渡形态仅作对照。
8. **构建边界 + 日志口径**：日志允许打印凭证字段（脱敏规则已由工程裁定废止，hr-h5
   实测登录会话留痕打印 userId/userName/accessToken）；token 等凭证不进 ARMS RUM /
   监控上报、不进仓库与文档；不得硬编码 token、不得伪造权限。`import.meta.env.DEV`
   门控日志以 dist grep 零匹配为验收方式（见本文件「验证」）。
   `localDebugLoaderBoundaryPlugin` 等构建边界设施**仅保留 localDebug 链路时需要**，
   登录框为主通道的形态无需。
9. **按钮权限消费统一范式**：权限码 = `PERMISSION_APP_CODE` 模板拼接（纯字母数字
   camelCase，与权限系统建档码逐字一致）；消费走 `usePermission.hasPermission` /
   `AuthButton` / 路由 `meta.permissionKey`；列表按钮区由后端 `buttons[]` 数组驱动
   （前端仅 `ACTIVITY_BUTTON_MAP` 元数据接线，未知枚举忽略，不做状态推演）。见
   [reference/permission-consumption.md](reference/permission-consumption.md)。

## 改造步骤（把存量 H5 改造成可本地开发）

### Step 0：确认前置条件

- 目标项目已按 `app-webview-bridge` skill 接入 App 免登（`__APP_CONTEXT__` 消费 +
  请求层兜底）；本 skill 不重复桥接契约。
- vite + pnpm 项目；依赖 `vite-plugin-mock-dev-server`（^1.8.4）。
- 目标项目有自己的「统一加载 / 错误 / 参数无效」状态口径（Mock 开发需要）。

### Step 1：命令、端口与代理

- `package.json` 增加 `dev:mock` / `dev:real` / `dev:realTest` 脚本与端口释放脚本
  `scripts/free-dev-port.mjs`，见
  [templates/vite-config-snippets.md](templates/vite-config-snippets.md) §1。
- `vite.config.ts`：固定端口 + `strictPort`；业务前缀代理**仅真实模式挂载**（Mock
  模式绝不代理业务请求）；登录框专用前缀 `/admin/api`、`/admin/user` 单独指向登录
  网关；所有 proxy 转发在 `proxyReq` 阶段把来源头（`Origin`/`Referer`）改写为恒定
  开发 Origin（真机/局域网 IP 调试依赖，见实测口径）。完整片段见
  [templates/vite-config-snippets.md](templates/vite-config-snippets.md) §2。
- `vite.config.ts` 同时挂 mock 插件（集中单入口 `include` + `log: false`，路由表内含
  501 兜底）与 `localDebugLoaderBoundaryPlugin`，见
  [templates/vite-config-snippets.md](templates/vite-config-snippets.md) §3/§4。
- `.env.development` 声明 `VITE_APP_MOCK`、`VITE_APP_PROXY_SERVE_URL`、base name 等，
  并注释「命令注入值优先于本文件」。

### Step 2：Mock 体系

- `mock/` 目录放接口定义；`mock/helpers.ts`（自动日志 + `ok()` 包体 + `paginate()`）
  从 [templates/mock-modules.md](templates/mock-modules.md) §1 复制改造。
- `vite.config.ts` 挂载 `mockDevServerPlugin`，插件 `prefix` 必须显式列出 mock 前缀
  （不列会静默穿透，细节见 [reference/mock-infrastructure.md](reference/mock-infrastructure.md) §1）；
  挂载采用集中单入口 `include: ['mock/index.mock.ts']` + `log: false`（路由入口只输出
  method/path/耗时，避免插件默认打印完整请求体；细节见
  [templates/vite-config-snippets.md](templates/vite-config-snippets.md) §4）。
- 未定义 mock 的业务接口由集中路由表内 `createFallbackRoutes` 501 兜底本地失败
  （不透传网关，与 mock 定义同处维护、可被契约测试覆盖），见
  [reference/mock-infrastructure.md](reference/mock-infrastructure.md) §2。
- 权限资源接口化：dev:mock 只 mock user-auth 双接口（资源树 × resourceIds 求交后
  仍是合法权限），与真实模式同代码路径，不本地合成权限上下文，见
  [templates/mock-modules.md](templates/mock-modules.md) §2。

### Step 3：本地登录框接入（真实联调主通道）

- 安装 npm 包并按技术栈选 UI 入口（core + react/vue），`vite.config.ts` 加
  `/admin/api`、`/admin/user` 登录网关代理，`.env.local` 配
  `VITE_UNIFIED_APP_KEY/SECRET`；完整四步接入见
  [templates/local-login-modules.md](templates/local-login-modules.md)：
  1. `pnpm add busyming-operation-app-h5-login`（peer 见模板 §1）；
  2. `vite.config.ts` 登录代理（在 `MOCK_EXCLUDED_PREFIXES` 显式排除，501 兜底不拦截）；
  3. `src/pages/devtool/LocalLoginPreview.tsx` 薄包装页 + DEV 路由注册；
  4. `setupApp.ts` 三处适配：登录页短路、会话识别与注入（登录签发设备）、
     权限引导走 user-auth 接口通道。
- `setupApp.ts` 注入与运行期行为见
  [reference/real-gateway-debug.md](reference/real-gateway-debug.md)。
- **可选扩展**：不想走短信验证码时，再引入 localDebug 链路（身份三件套配置单文件
  - 间接引用 + 校验门禁 + vConsole 复制工具；权限统一走接口，不含资源快照），
    非必选，见 [templates/local-debug-modules.md](templates/local-debug-modules.md)。

### Step 4：权限消费接入（页面/按钮门控）

- 权限码单一契约文件 `permissionCodes.ts`：`PERMISSION_APP_CODE` 模板拼接、页面码
  与按钮码分组常量、与权限系统建档码逐字一致，见
  [templates/permission-modules.md](templates/permission-modules.md) §1。
- 消费基础设施：`usePermission`（hasPermission / hasAllPermissions /
  hasAnyPermission）、`AuthButton` 声明式守卫、路由 `PAGE_ROUTE_PERMISSION_REGISTRY`，
  见 [templates/permission-modules.md](templates/permission-modules.md) §2/§3。
- 列表按钮区由后端 `buttons[]` 驱动：`ACTIVITY_BUTTON_MAP` 元数据接线 +
  `getButtonMeta` 未知枚举忽略 + `CHANGE_BUTTON_CODES` 置灰，见
  [templates/permission-modules.md](templates/permission-modules.md) §4/§5。
- 权限数据来源以 user-auth 双接口求交为主（fail-closed 空权限），承接 Step 2 的
  接口 mock 与 Step 3 的登录框会话，见
  [reference/permission-consumption.md](reference/permission-consumption.md)。

### Step 5：安全与边界

- 登录框凭证 `VITE_UNIFIED_APP_KEY/SECRET` 放 `.env.local`（gitignore），登录框路由
  仅 DEV 注册，生产构建不可达；包内不读 env、不落凭据。
- 日志允许打印凭证字段（脱敏规则已由工程裁定废止，hr-h5 实测登录会话留痕打印
  userId/userName/accessToken）；token 等凭证不进 ARMS RUM / 监控上报、不进仓库
  与文档；不得硬编码 token、不得伪造权限。`import.meta.env.DEV` 门控日志以 dist
  grep 零匹配为验收方式。
- 仅保留 localDebug 链路时：`localDebug.ts` 受跟踪但只允许短期有效、非生产环境的
  本地联调 Token（工程原则窄例外）；`localDebugLoaderBoundaryPlugin` 保证 Mock 与
  生产构建不加载真实凭证。
- 完整清单见 [reference/security-boundaries.md](reference/security-boundaries.md)。

### Step 6：验证

- `pnpm lint` / `tsc -b` / `pnpm test`（确定性验证命令，见目标项目 `.ai/config.md`）。
- 手工自检清单见本文件末尾「验证」。

## 避坑清单

**Mock 相关**

- mock 插件不显式指定 `prefix` → 前缀被归入 ws 通道、http 前缀为空而静默穿透网关，
  本地 mock 全量失效且无报错。
- 误以为未定义 mock 的接口会透传真实网关 → 当前口径是业务前缀内未命中本地 501
  失败，缺 mock 会显式报错，排查看 `[mock]` 日志与 501 响应体。
- mock 包体 code 与请求层判定口径不一致（如后端成功是 `code: 0`）→ 统一经 `ok()`
  生成，与 `request.ts` 的 `isBizSuccess` 对齐。
- `StrictMode` 双挂载导致 mock 日志 / 请求打两遍 → 区分「React 双跑」与「重复请求」，
  初始化类副作用放模块级单次执行。
- mock 前缀与兜底清单双口径手动同步 → 结构性漂移：已定义接口被 501 兜底拦截或
  未定义接口漏出网关；收敛为 `src/config/devServerPrefixes.ts` 单一来源
  （`BUSINESS_PREFIXES` / `MOCK_PREFIXES` / `MOCK_EXCLUDED_PREFIXES` 纯常量模块零
  import，dev proxy、mock 插件 prefix 与 501 兜底路由全部由该清单派生），结构性
  消除漂移。

**真实联调相关**

- 登录框未接入就启动 dev:real → 无 App Context 且无任何身份来源，请求全部 401；
  主通道是登录框，改造第一步应先装 `busyming-operation-app-h5-login`。
- 登录页不短路身份注入 → 残留旧会话 / 过期 token 触发 user-auth 401 弹「重新登录」
  落点又是登录页，永远无法登录；登录页必须清会话后直接返回。
- 删除登录包缓存后刷新却不进登录框 → token 有两份：登录包会话（真源，登录框写入）
  与 store 持久化副本（zustand persist，store 创建时同步 rehydrate，早于启动链路）。
  真源删除后副本把旧 token 复活进 store，路由守卫误判已登录、跳过登录框引导
  （开发者删缓存强制重登失效；旧 token 过期则先伪登录再 401 兜底跳转）。登录会话
  读取未命中时必须经统一清入口（`clearDevLoginCache({ redirect: false })`）清掉副本
  与登录人信息，再落无鉴权分支。App 免登命中即先于该清理 return，persist 旧 token
  对旧版 App 的容错不受影响；mock 模式被会话读取条件排除，不受影响。
- 身份来源切换（Mock ↔ 真实 ↔ App）不清残留状态 → 上一个账号的 token / 用户信息 /
  默认操作人混入本次会话；切换时清持久化 store（`clearAll`）与登录会话。
- 会话设备被换成其他来源（localDebug 快照 / mse WEB 兜底）→ user-auth 网关校验
  token 与设备绑定，会判「登录已失效」；登录框会话必须注入登录签发的设备。
- （仅保留 localDebug 链路时）localDebug 配置缺字段 → 校验不通过时请求门禁直接阻断
  （提示缺失字段名），token 不会留下；按 `[setupApp]` 日志补全配置。
- （仅保留 localDebug 链路时）联调 Token 过期后页面「一直转圈」→ 用真机 App
  vConsole「本地联调」复制新配置，或改用登录框实时登录（token 动态签发不依赖复制）。

**端口与代理**

- 端口冲突时换端口 → 网关按来源头路由找不到应用；必须固定端口并释放占用进程。
- proxy 转发不改写来源头 → 真机/局域网 IP 访问时浏览器发出 IP 形态的
  `Origin`/`Referer`，网关只认恒定开发来源（`http://localhost:<端口>`），登录网关
  拒收 500、业务网关拒收 403 Invalid CORS request；`changeOrigin` 只改写 Host 头、
  不改写浏览器真实来源头，必须在 `proxyReq` 阶段同时改写 `Origin`（恒定为开发
  Origin）与 `Referer`（保留原 path+search、仅替换 host）——只改 `Origin` 会漏掉
  GET 请求必带的 IP 形态 `Referer`（GET 请求浏览器不携带 `Origin` 头）。
- 把登录框代理 `/admin/api`、`/admin/user` 加进业务前缀清单 → 501 兜底会拦截
  登录请求，登录框无法使用；这两个前缀必须在 `MOCK_EXCLUDED_PREFIXES` 显式排除、
  登录网关 proxy 无条件挂载（登录链路始终走真实网关）。
- 把 App 内不可用的链路（如企微 OAuth2）当成本地兜底 → App 内跳授权页白屏；
  本地开发同样只走 App 免登等价链路（见 app-webview-bridge skill）。

**按钮权限相关**

- 权限码手写字符串而不走 `PERMISSION_APP_CODE` 模板拼接 → 前缀漂移，与权限系统
  建档码不一致导致求交永远为空；新增码必须先建档再用。
- 权限码带下划线 / 连字符 / 点等符号 → 后端 ACL 解析资源码失败；纯字母数字
  camelCase 是硬约束。
- 前端根据 status + roleType 自行推演按钮列表 → 与后端下发不一致，权限口径失真；
  按钮唯一权威来源是后端 `buttons[]`。
- 未知按钮枚举直接渲染或崩溃 → 必须先 `getButtonMeta` 安全取元数据，undefined
  过滤忽略，防后端新增枚举打爆前端。
- 把 NAVIGATION 与按钮区重复渲染 → 导航由地址行胶囊承接，按钮区过滤该 code。
- 为所有按钮 code 强配权限门控 → 工具能力（如 NAVIGATION）未建档也渲染不出来；
  仅配置过 `buttonPermissionKeys` 的 code 走门控。
- 为 dev:mock 本地合成权限上下文（写死资源树）→ 与真实模式代码路径分叉，接口
  契约变更时求交口径漂移；dev:mock 应 mock user-auth 双接口，与真实模式同代码路径
  （hr-h5 已按该口径落地：mock 身份经接口求交；参考项目 devMockPermissionContext
  为过渡形态）。

**MSE 签名与登录包**

- 误以为「登录包整体必须零进包」→ 静态 import `applyMseSignature` 后登录包 core 进
  生产主 chunk 属预期形态；验收口径是「DEV 门控登录页/路由/会话读取标识 dist grep
  零匹配 + `x-ca-signature`/`HmacSHA256` 命中主 chunk」，不可引申为登录包零进包。
- 登录包 axios 与宿主版本不一致 → `AxiosHeaders` 类型不兼容，传给
  `applyMseSignature` 的 `InternalAxiosRequestConfig` 需带注释类型断言（包内仅做
  config.headers 普通字段读写与 Object.assign、跨版本安全）；宿主升级 axios 对齐
  后删除断言。
- 随意删除 crypto-js（MSE 签名依赖，登录包硬依赖）→ 删前必须全局 grep 含 `tests/`
  （只查 `src/` 与 `mock/` 会漏判测试消费者，导致 tsc TS2307）；确认无运行时与测试
  消费后才能降级或移除。
- 见到 INEFFECTIVE_DYNAMIC_IMPORT 拆包警告就想「消警」→ 该警告是预期副作用：
  签名热路径无法异步化，验收看 dist grep 而非消警。
- React 版登录按钮 loading 不显示（0.1.0 / 0.1.1）→ 双根因：antd-mobile DotLoading
  是 SMIL 实现（rect 内嵌 animate），部分 WebView 渲染 rect 几何为 0；Vite 8
  Rolldown 预构建把 antd-mobile 组件 side-effect CSS import 整体剥离且不输出 CSS
  文件（`node_modules/.vite/deps` 无任何 .css，样式确实「丢失」）。0.1.2 起登录包
  改为组件自包含 CSS 动画点（style 注入 keyframes + div 圆点），宿主升级 `^0.1.2`
  即可；排查「DOM 在但视觉不可见」用 `getBoundingClientRect` 读几何定位。
- pnpm 10 升级无 scope 内网私有包（如该登录包）→ `.npmrc` 的「包名:registry=」
  包级覆盖不生效（键读入 config list 但解析仍走默认源，报 FETCH_404）；必须显式
  `pnpm add <pkg>@<version> --registry <内网地址>`。

## 验证

静态：

- `pnpm lint`、`tsc -b`、`pnpm test` 全绿。
- 产物 grep 验收（生产构建后）：DEV 门控标识（`本地登录` / `local-login` /
  `LocalLogin` / `devtool/local-login` 等）在 dist 零匹配；签名指纹（`x-ca-signature` /
  `HmacSHA256`）命中主 chunk。判断命中只看 grep 自身退出码，不得接管道取 `$?`
  （管道末级会吞掉 grep 退出码，导致命中判定失真）。

手工自检（浏览器）：

1. `pnpm dev:mock` 打开首页，接口返回 mock 数据且控制台有 `[mock]` 日志；访问一个
   未定义 mock 的业务接口，网络面板确认返回本地 501（不出现对真实网关的请求）；
   权限由 mock 的 user-auth 双接口求交得出（控制台 `[permission] 引导完成`），
   与 dev:real 同代码路径。
2. `pnpm dev:mock` 与 `pnpm dev:real` 各起一次，确认身份互不残留（切账号不混用）。
3. `pnpm dev:real` 打开 `/devtool/local-login` 完成手机号 + 验证码登录，整页跳转首页
   后接口带正确 `authorization` 与会话设备返回真实数据；再开 Mock 模式确认登录会话
   不生效（身份互不串用）。附加检查（仅保留 localDebug 链路时）：配好 `localDebug.ts`
   后删掉 `authToken` 刷新，请求被门禁阻断并提示缺失字段，而非静默带旧 token。
4. 生产构建成功，且产物与路由不含 `/devtool/local-login`（DEV 路由与凭证不进生产）。
5. 真机 App 内打开：`initAppContext` 命中 `__APP_CONTEXT__` 完成免登。（仅保留
   localDebug 链路时）vConsole 出现「本地联调」tab，点击复制可生成 localDebug 配置。

## 参考资料

- [reference/mock-infrastructure.md](reference/mock-infrastructure.md)：Mock 体系细节
  （插件坑、路由表 501 兜底与前缀清单单一来源、权限接口 mock、带日志 defineMock、
  StrictMode）。
- [reference/real-gateway-debug.md](reference/real-gateway-debug.md)：真实联调链路
  细节（身份优先级、登录框主通道、可选 localDebug 校验门禁、dev:real 自检）。
- [reference/security-boundaries.md](reference/security-boundaries.md)：安全边界
  （登录框凭证与路由边界、可选 localDebug 窄例外、日志与上报边界、Token 生命周期）。
- [reference/permission-consumption.md](reference/permission-consumption.md)：
  按钮权限消费机制（权限码命名硬约束、消费基础设施、buttons[] 后端驱动、
  user-auth 双接口求交）。
- [templates/permission-modules.md](templates/permission-modules.md)：权限消费
  模块族模板（permissionCodes、usePermission/AuthButton、路由注册表、
  ACTIVITY_BUTTON_MAP、buttons[] 驱动消费）。
- [templates/vite-config-snippets.md](templates/vite-config-snippets.md)：vite 配置
  可复制片段（命令、端口释放、代理、路由表 501 兜底、边界插件）。
- [templates/mock-modules.md](templates/mock-modules.md)：mock 模块族模板。
- [templates/local-login-modules.md](templates/local-login-modules.md)：本地登录框
  npm 包接入模板（薄包装页、会话、代理、setupApp 适配）——真实联调主通道。
- [templates/local-debug-modules.md](templates/local-debug-modules.md)：localDebug
  可选辅助模块族模板（身份三件套配置单文件、间接引用、校验门禁、vConsole 复制
  插件；权限统一走接口，不含资源快照），非必选。
