# AGENT.md

## 必读规范

**本项目的所有编码规范已整理至 [`project_conventions.md`](./project_conventions.md)**

> 在执行任何代码变更前，**必须先阅读** `project_conventions.md`，并严格遵守其中的规范。

**核心原则：**
- ✅ 使用 `@/` 路径别名，禁止相对路径
- ✅ 所有组件使用 `React.memo` + `useCallback`
- ✅ 过滤逻辑使用 `useMemo`
- ✅ 错误处理统一使用 `@/lib/errors`
- ✅ Hook 按 feature 拆分到子目录
- ✅ 类型通过 barrel 文件集中暴露
- ❌ 禁止使用 `any` 类型
- ❌ 禁止 `console.log`（使用 warn/error）

---

## 项目规则

### 开发命令

| 命令 | 用途 |
|------|------|
| `bun dev` | 启动开发服务器 (http://localhost:3000) |
| `bun build` | 构建生产版本 |
| `bun start` | 启动生产服务器 |
| `bun lint` | 运行 ESLint 代码检查 |
| `bun test` | 运行单元/集成测试 |
| `npx playwright test` | 运行 E2E 测试 |

### 构建规则

**所有代码变更必须通过以下检查：**

1. **Lint 检查** - 每次提交前必须运行：
   ```bash
   bun lint
   ```

2. **类型检查** - TypeScript 类型必须正确（通过 LSP 或 `bun build`）

3. **构建验证** - 重要变更后必须验证构建：
   ```bash
   bun build
   ```

### 测试规则

**所有代码变更必须运行测试确保功能正确：**

1. **Bun 测试** - 每次代码变更后必须运行：
   ```bash
   bun test
   ```

2. **E2E 测试** - 页面/UI 变更后必须运行：
   ```bash
   npx playwright test
   ```

3. **覆盖率检查** - 重要功能变更后运行：
   ```bash
   bun test --coverage
   ```

### 测试风格规范

- **颗粒度**: 优先行为测试，避免测试实现细节
- **文件大小**: 单个测试文件不超过 100 行
- **Mock**: 只 Mock 外部依赖 (fetch/localStorage)，不 Mock 内部函数
- **E2E**: 仅测试页面加载，不测试复杂交互

### CI 集成

- 所有 PR 和 Push 必须通过 `bun test` 和 `bun lint`
- E2E 测试在本地运行，不进入 CI
- 构建检查：`bun build` 必须成功

### 代码变更流程

```
1. 阅读 project_conventions.md 了解项目规范
2. 开发功能 (严格遵守规范)
3. bun lint    # 代码检查
4. bun test    # 运行测试
5. bun build   # 构建验证（重要变更）
6. 提交代码
```

---

## 规范速查

### 导入路径
```typescript
// ✅ 使用 @/ 路径别名
import { Button } from '@/components/ui/button';

// ❌ 禁止使用相对路径
import { Button } from '../../../components/ui/button';
```

### 组件导出
```typescript
import { memo } from 'react';

function Component({ prop }: Props) {
  return <div>{prop}</div>;
}

export default memo(Component);
```

### 错误处理
```typescript
import { parseApiError } from '@/lib/errors';

const message = parseApiError(err);
```

### 类型导出
```typescript
import type { Skill } from '@/types';  // 通过 barrel 文件
```
