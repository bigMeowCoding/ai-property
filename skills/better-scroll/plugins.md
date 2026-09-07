# better-scroll v2 插件参考

按需安装对应包并在模块顶层注册一次：`BScroll.use(插件类)`。注册后插件配置项与实例方法通过声明合并获得类型提示。

## 速查表

| 插件 | 包名 | 启用配置 | 典型场景 |
| --- | --- | --- | --- |
| 上拉加载 | @better-scroll/pull-up | `pullUpLoad: true \| { threshold }` | 列表加载更多 |
| 下拉刷新 | @better-scroll/pull-down | `pullDownRefresh: true \| { threshold, stop }` | 下拉刷新 |
| 滚轮选择 | @better-scroll/wheel | `wheel: true \| { ... }` | picker 选择器 |
| 轮播 / 分页滑动 | @better-scroll/slide | `slide: true \| { ... }` | banner、全屏分页 |
| 滚动条 | @better-scroll/scrollbar | `scrollbar: true \| { fade, interactive }` | PC 端滚动条 |
| 无限列表 | @better-scroll/infinity | `infinity: { fetch, render, createTombstone }` | 超长列表虚拟化 |
| 嵌套滚动 | @better-scroll/nested-scroll | `nestedScroll: true \| { groupId }` | 多层嵌套联动 |
| DOM 监听 | @better-scroll/observe-dom | `observeDOM: true` | 内容高度自动感知 |
| 图片监听 | @better-scroll/observe-image | `observeImage: true \| { debounceTime }` | 图片加载后自动 refresh |
| 鼠标滚轮 | @better-scroll/mouse-wheel | `mouseWheel: true \| { speed, invert, easeTime }` | PC 滚轮支持 |
| 缩放 | @better-scroll/zoom | `zoom: true \| { start, min, max }` | 图片双指缩放 |
| 自由拖动 | @better-scroll/movable | `movable: true`（配合 zoom） | 缩放后拖动查看 |
| 联动指示器 | @better-scroll/indicators | nested-scroll 联动进度 | 联动定位条 |

## pull-up（上拉加载）

- 事件：`pullingUp`
- 方法：`finishPullUp()`、`openPullUp(config?)`、`closePullUp()`、`autoPullUpLoad()`
- 要点：回调中必须 `finishPullUp()`（放 finally），否则只能触发一次；数据追加渲染后 `refresh()`。
- 终点陷阱：`finishPullUp()` 与 `refresh()`（contentChanged）都会重新武装 watcher，`closePullUp()` 不构成「不再触发」的硬保证；到达分页终点后以页面 `hasMore` ref 硬闸拒止（守卫分支调 `closePullUp()`，禁用 `finishPullUp()`），`openPullUp(config)` 恢复时必须显式回传配置（无参会重置 `threshold` 为 0）。

## pull-down（下拉刷新）

- 配置：`{ threshold: 90, stop: 40 }`（threshold 触发距离，stop 回弹停留位置）
- 事件：`pullingDown`
- 方法：`finishPullDown()`、`openPullDown(config?)`、`closePullDown()`、`autoPullDownRefresh()`

## wheel（滚轮选择）

- 配置：`{ selectedIndex: 0, rotate: 25, adjustTime: 400, wheelWrapperClass, wheelItemClass }`
- 事件：`scrollEnd`（滚动停止）后用 `getSelectedIndex()` 取选中下标
- 方法：`wheelTo(index)`、`getSelectedIndex()`
- 要点：每一项必须等高且固定；wrapper 高度 = 项高 × 可见行数；曲面弧度由 `rotate` 控制。

## slide（轮播 / 分页）

- 配置：`{ loop: true, threshold: 0.3, speed: 400, autoplay: false, interval: 3000, listeningFlick: true }`
- 结构：content 内每个直接子元素是一页
- 事件：`slideWillChange`（即将切换，参数为页码）、`slidePageChanged`
- 方法：`goToPage(x, y, time?)`、`next(time?)`、`prev(time?)`、`getCurrentPage()`
- 要点：loop 模式会克隆首尾页，动态内容变化后需 `refresh()`。

## scrollbar / mouse-wheel（PC 场景）

- scrollbar 配置：`{ fade: true, interactive: false, scrollbarTrackClickable: true }`
- mouseWheel 配置：`{ speed: 20, invert: false, easeTime: 300, discreteTime: 400 }`
- 要点：PC 场景通常两者一起开。

## nested-scroll（嵌套滚动）

- 配置：内外层实例均开启 `nestedScroll: { groupId: '同一字符串' }`
- 要点：同 groupId 的实例自动协调滚动接管顺序；双层嵌套最稳，三层以上注意分组设计。

## observe-dom / observe-image（自动 refresh）

- `observeDOM: true`：MutationObserver 监听 content 子树变化，自动 refresh
- `observeImage: { debounceTime: 100 }`：图片 load 后自动 refresh
- 要点：能用「数据变化后在 useEffect 手动 refresh」覆盖的场景不必开插件，减少运行时开销。

## zoom / movable（缩放与拖动）

- zoom 配置：`{ start: 1, min: 1, max: 4 }`
- 事件：`zoomStart`、`zoomEnd`；方法：`zoomTo(scale, x, y)`
- 要点：movable 基于 zoom 的缩放能力实现放大后的自由拖动，图片预览场景两者搭配使用。

## infinity（超长列表）

- 配置：`{ fetch(count), render(item, dom), createTombstone() }`
- 要点：实现成本高，千级以内的列表优先用 pull-up 分页。

## 核心配置速查（Options 常用项）

| 配置 | 默认值 | 说明 |
| --- | --- | --- |
| scrollX / scrollY | false / true | 滚动方向 |
| click | false | 派发原生 click（模板已默认 true） |
| probeType | 0 | 0 不派发 scroll 事件；3 实时派发（含惯性、回弹） |
| bounce | true | 边缘回弹 |
| momentum | true | 惯性滚动 |
| eventPassthrough | '' | 'vertical' / 'horizontal'，该方向保留原生滚动 |
| preventDefault | true | 配合 preventDefaultException 放行表单控件 |
| directionLockThreshold | 5 | 方向锁定阈值（px） |
| bounceTime | 800 | 回弹动画时长（ms） |
| useTransition / useTransform | true / true | 低端机可关 useTransition 降级动画 |
| specifiedIndexAsContent | 0 | 指定第 N 个子元素为滚动内容 |
| bindToWrapper | false | 事件绑定到 wrapper 而非 window |
| disableMouse / disableTouch | - | 禁用某类输入 |

### `disable()` 与点击事件的边界

`bs.disable()` 是整个实例的交互开关，不是「只禁止滚动」。实例禁用后不再产生 better-scroll 合成 click；但 wrapper 上已安装的触摸处理仍可以取消浏览器默认行为，因此 wrapper 内的自定义按钮可能同时失去合成 click 和原生 click。

- 需要保持可点的面板 / 浮层放到 wrapper 同级或 Portal。
- 为局部面板锁定背景滚动时，优先让 wrapper 退场，面板收起后调 `refresh()`。
- `preventDefaultException` 用于放行 INPUT / TEXTAREA / BUTTON / SELECT 等原生控件，不用于为大块业务 DOM 打补丁。
