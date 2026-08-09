---
name: init-ai-agent-project
description: Initialize or migrate a software repository into an AI Agent collaboration project with `.ai/AGENTS.md`, a project constitution, and dated acceptance specs. Detect or select the repository's technology stack and product shape, then compose different rules for React, Vue, WeChat Mini Program, Node.js, Python, admin, mobile, consumer Web, API service, and library projects. Use when asked to initialize `.ai/`, add Agent project rules, create a project constitution, or adapt AI development governance to a repository.
---

# 初始化 AI Agent 开发项目

把目标仓库改造成可执行、可验收的 Agent 协作项目。先勘察真实仓库，再按“技术栈 × 项目形态”生成不同的 `.ai/AGENTS.md` 与 `.ai/CONSTITUTION.md`。

不要生成 `UI-SPEC.md`、Claude/Codex 专属规则目录、通用占位规则或未蒸馏的设计原始数据。

## 输出结构

```text
<repo>/
├── AGENTS.md
└── .ai/
    ├── AGENTS.md
    ├── CONSTITUTION.md
    └── specs/
        ├── README.md
        └── YYYY-MM-DD-<slug>.spec.md
```

- 根 `AGENTS.md` 只作为 `.ai/` 规则入口。
- `.ai/AGENTS.md` 记录真实命令、目录、技术栈工作流和项目形态约束。
- `.ai/CONSTITUTION.md` 记录不可协商原则，并包含技术栈和项目形态附则。
- spec 保存需求、技术决策、UI 要求、测试与验收事实；UI 内容直接写入相关 spec。

## 工作流

### 1. 勘察仓库

读取以下事实，禁止直接套模板：

- `AGENTS.md`、README、贡献指南和现有 AI/IDE 规则。
- 清单、锁文件、脚本、运行时版本和测试配置。
- 源码、应用、包、测试、服务与小程序目录。
- React/Vue/小程序/Node/Python 等框架证据。
- 管理端、移动端、用户 Web、API 服务、库等交付形态证据。
- 遗留 `agents.md`、`constitution.md`、`plan.md`、`memory.md` 与旧 spec 布局。
- 用户已有工作区改动；不得覆盖或清理无关内容。

### 2. 选择两个独立档案

技术栈档案：

- `react`
- `vue`
- `wechat-miniprogram`
- `node`
- `python`
- `generic`（仅用于尚无法识别的仓库）

项目形态档案：

- `admin`
- `mobile`
- `consumer-web`
- `api-service`
- `library`
- `generic`（仅用于尚无法识别的仓库）

使用 `auto` 时，脚本只采纳强证据；发现多个候选会停止并要求显式选择。详细选择表见 [references/profile-selection.md](references/profile-selection.md)。

### 3. 初始化

优先运行确定性脚本：

```bash
bash scripts/init.sh /path/to/repo
```

识别错误或新项目缺少证据时显式指定：

```bash
bash scripts/init.sh /path/to/repo --stack react --project-type admin
bash scripts/init.sh /path/to/repo --stack vue --project-type mobile
bash scripts/init.sh /path/to/repo --stack wechat-miniprogram --project-type mobile
```

查看支持范围：

```bash
bash scripts/init.sh --list-profiles
```

默认保留目标仓库已有文件。只有在已读取并迁移其中定制规则后，才可使用 `--force` 重建 `.ai/AGENTS.md` 与 `.ai/CONSTITUTION.md`；随后把项目特有约束重新合入。

### 4. 校准生成结果

生成后必须逐项检查：

1. 技术栈和项目形态是否正确。
2. 包管理器、脚本和源码目录是否来自真实仓库。
3. 技术栈规则是否适用当前版本、渲染模式和测试工具。
4. 项目形态规则是否符合用户、权限、部署和运行环境。
5. 项目是否还有领域专属约束需要写入两个文档。
6. 宪法条款是否确属不可协商；普通建议只留在 AGENTS。

不要保留错误的自动识别说明。修正档案并重新生成，或在证据充分时人工校准。

### 5. 迁移已有知识

- `agents.md` 的有效规则迁入 `.ai/AGENTS.md`。
- `constitution.md` 的不可协商原则迁入 `.ai/CONSTITUTION.md`。
- `plan.md`、`memory.md` 的长期有效事实迁入相关 spec 或 AGENTS。
- 旧 `.ai/specs/<slug>/spec.md` 使用 `scripts/migrate-spec-layout.sh` 平铺迁移。
- 技术设计、接口约束和排障结论写入相关 spec，不建 `.ai/docs/` 或 `.ai/notes/`。
- 设计稿只作为输入；将可验收 UI 事实写入 spec，不提交批量截图或 raw JSON。

确认迁移完成后运行：

```bash
bash scripts/cleanup-legacy-docs.sh /path/to/repo
```

清理脚本不处理项目自己的 UI/设计系统文档。

### 6. 编写 spec

使用平铺命名：`.ai/specs/YYYY-MM-DD-<kebab-slug>.spec.md`。

每份 spec 至少包含：

- 背景、目标、范围与非范围。
- 可编号、可观察的功能要求。
- 技术与数据约束、失败路径和兼容要求。
- UI/交互要求（如适用），直接记录布局、状态、响应式和无障碍验收事实。
- 测试矩阵、验收标准、发布与回滚要求。
- 待确认项与明确假设。

需求演进时创建新日期版本并说明与旧版关系，不静默覆盖历史决策。

## 档案维护

模板采用三层组合：

1. `templates/base/`：所有项目共享的工作流和宪法底线。
2. `templates/profiles/stacks/<stack>/`：框架、运行时与测试约束。
3. `templates/profiles/project-types/<type>/`：权限、交互、部署和兼容约束。

新增档案时同时提供 `AGENTS.md` 与 `CONSTITUTION.md` 片段，登记到 `scripts/init_project.py`，更新选择参考并补充组合测试。不要复制完整模板形成难以同步的矩阵。

## 验收

- [ ] 没有生成或引用 `.ai/UI-SPEC.md`。
- [ ] 没有生成 Claude/Codex 专属文档或目录。
- [ ] `.ai/AGENTS.md` 同时包含所选技术栈与项目形态规则。
- [ ] `.ai/CONSTITUTION.md` 同时包含对应的两类附则。
- [ ] 生成文档中的命令、目录和证据来自目标仓库。
- [ ] 自动识别歧义会失败并给出显式参数指引。
- [ ] 已有文件默认不被覆盖，`--force` 仅在迁移定制内容后使用。
- [ ] spec 为平铺日期命名，且无 `docs/`、`notes/`、`mastergo-output/`。
- [ ] 无密钥、Token、Cookie、个人配置或未蒸馏原始数据进入 `.ai/`。

## 资源

- `scripts/init.sh`：稳定入口。
- `scripts/init_project.py`：档案识别、组合与生成。
- `scripts/migrate-spec-layout.sh`：迁移旧 spec 布局。
- `scripts/cleanup-legacy-docs.sh`：迁移完成后清理旧 Agent 文档。
- `references/profile-selection.md`：档案证据、选择原则和扩展清单。
