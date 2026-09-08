# SDD Spec Writer Skill

> 支持 SDD（Specification-Driven Development）模式，根据功能类型自动生成差异化 Spec 文档，并输出可并行的任务拆分计划。

## 目录结构

```
sdd-spec-writer/
├── SKILL.md                    # 主 Skill 定义文件（系统提示词）
├── README.md                   # 本文件
├── templates/                  # 三种类型的 Spec 模板
│   ├── business.md             # 业务功能模板
│   ├── utility.md              # 底层工具/库模板
│   └── shared.md               # 业务公共组件/工具模板
└── examples/                   # 完整示例
    ├── business-example.md     # 示例：手机号验证码登录
    ├── utility-example.md      # 示例：请求重试工具
    └── shared-example.md       # 示例：通用表格组件
```

## 快速开始

### 1. 安装

将本文件夹放入你的 Agent Skills 目录（具体路径取决于你使用的 Agent 框架）：

```bash
# 例如 Kimi Skills 目录
cp -r sdd-spec-writer ~/.kimi/skills/

# 例如 Cursor Rules 目录
cp -r sdd-spec-writer .cursor/rules/sdd-spec-writer
```

### 2. 使用

向 Agent 描述你的需求，Agent 会自动：

1. **识别类型**：判断是业务功能 / 底层工具 / 公共组件
2. **加载模板**：从 `templates/` 目录加载对应模板
3. **生成 Spec**：结合你的需求，生成完整的 Spec 文档
4. **拆分任务**：拆分为 2-3 个可并行的模块，分配给不同 Agent

### 3. 示例对话

**业务功能示例：**
```
用户：做一个订单退款页面，支持手机号+验证码登录
Agent：识别为 business 类型 → 加载 templates/business.md → 生成完整 Spec
```

**底层工具示例：**
```
用户：封装一个请求重试的工具函数，支持指数退避
Agent：识别为 utility 类型 → 加载 templates/utility.md → 生成完整 Spec
```

**公共组件示例：**
```
用户：做一个所有业务线都能用的图片上传组件，支持裁剪和压缩
Agent：识别为 shared 类型 → 加载 templates/shared.md → 生成完整 Spec
```

## 核心特性

### 1. 三种类型差异化模板

| 类型 | 核心关注点 | 典型产出 |
|------|-----------|----------|
| **business**（业务功能） | 用户旅程、业务规则、交互状态、验收标准 | 页面、弹窗、表单、流程状态机 |
| **utility**（底层工具/库） | API 契约、输入输出、性能边界、兼容性 | 工具函数、Hook、SDK |
| **shared**（公共组件/工具） | 复用场景、配置化接口、Props 设计、版本兼容 | 业务组件、公共 Hook、工具库 |

### 2. 项目资产对齐

每个 Spec 强制包含：
- **复用性审查**：检查项目中是否已有类似功能，避免重复造轮子
- **规范对齐**：明确遵循的 UI 规范、代码规范、目录规范等

### 3. 测试覆盖率矩阵

- 功能点 → 测试用例 → 场景覆盖，确保 100% 覆盖
- 复杂功能拆解到原子场景，每个场景一个测试用例

### 4. 任务拆分与并行计划

- 拆分为 2-3 个模块，每个 Agent 负责一个模块
- 明确模块边界、依赖关系、契约冻结点
- 提供并行时序图，指导开发排期

### 5. 验收注意点

- **必验场景**：P0/P1/P2 分级，验收时必须逐一验证
- **易遗漏场景**：开发时容易忽略的点，验收时重点抽查
- **回归检查**：本次改动可能影响的其他功能

## 模板使用指南

### 业务功能模板（business.md）

适用于：页面、功能模块、业务流程

关键章节：
- 用户旅程与交互（User Journey）
- 业务规则（Business Rules）
- 异常场景与兜底策略（Exception Handling）
- 交付物清单（Artifacts）

### 底层工具模板（utility.md）

适用于：工具函数、Hook、SDK、插件

关键章节：
- API 设计（API Design）
- 使用示例（Usage Examples）
- 非功能需求（Non-Functional）
- 错误契约（Error Contract）

### 公共组件模板（shared.md）

适用于：业务公共组件、通用工具、可复用模块

关键章节：
- 复用场景分析（Usage Scenarios）
- 接口设计（Interface Design）
- 扩展点（Slots / Extension Points）
- 版本与兼容（Version & Compatibility）

## 自定义配置

你可以根据团队实际情况，修改模板中的以下部分：

1. **规范对齐表格**：填入你们团队的具体规范（弹窗规范、表单规范、目录规范等）
2. **测试工具**：将 Vitest/Testing Library/Playwright 替换为你们使用的工具
3. **目录结构**：调整 `src/components/`、`src/utils/` 等路径为你们项目的实际路径
4. **Design Token**：填入你们设计系统的 Token 名称

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v2.3.0 | 2024-XX-XX | 新增项目资产对齐、测试覆盖率矩阵、验收注意点 |
| v2.2.0 | 2024-XX-XX | 新增任务拆分与并行计划 |
| v2.1.0 | 2024-XX-XX | 新增多模式模板（business/utility/shared） |
| v2.0.0 | 2024-XX-XX | 初始版本 |

## 贡献

欢迎提交 Issue 和 PR，改进模板或新增示例。

## License

MIT
