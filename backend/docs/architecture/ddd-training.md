# DDD Training Guide

Practical guide to Domain-Driven Design patterns used in this project.

---

## 1. DDD Overview

Domain-Driven Design aligns code structure with business domain concepts.

### Why DDD?

- **Business Logic Lives in One Place**: Domain rules are encapsulated in domain objects
- **Testable**: Domain objects have no external dependencies
- **Ubiquitous Language**: Developers and domain experts use the same terminology

### Simplified DDD

This project uses a streamlined approach without domain events, CQRS, or event sourcing.

---

## 2. Layered Architecture

### The Four Layers

```
API Layer → Application Layer → Domain Layer ← Infrastructure Layer
```

Dependency rules: API depends on Application, Application depends on Domain, Infrastructure implements Domain interfaces.

### Critical Constraints

```python
# NEVER in domain layer:
from fastapi import APIRouter  # ❌ Domain knows nothing about HTTP
from sqlalchemy import Column  # ❌ Domain knows nothing about ORM
from pydantic import BaseModel # ❌ Domain knows nothing about serialization
```

---

## 3. Value Objects

Immutable data structures defined by attributes, not identity.

### Slug Value Object

```python
from dataclasses import dataclass
import re

@dataclass(frozen=True)
class Slug:
    value: str
    _VALID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    _MAX_LENGTH = 128

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @classmethod
    def _validate(cls, value: str) -> str:
        if not value: raise ValidationError("Slug cannot be empty")
        if len(value) > cls._MAX_LENGTH: raise ValidationError(f"Slug too long")
        if not cls._VALID_PATTERN.match(value): raise ValidationError("Invalid slug format")
        return value.lower()

    @classmethod
    def from_name(cls, name: str) -> Slug:
        slug = name.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        if not slug: raise ValidationError("Cannot generate slug from empty name")
        return cls(slug)

    def __str__(self) -> str: return self.value
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Slug): return NotImplemented
        return self.value == other.value
    def __hash__(self) -> int: return hash(self.value)
```

### Email Value Object

```python
@dataclass(frozen=True)
class Email:
    value: str
    _VALID_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    _MAX_LENGTH = 255

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", self._validate(self.value))

    @classmethod
    def _validate(cls, value: str) -> str:
        if not value: raise ValidationError("Email cannot be empty")
        normalized = value.strip().lower()
        if len(normalized) > cls._MAX_LENGTH: raise ValidationError("Email too long")
        if not cls._VALID_PATTERN.match(normalized): raise ValidationError("Invalid email")
        return normalized
```

---

## 4. Entities & Aggregates

Entities have identity that persists across state changes.

### Skill Aggregate

```python
from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4

@dataclass
class Skill:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default_factory=uuid4)
    name: str = ""
    slug: Slug = field(default_factory=lambda: Slug(""))
    description: str | None = None
    tree_id: UUID | None = None
    is_public: bool = False
    version: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def update_name(self, new_name: str) -> None:
        if not new_name or not new_name.strip(): raise ValueError("Skill name cannot be empty")
        self.name = new_name.strip()
        self.slug = Slug.from_name(self.name)
        self._touch()

    def update_description(self, description: str | None) -> None:
        self.description = description
        self._touch()

    def set_public(self, is_public: bool) -> None:
        self.is_public = is_public
        self._touch()

    def assign_tree(self, tree_id: UUID | None) -> None:
        self.tree_id = tree_id
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1
```

### User Aggregate

```python
@dataclass
class User:
    id: UUID = field(default_factory=uuid4)
    email: Email = field(default_factory=lambda: Email("placeholder@invalid"))
    username: str = ""
    password_hash: str = ""
    is_active: bool = True
    email_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def verify_email(self) -> None:
        if self.email_verified: return
        self.email_verified = True
        self._touch()

    def deactivate(self) -> None:
        if not self.is_active: return
        self.is_active = False
        self._touch()

    def activate(self) -> None:
        if self.is_active: return
        self.is_active = True
        self._touch()

    def change_password(self, new_password_hash: str) -> None:
        if not new_password_hash: raise ValueError("Password hash cannot be empty")
        self.password_hash = new_password_hash
        self._touch()

    def is_authenticated(self) -> bool:
        return self.is_active and self.email_verified

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
```

### Tree Aggregate with Child Entities

```python
@dataclass
class TreeEntry:
    path: Path
    entry_type: str
    blob_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.entry_type not in ("blob", "tree"): raise ValidationError("Invalid entry type")
        if self.entry_type == "blob" and self.blob_id is None: raise ValidationError("Blob needs blob_id")

    def is_file(self) -> bool: return self.entry_type == "blob"


@dataclass
class Tree:
    id: UUID = field(default_factory=uuid4)
    entries: list[TreeEntry] = field(default_factory=list)

    def add_entry(self, path: str, entry_type: str, blob_id: UUID | None = None) -> None:
        validated_path = Path(path)
        if self._find_entry_by_path(str(validated_path)): raise ResourceConflictError("Entry exists")
        self.entries.append(TreeEntry(path=validated_path, entry_type=entry_type, blob_id=blob_id))

    def delete_entry(self, path: str) -> list[UUID]:
        normalized_path = str(Path(path)).rstrip("/")
        path_prefix = normalized_path + "/"
        entries_to_delete = [e for e in self.entries if str(e.path).rstrip("/") == normalized_path or str(e.path).startswith(path_prefix)]
        if not entries_to_delete: raise ResourceNotFoundError(f"Entry '{path}' not found")
        blob_ids = [e.blob_id for e in entries_to_delete if e.blob_id]
        deleted = {str(e.path).rstrip("/") for e in entries_to_delete}
        self.entries = [e for e in self.entries if str(e.path).rstrip("/") not in deleted]
        return blob_ids
```

---

## 5. Domain Services

Use domain services when logic spans multiple aggregates or involves complex calculations. Most logic fits within aggregates. Use sparingly.

---

## 6. Repositories

Repositories abstract persistence. Domain defines interfaces, infrastructure implements them.

### Repository Interface

```python
from abc import ABC, abstractmethod
from uuid import UUID

class SkillRepository(ABC):
    @abstractmethod
    async def get_by_id(self, skill_id: UUID) -> Skill | None: ...

    @abstractmethod
    async def get_by_slug(self, slug: Slug, user_id: UUID) -> Skill | None: ...

    @abstractmethod
    async def find_by_user(self, user_id: UUID, offset: int = 0, limit: int = 20) -> list[Skill]: ...

    @abstractmethod
    async def save(self, skill: Skill) -> None: ...

    @abstractmethod
    async def delete(self, skill_id: UUID) -> None: ...
```

### SQL Implementation

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

class SqlSkillRepository(SkillRepository):
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, skill_id: UUID) -> Skill | None:
        result = await self._db.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_slug(self, slug: Slug, user_id: UUID) -> Skill | None:
        result = await self._db.execute(select(SkillModel).where(SkillModel.slug == str(slug), SkillModel.user_id == user_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def find_by_user(self, user_id: UUID, offset: int = 0, limit: int = 20) -> list[Skill]:
        result = await self._db.execute(select(SkillModel).where(SkillModel.user_id == user_id).order_by(SkillModel.created_at.desc()).offset(offset).limit(limit))
        return [model.to_domain() for model in result.scalars().all()]

    async def save(self, skill: Skill) -> None:
        await self._db.merge(SkillModel.from_domain(skill))

    async def delete(self, skill_id: UUID) -> None:
        result = await self._db.execute(select(SkillModel).where(SkillModel.id == skill_id))
        model = result.scalar_one_or_none()
        if model: await self._db.delete(model)
```

### ORM Model with Mapping

```python
class SkillModel(Base):
    __tablename__ = "skills"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    tree_id: Mapped[UUID | None] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("trees.id"), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=text("NOW()"), onupdate=text("NOW()"))

    def to_domain(self) -> Skill:
        from src.domain.aggregates.skill import Skill
        from src.domain.value_objects.slug import Slug
        return Skill(id=self.id, user_id=self.user_id, name=self.name, slug=Slug(self.slug), description=self.description, tree_id=self.tree_id, version=self.version, is_public=self.is_public, created_at=self.created_at, updated_at=self.updated_at)

    @classmethod
    def from_domain(cls, skill: Skill) -> SkillModel:
        return cls(id=skill.id, user_id=skill.user_id, name=skill.name, slug=str(skill.slug), description=skill.description, tree_id=skill.tree_id, version=skill.version, is_public=skill.is_public, created_at=skill.created_at, updated_at=skill.updated_at)
```

### Dependency Injection

```python
async def get_skill_repo(db: AsyncSession = Depends(get_db)) -> SkillRepository:
    return SqlSkillRepository(db)

@router.post("")
async def create_skill(request: CreateSkillReq, skill_repo: SkillRepository = Depends(get_skill_repo)) -> CreateSkillResp: ...
```

---

## 7. Application Layer

Orchestrates use cases. Contains no business logic, only coordination.

### Handler Functions

```python
async def handle_create_skill(user_id: UUID, name: str, description: str | None, skill_repo: SkillRepository) -> Skill:
    slug = Slug.from_name(name)
    existing = await skill_repo.get_by_slug(slug, user_id)
    if existing: raise ResourceConflictError()
    skill = SkillFactory.create(user_id=user_id, name=name, description=description)
    await skill_repo.save(skill)
    return skill
```

```python
async def handle_update_skill(skill_id: UUID, user_id: UUID, name: str | None, description: str | None, is_public: bool | None, tree_id: UUID | None, skill_repo: SkillRepository) -> Skill:
    skill = await skill_repo.get_by_id(skill_id)
    if not skill or skill.user_id != user_id: raise ResourceNotFoundError()
    if name is not None:
        new_slug = Slug.from_name(name)
        existing = await skill_repo.get_by_slug(new_slug, user_id)
        if existing and existing.id != skill_id: raise ResourceConflictError()
        skill.update_name(name)
    if description is not None: skill.update_description(description)
    if is_public is not None: skill.set_public(is_public)
    if tree_id is not None: skill.assign_tree(tree_id)
    await skill_repo.save(skill)
    return skill
```

### Transaction Management

```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
```

---

## 8. Factory Pattern

```python
class SkillFactory:
    _MAX_NAME_LENGTH = 128

    @classmethod
    def create(cls, user_id: UUID, name: str, description: str | None = None) -> Skill:
        validated_name = cls._validate_name(name)
        now = datetime.now(timezone.utc)
        return Skill(id=uuid4(), user_id=user_id, name=validated_name, slug=Slug.from_name(validated_name), description=description or "", version=1, created_at=now, updated_at=now, is_public=False)

    @classmethod
    def _validate_name(cls, name: str) -> str:
        if not name or not name.strip(): raise ValidationError("Skill name cannot be empty")
        if len(name.strip()) > cls._MAX_NAME_LENGTH: raise ValidationError(f"Skill name too long")
        return name.strip()
```

---

## 9. Common Patterns

### Exception Hierarchy

```python
class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    message: str = "Domain error occurred"
    category: str = "BUSINESS"

    def __init__(self, message: str | None = None):
        self.message = message or self.message
        super().__init__(self.message)

class ValidationError(DomainError):
    code = "VALIDATION_ERROR"
    category = "VALIDATION"

class ResourceNotFoundError(DomainError):
    code = "RESOURCE_NOT_FOUND"
    category = "NOT_FOUND"

class ResourceConflictError(DomainError):
    code = "RESOURCE_CONFLICT"
    category = "CONFLICT"
```

### API Response Mapping

```python
class CreateSkillResp(BaseModel):
    id: UUID
    name: str
    slug: str
    description: str | None
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, skill: Skill) -> CreateSkillResp:
        return cls(id=skill.id, name=skill.name, slug=str(skill.slug), description=skill.description, version=skill.version, created_at=skill.created_at, updated_at=skill.updated_at)
```

---

## 10. Anti-patterns

### Anemic Domain Model

```python
# ❌ BAD: Entity is just a data bag
@dataclass
class Skill:
    id: UUID
    name: str
    version: int

class SkillService:
    def update_skill(self, skill: Skill, new_name: str) -> None:
        skill.name = new_name
        skill.version += 1

# ✅ GOOD: Entity encapsulates behavior
@dataclass
class Skill:
    id: UUID
    name: str
    version: int

    def update_name(self, new_name: str) -> None:
        if not new_name.strip(): raise ValueError("Name cannot be empty")
        self.name = new_name.strip()
        self.slug = Slug.from_name(new_name)
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1
```

### Transaction Script

```python
# ❌ BAD: All logic in one procedure
async def create_skill_procedure(db: AsyncSession, name: str, user_id: UUID) -> Skill:
    if len(name) > 128: raise ValueError("Name too long")
    slug = name.lower().replace(" ", "-")
    existing = await db.execute(select(SkillModel).where(SkillModel.slug == slug))
    if existing.scalar_one_or_none(): raise ValueError("Already exists")
    model = SkillModel(id=uuid4(), name=name, slug=slug, user_id=user_id)
    db.add(model)
    await db.commit()

# ✅ GOOD: Separation of concerns
async def handle_create_skill(user_id: UUID, name: str, skill_repo: SkillRepository) -> Skill:
    slug = Slug.from_name(name)
    existing = await skill_repo.get_by_slug(slug, user_id)
    if existing: raise ResourceConflictError()
    skill = SkillFactory.create(user_id=user_id, name=name)
    await skill_repo.save(skill)
    return skill
```

### Domain Layer Dependencies

```python
# ❌ BAD: Domain depends on infrastructure
from sqlalchemy import Column, String
from fastapi import HTTPException

# ✅ GOOD: Domain is pure Python
from dataclasses import dataclass
from uuid import UUID
from src.domain.value_objects.slug import Slug
```

### Exceptions with HTTP Codes

```python
# ❌ BAD: Domain exceptions coupled to HTTP
class SkillNotFoundError(Exception):
    status_code = 404

# ✅ GOOD: Category mapped in API layer
class ResourceNotFoundError(DomainError):
    category = "NOT_FOUND"

CATEGORY_STATUS_MAP = { "NOT_FOUND": 404, "CONFLICT": 409 }
```

---

## Quick Reference

### File Locations

| Type | Path |
|------|------|
| Aggregates | `src/domain/aggregates/` |
| Value Objects | `src/domain/value_objects/` |
| Repository Interfaces | `src/domain/repositories/` |
| Factories | `src/domain/factories/` |
| Handlers | `src/application/handlers/` |
| ORM Models | `src/infra/persistence/models/` |
| Repository Impl | `src/infra/persistence/repositories/` |

### Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Aggregate | Noun | `Skill`, `User`, `Tree` |
| Value Object | Noun | `Slug`, `Email`, `Path` |
| Repository Interface | `{Entity}Repository` | `SkillRepository` |
| Repository Impl | `Sql{Entity}Repository` | `SqlSkillRepository` |
| Factory | `{Entity}Factory` | `SkillFactory` |
| Handler | `handle_{action}_{entity}` | `handle_create_skill` |
| ORM Model | `{Entity}Model` | `SkillModel` |

### Checklist

- [ ] Domain layer has no FastAPI, SQLAlchemy, or Pydantic imports
- [ ] Aggregate encapsulates business behavior
- [ ] Value objects validate on construction
- [ ] Repository interface in domain, implementation in infra
- [ ] Handler uses function style
- [ ] Repository injected via FastAPI Depends
- [ ] Exceptions inherit from DomainError with category
