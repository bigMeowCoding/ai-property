---
name: better-scroll
description: Use when 在 React H5 中实现或排查 better-scroll v2 容器滚动、上下拉、滚轮选择、横向/嵌套滚动，以及点击失效、`disable()` 后控件不可点、`refresh()` 时机错误或 pull-up/pull-down 未复位等问题。
---

# BetterScroll 滚动方案

better-scroll v2 是基于 transform 的移动端滚动库（iscroll 系，兼容 PC），核心 + 插件架构。本技能提供选型决策、React 集成规范与可复制的模板代码。

## 选型决策（先做判断）

| 场景 | 方案 |
| --- | --- |
| 整页 window 滚动的无限加载 | 优先复用项目已有的整页滚动 Hook（如 `useScrollLoad`），不要引入 better-scroll |
| 常规选择器 / 轮播 / 下拉刷新（交互与 antd-mobile 默认一致） | antd-mobile 的 Picker、Swiper、PullToRefresh |
| 定高容器内滚动 + 惯性回弹手感 | better-scroll |
| 下拉刷新 + 上拉加载一体化、交互需定制 | better-scroll（pull-down + pull-up） |
| 滚轮选择器（自定义样式 / 多级联动） | better-scroll（wheel） |
| 横向惯性滑动、snap 分页 | better-scroll（scrollX / slide） |
| 嵌套滚动（如左右联动菜单） | better-scroll（nested-scroll） |
| 图片双指缩放、拖动预览 | better-scroll（zoom + movable） |

判定口诀：**滚动发生在定高容器内部且需要手势动效定制 → better-scroll；整页滚动或 antd-mobile 已覆盖的交互 → 不引入。**

## 安装

```bash
# 按需安装（推荐，控制包体积）
pnpm add @better-scroll/core @better-scroll/pull-up @better-scroll/pull-down

# 全量安装（包含全部插件）
pnpm add better-scroll
```

- 只使用 v2，v1 已停止维护。
- 按需安装时，插件必须在模块顶层注册一次：`BScroll.use(PullUp)`。

## 核心原理（结构硬性要求）

```html
<div class="wrapper">
  <!-- 必须有确定高度，overflow: hidden（初始化时自动设置） -->
  <div class="content">
    <!-- 默认滚动第一个子元素，其高度超过 wrapper 才能滚动 -->
    ...
  </div>
</div>
```

- wrapper 高度来源：`height: 100%`（要求父级链均有高度）或 flex 布局中 `flex: 1; min-height: 0`。
- v2.0.4+ 可用 `specifiedIndexAsContent` 指定第 N 个子元素作为滚动内容。
- 内容不足一屏时不可滚动；需要「始终可下拉」时给 content 加 `min-height: calc(100% + 1px)`。

## React 集成规范

1. 复制 [templates.md](templates.md) 中 useBScroll 代码到 `src/hooks/useBScroll.ts`，统一通过它创建实例。
2. 实例生命周期由 hook 管理：挂载后初始化，卸载时 destroy；React 18 StrictMode 双执行下 destroy 幂等，无需特殊处理。
3. **点击事件**：模板默认开启 `click: true`，否则容器内 onClick 全部失效。
4. **事件边界**：展开后仍需点击的筛选面板、弹层、工具栏放在 wrapper 同级或 Portal，不放在会被 `disable()` 的 wrapper 内。`disable()` 停止合成 click 但不等于撤销 touch `preventDefault`，可导致合成 / 原生 click 同时失效。
5. **锁定滚动**：局部面板展开时，优先让 wrapper 条件退场（如 `display: none`）并在收起后 `refresh()`；只有当 wrapper 内整体确实不再交互时才调 `disable()`。
6. **高度过期**：异步数据、图片加载导致内容高度变化后必须 `refresh()`（在数据变化的 useEffect 中调用）；也可启用 `observe-dom` / `observe-image` 插件自动处理。
7. **事件绑定**：依赖 hook 返回的 `bs` 实例 state，用 `bs.on` / `bs.off` 配对注册；回调中读取最新 state 需通过 ref（模板已示范）。
8. options 仅在初始化时读取一次，后续变更不生效；动态开关上拉 / 下拉用 `openPullUp` / `closePullUp` 等 API。
9. 滚动事件回调中不要 setState 后立刻读 state，使用函数式更新或 ref。

## 场景与模板速查

| 场景 | 直接使用 | 涉及插件 |
| --- | --- | --- |
| 下拉刷新 + 上拉加载列表 | [templates.md](templates.md) RefreshLoadList 节 | pull-down、pull-up |
| 滚轮选择器 | [templates.md](templates.md) WheelPicker 节 | wheel |
| 轮播焦点图 / 全屏分页滑动 | 见 [plugins.md](plugins.md) slide 节 | slide |
| 竖向页面内的横向分类滑动 | `scrollX: true` + `eventPassthrough: 'vertical'` | 无 |
| 嵌套滚动联动 | 见 [plugins.md](plugins.md) nested-scroll 节 | nested-scroll |
| 图片缩放预览 | 见 [plugins.md](plugins.md) zoom 节 | zoom、movable |

插件完整配置项、事件与方法清单见 [plugins.md](plugins.md)。

## 常见坑（排查清单）

1. **完全不能滚动**：① wrapper 无确定高度；② content 高度未超过 wrapper；③ 初始化时机过早（图片 / 数据未就绪，高度算错）→ 就绪后 `refresh()` 或用 observe-image 插件。
2. **容器内点击无效**：按顺序查三层——①未开启 `click: true`；②元素在已 `disable()` 的 wrapper 内，合成 click 停止但 touch 仍被 `preventDefault`；③原生输入控件未命中 `preventDefaultException`。局部业务面板优先移出 wrapper，不用扩大异常正则掩盖边界问题。
3. **下拉 / 上拉只能触发一次**：忘记在数据加载完成后调用 `finishPullDown()` / `finishPullUp()`（放 finally 中，失败也要复位）。
4. **没有更多数据**：`closePullUp()` 只是临时摘监听——`finishPullUp()` 与 `refresh()`（contentChanged）会重新武装 watcher，`pullingUp` 照常触发；终点拒止必须在回调入口加 `hasMore` ref 硬闸（命中即 `closePullUp()` 后 return，此分支禁用 `finishPullUp()`，否则恰好重新武装）。下拉刷新重置列表时用 `openPullUp(配置)` 恢复，必须显式回传配置——无参调用会把 `threshold` 重置为 0。
5. **滚动位置监听不触发**：`probeType` 默认 0 不派发 scroll 事件；监听位置（吸顶、回顶按钮）需 `probeType: 3`（有性能开销，非必要不开）。
6. **容器内有输入框无法聚焦**：配置 `preventDefaultException: { tagName: /^(INPUT|TEXTAREA|BUTTON|SELECT)$/ }`。
7. **嵌套滚动 / 横竖滑动冲突**：`directionLockThreshold: 5`；竖向页面内的横滚容器加 `eventPassthrough: 'vertical'`；多层嵌套用 nested-scroll 插件。
8. **App WebView 内下拉冲突**：App 原生下拉刷新与容器下拉二选一，不要叠加。

## 验证

- `pnpm check`（类型 + 测试）、`pnpm lint`。
- 交互元素跨 wrapper 边界时，组件测须断言 DOM 归属与锁定策略；不得用 jsdom 的 `fireEvent.click` 代替对真实触摸链的验证。
- 真机验证滚动惯性、回弹手感与容器内外点击（模拟器不可信）；App 内场景用 vConsole 辅助排查。
