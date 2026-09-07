# better-scroll React 模板

按需复制对应代码块到项目后调整。安装方式、插件注册与常见坑见 [SKILL.md](SKILL.md)。

## useBScroll（基础 Hook，复制到 `src/hooks/useBScroll.ts`）

所有场景模板都依赖它，必须最先复制。

```ts
import { useCallback, useEffect, useRef, useState } from 'react'
import BScroll from '@better-scroll/core'
import type { BScrollInstance, Options } from '@better-scroll/core'

/**
 * useBScroll 返回值
 */
export interface UseBScrollResult<E extends HTMLElement = HTMLDivElement> {
  /** 绑定到滚动容器 wrapper 的 ref */
  wrapperRef: React.RefObject<E>
  /** BScroll 实例（初始化完成后由 null 更新），事件绑定以此为准 */
  bs: BScrollInstance | null
  /** 读取当前实例（用于事件回调内部，避免闭包过期） */
  getInstance: () => BScrollInstance | null
  /** 内容高度变化后刷新（数据渲染、图片加载完成后调用） */
  refresh: () => void
  /** 滚动到指定坐标，time 为动画时长（ms） */
  scrollTo: (x: number, y: number, time?: number) => void
  /** 滚动到指定元素 */
  scrollToElement: (el: HTMLElement | string, time?: number) => void
}

/**
 * better-scroll React 封装 Hook
 *
 * 使用前在模块顶层注册插件（仅需一次）：BScroll.use(PullUp)
 *
 * 说明：
 * - 实例在挂载后创建、卸载时自动 destroy，StrictMode 下幂等
 * - options 只在初始化时读取一次，后续变更不生效
 * - 默认开启 click，保证容器内点击事件可用
 */
const useBScroll = <E extends HTMLElement = HTMLDivElement>(options: Options = {}): UseBScrollResult<E> => {
  const wrapperRef = useRef<E>(null)
  const bsRef = useRef<BScrollInstance | null>(null)
  const [bs, setBs] = useState<BScrollInstance | null>(null)
  /** 用 ref 持有 options，实例不随 options 变化重建 */
  const optionsRef = useRef(options)

  useEffect(() => {
    if (!wrapperRef.current) return undefined

    const instance = new BScroll(wrapperRef.current, {
      click: true,
      ...optionsRef.current
    })
    bsRef.current = instance
    setBs(instance)

    return () => {
      instance.destroy()
      bsRef.current = null
      setBs(null)
    }
  }, [])

  const getInstance = useCallback(() => bsRef.current, [])

  const refresh = useCallback(() => {
    bsRef.current?.refresh()
  }, [])

  const scrollTo = useCallback((x: number, y: number, time = 0) => {
    bsRef.current?.scrollTo(x, y, time)
  }, [])

  const scrollToElement = useCallback((el: HTMLElement | string, time = 0) => {
    bsRef.current?.scrollToElement(el, time)
  }, [])

  return { wrapperRef, bs, getInstance, refresh, scrollTo, scrollToElement }
}

export default useBScroll
```

## RefreshLoadList（下拉刷新 + 上拉加载列表）

复制到页面 `comps/` 目录或 `src/components/common/`。依赖：`@better-scroll/pull-down`、`@better-scroll/pull-up`，以及上文的 `useBScroll`（确保已复制到 `src/hooks/useBScroll.ts`，否则调整导入路径）。

```tsx
import { useCallback, useEffect, useRef, useState } from 'react'
import BScroll from '@better-scroll/core'
import PullDown from '@better-scroll/pull-down'
import PullUp from '@better-scroll/pull-up'
import useBScroll from '@/hooks/useBScroll'

/** 注册插件（模块顶层执行一次即可） */
BScroll.use(PullDown)
BScroll.use(PullUp)

/** 分页数据约定，按实际接口结构调整 */
interface PageData<T> {
  list: T[]
  /** 是否还有更多数据 */
  hasMore: boolean
}

/** 上拉加载配置（越过底部 30px 触发）；openPullUp 恢复监听时须显式回传，无参调用会把 threshold 重置为 0 */
const PULL_UP_OPTIONS = { threshold: -30 }

interface RefreshLoadListProps<T> {
  /** 分页加载函数，page 从 1 开始 */
  fetchList: (page: number) => Promise<PageData<T>>
  /** 列表项渲染 */
  renderItem: (item: T, index: number) => React.ReactNode
  /** 列表项 key */
  rowKey: (item: T) => string | number
  /** 空态展示 */
  empty?: React.ReactNode
}

/**
 * 下拉刷新 + 上拉加载更多列表
 *
 * 使用要求：
 * 1. 父级必须为组件提供确定高度（如 flex 布局中 flex: 1 + min-height: 0）
 * 2. 滚动内容（list-content）是 wrapper 的第一个子元素，其高度超过 wrapper 才可滚动
 */
function RefreshLoadList<T>({ fetchList, renderItem, rowKey, empty = null }: RefreshLoadListProps<T>) {
  const [list, setList] = useState<T[]>([])
  const [hasMore, setHasMore] = useState(true)
  const [loading, setLoading] = useState(false)

  const pageRef = useRef(1)
  /** 事件回调中读取最新值用，避免闭包过期 */
  const fetchListRef = useRef(fetchList)
  fetchListRef.current = fetchList
  const hasMoreRef = useRef(hasMore)
  hasMoreRef.current = hasMore

  const { wrapperRef, bs, getInstance, refresh } = useBScroll({
    pullDownRefresh: { threshold: 60, stop: 40 },
    pullUpLoad: PULL_UP_OPTIONS
  })

  /** 加载第一页（初始加载 + 下拉刷新共用） */
  const loadFirstPage = useCallback(async () => {
    const instance = getInstance()
    setLoading(true)
    try {
      const data = await fetchListRef.current(1)
      pageRef.current = 1
      setList(data.list)
      setHasMore(data.hasMore)
    } finally {
      /** 必须复位，否则无法再次触发下拉 / 上拉 */
      instance?.finishPullDown()
      instance?.finishPullUp()
      setLoading(false)
    }
  }, [getInstance])

  /** 加载下一页（上拉加载） */
  const loadNextPage = useCallback(async () => {
    const instance = getInstance()
    // 分页终点硬闸：finishPullUp / refresh 会重新武装 watcher（closePullUp 不构成硬保证），
    // 终点后再触发须直接 closePullUp 并 return；此分支禁用 finishPullUp（恰好重新武装）
    if (!hasMoreRef.current) {
      instance?.closePullUp()
      return
    }
    setLoading(true)
    try {
      const nextPage = pageRef.current + 1
      const data = await fetchListRef.current(nextPage)
      pageRef.current = nextPage
      setList((prev) => [...prev, ...data.list])
      setHasMore(data.hasMore)
    } finally {
      instance?.finishPullUp()
      setLoading(false)
    }
  }, [getInstance])

  /** 绑定插件事件（bs 初始化完成后执行） */
  useEffect(() => {
    if (!bs) return undefined
    bs.on('pullingDown', loadFirstPage)
    bs.on('pullingUp', loadNextPage)
    return () => {
      bs.off('pullingDown', loadFirstPage)
      bs.off('pullingUp', loadNextPage)
    }
  }, [bs, loadFirstPage, loadNextPage])

  /** 初始加载 */
  useEffect(() => {
    loadFirstPage()
  }, [loadFirstPage])

  /** 数据渲染完成后刷新滚动高度 */
  const skipFirstRefresh = useRef(true)
  useEffect(() => {
    if (skipFirstRefresh.current) {
      skipFirstRefresh.current = false
      return
    }
    refresh()
  }, [list, refresh])

  /** 没有更多数据时关闭上拉监听，刷新后恢复（显式回传配置，避免插件重置 threshold） */
  useEffect(() => {
    if (!bs) return
    if (hasMore) {
      bs.openPullUp(PULL_UP_OPTIONS)
    } else {
      bs.closePullUp()
    }
  }, [bs, hasMore])

  return (
    <div className="refresh-load-list" ref={wrapperRef} style={{ height: '100%', overflow: 'hidden' }}>
      <div className="list-content">
        {list.map((item, index) => (
          <div key={rowKey(item)}>{renderItem(item, index)}</div>
        ))}
        {!loading && list.length === 0 && empty}
        {!hasMore && list.length > 0 && <div className="no-more">没有更多了</div>}
      </div>
    </div>
  )
}

export default RefreshLoadList
```

## WheelPicker（滚轮选择器）

复制到页面 `comps/` 目录或 `src/components/common/`。依赖：`@better-scroll/wheel`，以及上文的 `useBScroll`。

```tsx
import { useEffect } from 'react'
import BScroll from '@better-scroll/core'
import Wheel from '@better-scroll/wheel'
import useBScroll from '@/hooks/useBScroll'

/** 注册插件（模块顶层执行一次即可） */
BScroll.use(Wheel)

interface WheelPickerProps {
  /** 选项文案列表 */
  options: string[]
  /** 当前选中下标 */
  selectedIndex: number
  /** 滚动停止后选中变化回调 */
  onChange: (index: number) => void
}

/**
 * 滚轮选择器
 *
 * 配套样式要求（itemHeight 固定且每项等高）：
 * .wheel-picker { height: itemHeight * 可见行数; overflow: hidden; }
 * .wheel-item { height: itemHeight; line-height: itemHeight; text-align: center; }
 * 选中区域视觉（上下渐变遮罩 + 中间分隔线）用伪元素自行实现
 */
function WheelPicker({ options, selectedIndex, onChange }: WheelPickerProps) {
  const { wrapperRef, bs, refresh } = useBScroll({
    wheel: {
      selectedIndex,
      /** 每行偏转角度，决定滚轮曲面弧度 */
      rotate: 25,
      /** 回弹吸附到最近一项的动画时长 */
      adjustTime: 400,
      wheelWrapperClass: 'wheel-list',
      wheelItemClass: 'wheel-item'
    }
  })

  /** 选项或选中值变化时刷新并定位 */
  useEffect(() => {
    if (!bs) return
    refresh()
    bs.wheelTo(selectedIndex)
  }, [bs, options, selectedIndex, refresh])

  /** 滚动停止后同步选中下标 */
  useEffect(() => {
    if (!bs) return undefined
    const handleScrollEnd = () => {
      onChange(bs.getSelectedIndex())
    }
    bs.on('scrollEnd', handleScrollEnd)
    return () => {
      bs.off('scrollEnd', handleScrollEnd)
    }
  }, [bs, onChange])

  return (
    <div className="wheel-picker" ref={wrapperRef}>
      <ul className="wheel-list">
        {options.map((option) => (
          <li className="wheel-item" key={option}>
            {option}
          </li>
        ))}
      </ul>
    </div>
  )
}

export default WheelPicker
```
