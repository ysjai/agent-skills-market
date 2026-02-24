# Backend Test Failure Decisions

## Date: 2026-02-20

## Decision 1: Fix SkillModel instead of tests
- **Rationale**: The model should be consistent with other models (UserModel, TreeModel)
- **Decision**: Add `server_default=text("gen_random_uuid()")` to SkillModel.id
- **Alternative rejected**: Modifying every test fixture to provide UUID

## Decision 2: Register exception handlers in main.py
- **Rationale**: Exception handlers already exist but aren't being used
- **Decision**: Add `register_exception_handlers(app)` call in main.py
- **Impact**: All domain exceptions will be properly converted to HTTP responses

## Decision 3: Update tests to match actual DTO format (for Tree API)
- **Rationale**: The DTO format `{id, entries, created_at}` is simpler and more direct
- **Decision**: Update test assertions from `data["data"]["entries"]` to `data["entries"]`
- **Alternative rejected**: Wrapping response in nested `data` object adds unnecessary complexity

## Decision 4: Implement blob deduplication in handler
- **Rationale**: Content-addressable storage is a common pattern
- **Decision**: Check `get_by_checksum()` before creating new blob
- **Impact**: Reduces storage, maintains expected test behavior
