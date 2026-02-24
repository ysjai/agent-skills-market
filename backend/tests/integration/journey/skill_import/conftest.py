import uuid

import httpx
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db


@pytest_asyncio.fixture
async def business_user(db_session: AsyncSession):

    import bcrypt

    unique_id = str(uuid.uuid4())[:8]
    email = f"biz-{unique_id}@example.com"
    username = f"bizuser_{unique_id}"

    password = "password123"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()

    from src.infra.persistence.models.user_model import UserModel

    user = UserModel(
        email=email,
        username=username,
        password_hash=password_hash,
        is_active=True,
        email_verified=True,
    )
    db_session.add(user)
    await db_session.flush()
    await db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def business_client(
    db_session: AsyncSession,
    business_user,
):
    from src.auth import create_access_token
    from src.infra.persistence.db.session import get_db
    from src.main import app

    app.dependency_overrides[get_db] = create_override_get_db(db_session)
    token = create_access_token({"sub": str(business_user.id)})

    async with AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac
