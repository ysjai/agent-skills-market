import bcrypt

from app.auth import create_access_token, create_refresh_token
from app.domain.aggregates.user import User
from app.domain.exceptions import ResourceConflictError
from app.domain.factories.user_factory import UserFactory
from app.domain.repositories.user_repository import UserRepository
from app.domain.value_objects.email import Email


async def handle_register_user(
    email: str,
    username: str,
    password: str,
    user_repo: UserRepository,
    phone: str | None = None,
) -> tuple[User, str, str]:
    email_vo = Email(email)
    exists = await user_repo.exists_by_email(email_vo)
    if exists:
        raise ResourceConflictError("Email already registered")
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    user = UserFactory.create(
        email=email,
        username=username,
        password_hash=password_hash,
        phone=phone,
    )
    await user_repo.save(user)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return user, access_token, refresh_token
