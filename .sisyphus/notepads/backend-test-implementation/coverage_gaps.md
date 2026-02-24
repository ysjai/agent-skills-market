# 后端测试覆盖率缺口分析报告

> 生成日期: 2026-02-20  
> 当前总体覆盖率: 78%  
> 目标覆盖率: 95%  
> 缺口: 17% (约 336 行代码未覆盖)

---

## 执行摘要

当前测试覆盖率为 **78%**，距离目标 95% 还有显著差距。本报告识别了所有覆盖率低于 60% 的模块，按业务价值和测试优先级排序，为达到 95% 覆盖率提供了具体的测试补充路线图。

---

## 一、极低覆盖率模块 (<30%) - 紧急优先级 🔴

### 1.1 app/core/auth.py (0% - 30行)

**模块功能**: FastAPI 认证依赖，处理 Bearer Token 验证、用户查找和状态检查

**未覆盖代码行**: 3-63 (全部)

**关键业务路径**:
- 无 Authorization Header 时的认证失败
- Bearer Token 提取和解析
- JWT Token 验证失败处理
- 无效 Token Payload 处理
- 用户不存在处理
- 非活跃用户处理

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 无 Authorization Header | 返回 401, "Not authenticated" |
| P0 | 无效 JWT Token | 返回 401, "Invalid authentication credentials" |
| P0 | Token 中无 sub 字段 | 返回 401, "Invalid token payload" |
| P0 | Token 对应的用户不存在 | 返回 401, "User not found" |
| P0 | 用户 is_active=False | 返回 401, "Inactive user" |
| P1 | 缺少 "Bearer " 前缀的 Token | 应能正常解析 |
| P1 | 有效 Token + 活跃用户 | 返回 User 对象 |

**依赖模块**: 需要 SQLAlchemy User CRUD 操作

---

### 1.2 app/application/handlers/delete_tree_handler.py (0% - 17行)

**模块功能**: 处理 Tree 删除操作

**未覆盖代码行**: 1-17 (全部)

**关键业务路径**:
- 成功删除存在的 Tree
- Tree 不存在时抛出 ResourceNotFoundError

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 删除存在的 Tree | 调用 tree_repo.delete(tree_id) |
| P0 | 删除不存在的 Tree | 抛出 ResourceNotFoundError |

**依赖模块**: TreeRepository

---

### 1.3 app/application/handlers/list_skill_files_handler.py (0% - 27行)

**模块功能**: 列出 Skill 的所有文件

**未覆盖代码行**: 1-27 (全部)

**关键业务路径**:
- Skill 不存在或无权访问
- Skill 无 tree_id (返回空列表)
- Skill 有 tree_id 但 Tree 不存在
- 成功返回 Skill 和文件列表

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | Skill 不存在 | 抛出 ResourceNotFoundError |
| P0 | Skill 属于其他用户 | 抛出 ResourceNotFoundError |
| P1 | Skill 无 tree_id | 返回 (skill, []) |
| P1 | tree_id 对应的 Tree 不存在 | 返回 (skill, []) |
| P1 | 成功获取文件列表 | 返回 (skill, tree.entries) |

**依赖模块**: SkillRepository, TreeRepository

---

## 二、低覆盖率模块 (30-60%) - 高优先级 🟠

### 2.1 app/application/handlers/update_skill_handler.py (28% - 25行)

**模块功能**: 更新 Skill 信息（名称、描述、公开状态、关联 Tree）

**未覆盖代码行**: 19-36 (18行)

**关键业务路径**:
- 各种字段的部分更新
- 名称冲突检测
- 权限验证

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 更新名称时与其他 Skill 冲突 | 抛出 ResourceConflictError |
| P0 | 无权更新他人 Skill | 抛出 ForbiddenError |
| P1 | 仅更新 description | 只更新 description 字段 |
| P1 | 仅更新 is_public | 只更新公开状态 |
| P1 | 仅更新 tree_id | 只关联新 Tree |
| P1 | 名称更新触发的 slug 变更 | 生成新 slug 并保存 |
| P2 | 所有字段同时更新 | 全部更新成功 |
| P2 | 无变更字段 (全为 None) | Skill 保持不变 |

**依赖模块**: SkillRepository, Slug

---

### 2.2 app/application/handlers/delete_skill_handler.py (33% - 21行)

**模块功能**: 删除 Skill 及其关联的 Tree 和 Blob

**未覆盖代码行**: 17-33 (14行)

**关键业务路径**:
- 级联删除 Tree 中的 Blob（引用计数管理）
- 权限验证

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 删除带 Tree 的 Skill | 递减 Blob 引用计数，删除 Tree |
| P0 | 删除无 Tree 的 Skill | 仅删除 Skill |
| P0 | 无权删除他人 Skill | 抛出 ForbiddenError |
| P1 | Blob 引用计数归零后删除 | 调用 blob_repo.delete(blob_id) |
| P1 | Blob 引用计数仍大于0 | 保留 Blob |

**依赖模块**: SkillRepository, TreeRepository, BlobRepository

---

### 2.3 app/application/handlers/add_tree_file_handler.py (38% - 26行)

**模块功能**: 向 Tree 添加文件条目，支持内容自动创建 Blob

**未覆盖代码行**: 23-44 (16行)

**关键业务路径**:
- 使用现有 blob_id 添加文件
- 传入 content 自动创建 Blob（含重复内容检测）
- Blob 引用计数管理

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 使用 blob_id 添加文件 | 添加条目，递增引用计数 |
| P0 | 使用 content 添加文件 | 创建新 Blob，添加条目 |
| P0 | 相同 content 已存在 | 复用现有 Blob，递增引用计数 |
| P1 | Tree 不存在 | 抛出 ResourceNotFoundError |
| P1 | 同时提供 blob_id 和 content | 优先使用 blob_id？或抛错？ |

**依赖模块**: TreeRepository, BlobRepository, BlobFactory

---

### 2.4 app/application/handlers/delete_tree_file_handler.py (40% - 20行)

**模块功能**: 从 Tree 删除文件条目，管理 Blob 引用计数

**未覆盖代码行**: 18-33 (12行)

**关键业务路径**:
- 正常删除文件
- 保护 SKILL.md 不被删除
- 级联删除目录
- Blob 引用计数管理

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 删除普通文件 | 删除条目，递减引用计数 |
| P0 | 尝试删除 SKILL.md | 抛出 ValidationError |
| P0 | 删除目录 | 级联删除，返回所有 blob_ids |
| P1 | Blob 引用计数归零 | 调用 blob_repo.delete |
| P1 | Tree 不存在 | 抛出 ResourceNotFoundError |

**依赖模块**: TreeRepository, BlobRepository

---

### 2.5 app/application/handlers/download_skill_handler.py (48% - 52行)

**模块功能**: 下载 Skill 内容，支持 Claude 格式 (markdown) 和 OpenCode 格式 (zip)

**未覆盖代码行**: 29-55, 65-72, 85-87 (39行)

**关键业务路径**:
- 权限验证
- 无 Tree 时的空内容返回
- Markdown 格式生成
- Zip 格式生成

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 无权下载他人 Skill | 抛出 ForbiddenError |
| P0 | Skill 无 Tree (claude 格式) | 返回空 markdown |
| P0 | Skill 无 Tree (zip 格式) | 返回空 zip |
| P1 | Claude 格式下载 | 返回 markdown 内容 |
| P1 | OpenCode 格式下载 | 返回 zip 内容 |
| P1 | Blob 不存在时跳过 | 继续处理其他文件 |
| P2 | 大文件下载性能 | 流式处理？ |

**依赖模块**: SkillRepository, TreeRepository, BlobRepository

---

### 2.6 app/domain/aggregates/user.py (49% - 47行)

**模块功能**: User 聚合根，管理用户状态和业务规则

**未覆盖代码行**: 23-26, 29-32, 35-38, 41-44, 47-52, 55, 58 (24行)

**关键业务路径**:
- 邮箱验证
- 账户激活/停用
- 密码修改
- 资料更新
- 认证状态检查

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | verify_email | email_verified=True, updated_at 更新 |
| P0 | deactivate | is_active=False, updated_at 更新 |
| P0 | activate | is_active=True, updated_at 更新 |
| P0 | change_password | password_hash 更新, updated_at 更新 |
| P0 | change_password 空值 | 抛出 ValueError |
| P1 | update_profile 更新 username | username 更新 |
| P1 | update_profile 空 username | 抛出 ValueError |
| P1 | update_profile 更新 phone | phone 更新 |
| P1 | is_authenticated | is_active && email_verified |
| P2 | 重复操作不报错 | verify_email 已验证时直接返回 |

**单元测试适用**: ✅ 适合纯单元测试，无外部依赖

---

### 2.7 app/infra/persistence/repositories/sql_blob_repository.py (58% - 45行)

**模块功能**: Blob 仓库 SQLAlchemy 实现

**未覆盖代码行**: 22-23, 33-34, 40, 45-48, 52-57, 61-64 (19行)

**关键业务路径**:
- 按 checksum 查询（含 compressed 筛选）
- 引用计数递增/递减

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | get_by_checksum 找到内容 | 返回 Blob |
| P0 | get_by_checksum 未找到 | 返回 None |
| P1 | get_by_checksum + compressed=True | 添加 compressed 条件 |
| P1 | increment_reference_count | reference_count +1 |
| P1 | decrement_reference_count | reference_count -1, 返回是否<=0 |
| P1 | decrement 时 Blob 不存在 | 返回 False |
| P2 | save 更新现有 Blob | merge 操作 |
| P2 | delete 存在的 Blob | 删除成功 |

**依赖模块**: 需要测试数据库

---

## 三、中等覆盖率模块 (60-80%) - 中等优先级 🟡

### 3.1 app/application/handlers/login_handler.py (50% - 18行)

**模块功能**: 用户登录处理

**未覆盖代码行**: 17-25 (9行)

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 邮箱不存在 | 抛出 UnauthorizedError |
| P0 | 密码错误 | 抛出 UnauthorizedError |
| P0 | 用户被停用 | 抛出 UnauthorizedError |

---

### 3.2 app/application/handlers/register_user_handler.py (53% - 19行)

**模块功能**: 用户注册处理

**未覆盖代码行**: 18-33 (9行)

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P0 | 邮箱已存在 | 抛出 ResourceConflictError |
| P1 | 带 phone 参数注册 | phone 保存成功 |
| P1 | 密码哈希正确生成 | bcrypt 校验通过 |

---

### 3.3 app/application/handlers/refresh_token_handler.py (66% - 29行)

**模块功能**: Token 刷新处理

**未覆盖代码行**: 24, 27-28, 30-36 (10行)

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P1 | 非 refresh token 类型 | 抛出 UnauthorizedError |
| P1 | Token 中无 sub | 抛出 UnauthorizedError |
| P1 | 无效的 user_id 格式 | 抛出 UnauthorizedError |
| P1 | 用户被停用 | 抛出 UnauthorizedError |

---

### 3.4 app/domain/entities/blob.py (61% - 69行)

**模块功能**: Blob 实体，管理二进制内容和压缩

**未覆盖代码行**: 22, 24, 29, 48-50, 53-58, 61-66, 77, 80-81, 84, 87, 89-95 (27行)

**测试场景建议**:

| 优先级 | 测试场景 | 预期行为 |
|-------|---------|---------|
| P1 | __post_init__ 计算 size | size = len(content) |
| P1 | __post_init__ 计算 checksum | checksum 正确计算 |
| P1 | create 空内容 | 抛出 ValueError |
| P1 | validate_content 失败 | 返回 False |
| P1 | compress 已压缩 | 直接返回 |
| P1 | decompress 未压缩 | 直接返回 |
| P1 | get_raw_content 解压缩失败 | 返回原内容 |
| P2 | increment_reference | reference_count +1 |
| P2 | decrement_reference | reference_count -1 (最小0) |
| P2 | is_orphaned | reference_count == 0 |
| P2 | is_empty | 内容为空 |
| P2 | get_content_preview | 返回 UTF-8 解码预览 |
| P2 | get_content_preview 二进制 | 返回 <binary:Nbytes> |

**单元测试适用**: ✅ 适合纯单元测试

---

## 四、测试优先级总览

### 4.1 按业务价值排序

| 排名 | 模块 | 当前覆盖率 | 优先级 | 业务价值 |
|-----|------|-----------|-------|---------|
| 1 | app/core/auth.py | 0% | 🔴 紧急 | 认证核心，安全关键 |
| 2 | app/application/handlers/login_handler.py | 50% | 🔴 紧急 | 登录核心流程 |
| 3 | app/application/handlers/register_user_handler.py | 53% | 🔴 紧急 | 注册核心流程 |
| 4 | app/application/handlers/delete_skill_handler.py | 33% | 🟠 高 | 级联删除，数据一致性 |
| 5 | app/application/handlers/update_skill_handler.py | 28% | 🟠 高 | Skill 更新核心功能 |
| 6 | app/application/handlers/add_tree_file_handler.py | 38% | 🟠 高 | 文件添加核心功能 |
| 7 | app/application/handlers/delete_tree_file_handler.py | 40% | 🟠 高 | 文件删除核心功能 |
| 8 | app/application/handlers/download_skill_handler.py | 48% | 🟠 高 | 下载核心功能 |
| 9 | app/application/handlers/refresh_token_handler.py | 66% | 🟡 中 | Token 刷新 |
| 10 | app/domain/entities/blob.py | 61% | 🟡 中 | 实体方法 |
| 11 | app/domain/aggregates/user.py | 49% | 🟡 中 | 领域逻辑 |
| 12 | app/application/handlers/delete_tree_handler.py | 0% | 🟢 低 | Tree 删除（相对简单）|
| 13 | app/application/handlers/list_skill_files_handler.py | 0% | 🟢 低 | 文件列表（相对简单）|
| 14 | app/infra/persistence/repositories/sql_blob_repository.py | 58% | 🟢 低 | 仓库实现 |

### 4.2 预计补充测试后覆盖率

| 模块 | 当前 | 预计新增测试 | 预计覆盖率 |
|-----|------|-------------|-----------|
| app/core/auth.py | 0% | 6-8 个场景 | 85-95% |
| app/application/handlers/delete_tree_handler.py | 0% | 2 个场景 | 90%+ |
| app/application/handlers/list_skill_files_handler.py | 0% | 4 个场景 | 90%+ |
| app/application/handlers/update_skill_handler.py | 28% | 6-8 个场景 | 85-95% |
| app/application/handlers/delete_skill_handler.py | 33% | 4-5 个场景 | 85-95% |
| app/application/handlers/add_tree_file_handler.py | 38% | 4-5 个场景 | 85-95% |
| app/application/handlers/delete_tree_file_handler.py | 40% | 4-5 个场景 | 85-95% |
| app/application/handlers/download_skill_handler.py | 48% | 5-6 个场景 | 85-95% |
| app/domain/aggregates/user.py | 49% | 8-10 个场景 | 90%+ |
| app/infra/persistence/repositories/sql_blob_repository.py | 58% | 6-8 个场景 | 85-95% |
| app/application/handlers/login_handler.py | 50% | 3 个场景 | 90%+ |
| app/application/handlers/register_user_handler.py | 53% | 3 个场景 | 90%+ |
| app/application/handlers/refresh_token_handler.py | 66% | 4 个场景 | 90%+ |
| app/domain/entities/blob.py | 61% | 8-10 个场景 | 90%+ |

**预计总体覆盖率**: 78% → **92-95%**

---

## 五、测试实施建议

### 5.1 测试类型分布

```
单元测试 (Unit Tests):
  - app/domain/entities/blob.py
  - app/domain/aggregates/user.py
  - app/core/auth.py (部分)

集成测试 (Integration Tests):
  - app/application/handlers/* (大部分)
  - app/infra/persistence/repositories/*
```

### 5.2 测试文件规划

```
backend/tests/
├── unit/
│   ├── domain/
│   │   ├── entities/
│   │   │   └── test_blob.py              # Blob 实体测试
│   │   └── aggregates/
│   │       └── test_user.py              # User 聚合测试
│   └── core/
│       └── test_auth.py                  # 认证依赖测试 (mock)
├── integration/
│   ├── handlers/
│   │   ├── test_auth_handlers.py         # login, register, refresh
│   │   ├── test_skill_handlers.py        # update, delete, list_files
│   │   └── test_tree_handlers.py         # add_file, delete_file, delete_tree
│   │   └── test_download_handler.py      # download_skill
│   └── repositories/
│       └── test_sql_blob_repository.py   # Blob 仓库实现测试
```

### 5.3 依赖 Mock 策略

**Handler 测试依赖**:
```python
# 使用 mock 仓库进行单元测试
@pytest.fixture
def mock_skill_repo():
    return AsyncMock(spec=SkillRepository)

@pytest.fixture
def mock_tree_repo():
    return AsyncMock(spec=TreeRepository)

@pytest.fixture
def mock_blob_repo():
    return AsyncMock(spec=BlobRepository)
```

**数据库集成测试**:
```python
# 使用测试数据库进行集成测试
@pytest.fixture
def blob_repo(test_db_session):
    return SqlBlobRepository(test_db_session)
```

---

## 六、风险与注意事项

### 6.1 高风险区域

1. **级联删除逻辑**: delete_skill_handler 和 delete_tree_file_handler 涉及多个仓库操作，需要确保事务一致性
2. **引用计数管理**: Blob 引用计数递增/递减容易出错，需要仔细验证
3. **认证安全**: auth.py 涉及安全敏感代码，测试需覆盖所有边界情况

### 6.2 已知问题 (来自 learnings.md)

1. **Tree.move_entry bug**: 冲突检测在修改后执行，可能导致数据覆盖
2. **Slug 大写处理**: 实现与期望行为不一致

### 6.3 测试数据准备

需要准备的工厂函数:
- `UserFactory` - 创建测试用户
- `SkillFactory` - 创建测试 Skill
- `TreeFactory` - 创建测试 Tree
- `BlobFactory` - 创建测试 Blob

---

## 七、附录：完整覆盖率数据

### 7.1 极低覆盖率 (<30%)

| 文件 | 语句 | 未覆盖 | 覆盖率 | Missing |
|-----|------|-------|-------|---------|
| delete_tree_handler.py | 9 | 9 | 0% | 1-17 |
| list_skill_files_handler.py | 15 | 15 | 0% | 1-27 |
| app/core/auth.py | 30 | 30 | 0% | 3-63 |
| update_skill_handler.py | 25 | 18 | 28% | 19-36 |

### 7.2 低覆盖率 (30-60%)

| 文件 | 语句 | 未覆盖 | 覆盖率 | Missing |
|-----|------|-------|-------|---------|
| add_tree_file_handler.py | 26 | 16 | 38% | 23-44 |
| delete_skill_handler.py | 21 | 14 | 33% | 17-33 |
| delete_tree_file_handler.py | 20 | 12 | 40% | 18-33 |
| download_skill_handler.py | 52 | 27 | 48% | 29-55, 65-72, 85-87 |
| user.py | 47 | 24 | 49% | 23-26, 29-32, 35-38, 41-44, 47-52, 55, 58 |
| sql_blob_repository.py | 45 | 19 | 58% | 22-23, 33-34, 40, 45-48, 52-57, 61-64 |

### 7.3 中等覆盖率 (60-80%)

| 文件 | 语句 | 未覆盖 | 覆盖率 | Missing |
|-----|------|-------|-------|---------|
| blob.py | 69 | 27 | 61% | 22, 24, 29, 48-50, 53-58, 61-66, 77, 80-81, 84, 87, 89-95 |
| login_handler.py | 18 | 9 | 50% | 17-25 |
| register_user_handler.py | 19 | 9 | 53% | 18-33 |
| refresh_token_handler.py | 29 | 10 | 66% | 24, 27-28, 30-36 |

---

*报告结束*
