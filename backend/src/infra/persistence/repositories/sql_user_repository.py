from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.aggregates.user import User
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email
from src.infra.persistence.models.user_model import UserModel


class SqlUserRepository(UserRepository):

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: UUID) -> User | None:
        result = await self._db.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_email(self, email: Email) -> User | None:
        result = await self._db.execute(select(UserModel).where(UserModel.email == str(email)))
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def exists_by_email(self, email: Email) -> bool:
        result = await self._db.execute(
            select(func.count()).select_from(UserModel).where(UserModel.email == str(email))
        )
        count = result.scalar_one()
        return count > 0

    async def save(self, user: User) -> None:
        model = UserModel.from_domain(user)
        await self._db.merge(model)

    async def delete(self, user_id: UUID) -> None:
        result = await self._db.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if model:
            await self._db.delete(model)
