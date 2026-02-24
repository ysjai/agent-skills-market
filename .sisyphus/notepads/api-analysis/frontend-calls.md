# Frontend API Calls Analysis

## Overview
- **Analysis Date**: 2026-02-20
- **API Client**: Custom `ApiClient` class in `/frontend/lib/api.ts`
- **HTTP Library**: Native `fetch` API (no axios)
- **Base URL**: `process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api'`

## API Client Structure

### Core Methods (lib/api.ts)
| Method | HTTP Method | Description |
|--------|-------------|-------------|
| `api.get<T>(url, params?)` | GET | Generic GET request with query params |
| `api.post<T>(url, data?, options?)` | POST | Generic POST request |
| `api.put<T>(url, data?, options?)` | PUT | Generic PUT request |
| `api.patch<T>(url, data?, options?)` | PATCH | Generic PATCH request |
| `api.delete<T>(url, params?, options?)` | DELETE | Generic DELETE request with query params |
| `api.getBlob(url, options?)` | GET | Download binary blob content |

### Auth Methods (lib/api.ts)
| Method | Endpoint | HTTP Method | Description |
|--------|----------|-------------|-------------|
| `api.login(email, password)` | `/auth/login` | POST | Authenticate user |
| `api.register(email, username, password)` | `/auth/register` | POST | Register new user |
| `api.logout()` | `/auth/logout` | POST | Logout user |
| `api.isAuthenticated()` | - | - | Check if user has access token |

---

## Complete API Endpoint Inventory

### Authentication Endpoints

#### POST /auth/login
- **Location**: `lib/api.ts:168`
- **Used by**: Direct client usage
- **Request Body**: `{ email: string, password: string }`
- **Response**: `TokenResponse { access_token, refresh_token, token_type }`
- **Notes**: Sets tokens in localStorage

#### POST /auth/register
- **Location**: `lib/api.ts:192`
- **Used by**: Direct client usage
- **Request Body**: `{ email: string, username: string, password: string }`
- **Response**: `TokenResponse`
- **Notes**: Sets tokens in localStorage

#### POST /auth/logout
- **Location**: `lib/api.ts:217`, `app/api/auth.ts:25`
- **Used by**: Auth module
- **Response**: None (204)
- **Notes**: Clears tokens and redirects to login

#### POST /auth/refresh
- **Location**: `lib/api.ts:146`
- **Used by**: Internal (auto-refresh on 401)
- **Request Headers**: `Authorization: Bearer {refresh_token}`
- **Response**: `TokenResponse`

#### GET /auth/me
- **Location**: `app/api/auth.ts:7,12,20`
- **Used by**: Auth module (`getCurrentUser`, `login`, `register`)
- **Response**: `User`

---

### Skills Endpoints

#### GET /skills
- **Location**: `app/[locale]/skills/page.tsx:75`, `components/skills/ImportSkillDialog.tsx:194`
- **Used by**: Skills list page, import dialog (duplicate check)
- **Response**: `SkillListResponse { items: Skill[] }`

#### GET /skills/{id}
- **Location**: `app/[locale]/skills/[id]/page.tsx:64`
- **Used by**: Skill detail page
- **Response**: `Skill`

#### POST /skills
- **Location**: `components/skills/CreateSkillDialog.tsx:75`
- **Used by**: Create skill dialog
- **Request Body**: `CreateSkillRequest { name, slug, description? }`
- **Response**: `Skill`

#### POST /skills/import
- **Location**: `components/skills/ImportSkillDialog.tsx:234`
- **Used by**: Import skill dialog
- **Request Body**: `CreateSkillRequest`
- **Response**: `Skill`

#### DELETE /skills/{id}
- **Location**: `app/[locale]/skills/page.tsx:102`, `app/[locale]/skills/[id]/page.tsx:89`
- **Used by**: Skills list page, skill detail page
- **Response**: None (204)

#### GET /skills/{skillId}/files
- **Location**: `components/misc/DownloadDialog.tsx:85,104`, `lib/download.ts:163,334`
- **Used by**: Download dialog, download utility
- **Response**: `{ files: Array<{ path: string, type: string, blob_id?: string }> }`

---

### Trees Endpoints (File Tree Management)

#### GET /trees/{treeId}
- **Location**: `hooks/file-tree/useFileTree.ts:87`
- **Used by**: File tree hook
- **Response**: `TreeStructure`

#### POST /trees/{treeId}/files
- **Location**: `hooks/useFileUpload.ts:218,300`, `hooks/useFileTreeDialogs.ts:88`
- **Used by**: File upload hook, file tree dialogs
- **Request Body**: `{ path: string, type: 'blob'|'tree', content?: string, blob_id?: string }`
- **Response**: Tree update response with entries

#### POST /trees/{treeId}/files/folder
- **Location**: `hooks/useFileUpload.ts:390`, `components/skills/ImportSkillDialog.tsx:292`
- **Used by**: Folder upload, skill import
- **Request Body**: `{ base_path: string, entries: Array<...> }`
- **Response**: `{ tree_id, data: { entries }, uploaded, failed }`

#### DELETE /trees/{treeId}/files
- **Location**: `hooks/useFileUpload.ts:278`, `hooks/useFileTreeDialogs.ts:153`
- **Used by**: File upload hook (overwrite), file tree dialogs (delete)
- **Request Body**: `{ path: string }`
- **Response**: Tree update response

#### PUT /trees/{treeId}/files/rename
- **Location**: `components/file-tree/FileTree.tsx:192`
- **Used by**: File tree (rename operation)
- **Request Body**: `{ old_path: string, new_path: string }`
- **Response**: Tree update response

#### PUT /trees/{treeId}/files/move
- **Location**: `components/file-tree/FileTree.tsx:225`
- **Used by**: File tree (move operation)
- **Request Body**: `{ source: string, target: string }`
- **Response**: Tree update response

#### PUT /trees/{treeId}/files/content
- **Location**: `components/editors/TextEditor.tsx:126`
- **Used by**: Text editor (save content)
- **Request Body**: `{ path: string, content: string }`
- **Response**: Tree update response

---

### Blobs Endpoints (Binary Content)

#### GET /blobs/{blobId}
- **Locations**:
  - `components/editors/TextEditor.tsx:95` (with signal)
  - `components/editors/TextViewer.tsx:50`
  - `components/editors/MarkdownEditor.tsx:73`
  - `components/editors/MarkdownViewer.tsx:136`
  - `components/file-tree/ImagePreview.tsx:30`
  - `components/file-tree/PdfPreview.tsx:28`
  - `app/[locale]/skills/[id]/page.tsx:101`
  - `lib/download.ts:201,384`
  - `hooks/useFolderDownload.ts:88,163`
  - `components/misc/DownloadDialog.tsx:113`
- **Used by**: Editors, preview components, download utilities
- **Response**: `Blob` (binary content)

#### POST /blobs
- **Location**: `hooks/useFileUpload.ts:129`, `components/skills/ImportSkillDialog.tsx:259`
- **Used by**: File upload (binary files), skill import
- **Request Body**: `FormData` with `file` field
- **Response**: `{ id, content_hash, size, compressed, created_at }`

#### PUT /blobs/{blobId}
- **Location**: `components/editors/TextEditor.tsx:180`, `components/editors/MarkdownEditor.tsx:153`
- **Used by**: Text/Markdown editors (save blob directly)
- **Request Body**: `FormData` with `file` field
- **Response**: None

---

## File-by-File API Usage Summary

### lib/api.ts
- **Type**: API Client Core
- **API Methods Defined**: `get`, `post`, `put`, `patch`, `delete`, `getBlob`
- **Auth Methods**: `login`, `register`, `logout`, `isAuthenticated`
- **Direct fetch Calls**: `/auth/refresh`, `/auth/login`, `/auth/register`

### app/api/auth.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/auth/me` | GET | `getCurrentUser()` - after register/login |
| `/auth/me` | GET | `getCurrentUser()` - standalone |
| `/auth/refresh` | POST | `refreshToken()` |
| `/auth/logout` | POST | `logout()` |

### app/[locale]/skills/page.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/skills` | GET | `loadSkills()` - list all skills |
| `/skills/{id}` | DELETE | `handleDeleteSkill()` - delete skill |

### app/[locale]/skills/[id]/page.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/skills/{id}` | GET | `loadSkill()` - get skill details |
| `/skills/{id}` | DELETE | `handleDelete()` - delete skill |
| `/blobs/{id}` | GET | `handleDownload()` - download file |

### components/skills/CreateSkillDialog.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/skills` | POST | Create new skill |

### components/skills/ImportSkillDialog.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/skills` | GET | `checkSkillExists()` - check for duplicates |
| `/skills/import` | POST | Import skill from directory |
| `/blobs` | POST | Upload binary files during import |
| `/trees/{treeId}/files/folder` | POST | Upload folder structure |

### components/file-tree/FileTree.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/trees/{treeId}/files/rename` | PUT | `handleRename()` - rename file/folder |
| `/trees/{treeId}/files/move` | PUT | `handleMove()` - move file/folder |

### components/editors/TextEditor.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{id}` | GET | `loadBlobContent()` - load file content |
| `/trees/{treeId}/files/content` | PUT | `saveBlobContent()` - save via tree API |
| `/blobs/{blobId}` | PUT | `saveBlobContent()` - save directly to blob (fallback) |

### components/editors/MarkdownEditor.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{id}` | GET | Load blob content |
| `/trees/{treeId}/files/content` | PUT | Save content via tree |
| `/blobs/{blobId}` | PUT | Save blob directly |

### components/editors/TextViewer.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{id}` | GET | Load blob content |

### components/editors/MarkdownViewer.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{id}` | GET | Load blob content |

### components/file-tree/ImagePreview.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{blobId}` | GET | Load image blob |

### components/file-tree/PdfPreview.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{blobId}` | GET | Load PDF blob |

### components/misc/DownloadDialog.tsx
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/skills/{skillId}/files` | GET | Get file list for ZIP creation |
| `/blobs/{blob_id}` | GET | Download each file for ZIP |

### hooks/useFileUpload.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs` | POST | `uploadBinaryFile()` - upload binary |
| `/trees/{treeId}/files` | POST | Add file to tree |
| `/trees/{treeId}/files` | DELETE | Delete file (for overwrite) |
| `/trees/{treeId}/files/folder` | POST | Upload folder contents |

### hooks/useFileTreeDialogs.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/trees/{treeId}/files` | POST | `handleDialogConfirm()` - create file/folder |
| `/trees/{treeId}/files` | DELETE | `executeDelete()` - delete file/folder |

### hooks/useFileTree.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/trees/{treeId}` | GET | `fetchTree()` - load tree structure |

### hooks/useFolderDownload.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/blobs/{blobId}` | GET | Download files for ZIP/folder download |

### lib/download.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| `/skills/{skillId}/files` | GET | Get file list |
| `/blobs/{blob_id}` | GET | Download file content |

### lib/auth.ts
| Endpoint | Method | Usage |
|----------|--------|-------|
| (calls api.logout) | POST | `/auth/logout` |

---

## Authentication Flow

1. **Login**: `api.login()` → POST `/auth/login` → Store tokens → GET `/auth/me`
2. **Register**: `api.register()` → POST `/auth/register` → Store tokens → GET `/auth/me`
3. **Token Refresh**: Automatic on 401 → POST `/auth/refresh` (using refresh token)
4. **Logout**: POST `/auth/logout` → Clear tokens → Redirect to login

---

## Key Patterns

### 1. Tree-Based File Operations
- All file mutations go through `/trees/{treeId}/files/*` endpoints
- Supports: create, delete, rename, move, update content, batch folder upload

### 2. Blob Storage
- Binary content stored separately via `/blobs` endpoints
- Blobs are immutable (new blob ID on update)
- Files reference blobs via `blob_id` field

### 3. Error Handling
- 401 triggers automatic token refresh
- Failed refresh redirects to login
- Network errors wrapped with descriptive messages

### 4. Request Types
- **JSON**: Default for most requests (`Content-Type: application/json`)
- **FormData**: Used for file uploads (binary blobs)
- **Query Params**: Used for DELETE requests with path parameter

---

## Missing/Commented Endpoints

### Versions (Currently Disabled)
- ~~POST /versions~~ - Commented in `app/[locale]/skills/[id]/page.tsx:75`
- ~~Skill version history and rollback~~ - Not currently implemented

---

## Total API Call Sites

| Category | Count |
|----------|-------|
| Authentication | 6 endpoints |
| Skills | 6 endpoints |
| Trees | 7 endpoints |
| Blobs | 3 endpoints |
| **Total Unique Endpoints** | **22** |
| **Total Call Sites** | **75+** |

---

## Files with API Calls (26 files)

1. `lib/api.ts` - API client core
2. `lib/auth.ts` - Auth utilities
3. `lib/download.ts` - Download utilities
4. `app/api/auth.ts` - Auth API wrappers
5. `app/[locale]/skills/page.tsx` - Skills list
6. `app/[locale]/skills/[id]/page.tsx` - Skill detail
7. `components/skills/CreateSkillDialog.tsx`
8. `components/skills/ImportSkillDialog.tsx`
9. `components/file-tree/FileTree.tsx`
10. `components/editors/TextEditor.tsx`
11. `components/editors/TextViewer.tsx`
12. `components/editors/MarkdownEditor.tsx`
13. `components/editors/MarkdownViewer.tsx`
14. `components/file-tree/ImagePreview.tsx`
15. `components/file-tree/PdfPreview.tsx`
16. `components/misc/DownloadDialog.tsx`
17. `hooks/useFileUpload.ts`
18. `hooks/useFileTreeDialogs.ts`
19. `hooks/useFileTree.ts`
20. `hooks/useFolderDownload.ts`
21. `lib/__tests__/api.integration.test.ts` - Tests
22. `lib/__tests__/auth.test.ts` - Tests
23. `test/__mocks__/api.ts` - Mocks
24. `project_conventions.md` - Documentation

---

## Backend Compatibility Notes

This analysis is for checking API compatibility after backend refactoring. Key areas to verify:

1. **Tree endpoints** - All file operations depend on these
2. **Blob endpoints** - File content storage/retrieval
3. **Skill endpoints** - CRUD operations
4. **Auth endpoints** - Session management
5. **Response formats** - Tree responses with `data.entries` structure
