from uuid import UUID

from jwt.exceptions import InvalidTokenError

from src.auth import create_access_token, create_refresh_token, verify_token
from src.domain.aggregates.user import User
from src.domain.exceptions import ResourceNotFoundError, UnauthorizedError
from src.domain.repositories.user_repository import UserRepository


async def handle_refresh_token(
    refresh_token: str,
    user_repo: UserRepository,
) -> tuple[User, str, str]:
    try:
        payload = verify_token(refresh_token)
    except InvalidTokenError:
        raise UnauthorizedError("Invalid refresh token")
    token_type = payload.get("type")
    if token_type != "refresh":
        raise UnauthorizedError("Invalid token type")
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token payload")
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Invalid user ID in token")
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise ResourceNotFoundError("User not found")
    if not user.is_active:
        raise UnauthorizedError("User account is inactive")
    new_access_token = create_access_token(data={"sub": str(user_id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user_id)})
    return user, new_access_token, new_refresh_token
