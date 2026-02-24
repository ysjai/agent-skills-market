import sys
import uuid
from pathlib import Path

import httpx
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

backend_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(backend_dir))

from tests.conftest import create_override_get_db


@pytest_asyncio.fixture
async def journey_user(db_session: AsyncSession):
    import bcrypt

    unique_id = str(uuid.uuid4())[:8]
    email = f"journey_{unique_id}@example.com"
    username = f"journey_user_{unique_id}"

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
async def journey_client(db_session: AsyncSession, journey_user):
    from src.auth import create_access_token
    from src.infra.persistence.db.session import get_db
    from src.main import app

    app.dependency_overrides[get_db] = create_override_get_db(db_session)
    token = create_access_token({"sub": str(journey_user.id)})

    async with AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=app),
        headers={"Authorization": f"Bearer {token}"},
    ) as ac:
        yield ac
