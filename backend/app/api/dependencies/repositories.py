from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.blob_repository import BlobRepository
from app.domain.repositories.skill_repository import SkillRepository
from app.domain.repositories.tree_repository import TreeRepository
from app.domain.repositories.user_repository import UserRepository
from app.infra.persistence.db.session import get_db
from app.infra.persistence.repositories.sql_blob_repository import SqlBlobRepository
from app.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from app.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository
from app.infra.persistence.repositories.sql_user_repository import SqlUserRepository


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
