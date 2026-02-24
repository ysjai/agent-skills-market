import os
from collections.abc import AsyncGenerator
from pathlib import Path


def load_env_file(env_path: Path) -> None:
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

backend_dir = Path(__file__).parent.parent
load_env_file(backend_dir / ".env")
load_env_file(backend_dir / ".env.test")

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from src.auth import create_access_token
from src.core.config import Settings, get_settings
from src.infra.persistence.db.base import Base
from src.infra.persistence.models.user_model import UserModel


def create_override_get_db(db_session):


    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise

    return override_get_db

@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return get_settings()

@pytest_asyncio.fixture
async def db_engine():
    settings = get_settings()
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        poolclass=NullPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session_factory = async_sessionmaker(
        db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with async_session_factory() as session:
        yield session

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> UserModel:

    import uuid

    import bcrypt

    # Use unique email to prevent any possible conflicts
    unique_id = str(uuid.uuid4())[:8]
    email = f"test_{unique_id}@example.com"
    username = f"testuser_{unique_id}"

    password = "password123"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()

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
async def auth_token(test_user: UserModel) -> str:
    return create_access_token({"sub": str(test_user.id)})

@pytest_asyncio.fixture
async def auth_client(
    db_session: AsyncSession,
    test_user: UserModel,
    auth_token: str,
) -> AsyncGenerator[AsyncClient, None]:
    from src.infra.persistence.db.session import get_db
    from src.main import app

    app.dependency_overrides[get_db] = create_override_get_db(db_session)

    async with AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=app),
        headers={"Authorization": f"Bearer {auth_token}"},
    ) as ac:
        yield ac

@pytest_asyncio.fixture
async def another_user(db_session: AsyncSession) -> UserModel:

    import uuid

    import bcrypt

    # Use unique email to prevent any possible conflicts
    unique_id = str(uuid.uuid4())[:8]
    email = f"another_{unique_id}@example.com"
    username = f"anotheruser_{unique_id}"

    password = "password123"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode(), salt).decode()

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
async def another_auth_client(
    db_session: AsyncSession,
    another_user: UserModel,
) -> AsyncGenerator[AsyncClient, None]:
    from src.infra.persistence.db.session import get_db
    from src.main import app

    app.dependency_overrides[get_db] = create_override_get_db(db_session)

    another_token = create_access_token({"sub": str(another_user.id)})

    async with AsyncClient(
        base_url="http://test",
        transport=httpx.ASGITransport(app=app),
        headers={"Authorization": f"Bearer {another_token}"},
    ) as ac:
        yield ac

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    from src.infra.persistence.db.session import get_db
    from src.main import app

    app.dependency_overrides[get_db] = create_override_get_db(db_session)

    async with AsyncClient(base_url="http://test", transport=httpx.ASGITransport(app=app)) as ac:
        yield ac
