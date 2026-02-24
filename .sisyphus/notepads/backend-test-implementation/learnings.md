

## Tree Handlers Integration Tests - Implementation Learnings

### Date: 2026-02-20

### Coverage Improvements

| Handler | Before | After | Improvement |
|---------|--------|-------|-------------|
| add_tree_file_handler.py | 38% | 100% | +62% |
| delete_tree_file_handler.py | 40% | 100% | +60% |
| delete_tree_handler.py | 0% | 100% | +100% |
| list_skill_files_handler.py | 0% | 100% | +100% |

### Test Scenarios Implemented

**add_tree_file_handler (4 scenarios):**
1. 使用 blob_id 添加文件 → 添加条目，递增引用计数
2. 使用 content 添加文件 → 创建新 Blob，添加条目
3. 相同 content 已存在 → 复用现有 Blob，递增引用计数
4. Tree 不存在 → 抛出 ResourceNotFoundError

**delete_tree_file_handler (5 scenarios):**
1. 删除普通文件 → 删除条目，递减引用计数
2. 尝试删除 SKILL.md → 抛出 ValidationError
3. 删除目录 → 级联删除，返回所有 blob_ids
4. Blob 引用计数归零 → 调用 blob_repo.delete
5. Tree 不存在 → 抛出 ResourceNotFoundError

**delete_tree_handler (2 scenarios):**
1. 删除存在的 Tree → 调用 tree_repo.delete
2. 删除不存在的 Tree → 抛出 ResourceNotFoundError

**list_skill_files_handler (5 scenarios):**
1. Skill 不存在 → 抛出 ResourceNotFoundError
2. Skill 属于其他用户 → 抛出 ResourceNotFoundError
3. Skill 无 tree_id → 返回 (skill, [])
4. 成功获取文件列表 → 返回 (skill, tree.entries)
5. tree_id 对应的 Tree 不存在 → 返回 (skill, [])

### Key Implementation Patterns

1. **Path Value Object**: TreeEntry.path is a Path value object, not string.
   Always use `str(entry.path)` for string comparisons.

2. **Blob Reference Count Management**:
   - Add file: increment_reference_count(blob_id) after adding entry
   - Delete file: decrement_reference_count(blob_id), if returns True, delete blob
   - Set explicit reference_count in test fixtures for predictable testing

3. **Content-based Blob Creation**: When adding file with content:
   - Calculate SHA256 hash
   - Check if blob with same checksum exists via blob_repo.get_by_checksum()
   - Reuse existing blob if found, else create new one

4. **Cascade Delete Logic**: Tree.delete_entry() returns list of blob_ids for deleted entries.
   Directory deletion uses path prefix matching to find all child entries.

5. **SKILL.md Protection**: Normalized path check prevents deletion:
   ```python
   if normalized_path == "SKILL.md":
       raise ValidationError("Cannot delete SKILL.md file")
   ```

6. **Skill Permission Check**: list_skill_files_handler checks both:
   - Skill existence: `if not skill`
   - User ownership: `if skill.user_id != user_id`
   Both raise ResourceNotFoundError (no information leak)

7. **Missing Tree Handling**: list_skill_files_handler handles edge case where
   skill.tree_id exists but Tree was deleted (returns empty list, not error).

### Repository Dependencies

- add_tree_file_handler: TreeRepository, BlobRepository
- delete_tree_file_handler: TreeRepository, BlobRepository
- delete_tree_handler: TreeRepository
- list_skill_files_handler: SkillRepository, TreeRepository

### Fixture Design

- `test_tree_empty`: Empty tree for add operations
- `test_tree_with_entries`: Tree with SKILL.md and regular file
- `test_tree_with_directory`: Tree with nested directory structure
- `test_skill_no_tree`: Skill without tree association
- `test_skill_with_tree`: Skill with tree association
- `test_blob`: Blob for entry references

### File Structure
- Test file: backend/tests/integration/handlers/test_tree_handlers.py
- 16 tests total, all passing
- Coverage: 100% across all four handlers

---

## Download Handler, User Aggregate, Blob Entity - Implementation Learnings

### Date: 2026-02-20

### Coverage Improvements

| Module | Before | After | Improvement |
|--------|--------|-------|-------------|
| download_skill_handler.py | 48% | 100% | +52% |
| user.py | 49% | 100% | +51% |
| blob.py | 61% | 97% | +36% |

### Test Scenarios Implemented

**download_skill_handler (11 scenarios):**
1. 无权下载他人 Skill → ForbiddenError
2. 下载不存在的 Skill → ResourceNotFoundError
3. Skill 无 Tree (claude 格式) → 返回空 markdown
4. Skill 无 Tree (zip 格式) → 返回空 zip
5. Skill 无 Tree (默认平台) → 返回空 zip
6. Claude 格式下载 → 返回 markdown 内容（含代码块格式）
7. OpenCode 格式下载 → 返回 zip 内容
8. Skill 有 tree_id 但 Tree 不存在 → ResourceNotFoundError
9. Blob 不存在时跳过 → 继续处理其他文件
10. Tree 包含目录 → 只导出文件（目录条目被过滤）
11. 压缩的 Blob → 自动解压后导出

**User Aggregate (26 scenarios):**
- verify_email: 首次验证、重复验证
- deactivate/activate: 状态切换、重复操作
- change_password: 正常更新、空值错误
- update_profile: 更新 username（含空白处理）、更新 phone、空值错误
- is_authenticated: 四种状态组合（is_active × email_verified）
- User creation: 默认构造、自定义值
- Complete workflow: 完整用户生命周期

**Blob Entity (38 scenarios):**
- __post_init__: size 计算、checksum 计算、保留已提供值
- create: 正常创建、空内容错误
- compress/decompress: 正常压缩解压、已压缩/未压缩时直接返回
- get_raw_content: 未压缩、压缩、解压失败回退
- Reference count: 递增、递减、最小值为0
- Orphan status: reference_count == 0
- Empty status: 内容为空检查
- Content preview: 文本预览、二进制预览、压缩内容预览
- validate_content: 有效、空内容、损坏内容
- _calculate_hash: SHA256 计算
- Complete lifecycle: 完整 Blob 生命周期

### Key Implementation Patterns

1. **Bytes vs String Handling**:
   - Bytes literals cannot contain non-ASCII: use `"...".encode("utf-8")`
   - Blob content is always bytes
   - Markdown content is UTF-8 encoded bytes

2. **Compression Testing**:
   - Small strings may NOT compress (zlib overhead)
   - Use repetitive content (e.g., `b"A" * 1000`) to ensure compression works
   - Compressed size assertion: `assert blob.size < original_size`

3. **Zip File Testing**:
   - Use `io.BytesIO` and `zipfile.ZipFile` for in-memory zip validation
   - Verify both file list and file contents
   - Example:
   ```python
   buffer = BytesIO(content_bytes)
   with zipfile.ZipFile(buffer, "r") as zf:
       assert "filename" in zf.namelist()
       assert zf.read("filename") == b"content"
   ```

4. **Directory Entry Filtering**:
   - Tree entries with `entry_type == "tree"` are directories
   - Download only includes `entry.is_file()` entries
   - Path matching with regex to distinguish directory from file path

5. **User Default Email Issue**:
   - User default email `Email("placeholder@invalid")` is invalid
   - TLD must be at least 2 chars per Email regex: `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$`
   - Test with valid email: `User(email=Email("test@example.com"))`

6. **Blob Checksum Calculation**:
   - Checksum calculated from `get_raw_content()` (decompressed if needed)
   - SHA256 hex digest: `hashlib.sha256(content).hexdigest()`
   - Preserves provided checksum in `__post_init__` if already set

7. **Handler Error Handling**:
   - Permission check: `if skill.user_id != user_id: raise ForbiddenError`
   - Not found: `if skill is None: raise ResourceNotFoundError`
   - Tree missing: `if tree is None: raise ResourceNotFoundError`

### Repository Dependencies

- download_skill_handler: SkillRepository, TreeRepository, BlobRepository
- User aggregate: No dependencies (pure domain logic)
- Blob entity: No dependencies (pure domain logic)

### File Structure

```
backend/tests/
├── integration/handlers/
│   └── test_download_handler.py (11 tests)
├── unit/domain/aggregates/
│   └── test_user.py (26 tests)
└── unit/domain/entities/
    └── test_blob.py (38 tests)
```

Total: 75 new tests, all passing
Overall coverage: 99% (168 statements, 2 missing - defensive error handling)
