# Backend API Endpoints Analysis

**Framework**: FastAPI (Python)  
**Analysis Date**: 2025-02-20  
**Total Routes**: 6 router modules  
**Total Endpoints**: 32 endpoints

---

## Architecture Overview

```
app.main:FastAPI
├── health_router (prefix: none)
│   └── GET /health
└── api_router (prefix: /api)
    ├── auth_router (prefix: /auth)
    ├── skills_router (prefix: /skills)
    ├── blobs_router (prefix: /blobs)
    ├── trees_router (prefix: /trees)
    └── file_versions_router (prefix: /file-versions)
```

---

## Complete Endpoint List

### 1. Health Check
**File**: `backend/app/api/routers/health.py`
**Router**: `APIRouter(tags=["health"])`

| Method | Path | Handler | Auth Required | Description |
|--------|------|---------|---------------|-------------|
| GET | `/health` | `health_check()` | No | Health check endpoint |

**Response**: `{"status": "ok", "version": "1.0.0"}`

---

### 2. Authentication
**File**: `backend/app/api/routers/auth.py`
**Router**: `APIRouter(prefix="/auth", tags=["auth"])`
**Base Path**: `/api/auth`

| Method | Path | Handler | Auth Required | DTOs |
|--------|------|---------|---------------|------|
| POST | `/api/auth/register` | `register()` | No | RegisterUserReq → RegisterUserResp |
| POST | `/api/auth/login` | `login()` | No | LoginReq → LoginResp |
| POST | `/api/auth/refresh` | `refresh_token()` | Yes (Bearer) | Header → LoginResp |
| GET | `/api/auth/me` | `get_current_user_endpoint()` | Yes (Bearer) | → GetUserResp |
| POST | `/api/auth/logout` | `logout()` | Yes | → Message |

**Dependencies**:
- `get_user_repo` - User repository
- `verify_token()` - JWT verification

**Handler Files**:
- `app.application.handlers.register_user_handler`
- `app.application.handlers.login_handler`
- `app.application.handlers.refresh_token_handler`
- `app.application.handlers.get_current_user_handler`

---

### 3. Skills
**File**: `backend/app/api/routers/skills.py`
**Router**: `APIRouter(prefix="/skills", tags=["skills"])`
**Base Path**: `/api/skills`

| Method | Path | Handler | Auth Required | DTOs |
|--------|------|---------|---------------|------|
| POST | `/api/skills` | `create_skill()` | Yes | CreateSkillReq → CreateSkillResp (201) |
| POST | `/api/skills/import` | `import_skill()` | Yes | ImportSkillReq → CreateSkillResp (201) |
| GET | `/api/skills` | `list_skills()` | Yes | Query: skip, limit → ListSkillsResp |
| GET | `/api/skills/{skill_id}` | `get_skill()` | Yes | → GetSkillResp |
| GET | `/api/skills/{skill_id}/files` | `get_skill_files()` | Yes | → ListSkillFilesResp |
| PUT | `/api/skills/{skill_id}` | `update_skill()` | Yes | UpdateSkillReq → UpdateSkillResp |
| DELETE | `/api/skills/{skill_id}` | `delete_skill()` | Yes | 204 No Content |
| GET | `/api/skills/{skill_id}/download` | `download_skill()` | Yes | Query: platform → StreamingResponse |

**Dependencies**:
- `get_skill_repo` - Skill repository
- `get_tree_repo` - Tree repository
- `get_blob_repo` - Blob repository
- `get_current_user` - Current user

**Handler Files**:
- `app.application.handlers.create_skill_handler`
- `app.application.handlers.import_skill_handler`
- `app.application.handlers.list_skills_handler`
- `app.application.handlers.get_skill_handler`
- `app.application.handlers.update_skill_handler`
- `app.application.handlers.delete_skill_handler`
- `app.application.handlers.download_skill_handler`

---

### 4. Blobs
**File**: `backend/app/api/routers/blobs.py`
**Router**: `APIRouter(prefix="/blobs", tags=["blobs"])`
**Base Path**: `/api/blobs`

| Method | Path | Handler | Auth Required | DTOs |
|--------|------|---------|---------------|------|
| POST | `/api/blobs` | `upload_blob()` | Yes | Multipart file → UploadBlobResp (201) |
| PUT | `/api/blobs/{blob_id}` | `update_blob()` | Yes | Multipart file → UploadBlobResp |
| GET | `/api/blobs/{blob_id}` | `download_blob()` | Yes | → Binary content (Response) |

**Query Parameters**:
- `compress: bool = True` (for upload/update)

**Dependencies**:
- `get_blob_repo` - Blob repository
- `get_current_user` - Current user

**Handler Files**:
- `app.application.handlers.create_blob_handler`
- `app.application.handlers.get_blob_handler`

---

### 5. Trees
**File**: `backend/app/api/routers/trees.py`
**Router**: `APIRouter(prefix="/trees", tags=["trees"])`
**Base Path**: `/api/trees`

| Method | Path | Handler | Auth Required | DTOs |
|--------|------|---------|---------------|------|
| POST | `/api/trees` | `create_tree()` | Yes | CreateTreeReq → CreateTreeResp (201) |
| GET | `/api/trees/{tree_id}` | `get_tree()` | Yes | → GetTreeResp |
| POST | `/api/trees/{tree_id}/files` | `add_file()` | Yes | AddTreeFileReq → AddTreeFileResp |
| DELETE | `/api/trees/{tree_id}/files` | `delete_file()` | Yes | DeleteTreeFileReq → CreateTreeResp |
| PUT | `/api/trees/{tree_id}/files/rename` | `rename_file()` | Yes | RenameTreeFileReq → CreateTreeResp |
| PUT | `/api/trees/{tree_id}/files/move` | `move_file()` | Yes | MoveTreeFileReq → CreateTreeResp |
| PUT | `/api/trees/{tree_id}/files/content` | `update_file_content()` | Yes | UpdateTreeFileContentReq → CreateTreeResp |
| POST | `/api/trees/{tree_id}/files/batch` | `batch_upload()` | Yes | BatchUploadReq → BatchUploadResp |
| POST | `/api/trees/{tree_id}/files/folder` | `upload_folder()` | Yes | FolderUploadReq → AddTreeFileResp |

**Dependencies**:
- `get_tree_repo` - Tree repository
- `get_blob_repo` - Blob repository
- `get_current_user` - Current user

**Handler Files**:
- `app.application.handlers.create_tree_handler`
- `app.application.handlers.get_tree_handler`
- `app.application.handlers.add_tree_file_handler`
- `app.application.handlers.delete_tree_file_handler`
- `app.application.handlers.rename_tree_file_handler`
- `app.application.handlers.move_tree_file_handler`
- `app.application.handlers.update_tree_file_content_handler`

---

### 6. File Versions
**File**: `backend/app/api/routers/file_versions.py`
**Router**: `APIRouter(prefix="/file-versions", tags=["file-versions"])`
**Base Path**: `/api/file-versions`

| Method | Path | Handler | Auth Required | DTOs |
|--------|------|---------|---------------|------|
| POST | `/api/file-versions` | `create_file_version()` | Yes | CreateFileVersionReq → CreateFileVersionResp (201) |
| GET | `/api/file-versions` | `list_file_versions()` | Yes | Query: skill_id, file_path → list[FileVersionItem] |
| GET | `/api/file-versions/{file_version_id}` | `get_file_version()` | Yes | → FileVersionItem |

**Query Parameters**:
- `skill_id: UUID` (required for list)
- `file_path: str | None` (optional for list)

**Dependencies**:
- `get_file_version_repo` - File version repository
- `get_skill_repo` - Skill repository
- `get_current_user` - Current user

**Handler Files**:
- `app.application.handlers.create_file_version_handler`
- `app.application.handlers.list_file_versions_handler`
- `app.application.handlers.get_file_version_handler`

---

## Route Registration

**Main Entry**: `backend/app/main.py`

```python
app = FastAPI(title="Agent Skills Manager API", version="1.0.0")
app.include_router(health_router)
app.include_router(api_router)
```

**API Router Assembly**: `backend/app/api/__init__.py`

```python
api_router = APIRouter(prefix="/api")
api_router.include_router(auth_router)
api_router.include_router(skills_router)
api_router.include_router(blobs_router)
api_router.include_router(trees_router)
api_router.include_router(file_versions_router)
```

---

## File Structure

```
backend/app/api/
├── __init__.py              # API router assembly
├── exception_handlers.py    # Global exception handlers
├── dependencies/
│   ├── __init__.py
│   ├── auth.py             # get_current_user dependency
│   └── repositories.py     # Repository DI functions
├── routers/
│   ├── __init__.py
│   ├── auth.py             # 5 endpoints
│   ├── blobs.py            # 3 endpoints
│   ├── file_versions.py    # 3 endpoints
│   ├── health.py           # 1 endpoint
│   ├── skills.py           # 8 endpoints
│   └── trees.py            # 9 endpoints
└── schemas/
    ├── __init__.py
    ├── blob.py
    ├── file_version.py
    ├── skill.py
    ├── tree.py
    └── user.py
```

---

## Schema Files

| File | Schemas |
|------|---------|
| `schemas/user.py` | RegisterUserReq, RegisterUserResp, LoginReq, LoginResp, GetUserResp |
| `schemas/skill.py` | CreateSkillReq, CreateSkillResp, GetSkillResp, ListSkillsResp, ListSkillsItemResp, UpdateSkillReq, UpdateSkillResp, ListSkillFilesResp |
| `schemas/blob.py` | UploadBlobResp |
| `schemas/tree.py` | CreateTreeReq, CreateTreeResp, GetTreeResp, AddTreeFileReq, AddTreeFileResp, DeleteTreeFileReq, RenameTreeFileReq, MoveTreeFileReq, UpdateTreeFileContentReq, BatchUploadReq, BatchUploadResp, FolderUploadReq |
| `schemas/file_version.py` | CreateFileVersionReq, CreateFileVersionResp, FileVersionItem |

---

## Handler Files (Application Layer)

```
backend/app/application/handlers/
├── add_tree_file_handler.py
├── create_blob_handler.py
├── create_file_version_handler.py
├── create_skill_handler.py
├── create_tree_handler.py
├── delete_skill_handler.py
├── delete_tree_file_handler.py
├── download_skill_handler.py
├── get_blob_handler.py
├── get_current_user_handler.py
├── get_file_version_handler.py
├── get_project_handler.py
├── get_skill_handler.py
├── get_tree_handler.py
├── handle_create_tree_file.py
├── import_skill_handler.py
├── list_file_versions_handler.py
├── list_skills_handler.py
├── login_handler.py
├── move_tree_file_handler.py
├── refresh_token_handler.py
├── register_user_handler.py
├── rename_tree_file_handler.py
└── update_skill_handler.py
```

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Total Router Modules** | 6 |
| **Total Endpoints** | 32 |
| **Public Endpoints** | 3 (/health, /api/auth/register, /api/auth/login) |
| **Protected Endpoints** | 29 |
| **GET Endpoints** | 12 |
| **POST Endpoints** | 13 |
| **PUT Endpoints** | 4 |
| **DELETE Endpoints** | 3 |

---

## Authentication Pattern

All protected endpoints use:
```python
current_user: User = Depends(get_current_user)
```

The `get_current_user` dependency extracts and validates JWT from Authorization header.

---

## Repository Dependencies

| Repository | Used In Routers |
|------------|-----------------|
| `UserRepository` | auth |
| `SkillRepository` | skills, file_versions |
| `TreeRepository` | skills, trees |
| `BlobRepository` | skills, blobs, trees |
| `FileVersionRepository` | file_versions |
