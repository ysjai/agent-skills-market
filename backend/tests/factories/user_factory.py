import bcrypt

from src.infra.persistence.models.user_model import UserModel


def create_user(
    email: str = "test@example.com",
    username: str = "testuser",
    password: str = "password123",
    is_active: bool = True,
    email_verified: bool = True,
) -> UserModel:
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()
    return UserModel(
        email=email,
        username=username,
        password_hash=password_hash,
        is_active=is_active,
        email_verified=email_verified,
    )
