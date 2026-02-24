# 测试用例清单 - API 端点测试

> **目标**: 覆盖所有 API 端点的重要场景和边界条件  
> **目标覆盖率**: 95%  
> **格式**: Given-When-Then  
> **状态说明**: ✅ 已实现 | ⬜ 待实现

---

## 📋 文档导航

- [API 清单概览](#api-清单概览)
- [Auth API](#1-auth-api)
- [Skills API](#2-skills-api)
- [Trees API](#3-trees-api)
- [Blobs API](#4-blobs-api)
- [Health API](#5-health-api)

---

## API 清单概览

| 端点路径 | HTTP方法 | 认证 | 现有测试 | 状态 |
|---------|---------|------|---------|------|
| `/api/auth/register` | POST | 否 | test_auth_api.py | ✅ 部分覆盖 |
| `/api/auth/login` | POST | 否 | test_auth_api.py | ✅ 部分覆盖 |
| `/api/auth/refresh` | POST | 否 | test_auth_api.py | ✅ 部分覆盖 |
| `/api/auth/me` | GET | 是 | test_auth_api.py | ✅ 部分覆盖 |
| `/api/auth/logout` | POST | 否 | test_auth_api.py | ✅ 基础覆盖 |
| `/api/skills` | GET | 是 | test_skills_api.py | ✅ 部分覆盖 |
| `/api/skills` | POST | 是 | test_skills_api.py | ✅ 部分覆盖 |
| `/api/skills/import` | POST | 是 | journey tests | ✅ 已覆盖 |
| `/api/skills/{id}` | GET | 是 | test_skills_api.py | ✅ 部分覆盖 |
| `/api/skills/{id}` | PUT | 是 | ❌ 缺失 | ⬜ 待实现 |
| `/api/skills/{id}` | DELETE | 是 | journey tests | ✅ 已覆盖 |
| `/api/skills/{id}/files` | GET | 是 | test_skills_files_api.py | ✅ 部分覆盖 |
| `/api/skills/{id}/download` | GET | 是 | journey tests | ✅ 已覆盖 |
| `/api/trees` | POST | 是 | test_trees_api.py | ✅ 部分覆盖 |
| `/api/trees/{id}` | GET | 是 | test_trees_api.py | ✅ 部分覆盖 |
| `/api/trees/{id}/files` | POST | 是 | test_trees_api.py | ✅ 部分覆盖 |
| `/api/trees/{id}/files` | DELETE | 是 | test_trees_api.py | ✅ 部分覆盖 |
| `/api/trees/{id}/files/rename` | PUT | 是 | test_trees_api.py | ✅ 部分覆盖 |
| `/api/trees/{id}/files/move` | PUT | 是 | test_trees_api.py | ✅ 部分覆盖 |
| `/api/trees/{id}/files/content` | PUT | 是 | ❌ 缺失 | ⬜ 待实现 |
| `/api/trees/{id}/files/batch` | POST | 是 | ❌ 缺失 | ⬜ 待实现 |
| `/api/trees/{id}/files/folder` | POST | 是 | ❌ 缺失 | ⬜ 待实现 |
| `/api/blobs` | POST | 是 | test_blobs_api.py | ✅ 部分覆盖 |
| `/api/blobs/{id}` | GET | 是 | test_blobs_api.py | ✅ 部分覆盖 |
| `/api/blobs/{id}` | PUT | 是 | test_blobs_api.py | ✅ 部分覆盖 |
| `/api/health` | GET | 否 | ❌ 缺失 | ⬜ 待实现 |

---

## 1. Auth API

### 1.1 POST /api/auth/register

#### 基础成功场景
```gherkin
✅ 已实现 - tests/integration/test_auth_api.py::TestRegisterEndpoint

Scenario: 使用有效数据注册用户
  Given 未注册用户 "newuser@example.com"
  When 发送 POST /api/auth/register
    """
    {
      "email": "newuser@example.com",
      "username": "newuser",
      "password": "SecurePass123!"
    }
    """
  Then 应该返回 201 Created
  And 响应应该包含 access_token
  And 响应应该包含 refresh_token
  And 响应应该包含 token_type "bearer"
  And 用户应该能在数据库中查询到
```

#### 边界场景 - 邮箱验证
```gherkin
✅ 已实现 - test_auth_api.py::should_return_422_when_register_given_invalid_email

Scenario: 使用无效邮箱格式注册
  When 发送 POST /api/auth/register
    """
    {
      "email": "not-an-email",
      "username": "testuser",
      "password": "SecurePass123!"
    }
    """
  Then 应该返回 422 Unprocessable Entity
  And 错误消息应该提示邮箱格式无效

⬜ 待实现
Scenario: 使用超长邮箱注册
  When 发送 POST /api/auth/register
    """
    {
      "email": "a@" + "b"*250 + ".com",
      ...
    }
    """
  Then 应该返回 422
  And 错误消息应该提示邮箱过长

⬜ 待实现
Scenario: 使用空邮箱注册
  When 发送 POST /api/auth/register
    """
    {
      "email": "",
      ...
    }
    """
  Then 应该返回 422
  And 错误消息应该提示邮箱不能为空
```

#### 边界场景 - 密码验证
```gherkin
✅ 已实现 - test_auth_api.py::should_return_422_when_register_given_short_password

Scenario: 使用太短密码注册
  When 发送 POST /api/auth/register
    """
    {
      "email": "valid@example.com",
      "username": "testuser",
      "password": "short"
    }
    """
  Then 应该返回 422
  And 错误消息应该提示密码长度不足

⬜ 待实现
Scenario: 使用空密码注册
  When 发送 POST /api/auth/register
    """
    {
      "email": "valid@example.com",
      "username": "testuser",
      "password": ""
    }
    """
  Then 应该返回 422

⬜ 待实现
Scenario: 使用常见弱密码注册
  When 发送 POST /api/auth/register
    """
    {
      "password": "12345678"
    }
    """
  Then 应该返回 422
  And 错误消息应该提示密码强度不足
```

#### 边界场景 - 用户名验证
```gherkin
⬜ 待实现

Scenario: 使用超长用户名注册
  When 发送 POST /api/auth/register
    """
    {
      "username": "a" * 51,
      ...
    }
    """
  Then 应该返回 422
  And 错误消息应该提示用户名过长（最大50字符）

⬜ 待实现
Scenario: 使用空用户名注册
  When 发送 POST /api/auth/register
    """
    {
      "username": "",
      ...
    }
    """
  Then 应该返回 422

⬜ 待实现
Scenario: 使用特殊字符用户名注册
  When 发送 POST /api/auth/register
    """
    {
      "username": "test@user!",
      ...
    }
    """
  Then 应该返回 422
  And 错误消息应该提示用户名格式无效
```

#### 冲突场景
```gherkin
✅ 已实现 - test_auth_api.py::should_return_409_when_register_given_duplicate_email

Scenario: 使用已存在邮箱注册
  Given 用户 "existing@example.com" 已存在
  When 使用相同邮箱注册
  Then 应该返回 409 Conflict
  And 错误消息应该提示邮箱已被注册

⬜ 待实现
Scenario: 并发注册相同邮箱
  When 两个并发请求同时注册相同邮箱
  Then 只有一个应该成功（201）
  And 另一个应该返回 409
```

---

### 1.2 POST /api/auth/login

#### 基础成功场景
```gherkin
✅ 已实现 - tests/integration/test_auth_api.py::TestLoginEndpoint

Scenario: 使用有效凭证登录
  Given 用户 "test@example.com" 已注册，密码 "password123"
  When 发送 POST /api/auth/login
    """
    {
      "email": "test@example.com",
      "password": "password123"
    }
    """
  Then 应该返回 200 OK
  And 响应应该包含 access_token
  And 响应应该包含 refresh_token
  And 响应应该包含 token_type "bearer"
```

#### 失败场景
```gherkin
✅ 已实现 - test_auth_api.py::should_return_401_when_login_given_invalid_password

Scenario: 使用错误密码登录
  Given 用户 "test@example.com" 已注册
  When 使用密码 "wrongpassword" 登录
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示 "Incorrect email or password"
  And 响应中不应该包含 password 或 password_hash 字段

✅ 已实现 - test_auth_api.py::should_return_401_when_login_given_nonexistent_user

Scenario: 使用不存在的邮箱登录
  When 使用 "nonexistent@example.com" 登录
  Then 应该返回 401 Unauthorized
  And 错误消息应该相同（防止邮箱枚举攻击）

⬜ 待实现
Scenario: 使用未激活账户登录
  Given 用户存在但 is_active=false
  When 使用正确密码登录
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示账户未激活
```

#### 边界场景
```gherkin
⬜ 待实现

Scenario: 邮箱大小写不敏感
  Given 用户 "Test@Example.com" 已注册
  When 使用 "test@example.com" 登录
  Then 应该成功（200）
  
  When 使用 "TEST@EXAMPLE.COM" 登录
  Then 应该成功（200）

⬜ 待实现
Scenario: 密码大小写敏感
  Given 用户密码为 "Password123"
  When 使用 "password123" 登录
  Then 应该返回 401（密码大小写敏感）
```

---

### 1.3 POST /api/auth/refresh

#### 基础成功场景
```gherkin
✅ 已实现 - tests/integration/test_auth_api.py::TestRefreshEndpoint

Scenario: 使用有效 refresh_token 刷新
  Given 用户已登录，持有 refresh_token
  When 发送 POST /api/auth/refresh
    Headers: Authorization: Bearer {refresh_token}
  Then 应该返回 200 OK
  And 响应应该包含新的 access_token
  And 响应应该包含新的 refresh_token

⬜ 待实现
Scenario: Refresh Token 只能使用一次
  Given 持有 refresh_token_v1
  When 第一次使用 refresh_token_v1
  Then 应该成功，获得新 token 对
  
  When 再次使用 refresh_token_v1
  Then 应该返回 401 Unauthorized
  And 该用户的所有 token 应该被撤销（检测重放攻击）
```

#### 失败场景
```gherkin
✅ 已实现 - test_auth_api.py::should_return_401_when_refresh_given_no_token

Scenario: 不提供 Token 刷新
  When 发送 POST /api/auth/refresh（无 Header）
  Then 应该返回 401 Unauthorized

✅ 已实现 - test_auth_api.py::should_return_401_when_refresh_given_invalid_token

Scenario: 使用无效 Token 刷新
  When 使用 "Bearer invalid-token" 刷新
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示 "Invalid"

✅ 已实现 - test_auth_api.py::should_return_401_when_refresh_given_access_token

Scenario: 错误地使用 access_token 刷新
  Given 持有 access_token
  When 使用 access_token 作为 refresh token
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示 "Invalid token type"

⬜ 待实现
Scenario: 使用过期 refresh_token
  Given refresh_token 已过期
  When 尝试刷新
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示 token 已过期

⬜ 待实现
Scenario: 使用已注销用户的 Token
  Given 用户 token 有效
  And 用户已被禁用（is_active=false）
  When 尝试刷新 token
  Then 应该返回 401 Unauthorized
```

---

### 1.4 GET /api/auth/me

#### 基础成功场景
```gherkin
✅ 已实现 - tests/integration/test_auth_api.py::TestMeEndpoint

Scenario: 获取当前用户信息
  Given 用户已登录，持有有效 access_token
  When 发送 GET /api/auth/me
    Headers: Authorization: Bearer {access_token}
  Then 应该返回 200 OK
  And 响应应该包含用户 id
  And 响应应该包含 email
  And 响应应该包含 username
  And 响应不应该包含 password_hash
```

#### 失败场景
```gherkin
✅ 已实现 - test_auth_api.py::should_return_401_when_get_me_given_no_token

Scenario: 未认证获取用户信息
  When 发送 GET /api/auth/me（无 Header）
  Then 应该返回 401 Unauthorized

✅ 已实现 - test_auth_api.py::should_return_401_when_get_me_given_invalid_token

Scenario: 使用无效 Token 获取用户信息
  When 使用 "Bearer invalid-token"
  Then 应该返回 401 Unauthorized

✅ 已实现 - test_auth_api.py::should_return_404_when_get_me_given_nonexistent_user

Scenario: Token 有效但用户不存在
  Given access_token 包含不存在的 user_id
  When 获取用户信息
  Then 应该返回 404 Not Found

⬜ 待实现
Scenario: 使用过期 access_token
  Given access_token 已过期
  When 获取用户信息
  Then 应该返回 401 Unauthorized
```

---

### 1.5 POST /api/auth/logout

#### 基础场景
```gherkin
✅ 已实现 - tests/integration/test_auth_api.py::TestLogoutEndpoint

Scenario: 用户登出
  When 发送 POST /api/auth/logout
  Then 应该返回 200 OK
  And 消息应该提示 "Logged out successfully"

Note: 当前实现是无状态的，登出只是返回成功消息。
实际应该将 token 加入黑名单或实现 Token 轮换机制。
```

---

## 2. Skills API

### 2.1 GET /api/skills

#### 基础成功场景
```gherkin
✅ 已实现 - tests/integration/test_skills_api.py

Scenario: 获取用户 Skill 列表
  Given 用户已认证
  And 用户拥有 3 个 Skill
  When 发送 GET /api/skills
  Then 应该返回 200 OK
  And 响应应该包含 items 数组
  And items 长度应该为 3
  And 每个 item 应该包含 id, name, slug, description
  And 应该包含 total 字段
```

#### 分页场景
```gherkin
✅ 已实现

Scenario: 分页获取 Skill 列表
  Given 用户拥有 100 个 Skill
  When 发送 GET /api/skills?skip=0&limit=10
  Then 应该返回前 10 个 Skill
  
  When 发送 GET /api/skills?skip=10&limit=10
  Then 应该返回第 11-20 个 Skill

⬜ 待实现
Scenario: 分页边界值测试
  When 发送 GET /api/skills?skip=-1
  Then 应该返回 400 Bad Request
  
  When 发送 GET /api/skills?limit=0
  Then 应该返回 400 Bad Request
  
  When 发送 GET /api/skills?limit=101
  Then 应该返回 400 Bad Request（超过最大限制 100）
```

#### 认证场景
```gherkin
✅ 已实现

Scenario: 未认证获取 Skill 列表
  When 发送 GET /api/skills（无 Token）
  Then 应该返回 401 Unauthorized
```

---

### 2.2 POST /api/skills

#### 基础成功场景
```gherkin
✅ 已实现 - tests/integration/test_skills_api.py

Scenario: 创建新 Skill
  Given 用户已认证
  When 发送 POST /api/skills
    """
    {
      "name": "My New Skill",
      "slug": "my-new-skill",
      "description": "A description"
    }
    """
  Then 应该返回 201 Created
  And 响应应该包含 id
  And 响应应该包含 tree_id
  And 响应 should contain created_at
```

#### 边界场景 - 名称验证
```gherkin
✅ 已实现

Scenario: 使用空名称创建 Skill
  When 发送 POST /api/skills {"name": ""}
  Then 应该返回 422 Unprocessable Entity

⬜ 待实现
Scenario: 使用超长名称创建 Skill（>200字符）
  When 发送 POST /api/skills {"name": "a" * 201}
  Then 应该返回 422

⬜ 待实现
Scenario: 使用特殊字符名称创建 Skill
  When 发送 POST /api/skills {"name": "Skill<script>"}
  Then 应该返回 422 或正确转义
```

#### 边界场景 - Slug 验证
```gherkin
⬜ 待实现

Scenario: 使用无效 slug 格式创建 Skill
  When 发送 POST /api/skills {"slug": "Invalid_Slug"}
  Then 应该返回 422
  And 错误消息应该提示 slug 只能包含小写字母、数字和连字符

⬜ 待实现
Scenario: 使用超长 slug 创建 Skill
  When 发送 POST /api/skills {"slug": "a" * 129}
  Then 应该返回 422
```

#### 冲突场景
```gherkin
✅ 已实现

Scenario: 创建同名 Skill
  Given 已存在 Skill "existing-skill"
  When 创建同名 Skill
  Then 应该返回 409 Conflict
  And 错误消息应该提示名称冲突
```

---

### 2.3 POST /api/skills/import

#### 基础场景
```gherkin
✅ 已实现 - 通过 journey tests

Scenario: 导入新 Skill
  Given 用户已认证
  When 发送 POST /api/skills/import
    """
    {
      "name": "Imported Skill",
      "slug": "imported-skill",
      "description": "Imported description"
    }
    """
  Then 应该返回 201 Created
  And 应该自动创建关联的 Tree
```

---

### 2.4 GET /api/skills/{id}

#### 基础场景
```gherkin
✅ 已实现 - tests/integration/test_skills_api.py

Scenario: 获取 Skill 详情
  Given 用户已认证
  And Skill {id} 存在且属于该用户
  When 发送 GET /api/skills/{id}
  Then 应该返回 200 OK
  And 响应应该包含完整 Skill 信息
```

#### 权限场景
```gherkin
✅ 已实现

Scenario: 获取其他用户的 Skill
  Given Skill {id} 属于其他用户
  When 发送 GET /api/skills/{id}
  Then 应该返回 403 Forbidden

✅ 已实现

Scenario: 获取不存在的 Skill
  When 发送 GET /api/skills/00000000-0000-0000-0000-000000000000
  Then 应该返回 404 Not Found
```

---

### 2.5 PUT /api/skills/{id}

#### 基础场景
```gherkin
⬜ 待实现 - ❌ 测试文件缺失

Scenario: 更新 Skill 元数据
  Given 用户已认证
  And Skill {id} 存在
  When 发送 PUT /api/skills/{id}
    """
    {
      "name": "Updated Name",
      "description": "Updated description",
      "is_public": true
    }
    """
  Then 应该返回 200 OK
  And Skill 应该被更新
  And version 应该增加

⬜ 待实现
Scenario: 部分更新 Skill
  When 只更新 name 字段
  Then 其他字段应该保持不变

⬜ 待实现
Scenario: 更新其他用户的 Skill
  When 更新属于其他用户的 Skill
  Then 应该返回 403 Forbidden

⬜ 待实现
Scenario: 更新不存在的 Skill
  When 更新不存在的 Skill
  Then 应该返回 404 Not Found

⬜ 待实现
Scenario: 并发更新冲突
  Given 两个客户端同时获取 Skill
  When 客户端 A 先更新
  And 客户端 B 后更新（基于旧版本）
  Then B 应该返回 409 Conflict
```

---

### 2.6 DELETE /api/skills/{id}

#### 基础场景
```gherkin
✅ 已实现 - 通过 journey tests

Scenario: 删除 Skill
  Given 用户已认证
  And Skill {id} 存在
  When 发送 DELETE /api/skills/{id}
  Then 应该返回 204 No Content
  And Skill 应该被删除
  And 关联的 Tree 应该被删除
  And 关联的 Blob 引用应该减少
```

---

### 2.7 GET /api/skills/{id}/files

#### 基础场景
```gherkin
✅ 已实现 - tests/integration/api/test_skills_files_api.py

Scenario: 获取 Skill 文件列表
  Given Skill 存在且有文件
  When 发送 GET /api/skills/{id}/files
  Then 应该返回 200 OK
  And 响应应该包含 files 数组
```

---

### 2.8 GET /api/skills/{id}/download

#### 基础场景
```gherkin
✅ 已实现 - 通过 journey tests

Scenario: 下载 Skill 为 ZIP
  When 发送 GET /api/skills/{id}/download?platform=opencode
  Then 应该返回 200
  And Content-Type 应该是 application/zip

Scenario: 下载 Skill 为 Markdown
  When 发送 GET /api/skills/{id}/download?platform=claude
  Then 应该返回 200
  And Content-Type 应该是 text/markdown
```

---

## 3. Trees API

### 3.1 POST /api/trees

#### 基础场景
```gherkin
✅ 已实现 - tests/integration/api/test_trees_api.py

Scenario: 创建 Tree
  Given 用户已认证
  When 发送 POST /api/trees
    """
    {
      "entries": [
        {"path": "README.md", "type": "blob", "blob_id": "..."}
      ]
    }
    """
  Then 应该返回 201 Created
  And 响应应该包含 tree id
```

---

### 3.2 GET /api/trees/{id}

#### 基础场景
```gherkin
✅ 已实现 - test_trees_api.py

Scenario: 获取 Tree
  Given Tree 存在
  When 发送 GET /api/trees/{id}
  Then 应该返回 200 OK
  And 响应应该包含 entries 数组

✅ 已实现
Scenario: 获取不存在的 Tree
  When 发送 GET /api/trees/{invalid_id}
  Then 应该返回 404 Not Found
```

---

### 3.3 POST /api/trees/{id}/files

#### 基础场景
```gherkin
✅ 已实现 - test_trees_api.py

Scenario: 添加文件到 Tree
  Given Tree 存在
  When 发送 POST /api/trees/{id}/files
    """
    {
      "path": "newfile.txt",
      "type": "blob",
      "content": "file content"
    }
    """
  Then 应该返回 200 OK
  And 文件应该被添加到 Tree
```

#### 边界场景
```gherkin
✅ 已实现
Scenario: 添加重复路径文件
  Given Tree 已存在 "test.txt"
  When 再次添加 "test.txt"
  Then 应该返回 409 Conflict

⬜ 待实现
Scenario: 添加路径遍历攻击路径
  When 添加路径 "../../../etc/passwd"
  Then 应该返回 400 Bad Request
  And 错误消息应该提示路径包含遍历序列

⬜ 待实现
Scenario: 添加超长路径
  When 添加路径长度 > 512 字符
  Then 应该返回 400 Bad Request
```

---

### 3.4 DELETE /api/trees/{id}/files

#### 基础场景
```gherkin
✅ 已实现 - test_trees_api.py

Scenario: 删除 Tree 中的文件
  Given Tree 存在且有文件
  When 发送 DELETE /api/trees/{id}/files
    """
    {"path": "file.txt"}
    """
  Then 应该返回 200 OK
  And 文件应该被删除

⬜ 待实现
Scenario: 尝试删除 SKILL.md
  When 尝试删除 "SKILL.md"
  Then 应该返回 400 Bad Request
  And 错误消息应该提示 "Cannot delete SKILL.md file"
```

---

### 3.5 PUT /api/trees/{id}/files/rename

#### 基础场景
```gherkin
✅ 已实现 - test_trees_api.py

Scenario: 重命名文件
  Given Tree 存在且有 "old.txt"
  When 发送 PUT /api/trees/{id}/files/rename
    """
    {
      "old_path": "old.txt",
      "new_path": "new.txt"
    }
    """
  Then 应该返回 200 OK
  And 文件应该被重命名
```

---

### 3.6 PUT /api/trees/{id}/files/move

#### 基础场景
```gherkin
✅ 已实现 - test_trees_api.py

Scenario: 移动文件
  Given Tree 存在且有 "src/file.txt"
  When 发送 PUT /api/trees/{id}/files/move
    """
    {
      "source": "src/file.txt",
      "target": "dest/file.txt"
    }
    """
  Then 应该返回 200 OK
  And 文件应该被移动
```

---

### 3.7 PUT /api/trees/{id}/files/content

#### 基础场景
```gherkin
⬜ 待实现 - ❌ 测试文件缺失

Scenario: 更新文件内容
  Given Tree 存在且有文件
  When 发送 PUT /api/trees/{id}/files/content
    """
    {
      "path": "file.txt",
      "content": "new content"
    }
    """
  Then 应该返回 200 OK
  And 文件内容应该被更新
  And 应该创建新的 Blob
```

---

### 3.8 POST /api/trees/{id}/files/batch

#### 基础场景
```gherkin
⬜ 待实现 - ❌ 测试文件缺失

Scenario: 批量上传文件
  When 发送 POST /api/trees/{id}/files/batch
    """
    {
      "entries": [
        {"path": "file1.txt", "content": "content1"},
        {"path": "file2.txt", "content": "content2"}
      ]
    }
    """
  Then 应该返回 200 OK
  And 响应应该包含 uploaded 和 failed 计数

⬜ 待实现
Scenario: 批量上传包含失败项
  When 批量上传包含无效文件
  Then 有效文件应该成功
  And 无效文件应该计入 failed
```

---

### 3.9 POST /api/trees/{id}/files/folder

#### 基础场景
```gherkin
⬜ 待实现 - ❌ 测试文件缺失

Scenario: 上传文件夹
  When 发送 POST /api/trees/{id}/files/folder
    """
    {
      "base_path": "templates",
      "entries": [...]
    }
    """
  Then 应该返回 200 OK
  And 所有文件应该创建在 base_path 下
```

---

## 4. Blobs API

### 4.1 POST /api/blobs

#### 基础场景
```gherkin
✅ 已实现 - tests/integration/api/test_blobs_api.py

Scenario: 上传文本文件
  Given 用户已认证
  When 上传文本文件 "test.txt" 内容 "Hello World"
  Then 应该返回 201 Created
  And 响应应该包含 blob id
  And 响应应该包含 content_hash
  And 响应应该包含 size

✅ 已实现
Scenario: 上传二进制文件
  When 上传二进制文件
  Then 应该成功
  And 文件应该无损存储

✅ 已实现
Scenario: 上传空文件
  When 上传空文件（size=0）
  Then 应该成功（201）
  And size 应该为 0
```

#### 压缩场景
```gherkin
✅ 已实现
Scenario: 上传可压缩文件（compress=true）
  When 上传大量重复内容并启用压缩
  Then 应该返回 compressed: true
  And 存储大小应该小于原始大小

✅ 已实现
Scenario: 上传小文件（compress=true）
  When 上传小文件并启用压缩
  Then 应该返回 compressed: false（压缩后反而更大）
```

#### 边界场景 - 文件大小限制
```gherkin
⬜ 待实现（用户明确要求）

Scenario: 上传超过大小限制的文件
  Given 文件大小限制为 10MB（按原始内容计算）
  When 上传 10.1MB 文件
  Then 应该返回 413 Payload Too Large
  And 错误消息应该提示文件大小限制

⬜ 待实现（Metis 建议补充）
Scenario: 压缩后大小不同但原始大小合规
  Given 文件大小限制为 10MB（按原始内容计算）
  When 上传 9MB 高度可压缩内容（如重复字符，压缩后 < 1MB）
  Then 应该成功（201）
  And 按原始大小 9MB 计算，不违反限制

Scenario: 上传刚好达到限制的文件
  When 上传 10MB 文件
  Then 应该成功（201）
  And 响应应该包含正确的 size 和 content_hash

Scenario: 上传前检查大小限制（不浪费带宽）
  When 开始上传 100MB 文件
  Then 应该在请求开始时立即拒绝（不等待上传完成）
  And 返回 413
  And 不应该实际接收文件内容

⬜ 待实现
Scenario: 上传刚好达到限制的文件
  When 上传 10MB 文件
  Then 应该成功（201）
```

#### 去重场景
```gherkin
✅ 已实现
Scenario: 上传重复内容文件
  When 上传相同内容的文件两次
  Then 两次返回的 blob_id 应该相同
  And 引用计数应该增加
```

---

### 4.2 GET /api/blobs/{id}

#### 基础场景
```gherkin
✅ 已实现 - test_blobs_api.py

Scenario: 下载文件
  Given Blob 存在
  When 发送 GET /api/blobs/{id}
  Then 应该返回 200 OK
  And 内容应该与上传时一致

✅ 已实现
Scenario: 下载压缩过的文件
  Given Blob 存储时启用了压缩
  When 下载文件
  Then 应该自动解压
  And 内容应该与原始一致
```

#### 失败场景
```gherkin
✅ 已实现
Scenario: 下载不存在的 Blob
  When 发送 GET /api/blobs/{invalid_id}
  Then 应该返回 404 Not Found

✅ 已实现
Scenario: 使用无效 ID 格式
  When 发送 GET /api/blobs/not-a-uuid
  Then 应该返回 422 Unprocessable Entity
```

---

### 4.3 PUT /api/blobs/{id}

#### 基础场景
```gherkin
✅ 已实现 - test_blobs_api.py

Scenario: 更新 Blob 内容
  Given Blob 存在
  When 发送 PUT /api/blobs/{id} 新内容
  Then 应该返回 200 OK
  And 应该返回新的 blob_id
  And 旧 Blob 的引用应该减少
```

---

## 5. Health API

### 5.1 GET /api/health

#### 基础场景
```gherkin
⬜ 待实现 - ❌ 测试文件缺失

Scenario: 健康检查
  When 发送 GET /api/health
  Then 应该返回 200 OK
  And 响应应该包含 {"status": "ok"}
  And 响应应该包含版本信息

⬜ 待实现
Scenario: 数据库断开时的健康检查
  Given 数据库连接断开
  When 发送 GET /api/health
  Then 应该返回 503 Service Unavailable
  And 响应应该包含错误详情
```

---

## 📊 覆盖统计

### 按端点统计

| API 类别 | 端点总数 | 已测试 | 未测试 | 覆盖率 |
|---------|---------|--------|--------|--------|
| Auth | 5 | 5 | 0 | 100% |
| Skills | 8 | 6 | 2 | 75% |
| Trees | 9 | 6 | 3 | 67% |
| Blobs | 3 | 3 | 0 | 100% |
| Health | 1 | 0 | 1 | 0% |
| **总计** | **26** | **20** | **6** | **77%** |

### 按场景类型统计

| 场景类型 | 总数 | 已实现 | 待实现 | 优先级 |
|---------|------|--------|--------|--------|
| 基础成功场景 | 26 | 20 | 6 | P0 |
| 边界值测试 | 35 | 8 | 27 | P1 |
| 失败/错误场景 | 20 | 12 | 8 | P0 |
| 安全/权限场景 | 15 | 5 | 10 | P0 |
| 并发场景 | 5 | 0 | 5 | P2 |
| **总计** | **101** | **45** | **56** | - |

---

## 🎯 实现优先级建议（Metis 审核后修订）

### P0 - 立即实现（本周）

1. **文件大小限制测试**（用户明确要求 ✅）
   - POST /api/blobs 10MB 限制测试（原始大小计算）
   - 压缩后大小合规场景

2. **缺失端点基础测试**
   - PUT /api/skills/{id}
   - PUT /api/trees/{id}/files/content
   - POST /api/trees/{id}/files/batch
   - POST /api/trees/{id}/files/folder
   - GET /api/health

3. **关键边界测试**
   - 路径遍历攻击防护
   - SKILL.md 保护机制（调整为 P1，详见下方说明）
   - Slug 格式验证

4. **Token 刷新轮换机制**（安全基础设施，提升为 P0）
   - Refresh Token 一次性使用测试
   - 并发刷新竞态测试

### P1 - 短期实现（2周内）

4. **完善边界测试**
   - 所有字段的长度限制测试
   - 特殊字符处理测试
   - 分页边界测试

5. **安全增强测试**
   - 速率限制测试
   - Token 篡改检测
   - SQL 注入防护

### P2 - 中期实现（1月内）

6. **并发场景测试**
7. **性能基准测试**
8. **断电/降级测试**

---

**文档版本**: 1.0  
**生成时间**: 2026-02-20  
**目标覆盖率**: 95%（当前 API 覆盖率约 77%，需补充 56 个测试场景）
