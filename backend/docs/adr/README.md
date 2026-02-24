# Architecture Decision Records (ADRs)

This directory contains Architecture Decision Records documenting key decisions made during the DDD refactoring of the Agent Skills Manager backend.

## What are ADRs?

ADRs capture important architectural decisions, the context in which they were made, and the consequences of those decisions. They provide a historical record for future developers to understand why the codebase is structured as it is.

## Index

| ADR | Title | Description |
|-----|-------|-------------|
| [ADR-001](001-simplified-ddd.md) | Simplified DDD | Chose simplified DDD without domain events, CQRS, or event sourcing |
| [ADR-002](002-function-based-handlers.md) | Function-Based Application Layer | Use functions instead of classes for handlers |
| [ADR-003](003-no-separate-mappers.md) | No Separate Mappers | Mapping methods in ORM models instead of separate mapper classes |
| [ADR-004](004-exception-design.md) | Simplified Exception Design | Single DomainError base class with category attribute |
| [ADR-005](005-transaction-management.md) | Transaction Management | Using get_db() for request-scoped transactions |
| [ADR-006](006-dto-naming-convention.md) | DTO Naming Convention | Per-use-case DTO naming patterns |

## Format

Each ADR follows this structure:
- **Status**: Current status (Accepted, Deprecated, Superseded)
- **Context**: The problem or situation requiring a decision
- **Decision**: What was decided
- **Consequences**: Trade-offs and outcomes
- **Alternatives Considered**: Other options that were evaluated

## References

- [Project Conventions](../../project_conventions.md) - Implementation details and coding standards
- [DDD Guide](../architecture/ddd-guide.md) - Domain-Driven Design tutorials
