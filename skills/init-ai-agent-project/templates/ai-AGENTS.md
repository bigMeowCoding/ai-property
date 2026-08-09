# AGENTS.md

本文件为仓库内 **所有 AI Agent** 的共享规则入口（物理路径：`.ai/AGENTS.md`）。

## 项目宪法

本项目遵循 **[`CONSTITUTION.md`](./CONSTITUTION.md)**。UI 实现遵循 **[`UI-SPEC.md`](./UI-SPEC.md)**。

## `.ai/` 目录

| 路径 | 说明 |
|------|------|
| `.ai/specs/*.spec.md` | 验收规格（功能 + **§4 UI 实现 Prompt**） |
| `.ai/UI-SPEC.md` | 全局 Token / 组件模式 |
| `.ai/specs/README.md` | Spec 与 UI Prompt 约定 |

> **PKB 视角**：`.ai/` 是轻量级项目知识库。`CONSTITUTION.md` + `AGENTS.md` 为规则层，`specs/` + `UI-SPEC.md` 为编译后的知识层；MasterGo 等原始输入应蒸馏进 spec / UI-SPEC 后清理，避免 raw 数据长期堆积。

### Spec 命名

- 文件：`YYYY-MM-DD-<slug>.spec.md`
- 有设计稿：MasterGo 提取仅作写 spec 辅助，视觉须写入 **§4.8 页面实现 Prompt**（见 sdd-spec-writer `references/ui-prompt-language.md`）
- **禁止**默认向仓库提交 MasterGo `raw/`、批量截图

### 禁止存放

- 密钥、令牌
- `.ai/mastergo-output/`、未 gitignore 的大体量设计提取物

## Agent 协作

1. 改功能前读 `CONSTITUTION.md`；做 UI 前读 `UI-SPEC.md`
2. 有需求写/查 `specs/YYYY-MM-DD-<slug>.spec.md`
3. 有 MasterGo：`mastergo-extract` → `sdd-spec-writer` → spec §4.8 + UI-SPEC

<!-- 按项目补充：技术栈、目录结构、常用命令 -->
