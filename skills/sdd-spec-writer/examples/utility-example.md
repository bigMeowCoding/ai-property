# Spec: 请求重试工具（withRetry）
type: utility

## 1. 需求定义

### 1.1 背景与目标
- 解决什么问题：项目中多处需要网络请求重试逻辑（文件上传、关键表单提交），目前各业务线重复实现，逻辑不统一
- 使用方：所有需要请求重试的业务模块
- 替代方案：如果不做这个，各业务线自行封装 axios interceptors，维护成本高

### 1.2 能力范围（Capability Scope）
- **提供的能力：**
  - [ ] 自动重试失败的 HTTP 请求
  - [ ] 支持指数退避（exponential backoff）策略
  - [ ] 支持自定义重试次数、超时时间
  - [ ] 支持自定义重试条件（如仅对 5xx 错误重试）
  - [ ] 支持请求取消（AbortController）
- **明确不提供的能力：**
  - [ ] 请求缓存（由专门的缓存工具负责）
  - [ ] 请求去重（由专门的去重工具负责）
  - [ ] 自动轮询（由专门的轮询工具负责）

### 1.3 待确认项
| 问题 | 当前假设 | 优先级 |
|------|----------|--------|
| 默认重试次数？ | 建议：3 次 | 阻塞 |
| 默认退避策略？ | 建议：指数退避，基础延迟 1s，最大延迟 10s | 阻塞 |
| 是否支持 jitter（抖动）？ | 建议：支持，防止惊群效应 | 非阻塞 |

---

## 2. 项目资产对齐（Project Asset Alignment）

### 2.1 复用性审查（Reusability Audit）

| 检查项 | 现有资产 | 状态 | 本次策略 |
|--------|----------|------|----------|
| 类似工具 | `axios-retry` 第三方库 | ✅ 已有（外部） | 评估是否引入或自建，考虑包体积和可控性 |
| 请求封装 | `request.ts` 已有 axios 封装 | ✅ 已有 | 在现有封装基础上扩展重试能力 |
| 工具目录 | `src/utils/` 已有工具函数 | ✅ 已有 | 新工具放入 `src/utils/retry/` |
| 测试框架 | Vitest 已配置 | ✅ 已有 | 使用现有框架 |
| 打包配置 | Rollup 已有配置 | ✅ 已有 | 复用现有配置 |

### 2.2 规范对齐（Standard Compliance）

| 规范类别 | 项目规范要求 | 本次应用方式 |
|----------|--------------|--------------|
| **代码规范** | ESLint + Prettier，函数必须有 JSDoc | 所有公开 API 必须有 JSDoc |
| **目录规范** | 工具函数放 `src/utils/`，按功能分子目录 | `src/utils/retry/withRetry.ts` |
| **命名规范** | 工具函数使用 camelCase，文件使用 kebab-case | `withRetry.ts`，类名 `RetryError` |
| **测试规范** | 所有公开 API 必须有单元测试，覆盖率 ≥ 90% | 测试用例覆盖所有边界 |
| **版本规范** | 使用 SemVer，破坏性变更必须发 major | 初始版本 v1.0.0 |

---

## 3. API 设计（API Design）

### 3.1 核心接口

```typescript
/**
 * 对异步函数进行自动重试包装
 * @param fn - 需要重试的异步函数
 * @param options - 重试配置选项
 * @returns 包装后的函数，调用方式与原函数一致
 * @throws MaxRetryExceededError 超过最大重试次数时抛出
 * @throws AbortError 请求被取消时抛出
 */
function withRetry<T extends (...args: any[]) => Promise<any>>(
  fn: T,
  options?: RetryOptions
): T;

/**
 * 创建带有默认配置的重试包装器（偏函数应用）
 * @param defaultOptions - 默认重试配置
 * @returns withRetry 偏函数
 */
function createRetryWrapper(
  defaultOptions: RetryOptions
): <T extends (...args: any[]) => Promise<any>>(fn: T, options?: RetryOptions) => T;
```

### 3.2 配置项 / Options 定义

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| maxRetries | number | 否 | 3 | 最大重试次数（不含首次调用） |
| timeout | number | 否 | 10000 | 单次请求超时时间（ms） |
| backoff | 'fixed' \| 'exponential' \| BackoffFn | 否 | 'exponential' | 退避策略 |
| baseDelay | number | 否 | 1000 | 退避基础延迟（ms） |
| maxDelay | number | 否 | 10000 | 退避最大延迟（ms） |
| jitter | boolean | 否 | true | 是否添加随机抖动（防止惊群） |
| retryCondition | (error: Error) => boolean | 否 | 默认 5xx/网络错误 | 自定义重试条件函数 |
| onRetry | (error: Error, attempt: number) => void | 否 | - | 每次重试时的回调 |
| abortSignal | AbortSignal | 否 | - | 用于取消正在进行的请求 |

```typescript
interface RetryOptions {
  maxRetries?: number;
  timeout?: number;
  backoff?: 'fixed' | 'exponential' | ((attempt: number, baseDelay: number) => number);
  baseDelay?: number;
  maxDelay?: number;
  jitter?: boolean;
  retryCondition?: (error: Error) => boolean;
  onRetry?: (error: Error, attempt: number) => void;
  abortSignal?: AbortSignal;
}
```

### 3.3 返回值定义

> withRetry 返回的函数调用结果与原函数一致，类型自动推断。

```typescript
// 使用示例
const retryFetch = withRetry(fetchUserData, { maxRetries: 5 });
const user = await retryFetch(userId); // 类型与 fetchUserData 返回值一致
```

### 3.4 错误契约

| 错误类型 | 错误码/类名 | 触发场景 | 调用方如何处理 |
|----------|-------------|----------|--------------|
| 超过最大重试 | MaxRetryExceededError | 重试次数耗尽仍未成功 | 降级处理或提示用户 |
| 请求取消 | AbortError | AbortSignal 触发取消 | 忽略结果，清理状态 |
| 参数非法 | ValidationError | options 参数类型错误 | 检查参数后重试 |
| 超时 | TimeoutError | 单次请求超过 timeout | 增加 timeout 或检查网络 |

```typescript
class MaxRetryExceededError extends Error {
  constructor(
    message: string,
    public readonly cause: Error,
    public readonly attempts: number
  ) {
    super(message);
    this.name = 'MaxRetryExceededError';
  }
}

class AbortError extends Error {
  constructor() {
    super('Request was aborted');
    this.name = 'AbortError';
  }
}
```

---

## 4. 使用示例（Usage Examples）

### 4.1 基础用法

```typescript
import { withRetry } from '@utils/retry';
import { fetchUserData } from '@services/user';

// 包装现有请求函数，自动重试 3 次
const retryFetchUser = withRetry(fetchUserData);

// 调用方式与原函数完全一致
const user = await retryFetchUser(userId);
```

### 4.2 高级用法

```typescript
// 自定义重试策略
const retryFetchUser = withRetry(fetchUserData, {
  maxRetries: 5,
  timeout: 15000,
  backoff: 'exponential',
  baseDelay: 500,
  maxDelay: 8000,
  jitter: true,
  retryCondition: (error) => {
    // 仅对网络错误和 5xx 重试，4xx 不重试
    return error instanceof NetworkError || error.status >= 500;
  },
  onRetry: (error, attempt) => {
    console.log(`Retry attempt ${attempt} after error: ${error.message}`);
  },
});
```

### 4.3 创建默认配置的包装器

```typescript
// 创建项目统一的默认重试配置
const apiRetry = createRetryWrapper({
  maxRetries: 3,
  timeout: 10000,
  backoff: 'exponential',
  jitter: true,
});

// 所有 API 请求使用统一配置
const retryFetchUser = apiRetry(fetchUserData);
const retryFetchOrder = apiRetry(fetchOrderData);
const retrySubmitForm = apiRetry(submitForm, { maxRetries: 5 }); // 可覆盖个别配置
```

### 4.4 错误处理

```typescript
import { MaxRetryExceededError, AbortError } from '@utils/retry';

try {
  const user = await retryFetchUser(userId);
} catch (err) {
  if (err instanceof MaxRetryExceededError) {
    // 所有重试都失败了
    showToast('网络异常，请稍后重试');
    reportError(err.cause); // 上报原始错误
  } else if (err instanceof AbortError) {
    // 用户取消了请求
    console.log('Request cancelled');
  } else {
    // 其他错误（如 4xx）
    showToast(err.message);
  }
}
```

### 4.5 请求取消

```typescript
const controller = new AbortController();

const retryFetchUser = withRetry(fetchUserData, {
  abortSignal: controller.signal,
});

// 5 秒后自动取消
setTimeout(() => controller.abort(), 5000);

try {
  const user = await retryFetchUser(userId);
} catch (err) {
  if (err instanceof AbortError) {
    console.log('Request timed out and was cancelled');
  }
}
```

---

## 5. 非功能需求（Non-Functional）

| 指标 | 目标值 | 测试方法 |
|------|--------|----------|
| 包体积 | < 3KB (gzip) | rollup-plugin-analyzer |
| 执行耗时 | < 5ms（单次包装，不含重试等待） | benchmark |
| 兼容性 | Node ≥ 16, Chrome ≥ 90, Safari ≥ 14 | CI 矩阵测试 |
| 无外部依赖 | 是（纯原生实现） | package.json 检查 |
| TypeScript 支持 | 完整类型推断 | tsc 编译测试 |

---

## 6. 测试策略与覆盖率矩阵（Testing Strategy）

### 6.1 测试分层

| 测试类型 | 覆盖目标 | 工具 | 通过标准 |
|----------|----------|------|----------|
| 单元测试 | 所有公开 API、边界输入、错误路径 | Vitest | 覆盖率 ≥ 95%，核心逻辑 100% |
| 基准测试 | 包装函数性能开销 | benchmark.js | 单次包装 < 5ms |
| 集成测试 | 在真实 axios/fetch 场景中的使用 | 实际项目引入 | 无类型错误，重试行为正确 |

### 6.2 功能覆盖率矩阵（Coverage Matrix）

| 功能点 | 测试用例 | 场景覆盖 | 状态 |
|--------|----------|----------|------|
| 基础调用（无需重试） | 函数一次调用成功，直接返回结果 | 1/1 | ⬜ 待实现 |
| 固定退避重试 | 第 1 次失败，第 2 次成功，验证延迟固定 | 1/1 | ⬜ 待实现 |
| 指数退避重试 | 连续失败 3 次后成功，验证延迟 1s→2s→4s | 1/1 | ⬜ 待实现 |
| 最大重试次数 | 连续失败超过 maxRetries，抛出 MaxRetryExceededError | 1/1 | ⬜ 待实现 |
| 超时机制 | 单次请求超过 timeout，触发 TimeoutError | 1/1 | ⬜ 待实现 |
| 重试条件过滤 | 4xx 错误不重试，5xx 错误重试 | 2/2 | ⬜ 待实现 |
| 抖动随机性 | 多次重试验证延迟有随机偏移 | 1/1 | ⬜ 待实现 |
| 请求取消 | AbortSignal 触发后，当前请求立即停止 | 1/1 | ⬜ 待实现 |
| 取消后不再重试 | 取消后即使还有重试次数也不再执行 | 1/1 | ⬜ 待实现 |
| onRetry 回调 | 每次重试触发回调，参数正确 | 1/1 | ⬜ 待实现 |
| createRetryWrapper | 偏函数应用，默认配置生效，可覆盖 | 2/2 | ⬜ 待实现 |
| 类型推断 | 包装后函数返回类型与原函数一致 | 1/1 | ⬜ 待实现 |
| 错误类型识别 | MaxRetryExceededError / AbortError / TimeoutError 可被 instanceof 识别 | 3/3 | ⬜ 待实现 |

### 6.3 复杂功能场景拆解（Complex Scenario Breakdown）

**示例：指数退避 + 抖动 + 取消的组合场景**

| 场景编号 | 输入条件 | 执行过程 | 预期结果 | 测试类型 |
|----------|----------|----------|----------|----------|
| SC-01 | 首次调用成功 | 无重试 | 立即返回结果 | 单元测试 |
| SC-02 | 第 1 次失败，第 2 次成功 | 延迟 1s（±抖动）后重试 | 返回最终结果 | 单元测试 |
| SC-03 | 连续失败 3 次，第 4 次成功 | 延迟 1s→2s→4s（±抖动） | 返回最终结果 | 单元测试 |
| SC-04 | 连续失败超过 maxRetries=3 | 延迟 1s→2s→4s，然后停止 | 抛出 MaxRetryExceededError，attempts=4 | 单元测试 |
| SC-05 | 第 2 次重试时触发取消 | 第 1 次失败后延迟 1s，第 2 次执行中取消 | 立即抛出 AbortError，不再继续重试 | 单元测试 |
| SC-06 | 超时与重试同时触发 | timeout=500ms，baseDelay=1000ms | 超时优先，抛出 TimeoutError，不重试 | 单元测试 |
| SC-07 | 自定义 retryCondition 过滤 | 4xx 错误，retryCondition 返回 false | 立即抛出错误，不重试 | 单元测试 |
| SC-08 | 并发调用同一包装函数 | 同时调用 retryFetchUser(1) 和 retryFetchUser(2) | 两次调用独立重试，互不干扰 | 单元测试 |

---

## 7. 任务拆分与并行计划（Task Breakdown）

### 7.1 拆分原则

- **核心先行**：先完成最小可用版本（MVP），确保 API 契约稳定
- **测试并行**：核心逻辑开发的同时，测试用例可以同步编写
- **2 个 Agent 并行**：一个负责核心实现，一个负责测试 + 文档 + 工程化

### 7.2 任务卡片（Task Cards）

#### 模块 A：核心实现（Agent-1 负责）

| 任务 ID | 任务名称 | 类型 | 输入 | 输出 | 依赖 | 验收点 |
|---------|----------|------|------|------|------|--------|
| T-A1 | 核心重试逻辑实现 | core | Spec API 设计 | `withRetry.ts` + 类型定义 | 无 | 所有公开 API 有实现，通过基础用例 |
| T-A2 | 退避策略实现（fixed + exponential） | core | 退避算法定义 | `backoff.ts` | T-A1 | 固定退避和指数退避计算正确 |
| T-A3 | 错误类型定义 | core | 错误契约定义 | `errors.ts`（MaxRetryExceededError / AbortError / TimeoutError） | T-A1 | 所有错误类型可被正确 catch 和 instanceof 识别 |
| T-A4 | 请求取消支持 | core | AbortController API | `withRetry.ts` 扩展取消逻辑 | T-A1 | AbortSignal 触发后请求立即停止 |
| T-A5 | createRetryWrapper 偏函数 | core | 默认配置合并逻辑 | `createRetryWrapper.ts` | T-A1 | 默认配置生效，可覆盖，类型推断正确 |

> **模块 A 交付物：** 可运行的核心库代码  
> **并行条件：** T-A1 完成后，模块 B 启动

---

#### 模块 B：测试与工程化（Agent-2 负责）

| 任务 ID | 任务名称 | 类型 | 输入 | 输出 | 依赖 | 验收点 |
|---------|----------|------|------|------|------|--------|
| T-B1 | 单元测试用例 | test | Spec API 设计 + 错误契约 + 场景拆解 | `withRetry.test.ts`（覆盖率 ≥ 95%） | T-A1 | 所有公开 API 有测试，SC-01~08 全覆盖 |
| T-B2 | 基准测试 | test | 核心实现 | `benchmark.ts` + 报告 | T-A1 | 单次包装 < 5ms，可复现 |
| T-B3 | 使用文档 + README | docs | 所有使用示例 | `README.md` + `CHANGELOG.md` | T-A1, T-B1 | 新用户 5 分钟可上手，示例可直接运行 |
| T-B4 | 打包与发布配置 | infra | 核心实现 | `rollup.config.ts` + CI 脚本 | T-A1 | 产出 esm/cjs/umd 三种格式，类型文件完整 |

> **模块 B 交付物：** 完整测试 + 文档 + 工程化配置  
> **并行条件：** 依赖模块 A 的 T-A1 完成后启动，与 T-A2~A5 可部分并行

### 7.3 并行时序图

```
Day 1-2: [Agent-1] T-A1 核心重试逻辑
         │
         ▼
Day 2-3: [Agent-1] T-A2 退避策略 + T-A3 错误类型 + T-A4 取消支持 + T-A5 偏函数
         [Agent-2] T-B1 单元测试（T-A1 完成后启动） ──┐ 部分并行
         │                                          │
Day 4:   [Agent-2] T-B2 基准测试 + T-B3 文档        │
         │                                          │
Day 5:   [Agent-2] T-B4 打包配置 + CI               │
         [All] 集成发布                              │
```

### 7.4 契约冻结点

| 检查点 | 内容 | 责任方 |
|--------|------|--------|
| CK-1 | API 签名（withRetry / createRetryWrapper / RetryOptions）冻结 | Agent-1 |
| CK-2 | 错误类型与错误码确认（MaxRetryExceededError / AbortError / TimeoutError） | Agent-1 + Agent-2 |
| CK-3 | 默认配置值确认（maxRetries=3, timeout=10000, backoff=exponential） | Agent-1 |
| CK-4 | 包输出格式（esm/cjs/umd）和入口文件确认 | Agent-2 |

---

## 8. 验收注意点与重点场景（Acceptance Checklist）

### 8.1 必验场景（Must Verify）

| 优先级 | 场景 | 验证方式 | 通过标准 |
|--------|------|----------|----------|
| 🔴 P0 | 所有公开 API 正常调用 | 代码执行 | 返回值符合类型定义，类型推断正确 |
| 🔴 P0 | 重试逻辑正确执行 | 代码执行 | 失败时自动重试，成功后停止 |
| 🔴 P0 | 指数退避延迟正确 | 代码执行 | 延迟时间符合 1s→2s→4s 规律 |
| 🔴 P0 | 超过最大重试次数正确抛错 | 代码执行 | 抛出 MaxRetryExceededError，包含原始错误和尝试次数 |
| 🟡 P1 | 请求取消立即停止 | 代码执行 | AbortSignal 触发后，当前请求立即停止，不再重试 |
| 🟡 P1 | 自定义重试条件生效 | 代码执行 | 4xx 错误不重试，5xx 错误重试 |
| 🟡 P1 | 性能指标达标 | benchmark | 单次包装 < 5ms |
| 🟢 P2 | 文档完整性 | 人工阅读 | 基础/高级/错误处理/取消用法示例齐全 |

### 8.2 易遗漏场景（Easy to Miss）

| 风险点 | 为什么容易漏 | 验收方法 |
|--------|--------------|----------|
| 内存泄漏 | 定时器/事件未清理 | 长时间运行后检查内存占用，验证 setTimeout 已清除 |
| 并发调用隔离 | 同一包装函数并发执行 | 同时发起多个请求，验证各自独立重试，互不干扰 |
| 类型导出 | 忘记导出类型定义 | 在 TS 项目中引入验证 RetryOptions / RetryError 类型推断 |
| 副作用隔离 | 修改全局状态 | 验证多次调用互不干扰，onRetry 回调不共享状态 |
| 抖动范围 | 抖动导致延迟为负或过大 | 验证抖动后的延迟在合理范围内 [0.5*delay, 1.5*delay] |
| 取消时清理 | 取消后定时器未清除 | 验证取消后 setTimeout 已清除，不会泄露 |

### 8.3 回归检查（Regression Check）

| 影响面 | 检查项 | 验证方式 |
|--------|--------|----------|
| 现有项目引用 | 升级后现有调用点是否报错 | 在 1-2 个现有项目中试升级 |
| 包体积 | 新增工具是否显著增加产物体积 | 对比构建产物体积 |
| 现有请求封装 | 与现有 `request.ts` 是否兼容 | 在现有封装上集成 withRetry 测试 |

---

## 9. 发布与版本

- 初始版本：v1.0.0
- 破坏性变更策略：
  - 新增配置项：minor 版本升级
  - 修改默认配置值：major 版本升级
  - 删除/重命名 API：major 版本升级
- 文档发布位置：项目内部文档站 + README
