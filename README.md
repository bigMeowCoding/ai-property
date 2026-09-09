# AI Property

可复用 AI 资产的统一仓库，用于沉淀、维护和分发 Skills、MCP Servers、Codex Plugins 以及相关资源。

## 资产目录

| 类型 | 目录 | 说明 |
| --- | --- | --- |
| Skills | [`skills/`](skills/) | 面向 AI Agent 的工作流、领域知识、脚本和模板 |
| MCP Servers | [`mcp-servers/`](mcp-servers/) | 基于 Model Context Protocol 的工具服务 |
| Plugins | [`plugins/`](plugins/) | 可安装的 Codex 插件包，可组合 Skills、MCP、Apps 等能力 |
| Agents | [`agents/`](agents/) | 可分发的 Codex 自定义 Agent，安装后用于隔离开发与独立审查上下文 |

当前资产：

- [`ahooks`](skills/ahooks/)：提供 ahooks React Hooks 的状态、请求、副作用、性能和 DOM 使用指南。
- [`ant-design-mobile`](skills/ant-design-mobile/)：提供 Ant Design Mobile 组件、主题、API 与移动端适配指南。
- [`app-webview-bridge`](skills/app-webview-bridge/)：沉淀运营 App RN WebView 与内嵌 H5 的认证、上下文和原生桥接契约。
- [`better-scroll`](skills/better-scroll/)：指导 React H5 中 better-scroll v2 的选型、集成和交互问题排查。
- [`busy-ui`](skills/busy-ui/)：提供 `@busy-fe/ui` v7 管理端组件选型、API、迁移与页面模式指南。
- [`code-craft-and-refactoring`](skills/code-craft-and-refactoring/)：以证据驱动编码、重构、评审、性能与安全优化，并与前端架构工作双向路由。
- [`codex-troubleshooter`](skills/codex-troubleshooter/)：诊断并修复 Codex Desktop、CLI、Skill、Plugin、MCP、网络与配置问题。
- [`frontend-architect`](skills/frontend-architect/)：面向复杂前端系统的架构设计、审计、技术选型和渐进式演进。
- [`frontend-design`](skills/frontend-design/)：创建具有明确视觉方向和生产质量的前端界面。
- [`human-ui`](skills/human-ui/)：审查界面的人性化设计、可访问性、交互质感和设计偏好。
- [`init-ai-agent-project`](skills/init-ai-agent-project/)：按 React、Vue、微信小程序等技术栈与管理端、移动端、API 服务等项目形态，生成专属 `.ai/` 规则、项目宪法和可验收规格。
- [`integrate-busy-arms-rum`](skills/integrate-busy-arms-rum/)：为团队 H5/Web 项目接入、迁移并排查 `@busy-fe/monitor-web` 与阿里云 ARMS RUM。
- [`internet-product-manager`](skills/internet-product-manager/)：基于知识库方法论完成产品机会、需求、验证与优先级决策。
- [`vercel-react-best-practices`](skills/vercel-react-best-practices/)：提供 Vercel React 与 Next.js 性能优化规则。
- [`vue-best-practices`](skills/vue-best-practices/)：提供 Vue 3 Composition API、SFC、响应式与组件设计实践。
- [`vue-debug-guides`](skills/vue-debug-guides/)：诊断 Vue 3 运行时、异步、响应式与 SSR/Hydration 问题。
- [`vue-jsx-best-practices`](skills/vue-jsx-best-practices/)：说明 Vue JSX 与 React JSX 的关键语法和配置差异。
- [`vue-options-api-best-practices`](skills/vue-options-api-best-practices/)：提供 Vue 3 Options API 与 TypeScript 使用规范。
- [`vue-pinia-best-practices`](skills/vue-pinia-best-practices/)：提供 Pinia Store、状态管理与响应式实践。
- [`vue-router-best-practices`](skills/vue-router-best-practices/)：提供 Vue Router 4 导航守卫、参数与生命周期实践。
- [`vue-testing-best-practices`](skills/vue-testing-best-practices/)：提供 Vitest、Vue Test Utils 与 Playwright 测试实践。
- [`developer`](agents/developer.toml)：统一承担功能开发、缺陷修复和已确认审查意见返修，并按任务切换执行边界。
- [`code_reviewer`](agents/code-reviewer.toml)：只读的独立审查 Agent，覆盖通用代码与 Vue 管理端专项审查。

## 使用 Skill

复制或软链接目标 Skill 到 Codex 的 Skills 目录，例如：

```bash
ln -s "$(pwd)/skills/codex-troubleshooter" ~/.codex/skills/codex-troubleshooter
```

重启 Codex 或新建任务后即可使用。每个 Skill 的触发条件和工作流以其 `SKILL.md` 为准。

## 使用 Agent 资产

将 [`agents/`](agents/) 中的 TOML 文件复制到目标项目的 `.codex/agents/`，或复制到 `~/.codex/agents/` 作为个人 Agent：

```bash
mkdir -p /path/to/project/.codex/agents
cp agents/*.toml /path/to/project/.codex/agents/
```

安装后可直接要求：

```text
让 developer 完成实现；完成后新开 code_reviewer，仅根据需求、diff 和测试结果独立审查。
```

审查 Agent 配置为只读，开发 Agent 配置为工作区写入；实际权限仍受父任务的权限模式约束。两者应使用独立线程，交接时只传需求、基线、diff、测试结果和必要架构信息。

## 新增资产

```text
ai-property/
├── agents/<agent-name>.toml
├── skills/<skill-name>/
│   ├── SKILL.md
│   ├── agents/openai.yaml        # 推荐
│   ├── scripts/                  # 可选
│   ├── references/               # 可选
│   └── assets/                   # 可选
├── mcp-servers/<server-name>/
├── plugins/<plugin-name>/
│   └── .codex-plugin/plugin.json
└── scripts/validate_repository.py
```

资产名统一使用小写 `kebab-case`。提交前运行：

```bash
python3 scripts/validate_repository.py
```

更完整的要求见 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 许可证

除具体资产目录另有说明外，本仓库内容采用 [MIT License](LICENSE)。
