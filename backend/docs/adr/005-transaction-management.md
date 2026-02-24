# ADR-005: Transaction Management via get_db()

## Status
Accepted

## Context
We needed a transaction strategy that:
- Works with async SQLAlchemy
- Supports repository pattern
- Handles commit/rollback consistently
- Works with FastAPI dependency injection

## Decision
We use the existing `get_db()` dependency for transaction management.

- One request = one transaction
- `get_db()` yields a session, auto-commits on success, auto-rollback on exception
- Repositories call `session.add()` only, never `commit()`
- Explicit transaction control available when needed for complex cases

## Consequences

**Positive:**
- Simple, works with FastAPI's Depends pattern
- No transaction logic in handlers or repositories
- Automatic rollback on errors

**Negative:**
- Less control over transaction boundaries
- Complex multi-step transactions require explicit handling
- Cannot commit partial results within a request

## Alternatives Considered

1. **Unit of Work pattern**: Initially planned but simplified for current needs
   ```python
   async with unit_of_work() as uow:
       uow.skills.add(skill)
       await uow.commit()
   ```

2. **Explicit transaction decorators**: Rejected, adds complexity

## References
- See [backend/project_conventions.md](../../project_conventions.md) Chapter 9
