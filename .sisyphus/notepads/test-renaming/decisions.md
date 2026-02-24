# Test Method Renaming - Decisions

## Decision 1: Keep Scenario Test Names

**Decision**: Do NOT rename scenario tests (e.g., `test_scenario_1_import_skill_files_fully_accessible`).

**Rationale**: 
- Scenario tests already have descriptive names following a scenario-based pattern
- They represent business scenarios, not unit test cases
- Renaming would make them less readable
- The format `test_scenario_X_descriptive_name` is a valid naming convention for journey tests

## Decision 2: Use `should_*` Naming Pattern

**Decision**: Use `should_[result]_when_[action]_given_[condition]` format.

**Rationale**:
- Clearly communicates expected behavior
- Follows BDD-style naming conventions
- Makes test purpose immediately clear from the name
- Supports natural language reading: "Should return 201 when create skill given valid input"

## Decision 3: Update Pytest Configuration

**Decision**: Update `pyproject.toml` to recognize both `test_*` and `should_*` patterns.

**Rationale**:
- Maintains backward compatibility with any existing `test_*` functions
- Allows gradual migration if needed
- No risk of breaking existing test discovery

## Decision 4: Use Consistent Verb Tense

**Decision**: Use present tense for all action descriptions.

**Examples**:
- `when_create_skill` (not `when_creating_skill`)
- `when_delete_file` (not `when_deleting_file`)
- `when_upload_blob` (not `when_uploading_blob`)

**Rationale**:
- More direct and readable
- Consistent across all test names
- Aligns with BDD style

## Decision 5: Handle Special Cases

### Async Tests
- Keep `@pytest.mark.asyncio` decorator
- Method signature: `async def should_xxx_when_xxx_given_xxx(self, ...)`

### Class-based Tests
- Keep class name pattern: `Test*` (e.g., `TestCreateSkill`)
- Only rename the test methods

### Fixtures
- Do not rename fixtures (e.g., `test_user`, `auth_client`)
- Only rename test methods
