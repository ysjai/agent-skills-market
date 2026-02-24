import bcrypt

from src.auth import create_access_token, create_refresh_token
from src.domain.aggregates.user import User
from src.domain.exceptions import UnauthorizedError
from src.domain.repositories.user_repository import UserRepository
from src.domain.value_objects.email import Email


async def handle_login(
    email: str,
    password: str,
    user_repo: UserRepository,
) -> tuple[User, str, str]:
    email_vo = Email(email)
    user = await user_repo.get_by_email(email_vo)
    if not user:
        raise UnauthorizedError("Incorrect email or password")
    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        raise UnauthorizedError("Incorrect email or password")
    if not user.is_active:
        raise UnauthorizedError("User account is inactive")
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return user, access_token, refresh_token
