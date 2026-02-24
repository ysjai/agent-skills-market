# ADR-001: Simplified DDD (No Domain Events, CQRS, or Event Sourcing)

## Status
Accepted

## Context
The project required Domain-Driven Design (DDD) patterns to improve code organization and business logic encapsulation. However, we needed to balance architectural purity with practical maintainability for a small to medium-sized team.

## Decision
We chose a simplified DDD approach that focuses on:
- Layered architecture with clear boundaries (api / application / domain / infra)
- Rich domain models with encapsulated business logic
- Value objects for type safety and validation
- Repository pattern for persistence abstraction

We deliberately excluded:
- Domain events (event publishing/subscribing)
- CQRS (Command Query Responsibility Segregation)
- Event sourcing
- Complex bounded context mapping

## Consequences

**Positive:**
- Shorter learning curve for new team members
- Less boilerplate and infrastructure code
- Faster development cycles
- Easier to debug and test

**Negative:**
- Reduced decoupling between domain changes and side effects
- Less flexibility for read model optimization
- May require refactoring if system complexity grows significantly

## Alternatives Considered

1. **Full DDD with Events/CQRS**: Rejected as overkill for current scope
2. **Anemic domain models with service layer**: Rejected, contradicts DDD principles
3. **Event sourcing**: Rejected, adds unnecessary complexity

## References
- See [backend/project_conventions.md](../../project_conventions.md) for implementation details
