# Coverage Gap Analysis Report: Path to 95%

> **Analysis Date**: 2026-02-20  
> **Current Coverage**: 89.62% (1994 statements, 207 missing)  
> **Target Coverage**: 95%  
> **Statements to Cover**: ~107 additional statements needed

---

## Executive Summary

To reach the 95% coverage target from the current 89.62%, we need to cover approximately **107 additional statements**. Based on ROI analysis, this is achievable by targeting **7 high-impact modules** that collectively provide **103 statements** of coverage potential.

### Key Findings

| Priority | Modules | Missing Lines | Est. Coverage Gain |
|----------|---------|---------------|-------------------|
| 🔴 P1 | 7 critical gaps | ~70 lines | +3.5% |
| 🟡 P2 | Router error paths | ~30 lines | +1.5% |
| 🟢 P3 | Factory edge cases | ~18 lines | +0.9% |
| **Total** | **~15 test files** | **~118 lines** | **+5.9%** |

**Result**: 89.62% → **95.5%** (exceeds target)

---

## Detailed Gap Analysis

### Current State Calculation

```
Total Statements:        1994
Currently Missing:        207
Currently Covered:       1787 (89.62%)

Target (95%):            1894 statements needed
Gap to Close:            1894 - 1787 = 107 statements
```

---

## Priority 1: Critical Gaps (<70% coverage)

### 1.1 update_tree_handler.py 🎯 **HIGHEST ROI**

| Metric | Value |
|--------|-------|
| **Current Coverage** | 0% |
| **Total Lines** | 29 |
| **Missing Lines** | 15 (entire file) |
| **Estimated Gain** | +15 statements |
| **Test Effort** | Low (~1 hour) |
| **ROI Score** | ⭐⭐⭐⭐⭐ |

**Missing Logic** (lines 11-29):
```python
async def handle_update_tree(
    tree_repo: TreeRepository,
    tree_id: UUID,
    entries: list[dict[str, Any]],
) -> Tree:
    tree = await tree_repo.get_by_id(tree_id)  # Line 16
    if tree is None:  # Line 17
        raise ResourceNotFoundError(f"Tree '{tree_id}' not found")  # Line 18

    tree.entries = []  # Line 20
    for entry_data in entries:  # Line 21
        tree.add_entry(  # Line 22-26
            path=entry_data["path"],
            entry_type=entry_data["type"],
            blob_id=entry_data.get("blob_id"),
        )

    await tree_repo.save(tree)  # Line 28
    return tree  # Line 29
```

**Test Scenarios Needed**:
1. ✅ Update tree with valid entries list
2. ✅ Update tree with empty entries list
3. ❌ Tree not found raises ResourceNotFoundError
4. ✅ Verify entries are replaced (not appended)

---

### 1.2 update_tree_file_content_handler.py

| Metric | Value |
|--------|-------|
| **Current Coverage** | 43% |
| **Total Lines** | 38 |
| **Missing Lines** | 13 (lines 21-38) |
| **Estimated Gain** | +13 statements |
| **Test Effort** | Low (~1 hour) |
| **ROI Score** | ⭐⭐⭐⭐⭐ |

**Missing Logic** (lines 21-38):
```python
# Lines 20-23: Tree not found check
tree = await tree_repo.get_by_id(tree_id)
if tree is None:
    raise ResourceNotFoundError(f"Tree '{tree_id}' not found")

# Lines 25-33: Blob creation/reuse logic
content_bytes = content.encode("utf-8")
content_hash = hashlib.sha256(content_bytes).hexdigest()
existing_blob = await blob_repo.get_by_checksum(content_hash)
if existing_blob:
    new_blob_id = existing_blob.id
else:
    blob = Blob.create(content_bytes)
    await blob_repo.save(blob)
    new_blob_id = blob.id

# Lines 36-38: Update entry
tree.update_entry_content(path=path, new_blob_id=new_blob_id)
await tree_repo.save(tree)
return tree
```

**Test Scenarios Needed**:
1. ❌ Tree not found raises ResourceNotFoundError
2. ✅ Update file with new content (creates new blob)
3. ✅ Update file with existing content (reuses blob via checksum)
4. ✅ Verify blob reference counting works correctly

---

### 1.3 login_handler.py

| Metric | Value |
|--------|-------|
| **Current Coverage** | 50% |
| **Total Lines** | 25 |
| **Missing Lines** | 9 (lines 17-25) |
| **Estimated Gain** | +9 statements |
| **Test Effort** | Low (~30 min) |
| **ROI Score** | ⭐⭐⭐⭐ |

**Missing Logic** (success path - lines 17-25):
```python
user = await user_repo.get_by_email(email_vo)  # Line 16 (partial)
# Lines 17-22: All validation passed
if not user:  # Line 17 - NOT taken (covered)
if not bcrypt.checkpw(...):  # Line 19 - NOT taken (covered)
if not user.is_active:  # Line 21 - NOT taken (covered)

# Lines 23-25: Token creation (SUCCESS PATH - NOT COVERED)
access_token = create_access_token(data={"sub": str(user.id)})
refresh_token = create_refresh_token(data={"sub": str(user.id)})
return user, access_token, refresh_token
```

**Test Scenarios Needed**:
1. ✅ Valid credentials return user + tokens (covers lines 23-25)

*Note: Failure paths (invalid email, wrong password, inactive user) are already covered*

---

### 1.4 create_skill_handler.py

| Metric | Value |
|--------|-------|
| **Current Coverage** | 55% |
| **Total Lines** | 31 |
| **Missing Lines** | 9 (lines 20-31) |
| **Estimated Gain** | +9 statements |
| **Test Effort** | Low (~30 min) |
| **ROI Score** | ⭐⭐⭐⭐ |

**Missing Logic** (success path - lines 20-31):
```python
# Line 20-22: Slug conflict check (covered)
existing = await skill_repo.get_by_slug(slug, user_id)
if existing:
    raise ResourceConflictError()

# Lines 24-30: SUCCESS PATH - NOT COVERED
tree = TreeFactory.create()
await tree_repo.save(tree)
await tree_repo.flush()  # Flush tree to DB before saving skill with tree_id

skill = SkillFactory.create(user_id=user_id, name=name, description=description)
skill.assign_tree(tree.id)
await skill_repo.save(skill)
return skill
```

**Test Scenarios Needed**:
1. ✅ Successful skill creation with tree assignment

---

### 1.5 import_skill_handler.py

| Metric | Value |
|--------|-------|
| **Current Coverage** | 55% |
| **Total Lines** | 32 |
| **Missing Lines** | 9 (lines 21-32) |
| **Estimated Gain** | +9 statements |
| **Test Effort** | Low (~30 min) |
| **ROI Score** | ⭐⭐⭐⭐ |

**Missing Logic** (success path - lines 21-32):
```python
# Line 21-23: Slug conflict check (covered)
existing = await skill_repo.get_by_slug(skill_slug, user_id)
if existing:
    raise ResourceConflictError()

# Lines 25-31: SUCCESS PATH - NOT COVERED
tree = TreeFactory.create()
await tree_repo.save(tree)
await tree_repo.flush()

skill = SkillFactory.create(user_id=user_id, name=name, description=description, slug=slug)
skill.assign_tree(tree.id)
await skill_repo.save(skill)
return skill
```

**Test Scenarios Needed**:
1. ✅ Successful skill import with custom slug
2. ✅ Successful skill import with auto-generated slug

---

### 1.6 get_skill_handler.py

| Metric | Value |
|--------|-------|
| **Current Coverage** | 55% |
| **Total Lines** | 18 |
| **Missing Lines** | 5 (lines 14-18) |
| **Estimated Gain** | +5 statements |
| **Test Effort** | Low (~20 min) |
| **ROI Score** | ⭐⭐⭐ |

**Missing Logic** (success path):
```python
skill = await skill_repo.get_by_id(skill_id)  # Line 13 (partial)
if not skill:  # Line 14 - NOT taken (covered)
    raise ResourceNotFoundError()
if skill.user_id != user_id:  # Line 16 - NOT taken (covered)
    raise ForbiddenError()
return skill  # Line 18 - SUCCESS PATH NOT COVERED
```

**Test Scenarios Needed**:
1. ✅ Get skill with valid ID and ownership (covers line 18)

---

### 1.7 session.py (db)

| Metric | Value |
|--------|-------|
| **Current Coverage** | 53% |
| **Total Lines** | 44 |
| **Missing Lines** | 8 (lines 36-44) |
| **Estimated Gain** | +8 statements |
| **Test Effort** | Medium (~1 hour) |
| **ROI Score** | ⭐⭐⭐ |

**Missing Logic** (exception handling - lines 40-42):
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()  # Line 39 (covered)
        except Exception:  # Line 40 - NOT COVERED
            await session.rollback()  # Line 41 - NOT COVERED
            raise  # Line 42 - NOT COVERED
        finally:
            await session.close()  # Line 44 (covered)
```

**Test Scenarios Needed**:
1. ✅ Database exception triggers rollback
2. ✅ Verify session is closed even on exception

---

## Priority 2: Medium Gaps (70-90% coverage)

### 2.1 trees.py Router (76% coverage)

| Metric | Value |
|--------|-------|
| **Missing Lines** | ~16 lines |
| **Estimated Gain** | +16 statements |
| **Test Effort** | Medium (~2 hours) |
| **ROI Score** | ⭐⭐⭐⭐ |

**Missing Scenarios**:

| Line | Endpoint | Missing Scenario |
|------|----------|------------------|
| 94-96 | DELETE /files | Path validation error handling |
| 179 | POST /files/batch | Exception in batch upload |
| 193-206 | POST /files/folder | Folder upload edge cases |

**Test Scenarios Needed**:
1. ❌ Delete file without path parameter returns 400
2. ✅ Batch upload with partial failures
3. ✅ Folder upload with nested paths
4. ✅ Folder upload with empty base_path

---

### 2.2 skills.py Router (82% coverage)

| Metric | Value |
|--------|-------|
| **Missing Lines** | ~11 lines |
| **Estimated Gain** | +11 statements |
| **Test Effort** | Low (~1 hour) |
| **ROI Score** | ⭐⭐⭐ |

**Missing Scenarios**:

| Line | Scenario |
|------|----------|
| 91-105 | list_skills response construction edge cases |
| 135-138 | get_skill_files when skill has no tree |

**Test Scenarios Needed**:
1. ✅ List skills with empty result set
2. ✅ Get skill files when skill.tree_id is None

---

### 2.3 auth.py Router (86% coverage)

| Metric | Value |
|--------|-------|
| **Missing Lines** | ~7 lines |
| **Estimated Gain** | +7 statements |
| **Test Effort** | Low (~1 hour) |
| **ROI Score** | ⭐⭐⭐ |

**Missing Scenarios**:

| Line | Endpoint | Missing Scenario |
|------|----------|------------------|
| 37 | /register | Token return path edge case |
| 50, 67, 72 | /login, /refresh | Header parsing edge cases |
| 89, 96, 102 | /me | Token validation edge cases |

**Test Scenarios Needed**:
1. ✅ Refresh without "Bearer " prefix in header
2. ✅ /me endpoint without "Bearer " prefix

---

### 2.4 refresh_token_handler.py (76% coverage)

| Metric | Value |
|--------|-------|
| **Missing Lines** | ~7 lines (lines 30-36) |
| **Estimated Gain** | +7 statements |
| **Test Effort** | Low (~1 hour) |
| **ROI Score** | ⭐⭐⭐ |

**Missing Logic**:
```python
# Lines 30-33: User lookup and active check
user = await user_repo.get_by_id(user_id)
if not user:
    raise ResourceNotFoundError("User not found")
if not user.is_active:
    raise UnauthorizedError("User account is inactive")

# Lines 34-36: Token creation (success path)
new_access_token = create_access_token(data={"sub": str(user_id)})
new_refresh_token = create_refresh_token(data={"sub": str(user_id)})
return user, new_access_token, new_refresh_token
```

**Test Scenarios Needed**:
1. ❌ Refresh with valid token but user not found
2. ❌ Refresh with valid token but user inactive
3. ✅ Successful token refresh (if not covered)

---

### 2.5 blobs.py Router (85% coverage)

| Metric | Value |
|--------|-------|
| **Missing Lines** | ~4 lines |
| **Estimated Gain** | +4 statements |
| **Test Effort** | Low (~30 min) |
| **ROI Score** | ⭐⭐ |

**Missing Scenarios**: Error handling in blob download

---

## Priority 3: Minor Gaps (90-95% coverage)

### 3.1 Factory Edge Cases

| Module | Coverage | Missing | Lines |
|--------|----------|---------|-------|
| skill_factory.py | 86% | 5 | Validation edge cases |
| tree_factory.py | 75% | 7 | _validate_entries method |
| user_factory.py | 86% | 6 | Validation edge cases |

**Test Scenarios Needed**:
1. ❌ SkillFactory with empty name
2. ❌ SkillFactory with name too long
3. ❌ TreeFactory with invalid entry type
4. ❌ TreeFactory with missing blob_id for blob entry
5. ❌ UserFactory with empty username
6. ❌ UserFactory with phone too long

---

### 3.2 config.py (83% coverage)

| Metric | Value |
|--------|-------|
| **Missing Lines** | ~6 lines |
| **Estimated Gain** | +6 statements |

**Missing Scenarios**:
1. ALLOWED_ORIGINS parsing from comma-separated string
2. SECRET_KEY validation edge cases

---

### 3.3 Handlers at 95%+

| Module | Coverage | Missing |
|--------|----------|---------|
| register_user_handler.py | 95% | 1 line |
| delete_skill_handler.py | 95% | 1 line |

*These are diminishing returns - only 2 statements combined*

---

## Prioritized Implementation Plan

### Phase 1: Quick Wins (+65 statements) 🎯
**Estimated Time: 4-5 hours**
**Coverage Gain: 89.62% → 92.8%**

| Order | Module | Lines | Tests | Effort |
|-------|--------|-------|-------|--------|
| 1 | update_tree_handler.py | 15 | 3 | 1h |
| 2 | login_handler.py | 9 | 1 | 0.5h |
| 3 | create_skill_handler.py | 9 | 1 | 0.5h |
| 4 | import_skill_handler.py | 9 | 2 | 0.5h |
| 5 | get_skill_handler.py | 5 | 1 | 0.5h |
| 6 | update_tree_file_content_handler.py | 13 | 4 | 1h |
| 7 | session.py | 8 | 2 | 1h |
| **Subtotal** | | **68** | **14** | **5h** |

### Phase 2: Router Error Paths (+38 statements) 🎯
**Estimated Time: 4-5 hours**
**Coverage Gain: 92.8% → 94.7%**

| Order | Module | Lines | Tests | Effort |
|-------|--------|-------|-------|--------|
| 8 | trees.py router | 16 | 4 | 2h |
| 9 | skills.py router | 11 | 2 | 1h |
| 10 | auth.py router | 7 | 2 | 1h |
| 11 | refresh_token_handler.py | 7 | 3 | 1h |
| 12 | blobs.py router | 4 | 1 | 0.5h |
| **Subtotal** | | **45** | **12** | **5.5h** |

### Phase 3: Factory Edge Cases (+18 statements) 🎯
**Estimated Time: 2-3 hours**
**Coverage Gain: 94.7% → 95.6%**

| Order | Module | Lines | Tests | Effort |
|-------|--------|-------|-------|--------|
| 13 | tree_factory.py | 7 | 4 | 1h |
| 14 | skill_factory.py | 5 | 3 | 0.5h |
| 15 | user_factory.py | 6 | 3 | 0.5h |
| 16 | config.py | 6 | 2 | 1h |
| **Subtotal** | | **24** | **12** | **3h** |

---

## ROI Summary by Phase

```
Phase 1: 68 lines / 5 hours = 13.6 lines/hour ⭐⭐⭐⭐⭐
Phase 2: 45 lines / 5.5 hours = 8.2 lines/hour ⭐⭐⭐⭐
Phase 3: 24 lines / 3 hours = 8.0 lines/hour ⭐⭐⭐

Total: 137 potential lines / 13.5 hours = 10.1 lines/hour
```

**Recommendation**: Execute Phase 1 + Phase 2 for a total of:
- **~113 statements covered** (exceeds 107 needed)
- **~10 hours effort**
- **Final coverage: ~95.2%** (exceeds 95% target)

Skip Phase 3 unless perfection is required (diminishing returns).

---

## Risk Assessment

| Risk | Impact | Mitigation |
|------|--------|------------|
| Test flakiness in session.py | Low | Use transaction rollback |
| Integration test complexity | Medium | Use existing test fixtures |
| Router error path testing | Low | Use FastAPI TestClient |

---

## Conclusion

The path to 95% coverage is clear and achievable:

1. **Phase 1 (Quick Wins)**: 7 modules, 14 tests, 5 hours → 92.8%
2. **Phase 2 (Routers)**: 5 modules, 12 tests, 5.5 hours → 95.2%

**Total: 26 tests, ~10-11 hours to reach 95%+ coverage**

The key insight is that **success paths are the main gap** - failure paths are well-covered across all handlers. This is actually a healthy test distribution (security-focused), but filling in the success paths will push coverage to the target.

---

*Report generated by Sisyphus - Coverage Gap Analysis*  
*Date: 2026-02-20*
