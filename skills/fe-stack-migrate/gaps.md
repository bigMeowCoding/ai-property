# 手册外 / 其他注意事项（gaps）

下列项已写入 skill 同目录《使用手册》**「其他注意事项」**、「流水线改造」与「资源管理」。评估时**按业务实际情况对照**（非逐项必做）；手册未写到的新缺口再列入报告「人工待办」。

| 主题 | 手册位置 |
| --- | --- |
| 企微 / OAuth / 内嵌小程序白名单与回调 | 其他注意事项 §1（**内嵌场景必改域名**） |
| 入口系统（含小程序 webview URL） | §2 |
| CORS / Cookie | §3 |
| 同域 API 反代 | §4 |
| 流水线模板选型（直连 vs nginx）/ build 脚本 | §5 + 流水线改造 |
| 健康检查 | §6 |
| 安全响应头 | §7 |
| 自定义域名 / nginx 兼容旧路径 | §8 + 路由 · 自定义域名 + 流水线 nginx 小节 |
| 业务仓 Nginx / Dockerfile | §9（模板 A 默认不动；模板 B 必改） |
| assets 迁 CDN + 裁剪 | §10 + 图床稳定路径 + CDN 图片处理（`cdnDomain`；资源右侧 **处理** + `?image_process=`） |
| 密钥打码 | §11 |

## Agent 注意

- 评估报告只点名**本项目相关**项的责任方与是否阻断上线；无关项写「不适用」即可。  
- **不要**为迁就某个业务项目改手册契约；发现手册过时先更新 meta `skills/fe-stack-migrate/`（权威副本）。  
- 流水线须写明模板 **A（平台直连）** 或 **B（…-nginx）**；B 才改 Dockerfile/nginx。  
- upload-assets：开场只要一条真实 curl（研发运维平台「资源管理」Copy as cURL）；skill 自带 `scripts/api.mjs`+`upload.mjs`；字段用 **`cdnDomain`**；改引用后引导用户到资源管理点右侧 **处理** 预览再复制 `?image_process=`；见 `upload-assets.md`。
