---
name: init-ai-agent-project
description: >-
  Bootstraps AI agent mode: `.ai/` with CONSTITUTION.md, UI-SPEC.md, AGENTS.md, and
  flat specs/YYYY-MM-DD-<slug>.spec.md (§4 UI Prompt for agents). MasterGo extract is
  auxiliary to sdd-spec-writer—not persisted raw/screenshots by default. Chains with
  sdd-spec-writer and mastergo-extract-skill.
---

# 初始化 AI Agent 开发项目

将任意仓库改造成 **AI Agent 协作模式**：业务代码与 Agent 资料分离，规格用日期前缀迭代，全仓规则集中在 `AGENTS.md` 与 `CONSTITUTION.md`。

参考实现：`interview` 仓库的 `.ai/` 布局（本 skill 的模板与之对齐，内容按目标项目裁剪）。

## 何时使用

- 用户说「改成 agent 开发项目」「初始化 .ai」「搭 agent 目录」
- 新仓库需要可验收 spec 与宪法约束
- 已有项目要迁入 `.ai/specs/` 命名规范

## 目标目录结构

```
<repo-root>/
├── AGENTS.md                 # 入口：指向 .ai/AGENTS.md
└── .ai/
    ├── AGENTS.md             # 全仓 Agent 规则（主文档）
    ├── CONSTITUTION.md       # 项目宪法（最高约束，文件名大写）
    ├── UI-SPEC.md            # 团队 UI 设计规范（文件名大写）
    ├── specs/
    │   ├── README.md
    │   └── YYYY-MM-DD-<slug>.spec.md   # 验收 + §4.8 UI 实现 Prompt
    ├── UI-SPEC.md
```

初始化**仅**创建上述骨架；不默认生成 Claude Code / Codex 专属目录。

**固定文件名（大写）**：`.ai/CONSTITUTION.md`、**`.ai/UI-SPEC.md`**（禁止 `ui-spec.md`、`constitution.md` 等小写变体）；根目录与 `.ai/` 的 `AGENTS.md` 同理保持约定拼写。

**不要**创建 `.ai/docs/`、`.ai/mastergo-output/`、默认不创建 `.ai/mastergo/`（批量 JSON/截图）。
有 MasterGo 时：提取 → **spec §4.8 Prompt** + **UI-SPEC**（`mastergo-extract` + `sdd-spec-writer`）。
技术设计/排障写在 **spec 正文** 或 **`.ai/AGENTS.md` 业务片段**，不建 `notes/`。

**根目录遗留文件（改造后须删除）**：内容迁入 `.ai/` 后，**不要**在根目录保留跳转 stub。应删除：

| 遗留文件 | 迁入目标 | 根目录保留 |
|----------|----------|------------|
| `agents.md` | `.ai/AGENTS.md` | 仅 **`AGENTS.md`**（跳转指针） |
| `constitution.md` | `.ai/CONSTITUTION.md` | 无 |
| `plan.md` / `memory.md` | 并入 spec 或 `.ai/AGENTS.md` | 无 |
| 旧 `specs/<slug>/spec.md` | `specs/<slug>.spec.md` | `migrate-spec-layout.sh` |
| `.ai/mastergo-output/` | 蒸馏进 spec 后删除/归档 | 勿作验收依据 |


## 项目知识库视角（PKB 模式）

`.ai/` 目录本身可视为一个轻量级的项目知识库，其结构与 Karpathy 个人知识库模式（PKB）相互对应：

| PKB 三层 | `.ai/` 对应物 | 说明 |
|----------|---------------|------|
| **Schema / 规则层** | `.ai/CONSTITUTION.md` + `.ai/AGENTS.md` | 定义 Agent 如何构建和维护项目知识，是最高约束与操作规则 |
| **Wiki / 知识层** | `.ai/specs/*.spec.md`、`.ai/UI-SPEC.md`、`.ai/specs/README.md` | 编译后的需求、设计、UI 规范；README 作为索引 |
| **Raw / 原始资料** | MasterGo 提取的原始 JSON / 截图 | 默认不落库；如需临时使用，应在蒸馏进 spec / UI-SPEC 后清理 |

维护约定：

- Spec 用日期前缀迭代，旧版保留为历史版本，新版基于旧版演进；避免直接覆盖旧 spec，以便追溯决策。
- `UI-SPEC.md` 是设计系统知识，新增或变更 Token 时须同步更新。
- 技术决策、排障记录、接口规范等知识写入 spec 正文或 `.ai/AGENTS.md` 业务片段，不建长期 `notes/`。
- 初始化时若项目已有 `README`、`package.json`、旧版规则等原始资料，应将其中的关键约束迁移到 `.ai/` 知识层，而非简单复制。

## 工作流

### 1. 勘察目标项目（必做）

读取并记录（写入 `.ai/AGENTS.md` 对应章节，勿照抄 interview 示例）：

- 包管理器、`package.json` scripts、测试命令
- 主要源码目录（如 `src/`、`packages/`、`app/`）
- 技术栈、语言、是否 monorepo
- 是否已有 `.cursor/`、`.claude/`、旧版 rules
- 根目录是否存在 **`agents.md`**、**`constitution.md`**、**`plan.md`**、**`memory.md`** 等待迁移/清理的遗留文档
- 是否已有 **`ui-spec.md`**、**`UI.md`**、**`design-system.md`** 等 UI 规范待迁入 `.ai/UI-SPEC.md`
- 现有页面的色彩、字号、组件模式（用于填写 **UI-SPEC.md**，勿留空模板）

**禁止**在未勘察的情况下把 interview 项目的目录表原样复制进新项目。

### 2. 创建骨架

优先执行脚本（从 skill 目录解析模板路径）：

```bash
SKILL_DIR="${SKILL_DIR:-$HOME/.cursor/skills/init-ai-agent-project}"
bash "$SKILL_DIR/scripts/init.sh" /path/to/target-repo
```

若脚本不可用，则手动：

1. 创建 `.ai/specs/`（示例为平铺 `*.spec.md`）
2. 从 [templates/](templates/) 复制并**按项目改写**：
   - `root-AGENTS.md` → `<repo>/AGENTS.md`
   - `ai-AGENTS.md` → `<repo>/.ai/AGENTS.md`
   - `CONSTITUTION.md` → `<repo>/.ai/CONSTITUTION.md`
   - `UI-SPEC.md` → `<repo>/.ai/UI-SPEC.md`
3. 根目录 `AGENTS.md` 仅保留跳转说明，详细规则只在 `.ai/AGENTS.md`
4. **迁移**旧文档内容（勿留 stub）：
   - `agents.md` → `.ai/AGENTS.md`（根目录改用 `AGENTS.md` 指针）
   - `constitution.md` → `.ai/CONSTITUTION.md`
   - `plan.md` / `memory.md` → 写入 spec 或 `.ai/AGENTS.md`
5. **禁止** `.ai/docs/`、`.ai/mastergo-output/`、默认 `mastergo/` 提取物
6. 若有旧 `specs/<slug>/` 布局：`bash scripts/migrate-spec-layout.sh <repo>`
7. **清理遗留文件**（迁移完成后必做，见 §7）

### 3. 接入 Cursor / 仓库规则

若项目使用 Cursor：

- 在 `.cursor/rules/` 或根 `AGENTS.md`（Cursor 会读）中增加一条：**完整协作规则见 `.ai/AGENTS.md`**
- 与现有 `always_applied_workspace_rules` 并存时，避免重复矛盾；以 `CONSTITUTION.md` 为准做合宪性审查

### 4. 编写 / 迁移 spec

**文件命名（强制）**：`.ai/specs/YYYY-MM-DD-<kebab-slug>.spec.md`

| 内容 | 位置 |
|------|------|
| 验收 + UI 实现 Prompt（§4.8） | `*.spec.md`（**sdd-spec-writer**） |
| 全局 Token / 组件 | `.ai/UI-SPEC.md` |
| 技术设计 / 排障 | spec 正文 §实现提示 等 |
| MasterGo 提取 | 会话内辅助，**默认不落库** |

新建需求：

```bash
cp templates/spec.example.md .ai/specs/$(date +%Y-%m-%d)-my-feature.spec.md
```

有 MasterGo：**mastergo-extract** → **sdd-spec-writer** → §4.8 + UI-SPEC（见 `ui-prompt-language.md`）。

### 5. 定制 CONSTITUTION.md

与用户确认不可协商原则（通常 3–5 条）：TDD、简单性、错误处理、依赖策略等。模板见 [templates/CONSTITUTION.md](templates/CONSTITUTION.md)；版本行保留 `Version` / `Ratified` / `Adapted`。

### 6. 定制 UI-SPEC.md

**必做**：初始化或改造项目时须创建/更新 **`.ai/UI-SPEC.md`**（模板见 [templates/UI-SPEC.md](templates/UI-SPEC.md)）。

- **新建项目**：从模板复制，删除「待填写」占位，填入计划使用的 token 与组件模式。
- **改造项目**：从现有页面与全局样式（如 `uni.scss`、组件库主题）**归纳**真实色值、字号、间距，禁止长期保留空模板。
- 根目录若有 `ui-spec.md`、`UI.md`、`design-system.md` 等，内容并入 `.ai/UI-SPEC.md` 后删除源文件。
- UI 相关 spec 的「非功能要求 / 验收标准」须引用本文件；Agent 实现 UI 前先读 UI-SPEC。

### 7. 清理遗留文档（改造项目必做）

内容迁入 `.ai/` 且根 `AGENTS.md` 指针就绪后，删除根目录旧文件：

```bash
SKILL_DIR="${SKILL_DIR:-$HOME/.cursor/skills/init-ai-agent-project}"
bash "$SKILL_DIR/scripts/cleanup-legacy-docs.sh" /path/to/target-repo
```

脚本会（在前提满足时）：

- 删除 `constitution.md`（要求 `.ai/CONSTITUTION.md` 已存在）
- 删除 `plan.md`、`memory.md`
- 删除小写 `agents.md`（若与 `AGENTS.md` 并存）
- 删除根目录 `ui-spec.md`、`UI.md`、`design-system.md`（若 `.ai/UI-SPEC.md` 已存在）
- 将误建的 `.ai/docs/`、`.ai/notes/` 内文件并入 spec 或 `.ai/AGENTS.md` 后删除空目录

**禁止**只写「已迁移」跳转 stub 而不删除原文件。用 `grep` 确认仓库内无对旧路径的引用后再提交。

### 8. 验收清单

完成后逐项确认：

- [ ] `.ai/AGENTS.md` 含真实的技术栈、目录结构、常用命令
- [ ] `.ai/CONSTITUTION.md` 已 ratified，且 AGENTS.md 声明合宪性审查
- [ ] **`.ai/UI-SPEC.md` 已填写**（色彩/字号/组件/交互，非空模板）
- [ ] `.ai/specs/README.md` 存在且与模板一致
- [ ] spec 为平铺 **`*.spec.md`**，§4.8 UI Prompt 约定已写在 README
- [ ] 根 `AGENTS.md` 指向 `.ai/AGENTS.md`
- [ ] 无 `docs/`、`mastergo-output/`；无默认提交的 bulk mastergo 提取物
- [ ] 根目录**无** `agents.md`、`constitution.md`、`plan.md`、`memory.md` 等遗留文件（仅保留 `AGENTS.md` 指针）
- [ ] 无密钥、token 写入 `.ai/`

## Spec 文档最小结构

每个 **`specs/YYYY-MM-DD-<slug>.spec.md`** 建议包含：

| 章节 | 内容 |
|------|------|
| 范围 | 做什么 / 不做什么 |
| 功能要求 | 编号、可验收 |
| **UI 模块** | **§4.8 页面实现 Prompt**（Agent 施工单）+ Token/组件表；引用 `.ai/UI-SPEC.md` |
| 非功能 | 性能、可测试性、无障碍、UI 规范对齐等（按需） |
| 验收标准 | 检查清单或 Given-When-Then（含 UI 验收项） |
| 实现提示 | 路径、模块名（可选，实现前可填） |

完整 SDD spec（任务拆分、测试矩阵等）见 **sdd-spec-writer** skill 的 `templates/business.md` / `shared.md` 及 `templates/ui-module.md`。

## 维护约定

- 设计稿视觉 → **spec §4.8 Prompt** + **UI-SPEC**，勿长期维护 `mastergo/raw`
- 技术设计/排障 → spec 正文，不建 `notes/`
- UI token 变更时同步 **`.ai/UI-SPEC.md`**
- 改版用新日期新 `*.spec.md` 文件

## 关联 Skill

| Skill | 用途 |
|-------|------|
| **sdd-spec-writer** | 编写 `*.spec.md`（含 §4.8 UI Prompt） |
| **mastergo-extract-skill** | 辅助提取 → 蒸馏进 spec / UI-SPEC |
| **browser-assist** | MasterGo 提取时的 WebBridge |

## 附加资源

| 文件 | 用途 |
|------|------|
| [templates/](templates/) | 可复制骨架 |
| [templates/UI-SPEC.md](templates/UI-SPEC.md) | UI 设计规范模板 |
| [scripts/init.sh](scripts/init.sh) | 非交互初始化 |
| [scripts/cleanup-legacy-docs.sh](scripts/cleanup-legacy-docs.sh) | 改造后删除根目录遗留文档 |

## 知识库关联（个人知识库）

本 skill 的 `.ai/` 初始化与维护方法与用户个人知识库中的以下概念相互支撑。当需要向用户解释 `.ai/` 的价值、或补充项目知识管理约定时，可主动参考：

| 场景 | 可参考知识库概念 |
|------|------------------|
| 项目知识库架构 | Karpathy 的个人知识库模式、知识体系、个人知识库 |
| 目标与验收 | 以终为始、DoD、验收测试 |
| 需求拆分与接口 | MECE 原则、接口设计、接口规范、SOLID 原则 |
| 反过度设计 | YAGNI、过度设计、简单直观原则、代码坏味道 |
| 代码质量保障 | 代码质量、代码评审、重构、测试驱动开发、持续集成 |

> `.ai/` 是项目级知识库：规则层（CONSTITUTION / AGENTS）约束知识生成，specs 与 UI-SPEC 是编译后的知识产物，MasterGo 等原始输入应蒸馏后丢弃，避免 raw 数据长期堆积。
| [scripts/migrate-spec-layout.sh](scripts/migrate-spec-layout.sh) | 旧 `specs/<slug>/spec.md` → 平铺 `*.spec.md` |
| [templates/specs-README.md](templates/specs-README.md) | 复制为 `.ai/specs/README.md` |
