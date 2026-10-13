# 手册步骤 ↔ 动作映射

控制台操作（入口 idp、自动发版、流水线选型、资源右侧「处理」、域名校验）以语雀《前端发布平台使用手册》为准。代码改造细节见 skill 同目录 `使用手册.md`。Agent 按表执行。

| 手册章节 | Agent / 用户动作 |
| --- | --- |
| 入口 / 新建项目 | 用户：研发运维平台 `https://idp.busyming.com` → 前端发布平台 →「项目管理」新建；projectCode = 云效仓库名。勿再走 portal。 |
| 自动发版 | 用户：项目详情 → 构建 Webhook 按环境开；构建成功≠线上；生产不能开。Agent：在评估/发布说明里写清，勿与构建通知混淆。 |
| 流水线 · 模板 A | **运维**：`新架构-前端统一发布模板`（平台直连或自定义域网关直连）。Agent：**不动** Dockerfile/nginx。 |
| 流水线 · 模板 B | **运维**：`新架构-前端统一发布模板-nginx`（旧地址不能改）。Agent：改 `Dockerfile`（`ARG ENV` + ADD + sed）+ nginx `proxy_pass`。 |
| 资源引用路径 | Agent：Vite `base: './'`；webpack `publicPath: './'`；`outDir`/`dist`。 |
| 路由 · 平台直连（A） | Agent：pathname 落在 `__APP_BASE__` 下则用注入值。 |
| 路由 · 自定义域（B1/B2） | Agent：pathname 对不上注入时用 `VITE_APP_BASE_NAME`。 |
| 发布测试 / 发布版本 | 用户：云效跑通 → 版本管理切环境 → 预览 → 发布。Agent：给出预期预览 URL。 |
| 如何访问 | 直连：`https://fe-stack.busyming.com/instance/p[/{env}]/{projectCode}...`；自定义域：网关或 nginx 反代。 |
| 灰度 / 配置 / 静态页 | 按需；非接入必改项。 |
| 资源管理 · 图床 | 模式 `upload-assets`：curl → scripts → put + register；字段 **`cdnDomain`**。 |
| 资源管理 · 图片处理 | 改引用后提醒：到资源管理点右侧 **处理** 预览，再复制 `?image_process=`；勿默认原图。 |
| 实用工具 · 域名校验 | 仅 fe-stack / `{env}-fe-stack` 主机；业务域自行放 `.txt`。 |
| 其他注意事项 | assess 按业务相关性对照；无关跳过。 |

## 框架适配提示

手册示例为 Vue Router + `createWebHistory(resolveAppBaseName())`。

- **React**：`createBrowserRouter(routes, { basename: resolveAppBaseName() })` 或 `BrowserRouter basename={...}`；`Window.__APP_BASE__` 类型声明按需补。
- **Hash 路由**：base 资源路径仍要 `./`；basename 规则与 history 不同，评估里单独说明，勿照搬 history 示例。

## 访问方案选择

向用户提问时只用 `SKILL.md` 里那一道 1 / 2 / 3 的题，不要贴本段，也不要让用户选「A / B1 / B2」。

Agent 内部对应：1 平台直连；2 网关直连（模板与 1 相同，路由用 `VITE_APP_BASE_NAME`）；3 nginx 模板并改 Dockerfile + nginx。会嵌才写白名单待办。
