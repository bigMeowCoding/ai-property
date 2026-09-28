# 按钮权限消费机制细节

来源：`busyming-store-opening-h5`（分支 feat/store-activity-1.1-on-master）实测。
文件路径均指参考项目相对路径。本节沉淀的是「权限上下文就位之后，页面/按钮权限
怎么消费」，与 [real-gateway-debug.md](real-gateway-debug.md) 的「权限引导」
是同一链路的前后两段。

## 1. 权限码命名与建档（硬约束）

- 单一契约文件 `src/service/activity/permissionCodes.ts`：service 与页面共同消费，
  所有值须与**权限系统已建资源编码逐字一致**。
- 用 `PERMISSION_APP_CODE` 常量 + 模板拼接生成全量前缀字符串
  （如 `` `${PERMISSION_APP_CODE}newStoreActivityMy` ``），杜绝手写前缀漂移。
- 权限码必须**纯字母数字 + camelCase**：英文字母与阿拉伯数字，无点、下划线、
  连字符等符号。这是后端 ACL 系统解析资源码的硬约束。
- 页面码与按钮码分组常量：`NEW_STORE_ACTIVITY_PAGE_PERMISSION` 与各
  `*_BUTTON_PERMISSION`（home/my/manage/assign/approval/detail 等），
  页面注册表、AuthButton、按钮门控统一从契约文件取码。
- 例外：详情页 CONFIRM 后端未建档独立资源码 → **不走权限门控**，显示与否完全
  以后端 buttons[] 为准（在契约文件中注释声明，不臆造码）。

## 2. 消费基础设施

| 设施           | 位置                                                     | 契约                                                                                                            |
| -------------- | -------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| 权限状态       | store `userPermissionKeys: string[]` + `permissionReady` | 引导落定后组件才可判定，页面不永久等待                                                                          |
| 单/多 key 判定 | `src/hooks/usePermission.ts`                             | `hasPermission(key)` / `hasAllPermissions(keys)` / `hasAnyPermission(keys)`；`userPermissionKeys.includes` 实现 |
| 声明式按钮守卫 | `src/components/common/AuthButton.tsx`                   | `permissionKey` + `fallback`，无权限渲染 fallback（默认不渲染）                                                 |
| 路由级门控     | `src/router/pageRoutePermissions.ts`                     | `PAGE_ROUTE_PERMISSION_REGISTRY`：`{ path, permissionKey }` 注册表，路由消费 `meta.permissionKey`               |

关键契约：

- 空串**不再**短路放行（1.1 权限码定稿后回收恒真口径），统一按权限集合判定；
  `has11Permission` 恒真等历史口径一并回收。
- `hasAllPermissions` / `hasAnyPermission` 空数组返回 true（空条件语义）。
- 权限引导未落定时（`permissionReady` 为 false）所有判定返回 false（hr-h5 fail-closed
  口径），组件不得在未就绪时做放行判定；开发旁路已按工程裁决删除，hook 内不再有
  任何旁路短路。

## 3. 按钮渲染：后端 buttons[] 数组驱动

列表卡片按钮区的**唯一权威来源是后端接口下发的 `buttons: string[]`**，
前端不做状态推演：

1. 后端按活动状态、角色差异化下发按钮编码（如 `NAVIGATION / DETAIL / CONFIRM /
ADJUST / ASSIGN / CANCEL_DELAY`）。
2. 前端 `ACTIVITY_BUTTON_MAP`（`src/pages/activity/constants/activityEnums.ts`）
   仅作**接线元数据**：`code → { label, action }`（action 为 openSheet / navigate /
   goDetail / openAssign 等动作标识，弹窗与跳转逻辑由消费方接线，映射表不含业务）。
3. `getButtonMeta(code)` 安全取元数据：后端下发**未知枚举返回 undefined**，
   消费方过滤忽略（防后端新增枚举打爆前端，AC9 裁定）。
4. `NAVIGATION` 由地址行导航胶囊承接，按钮区不重复渲染（胶囊显隐同样由 buttons
   驱动）。
5. `CHANGE_BUTTON_CODES`（CONFIRM / ADJUST / CANCEL_DELAY）：`hasPendingChange=true`
   时置灰，点击统一 Toast 提示阻断态。
6. 按钮级权限兜底可选：`buttonPermissionKeys` 配置后无权限按钮不渲染；
   **未配置的按钮 code（工具能力如 NAVIGATION）不走权限门控**。
7. 禁止：前端根据 `status` + `roleType` 等字段自行推演按钮列表。

## 4. 权限数据来源与求交（承接权限引导）

- 权限资源接口调用为主（减少本地配置化）：权限来源优先级收敛为三级（hr-h5 已落地）：
  store 权限上下文判源（防御路径，当前无运行时写入源）> user-auth 双接口（正式来源：
  token + userId 齐备的所有真实身份统一走接口，含 App 免登与生产）> fail-closed 空
  权限。App 不注入权限字段（portalAuthObj 仅作诊断日志）；URL `?permissionKeys=`
  调试通道与 App 直供求交层已按工程裁决删除。参考项目当前仍为五来源过渡形态
  （localDebug 快照与调试覆盖、dev-mock 本地合成），仅作对照，改造目标形态见
  [real-gateway-debug.md](real-gateway-debug.md)。
- user-auth 双接口求交：`POST /user-auth/web/app/resource/tree/by/app/id`
  （应用资源树，body `{ appCode }`）× `POST /user-auth/web/user/resource/list/by/app`
  （用户 resourceIds，body `{ id, appCode }`）→ 权限码集合；树扁平化 / 求交纯函数
  在 `src/helpers/permissionTree.ts`；接口封装与通道骨架见
  [../templates/local-login-modules.md](../templates/local-login-modules.md) §4.3。
- fail-closed：引导失败写空集合并置 `permissionReady`，路由守卫不永久等待。
- dev:mock 的合成资源同样必须是**合法权限输入**（页面 type=2 挂按钮 type=3，
  resourceIds 与树节点 id 一致，经 `resolveOwnedPermissionCodes` 求交），通过
  mock user-auth 双接口下发（见
  [../templates/mock-modules.md](../templates/mock-modules.md) §2），而不是本地合成
  上下文绕过权限系统。

## 5. 与本地开发模式的关系

- 按钮渲染逻辑与「Mock / 真实」模式无关：`buttons[]` 来自接口（mock 定义或真实
  网关），前端消费逻辑完全一致，切换模式不需要改组件。
- 新增权限码的本地开发闭环：`permissionCodes.ts` 建档 → dev:mock 合成树放行 →
  localDebug 快照 / App 真机验证门控 → 核对与权限系统建档码逐字一致。
