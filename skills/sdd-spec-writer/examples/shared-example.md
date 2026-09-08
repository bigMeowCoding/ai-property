# Spec: 通用表格组件（SharedTable）
type: shared

## 1. 需求定义

### 1.1 背景与目标
- 复用场景：交易业务的订单列表、运营后台的用户管理、财务系统的账单查询等 10+ 个页面
- 当前痛点：各业务线重复实现表格 + 分页 + 排序 + 筛选，逻辑不统一，维护成本高
- 成功指标：新表格需求接入成本降低 70%，使用方满意度 > 4.5/5

### 1.2 能力范围
- **In-Scope（提供的能力）：**
  - [ ] 基础表格渲染（列配置、数据展示）
  - [ ] 分页功能（内部分页 / 外部分页）
  - [ ] 排序功能（单列 / 多列）
  - [ ] 行选择功能（单选 / 多选 / 全选）
  - [ ] 表头筛选功能（文本筛选 / 下拉筛选 / 日期筛选）
  - [ ] 空状态 / 加载状态 / 错误状态
  - [ ] 扩展点（header slot、empty slot、自定义行、操作列）
- **Out-of-Scope（业务方自行处理）：**
  - [ ] 数据导出 Excel（业务方自行集成）
  - [ ] 复杂嵌套表格（树形数据，后续迭代考虑）
  - [ ] 表格编辑单元格（业务方自行实现或后续扩展）

### 1.3 待确认项
| 问题 | 当前假设 | 优先级 |
|------|----------|--------|
| 是否支持虚拟滚动？ | 建议：首期不支持，数据量 > 1000 时由业务方分页 | 非阻塞 |
| 筛选条件是前端还是后端？ | 建议：支持两种模式，通过配置切换 | 阻塞 |
| 行选择数据是受控还是非受控？ | 建议：支持两种模式 | 阻塞 |

---

## 2. 项目资产对齐（Project Asset Alignment）

### 2.1 复用性审查（Reusability Audit）

| 检查项 | 现有资产 | 状态 | 本次策略 |
|--------|----------|------|----------|
| 基础表格 | `BaseTable` 组件（仅渲染） | ✅ 已有 | 调研现有实现，评估扩展或重建 |
| 分页组件 | `Pagination` 组件 | ✅ 已有 | 复用，不重建 |
| 排序逻辑 | `sortBy` 工具函数 | ✅ 已有 | 复用或增强 |
| 选择框 | `Checkbox` 组件 | ✅ 已有 | 复用 |
| 筛选下拉 | - | ❌ 无 | **新建** 表头筛选能力 |
| 空状态组件 | `EmptyState` 组件 | ✅ 已有 | 复用 |
| 加载状态 | `Loading` 组件 | ✅ 已有 | 复用 |
| 主题系统 | Design Token 已配置 | ✅ 已有 | 组件样式全部基于 Token |

### 2.2 规范对齐（Standard Compliance）

| 规范类别 | 项目规范要求 | 本次应用方式 |
|----------|--------------|--------------|
| **组件规范** | 统一使用函数组件 + Hooks，Props 必须有类型定义 | 遵循规范 |
| **样式规范** | 使用 CSS Modules，禁止行内样式 | 遵循规范 |
| **颜色/字体** | 使用 Design Token：`--color-primary`、`--font-size-base` | 所有颜色、字号使用 Token |
| **目录规范** | 组件放 `components/shared/`，含 `index.tsx` + `style.module.css` + `__tests__/` | `components/shared/SharedTable/` |
| **文档规范** | 组件必须有使用示例文档 | 提供 README + 3 个场景示例 |
| **测试规范** | 组件测试覆盖率 ≥ 85%，交互事件必须测试 | 遵循测试规范 |

---

## 3. 复用场景分析（Usage Scenarios）

| 场景 | 业务方 | 当前实现方式 | 使用本组件后的方式 |
|------|--------|--------------|-------------------|
| 订单列表 | 交易业务 | 自研表格 + 分页 + 排序，约 300 行代码 | `<SharedTable columns={orderColumns} dataSource={orders} pagination />` |
| 用户管理 | 运营后台 | copy 交易业务的表格代码改字段 | `<SharedTable columns={userColumns} dataSource={users} rowSelection />` |
| 账单查询 | 财务系统 | 自研表格 + 日期筛选，约 250 行代码 | `<SharedTable columns={billColumns} dataSource={bills} filters />` |

---

## 4. 接口设计（Interface Design）

### 4.1 Props / API 定义

| 属性 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| dataSource | T[] | 是 | - | 数据源 |
| columns | Column<T>[] | 是 | - | 列配置 |
| loading | boolean | 否 | false | 加载状态 |
| pagination | boolean \| PaginationConfig | 否 | false | 分页配置 |
| rowSelection | RowSelectionConfig<T> | 否 | - | 行选择配置 |
| sort | SortConfig | 否 | - | 排序配置 |
| filters | FilterConfig<T>[] | 否 | - | 筛选配置 |
| empty | ReactNode | 否 | `<EmptyState />` | 自定义空状态 |
| header | ReactNode | 否 | - | 自定义表头区域 |
| rowKey | string \| ((record: T) => string) | 否 | 'id' | 行唯一标识 |
| onRowClick | (record: T, index: number) => void | 否 | - | 行点击回调 |
| onChange | (params: TableChangeParams) => void | 否 | - | 表格变化回调（分页/排序/筛选/选择） |
| scroll | { x?: number; y?: number } | 否 | - | 滚动配置 |
| className | string | 否 | - | 自定义类名 |
| style | CSSProperties | 否 | - | 自定义样式 |

### 4.2 配置项结构

```typescript
interface Column<T = any> {
  key: string;
  title: string;
  dataIndex?: string | string[]; // 支持嵌套路径：'user.name' 或 ['user', 'name']
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
  sorter?: boolean | ((a: T, b: T) => number);
  filters?: FilterItem[];
  filterMode?: 'frontend' | 'backend'; // 筛选模式
  render?: (value: any, record: T, index: number) => ReactNode;
  className?: string;
}

interface FilterItem {
  text: string;
  value: string | number;
}

interface PaginationConfig {
  current?: number;
  pageSize?: number;
  total?: number;
  pageSizeOptions?: number[];
  showSizeChanger?: boolean;
  showTotal?: boolean;
  onChange?: (page: number, pageSize: number) => void;
}

interface RowSelectionConfig<T = any> {
  type?: 'checkbox' | 'radio';
  selectedRowKeys?: string[];
  onChange?: (selectedRowKeys: string[], selectedRows: T[]) => void;
  onSelect?: (record: T, selected: boolean, selectedRows: T[]) => void;
  onSelectAll?: (selected: boolean, selectedRows: T[], changeRows: T[]) => void;
  getCheckboxProps?: (record: T) => { disabled?: boolean };
}

interface SortConfig {
  sortField?: string;
  sortOrder?: 'ascend' | 'descend' | null;
  onChange?: (field: string, order: 'ascend' | 'descend' | null) => void;
}

interface TableChangeParams {
  pagination: { current: number; pageSize: number };
  sort: { field: string; order: 'ascend' | 'descend' | null };
  filters: Record<string, (string | number)[]>;
  selectedRows: any[];
}
```

### 4.3 插槽 / 扩展点

| 扩展点 | 类型 | 用途 |
|--------|------|------|
| header | ReactNode | 自定义表头区域（如标题、操作按钮） |
| empty | ReactNode | 自定义空状态 |
| rowClassName | string \| ((record: T, index: number) => string) | 自定义行样式 |
| expandRow | (record: T) => ReactNode | 展开行内容 |
| actionColumn | Column<T> | 操作列（编辑/删除/查看） |

---

## 5. 使用示例

### 5.1 基础用法（覆盖 80% 场景）

```tsx
import { SharedTable } from '@components/shared/SharedTable';

const columns = [
  { key: 'name', title: '姓名', dataIndex: 'name' },
  { key: 'age', title: '年龄', dataIndex: 'age', width: 80 },
  { key: 'address', title: '地址', dataIndex: 'address', ellipsis: true },
];

const data = [
  { id: '1', name: '张三', age: 28, address: '北京市朝阳区' },
  { id: '2', name: '李四', age: 32, address: '上海市浦东新区' },
];

<SharedTable
  dataSource={data}
  columns={columns}
  rowKey="id"
/>
```

### 5.2 高级用法（分页 + 排序 + 选择）

```tsx
<SharedTable
  dataSource={orders}
  columns={orderColumns}
  pagination={{
    current: 1,
    pageSize: 20,
    total: 1000,
    showSizeChanger: true,
    showTotal: true,
  }}
  sort={{
    sortField: 'createTime',
    sortOrder: 'descend',
    onChange: (field, order) => fetchOrders({ sortField: field, sortOrder: order }),
  }}
  rowSelection={{
    type: 'checkbox',
    selectedRowKeys: selectedIds,
    onChange: (keys, rows) => setSelectedIds(keys),
  }}
  onChange={(params) => {
    // 统一处理分页/排序/筛选/选择变化
    fetchOrders(params);
  }}
/>
```

### 5.3 筛选用法（表头筛选）

```tsx
const columns = [
  {
    key: 'status',
    title: '状态',
    dataIndex: 'status',
    filters: [
      { text: '待处理', value: 'pending' },
      { text: '处理中', value: 'processing' },
      { text: '已完成', value: 'completed' },
    ],
    filterMode: 'backend', // 筛选条件通过 onChange 回调给后端
  },
  {
    key: 'amount',
    title: '金额',
    dataIndex: 'amount',
    sorter: (a, b) => a.amount - b.amount,
  },
];

<SharedTable
  dataSource={bills}
  columns={columns}
  onChange={(params) => {
    // params.filters = { status: ['pending', 'processing'] }
    fetchBills(params);
  }}
/>
```

### 5.4 自定义扩展

```tsx
<SharedTable
  dataSource={users}
  columns={userColumns}
  header={
    <div className="table-header">
      <h3>用户列表</h3>
      <Button onClick={handleExport}>导出</Button>
    </div>
  }
  empty={<CustomEmpty description="暂无用户数据" />}
  rowClassName={(record) => record.status === 'inactive' ? 'row-inactive' : ''}
  expandRow={(record) => <UserDetail user={record} />}
/>
```

---

## 6. 技术实现要点

- **内部状态管理：**
  - 分页状态：current / pageSize（受控/非受控双模式）
  - 排序状态：sortField / sortOrder
  - 筛选状态：activeFilters（Map 结构）
  - 选择状态：selectedRowKeys / selectedRows
- **性能优化点：**
  - 使用 `React.memo` 避免不必要的重渲染
  - 大数据量时建议分页，首期不支持虚拟滚动
  - 筛选/排序计算使用 `useMemo` 缓存
- **样式隔离方案：**
  - CSS Modules 隔离组件样式
  - 所有颜色/字号使用 Design Token
  - 支持通过 className / style 覆盖样式

---

## 7. 测试策略与覆盖率矩阵（Testing Strategy）

### 7.1 测试分层

| 测试类型 | 覆盖目标 | 工具 | 通过标准 |
|----------|----------|------|----------|
| 单元测试 | 纯逻辑函数（排序、筛选、分页计算） | Vitest | 覆盖率 ≥ 90% |
| 组件测试 | 渲染、Props 变化、交互事件 | Testing Library | 所有 Props 组合有快照 |
| 视觉测试 | UI 回归（可选） | Chromatic / Loki | 无意外样式变更 |

### 7.2 功能覆盖率矩阵（Coverage Matrix）

| 功能点 | 测试用例 | 场景覆盖 | 状态 |
|--------|----------|----------|------|
| 基础渲染 | 空数据、有数据、大数据量 | 3/3 | ⬜ 待实现 |
| 列配置 | 普通列、自定义 render、隐藏列、嵌套 dataIndex | 4/4 | ⬜ 待实现 |
| 排序 | 单列升序、单列降序、多列排序、取消排序、后端排序 | 5/5 | ⬜ 待实现 |
| 分页 | 页码切换、每页条数、边界页码、外部分页 | 4/4 | ⬜ 待实现 |
| 行选择 | 单选、全选、反选、受控模式、禁用行 | 5/5 | ⬜ 待实现 |
| 筛选 | 单列筛选、多列筛选、前端筛选、后端筛选、筛选清空 | 5/5 | ⬜ 待实现 |
| 扩展点 | header slot、empty slot、自定义行、展开行 | 4/4 | ⬜ 待实现 |
| 空状态 | 无数据、加载中、加载失败 | 3/3 | ⬜ 待实现 |
| 固定列 | 左固定、右固定 | 2/2 | ⬜ 待实现 |
| 响应式 | 窗口缩放、横向滚动 | 2/2 | ⬜ 待实现 |

### 7.3 复杂功能场景拆解（Complex Scenario Breakdown）

**示例：排序 + 分页 + 筛选组合交互**

| 场景编号 | 前置操作 | 用户操作 | 预期结果 | 测试类型 |
|----------|----------|----------|----------|----------|
| SC-01 | 无 | 点击排序 | 数据按该列排序，分页回到第 1 页 | 组件测试 |
| SC-02 | 已排序 | 切换分页 | 当前排序条件保持，展示对应页数据 | 组件测试 |
| SC-03 | 已筛选 | 点击排序 | 在筛选结果内排序，分页回到第 1 页 | 组件测试 |
| SC-04 | 已排序+已筛选+第 3 页 | 清空筛选 | 排序保持，分页回到第 1 页，数据更新 | 组件测试 |
| SC-05 | 已选择 2 行 | 切换分页 | 选择状态保持，跨页选择累加 | 组件测试 |
| SC-06 | 全选当前页 | 切换分页 | 新页面数据未选中，全选 checkbox 变为半选 | 组件测试 |
| SC-07 | 大数据量 | 快速切换排序 | 无卡顿，Loading 状态正确 | 组件测试 |
| SC-08 | 后端筛选模式 | 选择筛选条件 | onChange 回调携带筛选参数，不修改本地数据 | 组件测试 |

---

## 8. 任务拆分与并行计划（Task Breakdown）

### 8.1 拆分原则

- **契约先行**：Props 接口和类型定义必须先冻结，所有 Agent 基于此开发
- **渲染与逻辑分离**：一个 Agent 负责 UI 渲染，一个负责交互逻辑/Hook，一个负责文档和测试
- **扩展点预留**：核心渲染完成后，扩展能力（排序、筛选、分页）可并行开发

### 8.2 任务卡片（Task Cards）

#### 模块 A：契约与基础渲染（Agent-1 负责）

| 任务 ID | 任务名称 | 类型 | 输入 | 输出 | 依赖 | 验收点 |
|---------|----------|------|------|------|------|--------|
| T-A1 | Props 类型与接口定义 | types | Spec 第 4 章接口设计 | `types.ts` 冻结版本 | 无 | 类型覆盖所有 Props、Events、Slots、Config |
| T-A2 | 核心渲染逻辑 | core | 类型定义 + 设计稿 | `SharedTable.tsx` 基础渲染（无交互） | T-A1 | 传入 dataSource + columns 正确渲染行列，支持嵌套 dataIndex |
| T-A3 | 空状态与加载态 | core | 设计稿 + 现有 EmptyState/Loading | `EmptyWrapper.tsx` / `LoadingWrapper.tsx` | T-A2 | 空数据、加载中、错误态 UI 正确 |
| T-A4 | 固定列支持 | core | 设计稿 | 左/右固定列渲染 | T-A2 | 固定列位置正确，横向滚动时固定 |

> **模块 A 交付物：** 类型定义 + 基础渲染组件（可独立运行）  
> **并行条件：** T-A1 完成后，模块 B 和 C 可同时启动

---

#### 模块 B：交互与扩展能力（Agent-2 负责）

| 任务 ID | 任务名称 | 类型 | 输入 | 输出 | 依赖 | 验收点 |
|---------|----------|------|------|------|------|--------|
| T-B1 | 排序功能 | feature | 模块 A 核心渲染 + 现有 sortBy | `useSort.ts` + 表头排序 UI | T-A2 | 支持单列/多列排序，回调 onChange，前端/后端模式 |
| T-B2 | 分页功能 | feature | 模块 A 核心渲染 + 现有 Pagination | `usePagination.ts` + 分页 UI | T-A2 | 内部分页/外部分页模式，页码切换、每页条数调整 |
| T-B3 | 行选择与批量操作 | feature | 模块 A 核心渲染 + 现有 Checkbox | `useRowSelection.ts` + 选择列 UI | T-A2 | 单选/多选/全选/反选，受控/非受控，跨页选择 |
| T-B4 | 筛选功能 | feature | 模块 A 核心渲染 | `useFilter.ts` + 表头筛选 UI | T-A2 | 文本/下拉/日期筛选，前端/后端模式，多条件组合 |
| T-B5 | 扩展点实现 | feature | 模块 A 核心渲染 | header slot、empty slot、expandRow、rowClassName | T-A2 | 所有扩展点可正确渲染传入内容 |

> **模块 B 交付物：** 所有交互功能（排序、分页、选择、筛选、扩展点）  
> **并行条件：** 依赖模块 A 的 T-A2 完成后启动，与模块 C 并行

---

#### 模块 C：文档、测试与工程化（Agent-3 负责）

| 任务 ID | 任务名称 | 类型 | 输入 | 输出 | 依赖 | 验收点 |
|---------|----------|------|------|------|------|--------|
| T-C1 | 组件单元测试 | test | 模块 A + B 的全部功能 | `SharedTable.test.tsx`（覆盖率 ≥ 85%） | T-A2, T-B1~B5 | 所有 Props 组合有渲染快照，交互有事件测试，SC-01~08 全覆盖 |
| T-C2 | 使用文档 + 场景示例 | docs | 所有使用示例 | `README.md` + 3 个场景示例代码 | T-A1~A4, T-B1~B5 | 覆盖基础/高级/筛选/扩展点用法，含可直接运行的代码片段 |
| T-C3 | 样式主题与变量 | style | 设计规范 + Design Token | `style.module.css`（全部使用 Token） | T-A2 | 支持主题切换，样式不侵入业务，响应式适配 |
| T-C4 | 打包与发布 | infra | 全部源码 | `index.ts` 统一导出 + build 验证 | T-C1 | 类型文件完整，Tree-shaking 友好 |

> **模块 C 交付物：** 测试 + 文档 + 主题 + 工程化  
> **并行条件：** T-C1 需等模块 B 主要功能完成；T-C2/T-C3 可与模块 B 部分并行

### 8.3 并行时序图

```
Day 1:   [Agent-1] T-A1 契约定义 ──→ 冻结 Props 接口
         │
Day 2-3: [Agent-1] T-A2 核心渲染 + T-A3 空加载态 + T-A4 固定列
         │
         ▼
Day 3-5: [Agent-2] T-B1~B5 交互扩展（排序/分页/选择/筛选/扩展点） ──┐
         [Agent-3] T-C3 样式主题 + T-C2 文档编写（并行）            │
         │                                                          │
Day 5-6: [Agent-3] T-C1 单元测试（等模块 B 完成）                  │
         [Agent-3] T-C4 打包发布                                   │
         [All] 集成验收                                             │
```

### 8.4 契约冻结点

| 检查点 | 内容 | 责任方 |
|--------|------|--------|
| CK-1 | Props / API 签名冻结（SharedTableProps / Column / PaginationConfig / RowSelectionConfig / SortConfig / FilterConfig） | Agent-1（模块 A） |
| CK-2 | 扩展点（header / empty / rowClassName / expandRow / actionColumn）签名确认 | Agent-1 + Agent-2 |
| CK-3 | 主题变量命名规范（表格专用 Token 如 `--table-header-bg`） | Agent-3（模块 C） |
| CK-4 | 回调函数签名（onChange / onRowClick / onSelect 等参数结构） | Agent-2（模块 B） |
| CK-5 | onChange 回调参数结构统一（pagination + sort + filters + selectedRows） | Agent-2（模块 B） |

---

## 9. 验收注意点与重点场景（Acceptance Checklist）

### 9.1 必验场景（Must Verify）

| 优先级 | 场景 | 验证方式 | 通过标准 |
|--------|------|----------|----------|
| 🔴 P0 | 组件在场景 A（交易业务订单列表）零改动接入 | 实际接入交易业务 | 传入配置即可渲染，无报错，功能正常 |
| 🔴 P0 | 组件在场景 B（运营后台用户管理）通过配置满足需求 | 实际接入运营后台 | 不 fork 代码，仅通过 Props 配置实现行选择 + 筛选 |
| 🔴 P0 | 所有交互功能正常 | 手动操作 | 排序、分页、选择、筛选均可触发，反馈正确 |
| 🟡 P1 | 大数据量性能 | 1000 条数据测试 | 无卡顿，渲染时间 < 1s |
| 🟡 P1 | 主题切换 | 切换 Design Token | 组件样式跟随主题变化（表头背景、行hover、选中态） |
| 🟡 P1 | 固定列功能 | 横向滚动测试 | 左/右固定列在滚动时保持固定 |
| 🟢 P2 | 文档示例可运行 | 复制文档代码到项目 | 直接可用，无额外配置 |
| 🟢 P2 | 响应式适配 | 缩小窗口 | 横向滚动出现，固定列保持 |

### 9.2 易遗漏场景（Easy to Miss）

| 风险点 | 为什么容易漏 | 验收方法 |
|--------|--------------|----------|
| 受控/非受控模式 | 只测了一种模式 | 验证 pagination/sort/filters/rowSelection 的 value + onChange 和 defaultValue 两种模式 |
| 动态列配置 | 运行时修改 columns | 验证增删改列后表格正确更新，不残留旧列数据 |
| 嵌套数据渲染 | 复杂对象路径如 `user.address.city` | 验证 dataIndex 支持字符串路径和数组路径 |
| 键盘无障碍 | 只测了鼠标操作 | Tab 切换焦点，Enter 触发排序/选择，Space 选择行 |
| 响应式适配 | 只在桌面端测试 | 缩小窗口，验证横向滚动或列隐藏 |
| 内存泄漏 | 大数据量频繁更新 | 长时间运行后检查内存占用，验证事件监听已清理 |
| 跨页选择状态 | 选择多页数据后切换分页 | 验证选择状态保持，全选 checkbox 状态正确（全选/半选/未选） |
| 筛选后分页重置 | 筛选后当前页可能超出范围 | 验证筛选后自动回到第 1 页 |
| 空数据分页 | 数据为空时分页组件展示 | 验证分页隐藏或展示 0 条 |

### 9.3 回归检查（Regression Check）

| 影响面 | 检查项 | 验证方式 |
|--------|--------|----------|
| 现有表格组件 | 升级后现有页面表格是否正常 | 随机抽查 2-3 个现有页面 |
| 主题系统 | 新组件样式是否破坏全局主题 | 检查 Design Token 覆盖范围，验证无样式污染 |
| 包体积 | 新增组件是否显著增加产物体积 | 对比构建产物体积，目标增量 < 20KB |
| 现有分页组件 | 与现有 Pagination 集成是否正常 | 验证页码切换、每页条数功能 |
| 现有 Checkbox | 与现有 Checkbox 集成是否正常 | 验证行选择功能 |

---

## 10. 版本与兼容

- 初始版本：v1.0.0
- 后续迭代预留的扩展点：
  - 虚拟滚动（大数据量优化）
  - 表格编辑单元格
  - 树形数据支持
  - 列拖拽排序
  - 列显示/隐藏配置
