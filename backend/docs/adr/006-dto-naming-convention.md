# ADR-006: Per-Use-Case DTO Naming Convention

## Status
Accepted

## Context
We needed consistent naming for request/response DTOs across API endpoints. Options included generic DTOs with optional fields or specific DTOs per use case.

## Decision
We chose explicit, per-use-case DTO naming:

- Non-list: `{Action}{Resource}Req` / `{Action}{Resource}Resp`
  - Examples: `CreateSkillReq`, `UpdateSkillResp`
- List items: `List{Resources}ItemResp`
  - Example: `ListSkillsItemResp`

Each use case gets its own DTO types, even if fields are similar.

## Consequences

**Positive:**
- Explicit and clear intent
- Each DTO documents the exact contract for that use case
- Easy to modify one use case without affecting others
- Self-documenting API contracts

**Negative:**
- More DTO classes to maintain
- Some field duplication across similar DTOs

## Alternatives Considered

1. **Generic DTOs with Optional fields**: Rejected for lack of clarity
   ```python
   class SkillRequest(BaseModel):
       name: Optional[str] = None  # Used for create and update
       description: Optional[str] = None
   ```

2. **Single DTO per resource**: Rejected, fields differ between use cases

## References
- See [backend/project_conventions.md](../../project_conventions.md) Chapter 7
