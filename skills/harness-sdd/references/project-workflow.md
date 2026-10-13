# 仓库治理与标准化

为新项目建立、或将已有项目改造成一套可执行、可验收的 AI 协作基线。所有规则必须来自真实仓库证据；模板只提供结构，不能替代项目事实。

仅在用户明确要求初始化、改造或校准仓库治理时执行本参考。普通代码交付按主 `SKILL.md` 的任务交付模式处理。

不要生成长期 `.ai/specs/`、`UI-SPEC.md`、Claude/Codex 专属规则目录、通用占位文档或未蒸馏的设计原始数据。

## 入口判断

| 项目状态 | 处理方式 | 结果 |
| --- | --- | --- |
| 新项目或早期空仓库 | **工作流初始化**：明确技术栈与项目形态，建立最小治理基线 | 项目从第一项需求开始遵循统一交付流程 |
| 已有代码但尚无统一 AI 规则 | **标准化改造**：勘察现状、迁移有效规则、建立治理文件 | 保留现有工程事实，不另建平行体系 |
| 已完成标准化 | **任务交付**：按临时验收契约实施、验证与交接 | 长期约束留在代码、测试、配置和精简规则中 |

如果用户同时要求改造项目和实现功能，先建立治理基线，再使用一次性任务 Spec 或会话内验收契约推进功能。

## 标准产物

```text
<repo>/
├── AGENTS.md
└── .ai/
    ├── AGENTS.md
    └── CONSTITUTION.md
```

- 根 `AGENTS.md` 只作为 `.ai/` 规则入口。
- `.ai/AGENTS.md` 记录项目事实、真实命令、目录边界和标准交付循环。
- `.ai/CONSTITUTION.md` 只记录不可协商的工程原则。
- 需求与任务状态不在 `.ai/` 中长期归档；稳定事实优先固化到代码、测试、类型、配置或已有权威文档。

## AI 标准交付循环

1. **发现（Discover）**：读取当前需求、代码、调用链、既有规则、测试和工作区状态，建立行为基线。
2. **定义（Specify）**：在会话或临时任务 Spec 中明确目标、范围、接口、失败路径和可观察验收标准。
3. **规划（Plan）**：按模块边界拆任务，明确依赖、写入范围、契约冻结点和验证方式。
4. **实施（Implement）**：保持最小聚焦 diff，遵守项目规则，不覆盖用户改动，不建立平行架构。
5. **验证（Verify）**：从自然调用者层级验证核心价值流，再覆盖边界、错误、权限、并发和清理路径。
6. **审查（Review）**：对照当前验收契约、最终 diff 和验证证据检查行为、风险与兼容性。
7. **交接（Handoff）**：报告行为变化、验证结果、未验证项和剩余风险；交付确认后清理临时 Spec。

阶段可以按任务规模合并，但不得跳过需求依据、验证证据或风险交接。只有依赖和写入范围真正独立时才设计并行工作包。

## 建立工作流基线

### 1. 勘察真实仓库

至少检查：

- `AGENTS.md`、README、贡献指南和现有 AI/IDE 规则。
- 清单、锁文件、脚本、运行时版本、构建和测试配置。
- 源码、应用、包、测试、服务与小程序目录。
- React、Vue、微信小程序、Node、Python 等框架证据。
- 管理端、移动端、用户 Web、API 服务、库等项目形态证据。
- 遗留 `agents.md`、`constitution.md`、`plan.md`、`memory.md` 和旧 `.ai/specs/`。
- 用户已有工作区改动；不得覆盖、清理或重写无关内容。

### 2. 选择两个独立档案

技术栈档案：`react`、`vue`、`wechat-miniprogram`、`node`、`python`、`generic`。

项目形态档案：`admin`、`mobile`、`consumer-web`、`api-service`、`library`、`generic`。

`auto` 只采纳强证据；多个候选会停止并要求显式选择。新项目缺少证据时，根据用户已经确定的方案显式指定，不把猜测写成事实。详细规则见 [profile-selection.md](profile-selection.md)。

### 3. 生成或校准基线

```bash
bash <skill-dir>/scripts/init.sh /path/to/repo
bash <skill-dir>/scripts/init.sh /path/to/repo --stack react --project-type admin
bash <skill-dir>/scripts/init.sh /path/to/repo --stack vue --project-type mobile
bash <skill-dir>/scripts/init.sh --list-profiles
```

生成后检查技术栈、项目形态、包管理器、命令、源码目录、渲染模式、测试工具、权限和部署环境。识别错误时使用正确档案重新生成，不要在错误结果上追加规则。

默认保留已有文件。只有在已经读取并迁移定制规则后，才可使用 `--force` 重建 `.ai/AGENTS.md` 与 `.ai/CONSTITUTION.md`。

### 4. 标准化已有项目

- 将旧 `agents.md` 的有效工作规则迁入 `.ai/AGENTS.md`。
- 将旧 `constitution.md` 的不可协商原则迁入 `.ai/CONSTITUTION.md`。
- 将 `plan.md`、`memory.md` 和旧 `.ai/specs/` 中仍然有效的长期事实迁入代码、测试、类型、配置、AGENTS、CONSTITUTION 或项目已有权威文档。
- 不新建 `.ai/docs/`、`.ai/notes/` 或其他任务历史归档。
- 设计稿只作为当前任务输入；不提交批量截图或 raw JSON。
- 删除旧文档前必须确认仍有效的事实已迁移，并获得明确授权。

确认迁移后，可运行：

```bash
bash <skill-dir>/scripts/cleanup-legacy-docs.sh /path/to/repo
```

该脚本不删除 `.ai/specs/`、项目自有 UI 文档或设计系统文档；这些内容应由用户明确决定归档或删除。

## 档案维护

规则模板采用三层组合：

1. `templates/base/`：所有项目共享的标准交付循环和宪法底线。
2. `templates/profiles/stacks/<stack>/`：框架、运行时和测试约束。
3. `templates/profiles/project-types/<type>/`：权限、交互、部署和兼容约束。

新增档案时同时提供 `AGENTS.md` 与 `CONSTITUTION.md` 片段，登记到 `scripts/apply_workflow.py`，更新选择参考并补充组合测试。不要复制完整模板形成难以维护的矩阵。

## 完成检查

- [ ] `.ai/AGENTS.md` 和 `.ai/CONSTITUTION.md` 包含正确的技术栈与项目形态规则。
- [ ] 初始化没有创建 `.ai/specs/` 或其他长期任务文档。
- [ ] 生成内容中的命令、目录、版本和证据来自真实仓库或用户明确选择。
- [ ] 已有规则和用户改动没有被静默覆盖；清理只发生在确认迁移并获得授权后。
- [ ] 没有生成 `UI-SPEC.md`、工具专属规则目录或未蒸馏原始数据。
- [ ] 实施、验证、审查和交接均有可追溯证据。
- [ ] 无密钥、Token、Cookie 或个人配置进入 `.ai/`。

## 资源

- `scripts/init.sh`：稳定入口。
- `scripts/apply_workflow.py`：档案识别、规则组合与工作流基线生成。
- `scripts/cleanup-legacy-docs.sh`：确认迁移后清理旧 Agent 文档。
- `references/profile-selection.md`：档案证据、选择原则和扩展清单。
