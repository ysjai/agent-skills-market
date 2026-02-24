# 代码重构工作计划

## TL;DR

> **目标**: 消除代码坏味道，提升代码质量评分从7.5到8.5+
> 
> **交付物**: 重构后的核心组件，提取的公共逻辑，代码规范文档
> 
> **预计工时**: 12-16小时（2-3天）
> **并行度**: 中 - 依赖关系需要一定顺序
> **关键路径**: 分析 → 提取公共逻辑 → 重构组件 → 验证

---

## Context

### Current Code Quality Issues

| 坏味道 | 位置 | 严重程度 | 影响 |
|--------|------|----------|------|
| 函数过长 | skills.py:download_skill (95行) | 高 | 难以测试和维护 |
| 重复代码 | 多处404/403检查 | 中 | 维护成本高 |
| useState过多 | FileTree.tsx (10+状态) | 高 | 逻辑复杂，易出错 |
| 嵌套过深 | buildTree双重循环 | 中 | 可读性差 |
| Magic Numbers | auth.py:15*60 | 低 | 可读性差 |
| 类型断言 | file-utils.ts:as any | 中 | 类型安全降低 |
| 关注点分离不足 | FileTree.tsx | 高 | 测试困难 |

### Target Metrics

| 指标 | 当前 | 目标 |
|------|------|------|
| 平均函数长度 | ~45行 | <30行 |
| 重复代码块 | 8处 | 0处 |
| 组件文件大小 | ~800行 | <500行 |
| 类型断言 | 12处 | 0处 |

---

## Work Objectives

### Core Objective
系统性地重构代码，消除坏味道，提升可读性、可维护性和可测试性，同时保持功能不变。

### Concrete Deliverables
1. 重构FileTree组件（提取hooks，拆分组件）
2. 提取公共错误处理逻辑
3. 重构过长函数（download_skill, buildTree）
4. 统一常量管理
5. 消除类型断言
6. 创建代码规范文档

### Definition of Done
- [ ] 所有函数<50行
- [ ] 重复代码消除
- [ ] FileTree组件拆分为<300行
- [ ] 类型断言清零
- [ ] 所有测试通过
- [ ] 代码审查通过

### Must Have
- 功能保持不变（回归测试通过）
- 类型安全提升
- 性能不下降

### Must NOT Have
- 不引入新功能
- 不改变业务逻辑
- 不修改API契约

---

## Verification Strategy

### Agent-Executed QA Scenarios

#### Scenario 1: FileTree功能回归
```
Tool: Playwright / interactive_bash
Preconditions: 前后端服务运行
Steps:
  1. 打开Skills页面
  2. 创建一个skill
  3. 展开文件树
  4. 创建文件夹和文件
  5. 拖拽文件到不同文件夹
  6. 选择文件并预览
  7. 刷新页面，验证状态持久化
Expected Result: 所有操作与重构前行为一致
Evidence: 操作录屏或截图序列
```

#### Scenario 2: 性能对比
```
Tool: Bash
Preconditions: 可运行重构前后版本
Steps:
  1. 重构前：记录FileTree渲染时间（React DevTools Profiler）
  2. 重构后：记录相同操作渲染时间
  3. 验证性能无下降（允许±5%误差）
  4. 检查无额外重渲染
Expected Result: 性能持平或提升
Evidence: Profiler截图对比
```

#### Scenario 3: 代码质量检查
```
Tool: Bash
Steps:
  1. 运行：npx eslint frontend/ --max-warnings=0
  2. 运行：cd backend && ruff check . && ruff format --check .
  3. 运行：grep -r "as any" frontend/ | wc -l # 应为0
  4. 运行：grep -r "Exception:" backend/app/ | grep -v "JWTError" | wc -l # 应为0
Expected Result: 无lint错误，无类型断言，异常处理具体化
Evidence: 命令输出截图
```

#### Scenario 4: 函数长度检查
```
Tool: Bash
Steps:
  1. 统计重构前函数长度：grep -r "def " backend/app/ | wc -l
  2. 运行脚本检查所有函数<50行
  3. 检查FileTree.tsx总行数<500
Expected Result: 所有指标符合目标
Evidence: 脚本输出
```

---

## Execution Strategy

### Wave 1: 提取公共逻辑（3-4小时）
```
├── Task 1: 创建错误处理装饰器 [90分钟]
├── Task 2: 提取权限验证逻辑 [60分钟]
├── Task 3: 创建通用hooks [90 minutes]
└── Task 4: 统一常量管理 [60 minutes]
```

### Wave 2: 重构FileTree组件（4-6小时）
```
├── Task 5: 提取useFileTree hook [120分钟]
├── Task 6: 提取useFileUpload hook [60分钟]
├── Task 7: 拆分FileTree子组件 [120分钟]
└── Task 8: 重构buildTree函数 [60分钟]
```

### Wave 3: 重构后端函数（3-4小时）
```
├── Task 9: 重构download_skill函数 [90分钟]
├── Task 10: 重构create_skill函数 [60分钟]
├── Task 11: 优化异常处理 [60分钟]
└── Task 12: 消除类型断言 [60分钟]
```

### Wave 4: 验证和文档（2-4小时）
```
├── Task 13: 回归测试 [120分钟]
└── Task 14: 编写重构文档 [60分钟]
```

---

## TODOs

- [ ] 1. 创建错误处理装饰器

  **What to do**:
  - 创建 `backend/app/dependencies/common.py`
  - 实现 `verify_resource_ownership` 装饰器
  - 统一处理404/403错误

  **Must NOT do**:
  - 不改变错误响应格式
  - 不修改HTTP状态码

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocked By**: None

  **Implementation**:
  ```python
  # app/dependencies/common.py
  from functools import wraps
  
  def verify_ownership(get_resource, owner_field="user_id"):
      """Decorator to verify resource ownership."""
      def decorator(func):
          @wraps(func)
          async def wrapper(*args, **kwargs):
              db = kwargs.get('db')
              resource_id = kwargs.get('skill_id') or kwargs.get('project_id')
              current_user = kwargs.get('current_user')
              
              resource = await get_resource(db, id=resource_id)
              if not resource:
                  raise HTTPException(404, "Resource not found")
              
              if getattr(resource, owner_field) != current_user.id:
                  raise HTTPException(403, "Not authorized")
              
              kwargs['resource'] = resource
              return await func(*args, **kwargs)
          return wrapper
      return decorator
  
  # Usage
  @router.get("/{skill_id}")
  @verify_ownership(skill.get)
  async def get_skill(resource: Skill = None, ...):
      return SkillResponse.model_validate(resource)
  ```

  **Acceptance Criteria**:
  - [ ] 装饰器可用
  - [ ] 所有skills router使用装饰器
  - [ ] 测试通过
  - [ ] 删除重复的错误检查代码

  **Commit**: YES
  - Message: `refactor(dependencies): add ownership verification decorator`

- [ ] 2. 提取权限验证逻辑

  **What to do**:
  - 创建 `backend/app/dependencies/permissions.py`
  - 提取重复的权限检查

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Commit**: YES
  - Message: `refactor(permissions): extract permission checking logic`

- [ ] 3. 创建通用React hooks

  **What to do**:
  - 创建 `frontend/hooks/useLocalStorage.ts`
  - 创建 `frontend/hooks/useApi.ts`
  - 创建 `frontend/hooks/useToggle.ts`

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Implementation**:
  ```typescript
  // hooks/useLocalStorage.ts
  export function useLocalStorage<T>(key: string, initialValue: T) {
    const [storedValue, setStoredValue] = useState<T>(() => {
      if (typeof window === 'undefined') return initialValue;
      try {
        const item = window.localStorage.getItem(key);
        return item ? JSON.parse(item) : initialValue;
      } catch {
        return initialValue;
      }
    });
    
    const setValue = (value: T | ((val: T) => T)) => {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    };
    
    return [storedValue, setValue] as const;
  }
  ```

  **Acceptance Criteria**:
  - [ ] hooks可用
  - [ ] 有基本测试
  - [ ] FileTree等组件可使用

  **Commit**: YES
  - Message: `refactor(hooks): add reusable hooks for localStorage and API`

- [ ] 4. 统一常量管理

  **What to do**:
  - 创建 `frontend/lib/constants.ts`
  - 创建 `backend/app/core/constants.py`
  - 将所有Magic Numbers替换为常量

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **Constants**:
  ```python
  # backend/app/core/constants.py
  # Token expiration
  ACCESS_TOKEN_EXPIRE_MINUTES = 30
  REFRESH_TOKEN_EXPIRE_DAYS = 7
  ACCESS_TOKEN_MAX_AGE_SECONDS = 15 * 60  # 15 minutes
  REFRESH_TOKEN_MAX_AGE_SECONDS = 7 * 24 * 60 * 60  # 7 days
  
  # Pagination
  DEFAULT_PAGE_SIZE = 20
  MAX_PAGE_SIZE = 100
  
  # Validation
  MIN_PASSWORD_LENGTH = 8
  MAX_SLUG_LENGTH = 100
  ```

  **Acceptance Criteria**:
  - [ ] 所有Magic Numbers替换
  - [ ] 常量文件有注释说明
  - [ ] 测试通过

  **Commit**: YES
  - Message: `refactor(constants): centralize magic numbers into constants`

- [ ] 5. 提取useFileTree hook

  **What to do**:
  - 创建 `frontend/hooks/useFileTree.ts`
  - 从FileTree.tsx提取状态管理
  - 包括：节点加载、展开/折叠、选择逻辑

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖分析）
  - **Parallel Group**: Wave 2

  **Hook Interface**:
  ```typescript
  interface UseFileTreeOptions {
    treeId?: string;
    onFileSelect?: (path: string, blobId?: string) => void;
  }
  
  interface UseFileTreeReturn {
    nodes: FileTreeNode[];
    loading: boolean;
    error: string | null;
    selectedPath: string | undefined;
    expandedPaths: string[];
    selectFile: (path: string, blobId?: string) => void;
    toggleFolder: (path: string) => void;
    refresh: () => Promise<void>;
    moveNode: (sourcePath: string, targetPath: string) => Promise<void>;
  }
  
  export function useFileTree(options: UseFileTreeOptions): UseFileTreeReturn {
    // Implementation
  }
  ```

  **Acceptance Criteria**:
  - [ ] Hook功能完整
  - [ ] 有单元测试
  - [ ] FileTree组件简化
  - [ ] 行为与之前一致

  **Commit**: YES
  - Message: `refactor(hooks): extract useFileTree hook from FileTree component`

- [ ] 6. 提取useFileUpload hook

  **What to do**:
  - 从FileTree.tsx提取文件上传逻辑
  - 包括：拖拽处理、冲突检测、批量上传

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Commit**: YES
  - Message: `refactor(hooks): extract useFileUpload hook`

- [ ] 7. 拆分FileTree子组件

  **What to do**:
  - 创建 `frontend/components/FileTree/`
  - 拆分：TreeNode, TreeToolbar, UploadDialog
  - 保持主组件<300行

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Structure**:
  ```
  components/FileTree/
  ├── index.tsx (主入口，<100行)
  ├── TreeNode.tsx (单个节点渲染)
  ├── TreeToolbar.tsx (工具栏按钮)
  ├── UploadDialog.tsx (上传对话框)
  ├── FileTree.tsx (容器组件)
  └── types.ts (共享类型)
  ```

  **Acceptance Criteria**:
  - [ ] 每个文件<200行
  - [ ] 主组件<100行
  - [ ] 所有测试通过
  - [ ] Agent-Executed QA: 运行Scenario 1通过

  **Commit**: YES
  - Message: `refactor(components): split FileTree into smaller sub-components`

- [ ] 8. 重构buildTree函数

  **What to do**:
  - 将buildTree提取到 `frontend/lib/tree-utils.ts`
  - 简化嵌套逻辑
  - 添加单元测试

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Refactored Code**:
  ```typescript
  // lib/tree-utils.ts
  export function buildTree(entries: TreeEntry[]): FileTreeNode[] {
    if (!entries?.length) return [];
    
    const nodeMap = createNodeMap(entries);
    const rootNodes = attachToParents(nodeMap, entries);
    return sortTreeNodes(rootNodes);
  }
  
  function createNodeMap(entries: TreeEntry[]): Map<string, FileTreeNode> {
    // 创建节点映射
  }
  
  function attachToParents(nodeMap: Map<string, FileTreeNode>, entries: TreeEntry[]): FileTreeNode[] {
    // 建立父子关系
  }
  
  function sortTreeNodes(nodes: FileTreeNode[]): FileTreeNode[] {
    // 排序节点
  }
  ```

  **Acceptance Criteria**:
  - [ ] 每个子函数<30行
  - [ ] 有完整单元测试
  - [ ] 性能无下降

  **Commit**: YES
  - Message: `refactor(utils): extract and simplify buildTree function`

- [ ] 9. 重构download_skill函数

  **What to do**:
  - 将 `backend/app/routers/skills.py:download_skill` 拆分
  - 提取：权限检查、ZIP生成、文件名生成

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖权限装饰器）
  - **Parallel Group**: Wave 3

  **Refactored Structure**:
  ```python
  @router.get("/{skill_id}/download")
  @verify_ownership(skill.get)
  async def download_skill(
      resource: Skill = None,  # 由装饰器注入
      platform: Literal["opencode", "claude"] = Query("opencode"),
  ) -> StreamingResponse:
      tree = await fetch_skill_tree(db, resource.tree_id)
      zip_buffer = await create_skill_zip(db, resource, tree)
      filename = generate_filename(resource, platform)
      
      return StreamingResponse(
          zip_buffer,
          media_type="application/zip",
          headers={"Content-Disposition": f"attachment; filename={filename}"},
      )
  
  async def fetch_skill_tree(db, tree_id: UUID) -> Tree:
      # 提取树获取逻辑
      
  async def create_skill_zip(db, skill: Skill, tree: Tree) -> BytesIO:
      # 提取ZIP生成逻辑
      
  def generate_filename(skill: Skill, platform: str) -> str:
      # 提取文件名生成逻辑
  ```

  **Acceptance Criteria**:
  - [ ] 主函数<30行
  - [ ] 子函数职责单一
  - [ ] 所有测试通过
  - [ ] Agent-Executed QA: 运行Scenario 4通过

  **Commit**: YES
  - Message: `refactor(skills): break down download_skill into smaller functions`

- [ ] 10. 重构create_skill函数

  **What to do**:
  - 类似Task 9，重构create_skill
  - 提取：slug验证、blob创建、tree创建

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Commit**: YES
  - Message: `refactor(skills): break down create_skill into smaller functions`

- [ ] 11. 优化异常处理

  **What to do**:
  - 将所有 `except Exception:` 替换为具体异常
  - 创建自定义异常类
  - 统一错误响应

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Custom Exceptions**:
  ```python
  # app/core/exceptions.py
  class AuthenticationError(HTTPException):
      def __init__(self, detail: str = "Authentication failed"):
          super().__init__(status_code=401, detail=detail)
  
  class PermissionDeniedError(HTTPException):
      def __init__(self, detail: str = "Permission denied"):
          super().__init__(status_code=403, detail=detail)
  
  class ResourceNotFoundError(HTTPException):
      def __init__(self, resource: str = "Resource"):
          super().__init__(status_code=404, detail=f"{resource} not found")
  ```

  **Acceptance Criteria**:
  - [ ] 无 `except Exception:`（除顶层）
  - [ ] 所有异常具体化
  - [ ] Agent-Executed QA: 运行Scenario 3通过

  **Commit**: YES
  - Message: `refactor(exceptions): use specific exceptions instead of broad Exception`

- [ ] 12. 消除类型断言

  **What to do**:
  - 搜索所有 `as any` 和 `!`（非空断言）
  - 添加正确的类型定义
  - 使用类型守卫

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 3

  **Before**:
  ```typescript
  if (IMAGE_EXTENSIONS.includes(ext as any)) {
    const node = map.get(normalizedPath)!;
  }
  ```

  **After**:
  ```typescript
  if (IMAGE_EXTENSIONS.includes(ext as ImageExtension)) {
    const node = map.get(normalizedPath);
    if (!node) throw new Error(`Node not found: ${normalizedPath}`);
  }
  ```

  **Acceptance Criteria**:
  - [ ] `grep -r "as any" frontend/ | wc -l` 返回0
  - [ ] 无编译错误
  - [ ] 测试通过

  **Commit**: YES
  - Message: `refactor(types): eliminate type assertions and improve type safety`

- [ ] 13. 回归测试

  **What to do**:
  - 运行所有测试
  - 验证功能无回归
  - 性能对比测试

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（最后执行）
  - **Parallel Group**: Wave 4

  **Acceptance Criteria**:
  - [ ] 所有测试通过
  - [ ] 功能无回归
  - [ ] 性能持平或提升
  - [ ] Agent-Executed QA: 运行所有Scenarios通过

  **Commit**: NO（仅验证）

- [ ] 14. 编写重构文档

  **What to do**:
  - 创建 `docs/refactoring.md`
  - 记录重构决策
  - 编写代码规范指南

  **Recommended Agent Profile**:
  - **Category**: `writing`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 4

  **Content**:
  ```markdown
  # 代码重构指南
  
  ## 重构原则
  1. 功能不变
  2. 测试先行
  3. 小步前进
  
  ## 代码规范
  - 函数长度 < 50行
  - 使用常量替代Magic Numbers
  - 避免类型断言
  - 异常处理具体化
  
  ## 重构清单
  - [ ] 提取重复代码
  - [ ] 拆分大组件
  - [ ] 优化类型定义
  ```

  **Acceptance Criteria**:
  - [ ] 文档完整
  - [ ] 包含示例代码
  - [ ] 团队可遵循

  **Commit**: YES
  - Message: `docs: add refactoring guide and code style documentation`

---

## Commit Strategy

| After Task | Message | Files |
|------------|---------|-------|
| 1 | `refactor(dependencies): add ownership verification decorator` | dependencies/common.py |
| 3 | `refactor(hooks): add reusable hooks` | hooks/*.ts |
| 4 | `refactor(constants): centralize magic numbers` | core/constants.py, lib/constants.ts |
| 5 | `refactor(hooks): extract useFileTree hook` | hooks/useFileTree.ts |
| 7 | `refactor(components): split FileTree into smaller sub-components` | components/FileTree/ |
| 8 | `refactor(utils): extract and simplify buildTree function` | lib/tree-utils.ts |
| 9 | `refactor(skills): break down download_skill` | routers/skills.py |
| 11 | `refactor(exceptions): use specific exceptions` | core/exceptions.py |
| 12 | `refactor(types): eliminate type assertions` | Multiple files |
| 14 | `docs: add refactoring guide` | docs/refactoring.md |

---

## Success Criteria

### Code Quality Metrics
```bash
# 检查函数长度
find backend/app -name "*.py" -exec grep -c "^def " {} + | awk '{sum+=$1} END {print sum}'

# 检查类型断言
grep -r "as any" frontend/ | wc -l  # 目标: 0

# 检查异常处理
grep -r "except Exception:" backend/app/ | grep -v "JWTError" | wc -l  # 目标: 0

# 检查重复代码（需安装jscpd）
npx jscpd frontend/ --threshold 5

# 检查FileTree行数
wc -l frontend/components/FileTree.tsx  # 目标: <300
```

### Verification Checklist
- [ ] 所有函数<50行
- [ ] 无重复代码块
- [ ] FileTree<300行
- [ ] 无类型断言
- [ ] 异常处理具体化
- [ ] 所有测试通过
- [ ] 性能无下降
- [ ] 代码审查通过

---

## Risk Mitigation

### 重构风险
| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 功能回归 | 中 | 高 | 完整测试覆盖，小步提交 |
| 性能下降 | 低 | 中 | 性能测试，Profiler对比 |
| 引入bug | 中 | 中 | 代码审查，Pair Programming |
| 时间超支 | 中 | 低 | 分阶段交付，优先高价值任务 |

### 回滚计划
1. 每个重构任务单独提交
2. 保留重构前分支 `before-refactor`
3. 如有问题，可单独回滚某个提交

---

## Post-Completion

After completing this plan:
1. 更新代码规范文档
2. 配置CI代码质量检查（lint, coverage）
3. 定期进行代码审查
4. 考虑引入自动化重构工具（如更严格的ESLint规则）

**Expected Outcome**: 
- 代码质量评分从7.5提升到8.5+
- 可维护性显著提升
- 开发效率提高（代码更易理解）
- 测试更容易编写

---

**文档已生成完毕。开始执行请运行：**
```
/start-work security-hardening
/start-work testing-improvement
/start-work code-refactoring
```
