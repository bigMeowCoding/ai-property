# Spec 目录约定

每个需求一个文件：**`YYYY-MM-DD-<slug>.spec.md`**。

## 原则

- **Spec** = 功能 + **§4.8 UI 实现 Prompt**
- **UI-SPEC** = 全局 Token / 组件
- **MasterGo** = 辅助写 spec，默认不提交 raw/截图
- **不建 `notes/`**；技术细节写在 spec 内

## 布局

```
.ai/
├── specs/YYYY-MM-DD-<slug>.spec.md
└── UI-SPEC.md
```

## 工作流

mastergo-extract → sdd-spec-writer → `*.spec.md` + UI-SPEC → 开发

UI Prompt：`sdd-spec-writer/references/ui-prompt-language.md`
