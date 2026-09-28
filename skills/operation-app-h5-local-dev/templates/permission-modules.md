# 权限消费模块族模板

来源：`busyming-store-opening-h5`。复制到目标项目 `src/service/<module>/`、
`src/hooks/`、`src/components/common/`、`src/router/`，按项目权限系统应用码与
页面/按钮清单改造。机制细节见 [../reference/permission-consumption.md](../reference/permission-consumption.md)。

## §1 permissionCodes.ts（权限码单一契约文件）

```ts
/**
 * 模块权限资源码共享契约。
 * service 与页面共同消费，所有值须与权限系统已建资源编码逐字一致。
 */

/** 权限系统注册的应用编码（模板拼接前缀，杜绝手写漂移） */
export const PERMISSION_APP_CODE = 'storeoperationApp'

/** 页面资源码 */
export const PAGE_PERMISSION = {
  home: `${PERMISSION_APP_CODE}newStoreActivity`,
  my: `${PERMISSION_APP_CODE}newStoreActivityMy`
  // ...其余页面
} as const

/** 我的活动动作资源码 */
export const MY_BUTTON_PERMISSION = {
  detail: `${PERMISSION_APP_CODE}newStoreActivityMyDetail`,
  confirm: `${PERMISSION_APP_CODE}newStoreActivityMyConfirm`,
  adjust: `${PERMISSION_APP_CODE}newStoreActivityMyAdjust`
} as const

// 例外声明：后端未建档独立资源码的动作不走门控，以后端 buttons[] 为准
// （如详情页 CONFIRM 未建独立资源码，调用方必须不传并降级基础操作信息）。

/** 全量已建资源码，供权限校验与测试注入。 */
export const ALL_PERMISSION_KEYS: string[] = [...Object.values(PAGE_PERMISSION), ...Object.values(MY_BUTTON_PERMISSION)]
```

要点：

- 权限码**纯字母数字 + camelCase**（后端 ACL 硬约束），模板拼接保证与建档码
  逐字全等。
- 页面码与按钮码分组常量，消费侧统一从契约文件取码，不写字符串字面量。

## §2 usePermission / AuthButton（消费 hook 与声明式守卫）

```ts
// src/hooks/usePermission.ts
import { useCallback, useMemo } from 'react'

import { useGlobalState } from '@/store'

export function usePermission() {
  const userPermissionKeys = useGlobalState((s) => s.userPermissionKeys)
  const permissionReady = useGlobalState((s) => s.permissionReady)
  const permissionKeySet = useMemo(() => new Set(userPermissionKeys), [userPermissionKeys])

  /**
   * 判断当前用户是否拥有指定权限。纯 fail-closed（hr-h5 已落地口径）：
   * 空码不设门控返回 true（工具能力语义）；权限引导未落定（permissionReady 为
   * false）时不放行；非空码统一按权限集合判定。
   */
  const hasPermission = useCallback(
    (permissionKey: string): boolean => {
      if (!permissionKey) return true

      return permissionReady && permissionKeySet.has(permissionKey)
    },
    [permissionKeySet, permissionReady]
  )

  /** 批量判断：是否拥有全部指定权限（空数组返回 true） */
  const hasAllPermissions = useCallback(
    (keys: string[]): boolean => {
      if (!keys.length) return true

      return permissionReady && keys.every((key) => permissionKeySet.has(key))
    },
    [permissionKeySet, permissionReady]
  )

  /** 批量判断：是否拥有任一指定权限（空数组返回 true） */
  const hasAnyPermission = useCallback(
    (keys: string[]): boolean => {
      if (!keys.length) return true

      return permissionReady && keys.some((key) => permissionKeySet.has(key))
    },
    [permissionKeySet, permissionReady]
  )

  return {
    userPermissionKeys,
    permissionReady,
    hasPermission,
    hasAllPermissions,
    hasAnyPermission
  }
}
```

```tsx
// src/components/common/AuthButton.tsx
import type { ReactNode } from 'react'

import { usePermission } from '@/hooks/usePermission'

interface AuthButtonProps {
  /** 需要的权限 key，与后端 ACL 配置一致 */
  permissionKey: string
  /** 有权限时渲染的内容 */
  children: ReactNode
  /** 无权限时的兜底内容，默认不渲染 */
  fallback?: ReactNode
}

export default function AuthButton({ permissionKey, children, fallback = null }: AuthButtonProps) {
  const { hasPermission } = usePermission()

  if (!hasPermission(permissionKey)) return fallback

  return children
}
```

## §3 路由权限注册表（pageRoutePermissions）

```ts
// src/router/pageRoutePermissions.ts
import { PAGE_PERMISSION } from '@/service/<module>/permissionCodes'

export interface PageRoutePermission {
  path: string
  permissionKey: string
}

/** 页面路由权限注册表：路由定义与守卫统一从本表取 path + permissionKey */
export const PAGE_ROUTE_PERMISSION_REGISTRY = {
  home: { path: '/', permissionKey: PAGE_PERMISSION.home },
  my: { path: '/activity/my', permissionKey: PAGE_PERMISSION.my }
  // ...其余页面
} as const
```

消费方（路由守卫 / 布局）按 `meta.permissionKey` 判定 `hasPermission`，无权限落
`/no-auth`。

## §4 按钮映射扩展点（ACTIVITY_BUTTON_MAP）

```ts
// src/pages/<module>/constants/<module>Enums.ts
/** 后端 buttons[] 下发的按钮编码（与 OAS 枚举一致） */
export type ActivityButtonCode = 'NAVIGATION' | 'DETAIL' | 'CONFIRM' | 'ADJUST' | 'ASSIGN' | 'CANCEL_DELAY'

/** 按钮元数据：文案 + 动作标识（动作由消费方接线，弹窗/跳转逻辑不在本表） */
export interface ActivityButtonMeta {
  code: ActivityButtonCode
  label: string
  /** 动作标识：openSheet-打开异动弹窗，navigate-导航到店，goDetail-查看详情，openAssign-打开分配弹窗 */
  action: 'openSheet' | 'navigate' | 'goDetail' | 'openAssign'
}

export const ACTIVITY_BUTTON_MAP: Record<ActivityButtonCode, ActivityButtonMeta> = {
  NAVIGATION: { code: 'NAVIGATION', label: '导航到店', action: 'navigate' },
  DETAIL: { code: 'DETAIL', label: '查看详情', action: 'goDetail' },
  CONFIRM: { code: 'CONFIRM', label: '活动确认', action: 'openSheet' },
  ADJUST: { code: 'ADJUST', label: '活动调整', action: 'openSheet' },
  ASSIGN: { code: 'ASSIGN', label: '活动分配', action: 'openAssign' },
  CANCEL_DELAY: { code: 'CANCEL_DELAY', label: '取消/延期', action: 'openSheet' }
}

/**
 * 安全取按钮元数据：后端下发未知枚举时返回 undefined，消费方过滤忽略
 * （后端按状态差异化下发按钮，前端不做状态推演）
 */
export function getButtonMeta(code: string): ActivityButtonMeta | undefined {
  return ACTIVITY_BUTTON_MAP[code as ActivityButtonCode]
}

/** 异动动作按钮（hasPendingChange=true 时置灰的对象） */
export const CHANGE_BUTTON_CODES: ActivityButtonCode[] = ['CONFIRM', 'ADJUST', 'CANCEL_DELAY']
```

要点：

- 映射表是**接线元数据**，不承载「该显示哪些按钮」的业务推演；按钮列表权威来源
  是后端 buttons[]。
- 新增按钮编码时：OAS 枚举确认 → 映射表加条目 → 消费方接动作，不碰既有条目。

## §5 后端 buttons[] 驱动消费（组件侧）

```tsx
// 卡片按钮区：buttons[] 映射元数据，未知枚举忽略；
// NAVIGATION 由地址行导航胶囊承接，按钮区不重复渲染（胶囊显隐同样由 buttons 驱动）
function resolveVisibleButtons(buttons: string[]): ActivityButtonMeta[] {
  return buttons
    .map(getButtonMeta)
    .filter((meta): meta is ActivityButtonMeta => !!meta && meta.code !== ACTIVITY_BUTTON_MAP.NAVIGATION.code)
}

function ActionButtonArea({ buttons }: { buttons: string[] }) {
  const metaList = resolveVisibleButtons(buttons)

  if (metaList.length === 0) return null

  return (
    <div className="card__buttons">
      {metaList.map((meta, index) => (
        <button
          key={meta.code}
          className={index === metaList.length - 1 ? 'btn--primary' : 'btn--outline'}
          onClick={() => handleAction(meta.action)}
        >
          {meta.label}
        </button>
      ))}
    </div>
  )
}
```

要点：

- 按钮区按后端 buttons[] 顺序渲染，末位主按钮；未知枚举静默忽略。
- 可选权限兜底：`buttonPermissionKeys` 映射配置后，无权限按钮不渲染；未配置的
  工具能力 code（如 NAVIGATION）不走权限门控。
- 置灰态：`hasPendingChange` 时 `CHANGE_BUTTON_CODES` 内按钮置灰，点击统一 Toast
  提示阻断态。
- **禁止**用 `status` + `roleType` 前端推演按钮列表；状态文案（如 statusDesc）可
  按接口枚举安全映射（未知回退默认），但按钮显隐不可。
