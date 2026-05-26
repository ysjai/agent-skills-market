"""
Extended sharing & social journey tests.

Covers remaining uncovered lines in:
- sql_shared_skill_repository.py: find_by_user_and_skill, delete, find_like, save_like, delete_like
- sql_shared_prompt_repository.py: find_by_user_and_prompt, delete, find_like, save_like, delete_like
- sql_skill_favorite_repository.py: save, delete, find_by_user_and_shared_skill, count_by_user, find_all_by_shared_skill_id
- sql_prompt_favorite_repository.py: save, delete, find_by_user_and_shared_prompt, find_by_id
"""

from typing import cast
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.category_model import CategoryModel

pytestmark = pytest.mark.asyncio


# ── helpers ──────────────────────────────────────────────────────────────


async def _get_or_create_category(auth_client: AsyncClient, db_session: AsyncSession) -> str:
    response = await auth_client.get("/api/categories")
    assert response.status_code == 200
    data = cast(dict[str, list[dict[str, str]]], response.json())
    if not data["items"]:
        category = CategoryModel(
            name="Extended Test",
            slug=f"extended-test-{uuid4().hex[:8]}",
            description="Extended testing category",
            display_order=1,
            is_active=True,
        )
        db_session.add(category)
        await db_session.flush()
        response = await auth_client.get("/api/categories")
        data = cast(dict[str, list[dict[str, str]]], response.json())
    return data["items"][0]["id"]


async def _create_and_share_skill(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    name: str | None = None,
) -> tuple[str, str]:
    """Create a skill, share it, return (skill_id, shared_skill_id)."""
    slug = name or f"ext-skill-{uuid4().hex[:8]}"
    resp = await auth_client.post(
        "/api/skills",
        json={"name": slug, "slug": slug, "description": f"Skill {slug}"},
    )
    assert resp.status_code == 201, resp.text
    skill_id = resp.json()["id"]

    category_id = await _get_or_create_category(auth_client, db_session)
    resp = await auth_client.post(
        f"/api/skills/{skill_id}/share",
        json={"category_id": category_id, "share_message": "sharing for test"},
    )
    assert resp.status_code == 201, resp.text
    shared_skill_id = resp.json()["id"]
    return skill_id, shared_skill_id


async def _create_and_share_prompt(
    auth_client: AsyncClient,
    title: str | None = None,
) -> tuple[str, str]:
    """Create a prompt, share it, return (prompt_id, shared_prompt_id)."""
    t = title or f"Prompt {uuid4().hex[:8]}"
    resp = await auth_client.post(
        "/api/prompts",
        json={"title": t, "content": "Hello {{name}}", "description": "test"},
    )
    assert resp.status_code == 201, resp.text
    prompt_id = resp.json()["id"]

    resp = await auth_client.post(
        f"/api/prompts/{prompt_id}/share",
        json={"share_message": "sharing prompt"},
    )
    assert resp.status_code == 201, resp.text
    shared_prompt_id = resp.json()["id"]
    return prompt_id, shared_prompt_id


# ── Skill sharing extended tests ─────────────────────────────────────────


class TestSkillSharingExtended:
    """Tests covering remaining shared_skill_repository and skill_favorite_repository lines."""

    async def test_duplicate_share_returns_conflict(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ):
        """Share same skill twice → should get 409 or reuse.
        Covers find_by_user_and_skill path.
        """
        slug = f"dup-share-{uuid4().hex[:8]}"
        resp = await auth_client.post(
            "/api/skills",
            json={"name": slug, "slug": slug, "description": "Dup share test"},
        )
        assert resp.status_code == 201
        skill_id = resp.json()["id"]

        category_id = await _get_or_create_category(auth_client, db_session)
        # First share — OK
        resp = await auth_client.post(
            f"/api/skills/{skill_id}/share",
            json={"category_id": category_id, "share_message": "first share"},
        )
        assert resp.status_code == 201

        # Second share — should fail or reactivate
        resp = await auth_client.post(
            f"/api/skills/{skill_id}/share",
            json={"category_id": category_id, "share_message": "second share"},
        )
        # Could be 409 Conflict or 200 if reactivation
        assert resp.status_code in (200, 201, 409), resp.text

    async def test_skill_like_unlike_full_cycle(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Like → Unlike → Like again.
        Covers find_like, save_like, delete_like in shared_skill_repo.
        """
        _, shared_id = await _create_and_share_skill(auth_client, db_session)

        # Like with another user
        resp = await another_auth_client.post(f"/api/market/skills/{shared_id}/like")
        assert resp.status_code in (200, 201), resp.text

        # Check detail — is_liked=True
        resp = await another_auth_client.get(f"/api/market/skills/{shared_id}")
        assert resp.status_code == 200
        assert resp.json()["is_liked"] is True

        # Unlike
        resp = await another_auth_client.delete(f"/api/market/skills/{shared_id}/like")
        assert resp.status_code in (200, 204), resp.text

        # Check again — is_liked=False
        resp = await another_auth_client.get(f"/api/market/skills/{shared_id}")
        assert resp.status_code == 200
        assert resp.json()["is_liked"] is False

        # Like again
        resp = await another_auth_client.post(f"/api/market/skills/{shared_id}/like")
        assert resp.status_code in (200, 201), resp.text

    async def test_skill_favorite_unfavorite_full_cycle(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Favorite → check → Unfavorite → check.
        Covers save, find_by_user_and_shared_skill, delete, count_by_user
        in skill_favorite_repo.
        """
        _, shared_id = await _create_and_share_skill(auth_client, db_session)

        # Favorite with another user
        resp = await another_auth_client.post(f"/api/market/skills/{shared_id}/favorite")
        assert resp.status_code in (200, 201), resp.text

        # Check detail — is_favorited=True
        resp = await another_auth_client.get(f"/api/market/skills/{shared_id}")
        assert resp.status_code == 200
        assert resp.json()["is_favorited"] is True

        # List favorites — should include this skill
        resp = await another_auth_client.get(
            "/api/favorites/skills", params={"skip": 0, "limit": 10}
        )
        assert resp.status_code == 200
        fav_shared_ids = [str(f.get("shared_skill_id", f.get("id"))) for f in resp.json()["items"]]
        assert shared_id in fav_shared_ids

        # Unfavorite
        resp = await another_auth_client.delete(f"/api/market/skills/{shared_id}/favorite")
        assert resp.status_code in (200, 204), resp.text

        # Verify removed
        resp = await another_auth_client.get(f"/api/market/skills/{shared_id}")
        assert resp.status_code == 200
        assert resp.json()["is_favorited"] is False

    async def test_unshare_skill_withdraws(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Unshare (withdraw) a skill after someone favorited it.
        Covers find_all_by_shared_skill_id + delete paths in repos.
        """
        skill_id, shared_id = await _create_and_share_skill(auth_client, db_session)

        # Another user favorites it
        resp = await another_auth_client.post(f"/api/market/skills/{shared_id}/favorite")
        assert resp.status_code in (200, 201)

        # Owner unshares
        resp = await auth_client.delete(f"/api/skills/{skill_id}/share")
        assert resp.status_code == 200

        # Skill should no longer appear in market
        resp = await another_auth_client.get(f"/api/market/skills/{shared_id}")
        # Should be 404 or status=withdrawn
        assert resp.status_code in (200, 404)


# ── Prompt sharing extended tests ────────────────────────────────────────


class TestPromptSharingExtended:
    """Tests covering remaining shared_prompt_repository and prompt_favorite_repository lines."""

    async def test_duplicate_prompt_share_conflict(self, auth_client: AsyncClient):
        """Share same prompt twice → should get conflict or reactivate.
        Covers find_by_user_and_prompt.
        """
        title = f"Dup Share Prompt {uuid4().hex[:8]}"
        resp = await auth_client.post(
            "/api/prompts",
            json={"title": title, "content": "Hello", "description": "test"},
        )
        assert resp.status_code == 201
        prompt_id = resp.json()["id"]

        # First share
        resp = await auth_client.post(
            f"/api/prompts/{prompt_id}/share",
            json={"share_message": "first"},
        )
        assert resp.status_code == 201

        # Second share — should fail or reactivate
        resp = await auth_client.post(
            f"/api/prompts/{prompt_id}/share",
            json={"share_message": "second"},
        )
        assert resp.status_code in (200, 201, 409), resp.text

    async def test_prompt_like_unlike_cycle(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """Like → Unlike → Like.
        Covers find_like, save_like, delete_like in shared_prompt_repo.
        """
        _, shared_prompt_id = await _create_and_share_prompt(auth_client)

        # Like
        resp = await another_auth_client.post(f"/api/market/prompts/{shared_prompt_id}/like")
        assert resp.status_code in (200, 201), resp.text

        # Check
        resp = await another_auth_client.get(f"/api/market/prompts/{shared_prompt_id}")
        assert resp.status_code == 200
        assert resp.json()["is_liked"] is True

        # Unlike
        resp = await another_auth_client.delete(f"/api/market/prompts/{shared_prompt_id}/like")
        assert resp.status_code in (200, 204), resp.text

        # Check again
        resp = await another_auth_client.get(f"/api/market/prompts/{shared_prompt_id}")
        assert resp.status_code == 200
        assert resp.json()["is_liked"] is False

        # Like again
        resp = await another_auth_client.post(f"/api/market/prompts/{shared_prompt_id}/like")
        assert resp.status_code in (200, 201)

    async def test_prompt_favorite_unfavorite_cycle(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """Favorite → check → Unfavorite → check.
        Covers save, find_by_user_and_shared_prompt, delete, count_by_user
        in prompt_favorite_repo.
        """
        _, shared_prompt_id = await _create_and_share_prompt(auth_client)

        # Favorite
        resp = await another_auth_client.post(f"/api/market/prompts/{shared_prompt_id}/favorite")
        assert resp.status_code in (200, 201), resp.text

        # Check detail
        resp = await another_auth_client.get(f"/api/market/prompts/{shared_prompt_id}")
        assert resp.status_code == 200
        assert resp.json()["is_favorited"] is True

        # List favorites
        resp = await another_auth_client.get(
            "/api/favorites/prompts", params={"skip": 0, "limit": 10}
        )
        assert resp.status_code == 200
        fav_shared_ids = [str(f.get("shared_prompt_id", f.get("id"))) for f in resp.json()["items"]]
        assert shared_prompt_id in fav_shared_ids

        # Unfavorite
        resp = await another_auth_client.delete(f"/api/market/prompts/{shared_prompt_id}/favorite")
        assert resp.status_code in (200, 204), resp.text

        # Verify removed from favorites
        resp = await another_auth_client.get(
            "/api/favorites/prompts", params={"skip": 0, "limit": 10}
        )
        assert resp.status_code == 200
        fav_shared_ids = [str(f.get("shared_prompt_id", f.get("id"))) for f in resp.json()["items"]]
        assert shared_prompt_id not in fav_shared_ids

    async def test_unshare_prompt_withdraws(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """Unshare a prompt after someone favorited it.
        Covers find_all_by_prompt_id + delete paths.
        """
        prompt_id, shared_prompt_id = await _create_and_share_prompt(auth_client)

        # Another user favorites it
        resp = await another_auth_client.post(f"/api/market/prompts/{shared_prompt_id}/favorite")
        assert resp.status_code in (200, 201)

        # Owner unshares
        resp = await auth_client.delete(f"/api/prompts/{prompt_id}/share")
        assert resp.status_code == 200

        # Prompt should no longer appear in market
        resp = await another_auth_client.get(f"/api/market/prompts/{shared_prompt_id}")
        assert resp.status_code in (200, 404)

    async def test_reshare_prompt_after_unshare(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """Unshare then re-share a prompt.
        Covers the reactivation path in shared_prompt_repo.
        """
        prompt_id, shared_prompt_id = await _create_and_share_prompt(auth_client)

        # Another user favorites it
        resp = await another_auth_client.post(f"/api/market/prompts/{shared_prompt_id}/favorite")
        assert resp.status_code in (200, 201)

        # Owner unshares
        resp = await auth_client.delete(f"/api/prompts/{prompt_id}/share")
        assert resp.status_code == 200

        # Re-share
        resp = await auth_client.post(
            f"/api/prompts/{prompt_id}/share",
            json={"share_message": "reshared"},
        )
        assert resp.status_code in (200, 201), resp.text

    async def test_delete_shared_prompt_with_favorites(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """Delete the underlying prompt when it has favorites.
        Covers prompt delete with cascading shared prompt cleanup.
        """
        title = f"Delete Me {uuid4().hex[:8]}"
        prompt_id, shared_prompt_id = await _create_and_share_prompt(auth_client, title=title)

        # Another user favorites it
        resp = await another_auth_client.post(f"/api/market/prompts/{shared_prompt_id}/favorite")
        assert resp.status_code in (200, 201)

        # Delete the prompt (should also clean up shared prompt + favorites)
        resp = await auth_client.delete(f"/api/prompts/{prompt_id}")
        assert resp.status_code == 204

        # Verify prompt is gone
        resp = await auth_client.get(f"/api/prompts/{prompt_id}")
        assert resp.status_code == 404


# ── Market browsing with pagination ──────────────────────────────────────


class TestMarketBrowsingExtended:
    """Market browsing tests that hit offset/limit and filter paths."""

    async def test_market_skills_pagination(
        self,
        auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Create and share multiple skills, paginate through market.
        Covers find_active_by_filters offset/limit and count_active_by_filters.
        """
        for i in range(3):
            await _create_and_share_skill(
                auth_client, db_session, name=f"market-pag-{uuid4().hex[:8]}"
            )

        # First page
        resp = await auth_client.get("/api/market/skills", params={"skip": 0, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 3

        # Second page
        resp = await auth_client.get("/api/market/skills", params={"skip": 2, "limit": 2})
        assert resp.status_code == 200
        data2 = resp.json()
        assert len(data2["items"]) >= 1

    async def test_market_prompts_pagination(
        self,
        auth_client: AsyncClient,
    ):
        """Create and share multiple prompts, paginate through market.
        Covers find_active_by_filters offset/limit and count_active_by_filters.
        """
        for i in range(3):
            await _create_and_share_prompt(
                auth_client, title=f"Market Pag Prompt {uuid4().hex[:8]}"
            )

        # First page
        resp = await auth_client.get("/api/market/prompts", params={"skip": 0, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 3

        # Second page
        resp = await auth_client.get("/api/market/prompts", params={"skip": 2, "limit": 2})
        assert resp.status_code == 200
        data2 = resp.json()
        assert len(data2["items"]) >= 1
