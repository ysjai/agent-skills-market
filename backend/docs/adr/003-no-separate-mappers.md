# ADR-003: Mapping Methods in ORM Models (No Separate Mappers)

## Status
Accepted

## Context
We needed to map between domain objects (rich models) and persistence objects (ORM models). Options included:
1. Separate mapper classes
2. Mapping methods inside ORM models
3. Mapping logic in repositories

## Decision
We chose to put `to_domain()` and `from_domain()` methods directly on ORM model classes.

- Each ORM model knows how to convert itself to/from domain objects
- No separate mapper classes needed
- Mapping logic stays with the data structure it transforms

## Consequences

**Positive:**
- Less indirection and fewer files
- Mapping logic is co-located with the model it transforms
- Simpler to understand and maintain

**Negative:**
- ORM models have knowledge of domain models (coupling)
- Cannot change persistence layer without modifying ORM models

## Alternatives Considered

1. **Separate mapper classes**: Rejected as YAGNI
   ```python
   class SkillMapper:
       def to_domain(self, model): ...
       def to_model(self, domain): ...
   ```

2. **Mapping in repository**: Rejected, clutters repository with conversion logic

## References
- See [backend/project_conventions.md](../../project_conventions.md) Chapter 5
