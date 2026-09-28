# 安全边界

本地开发链路承载真实凭证，必须守住以下边界。参考项目
`busyming-store-opening-h5` 实测口径。

> 以登录框为主通道的精简形态只需遵守 §1（登录框凭证与路由边界）与 §2（日志与上报
> 边界）；§3-§5 仅在目标项目选择保留 localDebug 链路时需要。

## 1. 登录框凭证与路由边界（主条款）

- 登录框凭证 `VITE_UNIFIED_APP_KEY` / `VITE_UNIFIED_APP_SECRET` 放 `.env.local`
  （gitignore 排除），不进仓库、不进 `.env.example` 实际值。
- 登录框路由 `/devtool/local-login` 仅 `import.meta.env.DEV` 注册，生产构建不可达。
- 会话存 sessionStorage（关闭标签页即失效），读取逐字段校验形态，非法一律按无会话
  处理，不抛异常。
- 会话读取（消费端）用动态 import + `import.meta.env.DEV` 门禁：生产构建常量折叠后
  会话读取代码零进包（验收：dist grep 登录会话读取标识零匹配）。薄包装页静态 import
  与消费端动态 import 构成双通道；签名 core 静态进生产主 chunk 属预期（见
  [real-gateway-debug.md](real-gateway-debug.md) §5）。
- 包内不读 env、不落凭据：`busyming-operation-app-h5-login` 的凭证与 token 由宿主
  运行时注入/保存。

## 2. 日志与上报边界

脱敏规则已由工程裁定废止（hr-h5 实测登录会话留痕打印 userId/userName/accessToken）：
本地开发日志允许打印凭证字段，但凭证**不得进 ARMS RUM / 监控上报、不得进仓库与
文档**；不得硬编码 token、不得伪造权限。`import.meta.env.DEV` 门控日志以 dist grep
零匹配为验收方式。

---

> 以下 §3-§5 仅保留 localDebug 链路时需要。

## 3. 工程原则窄例外

`localDebug.ts` 含 token 但受跟踪，依据工程原则 v1.7.1 的窄例外：**仅允许短期有效、
非生产环境的本地联调 Token**。文件只含身份三件套（token / 用户 / 设备），权限统一
走 user-auth 接口，不含权限资源快照。禁止进文件/提交的内容：

- 生产环境 Token、密钥、App Secret；
- 任何长期有效凭证；
- token 进 ARMS RUM / 监控上报、进仓库与文档。

个人差异配置（不想入库的本地值）放 `localDebug.private.ts`，`.gitignore` 排除。

## 4. 加载器边界（Mock 与生产构建不读凭证）

`localDebug.ts` 不被直接 import：`localDebugLoader.ts` 用 `import.meta.glob` 间接
引用（直接 import 会被静态分析、打包器无法排除）。`localDebugLoaderBoundaryPlugin`
（见 [../templates/vite-config-snippets.md](../templates/vite-config-snippets.md) §3）做两层防护：

1. `transform` 阶段：Mock 模式（`useMock`）与生产构建（`command === 'build'`）把
   `localDebugLoader.ts` 替换为 `export default undefined`——真实凭证不进内存与产物；
2. `generateBundle` 阶段：生产构建产物若意外包含 `localDebug.ts`（例如被别处直接
   import），直接 `this.error('生产构建意外包含本地联调配置')` 使构建失败。

两层互补：第一层是主动排除，第二层是兜底检测。

## 5. 请求门禁与 token 生命周期

- `localDebugContext.ts` 校验失败时 `localDebugToken` 置空——**无效配置不会留下可用
  token**；`request.ts` 在 DEV 下检测到缺失字段直接阻断请求（不发带旧 token 的请求）。
- 切换 App / Mock 来源时 `resetLocalDebugSession()` 清除本地凭证与诊断，避免跨来源
  复用。
- token 短期有效，过期是正常现象：从真机 App vConsole「本地联调」复制新配置，或
  改用登录框实时登录（主通道）。
- 会话（登录框）token 与设备绑定：换设备会被网关判「登录已失效」，不得混用。
- 以登录框为主通道的项目无需 localDebug 构建边界：`busyming-operation-app-h5-login`
  包本身不含凭证文件，凭证只存在于宿主 `.env.local` 与 sessionStorage。
