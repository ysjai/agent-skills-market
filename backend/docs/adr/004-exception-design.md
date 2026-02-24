# ADR-004: Simplified Exception Design

## Status
Accepted

## Context
We needed a consistent exception strategy that:
- Keeps domain layer HTTP-agnostic
- Provides clear error classification
- Enables consistent API responses

## Decision
We chose a single `DomainError` base class with a `category` attribute.

- One exception hierarchy, not multiple
- Domain exceptions know their business category (NOT_FOUND, CONFLICT, etc.)
- API layer maps categories to HTTP status codes via `CATEGORY_STATUS_MAP`
- No HTTP status codes in domain layer

## Consequences

**Positive:**
- Domain layer remains clean of HTTP concerns
- Easy to add new exception types
- Global exception handler provides consistent API responses
- Flat, simple exception hierarchy

**Negative:**
- Category-based mapping is less flexible than status code per exception
- Need to maintain the category-to-status mapping separately

## Alternatives Considered

1. **Multiple exception hierarchies** (DomainError, ValidationError, NotFoundError): Rejected for complexity
2. **HTTP status codes in exceptions**: Rejected, violates layered architecture
3. **Exception per HTTP status**: Rejected, mixes HTTP concerns with domain

## References
- See [backend/project_conventions.md](../../project_conventions.md) Chapter 8
