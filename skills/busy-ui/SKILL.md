---
name: busy-ui
description: |
  Busy-UI（@busy-fe/ui v7）公司管理端组件库能力手册。MUST be used when implementing or reviewing
  any UI with Busy-UI / @busy-fe/ui: lists, forms, selectors, dialogs, feedback, ProTable, Searcher,
  MessageBox, PageableSelect, Form, BusyInput, business selectors, or choosing which component to use.
  Also use when the user asks about Busy-UI props/events/slots/methods, component selection, deprecated
  Table/StoreSelector migration, or management-console page patterns. Read this skill BEFORE writing
  Busy-UI code; query references/components.md for full API.
metadata:
  version: "1.3.0"
---

# Busy-UI 组件库能力手册

Busy-UI 是公司管理端 UI 组件库（**v7.0.0-next.51**，以项目 `package.json` 为准），共 **70** 个组件。本 Skill 是 Agent 查询 Busy-UI **选型、用法、Prop/Event/Slot/Methods** 的**唯一权威入口**。

> 官网：https://busy-fe.hnlshm.com/busy-ui/

---

## Agent 必读（开发前）

涉及 `@busy-fe/ui` / Busy-UI 的实现、重构、Review、测试接线时，**必须先读取本 Skill**，再写代码或给建议。有问题查本 Skill + `references/components.md`，勿臆造 API。

### 咨询流程

```text
1. 读本 Skill（选型原则 + 场景速查 + 项目约定）
2. 查具体组件 API → 读 references/components.md（按组件名搜索）
3. 列表 URL 基建 → 读项目 .ai/specs/target-manage-v1/01-platform-foundation.md §4.2–4.3
4. 仍不确定 → components.md 官网 link，或对照仓库已有用法
```

### 何时必须读本 Skill

| 场景 | 先查 |
|------|------|
| 新建/改列表页（表格、筛选、分页） | 本 Skill §ProTable + §项目列表页 |
| 表单、录入、校验 | `Form`、`BusyInput`、`PageableSelect`、`DatePicker` |
| 二次确认、提示、弹窗 | `MessageBox`、`Message`、`Dialog`、`Drawer` |
| 选品牌/门店/人员/组织/区域 | 业务 `*Selector` / `*SelectorV2`，禁止自封装 |
| 不确定用哪个组件 | 本 Skill §快速选型表 → components.md |
| 代码里出现 `Table`、`StoreSelector` 等 | 本 Skill §废弃迁移 |
| Review Busy-UI 用法 | 对照本 Skill |

---

## 快速选型表

| 业务场景 | 选用 |
|----------|------|
| 带筛选的列表页 | `Searcher` + `ProTable` + `useUrlState` |
| 纯展示表格 | `ProTable`（`columns` + `pagination`） |
| 表格状态列（圆点 + 文案） | `ProTable ColumnSchema.render` + `BusyBadge status` |
| 详情只读 | `Descriptions` |
| 新建/编辑表单 | `Form` + `BusyInput` / `PageableSelect` / `DatePicker` |
| 独立筛选栏（≥3 项或需展开） | `Searcher`（`searchConfig`） |
| 选门店/人员/组织/品牌/区域 | `StoreSelectorV2`、`UserSelectorV2`、`OrgSelector`、`BrandSelector`、`AreaSelector` |
| 操作成功/失败 | `Message` |
| 删除/启停等二次确认 | `MessageBox.confirm` |
| 复杂弹窗 / 侧滑 | `Dialog` / `Drawer` |
| 步骤向导 / 页内 Tab | `Steps` / `BusyTabs` |

---

## 选型原则

- **优先 ProTable** 替代旧 Table（Table 已废弃）；模板标签用 **BusyProTable**
- **优先业务选择器**，不要重复封装
- **废弃组件** 新需求禁止使用
- **表单**：Form + BusyInput + PageableSelect + DatePicker + Searcher；校验走 Form，不引入 vee-validate / Zod
- **反馈**：Message 轻提示、MessageBox 确认、Dialog 自定义
- **样式**：页面根 class + `scoped`；改内部样式用 `:deep()`；主题色 `APP_THEME_COLOR`

### 废弃与迁移

| 废弃 | 替代 |
|------|------|
| `Table` / `BusyTable` | `ProTable` / `BusyProTable` |
| `StoreSelector` | `StoreSelectorV2` |
| `UserSelector` | `UserSelectorV2` |

---

## ProTable 要点

- 内置：搜索区、分页、Tabs、工具栏、列设置、行选择、操作列（`actions`）
- 搜索联动：`@search` / `@reset`；`getSearchParams()`、`refresh()`、`reset()`
- 两种数据模式（二选一）：

| 模式 | 用法 | 适用 |
|------|------|------|
| **`request`** | 传入 `request`，组件自管 loading/data | 简单 CRUD |
| **`data` + composable** | 外部拉数 + `:data` + 绑定分页 | **busyming-target-manage 默认** |

- 行操作确认：**MessageBox.confirm**，不用浏览器 `confirm`
- 行操作权限：ProTable `actions` + `v-permission` 或 composable 过滤
- 行身份：必须显式声明 `row-key`，并使用契约保证唯一的业务主键；禁止使用 `name` / `orgName` 等可重复展示字段。接口无行 ID 时的适配与测试要求见 `.ai/AGENTS.md` 「ProTable 行键唯一性」。

### 状态列与自定义视觉列

状态圆点、Tag、徽标等已有 Busy-UI 标准组件的列，优先用 `ColumnSchema.render` 直接渲染对应组件。状态列统一使用 `BusyBadge` 的 `status + text` 模式；不要在页面内重复手写圆点 DOM、颜色 class 和 scoped CSS，也不要仅因多个页面都未出现自定义内容就先判断 ProTable 组件损坏。

```ts
import { h } from 'vue'
import BusyBadge from '@busy-fe/ui/Badge'

const columns = [
  {
    prop: 'statusName',
    label: '状态',
    render: (_value, row) => h(BusyBadge, {
      status: statusTone(row.status),
      text: row.statusName
    })
  }
]

function statusTone(status: string) {
  if (status === 'ENABLED') return 'success'
  if (status === 'DISABLED') return 'info'

  return 'primary'
}
```

- `status` 可选：`primary`（蓝）、`success`（绿）、`warning`、`error`、`info`（灰）。状态点模式用 `status`，不是徽标背景色的 `type`；两者枚举也不同（`status` 用 `error`，`type` 用 `danger`）。
- 展示文案继续使用接口返回的名称；颜色优先依据接口协议值或权威公共字典映射。不得为了颜色擅自给返回 DTO 补造后端未承诺的状态码字段；未知状态降级为 `info`。
- 只有标准组件或 `render` 无法承载复杂交互时才使用列 slot。驼峰 `prop` 使用 slot 时，显式配置稳定的全小写 kebab-case `col-*` 名称，并保证 `ColumnSchema.slot` 与模板同名。
- 排查“状态列没有变化”时，依次确认页面实际加载的 JS/CSS 产物版本、路由权限是否真正进入目标列表、列配置是否到达真实 ProTable、最终 DOM 是否出现 `.busy-badge--status`。不要把测试环境旧产物、权限守卫或页面自定义样式问题归因于 Table。

---

## busyming-target-manage 项目列表页

### 推荐结构

```text
ListView
├── PageHeader（可选）
├── Searcher 或 ProTable 内置搜索区
└── ProTable（BusyProTable）
    ├── columns + actions
    └── pagination ← 绑定 useUrlState 的 pageNo / pageSize
```

| 筛选项数量 | 推荐 |
|------------|------|
| ≤ 2 且布局简单 | ProTable 内置搜索 或 Searcher |
| ≥ 3 或需展开/复杂控件 | Searcher + ProTable（仅表格+分页） |
| 须 URL 可分享 | 搜索值、分页经 **useUrlState** 同步 query |

### useUrlState 接线

```text
useUrlState(DEFAULTS)
  → listParams = buildListParams({ ...state })
  → watch(listParams) → fetchList()
  → ProTable :data="records" + pagination 绑定 state.pageNo / pageSize / totalCount
  → Searcher @search / @reset → setState({ pageNo: 1, ...filters })
```

**筛选参数保真**：`type: 'input'` 等自由文本须按 Spec 原样透传（可做已确认的 `trim` / 旧格式拒绝），禁止复用 Select、日期选择器或路由身份的完整值校验器。`buildListParams` 会过滤空值，所以上游误归一为空就会静默丢参。详见 `.ai/handbook/vue-pages.md` 「列表筛选参数语义一致性」。

参考：`src/composables/list-page-scaffold.example.ts`、`src/modules/target-manage/composables/use-goal-summary.ts`。

> 勿手写 `el-form` + `el-table` + `el-pagination` 三套拼装。

---

## 组件分类速查

| 大类 | 子分类 | 代表组件 |
|------|--------|----------|
| 基础组件 | 全局 | ThemeColor、Icon、Text、Button、Layout |
| 基础组件 | 导航 | PortalNav、Steps、BusyTabs |
| 基础组件 | 反馈提醒 | Dialog、MessageBox、Message、GuideBubble、Drawer |
| 基础组件 | 信息录入 | BusyInput、PageableSelect、DatePicker、Upload、Form、Searcher |
| 基础组件 | 信息展示 | ProTable、Pagination、Tag、Descriptions、Avatar |
| 业务组件 | - | BrandSelector、StoreSelectorV2、UserSelectorV2、AreaSelector、OrgSelector |

---

## 查 API（references/components.md）

**[references/components.md](references/components.md)** — 70 组件 Prop / Event / Slot / Methods。

1. 搜索 `### {组件名}`（如 `### ProTable`）
2. 阅读属性、事件、插槽、方法表格
3. 需要详情时用节末官网 link

---

## 测试约定

- 不断言 Busy-UI 内部实现、主题色 hex、像素级样式
- 列表业务逻辑（URL ↔ 请求参数）→ composable Hook 测 + 集成测；每个修改的筛选字段须断言代表性非空值进入最终 API `entity`
- ProTable / Searcher 接线 → 组件测 stub Busy-UI
- ProTable 自定义 `render` / slot 的关键视觉列 → 至少保留一个挂载真实 BusyProTable 的集成用例；stub 只断言列配置与业务映射，不能证明真实组件消费了渲染入口
- BusyBadge 状态列集成测断言圆点、文案及语义 class（如 `busy-badge__status-dot--success`），不锁定主题 hex 或像素值

---

## 相关文档

| 文档 | 说明 |
|------|------|
| `references/components.md` | 70 组件 API 全集 |
| 项目 `.ai/AGENTS.md` | 协作规则、样式隔离 |
| 项目 `01-platform-foundation.md` §4 | URL 列表基建 |
