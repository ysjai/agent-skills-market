# 安全加固工作计划

## TL;DR

> **目标**: 修复7个安全风险，提升安全评分从7.0到8.5+
> 
> **交付物**: 6个安全修复PR，1份安全审计文档
> 
> **预计工时**: 8-12小时（1-2天）
> **并行度**: 高 - 5个任务可同时进行
> **关键路径**: 依赖扫描 → 关键修复 → 安全验证

---

## Context

### 当前安全状况
- JWT认证实现规范，但存在细节问题
- 输入验证不完整
- 依赖安全未定期扫描
- 异常处理过于宽泛可能泄露信息

### 风险评估
| 风险等级 | 数量 | 影响 |
|----------|------|------|
| 🔴 高危 | 3个 | 可能导致未授权访问或数据泄露 |
| 🟡 中危 | 2个 | 可能暴露系统信息 |
| 🟢 低危 | 2个 | 最佳实践改进 |

---

## Work Objectives

### Core Objective
系统性修复Agent Skills Manager的安全漏洞，建立安全基线，确保生产环境安全合规。

### Concrete Deliverables
1. 修复dependencies/auth.py异常捕获问题
2. 添加slug输入验证和路径遍历防护
3. 移除localStorage残留代码
4. 建立依赖安全扫描流程
5. 完善错误处理和日志脱敏
6. 添加CSRF双重验证

### Definition of Done
- [ ] 所有🔴高危问题修复完成
- [ ] 安全扫描无高危漏洞
- [ ] 渗透测试通过（基础测试）
- [ ] 安全文档更新

### Must Have
- JWT异常处理具体化
- 输入验证完整（slug、文件路径）
- 敏感信息不在日志中泄露

### Must NOT Have
- 不引入新的安全工具（保持简洁）
- 不改变现有认证流程（用户无感知）

---

## Verification Strategy

### Agent-Executed QA Scenarios

#### Scenario 1: JWT异常处理验证
```
Tool: Bash (curl)
Preconditions: 后端服务运行在localhost:8000
Steps:
  1. 发送请求：curl -X GET http://localhost:8000/api/v1/auth/me \
       -H "Cookie: access_token=invalid.token.here"
  2. 验证响应状态码为401
  3. 验证响应体不包含"Traceback"或堆栈信息
  4. 验证响应体为：{"detail": "Invalid authentication credentials"}
Expected Result: 仅返回通用错误信息，不泄露内部实现
Evidence: 截图或curl输出保存到 .sisyphus/evidence/security-1-jwt-error.log
```

#### Scenario 2: Slug注入攻击防护
```
Tool: Bash (curl)
Preconditions: 用户已登录，有有效的access_token
Steps:
  1. 尝试创建skill：curl -X POST http://localhost:8000/api/v1/skills \
       -H "Content-Type: application/json" \
       -H "Cookie: access_token=$TOKEN" \
       -d '{"name": "test../../../etc/passwd", "description": "test"}'
  2. 验证返回400错误
  3. 验证错误信息为："Invalid slug format"
  4. 验证数据库中未创建该skill
Expected Result: 特殊字符被拦截，系统安全
Evidence: curl输出和数据库查询结果
```

#### Scenario 3: 路径遍历攻击防护
```
Tool: Bash (curl)
Preconditions: 存在tree_id为test-tree的skill
Steps:
  1. 尝试访问：curl -X GET "http://localhost:8000/api/v1/trees/test-tree/../../../etc/passwd" \
       -H "Cookie: access_token=$TOKEN"
  2. 验证返回404，不泄露系统文件
  3. 检查后端日志无异常堆栈
Expected Result: 路径遍历被阻止
Evidence: 响应截图
```

#### Scenario 4: 依赖安全扫描
```
Tool: Bash
Preconditions: 在backend目录
Steps:
  1. 运行：pip install safety && safety check
  2. 验证输出无Critical或High级别漏洞
  3. 运行：cd ../frontend && npm audit --audit-level=high
  4. 验证无High级别漏洞
Expected Result: 依赖扫描无高危漏洞
Evidence: safety和npm audit输出保存
```

---

## Execution Strategy

### Wave 1: 关键安全修复（2-3小时）
并行执行：
```
├── Task 1: JWT异常处理修复 [20分钟]
├── Task 2: Slug输入验证 [30分钟]
├── Task 3: 路径规范化 [40分钟]
└── Task 4: 移除localStorage代码 [30分钟]
```

### Wave 2: 依赖与日志安全（2-3小时）
```
├── Task 5: 依赖安全扫描流程 [60分钟]
└── Task 6: 日志脱敏处理 [90分钟]
```

### Wave 3: 增强防护（可选，2-4小时）
```
└── Task 7: CSRF双重验证 [120分钟]
```

---

## TODOs

- [ ] 1. 修复JWT异常捕获过于宽泛

  **What to do**:
  - 修改 `backend/app/dependencies/auth.py` 第33-38行
  - 将 `except Exception:` 改为 `except JWTError:`
  - 添加日志记录（不包含敏感信息）

  **Must NOT do**:
  - 不要暴露内部异常详情给客户端
  - 不要将token内容记录到日志

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: `git-master`

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1
  - **Blocked By**: None

  **References**:
  - Current: `backend/app/dependencies/auth.py:33-38`
  - Pattern: FastAPI error handling best practices

  **Acceptance Criteria**:
  - [ ] 代码修改：except JWTError as e:
  - [ ] 测试：发送无效token返回401，无堆栈信息
  - [ ] Agent-Executed QA: 运行Scenario 1通过

  **Commit**: YES
  - Message: `fix(auth): restrict exception handling to JWTError only`
  - Files: `backend/app/dependencies/auth.py`

- [ ] 2. 添加Skill slug输入验证

  **What to do**:
  - 在 `backend/app/routers/skills.py` 添加slug格式验证
  - 只允许小写字母、数字、连字符
  - 验证slug不以连字符开头或结尾

  **Must NOT do**:
  - 不要改变现有API响应格式
  - 不要破坏已有skill的slug

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **References**:
  - Current: `backend/app/routers/skills.py:88-89`
  - Pattern: Pydantic validator pattern

  **Code Change**:
  ```python
  import re
  
  SLUG_PATTERN = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
  
  # 在create_skill函数中
  auto_slug = skill_in.name.lower()
  if not SLUG_PATTERN.match(auto_slug):
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="Skill name must contain only letters, numbers, and hyphens"
      )
  ```

  **Acceptance Criteria**:
  - [ ] 代码添加slug验证逻辑
  - [ ] 测试：有效slug通过
  - [ ] 测试：无效slug（如"test../../../"）返回400
  - [ ] Agent-Executed QA: 运行Scenario 2通过

  **Commit**: YES
  - Message: `feat(skills): add slug format validation to prevent path traversal`
  - Files: `backend/app/routers/skills.py`

- [ ] 3. 添加文件路径规范化防护

  **What to do**:
  - 在trees router中添加路径规范化验证
  - 拒绝包含 `..` 或 `~` 的路径
  - 统一使用正斜杠

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **References**:
  - Current: `backend/app/routers/trees.py`
  - Pattern: Path traversal prevention

  **Acceptance Criteria**:
  - [ ] 路径验证中间件或函数
  - [ ] 测试：包含".."的路径被拒绝
  - [ ] Agent-Executed QA: 运行Scenario 3通过

  **Commit**: YES
  - Message: `fix(trees): prevent path traversal in file operations`

- [ ] 4. 移除localStorage残留代码

  **What to do**:
  - 检查 `frontend/app/lib/auth.ts`
  - 检查所有localStorage.removeItem调用
  - 如果确认不再需要，删除相关代码
  - 如果作为降级方案保留，添加注释说明

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1

  **References**:
  - Current: `frontend/app/lib/auth.ts`, `frontend/app/login/page.tsx`

  **Acceptance Criteria**:
  - [ ] 无冗余的localStorage token操作
  - [ ] 登录/登出流程正常
  - [ ] 浏览器开发者工具Application面板无残留token

  **Commit**: YES
  - Message: `refactor(auth): remove legacy localStorage token handling`

- [ ] 5. 建立依赖安全扫描流程

  **What to do**:
  - 添加safety到development依赖
  - 创建scripts/security-check.sh脚本
  - 更新README.md添加安全扫描说明
  - （可选）配置GitHub Action自动扫描

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2
  - **Blocked By**: None

  **Script Content**:
  ```bash
  #!/bin/bash
  set -e
  
  echo "🔍 Python dependency security scan..."
  cd backend
  safety check || true
  
  echo "🔍 Node.js dependency security scan..."
  cd ../frontend
  npm audit --audit-level=high || true
  
  echo "✅ Security scan complete"
  ```

  **Acceptance Criteria**:
  - [ ] safety可运行：`pip install safety && safety check`
  - [ ] npm audit可运行
  - [ ] 脚本文件存在且可执行
  - [ ] Agent-Executed QA: 运行Scenario 4通过

  **Commit**: YES
  - Message: `chore(security): add dependency security scanning`

- [ ] 6. 日志脱敏处理

  **What to do**:
  - 配置FastAPI日志不输出敏感信息
  - 在auth相关操作脱敏email（如 t***@example.com）
  - 确保不记录密码、token等

  **Recommended Agent Profile**:
  - **Category**: `unspecified-low`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 2

  **Acceptance Criteria**:
  - [ ] 日志配置更新
  - [ ] 无敏感信息泄露测试
  - [ ] 登录失败只记录用户ID，不记录密码

  **Commit**: YES
  - Message: `feat(logging): redact sensitive information from logs`

- [ ] 7. 添加CSRF双重验证（可选增强）

  **What to do**:
  - 添加CSRF token机制
  - 在关键操作（删除、修改）验证CSRF token
  - 或者使用SameSite=Lax/Strict Cookie（已配置✅）

  **Note**: 当前SameSite=Strict配置已提供基础CSRF防护，此项为可选增强

  **Recommended Agent Profile**:
  - **Category**: `unspecified-high`
  - **Skills**: None

  **Parallelization**:
  - **Can Run In Parallel**: NO（依赖前面任务）

  **Acceptance Criteria**:
  - [ ] CSRF token生成和验证
  - [ ] 非简单请求验证CSRF
  - [ ] 测试：无CSRF token请求被拒绝

  **Commit**: YES
  - Message: `feat(security): add CSRF token validation for state-changing operations`

---

## Commit Strategy

| After Task | Message | Files |
|------------|---------|-------|
| 1 | `fix(auth): restrict exception handling to JWTError only` | dependencies/auth.py |
| 2 | `feat(skills): add slug format validation` | routers/skills.py |
| 3 | `fix(trees): prevent path traversal` | routers/trees.py |
| 4 | `refactor(auth): remove legacy localStorage handling` | app/lib/auth.ts |
| 5 | `chore(security): add dependency security scanning` | scripts/security-check.sh, README.md |
| 6 | `feat(logging): redact sensitive information` | core/logging.py |
| 7 | `feat(security): add CSRF token validation` | routers/*, middleware/ |

---

## Success Criteria

### Verification Commands
```bash
# 测试JWT错误处理
curl -s http://localhost:8000/api/v1/auth/me -H "Cookie: access_token=invalid" | grep -v Traceback

# 测试slug验证
curl -s -X POST http://localhost:8000/api/v1/skills \
  -H "Cookie: access_token=$TOKEN" \
  -d '{"name": "test../", "description": "x"}' | grep "Invalid slug"

# 运行安全扫描
cd backend && safety check --json | jq '.vulnerabilities | length' # 应为0

# 检查日志无敏感信息
grep -r "password" backend/logs/ # 应无结果
```

### Final Checklist
- [ ] All 🔴 high-risk issues resolved
- [ ] Security scan shows no high/critical vulnerabilities
- [ ] All QA scenarios pass
- [ ] No sensitive data in logs
- [ ] Code review approved

---

## Post-Completion

After completing this plan:
1. Update security documentation
2. Schedule quarterly security reviews
3. Consider penetration testing for production

**Expected Outcome**: Security score increases from 7.0 to 8.5+
