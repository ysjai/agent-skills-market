# Backend API 全面功能测试计划

## TL;DR

> **快速 Summary**: 为后端 API 端点增加全面的集成测试覆盖，包括 Blobs、Trees、Skills、Versions API 的基础功能、边界、权限测试，以及 7 个核心 User Journey 集成场景。

> **Deliverables**:
> - `backend/tests/integration/api/test_blobs_api.py` - Blobs API 测试 (~20 测试用例)
> - `backend/tests/integration/api/test_trees_api.py` - Trees API 测试 (~25 测试用例)
> - `backend/tests/integration/api/test_skills_files_api.py` - 技能文件列表/下载测试 (~10 测试用例)
> - `backend/tests/integration/api/test_versions_api.py` - Versions API 测试 (~12 测试用例)
> - `backend/tests/integration/journey/test_journey_creation.py` - 完整创建流程 (Journey 1)
> - `backend/tests/integration/journey/test_journey_download.py` - 下载流程 (Journey 7)
> - `backend/tests/integration/journey/test_journey_import.py` - 导入流程 (Journey 2)
> - `backend/tests/integration/journey/test_journey_file_ops.py` - 文件树操作 (Journey 3)
> - `backend/tests/integration/journey/test_journey_multiuser.py` - 多用户隔离 (Journey 4)
> - `backend/tests/integration/journey/test_journey_deletion.py` - 删除清理 (Journey 5)
> - `backend/tests/integration/journey/test_journey_token.py` - Token 刷新 (Journey 6)

> **Estimated Effort**: Medium-Large
> **Parallel Execution**: YES - 多文件可并行开发
> **Critical Path**: Blobs → Trees → Skills/Versions → Journeys

---

## Context

### Original Request
用户希望为后端 API 端点增加"足够全面的 API 功能测试"，包括：
- 基础功能测试
- 边界测试
- 权限测试
- User Journey 连贯集成流程场景

### Metis Review 关键发现

**CRITICAL 发现**:
1. **Versions.py 无 rollback 端点** - 回滚是通过 `PUT /skills/{id}` 传入旧 `tree_id` 实现，而非独立的 rollback API
2. **Blob/Tree 授权不明确** - 代码中未发现 user ownership 检查，任何认证用户可访问任意 blob/tree（需确认是否为设计意图）

**需要澄清的问题**:
- Blob/Tree 的跨用户访问是否为预期行为？（安全考量）

---

## Work Objectives

### Core Objective
为以下 API 模块创建完整的集成测试覆盖：

| 模块 | 文件 | 测试用例数 | 优先级 |
|------|------|-----------|--------|
| Blobs API | api/test_blobs_api.py | ~20 | P0 |
| Trees API | api/test_trees_api.py | ~25 | P1 |
| Skills API (文件相关) | api/test_skills_files_api.py | ~10 | P1 |
| Versions API | api/test_versions_api.py | ~12 | P2 |
| Journey 完整创建 | journey/test_journey_creation.py | 1 | P2 |
| Journey 下载流程 | journey/test_journey_download.py | 1 | P2 |
| Journey 导入流程 | journey/test_journey_import.py | 1 | P2 |
| Journey 文件操作 | journey/test_journey_file_ops.py | 1 | P2 |
| Journey 多用户隔离 | journey/test_journey_multiuser.py | 1 | P2 |
| Journey 删除清理 | journey/test_journey_deletion.py | 1 | P2 |
| Journey Token刷新 | journey/test_journey_token.py | 1 | P2 |

### Definition of Done

- [ ] 所有端点的 成功 场景测试通过
- [ ] 所有端点的 404/401/403 错误场景测试通过
- [ ] CSRF 保护在所有写操作上验证
- [ ] 所有 User Journey 场景端到端通过

### Must Have
- 使用现有 `conftest.py` fixtures (auth_client, client, db_session)
- 使用 `pytest.mark.asyncio` 异步测试
- 遵循现有测试文件结构 (class-based organization)
- 每个测试独立，不依赖执行顺序

### 测试数据策略

#### 单点 API 测试：完全独立
- 每个测试使用 fixture 创建自己的测试数据
- 测试结束后不清理（依赖测试数据库自动隔离）
- 不同测试之间无数据依赖

#### User Journey 测试：场景内共享，场景间独立
- 每个 Journey 是**一个独立的测试函数**，从头到尾按顺序执行
- 同一个 Journey 内的步骤共享数据（如：步骤1创建的 skill_id 用于步骤2）
- 不同 Journey 之间**完全独立**（每个 Journey 使用自己的用户/技能）
- 使用 class 分组，每个 Journey class 就是一个完整场景

### Must NOT Have (Guardrails)
- ❌ 不修改任何 API router、model、schema
- ❌ 不创建单元测试（仅集成 API 测试）
- ❌ 不添加性能测试
- ❌ 不添加数据库压力测试
- ❌ 不实现新端点（仅测试已存在的端点）

---

## Verification Strategy

### Test Infrastructure
- **Framework**: pytest + pytest-asyncio
- **HTTP Client**: httpx (AsyncClient)
- **Database**: 使用现有 test fixtures (db_session, db_engine)
- **Authentication**: Cookie-based JWT + CSRF (通过 auth_client fixture)

### QA Policy
每个端点必须测试：
1. **Success**: 正确状态码 + 响应结构
2. **Not Found**: 404 错误
3. **Unauthorized**: 401 错误 (无认证)
4. **Forbidden**: 403 错误 (无权限)
5. **CSRF**: 写操作需要 CSRF token

### Test Execution
```bash
# 运行所有集成测试
cd backend && pytest tests/integration/ -v

# 仅运行 API 测试
pytest tests/integration/api/ -v

# 仅运行 Journey 测试
pytest tests/integration/journey/ -v

# 运行特定文件
pytest tests/integration/api/test_blobs_api.py -v

# 运行特定测试类
pytest tests/integration/test_blobs_api.py::TestUploadBlob -v
```

---

## Execution Strategy

### Phase 1: Blobs API (P0 - 基础依赖)
```
Wave 1: 创建 api/test_blobs_api.py (~300-400 行)
├── Task 1: TestUploadBlob - 上传测试 (6 用例)
├── Task 2: TestDownloadBlob - 下载测试 (5 用例)
├── Task 3: TestUpdateBlob - 更新测试 (3 用例)
└── Task 4: TestBlobEdgeCases - 边界测试 (6 用例)
```

### Phase 2: Trees API (P1 - 核心功能)
```
Wave 2: 创建 api/test_trees_api.py (~500-600 行)
├── Task 1: TestCreateTree - 创建树 (3 用例)
├── Task 2: TestGetTree - 获取树 (3 用例)
├── Task 3: TestAddFiles - 添加文件/文件夹 (6 用例)
├── Task 4: TestDeleteFiles - 删除文件 (4 用例)
├── Task 5: TestRenameMove - 重命名/移动 (4 用例)
├── Task 6: TestBatchUpload - 批量上传 (3 用例)
└── Task 7: TestTreeEdgeCases - 边界/安全 (5 用例)
```

### Phase 3: Skills 文件相关 + Versions (P1-P2)
```
Wave 3: 并行创建 api/
├── Task 1: api/test_skills_files_api.py (~200-300 行)
│   ├── 获取文件列表 (GET /skills/{id}/files)
│   ├── 下载 ZIP (GET /skills/{id}/download)
│   └── 权限测试
└── Task 2: api/test_versions_api.py (~300-400 行)
    ├── 创建版本 (POST /versions)
    ├── 列表/获取版本 (GET /versions)
    └── 权限测试
```

### Phase 4: User Journeys (P2 - 集成场景)
```
Wave 4: 创建 journey/ 目录，每个场景一个文件

├── journey/test_journey_creation.py   (Journey 1)
├── journey/test_journey_download.py   (Journey 7)
├── journey/test_journey_import.py     (Journey 2)
├── journey/test_journey_file_ops.py   (Journey 3)
├── journey/test_journey_multiuser.py  (Journey 4)
├── journey/test_journey_deletion.py   (Journey 5)
└── journey/test_journey_token.py      (Journey 6)
```
├── Journey 3: 文件树操作完整流程
├── Journey 4: 多用户数据隔离
├── Journey 5: 技能删除完整清理
├── Journey 6: Token 刷新流程
└── Journey 7: 下载到本地流程
```

---

## TODOs

### Phase 1: Blobs API

- [ ] 1. **test_blobs_api.py - TestUploadBlob**

  **What to do**:
  - `test_upload_text_blob_success`: 上传纯文本，返回 201 + blob 元数据
  - `test_upload_binary_blob_success`: 上传图片，返回 201 + blob 元数据
  - `test_upload_with_compression`: compress=true 上传可压缩内容，验证 compressed=true
  - `test_upload_without_compression`: compress=false 上传，验证 compressed=false
  - `test_upload_duplicate_content`: 上传相同内容两次，验证返回相同 blob_id (去重)
  - `test_upload_unauthenticated`: 未认证上传，验证 401

  **Must NOT do**:
  - 不测试超大文件（内存限制）

  **Recommended Agent Profile**:
  - **Category**: `quick`
  - **Skills**: []
  - Reason: Blobs API 相对简单，标准 CRUD 测试

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Wave 1 (with Tasks 1-4)
  - **Blocks**: Phase 2 (Trees 依赖 blobs 上传)

  **References**:
  - `app/routers/blobs.py:1-80` - Blobs router 实现
  - `app/schemas/blob.py` - Blob 请求/响应 schema
  - `tests/integration/test_skills_api.py` - 参考测试结构

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_blobs_api.py::TestUploadBlob -v → PASS (6 tests)

- [ ] 2. **test_blobs_api.py - TestDownloadBlob**

  **What to do**:
  - `test_download_blob_success`: 下载已上传的 blob，验证内容一致
  - `test_download_compressed_blob`: 下载已压缩 blob，验证自动解压
  - `test_download_nonexistent_blob`: 下载不存在的 blob，验证 404
  - `test_download_unauthenticated`: 未认证下载，验证 401
  - `test_download_invalid_blob_id_format`: 无效 blob_id 格式

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_blobs_api.py::TestDownloadBlob -v → PASS (5 tests)

- [ ] 3. **test_blobs_api.py - TestUpdateBlob**

  **What to do**:
  - `test_update_blob_success`: PUT 更新 blob，验证返回新 blob_id
  - `test_update_blob_unauthenticated`: 未认证更新，验证 401

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_blobs_api.py::TestUpdateBlob -v → PASS (2 tests)

- [ ] 4. **test_blobs_api.py - TestBlobEdgeCases**

  **What to do**:
  - `test_upload_empty_file`: 上传 0 字节文件
  - `test_upload_text_with_special_chars`: 含特殊字符的文本
  - `test_download_content_hash_verification`: 下载后验证内容哈希

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_blobs_api.py::TestBlobEdgeCases -v → PASS (3 tests)

---

### Phase 2: Trees API

- [ ] 5. **test_trees_api.py - TestCreateTree**

  **What to do**:
  - `test_create_tree_success`: POST /trees 创建空树
  - `test_create_tree_with_entries`: 创建带初始 entries 的树
  - `test_create_tree_unauthenticated`: 未认证创建

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestCreateTree -v → PASS

- [ ] 6. **test_trees_api.py - TestGetTree**

  **What to do**:
  - `test_get_tree_success`: GET /trees/{id}
  - `test_get_nonexistent_tree`: 404
  - `test_get_tree_unauthenticated`: 401

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestGetTree -v → PASS

- [ ] 7. **test_trees_api.py - TestAddFiles**

  **What to do**:
  - `test_add_text_file`: 添加文本文件 (content 字段)
  - `test_add_binary_file`: 通过 blob_id 添加二进制文件
  - `test_add_folder`: 添加文件夹 (type=tree)
  - `test_add_file_to_nested_path`: 添加深层嵌套路径
  - `test_add_duplicate_file`: 添加同名文件行为
  - `test_add_file_unauthenticated`: 401

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestAddFiles -v → PASS

- [ ] 8. **test_trees_api.py - TestDeleteFiles**

  **What to do**:
  - `test_delete_file_success`: DELETE /trees/{id}/files?path=xxx
  - `test_delete_folder_success`: 删除文件夹 (递归)
  - `test_delete_nonexistent_path`: 404
  - `test_delete_file_unauthenticated`: 401
  - **`test_delete_file_removes_blob`**: 删除文件后，验证 blob 也被删除 (返回 404)

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestDeleteFiles -v → PASS (包括 blob 清理验证)

- [ ] 9. **test_trees_api.py - TestRenameMove**

  **What to do**:
  - `test_rename_file_success`: PUT /trees/{id}/files/rename
  - `test_move_file_success`: PUT /trees/{id}/files/move
  - `test_rename_to_existing_name`: 覆盖行为
  - `test_move_to_invalid_target`: 无效目标

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestRenameMove -v → PASS

- [ ] 10. **test_trees_api.py - TestBatchOperations**

  **What to do**:
  - `test_batch_upload_success`: POST /trees/{id}/files/batch
  - `test_folder_upload_success`: POST /trees/{id}/files/folder
  - `test_update_file_content`: PUT /trees/{id}/files/content

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestBatchOperations -v → PASS

- [ ] 11. **test_trees_api.py - TestTreeEdgeCases**

  **What to do**:
  - `test_path_traversal_double_dot`: 路径 "../etc" → 400
  - `test_path_traversal_tilde`: 路径 "~" → 400
  - `test_path_with_unicode`: 路径含中文/emoji
  - `test_deep_nesting`: >10 层嵌套
  - `test_delete_root_path`: 删除 "/" → 400
  - **`test_upload_and_verify_content`**: 上传复杂目录结构，验证文件在正确路径，可下载并比对内容

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_trees_api.py::TestTreeEdgeCases -v → PASS

---

### Phase 3: Skills 文件相关 + Versions

- [ ] 12. **test_skills_files_api.py**

  **What to do**:
  - `test_get_skill_files_success`: GET /skills/{id}/files
  - `test_get_files_empty_skill`: 空技能返回空列表
  - `test_get_files_unauthorized`: 401
  - `test_get_files_forbidden`: 403 (跨用户)
  - `test_download_zip_success`: GET /skills/{id}/download?platform=opencode
  - `test_download_markdown`: GET /skills/{id}/download?platform=claude
  - `test_download_empty_skill`: 空技能下载
  - `test_download_forbidden`: 403

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_skills_files_api.py -v → PASS

- [ ] 13. **test_versions_api.py**

  **What to do**:
  - `test_create_version_success`: POST /versions
  - `test_version_number_increments`: 多次创建版本号递增
  - `test_list_versions`: GET /versions?skill_id=xxx
  - `test_get_version`: GET /versions/{id}
  - `test_create_version_unauthorized`: 401
  - `test_create_version_forbidden`: 403 (非所有者)
  - `test_list_versions_forbidden`: 403
  - `test_rollback_via_skill_update`: PUT /skills/{id} 用旧 tree_id 回滚

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/api/test_versions_api.py -v → PASS

---

### Phase 4: User Journeys (每个场景一个文件)

#### journey/test_journey_creation.py

- [ ] 14. **Journey 1: 完整技能创建流程**

  **Scenario**: 注册→登录→创建技能→上传文件→创建版本→验证

  **Data Strategy**: 同一个测试函数内按顺序执行，步骤间共享数据

  **Steps**:
  1. POST /auth/register (或使用现有 test_user)
  2. POST /skills (创建技能) → 获取 tree_id
  3. POST /blobs (上传文件1, 内容 "hello")
  4. POST /blobs (上传文件2, 内容 "world")
  5. POST /trees/{tree_id}/files (添加文件1)
  6. POST /trees/{tree_id}/files (添加文件2)
  7. GET /skills/{id} (验证)
  8. GET /skills/{id}/files (获取文件列表)
  9. GET /blobs/{blob_id} (下载验证内容)
  10. POST /versions (创建 v1)
  11. PUT /trees/{tree_id}/files/content (修改文件)
  12. POST /versions (创建 v2)
  13. GET /versions?skill_id={id} (查看历史)
  14. PUT /skills/{id} with tree_id=v1 (回滚)
  15. GET /trees/{tree_id} (验证回到 v1)

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_creation.py -v → PASS

---

#### journey/test_journey_download.py

- [ ] 15. **Journey 7: 下载到本地流程**

  **Scenario**: 前端实际使用的下载流程

  **Data Strategy**: 独立于其他 Journey，完全新的用户/技能数据

  **Steps**:
  1. POST /auth/login
  2. POST /skills (创建)
  3. POST /blobs (上传多个文件)
  4. POST /trees/{tree_id}/files/folder (添加)
  5. GET /skills/{id}/files (获取列表)
  6. 循环 GET /blobs/{id} (逐个下载)
  7. 验证内容与上传一致

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_download.py -v → PASS

---

#### journey/test_journey_import.py

- [ ] 16. **Journey 2: 技能导入流程 (复杂结构)**

  **Scenario**: 模拟前端导入本地文件夹流程 - 使用更复杂的 skill 结构

  **Data Strategy**: 独立数据环境

  **复杂目录结构**:
  ```
  my-skill/
  ├── SKILL.md                    # 技能说明文件
  ├── config.json                  # JSON 配置文件
  ├── main.py                      # Python 主脚本
  ├── requirements.txt             # Python 依赖
  ├── scripts/
  │   ├── setup.py                 # 安装脚本
  │   ├── run.py                   # 运行脚本
  │   └── test_runner.py           # 测试运行器
  ├── docs/
  │   ├── README.md                # 文档
  │   └── API.md                   # API 文档
  ├── assets/
  │   └── logo.png                 # 图片文件 (PNG)
  └── resources/
      └── manual.pdf               # PDF 文件
  ```

  **Steps**:
  1. POST /auth/login
  2. POST /skills/import (创建技能)
  3. 上传文件到 blobs:
     - SKILL.md, config.json, main.py, requirements.txt (根目录)
     - setup.py, run.py, test_runner.py (scripts/)
     - README.md, API.md (docs/)
     - logo.png (assets/) - 模拟 PNG 图片二进制
     - manual.pdf (resources/) - 模拟 PDF 二进制
  4. 批量添加文件到树 (创建目录结构和文件)
  5. GET /trees/{tree_id} (验证完整目录结构)
  6. GET /skills/{id}/files (验证文件列表)
  7. 逐个下载 blobs 验证内容完整性

  **验证点**:
  - [ ] 目录结构正确：scripts/, docs/, assets/, resources/ 四个子目录
  - [ ] 文件数量正确：至少 11 个文件
  - [ ] 能获取所有文件的 blob 并验证内容
  - [ ] 二进制文件 (PNG, PDF) 能正确下载

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_import.py -v → PASS

---

#### journey/test_journey_file_ops.py

- [ ] 17. **Journey 3: 文件树操作**

  **Scenario**: 完整文件树 CRUD

  **Data Strategy**: 独立数据环境

  **Steps**:
  1. POST /auth/login
  2. POST /skills (创建技能)
  3. POST /trees/{tree_id}/files (创建文件夹)
  4. POST /trees/{tree_id}/files (创建文件)
  5. PUT /trees/{tree_id}/files/rename (重命名)
  6. PUT /trees/{tree_id}/files/move (移动)
  7. DELETE /trees/{tree_id}/files (删除)

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_file_ops.py -v → PASS

---

#### journey/test_journey_multiuser.py

- [ ] 18. **Journey 4: 多用户数据隔离**

  **Scenario**: 验证用户之间数据隔离

  **Data Strategy**: 独立数据环境，需要两个不同用户

  **Steps**:
  1. 用户A: 注册 + 创建技能A
  2. 用户B: 注册 + 创建技能B
  3. 各自列表验证只能看到自己的
  4. 交叉访问 → 403

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_multiuser.py -v → PASS

---

#### journey/test_journey_deletion.py

- [ ] 5. **Journey 5: 技能删除完整清理**

  **Scenario**: 删除技能后关联数据清理

  **Data Strategy**: 独立数据环境

  **Steps**:
  1. POST /auth/login
  2. POST /skills (创建) → 获取 tree_id
  3. POST /blobs (上传)
  4. POST /versions (创建版本)
  5. DELETE /skills/{id}
  6. GET /skills/{id} → 404
  7. GET /trees/{tree_id} → 404
  8. **GET /blobs/{blob_id} → 404 (验证 blob 已被删除)**

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_deletion.py -v → PASS (包括 blob 清理验证)

---

#### journey/test_journey_token.py

- [ ] 20. **Journey 6: Token 刷新流程**

  **Scenario**: 验证 token 刷新流程

  **Data Strategy**: 独立数据环境

  **Steps**:
  1. POST /auth/login
  2. GET /auth/me (正常)
  3. POST /auth/refresh (刷新)
  4. GET /auth/me (新 token 正常)

  **Acceptance Criteria**:
  - [ ] pytest tests/integration/journey/test_journey_token.py -v → PASS

---

## Success Criteria

### Verification Commands
```bash
# 运行所有集成测试
cd backend && pytest tests/integration/ -v

# 仅运行 API 测试
pytest tests/integration/api/ -v

# 仅运行 Journey 测试
pytest tests/integration/journey/ -v

# 期望输出示例
# tests/integration/api/test_blobs_api.py .............. [20 tests]
# tests/integration/api/test_trees_api.py .............. [25 tests]
# tests/integration/api/test_skills_files_api.py ...... [10 tests]
# tests/integration/api/test_versions_api.py ........... [12 tests]
# tests/integration/journey/test_journey_creation.py . [1 test]
# tests/integration/journey/test_journey_download.py ... [1 test]
# tests/integration/journey/test_journey_import.py .... [1 test]
# tests/integration/journey/test_journey_file_ops.py .. [1 test]
# tests/integration/journey/test_journey_multiuser.py  [1 test]
# tests/integration/journey/test_journey_deletion.py . [1 test]
# tests/integration/journey/test_journey_token.py .... [1 test]
# ========================== 74 tests passed ==========================
```

### Final Checklist
- [ ] 74 个测试用例全部通过
- [ ] 无 401/403 绕过漏洞
- [ ] 路径遍历防护生效
- [ ] CSRF 保护在所有写操作上生效
- [ ] User Journey 端到端流程通过
