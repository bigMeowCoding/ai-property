---
name: app-webview-bridge
description: >-
  为门店运营 App（busyming-operation-app）的 RN WebView 接入、实现或排查 H5 Bridge。
  覆盖异步五组上下文、三类认证凭证与两套权限、可信页面限制、导航与工作台抽屉、
  安全区/定位/系统权限、媒体上传与签名、文件预览、报告分享和巡店专用桥、
  TypeScript 声明、旧协议兼容及真机验收。适用于 App 免登、Token/权限选型、
  桥超时或 401、原生相机/相册/扫码/定位/返回等任务；不用于普通浏览器或微信小程序桥。
---

# 门店运营 App WebView Bridge

依据 `busyming-operation-app` 的 App 侧契约实现 H5，不根据方法名、旧 H5 样例或
User-Agent 猜测行为。

## 信息源与读取路由

| 资料 | 用途 | 优先级 |
|---|---|---|
| [reference/app-bridge-api.md](reference/app-bridge-api.md) | App 基线 `feature/cwc_2.1.5`、提交 `34310b6`、2026-09-05 核对的完整契约、类型和验收清单 | 最高 |
| [templates/auth-context.md](templates/auth-context.md) | 新 H5 等待异步上下文并延迟启动业务的通用骨架 | 从属权威契约 |
| [templates/native-capabilities.md](templates/native-capabilities.md) | 安全区、返回、Promise 媒体和旧事件流的实现骨架 | 从属权威契约 |
| [reference/bridge-contract.md](reference/bridge-contract.md) | `busyming-store-information-h5` 的历史定制接入切片 | 仅维护该旧链路时参考 |

按任务加载资料：

- 初始化、Token、权限、401：读权威文档第一部分与第 8 节；实现时再读 `auth-context.md`。
- 某个 `__APP_*` 方法：读权威文档第 7 节公共约定及该方法所属章节。
- 相机、相册、视频、文件上传：读第 12、13 节；不要混合新旧协议。
- 全局声明：直接使用权威文档附录 A；项目已有同名声明时合并。
- 联调、验收或排错：读附录 B，并核对目标 iOS/Android 安装包。
- 只有任务明确涉及旧定制上下文、`receiveRNData` 历史封装或参考项目时，才读
  `bridge-contract.md`；冲突一律服从权威文档。

## 新 H5 的启动契约

推荐顺序固定为：等待桥可用 → 获取上下文 → 配置请求与权限 → 启动业务页面。

1. 使用 `window.__APP_GET_CONTEXT__(): Promise<ReadyAppContext>` 获取当前快照。
2. 桥脚本可能晚于 H5 加载；同时监听一次 `app-context-bridge-ready`，不要轮询。
3. H5 总等待默认可取 15 秒，并监听 `pagehide`；离页后丢弃旧结果。
4. 成功后再延迟导入业务入口，在 `mount(context)` 内初始化请求客户端、权限、路由和框架。
5. `window.__APP_CONTEXT__` 只用于旧链路兼容；它可能未及时注入，也不是持续订阅。
6. 旧 App 没有异步桥时提示升级或使用独立开发 Mock，不能把旧对象假装成已就绪新上下文。

公共异步上下文成功后有五组平级数据：

| 字段 | 用途 |
|---|---|
| `unifiedPortal` | 统一门户 Token 与原始门户用户信息 |
| `personnel` | 原业务 Token、人员白名单信息、原业务权限码 |
| `portalAuthObj` | 门户有效权限码、资源树、用户资源 ID |
| `deviceInfo` | App 设备描述；失败时可为 `null` |
| `zoneOwnerInfo` | 当前战区和负责人；字段仍可能为空 |

异步桥只向配置的可信根路径及子路径开放，并拒绝专用 `route.params.appContext` 页面。
处理 `UNTRUSTED_PAGE`、`UNSUPPORTED_CONTEXT`、`SESSION_CHANGED`、超时等错误时按文档表格
给出明确出口；不能靠延长等待、篡改上下文或无限重试绕过。

## 认证与权限必须分流

| 系统 | 凭证 | 权限 |
|---|---|---|
| 原业务/人资接口 | `context.personnel.accessToken`；旧兼容字段为 `__APP_TOKEN__` | `context.personnel.permissionCodes` |
| 明确要求 `BizMidPlatform` | `await __APP_GET_TOKEN_AUTHINFO__({ bizType: 'BizMidPlatform', brand: 'LSHM' })` | 按该后端合同 |
| 统一门户/统一网关 | `context.unifiedPortal.accessToken` | `portalAuthObj.portalAuthCodes` 或统一类型后的 `resourceIds` |

- 三类凭证不可互换，不要收敛成含义不明的单个 `token` 变量。
- 正常空权限是合法结果，显示无权限；不要持续等待数组变为非空。
- 资源树不是当前用户的授权菜单；结合 `resourceIds` 和产品规则保留必要父节点。
- H5 隐藏按钮不能替代后端鉴权。
- Token 不等于完整请求配置。MSE 签名、设备头、`X-Operate-Info` 和刷新协议必须按对应
  网关合同确认；不要在 H5 内置生产 Secret。
- `__APP_GET_CONTEXT__()` 没有 `forceRefreshToken` 参数，重复调用不保证 Token 变化。

## 调用桥方法

先检查具体函数是否存在；`__BUSYMING_OPERATION_APP__` 只能帮助识别容器，不能证明某个
能力可用。`__APP_BRIDGE_CODE__ = 1` 也不能代表具备新方法。

区分返回模型：

- `void`：只表示操作已发出，没有成功回执，不能据此判完成。
- `Promise<T>`：捕获 reject 并检查结果内失败标志；交互操作防并发。
- 同步字符串：例如安全区返回 JSON 字符串，解析失败要降级。
- 事件流：先注册根级回调再调用；不要假设一定有统一结束事件。
- H5 超时只结束自身等待，不会关闭相机或取消 App 任务；超时后不要自动重开。

不要自行生成底层 `callbackId`、调用 `ReactNativeWebView.postMessage({ action: ... })`、覆盖
App 内部回调，或把原生内部 action 当公共 API。

## 关键能力决策

- 同一 H5 内跳转用 H5 Router；回退/关闭用 `__APP_ROUTER_BACK__()`；回运营指导工作台用
  `__APP_GO_HOME_TAB__()`；新开可信 WebView 才用 `__APP_OPEN_NEW_WINDOW__()`。
- 当前工作台抽屉用 `__APP_OPEN_WORKBENCH_DRAWER__()`，但只在特定宿主注入，必须探测。
- 当前没有“跳任意 App Tab”的公共桥，不传虚构参数，不直接发内部 `openPage` action。
- 新媒体优先 `*_WITH_RESULT__` Promise 协议，并逐个检查文件 `status`；需要上传进度、
  逐文件回调或旧包兼容时才用旧事件流。一次用户操作只能发起一套协议。
- `__APP_OPEN_SIGNATURE__()` 的取消/超时通常在结果中表达；签名 Base64 不记录。
- `__APP_GET_CURRENT_LOCATION__()` 当前接收 `{ timeout, accuracy }` 对象；结果是兼容字符串
  行为的装箱 `String` 对象或 `''`，用 `String(result)` 解析并验证数值。
- `__APP_SCAN_CODE__()` 当前返回 `{ success, data? }`；二维码内容按业务白名单解析。
- `__APP_DOCUMENT_VIEW__()` 声明为 Promise 但正常路径不 settle；用 `void` 调用，禁止 `await`。
- 键盘桥只有注册没有注销，在根模块注册一次。生命周期同时读取初始快照、监听事件并按
  `sequence` 去重。

## 401、身份变化与数据更新

- 网络失败、超时、5xx 不得清整个 App 登录态。
- 403 或空权限展示无权限，不无限刷新。
- 确认原业务登录失效后，对并发失败去重，再调用一次 `__APP_GO_LOGIN__()`；该方法会清理
  App 用户登录缓存并重置到登录页，不保证返回原 H5。
- 门户 401 先核对凭证归属和后端合同，可重新取一次上下文检查新快照，但不得自动无限重发，
  有副作用的提交接口未经业务确认不得自动重放。
- 旧同步对象可被热注入更新；异步方法每次返回快照，不会持续更新 H5 已保存对象。
  App 没有通用 `appContextChanged` 事件。用户/战区身份变化或恢复流程可能重建 WebView，
  页面必须可重复初始化并清理旧账号派生缓存。

## 安全与日志

禁止把 Token、refreshToken、TokenInfo、签名、Secret、完整上下文、原始接口响应、手机号、
签名 Base64 或完整资源树写入日志、埋点、监控、URL、截图或长期存储。排错只记录 App/系统
版本、方法名、脱敏错误码、耗时、字段是否存在和数组长度。

## 完成前验证

1. 静态类型、lint 和相关单测通过；声明与实际调用签名一致。
2. 冷启动、桥晚到、超时、网络恢复、合法空权限、401 去重和页面离开均有明确行为。
3. 新旧 App/普通浏览器缺桥时有升级提示或安全降级，不直接调用 `undefined`。
4. 媒体取消、部分失败、超限与空结果不被当成成功；文档预览不因 `await` 卡死。
5. 目标 iOS 和 Android 安装包分别真机验收权限、定位、相机/相册、返回、前后台与弱网。
6. 核对安装包版本、环境、最终重定向路径和宿主能力；代码分支支持不等于线上包已发布。
