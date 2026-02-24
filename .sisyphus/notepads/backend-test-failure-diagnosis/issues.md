# Backend Test Failure Issues

## Date: 2026-02-20

## Issue Summary

After analyzing 146 tests with many FAILURES and ERRORS, identified 5 root causes:

### 1. SkillModel Primary Key Missing server_default (CRITICAL)
- **Location**: `backend/app/infra/persistence/models/skill_model.py`
- **Problem**: `id` field has `primary_key=True` but no `server_default=text("gen_random_uuid()")`
- **Impact**: All tests using `test_skill` fixture fail with `FlushError: Instance has a NULL identity key`
- **Contrast**: `UserModel` and `TreeModel` have correct configuration

### 2. Exception Handlers Not Registered (CRITICAL)
- **Location**: `backend/app/main.py`
- **Problem**: `register_exception_handlers(app)` is never called
- **Impact**: Domain exceptions (UnauthorizedError, ForbiddenError, etc.) are not converted to HTTP responses
- **Files**: `exception_handlers.py` exists but is unused

### 3. Tree API Response Format Mismatch (MEDIUM)
- **Location**: `backend/tests/integration/api/test_trees_api.py`
- **Problem**: Tests expect `{id, data: {entries: [...]}}` but API returns `{id, entries: [...]}`
- **Impact**: ~30 tree-related tests fail

### 4. Blob Deduplication Missing (MEDIUM)
- **Location**: `backend/app/application/handlers/create_blob_handler.py`
- **Problem**: No check for existing blob with same content_hash before creating new one
- **Impact**: `test_upload_duplicate_content` fails

### 5. Test Fixtures Missing Required Fields (CRITICAL)
- **Locations**:
  - `backend/tests/integration/api/test_file_versions_api.py`
  - `backend/tests/integration/test_skills_api.py`
- **Problem**: `test_skill` fixtures don't provide `id` field
- **Impact**: Same as issue #1 (flush fails)
