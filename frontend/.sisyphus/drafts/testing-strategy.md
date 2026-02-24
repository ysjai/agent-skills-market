# 前端测试策略探讨

## 项目概况（已确认）

**技术栈**:
- Next.js 15 (App Router)
- React 19
- Bun test (测试框架)
- Tailwind CSS 4
- Zod (表单验证)
- Radix UI + Lucide React

**代码结构**:
- `app/` - 页面和API路由 (10个文件)
- `lib/` - 工具函数和业务逻辑 (12个文件)

**测试基础设施** (已有):
- ✅ Bun test (bun test, bun test --coverage)
- ✅ @testing-library/react
- ✅ @testing-library/jest-dom
- ✅ @testing-library/user-event
- ✅ happy-dom

**现有测试**:
- 仅有 4 个测试文件，覆盖率很低
- 覆盖: lib/auth.ts, lib/api.ts, lib/file-utils.ts

## 探索方向
1. 代码库结构和技术栈
2. 现有测试基础设施
3. 测试覆盖情况

## 讨论要点（待填充）
- 单元测试策略
- 集成测试策略
- E2E测试策略
- 测试金字塔
- 覆盖率目标
- Mock策略

## 用户核心需求（已确认）

1. **颗粒度大** - 避免测试实现细节，重构时不用改测试
2. **运行速度快** - Bun test 本身已满足
3. **稳定** - 不因实现细节变化而失败
4. **CI/CD 友好** - 可在流水线运行

## 核心代码分析

### lib/file-utils.ts
- `getFileType(fileName: string)`: 根据扩展名判断文件类型
- 纯函数，输入输出明确 ✅ 适合测试

### lib/file-tree-utils.ts
- `buildTree(entries)`: 从 Git 风格的 entries 构建树
- `findNodeByPath()`, `findFirstFileInDirectory()`, `applyExpandedState()`
- 纯函数为主，逻辑清晰 ✅ 适合测试

### lib/api.ts
- 已有 459 行详细测试，但粒度过细
- 建议：简化测试，只保留关键场景

### lib/utils.ts
- `cn(...inputs)`: tailwind-merge + clsx
- 纯函数 ✅ 适合测试

---

# 前端测试策略实施计划

## TL;DR

> **目标**: 建立"颗粒度大、重构友好、快速稳定、CI友好"的测试体系
> 
> **核心策略**: 行为驱动测试 + E2E 补充 + 精简单元测试
> 
> **交付物**: 
> - 4 个重构的测试文件（lib/）
> - Playwright E2E 测试基础
> - CI/CD 测试流水线配置

---

## Context

### 项目背景
- **阶段**: MVP (新项目)
- **团队**: 小团队 (1-3人)
- **技术栈**: Next.js 15 + React 19 + Bun test + Tailwind CSS 4

### 用户核心需求
1. **颗粒度大** - 避免测试实现细节，重构时不用改测试
2. **运行速度快** - Bun test 本身已满足
3. **稳定** - 不因实现细节变化而失败
4. **CI/CD 友好** - 可在流水线运行

### 当前测试状况
- ✅ 测试框架已配置 (Bun test + @testing-library)
- ❌ 现有测试粒度过细 (api.test.ts 有 459 行)
- ❌ 测试覆盖率低 (仅 4 个测试文件)

---

## Work Objectives

### 核心目标
建立一套"行为驱动、粗粒度、低维护"的测试体系

### 具体交付物

| # | 交付物 | 描述 |
|---|--------|------|
| 1 | `lib/__tests__/file-utils.test.ts` | 文件工具测试（粗粒度风格） |
| 2 | `lib/__tests__/file-tree.test.ts` | 文件树构建测试（粗粒度风格） |
| 3 | `lib/__tests__/api.integration.test.ts` | API 集成测试（简化版，~80行） |
| 4 | `lib/__tests__/utils.test.ts` | 通用工具测试 |
| 5 | `e2e/` 目录 | Playwright E2E 测试基础结构 |
| 6 | `playwright.config.ts` | Playwright 配置文件 |
| 7 | `.github/workflows/test.yml` | CI 测试流水线 |

### 定义
- [ ] 所有 lib/ 测试采用粗粒度风格
- [ ] 单个测试函数不超过 5 个断言
- [ ] E2E 测试覆盖核心用户流程
- [ ] CI 流水线可运行所有测试

---

## Verification Strategy

### 测试决策
- **自动化测试**: YES (Tests-after)
- **框架**: Bun test (单元/集成) + Playwright (E2E)
- **覆盖目标**: 
  - lib/: 60-70% 语句覆盖
  - E2E: 核心用户流程

### QA 策略
| 类型 | 工具 | 场景 |
|------|------|------|
| 单元/集成 | Bun test | `bun test` |
| E2E | Playwright | `npx playwright test` |
| CI | GitHub Actions | 每次 push 自动运行 |

---

## TODOs

### Wave 1: 单元/集成测试重构 (3 tasks)

- [ ] **1. 重构 file-utils 测试**
  
  **What to do**:
  - 重写 `lib/__tests__/file-utils.test.ts`
  - 采用粗粒度风格：每个函数 1-3 个测试
  - 覆盖场景：正常输入、大小写、未知扩展名、空输入
  
  **Must NOT do**:
  - 不测试每个扩展名的单独情况
  - 不测试内部实现细节
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1
  
  **References**:
  - `lib/file-utils.ts` - 被测试的源文件
  - `lib/__tests__/api.test.ts` - 参考现有测试结构（风格待改进）
  
  **Acceptance Criteria**:
  - [ ] 测试文件创建: `lib/__tests__/file-utils.test.ts`
  - [ ] `bun test lib/__tests__/file-utils.test.ts` → PASS
  
  **QA Scenarios**:
  ```
  Scenario: 运行 file-utils 测试
    Tool: Bash
    Preconditions: 无
    Steps:
      1. cd 到项目根目录
      2. 执行 bun test lib/__tests__/file-utils.test.ts
    Expected Result: 所有测试通过
    Evidence: 终端输出 "X passed"
  ```

- [ ] **2. 重构 file-tree 测试**
  
  **What to do**:
  - 重写 `lib/__tests__/file-tree.test.ts`
  - 覆盖场景：正常构建、空输入、排序、嵌套目录
  - 粗粒度风格
  
  **Must NOT do**:
  - 不测试内部 ID 生成逻辑
  - 不测试路径规范化的每个边界
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: YES (与 Task 1, 3)
  - Parallel Group: Wave 1
  
  **References**:
  - `lib/file-tree-utils.ts` - 被测试的源文件
  - `types/file-tree.ts` - 相关类型定义
  
  **Acceptance Criteria**:
  - [ ] 测试文件创建: `lib/__tests__/file-tree.test.ts`
  - [ ] `bun test lib/__tests__/file-tree.test.ts` → PASS
  
  **QA Scenarios**:
  ```
  Scenario: 运行 file-tree 测试
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 执行 bun test lib/__tests__/file-tree.test.ts
    Expected Result: 所有测试通过
    Evidence: 终端输出 "X passed"
  ```

- [ ] **3. 简化 api 集成测试**
  
  **What to do**:
  - 创建 `lib/__tests__/api.integration.test.ts`
  - 大幅简化：459 行 → ~80 行
  - 只保留关键场景：GET/POST 成功、错误处理、401 处理
  
  **Must NOT do**:
  - 不测试每个 HTTP 方法的细节
  - 不测试 fetch 调用次数等实现细节
  - 不测试边界情况（空响应、非 JSON 等）
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: YES (与 Task 1, 2)
  - Parallel Group: Wave 1
  
  **References**:
  - `lib/api.ts` - 被测试的源文件
  - 现有 `lib/__tests__/api.test.ts` - 参考（需要精简）
  
  **Acceptance Criteria**:
  - [ ] 测试文件创建: `lib/__tests__/api.integration.test.ts`
  - [ ] `bun test lib/__tests__/api.integration.test.ts` → PASS
  - [ ] 代码行数 < 100 行
  
  **QA Scenarios**:
  ```
  Scenario: 运行 api 集成测试
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 执行 bun test lib/__tests__/api.integration.test.ts
    Expected Result: 所有测试通过
    Evidence: 终端输出 "X passed"
  ```

### Wave 2: 通用工具测试 + 删除旧测试 (2 tasks)

- [ ] **4. 创建 utils 测试**
  
  **What to do**:
  - 创建 `lib/__tests__/utils.test.ts`
  - 测试 `cn()` 函数的各种场景
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2
  
  **Acceptance Criteria**:
  - [ ] 测试文件创建
  - [ ] `bun test lib/__tests__/utils.test.ts` → PASS

- [ ] **5. 删除旧的细粒度测试**
  
  **What to do**:
  - 删除旧的 `lib/__tests__/api.test.ts`（已被简化版替代）
  - 可选：审查其他旧测试文件
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: [`git-master`]
  
  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2
  
  **Acceptance Criteria**:
  - [ ] 旧的 api.test.ts 已删除
  - [ ] `bun test` 仍然全部通过

### Wave 3: E2E 测试基础 (2 tasks)

- [ ] **6. 安装和配置 Playwright**
  
  **What to do**:
  - 安装 Playwright 依赖
  - 创建 `playwright.config.ts` 配置文件
  - 配置：headless 模式、baseURL、超时等
  
  **Must NOT do**:
  - 不配置复杂的 CI 报告（先用简单配置）
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: NO (需要先完成前面的测试)
  - Blocked By: Wave 1, 2
  
  **References**:
  - 官方文档: https://playwright.dev/docs/intro
  
  **Acceptance Criteria**:
  - [ ] `playwright.config.ts` 创建完成
  - [ ] `npx playwright install` 成功
  - [ ] `npx playwright test --version` 正常

- [ ] **7. 创建 E2E 测试基础结构**
  
  **What to do**:
  - 创建 `e2e/` 目录
  - 创建基础测试文件：登录流程、核心页面加载
  - 测试核心用户旅程
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: [`playwright`]
  
  **Parallelization**:
  - Can Run In Parallel: NO
  - Blocked By: Task 6
  
  **Acceptance Criteria**:
  - [ ] `e2e/` 目录创建
  - [ ] 至少 2 个 E2E 测试文件
  - [ ] `npx playwright test` 可运行（可以失败，但不能报错）
  
  **QA Scenarios**:
  ```
  Scenario: 运行 E2E 测试
    Tool: Bash
    Preconditions: 开发服务器运行中
    Steps:
      1. 执行 npx playwright test
    Expected Result: 测试可运行（结果可失败）
    Evidence: 终端输出测试运行结果
  ```

### Wave 4: CI/CD 集成 (1 task)

- [ ] **8. 配置 GitHub Actions CI**
  
  **What to do**:
  - 创建 `.github/workflows/test.yml`
  - 配置：安装依赖 → 运行单元测试 → 运行 E2E 测试
  - 设置触发条件：push 和 PR
  
  **Must NOT do**:
  - 不配置部署（只做测试）
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: NO
  - Blocked By: Task 7
  
  **References**:
  - GitHub Actions 文档
  
  **Acceptance Criteria**:
  - [ ] `.github/workflows/test.yml` 创建完成
  - [ ] 本地 `bun test` 通过
  - [ ] 本地 E2E 测试可运行
  
  **QA Scenarios**:
  ```
  Scenario: 模拟 CI 环境测试
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 执行 bun test
    Expected Result: 所有测试通过
    Evidence: 终端输出
  ```

### Wave FINAL: 验证 (1 task)

- [ ] **9. 完整验证**
  
  **What to do**:
  - 运行完整测试套件
  - 检查覆盖率报告
  - 验证 CI 配置语法正确
  
  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []
  
  **Parallelization**:
  - Can Run In Parallel: NO
  - Blocked By: Wave 4
  
  **Acceptance Criteria**:
  - [ ] `bun test` → 全部通过
  - [ ] `npx playwright test` → 可运行
  - [ ] 覆盖率报告生成成功
  
  **QA Scenarios**:
  ```
  Scenario: 完整测试套件
    Tool: Bash
    Preconditions: 无
    Steps:
      1. 执行 bun test --coverage
      2. 检查覆盖率输出
    Expected Result: 覆盖率 > 60%
    Evidence: 终端输出覆盖率报告
  ```

---

## Success Criteria

### 验证命令
```bash
# 单元/集成测试
bun test

# E2E 测试
npx playwright test

# 覆盖率
bun test --coverage
```

### 最终检查清单
- [ ] 所有 lib/ 测试采用粗粒度风格
- [ ] 单个测试函数不超过 5 个断言
- [ ] E2E 测试覆盖核心用户流程
- [ ] CI 流水线可运行所有测试
- [ ] 覆盖率目标达成
