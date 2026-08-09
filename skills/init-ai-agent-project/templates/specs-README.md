# Spec 目录约定

每个需求一个文件：**`YYYY-MM-DD-<slug>.spec.md`**。

## 原则

- **Spec** = 可验收需求、技术约束、测试矩阵；UI 需求直接写入对应 spec
- **设计稿** = 辅助写 spec，默认不提交 raw/批量截图
- **不建 `notes/`**；技术细节写在 spec 内

## 布局

```
.ai/
└── specs/YYYY-MM-DD-<slug>.spec.md
```

## 工作流

需求/设计输入 → `*.spec.md` → 实现与测试 → 验收
