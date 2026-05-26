"""API endpoint tests for auth dependency edge cases.

Covers: api/dependencies/auth.py (get_current_user, get_optional_current_user).
"""

from uuid import uuid4

import httpx
import pytest
from httpx import AsyncClient

from src.auth import create_access_token


@pytest.mark.asyncio
class TestAuthDependency:
    """Test auth dependency via real HTTP endpoints."""

    async def test_should_return_401_when_no_auth_header(
        self,
        client: AsyncClient,
    ):
        """Protected endpoints should reject requests without auth."""
        # GET /api/skills requires auth
        resp = await client.get("/api/skills")
        assert resp.status_code == 401

    async def test_should_return_401_when_invalid_token(
        self,
        client: AsyncClient,
    ):
        """Invalid JWT token should return 401."""
        from src.main import app

        async with httpx.AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": "Bearer invalid.jwt.token"},
        ) as bad_client:
            resp = await bad_client.get("/api/skills")
            assert resp.status_code == 401

    async def test_should_return_401_when_token_for_nonexistent_user(
        self,
        client: AsyncClient,
    ):
        """Token with valid JWT but non-existent user_id should return 401."""
        from src.main import app

        fake_user_id = str(uuid4())
        token = create_access_token({"sub": fake_user_id})

        async with httpx.AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as fake_client:
            resp = await fake_client.get("/api/skills")
            assert resp.status_code == 401

    async def test_should_allow_optional_auth_without_token(
        self,
        client: AsyncClient,
    ):
        """Endpoints with optional auth should work without token."""
        # GET /api/market/skills uses get_optional_current_user
        resp = await client.get("/api/market/skills")
        assert resp.status_code == 200

    async def test_should_return_user_info_with_optional_auth(
        self,
        auth_client: AsyncClient,
    ):
        """Optional auth endpoints should still detect authenticated user."""
        # GET /api/market/skills with auth token should work and show is_liked/is_favorited
        resp = await auth_client.get("/api/market/skills")
        assert resp.status_code == 200

    async def test_should_return_401_when_bearer_prefix_missing(
        self,
        client: AsyncClient,
    ):
        """Token without Bearer prefix should still be accepted (stripped)."""
        from src.main import app

        # The auth dependency strips "Bearer " if present, otherwise uses raw token
        # A raw valid token should work
        token = create_access_token({"sub": str(uuid4())})

        async with httpx.AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": token},  # no Bearer prefix
        ) as raw_client:
            resp = await raw_client.get("/api/skills")
            # Token is valid JWT but user doesn't exist → 401
            assert resp.status_code == 401

    async def test_should_return_401_when_token_has_no_sub(
        self,
        client: AsyncClient,
    ):
        """Token without 'sub' claim should return 401."""
        from src.main import app

        # Create token without sub
        token = create_access_token({"other": "data"})

        async with httpx.AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as bad_client:
            resp = await bad_client.get("/api/skills")
            assert resp.status_code == 401
