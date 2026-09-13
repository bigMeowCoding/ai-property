---
name: layered-architecture
description: 设计、实现或审查 Java 21 / Spring Boot 3 的 Controller、Application/Service、Domain、Infrastructure 分层与依赖方向。涉及新增接口、业务用例、领域状态机、Repository、外部服务适配器、跨层重构或模块边界时使用；若仓库已有架构约定，优先保持现有边界。
---

# Spring 分层架构

让协议、业务规则和技术实现沿稳定方向依赖，避免为了形式增加无业务价值的层。

## 工作流

1. 读取 `AGENTS.md`、需求、相邻实现和测试，列出入口、状态变化、外部依赖与事务边界；只有实际文件和可运行结果属于现状，Spec/Task 中的方案必须标为待实现。
2. 先确定用例和失败语义，再放置类；不要从注解或目录模板反推设计。
3. 沿调用链检查依赖方向、跨层 DTO、异常转换和测试入口。
4. 完成后搜索 Controller 直连 Repository、Domain 依赖 HTTP、基础设施 DTO 泄漏等反向依赖。

## 分层职责

```text
Controller / Protocol
        ↓ request/response DTO
Application / Service
        ↓ domain command/value
Domain
        ↑ port/interface
Infrastructure
```

- **Controller**：解析 HTTP、触发 Bean Validation、调用应用用例、映射状态码；不编排多个 Repository，不承载业务状态转换。
- **Application/Service**：编排一个业务用例、定义事务边界、校验资源归属、协调领域对象和端口；不返回 Servlet、SSE 客户端或供应商 DTO。
- **Domain**：表达状态机、不变量和值语义；让非法状态转换在最接近规则的位置失败。简单 CRUD 不必强造聚合、领域事件或抽象工厂。
- **Infrastructure**：实现 JPA、模型客户端、加密、时钟、ZIP 等端口；在边界处转换外部 DTO、异常和资源生命周期。

## 依赖规则

- 只允许外层依赖内层；Domain 不依赖 Controller 或供应商客户端。
- Repository 接口放在其消费者能够稳定拥有的位置，实现放在 Infrastructure。
- 请求 DTO 与响应 DTO 分离；不得从 Controller 直接序列化 JPA Entity。
- 配置类只负责装配技术组件；业务分支不能藏在 `@Configuration`。
- 共享代码只有在存在真实的第二个消费者时再提取。
- 输出中区分“已存在”“Spec 要求”“建议方案”；为建议的包名、接口或类名不得伪造为仓库现状。

## 验证

- 从一个真实接口追踪到数据库或外部模型，再追踪错误返回和状态落库。
- 单元测试领域状态与边界；集成测试层间协作、事务和技术适配器。
- 检查公共契约没有因内部重构变化，且没有增加未使用的层或接口。

## 常见失误

- Controller 注入 Repository 或拼装领域状态。
- Service 既返回 `ResponseEntity` 又处理持久化。
- Domain 引用 OpenAI/Kimi、Jackson、Servlet 或 ZIP 实现类型。
- 为每个类机械创建接口，形成只有一个实现且没有边界价值的间接层。
- 把事务注解放在 Controller、私有方法或同类自调用的方法上。
