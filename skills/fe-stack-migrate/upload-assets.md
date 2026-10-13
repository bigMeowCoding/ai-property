# upload-assets 细则

把业务仓本地静态资源上传到平台图床（`{projectCode}/assets/...`，**无 YYYYMMDD**），可选改代码引用。默认**增量**（本地 manifest 按内容 sha256 skip）。

对象命名（读 `getGalleryToken` 返回的 `resourceUpload.overwrite`，项目 settings 默认 `false`）：

| 策略 | 行为 |
| --- | --- |
| 不覆盖（默认） | 首次用原名 `1.jpg`；OSS 已存在同名则落 `1_{5位hash}.jpg`；`register.fileName` 仍为 `1.jpg` |
| 覆盖 | 始终原名 `1.jpg`，OSS 直接覆盖 |

**走研发运维平台 gateway → stack-service**（控制台入口 `https://idp.busyming.com`）；禁止 instance（按日目录），禁止 `*-fe-stack.../stack-service`。

Agent **不要发明签名/上传实现**：复制本 skill 自带的参考脚本到业务仓临时目录执行（见「脚本策略」）。

## 开场只要一样东西：一条真实 curl

**不要**拆成多轮分别要 env / token / deviceId。一次要齐：

```text
请在【目标环境】登录研发运维平台（https://idp.busyming.com）→ 前端发布平台 →「资源管理」，
DevTools → Network，找一条返回 success:true 的 *-gateway.../stack-service/... 请求，
右键 Copy as cURL，整段贴给我。
（含鉴权信息；我不会回显或落盘 token / secret）
```

从这条 curl Agent 解析并校验：

| 字段 | 从 curl 取 |
| --- | --- |
| env / gateway 域名 | URL 主机（如 `test-gateway.busyming.com` → env=`test`） |
| Authorization | `-H 'Authorization: …'` |
| deviceId | `-H 'x-device-info: …'` 里 JSON 的 `id`（或等价） |
| X-Operate-Info | **完整**头值（不可自造、不可只写 `{"requestType":"USER"}`） |
| x-ca-key (appKey) | 如 `basic-test` |
| Origin / User-Agent | 可选，建议原样带上 |
| 签名自检素材 | path、body、`Content-MD5`、`x-ca-timestamp`、`x-ca-signature` |

再补：`projectCode` 默认目标仓文件夹名；`appSecret` 优先读工作区 `busyming-fe-stack-html/.env.{env}` 的 `VITE_APP_SECRET`，没有再问用户。

**校验**：curl 的 gateway 主机必须与用户声称的目标 env 一致；Authorization / deviceId / X-Operate-Info 必须来自**同一条** curl（同会话）。跨环境混用常只报「登录已失效」，与真过期难区分——以域名校验为准。

## 环境与 apiBase

| env | gateway origin | appKey |
| --- | --- | --- |
| `dev` | `https://dev-gateway.busyming.com` | `basic-dev` |
| `test` | `https://test-gateway.busyming.com` | `basic-test` |
| `uat` | `https://uat-gateway.busyming.com` | `basic-uat` |
| `pre` | `https://pre-gateway.busyming.com` | `basic` |
| `prod` | `https://gateway.busyming.com` | `basic` |

请求 path 形如：`/stack-service/resource/getGalleryToken`（完整 URL = origin + path）。

## 脚本策略（必读）

curl 无法替代签名与 OSS 直传。Skill 自带参考实现：

- [scripts/api.mjs](scripts/api.mjs) — MSE 现签 + `callApi` + `verifySignatureAgainstCurl`
- [scripts/upload.mjs](scripts/upload.mjs) — getGalleryToken → OSS put → register → manifest/report

Agent 流程：

1. 把上述两个文件**复制**到业务仓 `node_modules/.fe-stack-upload/`（`node_modules` 已 gitignore，**禁止**提交到仓库）  
2. 从 curl 解析后 `export` 环境变量（见脚本头注释）  
3. **先跑签名自检**（见下），再 `node upload.mjs`  
4. **manifest / report / 临时脚本**全部只放在 `node_modules/.fe-stack-upload/`：  
   - `manifest.{env}.json`  
   - `report.{env}.json`  
   - **不要**在仓库根写 `.fe-stack-assets*.json`  
5. 结束后问用户：保留还是删除 `node_modules/.fe-stack-upload/`  
6. **禁止**把脚本知识只留在对话里却不落 skill；也禁止让用户维护长期入库脚本

需要 `ali-oss`：业务仓没有则 `npm i ali-oss -D`（或 pnpm），装在业务仓即可。

## 签名自检（强烈推荐，拿到 curl 后第一步）

用 curl 里的 **path + body + x-ca-timestamp** 重算，与 curl 的 `x-ca-signature` / `Content-MD5` 逐字节比对（`api.mjs` 的 `verifySignatureAgainstCurl`）：

- **相同** → appSecret 与算法正确；后续报错只查身份/业务层，别再怀疑签名  
- **不同** → secret 取错或算法漂移，立刻停

## 必带请求头（现签，不可复用旧 x-ca-signature）

每次 `getGalleryToken` / `register` 都对**当次** body 现算：

| Header | 说明 |
| --- | --- |
| `Authorization` | 与 curl 同会话 Bearer |
| `Content-Type` | `application/json` |
| `Accept` | `application/json, text/plain, */*`（参与 stringToSign，勿改） |
| `Content-MD5` | body UTF-8 的 MD5→Base64 |
| `x-ca-timestamp` | `Date.now()`（毫秒） |
| `x-ca-key` | appKey |
| `x-ca-signature-method` | `HmacSHA256` |
| `x-ca-signature-headers` | 实测为 `x-ca-timestamp` |
| `x-ca-signature` | 现算 |
| `timestamp` | 秒级 |
| `x-device-info` | JSON，`id` = curl 里的 deviceId，**禁止自造** |
| `X-Operate-Info` | **必须**从 curl 原样复制的完整 JSON。⚠️ 只用 `{"requestType":"USER"}` 会网关 400「非法请求!」。含 `resourceId`/`resourceName`/`operateName`/`riskLevel`/`appId` 等，且 **每个环境不同**（不可写死 test 的值去打 dev） |
| `User-Agent` / `Origin` / `Referer` | 建议与 curl 一致 |

`permissionCode: feStackManageStatic`：**可选**。浏览器真实请求里经常没有；脚本默认不强制。若网关/权限体系要求再补。

stringToSign 与 toolkit 对齐（换行必须精确）：

```
POST
application/json, text/plain, */*
{Content-MD5}
application/json
\n
x-ca-timestamp:{ms}\n
/stack-service/resource/...
```

## 上传契约

1. 引用扫描（见下）→ 用户确认传哪些  
2. `POST /stack-service/resource/getGalleryToken` `{ "projectCode" }`  
3. **仅** `ali-oss` `put` 到 `{baseDir}/{relativePath}` — **禁止** `putACL` / `public-read`（STS 会 Access denied；CDN 由桶层控制）。不要照抄管理端 `setGalleryObjectPublicRead`  
4. `POST /stack-service/resource/register`：

```json
{
  "projectCode": "my-app",
  "source": "manage",
  "files": [
    {
      "filePath": "icons/1.jpg",
      "fileName": "1.jpg",
      "fileSize": 1024,
      "mimeType": "image/jpeg",
      "md5": "d41d8cd98f00b204e9800998ecf8427e"
    }
  ]
}
```

- `filePath`：相对 `assets/` 的实际对象路径（不覆盖且重名时可能是 `icons/1_{5位hash}.jpg`），**不含** `projectCode/assets` 前缀  
- `fileName`：真实原始文件名（展示用）  
- `md5`：文件内容 MD5（32 位小写 hex）；嵌套路径登记时服务端会自动补齐父目录记录  
- 响应：`data.items[i].{ cdnUrl, ossKey, relativePath, fileName, md5, ... }`；改引用以 `cdnUrl` 为准  

## 静态文件白名单

上传扩展名仅：`png|jpg|jpeg|gif|webp|svg|ico|ttf|woff|woff2`。  
排除：`.less` / `.scss` / `.css` / `.js` / `.ts` / `.vue` 等源码与样式（非图床静态资源）。

## 先扫引用，再问要不要传

在要 curl / 上传之前（或解析完 curl 后、真正 put 前）：

1. 枚举 assets 白名单文件  
2. 在源码中扫是否引用（路径、`@/assets/...`、文件名等，尽力匹配）  
3. 向用户确认后再传：

```text
发现 N 个静态文件，其中 M 个被代码引用、K 个未引用。
是否上传？(a) 全传  (b) 只传被引用的  (c) 先列出未引用清单我确认
```

未确认前**禁止**默默全量上传。

## 错误分层（先看响应体形状）

| 层 | 特征 | 含义 |
| --- | --- | --- |
| 网关 MSE/身份 | `code` 为**字符串**、字段名常为 `error`、`traceId` 带连字符 | 例：`{"code":"400","error":"非法请求!","traceId":"31b5fc-…"}` → 查签名 / X-Operate-Info / device / 跨环境 token |
| stack-service | `code` 为**数字**、字段名 `message`、`traceId` 常无连字符 | 例：`{"code":400,"message":"缺少参数: projectCode"}` → **已过网关**，别再折腾签名 |

| 现象 | 处理 |
| --- | --- |
| 「非法请求!」 | 多半缺/简化了 `X-Operate-Info`；从真实 curl 原样拷 |
| 「登录已失效」 | **先核对 curl 域名是否目标 env**（跨环境 token 也是这句）；再才是会话过期换 token |
| 设备绑定失败 | deviceId 必须与 Authorization 同条 curl |
| 签名自检失败 | appSecret/env 错 |
| OSS Access denied by authorizer | 是否误调了 putACL；改为只 put |
| 403 缺少资源上传权限 | 平台开 `resourceUpload` |
| 项目不存在 | 改 `projectCode` |

## 增量与产出位置

全部在 `node_modules/.fe-stack-upload/`：

- `manifest.{env}.json` — sha256 增量  
- `report.{env}.json` — 本次报告  

| 本地文件 | 行为 |
| --- | --- |
| manifest 无 / hash 变 | put + register |
| hash 未变 | skip |
| `FE_STACK_FORCE=1` | 全量重传 |

## 改引用（默认开启）

若开启：先切 `feat/fe-stack`（同 migrate）。用 register 的 `cdnUrl` 替换；破坏打包的 import → `replaceStatus: skipped`。默认不删本地 assets。

## 成功后对话里输出的 JSON

在对话中输出摘要（完整报告已在 `node_modules/.fe-stack-upload/report.{env}.json`）：含 `env`、`projectCode`、`cdnDomain`、`summary`、每文件 `cdnUrl` / `uploadStatus` / `replaceStatus`。密钥打码。

## CDN 使用规范（改引用时提醒）

- 凭证 / 登记返回的访问根字段是 **`cdnDomain`**（无末尾 `/`），拼 URL：`cdnDomain + '/' + objectKey`
- **不要默认用原图**：列表缩略图、头像、Banner 等应按展示尺寸加 `?image_process=...`（**不是** OSS 的 `x-oss-process`）
- **引导用户操作**（与语雀手册一致）：研发运维平台 → 前端发布平台 → **资源管理** → 点资源右侧 **处理** → 预览满意后复制带参数的地址
- 常用示例：
  - 列表缩略：`?image_process=resize,w_240/format,webp/quality,Q_75`
  - 头像方图：`?image_process=resize,s_100/crop,mid,w_100,h_100/format,webp/quality,Q_75`
  - H5 内容图：`?image_process=resize,w_750/format,webp/quality,Q_85`
- CDN **不支持** OSS 的 `m_fill` / `m_lfit`；`quality` 的 `Q_`/`q_` 须为 5 的倍数；场景优先用绝对质量 `Q_`
- 仅在需要下载原图、打印、设计稿等场景才用无处理参数的原图 URL

## 禁止

- 无 skill 参考脚本却从零发明签名；或用 curl 裸打 OSS/网关代替脚本  
- 建议网关豁免 MSE  
- 只带 Bearer、缺 `X-Operate-Info`、自造 Operate-Info / deviceId  
- `putACL` / `public-read`  
- 把 manifest、report、脚本写到仓库根或提交 git  
- instance STS 日期目录；`project/list` 换 id；向用户要 projectId  
- 未做引用确认就默默全传  
- 跨环境混用 token/deviceId/Operate-Info  
- assess 阶段上传  
