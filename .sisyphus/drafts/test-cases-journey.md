# 测试用例清单 - Journey 测试

> **目标**: 覆盖所有关键用户旅程，确保业务流程端到端正确性  
> **目标覆盖率**: 95%  
> **格式**: Given-When-Then  
> **状态说明**: ✅ 已实现 | ⬜ 待实现

---

## 📋 文档导航

- [P0 - 核心业务流程 (必须实现)](#p0---核心业务流程)
- [P1 - 安全和权限 (高优先级)](#p1---安全和权限)
- [P2 - 边缘场景和异常 (中优先级)](#p2---边缘场景和异常)
- [P3 - 性能和压力测试 (低优先级)](#p3---性能和压力测试)

---

## P0 - 核心业务流程

### 1. 用户认证旅程

#### 1.1 完整注册-登录-登出流程
```gherkin
✅ 已实现 - tests/integration/journey/auth/test_auth_flow.py

Scenario: 用户完成完整的认证生命周期
  Given 用户未登录
  When 用户使用有效邮箱 "test@example.com" 和密码 "SecurePass123!" 注册
  Then 应该返回 201 状态码
  And 应该返回 access_token 和 refresh_token
  And 用户应该能使用 access_token 获取个人信息
  
  When 用户使用相同的凭证登录
  Then 应该返回 200 状态码
  And 应该返回新的 token 对
  
  When 用户使用 refresh_token 刷新 access_token
  Then 应该返回 200 状态码
  And 新的 access_token 应该有效
  
  When 用户登出
  Then 应该返回 200 状态码
```

#### 1.2 Token 过期自动刷新
```gherkin
⬜ 待实现

Scenario: Access token 过期后自动刷新
  Given 用户已登录并持有 access_token 和 refresh_token
  And access_token 已过期（等待或修改过期时间）
  When 用户使用过期的 access_token 访问受保护资源
  Then 应该返回 401 状态码
  
  When 用户使用 refresh_token 获取新的 token 对
  Then 应该返回 200 状态码
  And 新的 access_token 应该能成功访问资源
```

#### 1.3 多设备登录会话管理
```gherkin
⬜ 待实现

Scenario: 同一用户在多个设备登录
  Given 用户在设备 A 登录，获得 token_A
  And 用户在设备 B 登录，获得 token_B
  When 用户同时使用 token_A 和 token_B 访问资源
  Then 两个 token 都应该有效
  
  When 用户从设备 A 登出
  And 设备 B 使用 token_B 访问资源
  Then 应该仍然有效（后端无状态登出）
```

---

### 2. Skill 管理旅程

#### 2.1 创建 Skill 完整流程
```gherkin
✅ 已实现 - tests/integration/journey/skill/test_crud.py

Scenario: 用户成功创建一个新的 Skill
  Given 用户已认证
  When 用户发送 POST /api/skills 请求
    """
    {
      "name": "My Test Skill",
      "slug": "my-test-skill",
      "description": "A test skill description"
    }
    """
  Then 应该返回 201 状态码
  And 响应应该包含 skill id
  And 响应应该包含 tree_id
  And skill 应该出现在 GET /api/skills 列表中
```

#### 2.2 Skill 导入基础流程
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_01_import_and_verify.py

Scenario: 导入 Skill 并验证文件完整可用
  Given 用户已认证
  When 用户导入 Skill "fully-accessible-skill"
    And 创建目录结构 ["src/", "docs/"]
    And 上传文件到 blob:
      | 文件名      | 内容                          |
      | SKILL.md   | # My Skill Description       |
      | config.json| {"version": "1.0.0"}         |
      | src/main.py| def main(): print('hello')   |
    And 将文件添加到 tree
  Then Skill 应该出现在列表中
  And 能查看 Skill 详情
  And 能查看完整目录树
  And 能下载每个文件并验证内容
```

#### 2.3 共享文件处理
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_02_shared_files.py

Scenario: 两个 Skill 共享同一个 blob 文件
  Given 用户已认证
  When 创建 Skill A 并上传文件 "shared.txt"
  And 创建 Skill B 引用同一个 blob_id
  Then 两个 Skill 都应该能访问文件
  And 文件的引用计数应该为 2
  
  When 删除 Skill A
  Then Skill B 应该仍然能访问文件
  And 文件的引用计数应该为 1
```

#### 2.4 重复名称冲突处理
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_03_duplicate_name.py

Scenario: 导入同名 Skill 应该失败
  Given 用户已认证
  And 已存在 Skill "duplicate-skill"
  When 尝试导入同名 Skill
  Then 应该返回 409 状态码
  And 错误消息应该提示名称冲突
```

#### 2.5 删除 Skill 后文件不可访问
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_04_delete_skill.py

Scenario: 删除 Skill 后其文件应该不可访问
  Given 用户已认证
  And 已创建 Skill 并上传文件
  When 删除 Skill
  Then GET /api/skills/{id} 应该返回 404
  And 该 Skill 的所有 blob 引用应该被清理
  And 孤儿 blob 应该被标记为可删除
```

#### 2.6 复杂目录结构处理
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_05_complex_structure.py

Scenario: 处理深层嵌套目录结构
  Given 用户已认证
  When 创建深度目录结构:
    """
    src/
    src/components/
    src/components/Button.tsx
    src/utils/
    src/utils/helpers.ts
    tests/
    tests/unit/
    tests/integration/
    docs/api/
    docs/guide/
    """
  Then 所有目录和文件应该正确创建
  And 能获取完整目录树
  And 能下载验证每个文件
```

#### 2.7 混合文件类型处理
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_06_mixed_file_types.py

Scenario: 处理多种文件类型
  Given 用户已认证
  When 上传不同类型文件:
    | 文件名                    | 类型          |
    | README.md                | 文本          |
    | script.py                | Python       |
    | style.css                | CSS          |
    | config.yaml              | YAML         |
    | data.json                | JSON         |
    | image.png (binary)       | 二进制        |
    | archive.zip (binary)     | 二进制        |
  Then 所有文件应该成功上传
  And 文本文件内容应该正确保存
  And 二进制文件应该无损存储
```

#### 2.8 增量文件添加
```gherkin
✅ 已实现 - tests/integration/journey/skill_import/scenarios/test_scenario_07_incremental_add.py

Scenario: 向已有 Skill 增量添加文件
  Given 用户已认证
  And 已创建 Skill 并添加初始文件
  When 后续添加更多文件到 tree
  Then 新文件应该正确添加
  And 原有文件应该保持不变
  And Skill 版本应该更新
```

#### 2.9 Skill 版本控制和回滚
```gherkin
⬜ 待实现

Scenario: Skill 版本历史管理
  Given 用户已认证
  And 已创建 Skill 版本 1
  When 更新 Skill 元数据
  Then 版本号应该自动增加到 2
  
  When 再次更新文件内容
  Then 版本号应该增加到 3
  
  When 查看版本历史
  Then 应该看到所有版本记录
  
  When 回滚到版本 1
  Then Skill 状态和文件应该恢复到版本 1
  And 版本号应该增加到 4（新版本）
```

---

### 3. 文件树操作旅程

#### 3.1 完整文件操作生命周期
```gherkin
✅ 已实现 - tests/integration/journey/file_tree/test_file_operations.py

Scenario: 文件 CRUD 完整流程
  Given 用户已认证
  And 已创建 Skill 获得 tree_id
  
  When 创建文件夹 "src"
  Then 文件夹应该出现在 tree 中
  
  When 创建文件 "test.txt" 内容 "hello"
  Then 文件应该出现在 tree 中
  
  When 重命名文件 "test.txt" 为 "hello.txt"
  Then "hello.txt" 应该存在
  And "test.txt" 不应该存在
  
  When 移动 "hello.txt" 到 "src/hello.txt"
  Then "src/hello.txt" 应该存在
  And "hello.txt" 不应该存在
  
  When 删除 "src/hello.txt"
  Then 文件不应该再出现在 tree 中
```

#### 3.2 批量文件上传
```gherkin
⬜ 待实现

Scenario: 批量上传多个文件
  Given 用户已认证
  And 已创建 Skill 获得 tree_id
  When 批量上传 100 个文件
    """
    POST /api/trees/{tree_id}/files/batch
    {
      "entries": [
        {"path": "file1.txt", "content": "content1"},
        {"path": "file2.txt", "content": "content2"},
        ... 100 files
      ]
    }
    """
  Then 应该返回上传统计
    """
    {"uploaded": 100, "failed": 0}
    """
  And 所有文件应该正确创建
  
  When 批量上传包含部分无效文件
  Then 有效文件应该成功
  And 无效文件应该计入 failed
  And 应该返回失败详情
```

#### 3.3 文件夹上传
```gherkin
⬜ 待实现

Scenario: 上传整个文件夹结构
  Given 用户已认证
  And 已创建 Skill 获得 tree_id
  When 上传文件夹:
    """
    POST /api/trees/{tree_id}/files/folder
    {
      "base_path": "templates",
      "entries": [
        {"path": "page.html", "content": "..."},
        {"path": "component.html", "content": "..."}
      ]
    }
    """
  Then 所有文件应该创建在 "templates/" 下
  And 目录结构应该保持
```

#### 3.4 复杂文件移动和重命名
```gherkin
⬜ 待实现

Scenario: 移动包含子目录的文件夹
  Given 用户已认证
  And tree 包含结构:
    """
    src/
    src/components/
    src/components/Button.tsx
    src/components/Modal.tsx
    src/utils/
    src/utils/helpers.ts
    """
  When 移动 "src/" 到 "lib/"
  Then 新结构应该为:
    """
    lib/
    lib/components/
    lib/components/Button.tsx
    lib/components/Modal.tsx
    lib/utils/
    lib/utils/helpers.ts
    """
  And 原 "src/" 不应该存在
```

#### 3.5 SKILL.md 保护机制
```gherkin
⬜ 待实现

Scenario: 不能删除 SKILL.md 文件
  Given 用户已认证
  And tree 包含 "SKILL.md"
  When 尝试删除 "SKILL.md"
  Then 应该返回 400 状态码
  And 错误消息应该提示 "Cannot delete SKILL.md file"
  And 文件应该仍然存在
```

---

### 4. Blob 操作旅程

#### 4.1 多文件下载流程
```gherkin
✅ 已实现 - tests/integration/journey/blob/test_download.py

Scenario: 下载 Skill 的所有文件
  Given 用户已认证
  And 已创建 Skill 包含多个文件
  When 逐个下载每个文件
  Then 所有文件内容应该正确
  
  When 下载 Skill ZIP 包（platform=opencode）
  Then 应该返回 application/zip
  And ZIP 应该包含所有文件
  
  When 下载 Skill Markdown（platform=claude）
  Then 应该返回 Markdown 格式
```

#### 4.2 Blob 引用计数和清理
```gherkin
✅ 已实现 - tests/integration/journey/blob/test_shared_blob_deletion.py

Scenario: 共享 blob 的引用计数管理
  Given 用户已认证
  And blob "shared.txt" 被多个 skill 引用
  When 删除其中一个引用
  Then blob 应该仍然存在
  And 引用计数应该减少
  
  When 删除最后一个引用
  Then blob 应该被标记为孤儿
  And 后续应该被清理
```

---

## P1 - 安全和权限

### 5. 多用户数据隔离

#### 5.1 用户数据完全隔离
```gherkin
✅ 已实现 - tests/integration/journey/multi_user/test_data_isolation.py

Scenario: 用户只能访问自己的数据
  Given 用户 A 已创建 Skill A
  And 用户 B 已创建 Skill B
  When 用户 A 获取 /api/skills
  Then 应该只看到 Skill A
  And 不应该看到 Skill B
  
  When 用户 A 尝试访问 /api/skills/{skill_b_id}
  Then 应该返回 403 Forbidden
  
  When 用户 A 尝试修改 Skill B
  Then 应该返回 403 Forbidden
  
  When 用户 A 尝试删除 Skill B
  Then 应该返回 403 Forbidden
```

#### 5.2 Token 泄露后的安全防护
```gherkin
⬜ 待实现

Scenario: Token 泄露后用户主动撤销会话
  Given 用户 A 已登录，持有 access_token_X
  And access_token_X 被泄露给用户 B
  
  When 用户 B 使用 access_token_X 访问 /api/skills
  Then 应该成功返回用户 A 的技能列表（Token 技术上仍有效）
  
  When 用户 A 检测到泄露并在设置中撤销所有会话
  Then 后端应该将 access_token_X 加入黑名单
  
  When 用户 B 再次使用 access_token_X 访问
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示 "Token has been revoked"

Scenario: 密码修改后 Token 失效策略
  Given 用户 A 已登录，持有 access_token_Y
  When 用户 A 修改密码
  Then 系统可以选择以下策略之一（需在文档中明确）：
    策略1（推荐）: 所有现有 Token 立即失效，用户需要重新登录
    策略2: 现有 Token 在短过渡期（如5分钟）后失效
    策略3: 现有 Token 保持有效直到自然过期（不推荐，安全性低）
  
  When 策略1实施后
  And 用户使用旧 access_token_Y 访问
  Then 应该返回 401 Unauthorized
```

#### 5.3 跨用户 Tree 访问控制
```gherkin
⬜ 待实现

Scenario: 用户不能访问其他用户的 Tree
  Given 用户 A 拥有 Tree A
  And 用户 B 知道 Tree A 的 ID
  When 用户 B 访问 /api/trees/{tree_a_id}
  Then 应该返回 403 Forbidden
  
  When 用户 B 尝试修改 Tree A 的文件
  Then 应该返回 403 Forbidden
```

---

### 6. 认证安全旅程

#### 6.1 暴力破解防护
```gherkin
⬜ 待实现

Scenario: 登录速率限制
  Given 用户未登录
  When 连续 5 次使用错误密码登录
  Then 前 4 次返回 401
  And 第 5 次应该触发速率限制
  And 应该返回 429 Too Many Requests
  And 应该暂时锁定该 IP/账户
  
  When 等待锁定期结束后
  And 使用正确密码登录
  Then 应该成功登录
```

#### 6.2 Token 篡改检测
```gherkin
⬜ 待实现

Scenario: 检测篡改的 Token
  Given 攻击者截获了一个有效 Token
  When 修改 Token payload 中的 user_id
  And 使用篡改后的 Token 访问
  Then 应该返回 401 Unauthorized
  And 错误消息应该提示 "Invalid token"
```

#### 6.3 Refresh Token 轮换
```gherkin
⬜ 待实现

Scenario: Refresh Token 一次性使用
  Given 用户持有 refresh_token_v1
  When 使用 refresh_token_v1 刷新
  Then 应该返回新的 token 对
  And refresh_token_v1 应该失效
  
  When 再次使用 refresh_token_v1
  Then 应该返回 401
  And 该用户的所有 Token 应该被撤销（检测重放攻击）
```

---

## P2 - 边缘场景和异常

### 7. 文件上传限制

#### 7.1 单个文件大小限制
```gherkin
⬜ 待实现

Scenario: 上传超过大小限制的文件
  Given 文件大小限制配置为 10MB
  When 上传 5MB 文件
  Then 应该成功上传
  
  When 上传 10MB 文件
  Then 应该成功上传（刚好达到限制）
  
  When 上传 10.1MB 文件
  Then 应该返回 413 Payload Too Large
  And 错误消息应该提示文件大小限制
  
  When 上传 100MB 文件
  Then 应该立即拒绝（不等待上传完成）
  And 返回 413
```

#### 7.2 总存储空间限制
```gherkin
⬜ 待实现

Scenario: 用户总存储空间限制
  Given 用户存储限制为 100MB
  And 用户已使用 95MB
  When 上传 3MB 文件
  Then 应该成功（总使用 98MB）
  
  When 再上传 5MB 文件
  Then 应该返回 507 Insufficient Storage
  And 错误消息应该提示存储空间不足
```

#### 7.3 特殊文件名处理
```gherkin
⬜ 待实现

Scenario: 处理特殊字符文件名
  Given 用户已认证
  When 上传文件名包含特殊字符:
    | 文件名                  |
    | file with spaces.txt   |
    | 中文文件名.md          |
    | emoji🎉.txt            |
    | name%20encoded.txt     |
    | path/../traversal.txt  |
  Then 合法特殊字符应该正确处理
  And 路径遍历攻击应该被阻止（返回 400）
```

---

### 8. 并发和竞态条件

#### 8.1 并发修改同一 Skill
```gherkin
⬜ 待实现

Scenario: 两个客户端同时修改同一 Skill
  Given 用户已认证
  And 客户端 A 和 B 同时获取 Skill 版本 1
  When 客户端 A 更新 Skill 元数据（基于版本 1）
  Then 应该成功，Skill 变为版本 2
  
  When 客户端 B 尝试更新 Skill（基于版本 1）
  Then 应该返回 409 Conflict
  And 错误消息应该提示 "Resource has been modified"
  And 客户端应该获取最新版本重试
```

#### 8.2 并发创建同名 Skill
```gherkin
⬜ 待实现

Scenario: 两个请求同时创建同名 Skill
  Given 用户已认证
  When 两个并发请求同时创建 Skill "conflict-skill"
  Then 最终数据库中应该只有一条 "conflict-skill" 记录
  And 至少一个请求返回 201 Created
  And 其余请求返回 409 Conflict
  
  Note: 不强制要求"只有一个成功"，因为在分布式系统中可能出现两个请求
  都通过唯一性检查，但数据库约束会确保最终一致性
```

#### 8.3 并发文件操作
```gherkin
⬜ 待实现

Scenario: 并发修改 Tree 的同一文件
  Given 用户已认证
  And 文件 "test.txt" 存在
  When 两个并发请求同时更新文件内容
  Then 应该有一个成功
  And 另一个可能失败或被覆盖（根据实现）
  And 最终文件内容应该是确定性的
```

---

### 9. 网络和故障恢复

#### 9.1 上传中断恢复
```gherkin
⬜ 待实现

Scenario: 大文件上传中断后恢复
  Given 用户正在上传 50MB 文件
  When 上传到 30MB 时网络中断
  Then 上传应该失败
  
  When 网络恢复后重试上传
  And 支持断点续传
  Then 应该从 30MB 处继续（如果实现）
  Or 重新上传整个文件
```

#### 9.2 数据库连接中断
```gherkin
⬜ 待实现

Scenario: 操作过程中数据库断开
  Given 用户正在执行一系列操作
  When 数据库连接突然断开
  Then 应该返回 503 Service Unavailable
  And 不应该有数据不一致
  
  When 数据库恢复后
  Then 操作应该能正常继续
```

---

## P3 - 性能和压力测试

### 10. 性能基准测试

#### 10.1 Skill 列表查询性能
```gherkin
⬜ 待实现

Scenario: 大量 Skill 列表查询性能
  Given 用户拥有 1000 个 Skill
  When 获取 /api/skills?limit=100
  Then 响应时间应该 < 200ms
  
  When 获取 /api/skills?limit=1000
  Then 响应时间应该 < 500ms
```

#### 10.2 大文件树加载性能
```gherkin
⬜ 待实现

Scenario: 加载包含大量文件的 Tree
  Given Tree 包含 1000 个文件
  When 获取 /api/trees/{tree_id}
  Then 响应时间应该 < 300ms
  And 内存使用应该合理（不加载所有 blob 内容）
```

#### 10.3 批量操作性能
```gherkin
⬜ 待实现

Scenario: 批量导入大量文件
  Given 需要导入 1000 个文件
  When 执行批量导入
  Then 应该在 10 秒内完成
  And 系统应该保持稳定
```

---

### 11. 数据一致性验证（新增）

#### 11.1 Skill-Tree 级联删除
```gherkin
⬜ 待实现

Scenario: 删除 Skill 后关联 Tree 应该被清理
  Given Skill {skill_id} 关联 Tree {tree_id}
  And Tree 包含多个文件条目
  When 删除 Skill {skill_id}
  Then GET /api/skills/{skill_id} 应该返回 404
  And GET /api/trees/{tree_id} 应该返回 404
  And 数据库中不应该存在该 Tree 的记录

Scenario: 删除 Skill 后 Blob 引用计数应该减少
  Given Skill 包含文件 "test.txt" (blob_id=blob_1)
  And Blob blob_1 的引用计数为 1
  When 删除 Skill
  Then Blob blob_1 的引用计数应该为 0
  And blob_1 应该被标记为孤儿（可删除）
```

#### 11.2 Blob 引用计数一致性
```gherkin
⬜ 待实现

Scenario: 多 Skill 共享 Blob 的引用计数
  Given Blob blob_2 被 Skill A 引用
  And Blob blob_2 被 Skill B 引用
  Then blob_2 的引用计数应该为 2
  
  When 删除 Skill A
  Then blob_2 的引用计数应该为 1
  And blob_2 不应该被删除
  
  When 删除 Skill B
  Then blob_2 的引用计数应该为 0
  And blob_2 应该被标记为可删除

Scenario: 并发修改 Blob 引用计数
  Given Blob blob_3 当前引用计数为 10
  When 10 个并发请求同时添加引用
  Then 最终引用计数应该为 20
  
  When 5 个并发请求同时删除引用
  Then 最终引用计数应该为 15
```

#### 11.3 事务失败回滚
```gherkin
⬜ 待实现

Scenario: 批量添加文件部分失败时的回滚
  Given Tree 当前有 5 个文件
  When 批量添加 10 个文件，其中第 6 个失败（如路径冲突）
  Then 应该返回失败响应
  And Tree 应该仍然只有原来的 5 个文件（全部回滚）
  Or Tree 有 15 个文件，失败的第 6 个被跳过（部分成功需明确策略）
```

#### 11.4 存储配额一致性
```gherkin
⬜ 待实现

Scenario: 删除文件后存储配额应该更新
  Given 用户已使用存储空间 95MB
  And 用户删除一个 10MB 的文件
  When 用户查看存储使用情况
  Then 已使用空间应该显示为 85MB
  
  When 用户立即上传 8MB 文件
  Then 应该成功（85 + 8 = 93MB < 100MB 限制）
```

---

## 📊 覆盖统计（Metis 审核后更新）

| 优先级 | 总数 | 已实现 | 待实现 | 覆盖率 |
|-------|------|--------|--------|--------|
| P0 - 核心流程 | 15 | 9 | 6 | 60% |
| P1 - 安全权限 | 9 | 1 | 8 | 11% |
| P2 - 边缘场景 | 10 | 0 | 10 | 0% |
| P3 - 性能测试 | 3 | 0 | 3 | 0% |
| **总计** | **37** | **10** | **27** | **27%** |

### 关键缺口（Metis 审核确认）

1. 🔴 **Domain 层单元测试缺失**: 这是最严重缺口，应优先补充（详见 test-cases-domain.md）
2. 🔴 **Token 安全和速率限制**: 无相关测试（用户明确要求 ✅）
3. 🔴 **文件大小限制**: 用户提出的 10MB 限制无测试 ✅
4. 🔴 **数据一致性验证**: Blob 引用计数、级联删除场景缺失
5. 🟡 **并发场景**: 所有并发测试缺失，部分场景可能为 flaky test 需特殊处理
6. 🟡 **性能基准**: 无性能测试
7. 🟢 **故障恢复**: 无断电/降级测试

---

## 🎯 实现优先级建议（Metis 审核后修订）

### P0 - 立即实现（本周）

1. **Domain 层单元测试**（Metis 建议提升为 P0）
   - Path Value Object（路径遍历防护是安全底线）
   - Tree Aggregate（所有文件操作的核心）
   - Slug Value Object（数据完整性）
   - 详见 test-cases-domain.md

2. **文件大小限制测试**（用户明确要求 ✅）
   - 原始内容大小限制（10MB）
   - 压缩后场景

3. **Token 安全测试**（用户明确要求 ✅）
   - Token 泄露后的撤销机制
   - Refresh Token 轮换机制（提升为 P0）

4. **数据一致性验证**（新增 P0）
   - Skill-Tree 级联删除
   - Blob 引用计数一致性

### P1 - 短期实现（2周内）
5. 批量文件上传测试
6. 文件夹上传测试
7. 复杂文件移动测试
8. SKILL.md 保护机制测试（从 P0 调整为 P1）
9. 并发场景测试（注意避免 flaky test）

### P2 - 中期实现（1月内）
10. 性能基准测试
11. 网络故障恢复
12. 断电/降级测试

### 中期实现（1月内）
7. 所有安全相关测试（速率限制、Token 轮换等）
8. 并发场景测试
9. 性能基准测试

---

**文档版本**: 1.0  
**生成时间**: 2026-02-20  
**目标覆盖率**: 95%（当前 Journey 覆盖率约 32%，需补充 21 个测试）
