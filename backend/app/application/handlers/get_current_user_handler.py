from uuid import UUID

from app.domain.aggregates.user import User
from app.domain.exceptions import ResourceNotFoundError
from app.domain.repositories.user_repository import UserRepository


async def handle_get_current_user(
    user_id: UUID,
    user_repo: UserRepository,
) -> User:
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("User not found")
    return user
