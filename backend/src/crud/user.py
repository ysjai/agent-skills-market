"""User CRUD operations.

This module provides a simple CRUD interface for User operations.
Note: This is a compatibility layer for existing code. New code should use
SqlUserRepository directly.
"""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.user import User
from src.infra.persistence.models.user_model import UserModel


class UserCRUD:
    """Simple CRUD wrapper for User operations."""

    async def get(self, db: AsyncSession, *, id: str) -> User | None:
        """Get user by ID.

        Args:
            db: Database session
            id: User ID as string

        Returns:
            User domain object if found, None otherwise
        """
        from sqlalchemy import select

        stmt = select(UserModel).where(UserModel.id == UUID(id))
        result = await db.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None


# Singleton instance for import
user = UserCRUD()
