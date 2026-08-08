# 贡献指南

## 基本原则

- 一个目录只承载一个独立资产，目录名使用小写 `kebab-case`。
- 不提交密钥、Token、Cookie、个人配置、运行日志或构建产物。
- 文档说明资产解决什么问题、何时触发以及如何验证，避免复制通用知识。
- 脚本优先提供确定性行为，并在资产目录内使用相对路径。

## Skills

每个 Skill 必须包含 `SKILL.md`，其 YAML frontmatter 至少包含 `name` 和 `description`，且 `name` 必须与目录名一致。推荐提供 `agents/openai.yaml` 作为 UI 元数据。

详细资料按需放入：

- `scripts/`：可重复执行的确定性脚本。
- `references/`：仅在需要时载入的参考资料。
- `assets/`：生成结果会使用的模板、图片或其他资源。

不要在单个 Skill 内增加 README、安装指南或变更日志；面向使用者的说明放在 `SKILL.md`，仓库级说明放在本文件或根 README。

## MCP Servers

每个 MCP Server 使用独立目录，并至少提供：

- 源代码和锁定依赖的清单。
- 不含真实凭据的环境变量示例。
- 启动、配置、工具列表和验证方法。
- 合理的超时、错误处理和敏感信息保护。

## Plugins

每个 Codex Plugin 必须包含 `.codex-plugin/plugin.json`。仅在对应资源真实存在时声明 Skills、MCP Servers 或 Apps，并使用 Codex Plugin 校验器验证。

## 提交流程

1. 将资产放入正确的类型目录。
2. 在根 `README.md` 的“当前资产”中登记。
3. 运行 `python3 scripts/validate_repository.py`。
4. 对资产自身的脚本或服务运行测试。
