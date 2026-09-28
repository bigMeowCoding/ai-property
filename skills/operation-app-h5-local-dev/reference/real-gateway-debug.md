# 真实网关联调链路（dev:real / dev:realTest，主通道：本地登录框）

浏览器真实模式下没有 App 注入，身份主通道来自本地登录框（npm 包
`busyming-operation-app-h5-login`，见
[../templates/local-login-modules.md](../templates/local-login-modules.md)）。参考项目
`busyming-store-opening-h5` 实测口径，文件路径均指该项目。

## 1. 身份来源优先级（登录框为主）

`setupApp` 编排（`src/helpers/setupApp.ts`）按序判定：

1. **登录页短路**（DEV + `/devtool/local-login`）：清会话与持久化身份后直接返回，
   不注入身份、不发 user-auth 请求。否则残留会话/过期 token 触发 401 弹「重新登录」、
   落点回登录页，永远无法登录。
2. **App 免登**（`initAppContext` 命中 `__APP_CONTEXT__`）：完成登录，清残留登录会话，
   上报上下文诊断；未命中则进入后续身份来源判定（URL 参数兜底已按 hr-h5 实测删除）。
3. **本地登录会话（主通道）**（真实模式 + 无 App Context）：`localLoginSessionStore.load()`
   命中时注入 `accessToken` / `userInfo` / **登录签发设备**，并跳过 localDebug 校验
   链路（会话即完整身份）。会话读取采用动态 import + `import.meta.env.DEV` 门禁
   （生产常量折叠后会话读取代码零进包，验收：dist grep 登录会话读取标识零匹配）。
   **未命中时**（登录包真源已删/从未登录）必须经统一清入口
   `clearDevLoginCache({ redirect: false })` 清掉持久化副本再落无鉴权分支：store
   持久化（zustand persist）在 store 创建时已同步把旧 token 副本恢复到内存（早于
   启动链路），不清会让路由守卫误判已登录、删除登录包缓存后仍不进登录框
   （「真源已删、副本复活」伪登录态）。App 免登命中即先于该清理 return，persist
   旧 token 对旧版 App 的容错不受影响；mock 模式被会话读取条件排除，不受影响。
4. **localDebug 校验链路（可选辅助）**（DEV + 非 Mock + 无 App Context + 无登录会话）：
   仅在目标项目选择保留 localDebug 时存在；`validateLocalDebugConfig` 校验字段完整性，
   通过才写入 token / userInfo / deviceInfo（身份三件套，权限统一走接口）。
5. **dev:mock 身份**（Mock 模式）：只注入 mock 身份（token / userId / 设备），权限走
   mock 的 user-auth 双接口（hr-h5 已落地；参考项目当前为 `DEV_MOCK_PORTAL_AUTH`
   本地合成，过渡形态）。
6. **权限引导（接口调用为主）**：权限来源优先级收敛为三级（hr-h5 已落地）：store
   权限上下文判源（防御路径，当前无运行时写入源）> user-auth 双接口（正式来源：token
   - userId 齐备的所有真实身份统一走接口，含 App 免登与生产）> fail-closed 空权限。
     App 不注入权限字段（portalAuthObj 仅作诊断日志）；URL `?permissionKeys=` 调试通道
     已按工程裁决删除。参考项目当前为五来源过渡形态（localDebug 快照与调试覆盖、
     dev-mock 本地合成），仅作对照，改造目标见
     [permission-consumption.md](permission-consumption.md) §4。

任何来源切换（Mock ↔ 真实 ↔ App）都先 `clearAll` 持久化 store，避免跨账号混用。

## 2. localDebug 配置的获取（可选辅助）

> 以下内容仅在目标项目选择保留 localDebug 链路时需要；以登录框为主通道的精简形态
> 可跳过本节。

token 短期有效（过期是正常现象），三种获取方式：

1. **真机 App vConsole「本地联调」复制**（首选）：App WebView 内 vConsole 出现
   「本地联调」tab，点击复制生成完整 `export default {...}` 文本，粘贴到
   `src/config/localDebug.ts`。仅非生产 App WebView 提供该入口。
2. **App 控制台日志**：`[appBridge]` 打印的上下文摘要（上下文字段与数量；权限字段
   仅作诊断日志消费），配合 Network 面板 `authorization` 头拼装配置。
3. **浏览器 Network 面板**：任意真实请求的 `authorization` 头（Bearer token）；
   设备信息用 App 内同账号请求的 `x-Device-Info`。

`buildLocalDebugConfig`（`src/helpers/appContextDebugConfig.ts`）对快照做边界校验，
缺失字段只暴露字段名（如 `unifiedPortal.accessToken`、`deviceInfo`），不打印原始
上下文；权限资源不再入快照（权限统一走接口）。

## 3. 校验与请求门禁（可选辅助）

> 仅在保留 localDebug 链路时需要；登录框为主通道的形态无需。

`src/helpers/localDebugContext.ts`：

- `getMissingLocalDebugFields`：必填 `authToken` / `userInfo.userId` / `userInfo.userName`
  / `deviceInfo`（身份三件套；权限统一走接口，不校验资源快照）。
- `validateLocalDebugConfig`：初始化阶段同步建立门禁——校验不过 `localDebugToken` 置空
  （**无效配置不会留下可用 token**）。
- `request.ts` 拦截器：DEV 下 `getLocalDebugIssue()` 非空直接抛
  `本地真实联调配置缺失：authToken, deviceInfo`，请求不发，而不是带旧 token 打网关。
- `resolveAuthToken`：`getLocalDebugToken()`（已校验）> URL `authToken` > store token。
- `resetLocalDebugSession`：切到 App/Mock 来源时清除本地凭证与诊断。

## 4. 设备绑定约束

user-auth 网关按「token 与 x-Device-Info 设备绑定」校验（实测）：

- 同一 token 带登录签发设备（如 PC 设备 `ops-sso`）→ 200；
- 带其他设备（localDebug 快照的 AND 设备）→ 401「登录已失效」；
- 带空设备（mse WEB 兜底）→ 400「设备ID不能为空!」。

因此：localDebug 的 `deviceInfo` 必须与 token **同账号同源**（App 注入的设备快照）；
登录框会话必须用登录签发的设备。换成本机合成值会 401。

## 5. MSE 网关验签

`src/utils/mse.ts`：

- 签名核心（HmacSHA256）上收至 `busyming-operation-app-h5-login` 的
  `applyMseSignature`（单一真源，本地登录链路与业务链共用同一实现）；本仓库保留
  业务请求链专属部分：APP_KEY/APP_SECRET 环境解析、设备解析与兜底、X-Operate-Info
  序列化与注入（签名之后注入，不参与签名）。
- `x-ca-key`：生产 `basic`，其他环境 `basic-${mode}`（MODE 自动拼接，无需配置）。
- `APP_SECRET`（`VITE_APP_SECRET`）由云效流水线注入；仓库内值仅供本地调试。
- 设备缺省走 WEB 兜底（本地开发默认设备），但 user-auth 链路必须用真实设备
  （见上节设备绑定约束）。

单一真源连带口径（hr-h5 实测，详见 SKILL.md 避坑清单「MSE 签名与登录包」）：

1. **登录包 core 进生产主 chunk 属预期**：静态 import `applyMseSignature` 后登录包
   core 进生产主 chunk；验收口径是「DEV 门控登录页/路由/会话读取标识 dist grep 零
   匹配 + `x-ca-signature`/`HmacSHA256` 命中主 chunk」，不可引申为「登录包整体零
   进包」（会话读取等 DEV 链路经动态 import + `import.meta.env.DEV` 门禁，常量折叠
   后零进包，见 [security-boundaries.md](security-boundaries.md) §1）。
2. **axios 版本类型断言**：登录包 axios 与宿主版本不一致时 `AxiosHeaders` 类型不兼容，
   传 `InternalAxiosRequestConfig` 需带注释类型断言（`as unknown as Parameters<
typeof applyMseSignature>[0]`）；包内仅做 config.headers 普通字段读写与
   Object.assign、跨版本安全，宿主升级 axios 对齐后删除断言。
3. **crypto-js 归属**：crypto-js 是登录包硬依赖（MSE 签名），可降级/移除；删前必须
   全局 grep 含 `tests/`（只查 `src/` 与 `mock/` 会漏判测试消费者，导致 tsc TS2307）。
4. **INEFFECTIVE_DYNAMIC_IMPORT 是预期副作用**：签名热路径无法异步化，拆包警告
   不可避免；验收看 dist grep 而非消警。

## 6. dev:real 自检（登录框为主）

1. 浏览器打开 `pnpm dev:real`，访问 `/devtool/local-login` 完成手机号 + 验证码登录，
   登录成功整页跳转首页。
2. 首页接口带正确 `authorization` 返回真实数据；控制台 `[setupApp]` 日志显示登录
   会话注入（用户与设备摘要），设备为登录签发设备。
3. 重新打开登录页并登出/清会话后，真实接口应回 401 或引导重新登录，而非静默带旧 token。
4. `pnpm dev:realTest` 打到 test 网关（`.env.test` 的 `VITE_APP_PROXY_SERVE_URL`），
   Network 面板确认请求目标域名切换为 test 网关。

附加（仅保留 localDebug 链路时）：配好 `src/config/localDebug.ts`（同账号 token +
`deviceInfo`，身份三件套；权限仍走接口），控制台出现 `[setupApp] 本地真实联调配置
（appContext 摘要）`且 `status: ready`；删掉 `authToken` 后刷新，请求被门禁阻断并
提示缺失字段。

## 7. 启动日志与监控富化

- `initArms` 启动 ARMS RUM（`.env.development` 默认关闭避免误上报）；
  `bindArmsUser` 基础用户绑定 + `enrichArmsUser` 异步富化（user-auth 当前用户详情，
  失败不影响首屏）；`reportAppContextDiagnostics` 上报 App 上下文诊断。
- 日志口径：允许打印凭证字段（脱敏规则已由工程裁定废止，hr-h5 实测登录会话留痕
  打印 userId/userName/accessToken，权限引导留痕打印 source/资源与权限码数量）；
  token 等凭证不进 ARMS RUM / 监控上报、不进仓库与文档；不得硬编码 token、不得
  伪造权限。`import.meta.env.DEV` 门控日志以 dist grep 零匹配为验收方式。
