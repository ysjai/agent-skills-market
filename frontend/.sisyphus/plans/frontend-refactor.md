# 前端工程重构优化计划

## TL;DR

> **目标**: 将 MVP 阶段的 Next.js 工程重构为符合 2025 年最佳实践的整洁架构
>
> **核心改进**:
>
> - 修复 Tailwind CSS v4 配置问题（删除遗留 v3 配置文件）
> - 启用严格的 ESLint 和 TypeScript 检查
> - 重构目录结构（Feature-based + 精简合并）
> - 优化状态管理（提取 Skills 页面状态，拆分 useFileTree hook）
> - 统一错误处理逻辑，修复类型安全问题
> - 添加性能优化（React.memo, useMemo）
>
> **规模**: 大型重构（预计 5-7 天）
> **并行度**: YES - 4 个 Wave，最多 7 个任务并行
> **关键路径**: Wave 0 → Wave 1 → Wave 2 → Wave 3 → Wave 4

---

## 背景与上下文

### 原始需求

用户希望对 MVP 阶段的 Next.js 前端工程进行全面重构优化，解决追赶时间导致的代码整洁度、编码规范和最佳实践问题。

### 技术债务识别

通过并行深度分析发现以下主要问题：

1. **配置问题**:

   - Tailwind CSS v4 配置遗留 v3 配置文件
   - ESLint 未配置（仅设置了 ignoreDuringBuilds）
   - TypeScript 严格检查被禁用（ignoreBuildErrors: true）
2. **目录结构问题**:

   - `i18n/` 和 `messages/` 分离导致配置分散
   - `components/` 混合 12 个根组件 + 2 个 feature 文件夹
   - 测试文件分散（`lib/__tests__/` + `lib/*.test.ts`）
   - `app/lib/auth.ts` 4 行代码导致跨目录导入
   - `lib/file-icons.tsx` 是 React 组件但放在 lib/
3. **代码质量问题**:

   - Skills 页面管理 15+ useState（287 行）
   - useFileTree hook 425 行，职责过多
   - `parseApiError` 在 3 个地方重复
   - Monaco Editor 使用 `any` 类型
   - 10+ TypeScript 错误被隐藏
4. **架构问题**:

   - 缺少全局状态管理方案
   - 无性能优化（React.memo, useMemo）
   - 错误处理逻辑不统一

### Metis 审查发现

**关键修正**:

- ✅ Tailwind v4 已经安装，问题是有遗留的 `tailwind.config.ts` 文件需要删除
- ✅ ESLint 从未配置过，需要先创建配置才能启用
- ✅ 测试框架混用（vitest vs bun:test）需要统一

**风险评估**:

- 启用严格检查可能暴露 50+ 错误
- Tailwind 配置迁移可能导致样式丢失
- 文件移动可能破坏导入路径

---

## 工作目标

### 核心目标

将技术债务严重、结构混乱的 MVP 代码库重构为：

1. **配置规范**: Tailwind v4 原生配置，严格 ESLint/TypeScript
2. **结构清晰**: Feature-based 目录，无重复/分散文件
3. **代码质量**: 统一错误处理，完整类型安全
4. **性能优化**: 合理的 memoization 和状态管理

### 具体交付物

- 修复后的配置文件（next.config.js, eslint.config.mjs）
- 精简的目录结构（合并 i18n，重组 components）
- 重构后的 Hooks（useSkills, useSkillDialogs, useTreeState 等）
- 统一的错误处理模块（lib/errors.ts）
- 新增的全局状态管理（Zustand stores）

### 完成标准

- [x] `bun run build` 0 错误 0 警告
- [x] `bun run lint` 0 错误
- [x] `npx tsc --noEmit` 0 类型错误
- [x] `bun test` 所有测试通过
- [x] 所有文件移动到正确位置，无跨目录导入

### 必须包含

- 配置修复（Tailwind v4, ESLint, TypeScript）
- 目录结构重组
- 代码质量修复（错误处理，类型安全）
- 状态管理优化

### 必须不包含（范围边界）

- ❌ 不添加新功能
- ❌ 不改变业务逻辑行为
- ❌ 不升级 React/Next.js 版本
- ❌ 不引入非必要的新依赖

---

## 验证策略

### 测试策略

**现有测试基础设施**:

- Bun Test + @testing-library（单元测试）
- Playwright（E2E 测试）
- 6 个测试文件已存在

**测试决策**:

- 本次重构 **包含** 测试修复（移动测试文件，修复导入）
- **不包含** 新增测试覆盖（保持现有测试通过即可）
- 每个重构任务包含 Agent-Executed QA 场景

### QA 策略

**所有任务必须包含 Agent-Executed QA Scenarios**:

- **配置任务**: 验证命令执行结果（exit code, 输出内容）
- **文件移动**: 验证文件存在性，导入路径检查
- **代码重构**: 验证编译通过，运行时行为正确
- **UI 组件**: 使用 Playwright 截图对比

---

## 执行策略

### 🛑 重要执行规则：Wave 停止检查点

**CRITICAL RULE**: 每个 Wave 完成后**必须停止**，等待用户验收后才能继续下一个 Wave。

**执行流程**:

```
Wave 0 完成 → 🛑 STOP → 用户验收 → 用户发出 "继续 Wave 1" 指令 → Wave 1 开始
Wave 1 完成 → 🛑 STOP → 用户验收 → 用户发出 "继续 Wave 2" 指令 → Wave 2 开始
...以此类推
```

**验收清单**（每个 Wave 完成后必须检查）:

- [x] 所有 Wave 任务完成
- [x] 所有 QA 场景通过
- [x] 构建/测试通过
- [x] 代码审查完成
- [ ] 用户确认 "继续"

**为什么重要**:

- **风险控制**: 重构风险高，分批验收可及时发现问题
- **回滚粒度**: 如果 Wave 失败，可以只回滚当前 Wave
- **质量把关**: 用户可以在每个阶段检查是否符合预期

---

### 工作流程说明（单人开发模式）

**当前工作模式**: 单人开发，直接在 `main` 分支上工作

**工作流程**:

1. 每个 Wave 的任务直接在 `main` 分支上执行
2. Wave 完成后，所有更改已提交到 `main` 分支
3. 用户验收后，继续下一个 Wave（无需切换分支或合并）
4. 如果某个 Wave 需要回滚，使用 `git reset` 或 `git revert`

**注意**: 如果是多人协作，建议为每个 Wave 创建功能分支（如 `refactor/wave-1`），Wave 完成后再合并到 `main`。但单人工作时，直接在 main 分支工作更简单高效。

---

### 并行执行波次

```
Wave 0 (基础准备 - 立即执行):
├── T0.1: 创建功能分支 + 基线测试 [quick]  ← 注：单人模式直接在 main 执行
├── T0.2: 创建 ESLint 配置文件 [quick]
├── T0.3: 创建 Zustand Store 类型定义 [quick]
└── T0.4: 更新 next.config.js 移除 ignores [quick]
└── ✅ Wave 0 已完成

Wave 1 (配置修复 - 高优先级):
├── T1.1: 删除 tailwind.config.ts [quick]
├── T1.2: 迁移 Tailwind 主题到 globals.css [visual-engineering]
├── T1.3: 修复所有 TypeScript 错误 [unspecified-high]
└── T1.4: 修复所有 ESLint 错误 [unspecified-high]
└── ✅ Wave 1 已完成

Wave 2 (目录结构 - 中等优先级):
├── T2.1: 移动 i18n 文件（messages/ → i18n/locales/） [quick]
├── T2.2: 移动组件（file-icons.tsx → components/ui/） [quick]
├── T2.3: 移动 auth.ts（app/lib/ → lib/） [quick]
├── T2.4: 重组 components/ 目录结构 [unspecified-high]
└── T2.5: 合并测试文件（删除重复） [quick]
└── ✅ Wave 2 已完成

Wave 3 (架构重构 - 中等优先级):
├── T3.1: 统一错误处理（提取 parseApiError） [quick]
├── T3.2: 修复 Monaco Editor 类型（移除 any） [quick]
├── T3.3: 拆分 useFileTree hook [deep]
├── T3.4: 拆分 Skills 页面状态（创建 useSkillsStore） [deep]
└── T3.5: 添加 barrel exports（index.ts） [quick]
└── ✅ Wave 3 已完成

Wave 4 (性能优化 - 低优先级):
├── T4.1: 添加 React.memo 到 SkillCard [quick]
├── T4.2: 添加 useMemo 到过滤逻辑 [quick]
├── T4.3: 优化 FileTree 渲染 [unspecified-high]
└── T4.4: 最终构建验证 [unspecified-high]
└── ✅ Wave 4 已完成

Wave FINAL (最终验证 - 独立并行):
├── TF1: 计划合规审计（oracle）
├── TF2: 代码质量检查（unspecified-high）
└── TF3: 完整回归测试（unspecified-high）
└── ✅ Wave FINAL 已完成

关键路径: Wave 0 → 🛑 → Wave 1 → 🛑 → Wave 2 → 🛑 → Wave 3 → 🛑 → Wave 4 → 🛑 → FINAL
并行加速: Wave 内部任务高度并行，但 Wave 之间必须等待用户确认
```

### 依赖矩阵

| 任务 | 依赖       | 阻塞         | 可并行组 |
| ---- | ---------- | ------------ | -------- |
| T0.1 | -          | T0.2-4, W1   | Wave 0   |
| T0.2 | T0.1       | T1.3-4       | Wave 0   |
| T0.3 | -          | T3.4         | Wave 0   |
| T0.4 | -          | T1.3-4       | Wave 0   |
| T1.1 | T0.1       | T1.2         | Wave 1   |
| T1.2 | T1.1       | T4.4         | Wave 1   |
| T1.3 | T0.1, T0.4 | W2, W3, W4   | Wave 1   |
| T1.4 | T0.1, T0.2 | W2, W3, W4   | Wave 1   |
| T2.1 | T1.3       | -            | Wave 2   |
| T2.2 | T1.3       | -            | Wave 2   |
| T2.3 | T1.3       | T3.1         | Wave 2   |
| T2.4 | T1.3       | T3.3, T4.1-3 | Wave 2   |
| T3.1 | T2.3       | -            | Wave 3   |
| T3.2 | T2.4       | -            | Wave 3   |
| T3.3 | T2.4       | T4.3         | Wave 3   |
| T3.4 | T0.3, T2.4 | T4.1-2       | Wave 3   |
| T4.1 | T2.4, T3.4 | TF3          | Wave 4   |
| T4.2 | T3.4       | TF3          | Wave 4   |
| T4.3 | T2.4, T3.3 | TF3          | Wave 4   |
| T4.4 | T1.2, T3.4 | TF           | Wave 4   |

### Agent 分配汇总

- **Wave 0**: 4 任务 → 3 quick + 1 unspecified-high
- **Wave 1**: 4 任务 → 2 quick + 1 visual-engineering + 2 unspecified-high
- **Wave 2**: 5 任务 → 4 quick + 1 unspecified-high
- **Wave 3**: 5 任务 → 2 quick + 2 deep
- **Wave 4**: 4 任务 → 2 quick + 1 unspecified-high
- **FINAL**: 3 任务 → 1 oracle + 2 unspecified-high

---

## TODOs

- [x] **T0.1 创建功能分支和基线测试**

  **What to do**: 创建重构专用分支，捕获当前测试基线

  **Steps**:

  1. `git checkout -b refactor/frontend-optimization`
  2. 运行 `bun test > .sisyphus/baseline-tests.txt 2>&1` 保存测试基线
  3. 运行 `bunx playwright test > .sisyphus/baseline-e2e.txt 2>&1` 保存 E2E 基线
  4. 验证所有测试当前通过

  **Must NOT do**: 不要修改任何代码，仅捕获基线

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: git-master

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 0)
  - **Blocks**: T0.2, T0.3, T0.4, Wave 1-4

  **Acceptance Criteria**:

  - [ ] 功能分支创建成功
  - [ ] `.sisyphus/baseline-tests.txt` 存在且包含测试通过信息
  - [ ] `.sisyphus/baseline-e2e.txt` 存在且包含 E2E 通过信息

  **QA Scenarios**:

  ```
  Scenario: Verify branch created
    Tool: Bash
    Preconditions: Git repo clean
    Steps:
      1. `git branch --show-current`
    Expected Result: Output contains "refactor/frontend-optimization"
    Evidence: .sisyphus/evidence/t0-1-branch.txt

  Scenario: Verify baseline captured
    Tool: Bash
    Preconditions: Baseline files created
    Steps:
      1. `cat .sisyphus/baseline-tests.txt | grep -E "(passed|failed)"`
    Expected Result: Shows test pass count, no failures
    Evidence: .sisyphus/evidence/t0-1-baseline.txt
  ```

  **Commit**: YES

  - Message: `chore: create refactor branch and capture test baselines`
  - Files: `.sisyphus/baseline-*.txt`
- [x] **T0.2 创建 ESLint 配置文件**

  **What to do**: 创建符合 Next.js 15 + TypeScript 5 的 ESLint 配置

  **Steps**:

  1. 创建 `eslint.config.mjs` 文件
  2. 配置 Next.js 核心规则
  3. 配置 TypeScript 规则
  4. 配置 React Hooks 规则
  5. 配置 Import/Export 排序规则

  **Config Content** (eslint.config.mjs):

  ```javascript
  import { dirname } from "path";
  import { fileURLToPath } from "url";
  import { FlatCompat } from "@eslint/eslintrc";
  import tseslint from 'typescript-eslint';
  import reactHooks from 'eslint-plugin-react-hooks';
  import importPlugin from 'eslint-plugin-import';

  const __filename = fileURLToPath(import.meta.url);
  const __dirname = dirname(__filename);

  const compat = new FlatCompat({
    baseDirectory: __dirname,
  });

  const eslintConfig = [
    ...compat.extends("next/core-web-vitals", "next/typescript"),
    ...tseslint.configs.recommended,
    {
      files: ['**/*.{js,jsx,ts,tsx}'],
      plugins: {
        'react-hooks': reactHooks,
        'import': importPlugin,
      },
      rules: {
        // React Hooks
        'react-hooks/rules-of-hooks': 'error',
        'react-hooks/exhaustive-deps': 'warn',

        // TypeScript
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/no-unused-vars': ['error', { 
          argsIgnorePattern: '^_',
          varsIgnorePattern: '^_'
        }],

        // Import organization
        'import/order': ['warn', {
          groups: ['builtin', 'external', 'internal', 'parent', 'sibling', 'index'],
          'newlines-between': 'always',
        }],

        // Code quality
        'no-console': ['warn', { allow: ['error', 'warn'] }],
        'prefer-const': 'error',
      },
    },
    {
      ignores: [
        '.next/',
        'node_modules/',
        '*.config.*',
        'test-results/',
        'playwright-report/',
      ],
    },
  ];

  export default eslintConfig;
  ```

  **Must NOT do**: 不要在此任务中运行 lint 或修复错误，仅创建配置

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 0)
  - **Blocked By**: T0.1
  - **Blocks**: T1.4

  **Acceptance Criteria**:

  - [ ] `eslint.config.mjs` 文件存在
  - [ ] 文件包含 Next.js + TypeScript + React Hooks 规则
  - [ ] 包含忽略模式（node_modules, .next 等）

  **QA Scenarios**:

  ```
  Scenario: Verify ESLint config exists
    Tool: Bash
    Preconditions: Config file created
    Steps:
      1. `test -f eslint.config.mjs && echo "EXISTS" || echo "MISSING"`
    Expected Result: Output is "EXISTS"
    Evidence: .sisyphus/evidence/t0-2-config-exists.txt

  Scenario: Verify config syntax
    Tool: Bash
    Preconditions: Config file created
    Steps:
      1. `node --check eslint.config.mjs 2>&1`
    Expected Result: No syntax errors, exit code 0
    Evidence: .sisyphus/evidence/t0-2-config-valid.txt
  ```

  **Commit**: YES

  - Message: `chore: add ESLint configuration with Next.js and TypeScript rules`
  - Files: `eslint.config.mjs`
- [x] **T0.3 创建 Zustand Store 类型定义**

  **What to do**: 创建全局状态管理的类型定义和基础 Store 结构

  **Steps**:

  1. 安装 Zustand: `bun add zustand`
  2. 创建 `stores/` 目录
  3. 创建 `stores/types.ts` - 定义所有 Store 类型
  4. 创建 `stores/index.ts` - barrel export

  **Files to Create**:

  **stores/types.ts**:

  ```typescript
  import type { Skill } from '@/types/skill';
  import type { User } from '@/types/user';

  // Auth Store
  export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    setUser: (user: User | null) => void;
    setAuthenticated: (value: boolean) => void;
    logout: () => void;
  }

  // Skills Store
  export interface SkillsState {
    skills: Skill[];
    loading: boolean;
    error: string | null;
    searchQuery: string;
    setSkills: (skills: Skill[]) => void;
    addSkill: (skill: Skill) => void;
    removeSkill: (id: string) => void;
    updateSkill: (id: string, updates: Partial<Skill>) => void;
    setLoading: (loading: boolean) => void;
    setError: (error: string | null) => void;
    setSearchQuery: (query: string) => void;
    getFilteredSkills: () => Skill[];
  }

  // UI Store (for dialog states, etc.)
  export interface UIState {
    isCreateDialogOpen: boolean;
    isImportDialogOpen: boolean;
    isUserMenuOpen: boolean;
    setCreateDialogOpen: (open: boolean) => void;
    setImportDialogOpen: (open: boolean) => void;
    setUserMenuOpen: (open: boolean) => void;
  }
  ```

  **stores/index.ts**:

  ```typescript
  export type { AuthState, SkillsState, UIState } from './types';
  ```

  **Must NOT do**: 不要在此任务中实现具体的 Store，仅创建类型定义

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 0)
  - **Blocks**: T3.4, T4.1-2

  **Acceptance Criteria**:

  - [ ] `stores/types.ts` 存在且包含所有 State 类型定义
  - [ ] `stores/index.ts` barrel export 存在
  - [ ] Zustand 已添加到 package.json

  **QA Scenarios**:

  ```
  Scenario: Verify types file
    Tool: Bash
    Preconditions: Files created
    Steps:
      1. `cat stores/types.ts | grep -E "(export interface)" | wc -l`
    Expected Result: Output shows at least 3 interfaces
    Evidence: .sisyphus/evidence/t0-3-types.txt

  Scenario: Verify TypeScript compiles
    Tool: Bash
    Preconditions: Types created
    Steps:
      1. `npx tsc --noEmit stores/types.ts`
    Expected Result: Exit code 0
    Evidence: .sisyphus/evidence/t0-3-compile.txt
  ```

  **Commit**: YES

  - Message: `chore: add Zustand store types and install dependency`
  - Files: `stores/types.ts`, `stores/index.ts`, `package.json`, `bun.lock`
- [x] **T0.4 更新 next.config.js 移除忽略设置**

  **What to do**: 移除 next.config.js 中的 ignoreDuringBuilds 和 ignoreBuildErrors

  **Current配置**:

  ```javascript
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  ```

  **修改后**:

  ```javascript
  // 删除整个 eslint 和 typescript 配置块
  // 或者设置为 false（显式启用检查）
  eslint: {
    ignoreDuringBuilds: false,
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  ```

  **Steps**:

  1. 编辑 `next.config.js`
  2. 移除或修改 eslint 配置块
  3. 移除或修改 typescript 配置块
  4. 保存文件

  **Must NOT do**: 不要运行构建验证（会在 Wave 1 完成），仅修改配置

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 0)
  - **Blocks**: T1.3, T1.4

  **Acceptance Criteria**:

  - [ ] `next.config.js` 中的 `ignoreDuringBuilds` 设为 false 或已移除
  - [ ] `next.config.js` 中的 `ignoreBuildErrors` 设为 false 或已移除

  **QA Scenarios**:

  ```
  Scenario: Verify ignores removed
    Tool: Bash
    Preconditions: Config updated
    Steps:
      1. `grep -E "ignoreDuringBuilds|ignoreBuildErrors" next.config.js || echo "CLEAN"`
    Expected Result: Output is "CLEAN" (no matches) or shows "false"
    Evidence: .sisyphus/evidence/t0-4-config.txt
  ```

  **Commit**: YES

  - Message: `chore: enable strict ESLint and TypeScript checks in build`
  - Files: `next.config.js`
- [x] **T1.1 删除 tailwind.config.ts**

  **What to do**: 删除遗留的 Tailwind CSS v3 配置文件

  **Background**: Tailwind v4 使用 CSS-first 配置，不需要 `tailwind.config.ts` 文件

  **Steps**:

  1. 备份 `tailwind.config.ts` 中的自定义主题值（用于 T1.2 迁移）
  2. 删除 `tailwind.config.ts` 文件
  3. 验证删除成功

  **Must NOT do**: 不要修改 postcss.config.mjs 或其他配置文件

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 1 串行，T1.2 依赖此任务)
  - **Blocked By**: T0.1
  - **Blocks**: T1.2

  **Acceptance Criteria**:

  - [ ] `tailwind.config.ts` 文件已删除
  - [ ] 备份的主题值已保存（用于 T1.2）

  **QA Scenarios**:

  ```
  Scenario: Verify config deleted
    Tool: Bash
    Preconditions: File deleted
    Steps:
      1. `test -f tailwind.config.ts && echo "EXISTS" || echo "DELETED"`
    Expected Result: Output is "DELETED"
    Evidence: .sisyphus/evidence/t1-1-deleted.txt

  Scenario: Verify theme values backed up
    Tool: Bash
    Preconditions: Theme backed up
    Steps:
      1. `cat .sisyphus/tailwind-theme-backup.json 2>/dev/null | head -20`
    Expected Result: Shows JSON with colors, fonts, spacing
    Evidence: .sisyphus/evidence/t1-1-backup.txt
  ```

  **Commit**: YES

  - Message: `chore: remove legacy tailwind.config.ts for v4 migration`
  - Files: Deleted `tailwind.config.ts`
- [x] **T1.2 迁移 Tailwind 主题到 globals.css**

  **What to do**: 将 tailwind.config.ts 中的主题配置迁移到 CSS @theme 指令

  **迁移内容**（从已删除的 tailwind.config.ts）:

  - Colors: primary (50-900), gray (50-900), success, warning, error, info
  - Font families: sans, mono
  - Spacing: '18': '4.5rem'
  - Border radius: sm, md, lg, xl, 2xl
  - Box shadows: glow
  - Animations: slide-in, fade-in

  **Steps**:

  1. 在 `globals.css` 中添加 `@theme` 块
  2. 迁移颜色定义
  3. 迁移字体定义
  4. 迁移间距、圆角、阴影
  5. 保留现有 CSS 动画（已在 globals.css 中）
  6. 删除旧的 Tailwind v3 配置残留

  **示例 CSS 添加**:

  ```css
  @theme {
    /* Colors */
    --color-primary-50: #f5f3ff;
    --color-primary-100: #ede9fe;
    /* ... continue for all colors ... */

    --color-gray-50: #fafafa;
    --color-gray-100: #f4f4f5;
    /* ... */

    --color-success: #22c55e;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
    --color-info: #3b82f6;

    /* Fonts */
    --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    --font-mono: 'JetBrains Mono', 'Fira Code', 'SF Mono', monospace;

    /* Spacing */
    --spacing-18: 4.5rem;

    /* Border radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
    --radius-xl: 1rem;
    --radius-2xl: 1.5rem;

    /* Shadows */
    --shadow-glow: 0 0 20px rgba(139, 92, 246, 0.3);
  }
  ```

  **Must NOT do**: 不要修改组件中的 Tailwind 类名（样式应该保持兼容）

  **Recommended Agent Profile**:

  - **Category**: visual-engineering
  - **Skills**: 不需要特殊技能
  - **Reason**: 涉及 CSS 和视觉配置，需要确保样式正确迁移

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 1 串行)
  - **Blocked By**: T1.1
  - **Blocks**: T4.4

  **Acceptance Criteria**:

  - [ ] `globals.css` 包含完整的 `@theme` 块
  - [ ] 所有颜色、字体、间距、阴影已迁移
  - [ ] 开发服务器启动时无 Tailwind 警告

  **QA Scenarios**:

  ```
  Scenario: Verify theme migration
    Tool: Bash
    Preconditions: CSS updated
    Steps:
      1. `grep -A 5 "@theme" app/globals.css | head -10`
    Expected Result: Shows @theme block with color definitions
    Evidence: .sisyphus/evidence/t1-2-theme.txt

  Scenario: Visual smoke test
    Tool: skill_mcp (Playwright)
    Preconditions: Dev server running
    Steps:
      1. Navigate to http://localhost:3000
      2. Screenshot the page
      3. Verify primary colors render correctly
    Expected Result: Page renders with purple primary colors (not default blue)
    Evidence: .sisyphus/evidence/t1-2-visual.png
  ```

  **Commit**: YES

  - Message: `chore: migrate Tailwind theme to CSS-first configuration`
  - Files: `app/globals.css`
- [x] **T1.3 修复所有 TypeScript 错误**

  **What to do**: 修复 `npx tsc --noEmit` 暴露的所有类型错误

  **已知问题**（从 LSP 诊断）:

  1. `lib/api.ts:110:49` - 'url' is declared but its value is never read
  2. `app/[locale]/skills/page.tsx:98:9` - 'parseApiError' is declared but its value is never read
  3. `app/[locale]/skills/[id]/page.tsx:79:9` - 'handleRollback' is declared but its value is never read
  4. `app/[locale]/skills/[id]/page.tsx:131:9` - Type error in SkillHeader props
  5. `lib/__tests__/auth.test.ts:1:67` - Cannot find module 'bun:test'
  6. `lib/file-utils.test.ts:1:38` - Cannot find module 'bun:test'

  **修复策略**:

  1. 运行 `npx tsc --noEmit > .sisyphus/typescript-errors.txt 2>&1` 获取完整错误列表
  2. 逐个修复错误
  3. 对于未使用的变量：删除或添加 `_` 前缀
  4. 对于类型错误：修复类型定义或使用正确的类型断言
  5. 对于测试模块错误：统一使用 `@testing-library` 或 `bun:test`

  **修复示例**:

  **lib/api.ts**:

  ```typescript
  // Before: url parameter unused
  private async handleError(response: Response, url: string): Promise<Error> {

  // After: remove unused parameter or use it
  private async handleError(response: Response, _url: string): Promise<Error> {
  // or use url in error message
  ```

  **app/[locale]/skills/page.tsx**:

  ```typescript
  // Remove unused parseApiError function (duplicates lib/errors.ts)
  // Or use it and remove import from lib/errors.ts
  ```

  **Must NOT do**: 不要使用 `@ts-ignore` 绕过错误，必须真正修复

  **Recommended Agent Profile**:

  - **Category**: unspecified-high
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 1 串行，依赖顺序)
  - **Blocked By**: T0.1, T0.4
  - **Blocks**: Wave 2, Wave 3, Wave 4

  **Acceptance Criteria**:

  - [ ] `npx tsc --noEmit` 退出码为 0
  - [ ] 没有 TypeScript 错误
  - [ ] `.sisyphus/typescript-errors-fixed.txt` 记录修复的错误数

  **QA Scenarios**:

  ```
  Scenario: Verify no TypeScript errors
    Tool: Bash
    Preconditions: All errors fixed
    Steps:
      1. `npx tsc --noEmit 2>&1`
    Expected Result: Exit code 0, no error output
    Evidence: .sisyphus/evidence/t1-3-no-errors.txt

  Scenario: Verify specific fixes
    Tool: Bash
    Preconditions: Errors fixed
    Steps:
      1. `grep -n "parseApiError" app/\[locale\]/skills/page.tsx | head -3`
    Expected Result: Either shows usage or shows function removed
    Evidence: .sisyphus/evidence/t1-3-fixes.txt
  ```

  **Commit**: YES

  - Message: `fix: resolve all TypeScript type errors`
  - Files: All files with type fixes
  - Pre-commit: `npx tsc --noEmit`
- [x] **T1.4 修复所有 ESLint 错误**

  **What to do**: 运行 `bun run lint` 并修复所有报告的错误

  **步骤**:

  1. 运行 `bun run lint > .sisyphus/eslint-errors.txt 2>&1` 获取错误列表
  2. 自动修复可自动修复的问题：`bun run lint --fix`
  3. 手动修复剩余问题
  4. 验证 `bun run lint` 退出码为 0

  **预期错误类型**:

  - Unused variables/parameters
  - Console.log 使用（根据我们的规则）
  - Import 排序问题
  - any 类型使用

  **修复策略**:

  - 未使用的变量：删除或重命名为 `_`
  - console.log：改为 console.warn/error 或删除
  - Import 排序：运行自动修复
  - any 类型：添加具体类型

  **Must NOT do**: 不要禁用规则来绕过错误，必须真正修复

  **Recommended Agent Profile**:

  - **Category**: unspecified-high
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 1 串行)
  - **Blocked By**: T0.1, T0.2, T1.3
  - **Blocks**: Wave 2, Wave 3, Wave 4

  **Acceptance Criteria**:

  - [ ] `bun run lint` 退出码为 0
  - [ ] 没有 ESLint 错误
  - [ ] `.sisyphus/eslint-errors-fixed.txt` 记录修复的错误数

  **QA Scenarios**:

  ```
  Scenario: Verify no ESLint errors
    Tool: Bash
    Preconditions: All errors fixed
    Steps:
      1. `bun run lint 2>&1`
    Expected Result: Exit code 0, output shows "No ESLint errors"
    Evidence: .sisyphus/evidence/t1-4-no-errors.txt

  Scenario: Verify auto-fix applied
    Tool: Bash
    Preconditions: Lint run
    Steps:
      1. `git diff --stat | tail -1`
    Expected Result: Shows number of files modified by lint --fix
    Evidence: .sisyphus/evidence/t1-4-changes.txt
  ```

  **Commit**: YES

  - Message: `style: fix all ESLint errors and apply auto-fixes`
  - Files: All files with lint fixes
  - Pre-commit: `bun run lint`
- [x] **T2.1 移动 i18n 文件（messages/ → i18n/locales/）**

  **What to do**: 合并分散的国际化配置，将 messages/ 移动到 i18n/locales/

  **Current Structure**:

  ```
  i18n/
  ├── request.ts
  └── routing.ts
  messages/
  ├── en.json
  └── zh.json
  ```

  **目标结构**:

  ```
  i18n/
  ├── config/
  │   ├── request.ts    (从 i18n/request.ts 移动)
  │   └── routing.ts    (从 i18n/routing.ts 移动)
  └── locales/
      ├── en.json       (从 messages/en.json 移动)
      └── zh.json       (从 messages/zh.json 移动)
  ```

  **Steps**:

  1. 创建 `i18n/config/` 和 `i18n/locales/` 目录
  2. 移动 `i18n/request.ts` → `i18n/config/request.ts`
  3. 移动 `i18n/routing.ts` → `i18n/config/routing.ts`
  4. 移动 `messages/en.json` → `i18n/locales/en.json`
  5. 移动 `messages/zh.json` → `i18n/locales/zh.json`
  6. 更新导入路径
  7. 删除空 `messages/` 目录

  **路径更新**:

  - `i18n/config/request.ts`: 更新 `../messages/${locale}.json` → `../locales/${locale}.json`
  - 其他文件中使用 `@/messages/*` 的路径需要更新为 `@/i18n/locales/*`

  **Must NOT do**: 不要修改 JSON 文件内容，仅移动位置

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: T1.3

  **Acceptance Criteria**:

  - [ ] `i18n/config/` 包含 request.ts 和 routing.ts
  - [ ] `i18n/locales/` 包含 en.json 和 zh.json
  - [ ] `messages/` 目录已删除
  - [ ] 所有导入路径已更新
  - [ ] 应用能正常加载翻译

  **QA Scenarios**:

  ```
  Scenario: Verify directory structure
    Tool: Bash
    Preconditions: Files moved
    Steps:
      1. `ls -la i18n/config/ i18n/locales/`
      2. `test -d messages && echo "EXISTS" || echo "DELETED"`
    Expected Result: Shows files in config/ and locales/, messages is DELETED
    Evidence: .sisyphus/evidence/t2-1-structure.txt

  Scenario: Verify i18n works
    Tool: skill_mcp (Playwright)
    Preconditions: Dev server running
    Steps:
      1. Navigate to http://localhost:3000/en
      2. Verify English text appears
      3. Navigate to http://localhost:3000/zh
      4. Verify Chinese text appears
    Expected Result: Both locales load correctly
    Evidence: .sisyphus/evidence/t2-1-i18n.png
  ```

  **Commit**: YES

  - Message: `refactor: consolidate i18n files into single directory structure`
  - Files: `i18n/config/*`, `i18n/locales/*`, deleted `messages/`, updated imports
- [x] **T2.2 移动组件（file-icons.tsx → components/ui/）**

  **What to do**: 将 React 组件从 lib/ 移动到正确的 components/ 位置

  **文件移动**:

  ```
  lib/file-icons.tsx → components/ui/FileIcons.tsx
  ```

  **更新导入**:
  搜索所有使用 `lib/file-icons` 的地方，更新为 `components/ui/FileIcons`：

  ```bash
  grep -r "from.*lib/file-icons" --include="*.tsx" --include="*.ts"
  ```

  **Must NOT do**: 不要修改组件代码，仅移动文件和更新导入

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: T1.3

  **Acceptance Criteria**:

  - [ ] `components/ui/FileIcons.tsx` 存在
  - [ ] `lib/file-icons.tsx` 已删除
  - [ ] 所有导入路径已更新

  **QA Scenarios**:

  ```
  Scenario: Verify component moved
    Tool: Bash
    Preconditions: File moved
    Steps:
      1. `test -f components/ui/FileIcons.tsx && echo "EXISTS" || echo "MISSING"`
      2. `test -f lib/file-icons.tsx && echo "EXISTS" || echo "DELETED"`
    Expected Result: FileIcons.tsx EXISTS, file-icons.tsx DELETED
    Evidence: .sisyphus/evidence/t2-2-moved.txt
  ```

  **Commit**: YES

  - Message: `refactor: move FileIcons component from lib to components/ui`
  - Files: New location, deleted old location, updated imports
- [x] **T2.3 移动 auth.ts（app/lib/ → lib/）**

  **What to do**: 将 4 行的 auth.ts 从 app/lib/ 移动到 lib/

  **Current文件** (`app/lib/auth.ts`):

  ```typescript
  export function logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/login';
  }
  ```

  **移动目标**: `lib/auth.ts`

  **更新导入**:

  - `lib/__tests__/auth.test.ts` - 更新导入路径
  - 其他使用 `app/lib/auth` 的文件

  **Must NOT do**: 不要修改 auth.ts 代码

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: T1.3
  - **Blocks**: T3.1

  **Acceptance Criteria**:

  - [ ] `lib/auth.ts` 存在
  - [ ] `app/lib/` 目录已删除
  - [ ] 测试文件导入路径已更新

  **QA Scenarios**:

  ```
  Scenario: Verify file moved
    Tool: Bash
    Preconditions: File moved
    Steps:
      1. `test -f lib/auth.ts && echo "EXISTS" || echo "MISSING"`
      2. `test -d app/lib && echo "EXISTS" || echo "DELETED"`
    Expected Result: lib/auth.ts EXISTS, app/lib DELETED
    Evidence: .sisyphus/evidence/t2-3-moved.txt

  Scenario: Verify tests pass
    Tool: Bash
    Preconditions: Import paths updated
    Steps:
      1. `bun test lib/__tests__/auth.test.ts`
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/t2-3-tests.txt
  ```

  **Commit**: YES

  - Message: `refactor: move auth utilities to lib/ and remove app/lib/`
  - Files: `lib/auth.ts`, deleted `app/lib/`, updated test imports
- [x] **T2.4 重组 components/ 目录结构**

  **What to do**: 将 components/ 从混合型改为 Feature-based 结构

  **Current Structure**:

  ```
  components/
  ├── ui/              # 12 个基础 UI 组件
  ├── skills/          # 10 个 Skill 相关组件
  ├── DownloadDialog.tsx
  ├── FilePreview.tsx
  ├── FileTree.tsx
  ├── FileTreeItem.tsx
  ├── ImagePreview.tsx
  ├── LanguageSwitcher.tsx
  ├── MarkdownEditor.tsx
  ├── MarkdownViewer.tsx
  ├── NextIntlProvider.tsx
  ├── PdfPreview.tsx
  ├── TextEditor.tsx
  └── TextViewer.tsx
  ```

  **目标结构**:

  ```
  components/
  ├── ui/                    # 基础 UI 组件（保持）
  ├── skills/                # Skill 功能组件（保持）
  ├── file-tree/            # NEW: 文件树功能
  │   ├── FileTree.tsx
  │   ├── FileTreeItem.tsx
  │   ├── FileTreeToolbar.tsx (从 ui/ 移动)
  │   ├── FileIcons.tsx
  │   ├── FilePreview.tsx
  │   ├── ImagePreview.tsx
  │   └── PdfPreview.tsx
  ├── editors/              # NEW: 编辑器组件
  │   ├── MarkdownEditor.tsx
  │   ├── MarkdownViewer.tsx
  │   ├── TextEditor.tsx
  │   └── TextViewer.tsx
  └── providers/            # NEW: Context Providers
      └── NextIntlProvider.tsx
  ```

  **Steps**:

  1. 创建 `components/file-tree/`, `components/editors/`, `components/providers/`
  2. 移动 FileTree 相关组件到 file-tree/
  3. 移动 Editor 相关组件到 editors/
  4. 移动 FileTreeToolbar 从 ui/ 到 file-tree/
  5. 移动 NextIntlProvider 到 providers/
  6. 更新所有导入路径
  7. （可选）添加 barrel exports

  **Must NOT do**: 不要修改组件代码，仅移动和组织

  **Recommended Agent Profile**:

  - **Category**: unspecified-high
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 2 串行，文件移动量大)
  - **Blocked By**: T1.3
  - **Blocks**: T3.3, T4.1-3

  **Acceptance Criteria**:

  - [ ] `components/file-tree/` 包含 7+ 个文件
  - [ ] `components/editors/` 包含 4 个文件
  - [ ] `components/providers/` 包含 1 个文件
  - [ ] `components/` 根目录没有松散组件（仅剩 ui/, skills/, file-tree/, editors/, providers/）
  - [ ] 所有导入路径已更新
  - [ ] 应用编译成功

  **QA Scenarios**:

  ```
  Scenario: Verify directory structure
    Tool: Bash
    Preconditions: Components reorganized
    Steps:
      1. `ls components/`
      2. `ls components/file-tree/ | wc -l`
      3. `ls components/editors/ | wc -l`
    Expected Result: Root only has folders, file-tree has 7+ files, editors has 4
    Evidence: .sisyphus/evidence/t2-4-structure.txt

  Scenario: Verify build passes
    Tool: Bash
    Preconditions: Imports updated
    Steps:
      1. `bun run build 2>&1 | tail -20`
    Expected Result: Build succeeds with no errors
    Evidence: .sisyphus/evidence/t2-4-build.txt
  ```

  **Commit**: YES

  - Message: `refactor: reorganize components into feature-based directory structure`
  - Files: All moved components, updated imports throughout codebase
- [x] **T2.5 合并测试文件（删除重复）**

  **What to do**: 删除重复的测试文件 `lib/file-utils.test.ts`

  **重复文件**:

  - `lib/file-utils.test.ts` (重复)
  - `lib/__tests__/file-utils.test.ts` (保留)

  **验证**:

  ```bash
  diff lib/file-utils.test.ts lib/__tests__/file-utils.test.ts
  ```

  **Steps**:

  1. 比较两个文件确认内容相同
  2. 删除 `lib/file-utils.test.ts`
  3. 验证 `lib/__tests__/file-utils.test.ts` 仍然存在

  **Must NOT do**: 不要删除 `lib/__tests__/file-utils.test.ts`

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 2)
  - **Blocked By**: T1.3

  **Acceptance Criteria**:

  - [ ] `lib/file-utils.test.ts` 已删除
  - [ ] `lib/__tests__/file-utils.test.ts` 仍然存在
  - [ ] `bun test lib/__tests__/file-utils.test.ts` 通过

  **QA Scenarios**:

  ```
  Scenario: Verify duplicate removed
    Tool: Bash
    Preconditions: File deleted
    Steps:
      1. `test -f lib/file-utils.test.ts && echo "EXISTS" || echo "DELETED"`
      2. `test -f lib/__tests__/file-utils.test.ts && echo "EXISTS" || echo "MISSING"`
    Expected Result: Root test DELETED, __tests__ version EXISTS
    Evidence: .sisyphus/evidence/t2-5-removed.txt
  ```

  **Commit**: YES

  - Message: `chore: remove duplicate test file lib/file-utils.test.ts`
  - Files: Deleted `lib/file-utils.test.ts`
- [x] **T3.1 统一错误处理（提取 parseApiError）**

  **What to do**: 将分散的 parseApiError 函数提取到 lib/errors.ts

  **当前状态**: `parseApiError` 在 3 个地方重复

  - `app/[locale]/skills/page.tsx:98-126`
  - `components/skills/CreateSkillDialog.tsx`
  - `components/skills/ImportSkillDialog.tsx`

  **目标**: 统一使用 `lib/errors.ts` 中的版本

  **步骤**:

  1. 增强 `lib/errors.ts` 中的 parseError 函数，支持 API 错误格式
  2. 在 Skills 页面使用 `lib/errors.ts` 的版本
  3. 更新 CreateSkillDialog 和 ImportSkillDialog
  4. 删除重复的 parseApiError 函数

  **lib/errors.ts 增强**:

  ```typescript
  export function parseApiError(err: unknown): string {
    // Type guard for error with response property (Axios-like errors)
    if (err && typeof err === 'object' && 'response' in err) {
      const response = (err as { response?: { data?: { detail?: unknown } } }).response;
      const detail = response?.data?.detail;

      if (Array.isArray(detail) && detail.length > 0) {
        const firstError = detail[0];
        if (firstError && typeof firstError === 'object' && 'msg' in firstError && 'loc' in firstError) {
          const loc = (firstError as { loc: unknown[] }).loc;
          const msg = (firstError as { msg: string }).msg;
          const field = loc[loc.length - 1];
          return `${field}: ${msg}`;
        }
        return JSON.stringify(detail);
      }

      if (typeof detail === 'string') {
        return detail;
      }
    }

    return parseError(err);
  }
  ```

  **Must NOT do**: 不要改变错误处理逻辑，仅统一位置

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocked By**: T2.3

  **Acceptance Criteria**:

  - [ ] `lib/errors.ts` 包含 parseApiError 函数
  - [ ] Skills 页面使用 lib/errors.ts
  - [ ] Dialogs 使用 lib/errors.ts
  - [ ] 没有重复的 parseApiError 定义

  **QA Scenarios**:

  ```
  Scenario: Verify unified error handling
    Tool: Bash
    Preconditions: Code refactored
    Steps:
      1. `grep -r "parseApiError" app/ components/ --include="*.tsx" | wc -l`
      2. `grep "parseApiError" lib/errors.ts`
    Expected Result: parseApiError only in lib/errors.ts and imports
    Evidence: .sisyphus/evidence/t3-1-unified.txt
  ```

  **Commit**: YES

  - Message: `refactor: unify error handling by extracting parseApiError to lib/errors`
  - Files: `lib/errors.ts`, updated components
- [x] **T3.2 修复 Monaco Editor 类型（移除 any）**

  **What to do**: 为 Monaco Editor refs 添加正确的类型定义

  **当前问题**:

  ```typescript
  // components/TextEditor.tsx:54-55
  const monacoRef = useRef<any>(null);
  const editorRef = useRef<any>(null);

  // components/MarkdownEditor.tsx:44,46
  const monacoRef = useRef<any>(null);
  const editorRef = useRef<any>(null);
  ```

  **目标类型**:

  ```typescript
  import type { editor } from 'monaco-editor';

  const monacoRef = useRef<typeof import('monaco-editor') | null>(null);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  ```

  **步骤**:

  1. 安装 Monaco Editor 类型：`bun add -D @types/monaco-editor`（如需要）
  2. 更新 `components/TextEditor.tsx`
  3. 更新 `components/MarkdownEditor.tsx`
  4. 验证 TypeScript 编译通过

  **Must NOT do**: 不要使用 `any`，不要使用 `@ts-ignore`

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 3)
  - **Blocked By**: T2.4

  **Acceptance Criteria**:

  - [ ] TextEditor.tsx 中没有 `any` 类型
  - [ ] MarkdownEditor.tsx 中没有 `any` 类型
  - [ ] `npx tsc --noEmit` 通过

  **QA Scenarios**:

  ```
  Scenario: Verify no any types
    Tool: Bash
    Preconditions: Types updated
    Steps:
      1. `grep "useRef<any>" components/TextEditor.tsx components/MarkdownEditor.tsx`
    Expected Result: No matches (exit code 1)
    Evidence: .sisyphus/evidence/t3-2-no-any.txt

  Scenario: Verify TypeScript compiles
    Tool: Bash
    Preconditions: Types updated
    Steps:
      1. `npx tsc --noEmit components/TextEditor.tsx components/MarkdownEditor.tsx`
    Expected Result: Exit code 0
    Evidence: .sisyphus/evidence/t3-2-compile.txt
  ```

  **Commit**: YES

  - Message: `types: replace Monaco Editor any types with proper TypeScript definitions`
  - Files: `components/TextEditor.tsx`, `components/MarkdownEditor.tsx`
- [x] **T3.3 拆分 useFileTree hook**

  **What to do**: 将 425 行的 useFileTree 拆分为多个小 hook

  **当前**: `hooks/useFileTree.ts` (425 行，太多职责)

  **目标结构**:

  ```
  hooks/
  ├── file-tree/
  │   ├── index.ts              # Barrel export
  │   ├── useFileTree.ts        # 主 hook（精简版）
  │   ├── useTreeState.ts       # Tree state management
  │   ├── useTreeOperations.ts  # CRUD operations
  │   ├── useTreePersistence.ts # localStorage persistence
  │   └── useTreeSelection.ts   # Selection logic
  ```

  **拆分策略**:

  1. `useTreeState`: 管理 nodes, selectedPath, loading, error
  2. `useTreeOperations`: addNode, removeNode, updateNode, toggleNode
  3. `useTreePersistence`: save/load expanded state, selected path
  4. `useTreeSelection`: selectNode, auto-select logic
  5. `useFileTree`: 组合以上 hooks

  **Must NOT do**: 不要改变任何逻辑行为，仅代码组织

  **Recommended Agent Profile**:

  - **Category**: deep
  - **Skills**: 不需要特殊技能
  - **Reason**: 需要仔细拆分逻辑，确保不破坏功能

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 3 串行，逻辑复杂)
  - **Blocked By**: T2.4
  - **Blocks**: T4.3

  **Acceptance Criteria**:

  - [ ] 创建了 `hooks/file-tree/` 目录
  - [ ] 拆分出至少 4 个独立 hook
  - [ ] 原 useFileTree 功能保持不变
  - [ ] 所有使用 useFileTree 的地方无需修改

  **QA Scenarios**:

  ```
  Scenario: Verify hooks created
    Tool: Bash
    Preconditions: Hooks split
    Steps:
      1. `ls hooks/file-tree/`
      2. `wc -l hooks/file-tree/*.ts`
    Expected Result: Shows multiple files, each < 150 lines
    Evidence: .sisyphus/evidence/t3-3-hooks.txt

  Scenario: Verify functionality preserved
    Tool: Bash
    Preconditions: Hooks split
    Steps:
      1. `bun test hooks/__tests__/file-tree.test.ts 2>/dev/null || bun test lib/__tests__/file-tree.test.ts`
    Expected Result: Tests pass
    Evidence: .sisyphus/evidence/t3-3-tests.txt
  ```

  **Commit**: YES

  - Message: `refactor: split useFileTree hook into smaller focused hooks`
  - Files: `hooks/file-tree/*`, updated imports
- [x] **T3.4 拆分 Skills 页面状态（创建 useSkillsStore）**

  **What to do**: 将 Skills 页面的 15+ useState 提取到 Zustand Store

  **当前**: `app/[locale]/skills/page.tsx` (287 行，15+ useState)

  **目标**:

  1. 创建 `stores/skillsStore.ts` - Zustand store
  2. 创建 `hooks/useSkills.ts` - React hook wrapper
  3. 创建 `hooks/useSkillDialogs.ts` - Dialog state management
  4. 简化 Skills 页面

  **stores/skillsStore.ts**:

  ```typescript
  import { create } from 'zustand';
  import type { SkillsState } from './types';
  import type { Skill } from '@/types/skill';

  export const useSkillsStore = create<SkillsState>((set, get) => ({
    skills: [],
    loading: true,
    error: null,
    searchQuery: '',
    setSkills: (skills) => set({ skills, loading: false }),
    addSkill: (skill) => set((state) => ({ 
      skills: [skill, ...state.skills] 
    })),
    removeSkill: (id) => set((state) => ({
      skills: state.skills.filter((s) => s.id !== id)
    })),
    setLoading: (loading) => set({ loading }),
    setError: (error) => set({ error, loading: false }),
    setSearchQuery: (query) => set({ searchQuery: query }),
    getFilteredSkills: () => {
      const { skills, searchQuery } = get();
      if (!searchQuery) return skills;
      const query = searchQuery.toLowerCase();
      return skills.filter(
        (s) =>
          s.name.toLowerCase().includes(query) ||
          s.description?.toLowerCase().includes(query)
      );
    },
  }));
  ```

  **Must NOT do**: 不要在此任务中完全重写 Skills 页面，仅创建 Store

  **Recommended Agent Profile**:

  - **Category**: deep
  - **Skills**: 不需要特殊技能
  - **Reason**: 状态重构需要仔细设计

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 3 串行)
  - **Blocked By**: T0.3, T2.4
  - **Blocks**: T4.1-2

  **Acceptance Criteria**:

  - [ ] `stores/skillsStore.ts` 存在且编译通过
  - [ ] Store 包含所有必要的状态和方法
  - [ ] `stores/index.ts` 导出 skillsStore

  **QA Scenarios**:

  ```
  Scenario: Verify store created
    Tool: Bash
    Preconditions: Store created
    Steps:
      1. `test -f stores/skillsStore.ts && echo "EXISTS" || echo "MISSING"`
      2. `grep -c "create<SkillsState>" stores/skillsStore.ts`
    Expected Result: File EXISTS, shows create call
    Evidence: .sisyphus/evidence/t3-4-store.txt

  Scenario: Verify store compiles
    Tool: Bash
    Preconditions: Store created
    Steps:
      1. `npx tsc --noEmit stores/skillsStore.ts`
    Expected Result: Exit code 0
    Evidence: .sisyphus/evidence/t3-4-compile.txt
  ```

  **Commit**: YES

  - Message: `feat: add Zustand store for skills state management`
  - Files: `stores/skillsStore.ts`, updated `stores/index.ts`
- [x] **T3.5 添加 barrel exports（index.ts）**

  **What to do**: 为 types/ 和 stores/ 添加 index.ts barrel exports

  **目标**:

  ```typescript
  // types/index.ts
  export type { Skill, SkillListResponse, CreateSkillRequest } from './skill';
  export type { FileTreeNode, TreeStructure } from './file-tree';
  export type { User } from './user';
  export type { Project } from './project';

  // stores/index.ts (已有基础，需更新)
  export { useSkillsStore } from './skillsStore';
  export type { AuthState, SkillsState, UIState } from './types';
  ```

  **步骤**:

  1. 创建 `types/index.ts`
  2. 更新 `stores/index.ts`（添加 useSkillsStore 导出）
  3. 可选：为 hooks/ 和 lib/ 添加 barrel exports

  **Must NOT do**: 不要强制所有地方都使用 barrel exports（逐步采用）

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 3)

  **Acceptance Criteria**:

  - [ ] `types/index.ts` 存在
  - [ ] `stores/index.ts` 导出 skillsStore
  - [ ] Barrel exports 可以正确导入类型

  **QA Scenarios**:

  ```
  Scenario: Verify barrel exports work
    Tool: Bash
    Preconditions: Index files created
    Steps:
      1. `echo "import type { Skill } from '@/types';" > /tmp/test-import.ts`
      2. `npx tsc --noEmit /tmp/test-import.ts 2>&1`
    Expected Result: No errors
    Evidence: .sisyphus/evidence/t3-5-barrel.txt
  ```

  **Commit**: YES

  - Message: `chore: add barrel exports for types and stores`
  - Files: `types/index.ts`, `stores/index.ts`
- [x] **T4.1 添加 React.memo 到 SkillCard**

  **What to do**: 为 SkillCard 组件添加 React.memo 优化

  **当前**: `components/skills/SkillCard.tsx` (无 memoization)

  **修改**:

  ```typescript
  import { memo } from 'react';

  // ... component definition ...

  export default memo(SkillCard);
  // 或 export const SkillCard = memo(SkillCardComponent);
  ```

  **考虑**:

  - 仅当组件 props 频繁变化但不实际需要重新渲染时才有收益
  - SkillCard 接收的 props: skill, openMenuId, onMenuToggle, onDownload, onDelete, onNavigate
  - 大部分 props 是回调函数，需要 useCallback 配合

  **Must NOT do**: 不要盲目添加 memo，需要配合 useCallback 使用

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 4)
  - **Blocked By**: T2.4, T3.4
  - **Blocks**: TF3

  **Acceptance Criteria**:

  - [ ] SkillCard 使用 React.memo 包裹
  - [ ] 父组件中的回调使用 useCallback

  **QA Scenarios**:

  ```
  Scenario: Verify memo added
    Tool: Bash
    Preconditions: Component updated
    Steps:
      1. `grep "memo" components/skills/SkillCard.tsx`
    Expected Result: Shows memo import and usage
    Evidence: .sisyphus/evidence/t4-1-memo.txt
  ```

  **Commit**: YES

  - Message: `perf: add React.memo to SkillCard for render optimization`
  - Files: `components/skills/SkillCard.tsx`, `app/[locale]/skills/page.tsx`
- [x] **T4.2 添加 useMemo 到过滤逻辑**

  **What to do**: 为 skills 过滤逻辑添加 useMemo

  **当前**:

  ```typescript
  const filteredSkills = skills.filter(
    (skill) =>
      skill.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      skill.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );
  ```

  **优化后**:

  ```typescript
  const filteredSkills = useMemo(() => {
    if (!searchQuery) return skills;
    const query = searchQuery.toLowerCase();
    return skills.filter(
      (skill) =>
        skill.name.toLowerCase().includes(query) ||
        skill.description?.toLowerCase().includes(query)
    );
  }, [skills, searchQuery]);
  ```

  **Must NOT do**: 仅在 skills 列表较大时才有明显收益

  **Recommended Agent Profile**:

  - **Category**: quick
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 4)
  - **Blocked By**: T3.4
  - **Blocks**: TF3

  **Acceptance Criteria**:

  - [ ] 过滤逻辑使用 useMemo
  - [ ] 依赖数组正确（skills, searchQuery）

  **QA Scenarios**:

  ```
  Scenario: Verify useMemo added
    Tool: Bash
    Preconditions: Logic updated
    Steps:
      1. `grep -A 5 "const filteredSkills" app/\[locale\]/skills/page.tsx`
    Expected Result: Shows useMemo wrapper
    Evidence: .sisyphus/evidence/t4-2-memo.txt
  ```

  **Commit**: YES

  - Message: `perf: memoize skills filtering with useMemo`
  - Files: `app/[locale]/skills/page.tsx`
- [x] **T4.3 优化 FileTree 渲染**

  **What to do**: 优化文件树组件的渲染性能

  **优化点**:

  1. 为 FileTreeItem 添加 React.memo
  2. 使用 useCallback 包装事件处理器
  3. 虚拟化（如果列表很长）- 可选

  **文件**:

  - `components/file-tree/FileTree.tsx`
  - `components/file-tree/FileTreeItem.tsx`

  **Must NOT do**: 不要过度优化，仅在识别到性能问题时才添加

  **Recommended Agent Profile**:

  - **Category**: unspecified-high
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: YES (Wave 4)
  - **Blocked By**: T2.4, T3.3
  - **Blocks**: TF3

  **Acceptance Criteria**:

  - [ ] FileTreeItem 使用 React.memo
  - [ ] 回调函数使用 useCallback

  **QA Scenarios**:

  ```
  Scenario: Verify optimizations
    Tool: Bash
    Preconditions: Components updated
    Steps:
      1. `grep "memo" components/file-tree/FileTreeItem.tsx`
      2. `grep "useCallback" components/file-tree/FileTree.tsx`
    Expected Result: Shows memo and useCallback usage
    Evidence: .sisyphus/evidence/t4-3-optimize.txt
  ```

  **Commit**: YES

  - Message: `perf: optimize FileTree rendering with memo and useCallback`
  - Files: `components/file-tree/FileTree.tsx`, `components/file-tree/FileTreeItem.tsx`
- [x] **T4.4 最终构建验证**

  **What to do**: 验证完整的构建流程

  **验证清单**:

  - [ ] `bun run build` 成功（无错误）
  - [ ] `bun run lint` 成功（无错误）
  - [ ] `npx tsc --noEmit` 成功（无类型错误）
  - [ ] `bun test` 成功（所有测试通过）
  - [ ] 开发服务器正常启动
  - [ ] 主要页面可以正常访问

  **步骤**:

  1. 运行完整构建
  2. 运行所有检查命令
  3. 启动开发服务器并手动验证
  4. 记录验证结果到 `.sisyphus/final-verification.txt`

  **Must NOT do**: 如果发现问题，不要强行通过，需要回滚或修复

  **Recommended Agent Profile**:

  - **Category**: unspecified-high
  - **Skills**: 不需要特殊技能

  **Parallelization**:

  - **Can Run In Parallel**: NO (Wave 4 最后任务)
  - **Blocked By**: T1.2, T3.4

  **Acceptance Criteria**:

  - [ ] 所有构建命令成功
  - [ ] 验证报告已保存

  **QA Scenarios**:

  ```
  Scenario: Verify build success
    Tool: Bash
    Preconditions: All changes applied
    Steps:
      1. `bun run build 2>&1 | tail -5`
    Expected Result: Shows "Build completed successfully"
    Evidence: .sisyphus/evidence/t4-4-build.txt

  Scenario: Verify all checks pass
    Tool: Bash
    Preconditions: Build successful
    Steps:
      1. `bun run lint && echo "LINT_OK"`
      2. `npx tsc --noEmit && echo "TS_OK"`
      3. `bun test && echo "TEST_OK"`
    Expected Result: All commands show _OK
    Evidence: .sisyphus/evidence/t4-4-checks.txt
  ```

  **Commit**: YES (如果发现问题则修复)

  - Message: `chore: final verification and build fixes`
  - Files: Any fixes needed

---

## Final Verification Wave

> **必须在所有 Wave 完成后执行**，4 个验证代理并行运行，全部通过才算完成

- [x] **TF1. 计划合规审计** - `oracle`

  **What to do**: 审核重构是否完全符合计划要求

  **验证清单**:

  - [ ] 所有 Must Have 项已完成（配置修复、目录结构、代码质量）
  - [ ] 所有 Must NOT Have 项未触碰（无新功能、无行为改变）
  - [ ] 所有文件移动到正确位置
  - [ ] 没有遗留的技术债务（console.log, any 类型等）

  **审计步骤**:

  1. 检查 `.sisyphus/plans/frontend-refactor.md` 中的每个 TODO
  2. 验证对应的证据文件存在
  3. 检查代码库中没有禁止的模式

  **Output**: `Must Have [Y/Y] | Must NOT Have [Y/Y] | Tasks [N/N] | VERDICT: APPROVE/REJECT`
- [x] **TF2. 代码质量审查** - `unspecified-high`

  **What to do**: 运行完整的代码质量检查

  **检查项**:

  - [ ] TypeScript: `npx tsc --noEmit` → 0 errors
  - [ ] ESLint: `bun run lint` → 0 errors
  - [ ] Tests: `bun test` → all pass
  - [ ] Build: `bun run build` → success

  **AI Slop 检测**:

  - [ ] 无 `any` 类型（除必要位置）
  - [ ] 无 `console.log`（除 error/warn）
  - [ ] 无未使用的变量/导入
  - [ ] 无重复代码

  **Output**: `Build [PASS] | Lint [PASS] | Tests [N pass] | Quality [PASS/WARN/FAIL] | VERDICT`
- [x] **TF3. 完整回归测试** - `unspecified-high`

  **What to do**: 执行全面的回归测试

  **测试范围**:

  1. **单元测试**: `bun test` - 对比基线测试通过率
  2. **E2E 测试**: `bunx playwright test` - 对比基线 E2E 通过率
  3. **手动验证**: 关键用户流程
     - 登录/注册
     - 创建/编辑/删除 Skill
     - 文件树操作（展开/折叠/选择）
     - 版本控制（保存/回滚）
     - 语言切换

  **输出**: `Unit [N/N pass] | E2E [N/N pass] | Manual [PASS/WARN] | VERDICT`

  **Evidence**: `.sisyphus/final-regression-test.txt`

---

## Commit Strategy

**工作模式**: 单人开发，直接在 `main` 分支上工作

**Wave 检查点与提交流程**（单人模式）：

```
1. 完成 Wave 的所有任务（直接在 main 分支上）
2. 运行预提交检查（见下方）
3. 逐个提交 Wave 的更改（每个任务一个提交）
4. 🛑 STOP - 等待用户验收
5. 用户审查代码和测试结果
6. 用户确认 "继续 Wave X+1"
7. 继续下一个 Wave（仍在 main 分支上）
```

**Wave 提交标记**（单人模式，main 分支）：

```bash
# Wave 0 完成时（已在 main 分支上）
git add .
git commit -m "chore: complete Wave 0 - setup and configuration"
# 🛑 等待用户验收

# Wave 1 完成时
git add .
git commit -m "chore: complete Wave 1 - configuration fixes"
# 🛑 等待用户验收

# ... 以此类推
```

**多人协作模式**（如需切换到此模式）：

- 为每个 Wave 创建功能分支：`git checkout -b refactor/wave-X`
- Wave 完成后合并到 main：`git checkout main && git merge refactor/wave-X`
- 删除功能分支：`git branch -d refactor/wave-X`

**Wave 提交**:

- Wave 0: 4 个独立提交（每个任务一个）+ 1 个 Wave 完成标记提交
- Wave 1: 4 个独立提交（配置修复逐个提交）+ 1 个 Wave 完成标记提交
- Wave 2: 5 个独立提交（目录重组逐个提交）+ 1 个 Wave 完成标记提交
- Wave 3: 5 个独立提交（架构重构逐个提交）+ 1 个 Wave 完成标记提交
- Wave 4: 4 个独立提交（性能优化和验证）+ 1 个 Wave 完成标记提交

**提交信息格式**:

```
type(scope): description

- type: chore|fix|refactor|feat|perf|style
- scope: config|components|lib|hooks|stores|types|tests
- description: 英文，小写，简洁

Example:
chore(config): add ESLint configuration with Next.js rules
refactor(components): reorganize into feature-based directory structure
perf(skills): add React.memo to SkillCard for render optimization
```

**预提交检查**（每个 Wave 的最后任务）:

```bash
# Wave 0
npx tsc --noEmit  # T0.3 需要验证类型

# Wave 1
bun run lint      # T1.4
npx tsc --noEmit  # T1.3

# Wave 2-4
bun run lint
npx tsc --noEmit
bun test
```

**用户验收指令**:

- 用户说 "继续" / "继续 Wave X" / "下一步" → 继续执行下一个 Wave
- 用户说 "回滚" / "撤销" / "重来" → 回滚当前 Wave 到上一个检查点
- 用户说 "暂停" / "停止" → 暂停执行，保存当前状态

---

## Success Criteria

### Wave 检查点验收标准

每个 Wave 完成后，执行以下验收检查：

**Wave 0 验收清单**:

- [X] ~~功能分支 `refactor/frontend-optimization` 已创建~~（单人模式：直接在 main 分支工作）
- [X] 测试基线已捕获 (`.sisyphus/baseline-tests.txt`)
- [X] E2E 基线已捕获 (`.sisyphus/baseline-e2e.txt`)
- [X] ESLint 配置已创建 (`eslint.config.mjs`)
- [X] Zustand 类型已定义 (`stores/types.ts`)
- [X] next.config.js 已更新（移除 ignores）
- [X] **用户确认**: "继续 Wave 1"

**Wave 1 验收清单**:

- [ ] `tailwind.config.ts` 已删除
- [ ] Tailwind 主题已迁移到 `globals.css`
- [ ] TypeScript 零错误 (`npx tsc --noEmit`)
- [ ] ESLint 零错误 (`bun run lint`)
- [ ] 开发服务器正常启动，样式正确
- [X] **用户确认**: "继续 Wave 2"

**Wave 2 验收清单**:

- [ ] `i18n/` 结构正确（config/ + locales/）
- [ ] `messages/` 已删除
- [ ] `lib/file-icons.tsx` 已移动到 `components/`
- [ ] `app/lib/` 已删除，`lib/auth.ts` 存在
- [ ] `components/` 按 feature 重组完成
- [ ] 重复测试文件已删除
- [ ] 构建成功，无导入错误
- [X] **用户确认**: "继续 Wave 3"

**Wave 3 验收清单**:

- [ ] `parseApiError` 统一在 `lib/errors.ts`
- [ ] Monaco Editor 无 `any` 类型
- [ ] `useFileTree` 已拆分完成
- [ ] `stores/skillsStore.ts` 已创建
- [ ] `types/index.ts` barrel export 存在
- [ ] 构建成功，测试通过
- [ ] **用户确认**: "继续 Wave 4"

**Wave 4 验收清单**:

- [ ] SkillCard 使用 React.memo
- [ ] 过滤逻辑使用 useMemo
- [ ] FileTree 渲染已优化
- [ ] 最终构建验证通过
- [ ] 所有检查命令通过 (lint, tsc, test, build)
- [ ] **用户确认**: "开始 Final Verification"

---

### 必须完成的核心指标

| 指标                        | 目标        | 验证命令                                                 |
| --------------------------- | ----------- | -------------------------------------------------------- |
| **TypeScript 零错误** | 0 errors    | `npx tsc --noEmit`                                     |
| **ESLint 零错误**     | 0 errors    | `bun run lint`                                         |
| **构建成功**          | 0 errors    | `bun run build`                                        |
| **测试通过**          | ≥ 基线     | `bun test`                                             |
| **目录精简**          | 10 顶层目录 | `ls -d */ \| wc -l`                                     |
| **代码重复**          | 消除        | `grep -r "parseApiError" app/ components/ \| wc -l` = 0 |

### 最终检查清单

- [ ] `tailwind.config.ts` 已删除
- [ ] `eslint.config.mjs` 存在且生效
- [ ] `next.config.js` 无 ignoreDuringBuilds/ignoreBuildErrors
- [ ] `messages/` 已合并到 `i18n/locales/`
- [ ] `app/lib/` 已删除
- [ ] `lib/file-icons.tsx` 已移动到 `components/`
- [ ] `components/` 按 feature 组织（ui/, skills/, file-tree/, editors/, providers/）
- [ ] `stores/` 包含 Zustand stores
- [ ] `types/index.ts` barrel export 存在
- [ ] `lib/file-utils.test.ts` 重复文件已删除
- [ ] Monaco Editor 无 `any` 类型
- [ ] Skills 页面使用 Zustand Store
- [ ] useFileTree 已拆分为小 hooks
- [ ] SkillCard 使用 React.memo
- [ ] 过滤逻辑使用 useMemo

### 证据文件清单

所有任务执行后，`.sisyphus/evidence/` 应包含：

```
.sisyphus/evidence/
├── t0-1-branch.txt
├── t0-1-baseline.txt
├── t0-2-config-exists.txt
├── t0-3-types.txt
├── t0-4-config.txt
├── t1-1-deleted.txt
├── t1-2-theme.txt
├── t1-2-visual.png
├── t1-3-no-errors.txt
├── t1-4-no-errors.txt
├── t2-1-structure.txt
├── t2-4-build.txt
├── t3-4-store.txt
├── t4-4-build.txt
└── t4-4-checks.txt
```

---

## 风险评估与回滚策略

### 风险等级

| 风险                            | 等级 | 缓解措施                             |
| ------------------------------- | ---- | ------------------------------------ |
| Tailwind 配置破坏样式           | 高   | T1.2 包含视觉验证，备份原配置        |
| TypeScript 严格模式暴露大量错误 | 中   | 分批修复，高优先级错误先修           |
| 文件移动破坏导入路径            | 中   | 使用 IDE 重构工具，T2.4 包含构建验证 |
| Zustand Store 引入 bug          | 中   | 保持原 Hook API 不变，逐步迁移       |
| 性能优化无效或负优化            | 低   | 使用 React DevTools Profiler 验证    |

### 回滚策略

**如果 Wave 1 失败**（配置修复）：

- 回滚 `next.config.js` 恢复 ignoreDuringBuilds
- 恢复 `tailwind.config.ts`（从备份）
- 重置 ESLint 配置

**如果 Wave 2 失败**（目录重组）：

- 使用 git 回滚到 Wave 1 完成状态
- 手动恢复文件位置

**如果 Wave 3-4 失败**：

- 回滚到上一个成功的 Wave
- 修复问题后继续

### 检查点

每个 Wave 完成后，执行检查点验证：

```bash
# Wave 0 检查点
git add .
git commit -m "chore: complete Wave 0 - setup and configuration"

# Wave 1 检查点
git add .
git commit -m "chore: complete Wave 1 - configuration fixes"
# ... 以此类推
```

如果 Wave 失败，可以回滚到上一个检查点：

```bash
git reset --hard HEAD~N  # N = 要回滚的提交数
```

---

## 后续建议（超出本计划范围）

1. **添加 Storybook** - 用于组件文档和测试
2. **引入 React Query/TanStack Query** - 替代手写 API 调用和缓存
3. **添加 Husky + lint-staged** - 预提交钩子强制代码质量
4. **设置 CI/CD 流水线** - GitHub Actions 自动检查
5. **添加监控和日志** - Sentry 错误追踪
6. **性能基准测试** - Lighthouse CI
7. **完善测试覆盖** - 目标 80%+ 单元测试覆盖率

---

*计划生成时间: 2026-02-19*
*计划版本: v1.0*
*Metis Review: 已审查，关键问题已修正*
