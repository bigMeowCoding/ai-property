# 档案选择参考

## 选择原则

技术栈描述“用什么构建”，项目形态描述“为谁、在哪运行、如何交付”。两个轴必须分别选择并组合，例如：

| 项目 | 技术栈 | 项目形态 |
|------|--------|----------|
| React 运营后台 | `react` | `admin` |
| Vue H5 活动页 | `vue` | `mobile` |
| Next.js 用户站点 | `react` | `consumer-web` |
| 原生微信小程序 | `wechat-miniprogram` | `mobile` |
| NestJS 服务 | `node` | `api-service` |
| FastAPI 服务 | `python` | `api-service` |
| npm 组件库 | `react` 或 `vue` | `library` |

不要从 UI 组件库单独推断管理端，也不要从响应式 CSS 单独推断移动端。自动识别只用于强信号；业务形态不清时读取 README、部署配置、路由和用户入口，或显式选择。

## 自动识别证据

### 技术栈

- `wechat-miniprogram`：`project.config.json` 与 `app.json`/WXML。
- `react`：依赖清单包含 `react`。
- `vue`：依赖清单包含 `vue`。
- `python`：`pyproject.toml` 或 `requirements*.txt`。
- `node`：存在 `package.json`，且没有更具体的 React/Vue 信号。

同时出现多个栈信号通常表示 monorepo 或迁移期。不要猜测根档案；选择主要交付单元，或先为子目录建立更具体的 `AGENTS.md`。

### 项目形态

- `admin`：仓库或包名明确包含 admin、dashboard、backoffice。
- `mobile`：微信小程序，或 React Native、Expo、UniApp、Taro 等移动依赖。
- `api-service`：Express、Nest、FastAPI、Django、Flask、Koa、Hono 等服务框架。
- `library`：包暴露 `exports`/`main`/`module`，且不是 private 包。
- `consumer-web`：不做弱自动推断，通常显式选择。

同时命中多种形态时必须显式选择。若仓库确实包含多个独立产品，应在根规则中写共享约束，并在各应用目录放置局部 `AGENTS.md`，不要强行用单一档案描述整个 monorepo。

## 扩展档案清单

新增技术栈或项目形态时：

1. 定义能改变实际开发决策的适用边界，避免只换名词。
2. 同时新增 `AGENTS.md` 工作流片段与 `CONSTITUTION.md` 不可协商片段。
3. 在 `STACKS` 或 `PROJECT_TYPES` 登记名称。
4. 只为强、稳定证据增加自动识别；其余保持显式选择。
5. 增加至少一个与现有另一轴组合的集成测试。
6. 验证生成结果不含其他档案的专属规则。
