## 技术栈规则：Vue

- Vue 3 默认使用 `<script setup lang="ts">`、Composition API 和类型安全的 props/emits。
- 局部状态留在组件或 composable；跨页面共享才进入 Pinia 等既有 store，禁止复制可派生状态。
- composable 必须明确输入、返回值、副作用和清理；避免解构导致响应性丢失。
- `computed` 用于纯派生，`watch`/`watchEffect` 只同步外部系统，并处理 flush 时机、竞态和销毁。
- 保持模板声明式，列表 key 稳定；不要用 `v-html` 接收未净化外部内容。
- 运行既有 lint、单测与 `vue-tsc`/类型检查；覆盖加载、空态、失败和路由/权限分支。
