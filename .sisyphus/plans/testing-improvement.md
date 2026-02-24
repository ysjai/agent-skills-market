# 测试完善工作计划

## TL;DR

> **目标**: 将测试覆盖率从65%提升到85%+
> 
> **交付物**: 15+新测试文件，覆盖率报告，CI/CD集成
> 
> **预计工时**: 16-20小时（3-4天）
> **并行度**: 高 - 多模块可同时进行
> **关键路径**: 基础设施 → 组件测试 → 集成测试 → CI集成

---

## Context

### Current Test Coverage

| Module | Coverage | Status | Test Files |
|--------|----------|--------|------------|
| Frontend API Client | ~75% | ⚠️ | lib/__tests__/api.test.ts |
| Frontend Auth | ~60% | ⚠️ | lib/__tests__/auth.test.ts |
| Frontend File Utils | ~40% | ❌ | lib/file-utils.test.ts |
| Frontend Components | ~10% | ❌ | 无 |
| Backend Auth API | ~80% | ✅ | tests/integration/test_auth_api.py |
| Backend Skills API | ~60% | ⚠️ | tests/integration/test_skills_api.py |
| Backend CRUD | ~30% | ❌ | 无单元测试 |

**Total Estimated Coverage**: ~65%
**Target Coverage**: 85%+

### Gap Analysis

1. **组件测试缺失**: FileTree, FilePreview, TextEditor, MarkdownEditor等核心组件无测试
2. **端到端测试**: 无E2E测试覆盖用户流程
3. **错误边界测试**: 仅基础错误测试，缺少边界情况
4. **CRUD单元测试**: 直接测试数据库操作
5. **覆盖率报告**: 未配置覆盖率收集和可视化
6. **CI/CD集成**: 测试未集成到CI流程

---

## Work Objectives

### Core Objective
建立完整的测试体系，覆盖核心功能、组件、集成和端到端场景，确保代码质量和回归防护。

### Concrete Deliverables
1. 组件测试：FileTree, FilePreview, TextEditor, MarkdownEditor, Button
2. API集成测试：Skills CRUD, Tree操作, Blob操作
3. 覆盖率报告配置（frontend & backend）
4. GitHub Actions CI集成
5. 端到端测试（关键用户流程）
6. CRUD单元测试

### Definition of Done
- [ ] 覆盖率≥85%（整体）
- [ ] 所有新增代码有测试
- [ ] CI自动运行测试
- [ ] 测试失败阻止合并
- [ ] 覆盖率下降警告

### Must Have
- 核心组件测试（FileTree, FilePreview）
- API集成测试覆盖所有端点
- 覆盖率报告可查看

### Must NOT Have
- 不测试第三方库
- 不测试简单的getter/setter
- 不过度测试（>95%边际效益低）

---

## Verification Strategy

### Agent-Executed QA Scenarios

#### Scenario 1: 覆盖率报告生成
```
Tool: Bash
Preconditions: 安装依赖
Steps:
  1. cd frontend && bun test --coverage
  2. 验证生成coverage/lcov-report/index.html
  3. 打开报告，验证显示覆盖率数据
  4. cd backend && pytest --cov=app --cov-report=html
  5. 验证生成htmlcov/index.html
Expected Result: HTML覆盖率报告可正常查看
Evidence: 报告截图保存到 .sisyphus/evidence/coverage-report.png
```

#### Scenario 2: FileTree组件测试
```
Tool: Bash
Steps:
  1. cd frontend
  2. 运行：bun test components/__tests__/FileTree.test.tsx
  3. 验证测试通过（✓）
  4. 验证测试覆盖：渲染、展开/折叠、选择、拖拽
Expected Result: FileTree测试通过，覆盖率>80%
Evidence: 测试输出截图
```

#### Scenario 3: CI Pipeline测试
```
Tool: Bash
Steps:
  1. 提交代码到feature分支
  2. 创建Pull Request
  3. 验证GitHub Actions触发
  4. 验证所有检查通过（绿色✓）
  5. 验证覆盖率评论发布到PR
Expected Result: CI流程正常运行
Evidence: PR页面截图
```

#### Scenario 4: 端到端登录流程
```
Tool: Playwright (待配置)
Steps:
  1. 启动前后端服务
  2. 运行：npx playwright test e2e/auth.spec.ts
  3. 验证测试自动打开浏览器
  4. 验证执行注册→登录→访问Skills→登出流程
  5. 验证测试通过
Expected Result: E2E测试覆盖完整用户流程
Evidence: Playwright报告（test-results/）
```

---

## Execution Strategy

### Wave 1: 基础设施（4-6小时）
```
├── Task 1: 配置前端覆盖率报告 [90分钟]
├── Task 2: 配置后端覆盖率报告 [90分钟]
├── Task 3: 创建测试fixtures和mocks [120分钟]
└── Task 4: 添加GitHub Actions CI [120分钟]
```

### Wave 2: 组件测试（6-8小时）
```
├── Task 5: FileTree组件测试 [120分钟]
├── Task 6: FilePreview组件测试 [90分钟]
├── Task 7: TextEditor组件测试 [90分钟]
├── Task 8: Button/Input基础组件测试 [60分钟]
└── Task 9: MarkdownEditor组件测试 [90分钟]
```

### Wave 3: API与集成测试（4-6小时）
```
├── Task 10: Skills API完整测试 [120分钟]
├── Task 11: Tree操作测试 [90分钟]
├── Task 12: Blob操作测试 [60分钟]
└── Task 13: CRUD单元测试 [90分钟]
```

### Wave 4: E2E测试（2-4小时）
```
├── Task 14: Playwright配置 [60分钟]
└── Task 15: 关键用户流程E2E测试 [120分钟]
```

---

## TODOs

- [ ] 1. 配置前端覆盖率报告

  **What to do**:
  - 更新 `frontend/package.json` 添加coverage脚本
  - 配置bun test覆盖率输出格式
  - 创建 `.nycrc` 或配置忽略文件（node_modules, types等）

  **Must NOT do**:
  - 不覆盖第三方库代码
  - 不覆盖类型定义文件

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocked By**: None

  **Changes**:
  ```json
  // package.json
  {
    "scripts": {
      "test": "bun test",
      "test:coverage": "bun test --coverage",
      "test:coverage:report": "bun test --coverage && open coverage/index.html"
    }
  }
  ```

  **Acceptance Criteria**:
  - [ ] `bun test --coverage` 正常运行
  - [ ] 生成HTML报告
  - [ ] 显示行覆盖率、分支覆盖率
  - [ ] Agent-Executed QA: 运行Scenario 1通过

  **Commit**: YES
  - Message: `chore(test): add frontend test coverage reporting`
  - Files: `frontend/package.json`

- [ ] 2. 配置后端覆盖率报告

  **What to do**:
  - 添加pytest-cov到requirements-dev.txt
  - 配置 `.coveragerc` 文件
  - 添加覆盖率脚本

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Files**:
  ```ini
  # .coveragerc
  [run]
  source = app
  omit = 
      */tests/*
      */venv/*
      */migrations/*
      */alembic/*
  
  [report]
  exclude_lines =
      pragma: no cover
      def __repr__
      raise AssertionError
      raise NotImplementedError
  ```

  **Acceptance Criteria**:
  - [ ] `pytest --cov=app` 运行成功
  - [ ] 生成HTML报告
  - [ ] 覆盖率>=80%显示为绿色

  **Commit**: YES
  - Message: `chore(test): add backend test coverage with pytest-cov`

- [ ] 3. 创建测试fixtures和mocks

  **What to do**:
  - 扩展 `backend/tests/conftest.py`
  - 创建 `frontend/test/fixtures/` 目录
  - 添加mock数据和工厂函数

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Backend Fixtures**:
  ```python
  # conftest.py additions
  @pytest_asyncio.fixture
  async def test_skill(db_session, test_user):
      """Create a test skill."""
      skill = Skill(user_id=test_user.id, name="Test Skill", slug="test-skill")
      db_session.add(skill)
      await db_session.commit()
      yield skill
  
  @pytest_asyncio.fixture
  async def test_tree(db_session, test_skill):
      """Create a test tree structure."""
      tree = Tree(data={"entries": []})
      db_session.add(tree)
      await db_session.commit()
      yield tree
  ```

  **Frontend Fixtures**:
  ```typescript
  // test/fixtures/skills.ts
  export const mockSkill = {
    id: "test-skill-id",
    name: "Test Skill",
    slug: "test-skill",
    description: "A test skill",
    user_id: "test-user-id",
    tree_id: "test-tree-id",
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };
  ```

  **Commit**: YES
  - Message: `test: add test fixtures for skills and trees`

- [ ] 4. 添加GitHub Actions CI

  **What to do**:
  - 创建 `.github/workflows/test.yml`
  - 配置前后端测试并行运行
  - 配置覆盖率上传（可选：Codecov）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Workflow File**:
  ```yaml
  # .github/workflows/test.yml
  name: Tests
  
  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]
  
  jobs:
    frontend-test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - uses: oven-sh/setup-bun@v1
        - run: cd frontend && bun install
        - run: cd frontend && bun test
        - run: cd frontend && bun test --coverage
        
    backend-test:
      runs-on: ubuntu-latest
      services:
        postgres:
          image: postgres:16
          env:
            POSTGRES_PASSWORD: postgres
          options: >-
            --health-cmd pg_isready
            --health-interval 10s
      steps:
        - uses: actions/checkout@v3
        - uses: actions/setup-python@v4
          with:
            python-version: '3.12'
        - run: cd backend && pip install -r requirements.txt -r requirements-dev.txt
        - run: cd backend && pytest --cov=app
  ```

  **Acceptance Criteria**:
  - [ ] CI配置文件存在
  - [ ] PR触发测试运行
  - [ ] 测试结果显示在PR中
  - [ ] Agent-Executed QA: 运行Scenario 3通过

  **Commit**: YES
  - Message: `ci: add GitHub Actions workflow for automated testing`

- [ ] 5. FileTree组件测试

  **What to do**:
  - 创建 `frontend/components/__tests__/FileTree.test.tsx`
  - 测试：渲染、展开/折叠、文件选择、拖拽操作
  - Mock API调用

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Test Structure**:
  ```typescript
  describe('FileTree', () => {
    it('should render file tree with entries', () => {
      // 测试渲染
    });
    
    it('should expand/collapse folders on click', () => {
      // 测试展开折叠
    });
    
    it('should call onFileSelect when file clicked', () => {
      // 测试选择回调
    });
    
    it('should handle drag and drop operations', () => {
      // 测试拖拽
    });
    
    it('should load tree data from API', async () => {
      // 测试API集成
    });
  });
  ```

  **Acceptance Criteria**:
  - [ ] 组件渲染测试
  - [ ] 交互测试（点击、拖拽）
  - [ ] API集成测试
  - [ ] 覆盖率>80%
  - [ ] Agent-Executed QA: 运行Scenario 2通过

  **Commit**: YES
  - Message: `test(components): add FileTree component tests`

- [ ] 6. FilePreview组件测试

  **What to do**:
  - 测试不同类型文件预览（text, image, pdf）
  - 测试下载功能
  - 测试错误处理

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Commit**: YES
  - Message: `test(components): add FilePreview component tests`

- [ ] 7. TextEditor组件测试

  **What to do**:
  - 测试编辑器渲染
  - 测试内容变更
  - 测试保存操作
  - 测试语法高亮（Monaco Editor）

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Commit**: YES
  - Message: `test(components): add TextEditor component tests`

- [ ] 8. Button/Input基础组件测试

  **What to do**:
  - 测试渲染
  - 测试点击事件
  - 测试变体样式
  - 测试disabled状态

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Commit**: YES
  - Message: `test(components): add Button and Input component tests`

- [ ] 9. MarkdownEditor组件测试

  **What to do**:
  - 测试渲染
  - 测试编辑和预览切换
  - 测试图片上传

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Commit**: YES
  - Message: `test(components): add MarkdownEditor component tests`

- [ ] 10. Skills API完整测试

  **What to do**:
  - 扩展 `backend/tests/integration/test_skills_api.py`
  - 测试所有CRUD操作
  - 测试权限控制
  - 测试错误情况

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Test Cases**:
  ```python
  class TestSkillsCRUD:
      async def test_create_skill_success(self, client, auth_token):
          pass
      
      async def test_create_skill_duplicate_slug(self, client, auth_token, test_skill):
          pass
      
      async def test_get_skill_not_found(self, client, auth_token):
          pass
      
      async def test_update_skill_unauthorized(self, client, auth_token, test_skill):
          pass
      
      async def test_delete_skill_cascade(self, client, auth_token, test_skill):
          pass
  ```

  **Commit**: YES
  - Message: `test(api): complete Skills API integration tests`

- [ ] 11. Tree操作测试

  **What to do**:
  - 创建 `backend/tests/integration/test_trees_api.py`
  - 测试tree创建、更新、删除
  - 测试entries操作

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Commit**: YES
  - Message: `test(api): add Tree API integration tests`

- [ ] 12. Blob操作测试

  **What to do**:
  - 测试blob上传、下载
  - 测试压缩/解压
  - 测试内容哈希

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Commit**: YES
  - Message: `test(api): add Blob API integration tests`

- [ ] 13. CRUD单元测试

  **What to do**:
  - 创建 `backend/tests/unit/test_crud_user.py`
  - 创建 `backend/tests/unit/test_crud_skill.py`
  - 直接测试CRUD方法，不通过HTTP

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Commit**: YES
  - Message: `test(unit): add CRUD layer unit tests`

- [ ] 14. Playwright配置

  **What to do**:
  - 安装Playwright: `npm install -D @playwright/test`
  - 创建 `frontend/e2e/` 目录
  - 配置playwright.config.ts

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4

  **Config**:
  ```typescript
  // playwright.config.ts
  export default defineConfig({
    testDir: './e2e',
    fullyParallel: true,
    forbidOnly: !!process.env.CI,
    retries: process.env.CI ? 2 : 0,
    workers: process.env.CI ? 1 : undefined,
    reporter: 'html',
    use: {
      baseURL: 'http://localhost:3000',
      trace: 'on-first-retry',
    },
  });
  ```

  **Acceptance Criteria**:
  - [ ] Playwright安装成功
  - [ ] 配置可运行
  - [ ] `npx playwright test` 可执行

  **Commit**: YES
  - Message: `test(e2e): setup Playwright for end-to-end testing`

- [ ] 15. 关键用户流程E2E测试

  **What to do**:
  - 创建 `frontend/e2e/auth.spec.ts` - 注册/登录/登出
  - 创建 `frontend/e2e/skills.spec.ts` - 创建/编辑/删除Skill
  - 创建 `frontend/e2e/files.spec.ts` - 文件操作

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4

  **Example Test**:
  ```typescript
  // e2e/auth.spec.ts
  test('complete auth flow', async ({ page }) => {
    // Register
    await page.goto('/register');
    await page.fill('[name="email"]', 'test@example.com');
    await page.fill('[name="password"]', 'Test123!');
    await page.click('button[type="submit"]');
    
    // Should redirect to skills page
    await expect(page).toHaveURL('/skills');
    
    // Logout
    await page.click('[data-testid="logout"]');
    await expect(page).toHaveURL('/login');
  });
  ```

  **Acceptance Criteria**:
  - [ ] 注册→登录→使用→登出流程测试
  - [ ] Skill CRUD流程测试
  - [ ] 文件上传下载测试
  - [ ] Agent-Executed QA: 运行Scenario 4通过

  **Commit**: YES
  - Message: `test(e2e): add critical user flow end-to-end tests`

---

## Commit Strategy

| After Task | Message | Files |
|------------|---------|-------|
| 1 | `chore(test): add frontend test coverage reporting` | frontend/package.json |
| 2 | `chore(test): add backend test coverage with pytest-cov` | .coveragerc |
| 3 | `test: add test fixtures for skills and trees` | tests/conftest.py, test/fixtures/ |
| 4 | `ci: add GitHub Actions workflow for automated testing` | .github/workflows/test.yml |
| 5 | `test(components): add FileTree component tests` | components/__tests__/FileTree.test.tsx |
| 6-9 | `test(components): add X component tests` | components/__tests__/*.test.tsx |
| 10-13 | `test(api): add X API tests` | tests/integration/*.py |
| 14 | `test(e2e): setup Playwright` | playwright.config.ts |
| 15 | `test(e2e): add critical user flow tests` | e2e/*.spec.ts |

---

## Success Criteria

### Coverage Targets
```
Frontend:
- Statements: ≥85%
- Branches: ≥80%
- Functions: ≥85%
- Lines: ≥85%

Backend:
- Statements: ≥85%
- Branches: ≥80%
- Functions: ≥85%
```

### Verification Commands
```bash
# 前端测试
cd frontend && bun test --coverage

# 后端测试
cd backend && pytest --cov=app --cov-report=term-missing

# E2E测试
cd frontend && npx playwright test

# 整体覆盖率检查
./scripts/check-coverage.sh  # 需创建
```

### Final Checklist
- [ ] Coverage ≥85% for all modules
- [ ] CI passes on every PR
- [ ] No failing tests
- [ ] E2E tests cover critical paths
- [ ] Coverage report accessible

---

## Post-Completion

After completing this plan:
1. Set up coverage monitoring (Codecov/ Coveralls)
2. Create testing guidelines document
3. Add pre-commit hook for test running
4. Consider mutation testing for critical code

**Expected Outcome**: Test coverage increases from 65% to 85%+, CI ensures quality
