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
| 文件 | 行数 | 风格 | 问题 |
|------|------|------|------|
| `api.test.ts` | 459 | 细粒度 | 测试 fetch 调用细节、错误处理流程 |
| `file-utils.test.ts` | 43 | 中等 | 可保留优化 |
| `auth.test.ts` | 36 | 最小 | 可不改动 |
| `setup.test.ts` | 15 | 基础 | 环境检查 |

### Metis 审查发现的问题
- 需先测量基线覆盖率
- 需明确定义"粗粒度"边界
- 需明确删除文件列表
- E2E 范围应进一步简化

---

## Work Objectives

### 核心目标
建立一套"行为驱动、粗粒度、低维护"的测试体系

### 具体交付物

| # | 交付物 | 描述 |
|---|--------|------|
| 1 | `lib/__tests__/file-utils.test.ts` | 文件工具测试（粗粒度风格） |
| 2 | `lib/__tests__/file-tree.test.ts` | 文件树构建测试（粗粒度风格） |
| 3 | `lib/__tests__/api.integration.test.ts` | API 集成测试（简化版） |
| 4 | `lib/__tests__/utils.test.ts` | 通用工具测试 |
| 5 | `e2e/` 目录 | Playwright E2E 测试（限 3 个简单测试） |
| 6 | `playwright.config.ts` | Playwright 配置文件 |
| 7 | `.github/workflows/test.yml` | CI 测试流水线 |

### 定义
- [x] 所有 lib/ 测试采用粗粒度风格
- [x] 单个测试文件不超过 100 行
- [x] 单个函数不超过 3 个测试用例
- [x] E2E 测试：最多 3 个，仅测页面加载，无交互
- [x] CI 仅运行 Bun test，无浏览器测试

---

## Guardrails (From Metis Review)

| # | Guardrail | 理由 |
|---|-----------|------|
| 1 | 测试文件不超过 100 行 | 防止回归到细粒度风格 |
| 2 | 单个函数不超过 3 个测试用例 | 保持粗粒度 |
| 3 | 只 Mock 外部依赖 (fetch/localStorage) | 不测试内部实现 |
| 4 | E2E: 最多 3 个测试，仅页面加载 | 简化维护 |
| 5 | CI: 仅 Bun test，无浏览器 | 保持快速 |
| 6 | 不设覆盖率门禁 | 无基线时会失败 |
| 7 | 不添加快照测试 | 维护负担大 |
| 8 | 不添加视觉回归测试 | 维护负担大 |
| 9 | 不测试 monaco-config.ts | 浏览器专用，低价值 |

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

- [x] **1. 测量基线 + 重构 file-utils 测试**

  **What to do**:
  - 运行 `bun test --coverage` 记录基线
  - 重写 `lib/__tests__/file-utils.test.ts`
  - 采用粗粒度风格：每个函数 1-3 个测试
  - 覆盖场景：正常输入、大小写、未知扩展名

  **Must NOT do**:
  - 不测试每个扩展名单独情况
  - 不测试内部实现细节
  - 文件不超过 50 行

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 1

  **References**:
  - `lib/file-utils.ts` - 被测试的源文件

  **Acceptance Criteria**:
  - [ ] 运行 `bun test --coverage` 记录基线
  - [ ] `lib/__tests__/file-utils.test.ts` 行数 ≤ 50
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

- [x] **2. 重构 file-tree 测试**

  **What to do**:
  - 重写 `lib/__tests__/file-tree.test.ts`
  - 覆盖场景：正常构建、空输入、排序、嵌套目录
  - 粗粒度风格

  **Must NOT do**:
  - 不测试内部 ID 生成逻辑
  - 不测试路径规范化的每个边界
  - 文件不超过 80 行

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: YES (与 Task 1, 3)
  - Parallel Group: Wave 1

  **References**:
  - `lib/file-tree-utils.ts` - 被测试的源文件

  **Acceptance Criteria**:
  - [ ] `lib/__tests__/file-tree.test.ts` 创建，行数 ≤ 80
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

- [x] **3. 简化 api 集成测试**

  **What to do**:
  - 创建 `lib/__tests__/api.integration.test.ts`
  - 大幅简化：459 行 → ~80 行
  - 只保留关键场景：
    - GET 成功返回数据
    - POST 成功提交数据
    - 401 错误抛出异常
    - 网络错误抛出异常
  - **不保留**：每个 HTTP 状态码的详细测试、fetch 调用细节

  **Must NOT do**:
  - 不测试每个 HTTP 方法的细节
  - 不测试 fetch 调用次数等实现细节
  - 不测试边界情况（空响应、非 JSON 等）
  - 文件不超过 100 行

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
  - [ ] `lib/__tests__/api.integration.test.ts` 创建，行数 ≤ 100
  - [ ] `bun test lib/__tests__/api.integration.test.ts` → PASS
  - [ ] 测试用例 ≤ 10 个

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

- [x] **4. 创建 utils 测试**

  **What to do**:
  - 创建 `lib/__tests__/utils.test.ts`
  - 测试 `cn()` 函数的各种场景
  - 文件不超过 30 行

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2

  **Acceptance Criteria**:
  - [ ] 测试文件创建，行数 ≤ 30
  - [ ] `bun test lib/__tests__/utils.test.ts` → PASS

- [x] **5. 删除旧的细粒度测试**

  **What to do**:
  - 删除旧的 `lib/__tests__/api.test.ts`（已被简化版替代）
  - 保留 `auth.test.ts`（36 行，无需改动）
  - 保留 `setup.test.ts`（15 行，无需改动）

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: [`git-master`]

  **Parallelization**:
  - Can Run In Parallel: YES
  - Parallel Group: Wave 2

  **Acceptance Criteria**:
  - [ ] 旧的 `lib/__tests__/api.test.ts` 已删除
  - [ ] `bun test` 仍然全部通过

### Wave 3: E2E 测试基础 (2 tasks)

- [x] **6. 安装和配置 Playwright**

  **What to do**:
  - 安装 Playwright 依赖
  - 创建 `playwright.config.ts` 配置文件
  - 配置：headless 模式、baseURL、超时等

  **Must NOT do**:
  - 不配置复杂的 CI 报告
  - 不配置视觉回归

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: []

  **Parallelization**:
  - Can Run In Parallel: NO
  - Blocked By: Wave 1, 2

  **References**:
  - 官方文档: https://playwright.dev/docs/intro

  **Acceptance Criteria**:
  - [ ] `playwright.config.ts` 创建完成
  - [ ] `npx playwright install` 成功
  - [ ] `npx playwright test --version` 正常

- [x] **7. 创建 E2E 测试基础结构**

  **What to do**:
  - 创建 `e2e/` 目录
  - 创建最多 3 个简单测试：
    1. 首页加载
    2. 登录页加载
    3. 技能列表页加载
  - **仅测试页面加载，不测试交互**
  - **无断言Beyond页面加载成功**

  **Must NOT do**:
  - 不测试文件上传流程
  - 不测试认证流程
  - 不测试 Monaco 编辑器
  - 不添加视觉回归
  - 测试文件不超过 2 个

  **Recommended Agent Profile**:
  - Category: `quick`
  - Skills: [`playwright`]

  **Parallelization**:
  - Can Run In Parallel: NO
  - Blocked By: Task 6

  **Acceptance Criteria**:
  - [ ] `e2e/` 目录创建
  - [ ] 测试文件 ≤ 2 个
  - [ ] 测试用例 ≤ 3 个
  - [ ] `npx playwright test` 可运行（可以失败，但不能报错）

  **QA Scenarios**:
  ```
  Scenario: 运行 E2E 测试
    Tool: Bash
    Preconditions: 开发服务器运行中 (npm run dev)
    Steps:
      1. 执行 npx playwright test
    Expected Result: 测试可运行
    Evidence: 终端输出测试运行结果
  ```

### Wave 4: CI/CD 集成 (1 task)

- [x] **8. 配置 GitHub Actions CI**

  **What to do**:
  - 创建 `.github/workflows/test.yml`
  - 配置流程：
    1. 安装依赖 (bun install)
    2. 运行单元测试 (bun test)
    3. **不运行 Playwright**（浏览器测试本地运行）
  - 设置触发条件：push 和 PR

  **Must NOT do**:
  - 不配置覆盖率门禁
  - 不运行浏览器测试
  - 不配置部署

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
  - [ ] 流水线执行时间目标 < 5 分钟

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

- [x] **9. 完整验证**

  **What to do**:
  - 运行完整测试套件
  - 检查覆盖率报告
  - 验证覆盖率相比基线有提升（或持平）

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
    Expected Result: 覆盖率 > 50%（因简化测试）
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
- [x] 所有 lib/ 测试采用粗粒度风格
- [x] 单个测试文件不超过 100 行
- [x] 单个函数不超过 3 个测试用例
- [x] E2E 测试 ≤ 3 个，仅页面加载
- [x] CI 流水线仅运行 Bun test
- [x] `bun test` 全部通过
- [x] Playwright 可运行
