## Vue 技术栈附则

- **Composition API：** 新代码使用 Composition API 与 `<script setup>`；仅在既有架构明确要求时延续 Options API。
- **响应性正确：** 不破坏 ref/reactive 跟踪，不用 watcher 维护本可由 computed 表达的数据。
- **副作用有生命周期：** watcher、订阅、请求和定时器必须具备停止、取消和卸载清理路径。
- **类型闭环：** props、emits、路由参数、store 和 API 边界必须有可检查类型，禁止扩散 `any`。
