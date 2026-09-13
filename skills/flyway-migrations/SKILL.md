---
name: flyway-migrations
description: 创建、修改或审查 Spring Boot 3 项目的 Flyway 版本迁移、MySQL 8 DDL、索引、约束、初始化数据或兼容发布步骤时使用。适用于新建表、字段演进、回填、唯一性与外键设计以及迁移失败诊断。
---

# Flyway 迁移

把数据库结构视为不可覆盖的版本历史，并用真实 MySQL 验证前向迁移。

## 工作流

1. 读取实际存在的全部迁移、实体映射、目标查询和部署约束，确认下一个未占用版本；Spec、Task 或示例中的 SQL 不算已存在迁移。
2. 区分结构、数据回填和约束收紧；高风险变更拆成可兼容的多个版本。
3. 检查旧应用与新结构的共存窗口、锁表风险、默认值和回滚策略。
4. 在空库和已有上一版本结构上运行迁移，再执行 Repository/事务测试。

## 规则

- 文件使用 `V<version>__<description>.sql`；已在任何共享环境执行的迁移禁止修改。
- 使用 MySQL 8 语法、字符集和索引能力，不复制 PostgreSQL 的 UUID、TIMESTAMPTZ 或 CONCURRENTLY 语法。
- 表、列、长度、可空性、枚举存储、外键和删除策略必须与实体一致。
- 为真实查询和外键设计索引；联合索引顺序基于过滤、排序和选择性证据。
- 新增非空列优先采用“可空/默认值 → 回填 → 校验 → 收紧”的分步路径。
- 破坏性删除或重命名必须经过兼容部署和数据验证，不能作为第一步。
- `baseline-on-migrate` 不是默认开关；只在接管已有非 Flyway 数据库且完成基线审计时启用。
- 生产数据不能混入测试种子；测试 fixture 由测试代码或专用 profile 管理。
- 引用“当前表”“已有 V1”或具体字段前必须给出实际文件证据；工程尚未初始化时只输出建议初始迁移。

## DevLoop 强制约束

- `Document.type` 只允许 `SPEC`、`TASKS`。
- 每项目每种类型最多一个当前文档。
- Tasks 的 `source_document_id` 必须引用同项目当前 Spec；若单个外键不能表达完整规则，结合复合约束、事务校验和集成测试实现。
- Project、ConversationMessage、Document、ModelConfig 的 PRD 核心字段由迁移创建。

## 验证

- 空 MySQL 8 容器可从零迁移到最新版本。
- 重启时迁移幂等，`flyway validate` 无 checksum 或顺序错误。
- 负向测试证明唯一性、外键、类型和跨项目引用约束生效。
- 检查最终 diff 没有改写历史迁移、引入方言错误或遗漏实体同步。

## 常见失误

- 使用单下划线文件名或重复版本。
- 为修错直接编辑已经执行的 SQL。
- 用 JPA 自动建表替代 Flyway 事实源。
- 从 PostgreSQL 示例复制 `gen_random_uuid()`、`TIMESTAMPTZ` 或并发索引语法。
- 只验证空库，未验证已有数据上的回填和约束收紧。
