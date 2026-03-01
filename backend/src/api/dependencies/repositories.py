from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.repositories.blob_repository import BlobRepository
from src.domain.repositories.prompt_repository import PromptRepository
from src.domain.repositories.skill_repository import SkillRepository
from src.domain.repositories.tree_repository import TreeRepository
from src.domain.repositories.user_repository import UserRepository
from src.infra.persistence.db.session import get_db
from src.infra.persistence.repositories.sql_blob_repository import SqlBlobRepository
from src.infra.persistence.repositories.sql_prompt_repository import SqlPromptRepository
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository
from src.infra.persistence.repositories.sql_user_repository import SqlUserRepository


async def get_skill_repo(
    db: AsyncSession = Depends(get_db),
) -> SkillRepository:
    """Get skill repository dependency."""
    return SqlSkillRepository(db)


async def get_user_repo(
    db: AsyncSession = Depends(get_db),
) -> UserRepository:
    """Get user repository dependency."""
    return SqlUserRepository(db)


async def get_tree_repo(
    db: AsyncSession = Depends(get_db),
) -> TreeRepository:
    """Get tree repository dependency."""
    return SqlTreeRepository(db)


async def get_blob_repo(
    db: AsyncSession = Depends(get_db),
) -> BlobRepository:
    """Get blob repository dependency."""
    return SqlBlobRepository(db)


async def get_prompt_repo(
    db: AsyncSession = Depends(get_db),
) -> PromptRepository:
    """Get prompt repository dependency."""
    return SqlPromptRepository(db)
