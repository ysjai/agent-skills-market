# 后端 API 契约完整清单

## 目录
1. [认证端点 (Auth)](#1-认证端点-auth)
2. [Skill 端点](#2-skill-端点)
3. [Tree 端点](#3-tree-端点)
4. [Blob 端点](#4-blob-端点)
5. [FileVersion 端点 (已废弃)](#5-fileversion-端点已废弃)
6. [Health 端点](#6-health-端点)

---

## 1. 认证端点 (Auth)

**前缀**: `/api/auth`

### 1.1 POST /api/auth/register
用户注册

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | `RegisterUserReq` |
| Response Schema | `RegisterUserResp` |
| 状态码 | 201 Created |

**RegisterUserReq:**
```yaml
email: str (required, EmailStr格式验证)
username: str (required, min_length=1, max_length=100)
password: str (required, min_length=8, max_length=100)
```

**RegisterUserResp:**
```yaml
id: UUID
email: str
username: str
phone: str | null
is_active: bool
email_verified: bool
created_at: datetime
access_token: str
refresh_token: str
token_type: str (default="bearer")
```

---

### 1.2 POST /api/auth/login
用户登录

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | `LoginReq` |
| Response Schema | `LoginResp` |

**LoginReq:**
```yaml
email: str (required, EmailStr格式验证)
password: str (required)
```

**LoginResp:**
```yaml
access_token: str
refresh_token: str
token_type: str (default="bearer")
```

---

### 1.3 POST /api/auth/refresh
刷新访问令牌

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | - |
| Response Schema | `LoginResp` |
| Header | `Authorization: Bearer <refresh_token>` |

**LoginResp:** (同上)
```yaml
access_token: str
refresh_token: str
token_type: str (default="bearer")
```

---

### 1.4 GET /api/auth/me
获取当前用户信息

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Request Schema | - |
| Response Schema | `GetUserResp` |
| Header | `Authorization: Bearer <token>` |

**GetUserResp:**
```yaml
id: UUID
email: str
username: str
phone: str | null
is_active: bool
email_verified: bool
created_at: datetime
updated_at: datetime
```

---

### 1.5 POST /api/auth/logout
用户登出

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | - |
| Response Schema | `dict` |

**Response:**
```yaml
message: str (="Logged out successfully")
```

---

## 2. Skill 端点

**前缀**: `/api/skills`

### 2.1 POST /api/skills
创建 Skill

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | `CreateSkillReq` |
| Response Schema | `CreateSkillResp` |
| 状态码 | 201 Created |
| Auth | Required |

**CreateSkillReq:**
```yaml
name: str (required, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
slug: str (required, min_length=1, max_length=255)
description: str (required, min_length=1, max_length=1000)
```

**CreateSkillResp:**
```yaml
id: UUID
user_id: UUID
name: str
slug: str
description: str | null
tree_id: UUID | null
is_public: bool
version: int
created_at: datetime
updated_at: datetime
```

---

### 2.2 POST /api/skills/import
导入 Skill

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | `ImportSkillReq` (继承 CreateSkillReq) |
| Response Schema | `CreateSkillResp` |
| 状态码 | 201 Created |
| Auth | Required |

**ImportSkillReq:** (同 CreateSkillReq)
```yaml
name: str (required, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
slug: str (required, min_length=1, max_length=255)
description: str (required, min_length=1, max_length=1000)
```

---

### 2.3 GET /api/skills
列出用户 Skills

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Request Schema | - |
| Response Schema | `ListSkillsResp` |
| Query Params | `skip: int (ge=0, default=0)`, `limit: int (ge=1, le=100, default=100)` |
| Auth | Required |

**ListSkillsResp:** (继承 CreateSkillResp)
```yaml
items: ListSkillsItemResp[]
total: int
# 继承 CreateSkillResp 的所有字段:
id: UUID
user_id: UUID
name: str
slug: str
description: str | null
tree_id: UUID | null
is_public: bool
version: int
created_at: datetime
updated_at: datetime
```

**ListSkillsItemResp:**
```yaml
id: UUID
name: str
slug: str
description: str | null
is_public: bool
version: int
created_at: datetime
updated_at: datetime
```

---

### 2.4 GET /api/skills/{skill_id}
获取 Skill 详情

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Path Param | `skill_id: UUID` |
| Response Schema | `GetSkillResp` |
| Auth | Required |

**GetSkillResp:**
```yaml
id: UUID
user_id: UUID
name: str
slug: str
description: str | null
tree_id: UUID | null
is_public: bool
version: int
created_at: datetime
updated_at: datetime
```

---

### 2.5 GET /api/skills/{skill_id}/files
获取 Skill 文件列表

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Path Param | `skill_id: UUID` |
| Response Schema | `ListSkillFilesResp` |
| Auth | Required |

**ListSkillFilesResp:**
```yaml
skill_id: UUID
skill_name: str
files: SkillFileEntry[]
```

**SkillFileEntry:**
```yaml
path: str
type: str
blob_id: UUID | null
```

---

### 2.6 PUT /api/skills/{skill_id}
更新 Skill

| 属性 | 值 |
|------|-----|
| 方法 | PUT |
| Path Param | `skill_id: UUID` |
| Request Schema | `UpdateSkillReq` |
| Response Schema | `UpdateSkillResp` |
| Auth | Required |

**UpdateSkillReq:**
```yaml
name: str | null (min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
slug: str | null (min_length=1, max_length=255)
description: str | null (max_length=1000)
tree_id: UUID | null
is_public: bool | null
```

**UpdateSkillResp:**
```yaml
id: UUID
user_id: UUID
name: str
slug: str
description: str | null
tree_id: UUID | null
is_public: bool
version: int
created_at: datetime
updated_at: datetime
```

---

### 2.7 DELETE /api/skills/{skill_id}
删除 Skill

| 属性 | 值 |
|------|-----|
| 方法 | DELETE |
| Path Param | `skill_id: UUID` |
| Response Schema | - (204 No Content) |
| 状态码 | 204 No Content |
| Auth | Required |

---

### 2.8 GET /api/skills/{skill_id}/download
下载 Skill

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Path Param | `skill_id: UUID` |
| Query Param | `platform: str | null` |
| Response | `StreamingResponse` (文件下载) |
| Auth | Required |

---

## 3. Tree 端点

**前缀**: `/api/trees`

### 3.1 POST /api/trees
创建 Tree

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Schema | `CreateTreeReq` |
| Response Schema | `CreateTreeResp` |
| 状态码 | 201 Created |
| Auth | Required |

**CreateTreeReq:**
```yaml
entries: list[dict[str, Any]] (default=[])
  # 每个 entry 包含: path, blob_id, type
```

**CreateTreeResp:**
```yaml
id: UUID
entries: TreeEntryItem[]
created_at: datetime
```

**TreeEntryItem:**
```yaml
path: str (min_length=0, max_length=512)
blob_id: UUID | null
entry_type: str (pattern="^(blob|tree)$", serialization_alias="type")
```

---

### 3.2 GET /api/trees/{tree_id}
获取 Tree

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Path Param | `tree_id: UUID` |
| Response Schema | `GetTreeResp` |
| Auth | Required |

**GetTreeResp:**
```yaml
id: UUID
entries: TreeEntryItem[]
created_at: datetime
```

---

### 3.3 POST /api/trees/{tree_id}/files
添加文件到 Tree

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Path Param | `tree_id: UUID` |
| Request Schema | `AddTreeFileReq` |
| Response Schema | `AddTreeFileResp` |
| Auth | Required |

**AddTreeFileReq:**
```yaml
path: str (required, min_length=1, max_length=512)
entry_type: str (required, pattern="^(blob|tree)$", validation_alias=["entry_type", "type"])
blob_id: UUID | null
content: str | null
```

**AddTreeFileResp:**
```yaml
id: UUID
entries: TreeEntryItem[]
created_at: datetime
```

---

### 3.4 DELETE /api/trees/{tree_id}/files
从 Tree 删除文件

| 属性 | 值 |
|------|-----|
| 方法 | DELETE |
| Path Param | `tree_id: UUID` |
| Request Body | `DeleteTreeFileReq` (可选) |
| Query Param | `path: str` (可选，与 body 二选一) |
| Response Schema | `CreateTreeResp` |
| Auth | Required |

**DeleteTreeFileReq:**
```yaml
path: str (required, min_length=1, max_length=512)
```

---

### 3.5 PUT /api/trees/{tree_id}/files/rename
重命名文件

| 属性 | 值 |
|------|-----|
| 方法 | PUT |
| Path Param | `tree_id: UUID` |
| Request Schema | `RenameTreeFileReq` |
| Response Schema | `CreateTreeResp` |
| Auth | Required |

**RenameTreeFileReq:**
```yaml
old_path: str (required, min_length=1, max_length=512)
new_path: str (required, min_length=1, max_length=512)
```

---

### 3.6 PUT /api/trees/{tree_id}/files/move
移动文件

| 属性 | 值 |
|------|-----|
| 方法 | PUT |
| Path Param | `tree_id: UUID` |
| Request Schema | `MoveTreeFileReq` |
| Response Schema | `CreateTreeResp` |
| Auth | Required |

**MoveTreeFileReq:**
```yaml
source: str (required, min_length=1, max_length=512)
target: str (required, min_length=1, max_length=512)
```

---

### 3.7 PUT /api/trees/{tree_id}/files/content
更新文件内容

| 属性 | 值 |
|------|-----|
| 方法 | PUT |
| Path Param | `tree_id: UUID` |
| Request Schema | `UpdateTreeFileContentReq` |
| Response Schema | `CreateTreeResp` |
| Auth | Required |

**UpdateTreeFileContentReq:**
```yaml
path: str (required, min_length=1, max_length=512)
content: str (required, min_length=0)
```

---

### 3.8 POST /api/trees/{tree_id}/files/batch
批量上传文件

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Path Param | `tree_id: UUID` |
| Request Schema | `BatchUploadReq` |
| Response Schema | `BatchUploadResp` |
| Auth | Required |

**BatchUploadReq:**
```yaml
entries: BatchUploadEntry[]
```

**BatchUploadEntry:**
```yaml
path: str (required, min_length=1, max_length=512)
entry_type: str (required, pattern="^(blob|tree)$", validation_alias=["entry_type", "type"])
content: str | null
```

**BatchUploadResp:**
```yaml
uploaded: int
failed: int
```

---

### 3.9 POST /api/trees/{tree_id}/files/folder
上传文件夹

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Path Param | `tree_id: UUID` |
| Request Schema | `FolderUploadReq` |
| Response Schema | `AddTreeFileResp` |
| Auth | Required |

**FolderUploadReq:**
```yaml
base_path: str (required, min_length=0, max_length=512)
entries: FolderUploadEntry[]
```

**FolderUploadEntry:**
```yaml
path: str (required, min_length=1, max_length=512)
entry_type: str (required, pattern="^(blob|tree)$", validation_alias=["entry_type", "type"])
blob_id: UUID | null
content: str | null
```

---

## 4. Blob 端点

**前缀**: `/api/blobs`

### 4.1 POST /api/blobs
上传 Blob

| 属性 | 值 |
|------|-----|
| 方法 | POST |
| Request Type | `multipart/form-data` |
| Form Field | `file: UploadFile` |
| Query Param | `compress: bool (default=true)` |
| Response Schema | `UploadBlobResp` |
| 状态码 | 201 Created |
| Auth | Required |

**UploadBlobResp:**
```yaml
id: UUID
content_hash: str (min_length=64, max_length=64)
size: int (ge=0)
compressed: bool
created_at: datetime
```

---

### 4.2 PUT /api/blobs/{blob_id}
更新 Blob

| 属性 | 值 |
|------|-----|
| 方法 | PUT |
| Path Param | `blob_id: str` |
| Request Type | `multipart/form-data` |
| Form Field | `file: UploadFile` |
| Query Param | `compress: bool (default=true)` |
| Response Schema | `UploadBlobResp` |
| Auth | Required |

---

### 4.3 GET /api/blobs/{blob_id}
下载 Blob

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Path Param | `blob_id: str` |
| Response | `Response` (二进制内容, media_type="application/octet-stream") |
| Auth | Required |

---

## 5. FileVersion 端点（已废弃）

**前缀**: `/api/file-versions`

⚠️ **注意**: 根据要求，忽略 FileVersion 相关端点。

---

## 6. Health 端点

### 6.1 GET /health
健康检查

| 属性 | 值 |
|------|-----|
| 方法 | GET |
| Response | `dict` |

**Response:**
```yaml
status: str (="ok")
version: str (="1.0.0")
```

---

## Schema 详细定义汇总

### 用户相关 Schemas

#### RegisterUserReq
```yaml
email: str (required, EmailStr格式验证)
username: str (required, min_length=1, max_length=100)
password: str (required, min_length=8, max_length=100)
```

#### LoginReq
```yaml
email: str (required, EmailStr格式验证)
password: str (required)
```

#### UpdateUserReq
```yaml
username: str | null (min_length=1, max_length=100)
phone: str | null (max_length=20)
```

### Skill 相关 Schemas

#### CreateSkillReq
```yaml
name: str (required, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
slug: str (required, min_length=1, max_length=255)
description: str (required, min_length=1, max_length=1000)
```

#### UpdateSkillReq
```yaml
name: str | null (min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
slug: str | null (min_length=1, max_length=255)
description: str | null (max_length=1000)
tree_id: UUID | null
is_public: bool | null
```

### Tree 相关 Schemas

#### CreateTreeReq
```yaml
entries: list[dict[str, Any]] (default=[])
```

#### AddTreeFileReq
```yaml
path: str (required, min_length=1, max_length=512)
entry_type: str (required, pattern="^(blob|tree)$", validation_alias=["entry_type", "type"])
blob_id: UUID | null
content: str | null
```

#### DeleteTreeFileReq
```yaml
path: str (required, min_length=1, max_length=512)
```

#### RenameTreeFileReq
```yaml
old_path: str (required, min_length=1, max_length=512)
new_path: str (required, min_length=1, max_length=512)
```

#### MoveTreeFileReq
```yaml
source: str (required, min_length=1, max_length=512)
target: str (required, min_length=1, max_length=512)
```

#### UpdateTreeFileContentReq
```yaml
path: str (required, min_length=1, max_length=512)
content: str (required, min_length=0)
```

#### BatchUploadReq
```yaml
entries: BatchUploadEntry[]
```

#### BatchUploadEntry
```yaml
path: str (required, min_length=1, max_length=512)
entry_type: str (required, pattern="^(blob|tree)$", validation_alias=["entry_type", "type"])
content: str | null
```

#### FolderUploadReq
```yaml
base_path: str (required, min_length=0, max_length=512)
entries: FolderUploadEntry[]
```

#### FolderUploadEntry
```yaml
path: str (required, min_length=1, max_length=512)
entry_type: str (required, pattern="^(blob|tree)$", validation_alias=["entry_type", "type"])
blob_id: UUID | null
content: str | null
```

### Project 相关 Schemas (未使用)

⚠️ **注意**: Project schemas 存在但未在任何 router 中使用。

#### CreateProjectReq
```yaml
name: str (required, min_length=1, max_length=255)
local_path: str | null (max_length=1000)
description: str | null (max_length=1000)
```

#### UpdateProjectReq
```yaml
name: str | null (min_length=1, max_length=255)
local_path: str | null (max_length=1000)
description: str | null (max_length=1000)
```

---

## 关键验证规则汇总

| Schema | 字段 | 规则 |
|--------|------|------|
| RegisterUserReq | username | min=1, max=100 |
| RegisterUserReq | password | min=8, max=100 |
| CreateSkillReq | name | min=1, max=255, pattern=`^[a-z0-9-]+$` |
| CreateSkillReq | description | min=1, max=1000 |
| UpdateSkillReq | name | min=1, max=255, pattern=`^[a-z0-9-]+$` |
| UpdateSkillReq | description | max=1000 |
| TreeEntryItem | path | min=0, max=512 |
| TreeEntryItem | entry_type | pattern=`^(blob\|tree)$` |
| AddTreeFileReq | path | min=1, max=512 |
| DeleteTreeFileReq | path | min=1, max=512 |
| RenameTreeFileReq | old_path/new_path | min=1, max=512 |
| MoveTreeFileReq | source/target | min=1, max=512 |
| UpdateTreeFileContentReq | path | min=1, max=512 |
| CreateProjectReq | name | min=1, max=255 |
| UploadBlobResp | content_hash | min=64, max=64 |
| UploadBlobResp | size | ge=0 |
| ListSkillsReq | skip | ge=0 |
| ListSkillsReq | limit | ge=1, le=100 |

---

## 字段别名说明

| Schema | 字段 | 别名配置 |
|--------|------|----------|
| TreeEntryItem | entry_type | `serialization_alias="type"` |
| AddTreeFileReq | entry_type | `validation_alias=AliasChoices("entry_type", "type")` |
| BatchUploadEntry | entry_type | `validation_alias=AliasChoices("entry_type", "type")` |
| FolderUploadEntry | entry_type | `validation_alias=AliasChoices("entry_type", "type")` |

---

## 认证要求汇总

| 端点 | 认证要求 |
|------|----------|
| POST /api/auth/register | 否 |
| POST /api/auth/login | 否 |
| POST /api/auth/refresh | 是 (Header: Bearer refresh_token) |
| GET /api/auth/me | 是 (Header: Bearer token) |
| POST /api/auth/logout | 是 |
| 所有 /api/skills/* | 是 |
| 所有 /api/trees/* | 是 |
| 所有 /api/blobs/* | 是 |
| 所有 /api/file-versions/* | 是 |
| GET /health | 否 |
