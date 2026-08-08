# AI Property

可复用 AI 资产的统一仓库，用于沉淀、维护和分发 Skills、MCP Servers、Codex Plugins 以及相关资源。

## 资产目录

| 类型 | 目录 | 说明 |
| --- | --- | --- |
| Skills | [`skills/`](skills/) | 面向 AI Agent 的工作流、领域知识、脚本和模板 |
| MCP Servers | [`mcp-servers/`](mcp-servers/) | 基于 Model Context Protocol 的工具服务 |
| Plugins | [`plugins/`](plugins/) | 可安装的 Codex 插件包，可组合 Skills、MCP、Apps 等能力 |

当前资产：

- [`code-craft-and-refactoring`](skills/code-craft-and-refactoring/)：以证据驱动编码、重构、评审、性能与安全优化，并与前端架构工作双向路由。
- [`codex-troubleshooter`](skills/codex-troubleshooter/)：诊断并修复 Codex Desktop、CLI、Skill、Plugin、MCP、网络与配置问题。
- [`frontend-architect`](skills/frontend-architect/)：面向复杂前端系统的架构设计、审计、技术选型和渐进式演进。

## 使用 Skill

复制或软链接目标 Skill 到 Codex 的 Skills 目录，例如：

```bash
ln -s "$(pwd)/skills/codex-troubleshooter" ~/.codex/skills/codex-troubleshooter
```

重启 Codex 或新建任务后即可使用。每个 Skill 的触发条件和工作流以其 `SKILL.md` 为准。

## 新增资产

```text
ai-property/
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
