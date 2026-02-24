# ADR-002: Function-Based Application Layer

## Status
Accepted

## Context
The application layer coordinates use cases by orchestrating domain objects and repositories. We needed to decide between class-based handlers (Handler.handle()) or function-based handlers (handle_action()).

## Decision
We chose function-based handlers over class-based handlers.

- Each use case is a standalone async function
- No shared state between handlers
- Dependencies passed as explicit parameters
- Repository injected via parameter, not constructor

Example naming: `handle_create_skill()`, `handle_update_skill()`

## Consequences

**Positive:**
- Simpler, flatter code structure
- Easier to unit test (pure functions with mockable dependencies)
- Less boilerplate (no class definitions, constructors, instance variables)
- Clear data flow (inputs and outputs are explicit)

**Negative:**
- Handler dependencies must be passed on every call
- Less structure for cross-cutting concerns (logging, metrics)

## Alternatives Considered

1. **Class-based handlers**: Rejected for unnecessary complexity
   ```python
   class CreateSkillHandler:
       def __init__(self, repo): self.repo = repo
       async def handle(self, cmd): ...
   ```

2. **Command objects with generic handler**: Rejected, too abstract for current needs

## References
- See [backend/project_conventions.md](../../project_conventions.md) Chapter 6
