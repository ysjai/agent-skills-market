# Test Method Renaming - Learnings

## Naming Convention Pattern

Format: `should_[result]_when_[action]_given_[condition]`

- **should_xxx**: Expected result/outcome (e.g., `should_return_201`, `should_delete_blob`, `should_preserve_content`)
- **when_xxx**: The action being performed (e.g., `when_create_skill`, `when_upload_blob`, `when_delete_file`)
- **given_xxx**: The condition/context (e.g., `given_valid_input`, `given_no_auth`, `given_shared_blob`)

## Transformation Examples

### Auth Tests
- `test_register_success` → `should_return_tokens_when_register_given_valid_input`
- `test_register_duplicate_email` → `should_return_409_when_register_given_duplicate_email`
- `test_login_success` → `should_return_tokens_when_login_given_valid_credentials`
- `test_login_invalid_password` → `should_return_401_when_login_given_invalid_password`

### Skill Tests
- `test_create_skill_success` → `should_return_201_when_create_skill_given_valid_input`
- `test_create_skill_unauthenticated` → `should_return_401_when_create_skill_given_no_auth`
- `test_get_skill_success` → `should_return_skill_when_get_skill_given_valid_id`
- `test_get_skill_not_found` → `should_return_404_when_get_skill_given_nonexistent_id`
- `test_delete_own_skill_success` → `should_delete_skill_when_delete_own_skill_given_owner`
- `test_delete_others_skill_forbidden` → `should_return_403_when_delete_skill_given_not_owner`

### Blob Tests
- `test_upload_text_blob_success` → `should_return_201_when_upload_blob_given_text_content`
- `test_download_blob_success` → `should_return_content_when_download_blob_given_valid_id`
- `test_upload_duplicate_content` → `should_return_same_id_when_upload_duplicate_content`

### Tree Tests
- `test_create_tree_success` → `should_return_201_when_create_tree_given_valid_input`
- `test_add_text_file` → `should_add_text_file_when_add_file_given_valid_path`
- `test_delete_file_success` → `should_delete_file_when_delete_file_given_valid_path`

### Journey Tests
- `test_download_flow` → `should_download_all_files_when_import_skill_given_multiple_files`
- `test_file_operations_flow` → `should_complete_file_operations_when_manage_tree`

### Logging Tests
- `test_filter_password` → `should_redact_password_when_filter_given_password_in_message`
- `test_setup_logging_configures_root_logger` → `should_configure_root_logger_when_setup_logging_called`

## Key Patterns for Naming

1. **HTTP Status Codes**: Use `should_return_xxx` when testing API responses
2. **Actions**: Use clear verb phrases like `when_create_skill`, `when_delete_file`
3. **Conditions**: Use `given_` prefix for context:
   - `given_valid_input`, `given_valid_id`
   - `given_no_auth`, `given_not_owner`
   - `given_nonexistent_id`, `given_duplicate_email`
   - `given_shared_blob`, `given_empty_skill`

4. **Results**: Be specific about outcomes:
   - `should_return_201`, `should_return_404`
   - `should_delete_skill`, `should_preserve_content`
   - `should_redact_password`, `should_mask_email`

## Scenario Tests

Keep scenario test names as they are (e.g., `test_scenario_1_import_skill_files_fully_accessible`) - they already have good descriptive names that follow a scenario-based pattern.

## Pytest Configuration Update

When renaming test methods from `test_*` to `should_*`, update `pyproject.toml`:

```toml
[tool.pytest.ini_options]
python_functions = ["test_*", "should_*"]
```

This ensures pytest recognizes both naming patterns.
