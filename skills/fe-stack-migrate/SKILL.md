---
name: fe-stack-migrate
description: >-
  Assess or migrate a frontend SPA into busyming fe-stack (统一发布平台): align
  Vite/webpack base and router basename with __APP_BASE__ / VITE_APP_BASE_NAME,
  upload local assets/ to platform gallery CDN (cdnDomain) and rewrite refs
  (incremental; remind CDN image_process crop), pick pipeline template
  (直连 vs nginx 兼容旧路径), and when nginx template is chosen update
  Dockerfile + nginx-default.conf to reverse-proxy to fe-stack. Map work to
  使用手册. Use when the user mentions fe-stack 接入, 统一发布平台改造, 迁移到
  instance/p, 上传静态资源/图床/assets, nginx 反代模板, or asks to
  evaluate/migrate a H5/Vue/React project onto the stack.
disable-model-invocation: true
---

# fe-stack 项目接入改造

对照「前端统一发布平台」使用手册，对**目标业务仓库**做评估或代码改造。默认**只评估不改代码**；仅当用户明确要求 migrate / 改造 / 落地 / 上传 assets 时才改目标仓或调上传 API。

## 权威文档（勿写死本机绝对路径）

按优先级查找《使用手册》，**找到即读**「接入 / 流水线改造 / 代码改造 / 如何访问 / 资源管理 / 其他注意事项」；都找不到则**停止并请用户提供路径或 @ 文件**，禁止凭记忆编造契约。

1. 用户本轮给出的路径，或对话里 @ 的手册文件
2. **本 skill 同目录** `[使用手册.md](使用手册.md)`（分发时与 skill 一起拷贝）
3. 当前工作区任意根下的 `docs/使用手册.md` / `docs/手册/平台操作手册.md` / `**/使用手册.md`
4. 可选捷径：`busyming-fe-stack-meta/skills/fe-stack-migrate/使用手册.md`（meta 权威副本）

细节补充始终读 skill 同目录：`checklist.md`、`gaps.md`、`handbook-map.md`；上传静态资源时再读 `upload-assets.md`。

**分发**：拷贝整个 `fe-stack-migrate/` 文件夹即可；勿只拷 `SKILL.md`。手册有更新时，以 meta `skills/fe-stack-migrate/` 为准再覆盖进业务仓。

**禁止**为迁就某个业务项目去改使用手册正文。手册覆盖不了时：在评估报告里写清缺口与责任方，停手或只改手册已覆盖的部分。

## 模式

| 模式 | 触发用语 | 行为 |
| --- | --- | --- |
| `assess` | 评估、影响面、能不能改、先看 | 只读扫描 → 输出报告。**禁止**改业务代码 / 手册 / 流水线云效配置（除非用户只要报告落盘且明确指定路径） |
| `migrate` | 改造、迁移、落地、按评估改 | 须先有评估结论且用户确认访问方案 + 流水线模板；只改白名单内文件 |
| `upload-assets` | 上传 assets、传图床、静态资源上传并改引用 | 读 [upload-assets.md](upload-assets.md) + 用 [scripts/](scripts/)；一条 curl → MSE 现签 → OSS 只 put；产出在 `node_modules/.fe-stack-upload/`；拼 URL 用 **`cdnDomain`** |

未指明模式时按 `assess`。可与 migrate 分两次做；同一会话先 migrate 再 upload-assets 时复用已有 `feat/fe-stack`。

## 对话怎么说（对用户）

内部进度勾选、手册对照表、gaps 表**不要贴进对话**。用小标题分段，不要挤成一行。

- 还没开工：只问下面这一题，问完就停
- 评估或改造做完：按「报告格式」写，其中**访问地址必须套用下一节的拼法**，把仓库名填进示例，不要只丢 `{projectCode}`

一次只问一个问题。用户已选过访问方式就不要再问。

## 访问地址怎么拼（给用户看示例时必写）

两段都要讲清，用这个仓库的真实名字，不要留占位符不解释。

- **projectCode**：平台「项目管理」里的**项目编码**，必须等于**云效仓库名**。示例里直接写本仓库文件夹名，并说明「这就是项目编码」。
- **env**：联调环境名，只能是 `dev`、`test`、`uat`、`pre` 之一。写在路径里表示「看这个环境刚构建的包」。**生产不要写 env**。给用户、小程序、消息的正式链接只用生产地址。

按用户选的方式只写对应那一种：

**1. 平台域名**（用户打开的就是这条）

- 联调：`https://fe-stack.busyming.com/instance/p/{env}/{projectCode}`
- 正式：`https://fe-stack.busyming.com/instance/p/{projectCode}`

例：仓库名 `remind-tool`、先看 dev → `https://fe-stack.busyming.com/instance/p/dev/remind-tool`。上线给用户则去掉 `dev`：`https://fe-stack.busyming.com/instance/p/remind-tool`。

**2. 自己的域名，走网关**（用户打开的是自己的域名，不是 fe-stack）

- 发给别人的地址：`https://{你们的域名}{页面路径}`。页面在网站根上就是 `https://sale.busyming.com/`；若本来挂在子路径，路径保持原样。
- 网关在背后把这个域名转到平台这条（用户地址栏里看不到）：非生产 `https://fe-stack.busyming.com/instance/p/{env}/{projectCode}`，生产去掉 `{env}`。
- `{env}`、`{projectCode}` 含义与上面相同。业务仓不用改 nginx。

**3. 自己的域名，旧地址不能改**

- 发给别人的地址：**保持改造前的域名和路径**，不要改成 fe-stack。
- 容器里的 nginx 把这个旧地址转到平台同一条：非生产 `.../instance/p/{env}/{projectCode}/`，生产去掉 `{env}/`。
- 要让运维用「新架构-前端统一发布模板-nginx」，并在构建时传入对应的 env。

固定某一版时，在 projectCode 后面再加版本号（别名后 `#` 起的五位）。日常预览不要加。

## 开始前确认（缺则先问）

1. **目标仓库**：用户当前打开的业务仓即可，不必再问路径
2. **访问路径**（assess / migrate 必问；没选之前禁止默认成平台直连，也禁止先改代码）

对用户**只发下面这一段**，不要加模板全名、Dockerfile 片段或手册摘抄：

```text
用户打开页面时，地址栏是哪一种？回 1、2 或 3。

1. 平台域名
   地址栏是 fe-stack.busyming.com
   仓库不用改 Dockerfile / nginx

2. 自己的域名，走网关（新业务）
   地址栏是你们自己的域名，这个域名上没有必须留着的旧页面
   仓库不用改 Dockerfile / nginx

3. 自己的域名，旧地址不能改（已经上线）
   必须继续用原来的域名和路径
   要改 Dockerfile 和 nginx，由容器转到平台

页面会不会嵌在企微或小程序里？会的话在后面加「会嵌」，不会就加「不嵌」。
```

对应关系（只给 Agent，不要贴给用户）：1 = 平台直连 +「新架构-前端统一发布模板」；2 = 网关直连 + 同一套模板；3 =「新架构-前端统一发布模板-nginx」。会嵌时才提醒域名校验 / 白名单。

3. **projectCode** 默认用仓库名，不要单独追问
4. upload-assets 另说：只要一条研发运维平台（`idp.busyming.com`）「资源管理」里的 Copy as cURL；改完引用后用一句话提醒：到资源管理点右侧 **处理** 预览，再复制带参数的图片地址

## Assess 工作流

复制并维护进度：

```
评估进度:
- [ ] 1. 定位手册与目标仓
- [ ] 2. 探测部署与构建（含是否已有 Dockerfile/nginx）
- [ ] 3. 探测路由与 base
- [ ] 4. 探测鉴权/入口/API
- [ ] 5. 对照手册与 gaps
- [ ] 6. 输出评估报告
```

### 1–4 必扫文件与信号

在目标仓搜索并阅读（有则读）：

- 构建：`vite.config.*`、`vue.config.*`、`webpack*.js`、`package.json` scripts（`build:*`）
- 路由：`createBrowserRouter` / `createWebHistory` / `BrowserRouter` / `basename` / `history` 模式
- 环境：`.env*`、`VITE_APP_BASE_NAME`、`PUBLIC_PATH`、`base`、`publicPath`
- 运行时：`__APP_BASE__`、OAuth、企微、小程序 bridge、绝对 URL 拼 `origin`/`pathname`
- 请求：`axios`/`fetch` 的 `baseURL`、是否依赖「同域反代 API」、`withCredentials`
- 静态目录（仅报告，不上传）：`src/assets`、`assets`、`public/assets`；是否适合后续 `upload-assets`
- 部署文件（**按模板决定是否进改造清单**）：`Dockerfile`、`nginx-default.conf`、`default.conf`、`nginx/**`

**模板 A（平台直连）**：Dockerfile / nginx **默认不处理**，报告可一句带过「有文件则留仓不动」。  
**模板 B（nginx 兼容）**：必须把 Dockerfile + nginx conf 列入改造清单，对照手册示例检查 `{env}` 占位与 `proxy_pass` 到 `fe-stack.busyming.com/instance/p/{env}/{projectCode}/`。

### 5 判定规则

对每一项标注：

- **手册已覆盖** — 按手册即可改
- **需运维** — 流水线模板选型、边缘反代、域名
- **手册外阻断** — 见 `gaps.md`；不改手册，列入「上线前人工待办」

总评只能三选一：

1. **可改** — 场景清晰，无手册外硬阻断（或阻断已有明确人工方案）
2. **有条件可改** — 代码可按手册改，但上线依赖运维/企微/CORS/入口等
3. **不可仅靠手册闭环** — 架构与平台模型冲突（例如强依赖容器内 API 反代且无法改成直连网关）；说明原因，**不要强行 migrate**

### 6 报告格式

[checklist.md](checklist.md) 只给 Agent 自己对照，**不要整份贴给用户**。

对用户按这个结构写（访问方式还没选时，先写结论和代码，最后再贴那一道 1/2/3 的题，地址示例等选完再给）：

```markdown
**结论**
可改 / 有条件可改 / 现在改不了。一句话原因。

**访问地址**
（按「访问地址怎么拼」写清：这条链接是给谁打开的、env 是什么、projectCode 就是本仓库名且等于云效仓库名和平台项目编码。用真实仓库名举一条 dev 示例和一条生产示例。）

**代码上会改**
- …
- …

**请你做**
- …
```

## Migrate 工作流

前置：assess 已完成，且总评为「可改」或「有条件可改」；用户已确认访问方案与流水线模板（A 平台直连 / B nginx 兼容）。

```
改造进度:
- [ ] 1. 复述将改文件与场景（等确认若用户未确认）
- [ ] 2. 检出分支 feat/fe-stack（默认；用户另指定分支名则用其名）
- [ ] 3. base / publicPath → 相对路径
- [ ] 4. router basename / appBase 解析
- [ ] 5. 构建脚本与产物目录对齐
- [ ] 6. （仅模板 B）Dockerfile ARG ENV + nginx proxy_pass
- [ ] 7. 自检清单 + 人工待办
```

### 分支（确认改造后、改文件前）

用户确认要 migrate 之后，**先建/切分支再改代码**，默认名 `feat/fe-stack`：

1. 在**目标业务仓**执行（不要改 stack-service / skill 仓）
2. 工作区有未提交改动时：先 `git status` 告知用户；有冲突风险则停手问清，禁止擅自 stash 丢弃
3. 若本地已有 `feat/fe-stack`：直接 `git checkout feat/fe-stack`（其上已有提交则接着改，勿 force 重置）
4. 若无：从当前分支（通常是用户当前所在分支或 `daily/*` / 主开发分支）`git checkout -b feat/fe-stack`
5. 用户明确说了别的分支名（如 `feat/fe-stack-remind`）→ 用用户的名字，规则同上
6. **不要**默认 push；用户要求再推。**不要**在 assess 阶段建分支

改造后输出里写明：当前分支名、基于哪条分支拉出。

### 白名单（只改这些，除非用户点名扩大）

| 改动 | 说明 |
| --- | --- |
| Vite `base: './'`（或删掉绝对 base） | webpack 则 `publicPath: './'` |
| `outDir`/`outputDir` → `dist`（若手册要求且项目不一致） | |
| `resolveAppBaseName`（或框架等价物） | A 用 `__APP_BASE__`；B / 自定义域用 `VITE_APP_BASE_NAME`；逻辑见手册示例 |
| router `basename` / `history` base | 使用上述 resolve，禁止写死旧 subapp 路径作为唯一来源 |
| `.env*` 中 `VITE_APP_BASE_NAME` | A：可保留但直连时以注入为准；B：必须等于浏览器路径前缀 |
| `package.json` `build:${env}` | 与流水线 `env` 对齐；缺的脚本与运维确认后再加 |
| **（仅模板 B）`Dockerfile`** | `ARG ENV` + `sed` 替换 conf 中 `{env}`（prod 删除 `{env}/`） |
| **（仅模板 B）`nginx-default.conf` 等** | 保留旧 path 的 location 反代到 `https://fe-stack.busyming.com/instance/p/{env}/{projectCode}/` |

**模板 A 默认不动**：`Dockerfile`、`*.conf`、`nginx/**` — 留在原处，不改、不删、不引导处理。  
**模板 B 必须改**：上表 Dockerfile + nginx；勿整文件推倒重写，优先在现有 conf 上改入口 `location` 的 `proxy_pass`。

### 模板 B：Dockerfile / nginx 要点（细节以手册为准）

Dockerfile 增加（在 ADD conf 之后）：

```dockerfile
ARG ENV
RUN if [ "$ENV" = "prod" ]; then \
      sed -i 's|{env}/||g' /etc/nginx/conf.d/default.conf; \
    else \
      sed -i "s|{env}|${ENV}|g" /etc/nginx/conf.d/default.conf; \
    fi
```

nginx 入口示例（`{projectCode}` 换成真实编码；`{env}` 留给 Dockerfile 替换）：

```nginx
location / {
  proxy_pass https://fe-stack.busyming.com/instance/p/{env}/{projectCode}/;
  proxy_ssl_server_name on;
  proxy_set_header Host fe-stack.busyming.com;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
}
```

说明：`proxy_ssl_*` / 额外 Cache / CORS header 按需保留，非必须；关键是 `proxy_pass` 指到平台对应环境路径。若旧站是子路径入口（如 `/subapp/xxx/`），应对该 location 做同样反代，而不是只改 `/`。

### 禁止

- 在默认分支 / 用户未确认的分支上直接改代码（须先 `feat/fe-stack` 或用户指定分支）
- 改业务页面逻辑、接口语义、鉴权流程（除非仅为接 `basename` 所必需）
- 改使用手册或 stack-service 契约
- 编写/提交含密钥的 `.env` 到文档里扩散；评估里对 secret 打码
- **模板 A** 下默认改写 / 删除 nginx、Dockerfile，或引导用户关注这些文件
- **模板 B** 下漏改 Dockerfile/`{env}`，导致非生产仍带着字面量 `{env}`
- 一次改造多个无关仓库
- 未用户要求就 commit / push（分支检出除外）
- 拼 CDN 时仍用已废弃字段 `cdnBaseUrl`（须用 `cdnDomain`）

### 改造后必须输出

不要再附评估表。结构与评估相同，并写上分支：

```markdown
**已改在分支** `feat/fe-stack`（从 xxx 拉出）。

**访问地址**
（仍按「访问地址怎么拼」，用真实 projectCode 写一条联调、一条正式。选 2、3 时写明用户打开的是自己的域名，fe-stack 那条只是背后转到的地址。）

**改了这些文件**
- …

**请你做**
- 推代码并跑流水线
- 版本管理页顶切到对应环境，用上面的联调地址预览
- 确认后再点「发布版本」（生产不能靠自动发版）
```

选 3 时在「请你做」里加：让运维用 nginx 那套模板。会嵌企微或小程序时加：白名单填用户真正打开的那个完整域名。

## Upload-assets 工作流

前置：用户明确要上传；平台已有项目。细节见 [upload-assets.md](upload-assets.md)。**用 skill 自带 scripts，勿从零发明签名。**

```
上传进度:
- [ ] 1. 扫 assets 白名单 + 源码引用；问用户 (a)全传 (b)只传引用 (c)先看未引用清单 — 未确认不传
- [ ] 2. 只要一条：研发运维平台（idp）「资源管理」里 stack-service 成功请求的 Copy as cURL
- [ ] 3. 校验 curl 域名与目标 env 一致；取 appSecret（html .env.{env} 或问用户）
- [ ] 4. 复制 scripts/api.mjs + upload.mjs → 业务仓 node_modules/.fe-stack-upload/；签名自检通过后再上传
- [ ] 5. 若改引用：检出 feat/fe-stack
- [ ] 6. node upload.mjs：getGalleryToken → OSS 只 put（禁止 putACL）→ register → 字段用 cdnDomain
- [ ] 7. 对话输出 JSON 摘要（密钥打码）；提醒到资源管理点右侧 **处理** 预览后再用带 `?image_process=` 的地址；问是否删除临时目录
```

要点：

- **开场只要 curl**，不要拆多轮要 token/deviceId  
- **X-Operate-Info 必须从 curl 原样复制**  
- **MSE 现签**；先自检再业务调用  
- **产出只进** `node_modules/.fe-stack-upload/`  
- 凭证访问根字段是 **`cdnDomain`**（禁止再写 `cdnBaseUrl`）  
- **禁止** putACL、instance 按日目录当迁移通道、网关豁免、无脚本发明签名  
- 改引用后：列表/头像/Banner **不要默认贴原图 URL**；引导用户到 **资源管理 → 资源右侧「处理」** 预览后再复制带 `image_process` 的地址（与语雀手册一致）

## 在业务仓如何调用（给用户）

把整个 `fe-stack-migrate/` 放到目标仓 `.cursor/skills/`，或放到 `~/.cursor/skills/`，然后说：

- `用 fe-stack-migrate 只评估本仓库，选 A 平台直连`
- `用 fe-stack-migrate 评估，选 B nginx 兼容旧路径 a.com`
- `按上次评估，用 fe-stack-migrate 改造，模板 A`（不动 nginx/Dockerfile）
- `按上次评估，用 fe-stack-migrate 改造，模板 B`（会改 Dockerfile + nginx-default.conf）
- `用 fe-stack-migrate 把 src/assets 传到图床并改引用`（贴一条目标环境 stack-service 成功请求的 curl 即可）
- `只上传 assets，不改代码引用`

手册已打进 skill 目录时，不必再指定手册路径；若用的是旧包缺手册，再 `@使用手册.md` 或给出路径。

## 附加资源

- [checklist.md](checklist.md) — 评估报告模板
- [gaps.md](gaps.md) — 手册外必查项
- [handbook-map.md](handbook-map.md) — 手册步骤 ↔ 代码/动作映射
- [upload-assets.md](upload-assets.md) — 静态资源上传 / 增量 / 改引用 / CDN 裁剪  
- [scripts/api.mjs](scripts/api.mjs) / [scripts/upload.mjs](scripts/upload.mjs) — upload-assets 参考实现（复制到业务仓 `node_modules/.fe-stack-upload/`）
