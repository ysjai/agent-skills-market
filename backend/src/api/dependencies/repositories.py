from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Annotated, Protocol, cast
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.skill_favorite import SkillFavorite
from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.category_repository import CategoryRepository
from src.domain.repositories.prompt_favorite_repository import PromptFavoriteRepository
from src.domain.repositories.prompt_repository import PromptRepository
from src.domain.repositories.shared_prompt_repository import SharedPromptRepository
from src.domain.repositories.shared_skill_repository import SharedSkillRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository
from src.domain.repositories.user_repository import UserRepository
from src.infra.persistence.db.session import get_db
from src.infra.persistence.repositories.sql_blob_repository import SqlBlobRepository
from src.infra.persistence.repositories.sql_category_repository import SqlCategoryRepository
from src.infra.persistence.repositories.sql_prompt_favorite_repository import (
    SqlPromptFavoriteRepository,
)
from src.infra.persistence.repositories.sql_prompt_repository import SqlPromptRepository
from src.infra.persistence.repositories.sql_shared_prompt_repository import (
    SqlSharedPromptRepository,
)
from src.infra.persistence.repositories.sql_shared_skill_repository import SqlSharedSkillRepository
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository
from src.infra.persistence.repositories.sql_user_repository import SqlUserRepository


class SkillFavoriteRepository(Protocol):
    async def save(self, skill_favorite: SkillFavorite) -> SkillFavorite: ...

    async def delete(self, user_id: UUID, shared_skill_id: UUID) -> None: ...

    async def find_by_user_and_shared_skill(
        self, user_id: UUID, shared_skill_id: UUID
    ) -> SkillFavorite | None: ...

    async def find_by_user(self, user_id: UUID, skip: int, limit: int) -> list[SkillFavorite]: ...

    async def count_by_user(self, user_id: UUID) -> int: ...

    async def find_all_by_shared_skill_id(self, shared_skill_id: UUID) -> list[SkillFavorite]: ...

    async def update_snapshot_status_batch(
        self, shared_skill_id: UUID, new_status: str
    ) -> None: ...


async def get_skill_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> SkillRepository:
    return SqlSkillRepository(db)


async def get_user_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    return SqlUserRepository(db)


async def get_tree_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> TreeRepository:
    return SqlTreeRepository(db)


async def get_blob_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> BlobRepository:
    return SqlBlobRepository(db)


async def get_prompt_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> PromptRepository:
    return SqlPromptRepository(db)


async def get_category_repo(db: Annotated[AsyncSession, Depends(get_db)]) -> CategoryRepository:
    return SqlCategoryRepository(db)


async def get_shared_skill_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SharedSkillRepository:
    return SqlSharedSkillRepository(db)


async def get_skill_favorite_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SkillFavoriteRepository:
    module = import_module("src.infra.persistence.repositories.sql_skill_favorite_repository")
    repository_class = cast(
        Callable[[AsyncSession], SkillFavoriteRepository],
        getattr(module, "SqlSkillFavoriteRepository"),
    )
    return repository_class(db)


async def get_shared_prompt_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SharedPromptRepository:
    return SqlSharedPromptRepository(db)


async def get_prompt_favorite_repo(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PromptFavoriteRepository:
    return SqlPromptFavoriteRepository(db)
