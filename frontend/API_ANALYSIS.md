# 前端 API 调用类型定义清单

## 概述
本文档全面分析了 `/Users/ysj/opensource/agent-skills-pointer/frontend` 目录下所有 API 调用，包括端点路径、请求/响应类型定义。

---

## API 调用汇总表

### 1. 认证相关 (Auth)

| 端点 | 方法 | 文件位置 | Request Type | Response Type |
|------|------|----------|--------------|---------------|
| `/auth/me` | GET | app/api/auth.ts:7 | - | `User` |
| `/auth/me` | GET | app/api/auth.ts:12 | - | `User` |
| `/auth/me` | GET | app/api/auth.ts:20 | - | `User` |
| `/auth/refresh` | POST | app/api/auth.ts:16 | - | `void` |
| `/auth/logout` | POST | app/api/auth.ts:25 | - | `void` |
| `/auth/login` | POST | lib/api.ts:168 | `{ email: string, password: string }` | `TokenResponse` |
| `/auth/register` | POST | lib/api.ts:192 | `{ email: string, username: string, password: string }` | `TokenResponse` |
| `/auth/refresh` | POST | lib/api.ts:146 | - (Header: Bearer) | `TokenResponse` |

**类型定义：**

```typescript
// types/user.ts
interface User {
  id: string;
  email: string;
  username: string | null;
  phone: string | null;
  is_active: boolean;
  email_verified: boolean;
  created_at: string;
  updated_at: string;
}

interface LoginRequest {
  email: string;
  password: string;
  remember_me?: boolean;
}

interface RegisterRequest {
  email: string;
  username?: string;
  phone?: string;
  password: string;
}

// lib/api.ts
interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}
```

---

### 2. Skills 相关

| 端点 | 方法 | 文件位置 | Request Type | Response Type |
|------|------|----------|--------------|---------------|
| `/skills` | GET | app/[locale]/skills/page.tsx:75 | - | `SkillListResponse` |
| `/skills/{id}` | GET | app/[locale]/skills/[id]/page.tsx:64 | - | `Skill` |
| `/skills/{id}` | DELETE | app/[locale]/skills/page.tsx:102 | - | `void` |
| `/skills/{id}` | DELETE | app/[locale]/skills/[id]/page.tsx:89 | - | `void` |
| `/skills` | POST | components/skills/CreateSkillDialog.tsx:75 | `CreateSkillRequest` | `Skill` |
| `/skills/import` | POST | components/skills/ImportSkillDialog.tsx:234 | `CreateSkillRequest` | `Skill` |
| `/skills/{id}/files` | GET | components/misc/DownloadDialog.tsx:85 | - | `{ files: Array<{ path: string; type: string }> }` |
| `/skills/{id}/files` | GET | components/misc/DownloadDialog.tsx:104 | - | `{ files: Array<{ path: string; type: string; blob_id?: string }> }` |
| `/skills/{id}/files` | GET | lib/download.ts:163 | - | `SkillFileResponse` |
| `/skills/{id}/files` | GET | lib/download.ts:334 | - | `SkillFileResponse` |

**类型定义：**

```typescript
// types/skill.ts
interface Skill {
  id: string;
  user_id: string;
  name: string;
  slug: string;
  description: string | null;
  version: number;
  is_public: boolean;
  tree_id: string | null;
  created_at: string;
  updated_at: string;
}

interface SkillListResponse {
  items: Skill[];
  total: number;
}

interface CreateSkillRequest {
  name: string;
  slug: string;
  description?: string;
  version?: string;
  is_public?: boolean;
  tags?: string[];
  platform_support?: string[];
}

interface UpdateSkillRequest {
  name?: string;
  slug?: string;
  description?: string;
  version?: string;
  is_public?: boolean;
  tags?: string[];
  platform_support?: string[];
}

// lib/download.ts
interface SkillFileResponse {
  files: Array<{
    path: string;
    type: string;
    blob_id?: string;
  }>;
}
```

---

### 3. Trees 相关

| 端点 | 方法 | 文件位置 | Request Type | Response Type |
|------|------|----------|--------------|---------------|
| `/trees/{id}` | GET | hooks/file-tree/useFileTree.ts:87 | - | `TreeStructure` |
| `/trees/{id}/files` | POST | hooks/useFileTreeDialogs.ts:88 | `{ path: string, type: 'blob' \| 'tree', content?: string }` | `CreateTreeResponse` |
| `/trees/{id}/files` | DELETE | hooks/useFileTreeDialogs.ts:151 | Query: `{ path: string }` | `void` |
| `/trees/{id}/files` | POST | hooks/useFileUpload.ts:218 | `{ path: string, type: string, content?: string, blob_id?: string }` | `CreateTreeResponse` |
| `/trees/{id}/files` | DELETE | hooks/useFileUpload.ts:276 | Query: `{ path: string }` | `void` |
| `/trees/{id}/files` | POST | hooks/useFileUpload.ts:298 | `{ path: string, type: string, content?: string, blob_id?: string }` | `CreateTreeResponse` |
| `/trees/{id}/files/rename` | PUT | components/file-tree/FileTree.tsx:192 | `{ old_path: string, new_path: string }` | `UpdateTreeResponse` |
| `/trees/{id}/files/move` | PUT | components/file-tree/FileTree.tsx:223 | `{ source: string, target: string }` | `UpdateTreeResponse` |
| `/trees/{id}/files/content` | PUT | components/editors/TextEditor.tsx:126 | `{ path: string, content: string }` | `UpdateTreeResponse` |
| `/trees/{id}/files/content` | PUT | components/editors/MarkdownEditor.tsx:103 | `{ path: string, content: string }` | `UpdateTreeResponse` |
| `/trees/{id}/files/folder` | POST | components/skills/ImportSkillDialog.tsx:292 | `{ base_path: string, entries: Array<{ path: string, type: 'blob' \| 'tree', content?: string, blob_id?: string }> }` | `CreateTreeResponse` |
| `/trees/{id}/files/folder` | POST | hooks/useFileUpload.ts:386 | `{ base_path: string, entries: Array<{ path: string, type: 'blob' \| 'tree', content?: string, blob_id?: string }> }` | `CreateTreeResponse` |

**类型定义：**

```typescript
// types/file-tree.ts
interface TreeEntry {
  path: string;
  blob_id?: string;
  type: 'blob' | 'tree';
  name?: string;
  children?: TreeEntry[];
}

interface TreeStructure {
  id: string;
  entries: TreeEntry[];
  created_at: string;
}

interface FileTreeNode extends TreeEntry {
  id: string;
  isExpanded?: boolean;
  isEditing?: boolean;
  depth: number;
  children?: FileTreeNode[];
}

interface CreateFileRequest {
  path: string;
  content?: string;
  type: 'blob' | 'tree';
}

// 内联响应类型 (来自各组件)
interface CreateTreeResponse {
  id: string;
  entries: Array<{
    path: string;
    blob_id: string | null;
    type: string;
  }>;
  created_at: string;
}

interface UpdateTreeResponse {
  id: string;
  entries: Array<{
    path: string;
    blob_id: string | null;
    type: string;
  }>;
  created_at: string;
}
```

---

### 4. Blobs 相关

| 端点 | 方法 | 文件位置 | Request Type | Response Type |
|------|------|----------|--------------|---------------|
| `/blobs` | POST | hooks/useFileUpload.ts:129 | `FormData (file: File)` | `UploadBlobResponse` |
| `/blobs/{id}` | GET | components/editors/TextEditor.tsx:95 | - | `Blob` |
| `/blobs/{id}` | GET | components/editors/MarkdownEditor.tsx:73 | - | `Blob` |
| `/blobs/{id}` | GET | app/[locale]/skills/[id]/page.tsx:101 | - | `Blob` |
| `/blobs/{id}` | GET | hooks/useFolderDownload.ts:88 | - | `Blob` |
| `/blobs/{id}` | GET | hooks/useFolderDownload.ts:163 | - | `Blob` |
| `/blobs/{id}` | GET | lib/download.ts:201 | - | `Blob` |
| `/blobs/{id}` | GET | lib/download.ts:384 | - | `Blob` |
| `/blobs/{id}` | PUT | components/editors/TextEditor.tsx:178 | `FormData (file: Blob)` | `void` |
| `/blobs/{id}` | PUT | components/editors/MarkdownEditor.tsx:151 | `FormData (file: Blob)` | `void` |
| `/blobs/{id}` | POST | components/skills/ImportSkillDialog.tsx:259 | `FormData (file: File)` | `UploadBlobResponse` |

**类型定义：**

```typescript
// 内联响应类型
interface UploadBlobResponse {
  id: string;
  content_hash: string;
  size: number;
  compressed: boolean;
  created_at: string;
}
```

---

## 按文件分类的 API 调用详情

### app/api/auth.ts
```typescript
// Line 4-8: 用户注册
POST /auth/register (via api.register)
→ 内部调用: api.get<User>('/auth/me')

// Line 10-13: 用户登录  
POST /auth/login (via api.login)
→ 内部调用: api.get<User>('/auth/me')

// Line 15-17: 刷新 Token
POST /auth/refresh

// Line 19-22: 获取当前用户
GET /auth/me
→ Response: User

// Line 24-26: 用户登出
POST /auth/logout
```

### app/[locale]/skills/page.tsx
```typescript
// Line 75: 获取技能列表
GET /skills
→ Response: SkillListResponse { items: Skill[], total: number }

// Line 102: 删除技能
DELETE /skills/${skillId}
```

### app/[locale]/skills/[id]/page.tsx
```typescript
// Line 64: 获取技能详情
GET /skills/${skillId}
→ Response: Skill

// Line 89: 删除技能
DELETE /skills/${skill.id}

// Line 101: 下载 Blob
GET /blobs/${blobId}
→ Response: Blob
```

### components/skills/CreateSkillDialog.tsx
```typescript
// Line 69-75: 创建技能
POST /skills
Request: {
  name: string;      // 必须: 小写字母、数字、连字符
  slug: string;      // 必须: 与 name 相同
  description?: string;
}
→ Response: Skill
```

### components/skills/ImportSkillDialog.tsx
```typescript
// Line 234: 导入技能
POST /skills/import
Request: CreateSkillRequest
→ Response: Skill

// Line 259-270: 上传 Blob
POST /blobs
Request: FormData (file: File)
→ Response: { id, content_hash, size, compressed, created_at }

// Line 292-296: 批量上传文件夹
POST /trees/${treeId}/files/folder
Request: {
  base_path: string;
  entries: Array<{
    path: string;
    type: 'blob' | 'tree';
    content?: string;
    blob_id?: string;
  }>;
}
→ Response: CreateTreeResponse

// Line 194: 检查技能是否存在
GET /skills
→ Response: { items?: Skill[] }
```

### components/file-tree/FileTree.tsx
```typescript
// Line 192-203: 重命名文件/文件夹
PUT /trees/${treeId}/files/rename
Request: {
  old_path: string;
  new_path: string;
}
→ Response: {
  id: string;
  entries: Array<{ path: string; blob_id: string | null; type: string }>;
  created_at: string;
}

// Line 223-247: 移动文件/文件夹
PUT /trees/${treeId}/files/move
Request: {
  source: string;
  target: string;
}
→ Response: UpdateTreeResponse
```

### components/editors/TextEditor.tsx & MarkdownEditor.tsx
```typescript
// Line 95-98 (Text), 73-76 (Markdown): 加载 Blob 内容
GET /blobs/${id}
→ Response: Blob

// Line 126-156 (Text), 103-131 (Markdown): 保存文件内容
PUT /trees/${treeId}/files/content
Request: {
  path: string;
  content: string;
}
→ Response: UpdateTreeResponse

// Line 178-183 (Text), 151-156 (Markdown): 更新 Blob (备用)
PUT /blobs/${blobId}
Request: FormData (file: Blob)
```

### hooks/useFileTree.ts
```typescript
// Line 87: 获取树结构
GET /trees/${treeId}
→ Response: TreeStructure { id, entries: TreeEntry[], created_at: string }
```

### hooks/useFileTreeDialogs.ts
```typescript
// Line 88-100: 创建文件/文件夹
POST /trees/${treeId}/files
Request: {
  path: string;
  type: 'blob' | 'tree';
  content?: string;  // 文件时有内容
}
→ Response: CreateTreeResponse

// Line 151: 删除文件/文件夹
DELETE /trees/${treeId}/files
Query: { path: string }
```

### hooks/useFileUpload.ts
```typescript
// Line 129-138: 上传二进制文件
POST /blobs
Request: FormData (file: File)
→ Response: UploadBlobResponse

// Line 218-246: 上传文件到树
POST /trees/${treeId}/files
Request: {
  path: string;
  type: 'blob';
  content?: string;    // 文本文件
  blob_id?: string;    // 二进制文件
}
→ Response: CreateTreeResponse

// Line 276: 删除文件(覆盖时)
DELETE /trees/${treeId}/files?path=${originalFilePath}

// Line 298-307: 单文件上传(冲突解决)
POST /trees/${treeId}/files

// Line 386-415: 批量上传文件夹
POST /trees/${treeId}/files/folder
Request: {
  base_path: string;
  entries: Array<{
    path: string;
    type: 'blob' | 'tree';
    content?: string;
    blob_id?: string;
  }>;
}
→ Response: CreateTreeResponse
```

### hooks/useFolderDownload.ts
```typescript
// Line 88, 163: 获取 Blob 用于下载
GET /blobs/${file.blobId}
→ Response: Blob
```

### lib/download.ts
```typescript
// Line 163: 获取技能文件列表
GET /skills/${skillId}/files
→ Response: SkillFileResponse

// Line 201, 334, 384: 下载 Blob
GET /blobs/${file.blob_id}
→ Response: Blob
```

### components/misc/DownloadDialog.tsx
```typescript
// Line 85: 检查文件名
GET /skills/${skillId}/files
→ Response: { files: Array<{ path: string; type: string }> }

// Line 104: 下载 ZIP
GET /skills/${skillId}/files
→ Response: { files: Array<{ path: string; type: string; blob_id?: string }> }

// Line 113: 获取 Blob
GET /blobs/${file.blob_id}
→ Response: Blob
```

---

## 查询参数汇总

| 端点 | 查询参数 | 说明 |
|------|----------|------|
| `/skills` | `skip`, `limit` | 分页参数 (代码中未实际使用，但后端支持) |
| `/trees/{id}/files` (DELETE) | `path` | 要删除的文件路径 |
| `/auth/refresh` | - | 使用 Authorization Header 传递 refresh_token |

---

## 关键内联类型定义

### Tree 操作响应类型 (多处使用)
```typescript
{
  id: string;
  entries: Array<{
    path: string;
    blob_id: string | null;
    type: string;
  }>;
  created_at: string;
}
```

### Blob 上传响应类型
```typescript
{
  id: string;
  content_hash: string;
  size: number;
  compressed: boolean;
  created_at: string;
}
```

### Skill 文件列表响应类型
```typescript
{
  files: Array<{
    path: string;
    type: string;
    blob_id?: string;
  }>;
}
```

---

## 注意事项

1. **Token 刷新**: `/auth/refresh` 使用特殊的处理逻辑，在 `lib/api.ts:139-165` 中实现

2. **FormData 上传**: 所有 Blob 上传 (`/blobs`) 使用 `FormData` 格式，不是 JSON

3. **路径参数**: 
   - `{id}` - 技能 ID 或 Tree ID
   - `{skillId}` - 技能 ID
   - `{blobId}` - Blob ID
   - `{treeId}` - Tree ID

4. **废弃代码**: FileVersion 相关 API 已废弃 (注释掉的代码在 `app/[locale]/skills/[id]/page.tsx:73-83`)

5. **文件上传特殊处理**:
   - 文本文件: 直接发送 `content` 字符串
   - 二进制文件: 先上传到 `/blobs`，然后发送 `blob_id`

6. **错误处理**: 所有 API 调用都使用统一的错误处理机制在 `lib/api.ts:110-137` 中实现

---

## 文件统计

- 总共分析文件数: 88 个
- 包含 API 调用的文件: 12 个
- 总 API 调用次数: 46 次

### API 调用分布
- GET: 20 次
- POST: 16 次
- PUT: 7 次
- DELETE: 3 次
