# Busy-UI 组件库能力总览

> 数据源：https://busy-fe.hnlshm.com/busy-ui/  
> 版本：BUSY-UI v7.0.0-next.50  
> 组件总数：70 个

## 分类概览

- **业务组件**：17 个
- **已有未纳入目录**：10 个
- **基础组件 / 全局**：5 个
- **基础组件 / 导航**：5 个
- **基础组件 / 反馈提醒**：7 个
- **基础组件 / 信息录入**：16 个
- **基础组件 / 信息展示**：10 个

## 基础组件 / 全局

### ThemeColor 主题色

主题色 用于动态切换 busy-ui 的主题颜色，并查看当前主题下的颜色场景配置。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| defaultThemeColor | 默认主题色 | string | - | '#0073FF' |
| persistent | 是否持久化到 localStorage | boolean | true / false | true |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 主题色变化后触发 | 当前主题色对应的主功能色 token 映射 |

### Icon 图标

图标 通用图标组件，根据传入属性自动选择渲染方式：内置状态图片（type）、自定义图片（src）、字体图标（name，可通过 group 切换通用/菜单图标库）、SVG 地址（path）或默认插槽 SVG。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| type | 内置状态图标类型，与 src 同时传入时 src 优先 | 'success' \| 'warning' \| 'info' \| 'error' | success / warning / info / error | — |
| src | 自定义图片地址，优先于 type 渲染 | string | — | '' |
| name | 字体图标类名，如 icon-tubiao_chazhao_V2；传入后进入 iconfont 模式，基础字体类由 group 决定 | string | — | '' |
| group | 字体图标分组，仅在传入 name 时生效：common 挂载 iconfont，menu 挂载 menu-iconfont | 'common' \| 'menu' | common / menu | common |
| path | SVG 资源地址 | string | — | '' |
| size | 图标尺寸，传数字时单位为 px，也可传 CSS 字符串如 '2em' | number \| string | — | '' |
| shape | 容器形状，square 默认 2px 圆角，circle 为圆形 | 'square' \| 'circle' | square / circle | — |
| alt | 图片 alt 文本，src / path 时生效 | string | — | '' |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| click | 点击图标时触发 | (event: MouseEvent) |

### Text  `[已验收]`

文字 设计语言与规范 以下为设计稿中的字体、字阶/行高与字重说明。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| tag | 根元素标签 | string | span |  |
| type | 展示类型 | 'text' \| 'number' \| 'percent' \| 'currency' \| 'fraction' \| 'title' \| 'tooltip' | text |  |
| text | text / title / tooltip 的默认文案（可与插槽并用） | string | ‘’ |  |
| size | 字阶（行高 = size + 8）；title 时无效（固定 16 / 行高 24） | 12 \| 14 \| … \| 40 | 14 |  |
| weight | 字重；auto 时 ≤16 为 400，否则 500；title 时无效（固定 500） | 400 \| 500 \| 'auto' | auto |  |
| value | number / percent / currency 的数值 | number \| string | — |  |
| decimals | 小数位（含万/亿换算） | number | 2 |  |
| abbreviate | 是否按万/亿展示 | boolean | true |  |
| showFullTitle | 缩写时 title 是否展示完整数值 | boolean | true |  |
| showPlus | 正数 +；货币正数且 true 时不显示货币符 | boolean | false |  |
| currencySymbol | 货币符号 | string | ￥ |  |
| numerator / denominator | 分数分子、分母 | string \| number | — |  |
| color | 文字颜色 | string | — |  |
| fixFontSize | %、货币符号、万/亿 字号 | number \| string | — |  |
| useDinAmount | 为 true 时数字主体使用 D-DIN（components/Text/resource/*.otf） | boolean | false |  |
| ... | 共 24 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| copy | 复制完成（仅文案复制能力触发） | { value: string; success: boolean } |

**插槽 Slot**

| name | 说明 |
|------|------|
| 默认 | text / title / tooltip 时自定义内容 |
| tooltip | 仅 tooltip：气泡内容；不传则与默认插槽相同 |

### Button 按钮 `[已验收]`

按钮 BusyButton 在 Element Plus Button 的基础上补齐了 busy 设计规范约束，包括按钮尺寸、默认态视觉收敛，以及 虚线按钮、幽灵按钮 两个 busy 扩展样式。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| variant | busy 扩展样式 | string | dashed / ghost | - |
| type | 按钮类型 | string | default / primary / success / warning / info / danger / text | '' |
| size | 尺寸 | string | large / default / small | default |
| plain | 是否为描边按钮 | boolean | - | false |
| link | 是否为文字按钮 | boolean | - | false |
| circle | 是否为圆形按钮 | boolean | - | false |
| loading | 是否显示加载状态 | boolean | - | false |
| disabled | 是否禁用 | boolean | - | false |
| nativeType | 原生 button 类型 | string | button / submit / reset | button |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| click | 点击按钮时触发 | (event: MouseEvent) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 按钮内容 |
| icon | 前置图标 |
| suffix-icon | 后缀图标，常用于切换、展开、更多 |
| loading | 自定义 loading 图标 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| - | 当前版本未额外扩展实例方法，透传 class、style、aria-* 等属性到内部 ElButton | - |

### Layout Layout 布局

Layout 布局 可配置行列的网格布局组件，基于 CSS Grid 实现。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| rows | 行配置数组 | LayoutTrackConfig[] | [{ span: 1 }] |  |
| columns | 列配置数组 | LayoutTrackConfig[] | [{ span: 1 }] |  |
| width | 容器宽度：'fill' 铺满（最小 1000px）/ 数字 / 字符串 | 'fill' \| string \| number | 'fill' |  |
| height | 容器高度：'fill' 铺满 / 数字 / 字符串 | 'fill' \| string \| number | 'fill' |  |
| gap | 行列统一间距 | string \| number | 12 |  |
| rowGap | 行间距（覆盖 gap） | string \| number | — |  |
| columnGap | 列间距（覆盖 gap） | string \| number | — |  |
| size | 固定尺寸（数字自动加 px，字符串直接透传） | string \| number | 最高 |  |
| flex | 弹性尺寸（如 'auto'、'1fr'、'minmax(0, 1fr)'） | string | 中 |  |
| span | 占比权重（如 span: 2 → 2fr） | number | 最低（默认 1） |  |
| default | 覆盖整个布局内容（使用后行列插槽失效） | — |  |  |
| cell-{rowIndex}-{colIndex} | 指定网格单元的内容 | — |  |  |
| cell | 通用单元格插槽，通过 slotProps 区分行列 | { rowIndex, colIndex, key } |  |  |

## 基础组件 / 导航

### FrameNavSider FrameNavSider 侧边导航栏 `[已废弃]`

FrameNavSider 侧边导航栏 维护提醒：FrameNavSider 组件已停止维护，后续侧栏导航请使用 PortalNav（菜单导航）的 mode="sider"。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| title | 顶部标题 | string | '' |  |
| menus | 菜单数据 | NavMenuGroup[] | [] |  |
| activeId | 当前激活菜单 ID（支持 v-model） | string \| number | '' |  |
| width | 侧边栏宽度 | string | '220px' |  |
| searchPlaceholder | 搜索框占位文本 | string | '菜单搜索' |  |
| defaultExpandAll | 默认展开所有分组 | boolean | true |  |
| id | 唯一标识 | string \| number |  |  |
| title | 分组标题 | string |  |  |
| icon | 图标（Element Plus icon 名称） | string |  |  |
| children | 子菜单项 | NavMenuItem[] |  |  |
| id | 唯一标识 | string \| number |  |  |
| title | 菜单名称 | string |  |  |
| path | 路由路径 | string |  |  |
| children | 子菜单（多级） | NavMenuItem[] |  |  |
| group-icon | 自定义分组图标 | { group: NavMenuGroup } |  |  |
| ... | 共 16 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:activeId | 激活菜单变化 | (id: string \| number) |
| menu-click | 菜单项点击 | (item: NavMenuItem, parents: NavMenuItem[]) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| expandAll | 展开所有分组 |  |
| collapseAll | 折叠所有分组 |  |

### FrameNavHeader FrameNavHeader 顶部导航栏 `[已废弃]`

FrameNavHeader 顶部导航栏 基于 Element Plus 的顶部导航组件，支持 Logo、导航菜单、搜索、用户信息等功能。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| logo | Logo 配置 | LogoConfig | {} |  |
| menus | 导航菜单数据 | NavHeaderItem[] | [] |  |
| activeId | 当前激活菜单 ID（支持 v-model） | string \| number | '' |  |
| maxVisibleMenus | 主导航栏最大显示菜单数量 | number | 8 |  |
| searchPlaceholder | 搜索框占位文本 | string | '搜索' |  |
| showSearch | 是否显示搜索功能 | boolean | true |  |
| user | 用户信息配置 | UserConfig | {} |  |
| leftDropdownMenus | 左侧下拉菜单配置 | DropdownMenuItem[] | [] |  |
| height | 导航栏高度 | string | '60px' |  |
| src | Logo 图片地址 | string |  |  |
| text | Logo 文本 | string |  |  |
| link | 点击跳转链接 | string |  |  |
| id | 唯一标识 | string \| number |  |  |
| title | 菜单名称 | string |  |  |
| path | 路由路径 | string |  |  |
| ... | 共 30 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:activeId | 激活菜单变化 | (id: string \| number) |
| menu-click | 菜单项点击 | (item: NavHeaderItem) |
| logo-click | Logo 点击 | () |
| search | 搜索 | (keyword: string) |
| user-menu-click | 用户下拉菜单点击 | (item: DropdownMenuItem) |
| left-dropdown-click | 左侧下拉菜单点击 | (item: DropdownMenuItem) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| showSearch | 显示搜索框 |  |
| hideSearch | 隐藏搜索框 |  |

### PortalNav PortalNav 菜单导航

PortalNav 菜单导航 基于 Element Plus 的 Portal 菜单导航组件，通过 mode 区分顶栏与应用内侧栏两种形态。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| mode | 展示模式 | 'header' \| 'sider' | 'header' |  |
| logo | 默认 Logo 配置（仅 mode="header" 且 #left 未使用时生效） | PortalNavLogoConfig | { src: 默认 logo } |  |
| menus | 导航菜单数据（顶栏 / 侧栏通用，按 mode 解析） | PortalNavMenuItem[] | [] |  |
| activeId | 当前激活菜单 ID（顶栏 / 侧栏通用，支持 v-model） | string \| number | '' |  |
| height | 顶栏高度 | string | '60px' |  |
| menuUnavailable | 菜单不可用判断（顶栏 / 侧栏通用） | (menu) => boolean | 内置 disabled / isPermission / available 判断 |  |
| unavailableTooltip | 不可用菜单提示文案（顶栏 / 侧栏通用） | string | '无权限' |  |
| siderOpenIds | 侧栏已展开目录 id 列表 | string[] | [] |  |
| src | Logo 图片地址 | string |  |  |
| text | Logo 文本 | string |  |  |
| link | 点击跳转链接 | string |  |  |
| id | 唯一标识 | string \| number |  |  |
| title | 菜单名称 | string |  |  |
| path | 路由路径（顶栏） | string |  |  |
| icon | 图标（iconfont 或图片 URL） | string |  |  |
| ... | 共 30 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:activeId | 激活菜单变化（顶栏 / 侧栏通用） | (id: string \| number) |
| menu-click | 顶栏菜单项点击 | (item: PortalNavMenuItem) |
| logo-click | 默认 Logo 点击（仅 #left 未使用时触发） | () |
| sider-select | 侧栏菜单选中 | (value: string) |
| sider-open | 侧栏目录展开 | (id: string) |
| sider-close | 侧栏目录收起 | (id: string) |
| sider-warmup | 侧栏菜单预热（鼠标悬停叶子节点） | () |

### Steps 步骤条 `[已验收]`

步骤条 步骤条可用于明示任务流程和当前完成程度，引导用户按照步骤完成任务。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| active | 当前激活步骤索引（从 0 开始） | number | — | 0 |
| direction | 步骤条方向 | string | horizontal / vertical | horizontal |
| steps-type | 步骤条类型 | string | default / dot / panel | default |
| size | 尺寸 | string | medium / small | medium |
| title-placement | 标题放置方向 | string | horizontal / vertical | horizontal |
| process-status | 当前步骤状态 | string | wait / process / finish / error / success | process |
| finish-status | 已完成步骤状态 | string | wait / process / finish / error / success | finish |
| title | 步骤标题 | string | — | — |
| sub-title | 步骤副标题 | string | — | — |
| description / content | 步骤描述 | string | — | — |
| icon | 自定义图标（传入则图标区域显示 slot#icon） | string | — | — |
| status | 强制指定该步骤状态，优先于父级计算 | string | wait / process / finish / error / success | — |
| disabled | 禁用该步骤的点击 | boolean | — | false |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 当绑定值变化时触发的事件 | 更新后的值 |

**插槽 Slot**

| name | 说明 |
|------|------|
| icon | 自定义图标内容 |
| title | 自定义标题内容 |
| subTitle | 自定义副标题内容 |
| description | 自定义描述内容 |
| extra | 描述区域额外内容 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| change | 点击步骤时触发（步骤不为 disabled） | (current: number) => void |

### BusyTabs 标签页 Tabs

标签页 Tabs 基于 Element Plus el-tabs 二次封装，对齐设计稿四种视觉变体：基础、卡片、按钮、胶囊。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值，选中标签的 name | string / number | - | - |
| variant | 视觉变体 | string | basic / card / button / capsule | basic |
| size | 尺寸（button / capsule 生效） | string | default / small | default |
| tabs | 配置式 tab 列表 | BusyTabItem[] | - | - |
| header-only | 仅渲染头部，隐藏内容区 | boolean | - | 配置式且无 default slot 时为 true |
| card-gapless | card 变体无边距模式，item 紧贴且相邻仅一条分隔线 | boolean | - | false |
| card-borderless | card 无边距布局上去掉所有 border，选中项白底且顶部圆角 8px（自动启用无边距） | boolean | - | false |
| level | 已废弃，请用 variant。1=basic，2=card，3=button | number / string | 1 / 2 / 3 | - |
| label | 标签标题 | string | - | - |
| name | 标签唯一标识 | string / number | - | - |
| disabled | 是否禁用 | boolean | - | false |
| closable | 是否可关闭 | boolean | - | - |
| lazy | 是否懒渲染 | boolean | - | false |
| icon | 标签左侧图标组件 | Component | - | - |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| tab-click | 标签被点击时触发 | (pane: TabsPaneContext, ev: Event) |
| tab-change | 标签切换时触发 | (name: string / number) |
| edit | 增删标签时触发（需 editable） | (paneName, action: ‘remove’ \| ‘add’) |
| tab-remove | 关闭标签时触发 | (name) |
| tab-add | 新增标签时触发 | - |

## 基础组件 / 反馈提醒

### Dialog Dialog 通用对话框 `[已验收]`

Dialog 通用对话框 统一封装 Element Plus Dialog，在保留原生声明式调用的基础上，补齐 busy 风格、消息确认形态与命令式调用能力。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue / v-model | 是否显示对话框 | boolean | true / false | false |
| title | 对话框标题 | string | - | - |
| msg | 消息确认文案，与默认插槽互斥，传入后优先显示 msg | string | - | - |
| type | 标题图标类型，不传则不显示图标 | string | info / success / warning / error | - |
| size | 弹窗尺寸，对应宽度 480 / 680 / 880 / 1080px | string | small / middle / large / xlarge | middle |
| disabledConfirm | 是否禁用确认按钮 | boolean | true / false | false |
| showFooter | 是否显示底部区域 | boolean | true / false | true |
| okText | 确认按钮文案 | string | - | 确定 |
| cancelText | 取消按钮文案 | string | - | 取消 |
| cancelBtn | 取消按钮配置 | DialogBtnConfig | - | { show: true } |
| submitBtn | 确认按钮配置 | DialogBtnConfig | - | { show: true } |
| showTrigger | 是否显示组件内部触发按钮 | boolean | true / false | false |
| triggerBtnTitle | 组件内部触发按钮文案 | string | - | 打开 |
| triggerBtnProps | 组件内部触发按钮的 ElButton props | Partial<ButtonProps> | - | {} |
| legacyCancelHideDialog | 是否使用旧的取消即关闭逻辑；由父组件控制显隐时建议设为 false | boolean | true / false | true |
| ... | 共 29 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 对话框显示状态变化时触发 | (value: boolean) |
| open | Dialog 打开时触发（Element Plus 对齐） | - |
| opened | Dialog 打开动画结束时触发（Element Plus 对齐） | - |
| close | Dialog 开始关闭时触发（Element Plus 对齐） | - |
| closed | Dialog 关闭动画结束时触发（Element Plus 对齐） | - |
| open-auto-focus | Dialog 打开且内容聚焦时触发（Element Plus 对齐） | - |
| close-auto-focus | Dialog 关闭且内容聚焦时触发（Element Plus 对齐） | - |
| cancel | 点击取消按钮时触发（Busy 扩展） | - |
| confirm | 点击确认按钮时触发（Busy 扩展） | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 对话框主体内容 |
| footer | 自定义底部区域，对齐 Element Plus #footer；未提供时使用 Busy 默认 footer |
| actions | 仅替换默认 footer 内的按钮区（Busy 扩展） |
| trigger | 组件内部触发元素自定义插槽 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| showMessageDialog | 命令式打开消息确认弹窗，返回 Promise（confirm \| cancel \| close） | ShowMessageDialogOptions |

### MessageBox MessageBox 通知提醒框 `[已验收]`

MessageBox 通知提醒框 统一封装通知提醒能力，支持从页面边缘或正中间弹出，自动注入 Busy 风格类名与默认行为。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| title | 通知标题 | string | - | - |
| message | 通知内容，支持字符串、数字、布尔值、VNode 或渲染函数；dangerouslyUseHTMLString: true 时按 HTML 解析 | string \| number \| boolean \| VNode \| (() => unknown) | - | - |
| dangerouslyUseHTMLString | 是否将 message 作为 HTML 片段解析（与 Element Plus 一致） | boolean | true / false | false |
| type | 通知状态类型 | success \| warning \| info \| error | - | - |
| position | 通知位置 | string | top-right / top-left / bottom-right / bottom-left / top-center / center | top-right |
| offset | 非 center 模式下距离视口边缘的偏移量 | number | - | 32 |
| offsetX | center 模式下水平方向偏移量 | number \| string | 像素值 | 0 |
| offsetY | center 模式下垂直方向偏移量 | number \| string | 像素值 | 0 |
| showMask | 是否显示遮罩；未显式配置时，带 actions 的通知默认显示遮罩 | boolean | true / false | false；配置 actions 且未传时为 true |
| duration | 自动关闭时长（单位 ms）；配置 actions 时默认不自动关闭 | number | - | 4500；配置 actions 时为 0 |
| showClose | 是否显示关闭按钮 | boolean | true / false | true |
| width | 通知宽度，支持推荐宽度、自定义像素值或 auto | number \| string | 480 / 680 / 880 / auto | auto；配置 actions 且未传时为 480 |
| actions | 底部操作按钮配置 | BusyMessageBoxAction[] | - | - |
| customClass | 自定义类名，会与 Busy 默认类名合并 | string | - | 自动注入 Busy 样式类名 |
| customStyle | 自定义内联样式 | Record<string, unknown> | - | - |
| ... | 共 20 个属性 | | | |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| BusyMessageBox(options) | 通知提醒，type 可指定图标风格 | 通知配置对象，或基础内容 |
| BusyMessageBox.success(options) | 成功态通知提醒 | 成功态通知配置对象，或基础内容 |
| BusyMessageBox.warning(options) | 警告态通知提醒 | 警告态通知配置对象，或基础内容 |
| BusyMessageBox.info(options) | 信息态通知提醒 | 信息态通知配置对象，或基础内容 |
| BusyMessageBox.error(options) | 错误态通知提醒 | 错误态通知配置对象，或基础内容 |
| BusyMessageBox.closeAll() | 关闭当前页面全部通知提醒 | - |
| await BusyMessageBox.alert(message, title?, options?) | 居中确认提醒，用户点确定后 resolve | Promise 用法与 Element Plus MessageBox.alert 一致 |
| await BusyMessageBox.confirm(message, title?, options?) | 居中二次确认，确定 resolve，取消/关闭 reject | Promise 用法与 Element Plus MessageBox.confirm 一致 |
| await BusyMessageBox.prompt(message, title?, options?) | 模态输入框，确定 resolve { value, action }，取消 reject | 基于 ElMessageBox.prompt，自动注入 Busy 样式，交互与 EP 一致 |
| BusyMessageBox.close() | 关闭当前 ElMessageBox 实例（含 prompt） | - |

### Message Message 轻提示 `[已验收]`

Message 轻提示 统一封装 Element Plus Message，在不破坏原有调用习惯的前提下，提供统一样式与默认行为。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| message | 提示内容，支持字符串、数字、布尔值或渲染函数 | string \| number \| boolean \| (() => unknown) | - | - |
| type | 轻提示状态类型 | success \| warning \| info \| error | - | - |
| placement | 轻提示显示位置 | string | top / bottom | top |
| offset | 距离视口边缘的偏移量 | number | - | 80 |
| duration | 自动关闭时长（单位 ms） | number | - | 4000 |
| customClass | 自定义类名，会与 Busy 默认类名合并 | string | - | 自动注入 Busy 样式类名 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| BusyMessage(options) | 普通轻提示 | 轻提示配置对象，或基础内容 |
| BusyMessage.success(options) | 成功态轻提示 | 成功态配置对象，或基础内容 |
| BusyMessage.warning(options) | 警告态轻提示 | 警告态配置对象，或基础内容 |
| BusyMessage.info(options) | 信息态轻提示 | 信息态配置对象，或基础内容 |
| BusyMessage.error(options) | 错误态轻提示 | 错误态配置对象，或基础内容 |
| BusyMessage.closeAll() | 关闭当前页面全部轻提示 | - |

### GuideBubble 局部气泡引导 `[已验收]`

局部气泡引导 用于在目标元素附近展示局部提示，不会打断当前页面流程。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model / model-value | 是否显示气泡；传入时为受控模式，未传时由组件内部维护显隐 | boolean | - |  |
| content | 提示文案，未传时可改用 content 插槽 | string | '' |  |
| placement | 气泡方向，支持简写和 Element Plus placement | GuideBubblePlacement | 'top' |  |
| show-close | 是否显示关闭按钮 | boolean | false |  |
| auto-close | 自动关闭时长，单位 ms，0 表示不自动关闭 | number | 0 |  |
| offset | Popper 偏移量 | number | 12 |  |
| show-arrow | 是否显示箭头 | boolean | true |  |
| teleported | 是否传送到 body | boolean | true |  |
| persistent | 隐藏后是否销毁 | boolean | true |  |
| disabled | 是否禁用组件 | boolean | false |  |
| max-width | 气泡内容最大宽度 | string \| number | '480px' |  |
| popper-class | 追加到 popper 的类名 | string | '' |  |
| line | 显示的最大行数 | number \| string | 1 |  |
| width | 容器宽度 | number \| string | '' |  |
| line-height | 行高 | number \| string | '24px' |  |
| ... | 共 16 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 显隐变化时触发 | (value: boolean) |
| show | 气泡显示时触发 | - |
| close | 组件内部主动关闭时触发 | (reason: 'close-button' \| 'auto-close') |

### BubbleCard 气泡卡片 `[已验收]`

气泡卡片 用于在目标元素附近展示轻量级卡片式提示内容，适合标题说明、状态提醒、快捷确认和自定义内容承载等场景。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model / model-value | 是否显示气泡卡片；传入时为受控模式，未传时由组件内部维护显隐 | boolean | - |  |
| title | 标题文案，未传时可改用 title 插槽 | string | '' |  |
| description | 描述文案，未传时可改用 description 插槽 | string | '' |  |
| status | 内置图标状态 | 'none' \| 'info' \| 'success' \| 'warning' \| 'danger' | 'none' |  |
| trigger | 触发方式 | 'hover' \| 'click' \| 'focus' \| 'contextmenu' | 'hover' |  |
| placement | 气泡方向，支持简写和 Element Plus placement | BubbleCardPlacement | 'top' |  |
| offset | Popper 偏移量 | number | 4 |  |
| show-arrow | 是否显示箭头 | boolean | true |  |
| teleported | 是否传送到 body | boolean | true |  |
| persistent | 隐藏后是否销毁 | boolean | true |  |
| disabled | 是否禁用组件 | boolean | false |  |
| min-width | 气泡卡片最小宽度；组件会保证最小不低于 240 | string \| number | 240 |  |
| max-width | 气泡卡片最大宽度；存在 actions 插槽时默认按交互态取 320 | string \| number | - |  |
| body-max-height | 内容区最大高度，超出时纵向滚动；组件会保证最大不超过 320 | string \| number | 320 |  |
| popper-class | 追加到 popper 的类名 | string | '' |  |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 显隐变化时触发 | (value: boolean) |
| show | 气泡卡片显示时触发 | - |
| hide | 气泡卡片隐藏时触发 | - |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| show | 显示气泡卡片 |  |
| hide | 隐藏气泡卡片 |  |
| toggle | 切换气泡卡片显隐 |  |

### AnnouncementBar 公告条 `[已验收]`

公告条 用于在页面内持续展示公告、提示和风险提醒，不打断当前操作流程。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| type | 公告条语义类型 | 'warning' \| 'danger' \| 'info' | 'warning' |  |
| content | 公告文案，未传时可改用默认插槽 | string | '' |  |
| show-icon | 是否显示左侧图标 | boolean | true |  |
| icon | 自定义左侧图标组件，与 #icon 插槽二选一，插槽优先级更高 | Component | — |  |
| closable | 是否显示关闭按钮 | boolean | false |  |
| close-aria-label | 关闭按钮的无障碍文案 | string | '关闭公告' |  |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| close | 点击关闭按钮时触发 | (event: MouseEvent) |

### Drawer 通用抽屉

通用抽屉 符合 UI 规范的通用抽屉组件，API 与 BusyDialog 对齐，可在两者之间低成本切换。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 是否显示 drawer | boolean | - | false |
| title | 标题 | string | - | ‘标题’ |
| size | 宽度档位，与 BusyDialog 一致（small=480px / middle=680px / large=880px / xlarge=1080px），不传则使用 el-drawer 默认值（30%） | string | small / middle / large / xlarge | - |
| showFooter | 是否显示底部按钮区域 | boolean | - | true |
| disabledConfirm | 是否禁用确认按钮 | boolean | - | - |
| cancelText | 取消按钮文案 | string | - | ‘取消’ |
| okText | 确定按钮文案 | string | - | ‘确定’ |
| cancelBtn | 取消按钮配置，show 控制显示，handle 自定义处理函数（设置后不再自动关闭） | { show: boolean; handle?: () => void } | - | { show: true } |
| submitBtn | 确认按钮配置，show 控制显示，handle 自定义处理函数 | { show: boolean; handle?: () => void } | - | { show: true } |
| legacyCancelHideDialog | 点击取消是否自动关闭抽屉（无 cancelBtn.handle 时生效） | boolean | - | true |
| showTrigger | 是否显示组件内部触发元素 | boolean | - | false |
| triggerBtnTitle | 组件内部触发按钮的文案 | string | - | ‘打开’ |
| triggerBtnProps | 组件内部触发按钮的 props | object | - | - |
| showClose | 是否显示右上角关闭图标 | boolean | - | true |
| showBack | 是否显示标题左侧返回箭头（多层级嵌套场景子级抽屉使用） | boolean | - | false |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 点击确认按钮时触发 | - |
| cancel | 点击取消按钮时触发 | - |
| close | 点击关闭图标时触发 | - |
| back | 点击返回箭头时触发 | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 抽屉主体内容 |
| header | 自定义头部（完全替换默认 header，scope: { close, titleId, titleClass }） |
| footer | 自定义底部（完全替换默认 footer，含按钮区） |
| actions | 自定义底部按钮区（仅替换按钮，底部容器样式保留） |
| trigger | 组件内部触发元素自定义插槽（需 showTrigger: true） |

## 基础组件 / 信息录入

### Radio 单选框

单选框 在一组备选项中进行单选。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值 | string \| number \| boolean | — | — |
| value | 单选框对应的值 | string \| number \| boolean | — | — |
| label | 标签文本 | string | — | — |
| disabled | 是否禁用 | boolean | — | false |
| size | 尺寸 | string | small / default / large | — |
| name | 原生 name 属性 | string | — | — |
| v-model | 绑定值 | string \| number \| boolean | — | — |
| disabled | 是否禁用 | boolean | — | false |
| size | 尺寸 | string | small / default / large | — |
| name | 原生 name 属性 | string | — | — |
| options | 选项数组 | RadioOption[] | — | — |
| fill | 按钮选中填充色 | string | — | '' |
| textColor | 按钮选中文字色 | string | — | '' |
| value | 按钮对应的值 | string \| number \| boolean | — | — |
| label | 标签文本 | string | — | — |
| ... | 共 17 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 绑定值变化时触发 | (value: string \| number \| boolean) |

### Checkbox 多选框

多选框 在一组备选项中进行多选。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue / v-model | 绑定值 | string \| number \| boolean | - | - |
| value | 选中状态的值（用于 checkbox-group 中） | string \| number \| boolean | - | - |
| label | Checkbox 对应的 label（兼容用途） | string \| number \| boolean | - | - |
| trueValue | 选中时的值 | string \| number \| boolean | - | - |
| falseValue | 没有选中时的值 | string \| number \| boolean | - | - |
| disabled | 是否禁用 | boolean | - | false |
| border | 是否显示边框 | boolean | - | false |
| size | Checkbox 的尺寸 | CheckboxSize | large / default / small | - |
| name | 原生 name 属性 | string | - | - |
| checked | 当前是否勾选（非受控模式） | boolean | - | false |
| indeterminate | 设置不确定状态，仅负责样式控制 | boolean | - | false |
| validateEvent | 是否触发表单的校验 | boolean | - | true |
| tabindex | input 的 tabindex | string \| number | - | - |
| id | input 的 id | string | - | - |
| controls | 与 aria-controls 关联，indeterminate 为 true 时生效 | string | - | - |
| ... | 共 35 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 绑定值变化时触发 | (value: CheckboxValueType) |
| change | 当绑定值变化时触发 | (value: CheckboxValueType) |
| update:modelValue | 绑定值变化时触发 | (value: CheckboxValueType[]) |
| change | 当绑定值变化时触发 | (value: CheckboxValueType[]) |
| change | 当绑定值变化时触发 | (value: CheckboxValueType) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义 checkbox 标签内容 |
| default | 自定义内容，一般放置 BusyCheckbox 或 BusyCheckboxButton 组件 |
| default | 自定义 checkbox-button 标签内容 |

### BusyInput 输入框

输入框 基于 el-input 的统一封装，支持按 type/validateType 启用内置校验规则，也支持自定义规则与 context 扩展规则。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值 | string \| number | ‘’ |  |
| type | 输入框类型 | text \| password \| textarea \| email \| url \| tel \| number | text |  |
| size | 尺寸 | small \| default \| large | default |  |
| validateType | 校验类型，auto 会根据 type 自动映射 | auto \| none \| mobile \| email \| url \| idCard \| integer \| float \| username \| passwordStrong | auto |  |
| rules | 自定义校验规则 | BusyInputRule[] | [] |  |
| ruleMode | 规则合并模式，append=内置+context+自定义，replace=context+自定义 | append \| replace | append |  |
| validateTrigger | 自动校验触发时机 | blur \| change \| manual | blur |  |
| contextKey | 从 context 读取扩展规则时的 key | string | ‘’ |  |
| showErrorMessage | 是否展示错误文案 | boolean | true |  |
| trimOnValidate | 校验前是否 trim 值 | boolean | true |  |
| validateOnMount | 挂载后是否立即校验 | boolean | false |  |
| copyable | 是否展示复制按钮（非 textarea） | boolean | false |  |
| copyText | 自定义复制内容，未传时复制当前输入值 | string | ‘’ |  |
| copySuccessText | 复制成功提示文案 | string | 复制成功 |  |
| copyErrorText | 复制失败提示文案 | string | 复制失败 |  |
| ... | 共 19 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | v-model 更新 | string \| number |
| input | 输入中触发 | string |
| change | 值变更触发 | string |
| blur | 失焦触发 | FocusEvent |
| copy | 点击复制按钮后触发 | { value: string; success: boolean } |
| validate | 校验完成触发 | { valid: boolean; message: string; trigger: ‘blur’ \| ‘change’ \| ‘manual’; ruleKey?: string } |

**插槽 Slot**

| name | 说明 |
|------|------|
| prepend | 输入框前置内容 |
| prefix | 输入框内前缀内容 |
| suffix | 输入框内后缀内容 |
| append | 输入框后置内容 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| validate | 手动触发校验 | trigger?: ‘blur’ \| ‘change’ \| ‘manual’ |
| copy | 手动触发复制 | - |
| clearValidate | 清空错误状态 | - |
| getResolvedRules | 获取当前生效规则列表 | - |

### Tree 树形控件

树形控件 符合ui规范的通用树形控件 基础用法 单选 多选 一级 1 二级 1-1 三级 1-1-1 二级 1-2 三级 1-2-1 一级 2 二级 2-1 三级 2-1-1 展开代码 复制代码 高级搜索 高级搜索方式为默认前端filter-node-method匹配搜索 一级 1 一级 2 高级搜索方式为前端filter-node-method，自定义filterFunc 一级 1 一级 2 高级搜索方式为接口搜索，自定义searchMethod 一级 1 一级 2 展开代码 复制代码 自定义节点显示 一级 1#1 二级 1-1#2 三级 1-1-1#3 一级 2#4 二级 2-1#5 三级

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| data | 树结构数据 | array | — | [] |
| multiple | 是否为多选 | boolean | — | false |
| nodeKey | 节点唯一键字段 | string | — | 'id' |
| treeOptionProps | 字段映射配置，如 { children, label, disabled } | object | — | { children: 'children', label: 'label', disabled: 'disabled' } |
| defaultExpandedKeys | 默认展开的节点 key 列表 | array | — | [] |
| checkedKeys | 选中的节点 key 列表（复选模式） | array | — | [] |
| filterFunc | 自定义前端过滤函数 (query, data) => boolean | function | — | undefined |
| searchable | 是否显示高级搜索框 | boolean | — | false |
| searchMethod | 接口搜索回调 (keyword) => Promise<TreeData>，有此 prop 则走接口搜索 | function | — | undefined |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| node-click | 节点被点击 | (data, node, event) |
| check | 复选框状态变化 | (data, checkedInfo) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义节点内容插槽，参数为 { node, data, key } |
| empty | 当数据为空时自定义的内容插槽 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| setCheckedKeys | 设置复选节点 key | (keys: (string \| number)[]) |
| setCurrentKey | 设置单选节点 key | (key: string \| number \| null) |

### PageableSelect 分页选择器 `[已验收]`

分页选择器 支持虚拟滚动和异步分页加载的选择器组件，基于 el-select-v2 二次封装。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue/v-model | 选中的值 | string / number / array | - | - |
| options | 本地选项数据 | SelectOption[] | - | - |
| loadData | 异步加载函数，返回 Promise<{ data: SelectOption[], total: number }> | Function | - | - |
| initialOptions | 预载选项，远程模式用于已选值回显 | SelectOption[] | - | [] |
| pageSize | 每页大小（仅远程分页模式生效） | number | - | 20 |
| popperClass | 自定义下拉框类名 | string | - | ‘’ |
| autoLoad | 远程模式首次打开时是否加载第一页 | boolean | true / false | true |
| labelKey | 自定义 label 字段名 | string | - | ‘label’ |
| valueKey | 自定义 value 字段名 | string | - | ‘value’ |
| showOptionCheckbox | 多选下拉选项前是否展示 checkbox | boolean | true / false | false |
| placeholder | 占位文本 | string | - |  |
| disabled | 是否禁用 | boolean | false |  |
| clearable | 是否可清空 | boolean | false |  |
| multiple | 是否多选 | boolean | false |  |
| multipleLimit | 多选数量限制，0 表示不限制 | number | 0 |  |
| ... | 共 29 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 选中值变化时触发 | value: string \| number \| array |
| load-success | 数据加载成功时触发 | data: SelectOption[] |
| load-error | 数据加载失败时触发 | error: Error |
| change | 选中值变化时触发 | value |
| clear | 点击清空按钮时触发 | - |
| remove-tag | 多选移除 tag 时触发 | value |
| focus | 输入框聚焦时触发 | event |
| blur | 输入框失焦时触发 | event |
| visible-change | 下拉框显示/隐藏时触发 | visible: boolean |

### Switch 开关 `[已验收]`

开关 需要表示开关状态 / 两种状态之间的切换时使用。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| model-value / v-model | 绑定值 | boolean \| string \| number | — | false |
| disabled | 是否禁用 | boolean | — | false |
| size | 尺寸 | 'large' \| 'default' \| 'small' | large / default / small | 'default' |
| width | 宽度 | number \| string | — | — |
| inline-prompt | 文本/图标是否内置 | boolean | — | false |
| active-icon | 开启态图标 | string \| Component | — | — |
| inactive-icon | 关闭态图标 | string \| Component | — | — |
| active-action-icon | 开启态操作图标 | string \| Component | — | — |
| inactive-action-icon | 关闭态操作图标 | string \| Component | — | — |
| active-text | 开启态文字 | string | — | '' |
| inactive-text | 关闭态文字 | string | — | '' |
| name | 原生 input name | string | — | '' |
| validate-event | 是否触发表单校验 | boolean | — | true |
| id | input id | string | — | — |
| tabindex | tabindex | number \| string | — | — |
| ... | 共 16 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 值变更 | (value: boolean \| string \| number) |

**插槽 Slot**

| name | 说明 |
|------|------|
| active | 自定义开关 开启 (on) 状态 的内容 |
| inactive | 自定义开关 关闭 (off) 状态 的内容 |
| active-action | 自定义开关 开启 (active) 行为 / 滑块 内容 |
| inactive-action | 自定义开关 关闭 (inactive) 行为 / 滑块 内容 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focus | 使 Switch 获取焦点 | — |

### Slider 滑动输入条 `[已验收]`

滑动输入条 展示当前值和可选范围。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model / model-value | 绑定值 | number \| number[] | - | 0 |
| min | 最小值 | number | - | 0 |
| max | 最大值 | number | - | 100 |
| disabled | 是否禁用 | boolean | - | false |
| step | 步长 | number | - | 1 |
| show-input | 是否显示输入框（BusySlider 增强：支持单值与 range 模式） | boolean | - | false |
| inputControlsPosition | 输入框控制按钮的位置 | string | ‘none’ / ‘right’ / ‘both’ | ‘none’ |
| show-stops | 是否显示间断点 | boolean | - | false |
| show-tooltip | 是否显示气泡提示 | boolean | - | true |
| format-tooltip | 格式化气泡提示信息 | (val: number) => string \| number | - | - |
| format-value-text | 格式化气泡屏幕阅读器信息 | (val: number) => string | - | - |
| placement | 气泡位置 | string | ‘top’ / ‘bottom’ / ‘left’ / ‘right’ | ‘top’ |
| range | 是否为范围选择 | boolean | - | false |
| vertical | 是否为垂直方向模式 | boolean | - | false |
| reverse | 是否反向（左右/上下互换） | boolean | - | false |
| ... | 共 17 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 值变更时触发（拖拽结束或输入框失焦时触发） | (value: number \| number[]) |
| input | 数据改变时触发（拖拽实时触发） | (value: number \| number[]) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focus | 使滑块获取焦点 | - |
| blur | 使滑块失去焦点 | - |

### TimePicker TimePicker 时间选择框 `[已验收]`

TimePicker 时间选择框 输入或选择时间的控件。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值；is-range 时为二元数组 | Date / string / number / 上述类型数组 / null | — |  |
| is-range | 时间范围选择 | boolean | false |  |
| range-type | 范围模式：default / custom-date | string | default |  |
| custom-date-options | custom-date 时日期列，如 [{ offset: 0, label: '今日' }, { offset: 1, label: '次日' }] | array | 今日、次日 |  |
| start-placeholder | 范围开始时间占位 | string | 开始时间（is-range 时） |  |
| end-placeholder | 范围结束时间占位 | string | 结束时间（is-range 时） |  |
| range-separator | 范围分隔符 | string | 至 |  |
| size | 尺寸 | large / default / small | default |  |
| disabled | 禁用，不可展开、不可编辑 | boolean | false |  |
| disabled-hours | 禁用的小时 | ( ) => number[] | — |  |
| disabled-minutes | 禁用的分钟 | (hour) => number[] | — |  |
| disabled-seconds | 禁用的秒 | (hour, minute) => number[] | — |  |
| placeholder | 占位文案 | string | '' |  |
| format | 展示格式 | string | — |  |
| value-format | 绑定值格式；不设则为 Date | string | — |  |
| ... | 共 22 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 点击「确定」后 | 当前绑定值 |
| visible-change | 面板展开 / 收起 | boolean |
| clear | 点击清空 | — |
| focus | 获得焦点 | FocusEvent |
| blur | 失去焦点 | FocusEvent |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focus | 聚焦 |  |
| blur | 失焦 |  |
| handleOpen | 打开面板 |  |
| handleClose | 关闭面板 |  |

### DatePicker 日期选择器 DatePicker `[已验收]`

日期选择器 DatePicker 基于 Element Plus el-date-picker 二次封装，提供日期、年、月、范围、季度、快捷选项等多种场景，并扩展了 footer 插槽与统一的设计风格。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue / v-model | 绑定值，range 模式下为长度 2 的数组 | string \| number \| Date \| string[] \| Date[] \| null | undefined |  |
| type | 选择器类型 | DatePickerType | 'date' |  |
| readonly | 是否只读 | boolean | false |  |
| disabled | 是否禁用 | boolean | false |  |
| size | 输入框尺寸 | 'large' \| 'default' \| 'small' | undefined |  |
| editable | 是否可手动输入 | boolean | true |  |
| clearable | 是否显示清除按钮 | boolean | true |  |
| placeholder | 非范围模式占位文字，不传时按 type 自动推导 | string | 按 type 推导 |  |
| startPlaceholder | 范围模式开始日期占位文字 | string | '开始时间' |  |
| endPlaceholder | 范围模式结束日期占位文字 | string | '结束时间' |  |
| format | 输入框显示格式 | string | undefined |  |
| valueFormat | v-model 字符串格式 | string | undefined |  |
| dateFormat | datetime 类型中日期部分的显示格式 | string | undefined |  |
| timeFormat | datetime 类型中时间部分的显示格式 | string | undefined |  |
| popperClass | 下拉框自定义类名 | string | 'busy-date-picker__popper' |  |
| ... | 共 46 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 绑定值变化时触发 | (value: string \| Date \| string[] \| Date[] \| null) |
| change | 用户确认选值或点击外部时触发 | (value: string \| Date \| string[] \| Date[] \| null) |
| blur | 输入框失焦时触发 | (ev: FocusEvent) |
| focus | 输入框聚焦时触发 | (ev: FocusEvent) |
| clear | 点击清除按钮时触发 | — |
| calendarChange | 范围选择中所选日期变化时触发 | (val: [Date, Date]) |
| panelChange | 点击面板导航按钮时触发 | (date: Date \| [Date, Date], mode: string, view: string) |
| visibleChange | 下拉面板显示 / 隐藏时触发 | (visibility: boolean) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focus | 使 input 获取焦点 | — |
| blur | 使 input 失去焦点 | — |
| handleOpen | 打开下拉面板 | — |
| handleClose | 关闭下拉面板 | — |

### DateTimePicker 日期时间选择器 `[已验收]`

日期时间选择器 选择日期和时间。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| type | 选择器类型 | string | datetime / datetimerange | datetime |
| v-model / modelValue | 绑定值。单选为 YYYY-MM-DD HH:mm:ss 字符串；范围为 [Date, Date]，空值为 [] | string \| [Date, Date] \| [] | — | '' |
| placeholder | 单选模式输入框占位文字 | string | — | '请选择日期时间' |
| startPlaceholder | 范围模式开始输入框占位文字 | string | — | '开始日期' |
| endPlaceholder | 范围模式结束输入框占位文字 | string | — | '结束日期' |
| rangeSeparator | 范围分隔符 | string | — | '至' |
| showSeconds | 时间面板是否展示秒列 | boolean | — | true |
| step | 时间面板步长，依次为 [时, 分, 秒] | [number, number, number] | — | [1, 1, 1] |
| disabled | 是否禁用 | boolean | — | false |
| readonly | 是否只读 | boolean | — | false |
| clearable | 是否显示清除按钮 | boolean | — | true |
| size | 输入框尺寸 | string | large / default / small | — |
| format | 输入框中显示的日期格式 | string | — | — |
| valueFormat | 绑定值的格式（设置后 v-model 为对应格式字符串） | string | — | — |
| popperClass | 下拉框自定义类名 | string | — | 'busy-date-picker__popper' |
| ... | 共 44 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | v-model 更新 | string \| [Date, Date] \| [] |
| change | 确认选择后触发 | string \| [Date, Date] \| [] |
| update:modelValue | v-model 更新 | [Date, Date] \| [] |
| change | 确认选择后触发 | [Date, Date] \| [] |
| clear | 用户清除后触发 | — |
| update:modelValue | v-model 更新 | string |
| change | 值变化时触发 | string |

### Upload 文件上传

文件上传 通用文件上传业务组件(oss直传) 基础用法 是否使用很忙运营平台oss直传 true 否 是 点击上传 格式：全部 大小：图片≤ 1MB、文件≤ 60MB 数量：不超过10个 food.jpeg flower.mp4 展开代码 复制代码 卡片列表 格式：全部 大小：图片≤ 30MB、文件≤ 60MB 数量：不超过5个 展开代码 复制代码 通过自定义类名修改样式、粘贴上传 格式：全部 大小：图片≤ 30MB、文件≤ 60MB 数量：不超过5个 展开代码 复制代码 支持拖拽上传 点击或将文件拖拽到这里上传 格式：全部 大小：图片≤ 30MB、文件≤ 60MB 数量：不超过5个 展开代码

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model:fileList | 默认上传文件 | UploadUserFile[] | - | — |
| multiple | 是否支持多选文件 | boolean | - | — |
| limit | 允许上传文件的最大数量 | number | - | 3 |
| ossDirName | 自定义oss文件夹名称 | string | - | ‘busyUiUpload’ |
| listType | 文件列表的类型 | ‘text’ \| ‘picture-card’ \| ‘dragger’ | - | ‘picture-card’ |
| accept | 接受上传的文件类型 | string | - | * |
| disabled | 是否禁用上传 | boolean | true/false | false |
| uploadTip | 提示语 | string | - | 格式：全部 大小：图片≤ 30MB、文件≤ 60MB 数量：不超过3个 |
| drag | 是否可拖拽上传文件 | boolean | - | false |
| paste | 是否支持粘贴上传（Ctrl+V / Cmd+V），hover 到上传区域即可粘贴 | boolean | - | false |
| useBusyAliOssUpload | 是否使用阿里云 OSS 上传服务 | boolean | true/false | true |
| uploadMode | OSS 上传模式 | ‘policy’ \| ‘sts’ | - | ‘policy’ |
| getSTSToken | 获取 STS Token 的方法（uploadMode 为 ‘sts’ 时必填） | () => Promise<STSTokenResponse> | - | - |
| customOssPolicyUrl | 自定义获取阿里云 OSS 直传配置的 api 地址 | string | ‘’ | ‘’ |
| fileApiPrefix | 存取文件时，业务后台对应的文件服务api前缀 | string | ‘’ | ‘/gateway/filemanage’ |
| ... | 共 27 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 当绑定值变化时触发的事件 | (currentFileList, currentFileOptions) => void |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 触发上传按钮自定义插槽 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| handleFileDownload | 触发文件下载，会根据 customDownload 和 useBuiltInDownloadCheck 的配置走对应下载流程 | (file: UploadUserFile & IFileMeta) => void |

### Import 文件导入控件

文件导入控件 通用导入控件，支持简单上传模式（弹窗，仅上传文件至 OSS）和解析导入模式（抽屉，本地/远程解析 Excel 并映射为 JSON 数据）。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| triggerTitle | 触发按钮文本 | string | - | 导入 |
| accept | 接受的文件类型 | string | - | .xlsx, .xls |
| uploadTips | 弹窗顶部的提示文字 | string | - | 请上传 Excel 文件，支持 .xlsx 和 .xls 格式 |
| description | 弹窗底部的导入说明（不传则不显示） | string | - | - |
| templateFileUrl | 模板文件下载链接（直接 URL，紧随提示文字后展示） | string | - | - |
| onDownloadTemplate | 模板下载处理函数，传入时优先于 templateFileUrl。用于请求后端接口下载等场景 | () => void \| Promise<void> | - | - |
| fileSize | 文件大小限制，单位 MB | number | - | 3 |
| limit | 上传文件个数限制（简单模式生效，解析模式内部强制为 1） | number | - | 3 |
| dataLimit | 解析数据行数限制 | number | - | 1000 |
| isSimpleMode | 是否简约模式（仅上传不带数据解析） | boolean | - | true |
| tableColumns | 表格列映射配置（解析模式必传） | TableColumn[] | - | - |
| showIndex | 是否显示表格序号（仅解析模式生效） | boolean | - | true |
| parseHandler | 远程解析函数，传入则使用远程解析，否则走本地 XLSX 解析 | (file: File) => Promise<any[]> | - | - |
| uploadProps | 透传给 busy-upload 的额外配置（如 OSS 相关）。解析模式下：传入空对象（默认）则只做本地解析不上传 OSS；传入 OSS 配置则同时上传并获取文件 URL | Record<string, any> | - | {} |
| drawerSize | 抽屉宽度（仅解析模式生效），支持预设档位（small=480px/middle=680px/large=880px/xlarge=1080px）或自定义像素值 | string \| number | - | 880 |
| ... | 共 20 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 点击确认按钮 | (files: UploadUserFile[], data?: any[]) — files 含 OSS url；data 为解析后的 JSON 数组（简单模式无 data） |
| cancel | 点击取消或关闭弹窗 | - |
| file-change | 文件列表变化 | (fileList: UploadUserFile[]) |
| parse-success | 文件解析成功 | (data: any[]) |
| parse-error | 文件解析失败 | (error: Error) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| openDialog | 打开导入弹窗/抽屉 | - |
| closeDialog | 关闭导入弹窗/抽屉并重置状态 | - |
| setTableData | 外部手动设置解析结果数据 | (data: any[]) |
| getTableData | 获取当前解析结果数据 | - → any[] |

### Transfer 穿梭框 `[已验收]`

穿梭框 基于 el-tree 的自定义树形穿梭框组件，支持树形 / 平铺两种右侧展示模式、搜索过滤、标题操作按钮及完整的插槽扩展能力。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 右侧已选叶子节点 key 列表 | TKey[] | [] |  |
| data | 树形数据源 | TreeNode[] | [] |  |
| node-key | 节点唯一 key 字段名 | string | 'id' |  |
| tree-props | el-tree 字段别名配置 | TreeFieldProps | { children: 'children', label: 'label' } |  |
| titles | 左右面板标题 | [string, string] | ['左侧标题', '右侧标题'] |  |
| size | 尺寸 | 'small' \| 'default' \| 'large' | 'default' |  |
| height | 列表区高度，数字按 px 处理 | string \| number | '' |  |
| disabled | 整体禁用 | boolean | false |  |
| default-expand-all | 默认展开全部节点 | boolean | true |  |
| check-strictly | 父子节点严格模式（互不关联） | boolean | false |  |
| empty-text | 空状态文案 | string | '您尚未选择范围哦！快去选择一个吧' |  |
| empty-icon | 空状态图标 URL | string | 内置图标 |  |
| filterable | 是否开启搜索框 | boolean | false |  |
| filter-placeholder | 搜索框占位文案 | string | '请输入' |  |
| left-action | 左侧标题操作按钮 | PanelAction | — |  |
| ... | 共 28 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | v-model 更新 | (value: TKey[]) |
| change | 右侧已选数据变化 | (value: TKey[], direction: TransferDirection, movedKeys: TKey[]) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| transferToRight | 将指定 key 移入右侧 | keys: TKey[] |
| transferToLeft | 将指定 key 移回左侧 | keys: TKey[] |
| clear | 清空右侧所有已选项 | — |
| selectAll | 全选左侧全部叶子节点 | — |
| leftTree | 左侧 el-tree 实例 | — |
| rightTree | 右侧 el-tree 实例 | — |

### Form 业务表单

业务表单 通用业务表单控件 基础用法 基础信息 账号： 姓名： 网址： Http:// 域名： .com 长文本示例： This is a very long prepend text that will be truncated This is a very long append text 密码： 确认密码： 详细信息 数量： 个 自定义状态： 未启用 留言： 区域： 请选择 区域（多选）： 请选择区域（多选） 分页选择： 请选择用户 其他信息 开关： 禁用开关： 单选： 很忙 一鸣 多选： 很忙 一鸣 鸣鸣很忙集团 日期： - 时间： - 上传图片： 格式：全部 大小：图片≤ 30MB、

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| formConfigList | 表单控件配置项 | IFormItemConfig[] | - | — |
| readonly | 是否只读 | boolean | true / false | false |
| flex | 表单项span值 | number | - | 24 |
| gutter | 行内间隔 | number | - | 0 |
| fullWidth | 是否撑满宽度（不限制max-width: 600px），适用于在Dialog/Drawer等弹层中使用 | boolean | true / false | false |
| value | 当前表单项的值 |  |  |  |
| change | 更新当前表单项值的方法 |  |  |  |
| item | 当前表单项配置 |  |  |  |
| form | 当前整个表单模型 |  |  |  |
| multiple | 是否多选 | boolean | false |  |
| checkStrictly | 父子节点不关联 | boolean | false |  |
| clearable | 是否可清空 | boolean | false |  |
| filterable | 是否可搜索 | boolean | false |  |
| lazy | 是否懒加载 | boolean | false |  |
| load | 懒加载方法 | function(node, resolve) | - |  |
| ... | 共 16 个属性 | | | |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| getFormRef | 获取el-form表单实例暴露出的方法 | — |

### Searcher 筛选器 Searcher

筛选器 Searcher 通用筛选组件，支持输入框、下拉选择、分页选择、树形选择、日期范围等多种控件类型，也支持自定义组件作为筛选项。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| searchConfig | 搜索配置项列表 | SearchConfigVo[] | — | [] |
| searchBtn | 查询按钮配置 | SearchBtnsVo | — | { show: true, name: '查询' } |
| resetBtn | 重置按钮配置 | SearchBtnsVo | — | { show: true, name: '重置' } |
| searchCacheKey | 搜索条件缓存 key，传入后开启内存缓存 | string | — | '' |
| type | 控件类型 | string \| Component \| (() => Component) | 'input' / 'select' / 'pageable-select' / 'tree-select' / 'daterange' / 自定义组件 | — |
| label | 标签文本 | string | — | — |
| name | 字段名（对应搜索表单的 key） | string | — | — |
| customProps | 透传给内部控件的 Props | CustomPropsVo | — | — |
| list | 选项列表（select / tree-select 使用） | SearchOptionItem[] | — | — |
| loadData | 异步分页加载函数（pageable-select 使用） | (pagination: PaginationConfig) => Promise<{ data: SelectOption[]; total: number }> | — | — |
| initialOptions | 初始选项数据（pageable-select 使用） | SelectOption[] | — | — |
| initValue | 初始值 | MaybeRef<SearchFormValue> | — | — |
| show | 是否显示，支持函数形式 | boolean \| (() => boolean) | — | — |
| span | 栅格列宽（24 栅格） | number | 1-24 | 自适应 |
| labelConfig | 标签配置，透传给 el-form-item | object | — | — |
| ... | 共 38 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| search | 触发搜索，点击查询按钮或回车时触发 | (params: SearchFormVo) |
| reset | 重置搜索表单，点击重置按钮时触发 | (params: SearchFormVo) |
| searchFormChange | 搜索表单字段值变化时触发 | (form: SearchFormVo) |
| toggleSearchForm | 搜索表单展开/收起状态变化时触发 | (info: { expanded: boolean; height?: number }) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 默认插槽 |
| search-btn-prefix | 搜索按钮前缀插槽，用于在查询/重置按钮前插入自定义内容 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| setSearchParams | 设置搜索参数（整体或单个字段） | (value: SearchFormVo) 或 (value: any, label: string) |
| setSearchFieldValue | 设置单个搜索字段的值 | (label: string, value: unknown) |
| getSearchParams | 获取当前搜索参数 | — |

### Cascader 级联选择器

级联选择器 基于 Element Plus ElCascader 的企业级封装，用于层级数据选择、远程加载与懒加载场景。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue | 绑定值 | CascaderModelValue | — |  |
| options | 静态选项 | CascaderOption[] | [] |  |
| fieldNames | 字段映射（label/value/children/disabled/leaf） | CascaderFieldNames | {} |  |
| multiple | 是否多选 | boolean | false |  |
| checkStrictly | 父子节点是否不互相关联 | boolean | false |  |
| emitPath | 是否返回完整路径 | boolean | true |  |
| expandTrigger | 展开触发方式 | 'click' \\| 'hover' | 'click' |  |
| filterable | 是否可搜索 | boolean | false |  |
| highlightSearch | 搜索时是否高亮匹配文案（见「可搜索」章节） | boolean | true |  |
| filterMethod | 自定义搜索方法 | (node, keyword) => boolean | — |  |
| beforeFilter | 搜索前置钩子 | (keyword) => boolean \\| Promise<boolean> | — |  |
| debounce | 搜索防抖毫秒数 | number | 300 |  |
| clearable | 是否可清空 | boolean | false |  |
| collapseTags | 多选是否折叠标签 | boolean | false |  |
| collapseTagsTooltip | 折叠标签是否展示 tooltip | boolean | false |  |
| ... | 共 32 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 绑定值更新 | (value: CascaderModelValue) |
| change | 选中值变化 | (value: CascaderModelValue) |
| expand-change | 展开路径变化 | (pathValues: CascaderValue[]) |
| visible-change | 下拉显示状态变化 | (visible: boolean) |
| remove-tag | 多选删除 tag | (value: CascaderValue) |
| focus | 获取焦点 | (event: FocusEvent) |
| blur | 失去焦点 | (event: FocusEvent) |
| request-error | request 加载失败 | (error: unknown) |
| load-error | lazyLoad 加载失败 | (error: unknown, node: CascaderLazyNode) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 节点自定义渲染，作用域参数与 ElCascader 默认插槽一致 |
| suggestion-item | 搜索建议项渲染（filterable 时），作用域参数 { item } |
| header | 下拉面板头部内容（与 ElCascader 一致） |
| footer | 下拉面板底部内容（与 ElCascader 一致，推荐用于全选等自定义操作） |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| refresh | 重新执行 request 拉取数据（无 request 时同步静态 options） | — |
| clearCache | 清理懒加载缓存 | — |
| getCheckedNodes | 获取已选节点 | leafOnly?: boolean |
| getFlattedNodes | 获取扁平节点（懒加载场景仅含已加载节点） | leafOnly?: boolean |
| getOptions | 获取当前 options（request 模式为拉取后的全量树） | — |
| togglePopperVisible | 控制下拉开合 | visible?: boolean |
| focus | 使输入框获取焦点 | — |
| blur | 使输入框失去焦点 | — |

## 基础组件 / 信息展示

### ProTable ProTable

ProTable ProTable 是基于 Element Plus Table 的业务增强表格组件，内置了搜索、分页、Tabs、工具栏、列设置、行选择与操作列等常用 CRUD 能力。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| columns | 列配置（核心配置） | ColumnSchema[] | [] |  |
| request | 请求配置，传入后组件自动管理 loading/data/error | RequestOptions | - |  |
| data | 静态数据源（与 request 二选一） | RowBase[] | - |  |
| rowKey | 行唯一标识字段 | string | 'id' |  |
| tabs | Tab 配置，切换时自动合并 tab.params 到请求参数 | TabSchema[] | - |  |
| actions | 行操作配置 | ActionSchema[] | [] |  |
| actionWidth | 操作列宽度 | number | 180 |  |
| actionLabel | 操作列标题 | string | '操作' |  |
| showIndex | 是否显示序号列 | boolean | false |  |
| selectable | 是否显示选择列 | boolean | false |  |
| selectionType | 选择类型 | 'checkbox' \| 'radio' | 'checkbox' |  |
| rowSelectable | 行级可选控制函数 | (row, index) => boolean | - |  |
| pagination | 分页配置，收敛 showPagination / pageSizes / defaultPageSize 到统一对象。false 隐藏分页器；undefined 使用默认配置 | ProTablePaginationConfig \| false | undefined |  |
| pageSizes | 已废弃，建议使用 pagination.pageSizes。分页 size 选项 | number[] | [10, 20, 50, 100] |  |
| defaultPageSize | 已废弃，建议使用 pagination.pageSize。默认每页条数（初始 pageSize） | number | 10 |  |
| ... | 共 147 个属性 | | | |

**ColumnSchema 常用列能力**

| 参数 | 说明 | 类型 |
|------|------|------|
| prop | 对应行数据字段 | keyof Row |
| formatter | 格式化为字符串或数字 | (value, row, index) => string \| number |
| render | 自定义渲染 VNode；适合直接使用 Badge、Tag 等 Busy-UI 组件 | (value, row, index) => VNode \| string \| number \| null |
| slot | 显式指定列插槽名；复杂交互且 render 不足时使用 | string |

渲染优先级：`slot > render > formatter > valueType > 原始值`。标准状态列优先 `render` BusyBadge，避免页面手写圆点 DOM 与样式。

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| search | 点击查询触发 | (params: RequestParams) |
| reset | 点击重置触发 | (params: RequestParams) |
| tab-change | 切换 Tab 触发 | (value: string \| number) |
| search-toggle | 搜索展开/收起触发 | (expanded: boolean) |
| row-click | 行点击 | (row, column, event) |
| row-dblclick | 行双击 | (row, column, event) |
| sort-change | 排序变化 | ({ prop, order }) |
| fullscreen-change | 全屏状态变化 | (value: boolean) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| refresh | 按当前分页和筛选刷新 | () => void |
| reset | 重置筛选并刷新 | () => void |
| getSelection | 获取选中行 | () => RowBase[] |
| clearSelection | 清空选中 | () => void |
| getSearchParams | 获取当前请求参数（分页 + 搜索 + tab） | () => RequestParams |
| searchModel | 搜索表单双向绑定数据 | Ref<Record<string, unknown>> |
| setData | 手动设置数据（仅 data 模式） | (data: RowBase[]) => void |
| tableRef | el-table 实例引用 | unknown |
| toggleFullscreen | 切换全屏状态 | () => void |

### Table 表格 `[已废弃]`

表格 公用表格业务组件 维护提醒：Table 组件已停止维护，后续表格相关需求请移步 ProTable（高级表格）。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| tableColumns | 表格列配置对象 | Array | 见下方 tableColumns 详情 | [] |
| listData | 列表数据 | Array | - | [] |
| searchConfig | 筛选配置对象,若配置则显示筛选栏 | Array | 见下方 searchConfig 详情 | [] |
| searchBtnPosition(v7.0.0+之后版本废弃) | 搜索按钮在表格两端的位置 | String | 'left'\'right' | 'right' |
| resetSearchFlag (6.12.99 已废弃) | 点击重置时是否保持传入初始值 | boolean | - | false |
| searchParams（1.4.11之后废弃） | 筛选对象的初始数据 | object | - | {} |
| showExpandBtn(v7.0.0+之后版本废弃) | 是否显示筛选项展开按钮 | boolean | - | false |
| showPagination | 是否展示分页 | boolean | true/false | true |
| pagination | 分页对象 | object | - | { pageNum: 1, pageSize: 10, total: 0 } |
| sizes | 每页显示个数选择器的选项设置 | Array | - | [10, 20, 50] |
| checkable | 是否显示选框 | boolean | true/false | true |
| selectionType | 选框类型 多/单选的选择框 | String | ‘checkbox’/‘radio’ | '' |
| selectedRowKey | 选中项的key | String | ‘id’ | ‘’ |
| selectable | 函数返回值用来决定这一行的 CheckBox or Radio 是否可以勾选 | (row: any, index: number) => boolean | - | - |
| selectionColumnProps | 自定义选择列（radio/checkbox）的 el-table-column 属性，如 className、width 等 | Partial<TableColumnPropsVo> | - | {} |
| ... | 共 73 个属性 | | | |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| setTableSelection | 设置表格选中状态 | setTableSelection: (selectedRows: Array<Record<string, any>>, flag?: boolean) => void |
| getTableSelection | 返回当前选中的行 获取焦点 | getTableSelection: () => Array<any> |
| clearTableSelection | 清空表格当前页选中项 | clearTableSelection: () => void |
| getSearchParams | 获取筛选条件数据 | getSearchParams: () => Object<any> |
| setSearchParams | 设置筛选条件数据 | setSearchParams: (val: any, label?: string) => void //label存在则设置label对应的值，否则设置整个对象 |
| tableRef | 表格Ref | - |

### Pagination 分页

分页 采用分页的形式分隔长列表，每次只加载一个页面。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| total | 总条目数 | number | - | 0 |
| currentPage / v-model:currentPage | 当前页数 | number | - | 1 |
| pageSize / v-model:pageSize | 每页显示条目个数 | number | - | 10 |
| pageSizes | 每页显示个数选择器的选项 | number[] | - | [10, 20, 30, 40, 50, 100] |
| pagerCount | 最大页码按钮数（必须为奇数，≥5 且 ≤21） | number | - | 5 |
| layout | 组件布局，子组件名用逗号分隔 | string | prev/pager/next/jumper/total/sizes/slot/-> | 'prev, pager, next' |
| background | 是否添加背景色 | boolean | - | false |
| size | 分页尺寸 | PaginationSize | default / small / large | 'default' |
| disabled | 是否禁用 | boolean | - | false |
| hideOnSinglePage | 只有一页时是否隐藏 | boolean | - | false |
| prevText | 上一页文字（替代图标） | string | - | '' |
| nextText | 下一页文字（替代图标） | string | - | '' |
| popperClass | sizes 下拉框类名 | string | - | '' |
| teleported | 是否将下拉菜单 teleport 至 body | boolean | - | true |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:currentPage | 当前页变化时触发 | (currentPage: number) |
| update:pageSize | 每页条数变化时触发 | (pageSize: number) |
| size-change | pageSize 改变时触发 | (pageSize: number) |
| current-change | currentPage 改变时触发 | (currentPage: number) |
| change | currentPage 或 pageSize 变更时触发 | (currentPage: number, pageSize: number) |
| prev-click | 点击上一页时触发 | (currentPage: number) |
| next-click | 点击下一页时触发 | (currentPage: number) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义内容，需要在 layout 中列出 slot |

### Tag 标签 Tag `[已验收]`

标签 Tag 标签是图形化标记界面上的元素的组件，用于信息的选择、筛选、分类。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| type | 颜色类型 | string | primary / success / warning / danger / info | primary |
| effect | 视觉效果 | string | solid / light / outline | solid |
| size | 尺寸 | string | default / large | default |
| shape | 形状（仅 size="default" 有效） | string | square / round | square |
| closable | 是否可关闭，显示右侧 × 按钮 | boolean | — | false |
| addable | 动态编辑模式，渲染为新增按钮 | boolean | — | false |
| disabled | 禁用状态（配合 addable 使用） | boolean | — | false |
| icon | 左侧图标组件，与 #icon 插槽二选一，插槽优先级更高 | Component | — | — |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| close | closable 模式下，点击 × 时触发 | — |
| add | addable 模式下，输入内容确认后触发 | (value: string) |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 标签文字内容 |
| icon | 左侧图标插槽，优先级高于 icon prop；SVG 建议使用 width="1em" height="1em" 随尺寸自动缩放 |

### ProgressBar 进度条 `[已验收]`

进度条 基础用法 线性进度条 Progress 组件设置 percentage 属性即可，表示进度条对应的百分比。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| percentage | 百分比进度（0-100） | number | - | 0 |
| type | 进度条类型 | string | line / circle / dashboard | line |
| status | 进度条状态 | string | success / exception / warning | - |
| stroke-width | 进度条线宽（px） | number | - | 6 |
| text-inside | 百分比文字显示在进度条内部（仅 line） | boolean | true / false | false |
| width | 环形进度条画布宽高（仅 circle/dashboard） | number | - | 126 |
| show-text | 是否显示进度条文字内容 | boolean | true / false | true |
| stroke-linecap | 路径两端形状（仅 circle/dashboard） | string | round / butt / square | round |
| color | 自定义进度条背景色，传入后将覆盖默认的颜色（支持字符串 / 数组 / 函数） | string / function / array | - | - |
| format | 自定义进度条文字内容 | function(percentage) => string | - | (p) => p + '%' |
| striped | 在进度条上增加条纹（仅 line） | boolean | true / false | false |
| striped-flow | 让条纹有流动感，需配合 striped 使用（仅 line） | boolean | true / false | false |
| indeterminate | 进入不确定进度状态（仅 line） | boolean | true / false | false |
| duration | 不确定状态动画周期（秒，仅 line） | number | - | 3 |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| - | - | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义进度条内容，插槽参数：{ percentage }；设置后将完全接管文字/图标区域的渲染 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| - | - | - |

### Badge  `[已验收]`

标记 Badge 设计语言与规范 以下为设计稿中的颜色、形态、尺寸与使用场景说明。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| dot / isDot | 小圆点（isDot 对齐 Element Plus） | boolean | — | false |
| count | 数字徽标 | number \| string | — | — |
| value | 展示值（对齐 EP）；数字同 count，字符串作文字 | number \| string | — | — |
| text | 文字徽标 / 状态点文案 | string | — | '' |
| max | 数字上限，超出显示 {max}+ | number | — | 99 |
| textMaxLength | 文字截断长度 | number | — | 4 |
| size | 预设尺寸（字号/高度） | string | S / M / L | M |
| fontSize | 自定义字号 | number \| string | — | — |
| height | 自定义高度 | number \| string | — | — |
| dotSize | 小圆点尺寸 | number \| string | — | 6 |
| shape | 形状；auto 按内容推断 | string | circle / ellipse / leaf / auto | auto |
| type | 语义色（对齐 EP） | string | primary / success / warning / danger / info | danger |
| backgroundColor / color | 背景色（color 对齐 EP，优先级更高） | string | — | 由 type 推导 |
| borderColor | 外描边色（1px） | string | — | #FFFFFF |
| placement | 组合模式位置 | string | 见上 | top-right |
| status | 状态点模式：语义色圆点 + `text` 文案；优先于 dot/count | string | primary / success / warning / error / info | — |
| tag | 状态点模式根元素标签 | string | HTML 标签名 | span |
| ... | 共 22 个属性 | | | |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 组合模式包裹的内容；状态点模式下的文案（与 text 并用） |
| content | 自定义徽标内容，作用域 { value }（对齐 Element Plus） |

**状态列示例**

```ts
import { h } from 'vue'
import BusyBadge from '@busy-fe/ui/Badge'

render: (_value, row) => h(BusyBadge, {
  status: row.enabled ? 'success' : 'info',
  text: row.statusName
})
```

`status` 是状态点语义色；普通徽标的 `type` 使用 `danger`，状态点的对应错误色使用 `error`，不要混用。

### Empty 空状态 `[已验收]`

空状态 指当前场景没有对应的数据内容，呈现出的展示占位图。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| image | 图片地址，传入后优先级高于 type | string | — |  |
| image-size | 图片宽度（px） | number | — |  |
| description | 描述文案 | string | — |  |
| type | 内置空状态图片类型，未传 image 时按该值展示对应内置图，未设置则展示 image_empty.png | 'empty' \| '404' \| 'internet' \| 'develop' \| 'store' \| 'search' \| 'selection' \| 'review' \| 'new' \| 'no-permission' \| 'history-order' \| 'ongoing-order' \| 'pre-order' \| 'claim-order' | 'empty' |  |

**插槽 Slot**

| name | 说明 |
|------|------|
| image | 自定义图片 |
| description | 自定义描述文案 |
| default | 自定义底部内容 |

### Descriptions 描述列表 Descriptions `[已验收]`

描述列表 Descriptions 成组展示多个只读字段，一般用于详情页的信息展示。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| title | 标题文案；未传时可改用 title 插槽 | string | '' |  |
| column | 总列数 | number | 4 |  |
| direction | 排列方向 | 'horizontal' \| 'vertical' | 'horizontal' |  |
| emphasis | 水平方向下的视觉重点：balanced 平均重点 / content 突出内容 | 'balanced' \| 'content' | 'balanced' |  |
| border | 是否启用带线框等分样式（仅 horizontal 生效，优先级高于 emphasis） | boolean | false |  |
| label-align | label 文本对齐方式 | 'left' \| 'right' | 'left' |  |
| label-width | label 列宽度；number 按 px，string 原样输出。未传时：content → max-content，border → 120px，balanced 不生效 | string \| number | - |  |
| content-min-width | 内容列最小宽度，防止 max-content label 列挤占内容列 | string \| number | 0 |  |
| colon | 是否在 balanced 水平模式下自动在 label 后添加冒号（「：」），属于开箱即用能力 | boolean | true |  |
| filled | 最后一个 item 独占新行时，是否自动将其扩展到整行 | boolean | false |  |
| label | 标签文本；也可通过 #label 插槽传入 | string | '' |  |
| span | 跨列数；'filled' 表示填满当前行剩余列；超出剩余列数时由父组件按行截断 | number \| 'filled' | 1 |  |
| ellipsis | 内容过长时的展示策略：true 单行省略 / false 允许换行 / 数字（如 2）多行截断省略 | boolean \| number | true |  |
| label-width | 单项覆盖父级 label-width；主要在 balanced / vertical 模式下针对 label 自身生效 | string \| number | - |  |

### Result 结果页

结果页 向用户传达任务完成结果，引导用户进行下一步操作。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| status | 结果状态 | ResultStatus | success / error | 'success' |
| title | 标题 | string \| VNode | - | - |
| subTitle | 副标题 | string \| VNode | - | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 主内容区（补充信息） |
| title | 标题插槽（覆盖 title prop） |
| subTitle | 副标题插槽（覆盖 subTitle prop） |
| icon | 自定义图标插槽（覆盖默认状态图标） |
| extra | 操作区插槽 |

### Avatar 头像

头像 用来代表用户或事物，支持图片、图标或字符展示。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| size | 尺寸（px） | number | 24 / 32 / 40 / 64 | 40 |
| shape | 形状 | string | circle / square | circle |
| type | 预置背景色类型 | string | default / primary / danger | default |
| backgroundColor | 自定义背景色 | string | — | — |
| color | 自定义文字/图标颜色 | string | — | — |
| src | 图片地址 | string | — | — |
| alt | 图片 alt 属性 | string | — | ‘’ |
| text | 文字内容 | string | — | — |
| icon | 图标组件 | object / function | — | — |
| gap | 字符距离左右两侧边界（px） | number | — | 4 |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| error | 图片加载失败时触发 | Event |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义头像内容（优先级最高） |

## 业务组件

### TableSearch TableSearch 搜索表单

TableSearch 搜索表单 通用表格搜索组件，支持多种字段类型（输入框、下拉、日期、日期范围、分页加载下拉选择器），可通过配置驱动渲染 支持插槽自定义字段 此组件主要是将表格与搜索表单功能解耦，支持需要自定义处理的特殊场景，降低原有表格组件的复杂度及功能局限性 组件支持设置输入元素宽度的最大值和最小值，内部会做自适应处理，因为要铺满容器，宽度可能会超过最大值 支持设置标签宽度 基础用法 编码 标签 请选择标签 名称 状态 请选择 创建日期 日期范围 至 重置 查询 当前表单值：{} 自定义插槽示例 关键词 标签 请选择标签 重置 查询 自定义插槽表单值：{} 展开代码 复制代码 API 

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue (v-model) | 搜索表单绑定值 | Record<string, string \| number \| undefined> | {} |  |
| searchConfig | 搜索表单字段配置 | SearchFieldConfig[] | [] |  |
| labelWidth | 表单 label 宽度 | string | '68px' |  |
| prop | 字段名 | string | - |  |
| label | 字段标签 | string | - |  |
| type | 表单类型 | 'input' \| 'select' \| 'date' \| 'daterange' | 'input' |  |
| placeholder | 占位文本 | string | - |  |
| options | select 选项（type 为 select 时生效） | Array<{ label: string; value: string \| number }> | - |  |
| defaultValue | 默认值 | string | - |  |
| search-{prop} | 自定义指定字段的渲染内容 | { field: SearchFieldConfig, model: Record<string, unknown> } |  |  |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 表单值变化 | (val: Record<string, string \| number \| undefined>) |
| search | 点击查询按钮 | - |
| reset | 点击重置按钮 | - |

### AuditDialog 审批流程弹窗

审批流程弹窗 统一规范的审批流程操作弹窗，可选择审批结果，填入备注，或者简单的二次确认弹窗，也可进行自定义配置表单项 基础用法 审核 展开代码 复制代码 二次确认提示语 审核 展开代码 复制代码 添加自定义表单项 审核 展开代码 复制代码 属性 prop 参数 说明 类型 可选值 默认值 title 审批流程弹窗标题 string - ‘审批操作’ msg 二次确认提示语 string - ‘’ showAuditRadio 是否展示审批结果单选组 Boolean - true rules 自定义表单校验规则 Object - null formConfigs 自定义表单配置项 Array a

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| title | 审批流程弹窗标题 | string | - | ‘审批操作’ |
| msg | 二次确认提示语 | string | - | ‘’ |
| showAuditRadio | 是否展示审批结果单选组 | Boolean | - | true |
| rules | 自定义表单校验规则 | Object | - | null |
| formConfigs | 自定义表单配置项 | Array as PropType<IFormItem[ ]> | - | [ ] |
| defaultFormData | 初始表单数据 | Object | - | null |
| remarkLimit | 备注输入框限制字数 | Number | - | 500 |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 确认按钮点击事件 | 表单数据 |
| close | 弹窗取消，关闭事件 | - |
| formChange | 表单值改变事件 | 表单数据 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| configForm | 审批表单数据 | - |

### BrandSelector 品牌选择器

品牌选择器 统一品牌单选业务组件，支持 radio 与 select 两种模式。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 选中值 | string \| number \| boolean \| undefined | - | - |
| mode | 展示模式 | 'select' \| 'radio' | select / radio | select |
| fetchOptions | 数据源，支持直接数组、Promise、或返回值为数组/Promise的函数 | BrandSelectorFetchSource | - | [{ label: '很忙', value: 'LSHM' }, { label: '一鸣', value: 'ZYM' }] |
| fetchOn | 加载时机 | 'mount' \| 'focus' \| 'manual' | mount / focus / manual | mount |
| lazy | 是否启用懒加载（等价于 fetchOn='focus'） | boolean | true / false | false |
| labelKey | 标签字段名（支持路径，如 meta.name） | string | - | label |
| valueKey | 值字段名（支持路径） | string | - | value |
| disabledKey | 禁用字段名（支持路径） | string | - | disabled |
| placeholder | select 占位符 | string | - | 请选择品牌 |
| clearable | select 是否可清空 | boolean | true / false | true |
| filterable | select 是否可搜索 | boolean | true / false | true |
| disabled | 是否禁用组件 | boolean | true / false | false |
| loadingText | 加载中文案 | string | - | 加载中 |
| emptyText | 空数据文案 | string | - | 暂无数据 |
| autoClearInvalidValue | 数据源变化后，当前值不在选项中时自动清空 | boolean | true / false | false |
| ... | 共 17 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 选中项变化 | (value, option) |
| loaded | 选项加载并归一化完成 | (options) |
| error | 加载数据失败 | (error) |

**插槽 Slot**

| name | 说明 |
|------|------|
| option | 自定义选项渲染，参数：{ option, index } |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| reload | 重新加载选项 | - |
| clear | 清空选中值 | - |
| focus | 聚焦组件 | - |
| getOptions | 获取归一化后的选项 | - |
| getOptionByValue | 根据 value 获取选项 | value |

### StoreSelectorV2 StoreSelectorV2 门店选择器 V2

StoreSelectorV2 门店选择器 V2 基于抽屉的门店选择器组件，支持在线选择和批量导入两种模式。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| visible | 控制抽屉显示（支持 v-model:visible），使用 trigger prop 或 #trigger slot 时无需传入 | boolean | false |  |
| title | 抽屉标题 | string | '添加门店' |  |
| size | 抽屉宽度 | string \| number | '70%' |  |
| type | 组件类型：complex（复杂版）/ basic（基础版） | 'complex' \| 'basic' | 'complex' |  |
| selectedValues | 已选门店数据，支持 v-model:selected-values 双向绑定。传 ID 数组时组件内部自动调接口补全门店名称；传 StoreItem 对象数组时直接完整回显 | (string \| number)[] \| StoreItem[] | [] |  |
| trigger | 内置触发器类型，设置后由组件内部管理抽屉显隐，无需外部 v-model:visible | 'button' \| 'input' | undefined |  |
| triggerText | 触发按钮文字，仅 trigger='button' 时有效 | string | '添加门店' |  |
| formatDisplay | 自定义 input 触发器的显示值格式化函数，仅 trigger='input' 时有效 | (items: StoreItem[]) => string | undefined |  |
| requestMode | 请求环境预设，用于切换不同环境的接口域名。不传时使用应用默认请求实例 | RequestPresetMode | undefined |  |
| permissionCode | MSE 验签权限码，通过 queryConfig / regionTreeConfig / importConfig 使用自定义接口时传入，组件自动将其注入请求 headers 供 MSE 匹配资源。固定接口无需传入 | string | undefined |  |
| queryConfig | ⚠️ 使用自定义接口时必须配置，详见下方注意事项 门店查询接口配置，不传则使用 Mock 数据 | QueryConfig | undefined |  |
| importConfig | 批量导入接口配置（仅 complex 模式）。⚠️ 自定义接口时需注意 MSE 验签要求 | ImportConfig | undefined |  |
| regionTreeConfig | ⚠️ 使用自定义接口时必须配置 省市区树接口配置，不传则使用 Mock 数据 | RegionTreeConfig | undefined |  |
| regionTreeTitle | 左侧筛选树标题，适用于非省市区维度的树形数据（如组织树） | string | '区域选项' |  |
| url | 查询接口地址 | string |  |  |
| ... | 共 26 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:visible | visible 状态变化 | (visible: boolean) |
| confirm | 确认选择，返回已选门店完整对象列表 | (selectedItems: StoreItem[]) |
| update:selectedValues | 确认选择时自动触发，返回已选门店 ID 数组，配合 v-model:selected-values 实现双向绑定 | (ids: (string \| number)[]) |
| cancel | 取消选择 | - |
| close | 抽屉关闭 | - |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| open | 打开抽屉 | - |
| close | 关闭抽屉 | - |
| getSelectedItems | 获取已选门店列表 | - |

### StoreDialog StoreDialog 弹框门店选择器

StoreDialog 弹框门店选择器 弹框类型的省市维度门店选择器，以省/市为颗粒度多选，支持下钻查看具体门店列表。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue | 控制弹框显示（支持 v-model），使用 trigger prop 或 #trigger slot 时无需传入 | boolean | false |  |
| title | 弹框标题 | string | '选择省市范围' |  |
| defaultSelected | 初始已选城市/省份 code 数组（回显用），组件内部自动映射为完整选中项 | string[] | [] |  |
| trigger | 内置触发器类型，设置后由组件内部管理弹框显隐，无需外部 v-model | 'button' \| 'input' | undefined |  |
| triggerText | 触发按钮的文字，仅 trigger='button' 时有效 | string | '选择省市范围' |  |
| formatDisplay | 自定义 input 触发器的显示值格式化函数，仅 trigger='input' 时有效 | (items: SelectedItem[]) => string | undefined |  |
| width | 弹框宽度 | string \| number | '900px' |  |
| regionTreeConfig | 省市树接口配置，不传则使用内置 Mock 数据 | StoreDialogRegionTreeConfig | undefined |  |
| storeListConfig | 门店下钻列表接口配置，不传则使用内置 Mock 数据 | StoreDialogStoreListConfig | undefined |  |
| requestMode | 请求环境预设，不传则使用宿主应用默认请求实例 | RequestPresetMode | undefined |  |
| url | 省市树接口地址 | string | ✓ |  |
| method | 请求方式 | 'get' \| 'post' | - |  |
| transform | 响应数据转换函数，将接口返回值映射为 RegionNode[] | (res: unknown) => RegionNode[] | - |  |
| url | 门店下钻接口地址 | string | ✓ |  |
| method | 请求方式 | 'get' \| 'post' | - |  |
| ... | 共 17 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 弹框开关状态变化 | (value: boolean) |
| confirm | 用户点击「确定」，返回完整的已选省市数据 | (selected: SelectedItem[]) |
| cancel | 用户点击「取消」或关闭弹框 | - |

### StoreSelector 门店选择器

门店选择器 通用的门店选择器业务组件 维护提醒：该组件已过期，新页面请使用门店选择器V2。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model:visible | 弹窗显示状态(支持v-model:visible，如果传入则由外部控制显示) | boolean | - | undefined |
| selectedStoreList/v-model | 已选门店信息列表(v-model为双向绑定) | any[] | - | [] |
| checkedOrgList | 已勾选组织信息列表 | any[] | - | [] |
| triggerType | 触发节点类型 | string | button / input | ‘button’ |
| triggerTitle | 触发节点文案 | string | - | ‘选择门店’ |
| dialogWidth | 容器宽度基准值（当前 drawer 场景会作为抽屉宽度，单位 px，会自动限制不超过视口宽度） | number | - | 1360 |
| mainHeight | 主内容区高度（px），不传时按容器剩余空间自适应 | number | - | undefined |
| orgPanelWidth | 组织面板宽度（输入和树区域，px） | number | - | 240 |
| orgTreeHeight | 组织树高度（px） | number | - | 590 |
| orgSearchPlaceholder | 组织搜索占位文案 | string | - | 请输入区域名称 |
| selectedPanelWidth | 已选区域宽度（px） | number | - | 320 |
| tabs | 左侧内容区 tabs 配置；不传时不展示 tabs | StoreSelectorTabItem[] | - | undefined |
| searchConfig | 搜索项配置（透传给待选表格） | SearchConfigVo[] | - | 内置门店搜索项 |
| tableColumns | 表格列配置（待选/已选共用） | TableColumnsVo[] | - | 内置门店列 |
| rowKey | 门店唯一标识字段 | string | - | storeId |
| ... | 共 28 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 点击确定按钮触发的事件 | { orgs: IOrgInfo[]; stores: IStoreInfo[] } |
| cancel | 点击取消按钮触发的事件 | - |
| selection-change | 选择过程实时变化（组织/门店） | { orgs: IOrgInfo[]; stores: IStoreInfo[]; source: 'init' \| 'user' \| 'restore' \| 'clear' \| 'reset' } |
| update:modelValue | v-model 绑定值更新（门店数组） | IStoreInfo[] |
| update:visible | v-model:visible 绑定值更新（弹窗显隐） | boolean |
| update:activeTab | v-model:activeTab 绑定值更新（左侧 tab） | string \| number |

**插槽 Slot**

| name | 说明 |
|------|------|
| trigger | 触发节点插槽 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| open | 打开选择器弹窗 | — |
| close | 关闭选择器弹窗 | — |
| reset | 清空当前选择与检索状态 | — |

### GoodsSelector 商品选择器 GoodsSelector

商品选择器 GoodsSelector 业务商品选择组件，提供三种交互模式： 模式 适用场景 交互 simple（默认） 快速选择、列表信息不宜过多 弹窗 + 穿梭双栏，滚动分页 advanced 精确、复杂、沉浸式选型 侧边抽屉 + 表格筛选分页 + 右侧已选卡片 select 轻量内联场景，无需弹窗 内联下拉选择器，滚动加载，支持单/多选 示例 简易选择器（simple） 分页查询接口 /item/api/item/component/pagingSpecQuery 请先登录 demo 站点 resourceCode： 添加商品（简单） 展开代码 复制代码 高级选择器（advanced） 

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| title | 弹窗 / 抽屉标题（select 模式无弹窗，不使用此参数） | string | 添加商品 |  |
| mode | simple 弹窗穿梭；advanced 抽屉表格；select 内联下拉 | simple \| advanced \| select | simple |  |
| triggerType | 触发方式：button / 只读 input（select 模式无触发器） | string | button |  |
| triggerText | 触发文案；input 未选择时作为 placeholder | string | 选择商品 |  |
| v-model:visible | 弹窗 / 抽屉显隐（可选，不传则内部维护；select 模式不使用） | boolean | — |  |
| drawerSize | advanced 下 BusyDrawer 宽度 | string \| number | 92% |  |
| pageSize | 每页条数 | number | 20 |  |
| extraFields | 扩展字段：key 为接口字段名，value 为中文 label；simple 在卡片固定区下方；advanced 在「商品信息」列；空值整行不渲染 | Record<string, string> | {} |  |
| advancedExtraColumns | advanced 在默认三列之后追加的 BusyTable 列 | TableColumnsVo[] | [] |  |
| requestMode | MSE 签名环境预设；simple 走 pagingSpecQuery，advanced / select 走 pagingQuery 及筛选字典接口 | RequestPresetMode | — |  |
| requestParams | 额外入参：sellPurchase（0 售 / 1 采 / 2 售采 / 3 非采非售） | object | {} |  |
| requestConfig | axios 补充配置 | AxiosRequestConfig | — |  |
| resourceCode | MSE 资源码，透传为请求头 permissionCode，用于匹配 X-Operate-Info；业务方必传当前操作资源码，未传时请求层兜底 portalMainGoodsSelector | string | — |  |
| initialSelectedItems | 初始已选商品列表；advanced / select 生效（simple 暂不支持）；传入 itemCode 字符串数组或对象数组；>100 条自动分段请求 | string[] \| GoodsSelectorInitialSelectedItem[] | [] |  |
| selectMultiple | select 模式是否多选 | boolean | false |  |
| ... | 共 16 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 点击确定 | GoodsSelectorConfirmPayload：total、keys（itemCode 列表）、items（接口原始记录） |
| cancel | 点击取消或关闭（未确认的中间勾选不写入已确认态） | — |

### GoodsSelectorV2 GoodsSelectorV2 商品选择器 V2

GoodsSelectorV2 商品选择器 V2 基于抽屉的新版商品选择器组件，支持自定义搜索、表格列和已选商品渲染。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| visible | 控制抽屉显示 | boolean | false |  |
| title | 抽屉标题 | string | '添加商品' |  |
| drawerWidth | 抽屉宽度 | string | '80%' |  |
| searchConfig | 搜索表单配置 | SearchFieldConfig[] | [] |  |
| tableColumns | 表格列配置 | TableColumnConfig[] | [] |  |
| rowKey | 数据唯一标识字段名 | string | 'id' |  |
| keyField | 已选商品列表唯一标识字段名（已废弃） | string | undefined |  |
| selectedConfig | 已选商品渲染配置（已废弃） | SelectedItemConfig \| string | undefined |  |
| selectedGoods | 已选商品列表 | GoodsItem[] | [] |  |
| fetchList | 获取商品列表的方法 | Function | - |  |
| pageSize | 每页显示数量 | number | 10 |  |
| pageSizes | 分页大小选项 | number[] | [10, 20, 50, 100] |  |
| searchLabelWidth | 搜索表单 label 宽度 | string | '68px' |  |
| selectedPanelWidth | 右侧已选区域宽度 | string | '304px' |  |
| maxSelectCount | 最大可选数量限制 | number | - |  |
| ... | 共 36 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:visible | visible 状态变化 | (visible: boolean) |
| confirm | 确认选择 | (selectedGoods: any[]) |
| cancel | 取消选择 | - |
| close | 抽屉关闭 | - |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| open | 打开抽屉 | - |
| close | 关闭抽屉 | - |
| getSelectedGoods | 获取已选商品 | - |

### UserSelectorV2 人员选择器V2

人员选择器V2 基于 dialog 容器的弹窗人员选择器，内置组织树、组织搜索、人员列表三种请求。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值 | Array | - | [] |
| mode | 环境模式 | string | - | ‘busyming-dev’ |
| selectionMode | 选择模式 | string | single / multiple | ‘multiple’ |
| treeProps | 树节点字段映射（展示配置） | TreeFieldProps | - | 见下方默认值 |
| rowKey | 表格行唯一标识字段（展示配置） | string | - | ‘id’ |
| orgTreeRequest | 组织树数据源 · 入参管道 | (node, props) => RequestArgs | - | 内置默认实现 |
| orgTreeResponse | 组织树数据源 · 出参管道 | (resp, props) => any[] | - | 内置默认实现 |
| orgSearchRequest | 组织搜索数据源 · 入参管道 | (keyword, props) => RequestArgs | - | 内置默认实现 |
| orgSearchResponse | 组织搜索数据源 · 出参管道 | (resp, props) => any[] | - | 内置默认实现 |
| userListRequest | 人员列表数据源 · 入参管道 | (input, props) => RequestArgs | - | 内置默认实现 |
| userListResponse | 人员列表数据源 · 出参管道 | (resp, props) => { data, total } | - | 内置默认实现 |
| value | 节点唯一标识字段 | string | 是 | ‘orgId’ |
| label | 节点展示字段 | string | 是 | ‘orgName’ |
| children | 子节点字段 | string | 是 | ‘children’ |
| isLeaf | 叶子节点标记字段 | string | 否 | ‘isLeaf’ |
| ... | 共 21 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 绑定值更新时触发 | (value: any[]) |
| change | 选中结果变更时触发 | (value: any[]) |

### UserSelector 人员选择器

人员选择器 通用人员选择器业务组件 维护提醒：该组件已过期，新页面请使用人员选择器V2。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model:visible | 弹窗显示状态（如果传入则由外部控制显隐） | boolean | - | undefined |
| selectedUsers / v-model | 已选用户列表（v-model 为双向绑定） | any[] | - | [] |
| v-model:brand | 搜索区默认所属品牌 | string | - | '' |
| checkedOrgs | 已选组织信息列表 | any[] | - | — |
| checkedJobPosts | 已选岗位列表 | any[] | - | — |
| triggerType | 触发节点类型 | string | button / input | 'button' |
| triggerTitle | 触发节点标题 | string | - | '选择用户' |
| placeholder | 占位符 | string | - | '选择用户' |
| multiple | 是否多选 | boolean | true / false | true |
| disabled | 是否禁用 | boolean | true / false | false |
| disabledBrand | 是否禁用品牌筛选 | boolean | true / false | false |
| requestOrgList | 自定义获取组织树的方法 | Function | - | 内部默认实现 |
| requestUserList | 自定义获取用户分页列表的方法 | Function | - | 内部默认实现 |
| userListRequestConfig | 默认用户列表请求的 axios 配置，仅在未传 requestUserList 时生效 | object | - | undefined |
| userListQueryTransform | 默认用户列表请求的查询参数转换函数，仅在未传 requestUserList 时生效 | Function | - | undefined |
| ... | 共 23 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 点击确认按钮时触发 | selectedInfo: { orgs, jobPosts, users } |
| cancel | 点击取消按钮时触发 | - |
| update:modelValue | v-model 绑定值更新 | IUserInfo[] |
| update:visible | v-model:visible 绑定值更新 | boolean |
| update:brand | v-model:brand 绑定值更新 | string |

**插槽 Slot**

| name | 说明 |
|------|------|
| trigger | 触发节点插槽 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| - | - | — |

### SimpleUserSelector 简易版人员选择器

简易版人员选择器 通用简易版人员选择器 维护提醒：该组件已过期，新页面请使用人员选择器V2。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| selectedUsers/v-model | 已选成员信息列表 | { userId, [x]: any }[] | - | [] |
| showSelectedLimit | 已选成员显示限制 | number | - | 2 |
| multiple | 多选/单选 | boolean | true / false | true |
| disabled | 是否禁用 | boolean | true / false | — |
| maxSelect | 最大选择数量 | number | - | Infinity |
| placeholder | 占位符 | string | - | 请选择 |
| reqUserListUrl | 请求人员列表接口地址 | string | - | ‘/gateway/personnel/user/page’ |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 当点击确认按钮时触发的事件 | selectedUsers: {userId,[x]: any}[] |
| cancel | 当点击取消按钮时触发的事件 | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| 默认插槽 | 默认插槽说明 |

### DesensitizeView 脱敏信息查看明文 DesensitizeView

脱敏信息查看明文 DesensitizeView 业务脱敏信息查看明文组件，用于展示脱敏内容并提供点击查看明文的能力。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| data | 行数据对象，包含脱敏字段和 x-mask-info 等（必传） | DesensitizeViewData | — |  |
| field | data 中要展示/解密的字段名（必传） | string | — |  |
| hasPermission | 是否有查看明文权限（业务侧传入）；小眼睛最终显示还需全局 resources 中 permissionCode 对应资源的 action === 'unmask' | boolean | false |  |
| permissionCode | MSE 资源码，透传为请求头 permissionCode，用于匹配 X-Operate-Info（必传） | string | — |  |
| requestMode | MSE 签名环境预设，不传时自动使用全局 setBusinessRequestContext 中的 requestMode | RequestPresetMode | — |  |
| requestConfig | axios 补充配置 | AxiosRequestConfig | — |  |
| default | 脱敏/明文内容显示区域 | { text: string, isPlaintext: boolean } |  |  |
| eyeIcon | 小眼睛图标区域 | { visible: boolean, loading: boolean } |  |  |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| plaintextLoad | 明文加载成功时触发 | (plaintext: string) |
| plaintextError | 明文加载失败时触发 | (error: unknown) |

### OrgSelector 组织选择器

组织选择器 组织架构选择器，基于 el-tree-select 封装，支持懒加载、多选、父子互斥及远程搜索。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue | 当前选中值，单选为对象或 null，多选为对象数组 | any \| any[] \| null | null | 否 |
| multiple | 是否多选模式 | boolean | false | 否 |
| parentChildExclusive | 是否启用父子节点选择互斥 | boolean | false | 否 |
| showNodeActions | 是否在非叶子节点 hover 时显示「全选 / 反选」按钮 | boolean | false | 否 |
| datasource | 数据源配置（详见下表） | OrgSelectorDatasource | - | 是 |
| treeOptions | 树结构与字段映射配置（详见下表） | OrgSelectorTreeOptions | {} | 否 |
| change | 选中值变化时触发 | [value] | value：当前选中值（单选为对象或 null，多选为对象数组）。emit 的对象会保留节点上除 children 与内部标记以外的所有字段（如 orgId / orgName / isLeaf 等）；label 为原始名称，不含层级路径 |  |
| update:modelValue | v-model 更新事件 | [value] | 同 change |  |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| getNodesWithChildren | 获取当前已加载的所有非叶子节点（带子节点关系）的 key | - |
| selectAllChildren | 全选指定节点下所有子孙节点（互斥模式下会取消该节点自身和其祖先节点） | data: any |
| deselectAllChildren | 反选指定节点下所有子孙节点 | data: any |
| treeSelectRef | 内部 el-tree-select 实例引用（高级场景使用） | - |

### AreaSelector 省市区选择器

省市区选择器 基于 BusyCascader 封装的全国省市区选择器，内置「行政区划树查询」接口。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 选中项绑定值（节点 code 路径） | AreaCascaderValue | — |  |
| disabled | 是否禁用 | boolean | false |  |
| placeholder | 占位文本 | string | '请选择' |  |
| multiple | 是否多选 | boolean | false |  |
| needAll | 是否显示「全国」选项（仅默认路径） | boolean | false |  |
| checkStrictly | 父子节点是否不互相关联（可选任意一级） | boolean | true |  |
| width | 选择器宽度，支持数字（px）、字符串（如 '200px'、'50%'） | number \| string | 自适应父容器 |  |
| isVisibleFetch | 是否在下拉展开时才请求数据 | boolean | false |  |
| levelDepth | 行政区划层级深度 0~4（仅默认路径） | number | 3 |  |
| requestAreaList | 自定义区域列表请求；传入后跳过内置接口及下方请求 props | () => Promise<AreaOption[]> | — |  |
| areaListRequestConfig | 内置请求的 axios 补充配置，见上文 areaListRequestConfig | AxiosRequestConfig | — |  |
| areaListQueryTransform | 内置请求 body 转换（仅默认路径） | (query) => unknown | — |  |
| areaListResponseTransform | 内置响应归一化为 AreaOption[]（仅默认路径） | (response) => AreaOption[] | — |  |
| requestMode | 请求环境预设，见上文 requestMode | RequestPresetMode | 'hnlshm-test' |  |
| getRef | 获取内部 Cascader ref 的回调 | (ref) => void | — |  |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 选中项变化 | AreaCascaderValue |
| request-error | 内置或自定义请求失败 | error: unknown |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义级联节点内容，透传自 BusyCascader |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| getCheckedNodes | 获取当前选中节点数组 | (leafOnly?: boolean) => any[] |
| clearCheckedNodes | 清空选中节点 | () => void |
| refresh | 重新拉取区域数据 | () => Promise<void> |
| togglePopperVisible | 切换下拉显示 | (visible?: boolean) => void |
| focus | 获取焦点 | () => void |
| blur | 失去焦点 | () => void |

### BusySelector 通用选择器

通用选择器 通用选择器弹窗组件，结合输入框、弹窗和表格，支持单选、多选、多 Tab 以及树状表格场景。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值 | unknown | - | - |
| model-label | 输入框展示文本（外部传入） | string / string[] | - | - |
| show-code-in-label | 输入框和已选摘要是否按 name(code) 展示 | boolean | - | false |
| selected-tab-key | 当前选中的 tab key | string / number | - | - |
| config | 选择器配置 | BusySelectorSingleConfig / BusySelectorSingleConfig[] | - | - |
| container-type | 外层容器类型 | ‘dialog’ / ‘drawer’ / ‘popover’ | - | ‘dialog’ |
| container-props | 外层容器透传属性 | Record<string, unknown> | - | - |
| multiple | 是否多选 | boolean | - | false |
| disabled | 是否禁用输入框触发 | boolean | - | false |
| init-search-params | 初始搜索参数，只参与请求 | Record<string, unknown> | - | - |
| search-params | 搜索表单参数，同时参与回显与请求 | Record<string, unknown> | - | - |
| request | 全局请求方法 | (searchParams, context) => Promise | - | - |
| get-select-rows | 根据值获取选中行数据 | (modelValue, searchParams) => Promise | - | - |
| key | 配置唯一标识 | string | - | - |
| tabProps | 页签信息（多 tab 场景） | BusyTabItem | - | - |
| ... | 共 29 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 确认选择时触发 | (payload: BusySelectorConfirmPayload) |
| select | 选择变化时触发 | (payload: BusySelectorConfirmPayload) |
| clear | 清空时触发 | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| default | 自定义弹窗主体内容。传入后仅渲染默认插槽，content-left / content-right 不生效；默认插槽-only 场景可不传 config |
| content-left | 弹窗内容左侧自定义区域 |
| content-right | 弹窗内容右侧自定义区域 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| open | 打开弹窗 | - |
| close | 关闭弹窗 | - |
| reload | 刷新列表 | - |
| getSelectedRows | 获取当前选中行 | - |

### WarZoneSelector 战区选择

战区选择 用于战区 / 省区 / 城市等层级地域选择，支持多选与单选。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 选中值；多选返回数组，单选返回单个值 | string \| number \| Array<string \| number> | [] | 否 |
| options | 本地模式树形数据源；dataSource="local" 时作为数据来源 | WarZoneOption[] | [] | 本地模式必填 |
| placeholder | 未选择时占位文案 | string | 请选择 | 否 |
| disabled | 是否禁用 | boolean | false | 否 |
| labelKey | 标签字段名 | string | orgName | 否 |
| valueKey | 值字段名 | string | orgId | 否 |
| childrenKey | 子节点字段名 | string | children | 否 |
| multiple | 是否多选；true 多选，false 单选 | boolean | true | 否 |
| collapseTags | 是否折叠已选标签 | boolean | true | 否 |
| maxCollapseTags | 折叠前最多展示标签数 | number | 3 | 否 |
| submitNodeMode | 对外提交节点模式；checked 返回真实勾选节点，leaf 在多选时会从当前叶子值补齐父级 / 根节点链 | 'checked' \| 'leaf' | checked | 否 |
| dataSource | 数据来源模式；remote 远程请求，local 本地 options | 'remote' \| 'local' | remote | 否 |
| requestMode | 远程请求预设模式；推荐由 setBusinessRequestContext 设置，本 prop 在全局未设置时兜底。可选值：busyming-dev / busyming-test / busyming-pre / busyming-uat / busyming-prod | RequestPresetMode | - | 远程模式需能解析到 mode（全局或 prop） |
| requestParams | 远程请求参数；远程模式下 userId 必传，resourceId 为接口业务参数；token / resources 不再逐组件透传 | RequestParams | { userId: 0, resourceId: 0 } | 远程模式必填 |
| resourceCode | 资源编码，由组件直传并桥接为请求头中的 permissionCode | string | '' | 依赖资源权限的远程模式建议传 |
| ... | 共 17 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 选中值变化时触发 | (value) |
| change | 选中值变化时触发，并返回选中节点摘要和原始对象 | (value, selectedOptions) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| open | 打开面板 | - |
| close | 关闭面板 | - |
| clear | 清空选中值 | - |
| getSelectedOptions | 获取当前选中的节点摘要（label/value）及原始对象 | - |

### SimpleUserSelectorV2 简易人员选择器

简易人员选择器 基于 el-input-tag + el-popover 的轻量人员选择器（壳层 + 数据面板分层）：input 只负责触发面板与展示已选 tag；popover 内的数据面板通过「数据源管道」（optionsRequest 入参管道 + 统一 request + optionsResponse 出参管道）动态加载 options，并内置滚动翻页（每页 20 条，滚动到底自动加载下一页并累计渲染）、页码/总数展示、已加载列表全选能力。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| model-value / v-model | 绑定值：多选为数组、单选为单值；支持 primitive（如 1、'a'）或 OptionItem（如 { id, nickName }），primitive 会在 options 命中后自动替换为完整对象 | OptionItem[] \| OptionItem \| Array<string \| number> \| string \| number | — | undefined |
| multiple | 是否多选 | boolean | — | false |
| mode | 请求预设环境 | string | RequestPresetMode | 'busyming-dev' |
| label-key | option 展示字段（tag 文案与选项 label 兜底） | string | — | 'nickName' |
| value-key | option 取值（唯一值）字段 | string | — | 'id' |
| options-request | 数据源入参管道：(input, props) => RequestArgs，input 含 keyword / pageNo / pageSize | OptionsRequest | — | 内置默认实现 |
| options-response | 数据源出参管道：(resp, props) => OptionItem[] \| { list, total }（返回 total 可精确判定分页结束） | OptionsResponse | — | 内置默认实现 |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 绑定值更新（v-model） | 更新后的值 |
| change | 选中值变化时触发 | 更新后的值 |

## 已有未纳入目录

### DynamicForm 动态表单

动态表单 根据schmea自动生成动态表单 （开发中：🚧 🚧 🚧） 基础用法 账号： 姓名： 网址： 域名： 长文本示例： 密码： 确认密码： 数量： 自定义状态： 留言： 区域： 请选择 区域（多选）： 请选择区域（多选） 分页选择： 开关： 禁用开关： 单选： 很忙 一鸣 多选： 很忙 一鸣 鸣鸣很忙集团 日期： - 时间： - 上传图片： 组织架构： 展开代码 复制代码 属性 prop 参数 说明 类型 可选值 默认值 size 尺寸 string medium / small / mini — 事件 event 事件名称 说明 回调参数 change 当绑定值变化时触发的事件 更新后的

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| size | 尺寸 | string | medium / small / mini | — |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 当绑定值变化时触发的事件 | 更新后的值 |

**插槽 Slot**

| name | 说明 |
|------|------|
| 默认插槽 | 默认插槽说明 |
| foo | 具名插槽说明 |
| bar | 作用域插槽说明，作用域插槽参数为 { paramOne, paramTwo } |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focus | 使 input 获取焦点 | — |

### PreviewImg 图片预览

图片预览 图片预览组件 基础用法 展开代码 复制代码 属性 prop 参数 说明 类型 可选值 默认值 url-list 用于预览的图片链接列表 string[] - [] z-index 预览时遮罩层的 z-index number - - initial-index 初始预览图像索引，小于 url-list 的长度 number - 0 infinite 是否可以无限循环预览 boolean true / false true hide-on-click-modal 是否可以通过点击遮罩层关闭预览 boolean true / false true teleported image 自身是

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| url-list | 用于预览的图片链接列表 | string[] | - | [] |
| z-index | 预览时遮罩层的 z-index | number | - | - |
| initial-index | 初始预览图像索引，小于 url-list 的长度 | number | - | 0 |
| infinite | 是否可以无限循环预览 | boolean | true / false | true |
| hide-on-click-modal | 是否可以通过点击遮罩层关闭预览 | boolean | true / false | true |
| teleported | image 自身是否插入至 body 元素上。 嵌套的父元素属性会发生修改时应该将此属性设置为 true | boolean | true / false | false |
| zoom-rate | 图像查看器缩放事件的缩放速率 | number | 1.2 |  |
| min-scale | 图像查看器缩放事件的最小缩放比例 | number | - | 0.2 |
| max-scale | 图像查看器缩放事件的最大缩放比例 | number | - | 7 |
| close-on-press-escape | 是否可以通过按下 ESC 关闭 Image Viewer | boolean | true / false | true |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| close | 当点击 X 按钮或者在hide-on-click-modal为 true 时点击遮罩层时触发 | () => void |
| switch | 切换图像时触发。 | (index: number) => void |
| close | 旋转图像时触发。 | (deg: number) => void |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| setActiveItem | 手动切换图片 | (index: number) => void |

### PreviewVideo 视频预览

视频预览 基础用法 预览 展开代码 复制代码 属性 prop 参数 说明 类型 可选值 默认值 src 视频文件地址 string - — name 视频文件名 string - — 事件 event 事件名称 说明 回调参数 插槽 slot name 说明 方法 Methods 方法名 说明 参数

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| src | 视频文件地址 | string | - | — |
| name | 视频文件名 | string | - | — |

### PreviewPDF 预览pdf文件

预览pdf文件 基础用法 预览 展开代码 复制代码 属性 prop 参数 说明 类型 可选值 默认值 src 文件地址 string - — name 文件名 string - — useLocalPreview 是否使用本地预览 boolean - true 事件 event 事件名称 说明 回调参数 插槽 slot name 说明 方法 Methods 方法名 说明 参数

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| src | 文件地址 | string | - | — |
| name | 文件名 | string | - | — |
| useLocalPreview | 是否使用本地预览 | boolean | - | true |

### Title 标题组件

标题组件 通用的标题组件 基础用法 很忙前端 展开代码 复制代码 slot用法 slot标题 展开代码 复制代码 属性 prop 参数 说明 类型 可选值 默认值 title 标题 string - ‘’ showLine 是否显示分割线 boolean - true 事件 event 事件名称 说明 回调参数 ------------- ----------------------- ---------- 插槽 slot name 说明 默认插槽 默认插槽说明 方法 Methods 方法名 说明 参数 ---- ---- ----

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| title | 标题 | string | - | ‘’ |
| showLine | 是否显示分割线 | boolean | - | true |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| ------------- | ----------------------- | ---------- |

**插槽 Slot**

| name | 说明 |
|------|------|
| 默认插槽 | 默认插槽说明 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| ---- | ---- | ---- |

### Tooltip 文字提示

文字提示 可自定义行数、tooltip浮层最大宽高、根据所在容器宽度自适应是否悬浮显示，超出长度自动省略。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| content | 提示文字内容 | string | - | ‘’ |
| placement | Tooltip 出现的位置 | string | top / bottom / left / right 等 | ‘top’ |
| line | 显示的最大行数 | number / string | - | 1 |
| width | 容器宽度 | number / string | - | ‘’ |
| lineHeight | 行高 | number / string | - | ‘23px’ |
| teleported | 是否将 Tooltip 渲染到 body 上 | boolean | - | true |
| rawContent | 是否启用原始 HTML 内容渲染 | boolean | - | false |
| tooltip-max-width | tooltip 浮层最大宽度 | number / string | - | ‘500px’ |
| tooltip-max-height | tooltip 浮层最大高度 | number / string | - | ‘400px’ |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| show | 当 Tooltip 显示时触发 | - |
| hide | 当 Tooltip 隐藏时触发 | - |

**插槽 Slot**

| name | 说明 |
|------|------|
| 默认插槽 | 需要显示省略和提示的文字内容 |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| handleShow | 手动触发显示 Tooltip | - |
| handleHide | 手动触发隐藏 Tooltip | - |

### DragList 拖拽列表

拖拽列表 组件内元素可拖拽调整顺序（单容器排序）。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue / v-model | 列表数据 | array | — | [] |
| itemKey | item 唯一 key。string 取 item[itemKey]；function 需对同一 item 返回稳定值 | string / function | — | — |
| disabled | 禁用拖拽；为 true 时项可点击并触发 item-click | boolean | — | false |
| labelKey | 默认项展示字段（未使用 item 插槽时） | string | — | 'name' |
| modelValue / v-model | 列表数据 | array | [] |  |
| itemKey | item 唯一 key | string / function | — |  |
| title | 标题 | string | '' |  |
| adjustText | 「调整排序」按钮文案 | string | '调整排序' |  |
| cancelText | 「取消」按钮文案 | string | '取消' |  |
| saveText | 「保存」按钮文案 | string | '保存' |  |
| labelKey | 默认项展示字段（透传 DragList） | string | 'name' |  |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| change | 排序变化时触发 | { oldIndex, newIndex, item, list } |
| drag-start | 拖拽开始 | { index, item } |
| drag-end | 拖拽结束 | { oldIndex, newIndex, item } |
| item-click | 项点击（disabled 为 true 时生效，发生拖拽后不触发） | { index, item } |
| update:modelValue | 保存时更新列表 | 排序后的列表 |
| save | 保存时触发 | 排序后的列表 |
| cancel | 取消时触发 | — |
| item-click | 项点击（非编辑态时生效，透传自 DragList） | { index, item } |

**插槽 Slot**

| name | 说明 |
|------|------|
| item | 自定义每一项渲染，参数为 { item, index, dragging } |
| title | 自定义标题区域 |
| item | 自定义 item 渲染，透传给 DragList |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| — | — | — |

### MixinsDialogSelector 混合弹窗选择器

混合弹窗选择器 混合使用多数据源的弹窗选择器，支持 dialog / drawer / popover 多种容器类型，以及单选、多选模式。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| v-model | 绑定值 | Array | - | [] |
| mode | 环境模式 | string | - | ‘busyming-dev’ |
| selectionMode | 选择模式 | string | single / multiple | ‘multiple’ |
| containerType | 容器类型 | string | dialog / drawer / popover | ‘dialog’ |
| treeDatasourceConfig | 树组件数据源配置 | OrgDatasourceConfig | - | 见下方默认配置 |
| tableDatasourceConfig | 表格数据源配置 | TableDatasourceConfig | - | 见下方默认配置 |
| url | 用户列表分页接口地址 | string | 是 |  |
| queryParams | 接口固定查询参数 | Record<string, any> | 是 |  |
| rowKey | 行数据唯一标识字段名 | string | 是 |  |
| url | 树数据接口地址 | string | 是 |  |
| queryParams | 请求参数 | Record<string, any> | 是 |  |
| treeProps | 树节点字段映射 | object | 是 |  |
| treeProps.value | 节点唯一标识字段 | string | 是 |  |
| treeProps.label | 节点展示字段 | string | 是 |  |
| treeProps.children | 子节点字段 | string | 是 |  |
| ... | 共 18 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:modelValue | 绑定值更新时触发 | (value: any[]) |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| handleOpen | 打开选择器 | (hasPrefix?: boolean) |
| handleClose | 关闭选择器 | - |
| handleDestroy | 销毁选择器 | - |

### IconSelector 图标选择器

图标选择器 资源图标选择气泡卡片，支持从预置 iconfont 菜单图标中选择，或通过 busy-upload 上传自定义图标到 OSS。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| modelValue / v-model | 当前选中的图标值 | `string | null` |  |
| visible / v-model:visible | 气泡是否可见 | boolean | false |  |
| title | 气泡标题 | string | '选择资源图标' |  |
| popoverWidth | 气泡宽度 | number | 392 |  |
| placement | 气泡出现位置 | string | 'bottom-start' |  |
| teleported | 是否挂载到 body | boolean | true |  |
| popperClass | 自定义 popper class | string | '' |  |
| itemSize | 图标格子尺寸（px） | number | 36 |  |
| triggerSize | 触发器尺寸（px），不传时默认跟随 itemSize | number | 36 |  |
| iconSize | 预置图标渲染尺寸（px） | number | 20 |  |
| pageSize | 每页展示的预置图标数量（不含上传按钮） | number | 31 |  |
| columns | 图标网格列数 | number | 8 |  |
| ossDirName | OSS 上传目录名称 | string | 'busyUiIconSelector' |  |
| uploadMode | 上传模式 | 'policy' \| 'sts' | 'policy' |  |
| customOssPolicyUrl | 自定义 OSS Policy URL | string | '' |  |
| ... | 共 19 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| confirm | 点击确定且已选择图标时触发 | (value: string) |
| cancel | 点击取消或关闭气泡时触发 | — |
| open | 气泡打开时触发 | — |
| closed | 气泡关闭后触发 | — |
| clear | 点击触发器右上角删除按钮时触发 | — |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| open | 打开气泡 | — |
| close | 关闭气泡 | — |

### PortalNavSearchPanel PortalNavSearchPanel 门户导航搜索面板

PortalNavSearchPanel 门户导航搜索面板 Portal 顶栏浮动搜索面板，支持搜索历史、结果卡片与热词。

**属性 Prop**

| 参数 | 说明 | 类型 | 可选值 | 默认值 |
|------|------|------|--------|--------|
| searchKeyword | 搜索关键词（支持 v-model） | string | '' |  |
| searchResults | 搜索匹配结果 | PortalNavSearchResult[] | [] |  |
| searchHistory | 搜索历史 | string[] | [] |  |
| searchHotwords | 搜索热词 | string[] | [] |  |
| placeholder | 搜索框占位文本 | string | '搜索' |  |
| emptyDescription | 无结果提示文案 | string | '未找到相关结果' |  |
| resultsSectionTitle | 结果区块标题 | string | '结果' |  |
| historyTitle | 搜索历史标题 | string | '搜索历史' |  |
| showHotwords | 是否展示搜索热词 | boolean | false |  |
| itemUnavailable | 搜索项不可用判断函数 | (item) => boolean | 内置 available 判断 |  |
| id | 唯一标识 | string \| number |  |  |
| title | 标题 | string |  |  |
| description | 描述/副标题 | string |  |  |
| icon | 图标地址 | string |  |  |
| disabled | 是否不可用 | boolean |  |  |
| ... | 共 16 个属性 | | | |

**事件 Event**

| 事件名称 | 说明 | 回调参数 |
|----------|------|----------|
| update:searchKeyword | 搜索关键词变化 | (value: string) |
| overlay-click | 点击遮罩关闭 | () |
| search-enter | 回车搜索 | () |
| history-select | 选中历史/热词 | (keyword: string) |
| result-select | 选中搜索结果 | (item: PortalNavSearchResult) |
| clear-history | 清空搜索历史 | () |

**方法 Methods**

| 方法名 | 说明 | 参数 |
|--------|------|------|
| focusInput | 聚焦搜索输入框 |  |
