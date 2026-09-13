# DevLoop 已确认契约基线

本文件记录当前 V1 Spec 已确认的不变量，不替代两端 Spec。端点路径、JSON 字段名、ID 类型、时间格式等未在 Spec 冻结的细节，必须在实现 Task 中对齐并通过契约测试固化。

## 资源与关系

```text
Project
├── ConversationMessage *
├── Document(SPEC) 0..1 current
├── Document(TASKS) 0..1 current
└── Model generation operations

ModelConfig: system-wide single configuration
```

- 消息、文档和耗时操作均按项目隔离。
- Tasks 的 `sourceDocumentId` 引用同项目当前 Spec。
- 每项目每种文档类型最多一个当前文档。

## 文档与确认

- 文档类型仅 `SPEC`、`TASKS`。
- Tasks 只能基于当前已确认 Spec 生成。
- 确认顺序为 Spec → Tasks。
- 覆盖或修改上游 Spec 时，下游 Tasks 的确认状态必须可靠失效。
- 保存内容可恢复；单文件下载必须与数据库最后保存内容逐字一致。

## 流式事件语义

| 语义 | 说明 |
| --- | --- |
| start | 服务端接受生成并建立上下文 |
| delta | 新增、有序的内容片段 |
| complete | 正常结束，内容可以提交为完成状态 |
| error | 生成失败，携带安全且稳定的错误语义 |
| cancelled | 客户端或服务端取消，资源已清理 |

- 供应商事件必须先转换成 DevLoop 内部事件。
- 模型失败不删除已经保存的用户消息。
- 重试和同项目并发不能产生重复消息或重复当前文档。

## 错误类别

- 参数或结构校验失败。
- 资源不存在。
- 项目归属不匹配。
- 状态或确认顺序冲突。
- 模型上游失败或超时。
- 服务内部错误。

错误响应禁止包含堆栈、API Key、完整 Authorization、SQL 或供应商敏感原文。

## 模型配置

- 系统只维护一个 OpenAI 兼容配置：API Base URL、加密 API Key、Model Name、更新时间。
- 读取接口不返回完整密钥，只返回是否已配置。
- 连接测试成功或返回脱敏错误，不改变已有业务数据。

## 导出

- 可以下载当前最后保存的 `spec.md` 和 `tasks.md`。
- 只有当前 Spec 与 Tasks 均确认时才能导出 ZIP。
- ZIP 根目录为 `devloop-{project-name}/`，包含：
  - `specs/spec.md`
  - `tasks/tasks.md`
  - `README.md`
- README 说明文档关系、推荐阅读顺序和生成时间。
- 项目名称必须安全规范化，任何条目都不能逃逸目标根目录。

## 变更门禁

以下变化必须同步服务端、Web 端、契约 fixture 和测试：

- 字段增加、删除、改名、类型或可空性变化。
- 枚举值、状态转换或确认门槛变化。
- HTTP 状态码、业务错误码或错误结构变化。
- SSE 事件名、字段、顺序或终态规则变化。
- 文件名、媒体类型、Content-Disposition 或 ZIP 目录结构变化。
