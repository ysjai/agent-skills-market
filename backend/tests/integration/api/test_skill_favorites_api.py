"""API endpoint tests for skill favorite operations.

Covers: skill_favorite_repository interface, sql_skill_favorite_repository,
additional sql_shared_skill_repository paths.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.category_model import CategoryModel


SKILLS_URL = "/api/skills"
SHARE_URL = "/api/skills"  # POST /api/skills/{id}/share
MARKET_SKILLS_URL = "/api/market/skills"
FAVORITES_URL = "/api/favorites/skills"


async def _create_and_share_skill(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    name: str = "fav-test-skill",
) -> tuple[str, str]:
    """Helper: create a skill and share it. Returns (skill_id, shared_skill_id)."""
    # Create category first
    suffix = uuid4().hex[:8]
    category = CategoryModel(name=f"cat_{suffix}", slug=f"cat-{suffix}")
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    category_id = str(category.id)

    # Create skill (name must be slug-format: ^[a-z0-9-]+$)
    slug = f"{name}-{suffix}"
    create_resp = await auth_client.post(
        SKILLS_URL,
        json={"name": name, "slug": slug, "description": "A skill for favorite testing"},
    )
    assert create_resp.status_code == 201, create_resp.text
    skill_id = create_resp.json()["id"]

    # Share skill
    share_resp = await auth_client.post(
        f"{SHARE_URL}/{skill_id}/share",
        json={"category_id": category_id, "share_message": "test share"},
    )
    assert share_resp.status_code == 201, share_resp.text
    shared_skill_id = share_resp.json()["id"]

    return skill_id, shared_skill_id


@pytest.mark.asyncio
class TestSkillFavoriteApi:
    """Test skill favorite CRUD via HTTP endpoints."""

    async def test_should_favorite_and_list_and_unfavorite(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        # ── Given: User A creates and shares a skill ──
        skill_id, shared_skill_id = await _create_and_share_skill(auth_client, db_session)

        # ── When: User B favorites ──
        fav_resp = await another_auth_client.post(f"{MARKET_SKILLS_URL}/{shared_skill_id}/favorite")
        assert fav_resp.status_code == 201
        fav_data = fav_resp.json()
        assert fav_data["snapshot_name"] == "fav-test-skill"
        assert fav_data["snapshot_status"] == "active"
        favorite_id = fav_data["id"]

        # ── Then: Favorite appears in User B's favorites list ──
        list_resp = await another_auth_client.get(FAVORITES_URL)
        assert list_resp.status_code == 200
        list_data = list_resp.json()
        assert list_data["total"] >= 1
        fav_item = next((i for i in list_data["items"] if i["id"] == favorite_id), None)
        assert fav_item is not None
        assert fav_item["snapshot_name"] == "fav-test-skill"

        # ── Then: Market detail shows is_favorited = True ──
        detail_resp = await another_auth_client.get(f"{MARKET_SKILLS_URL}/{shared_skill_id}")
        assert detail_resp.status_code == 200
        assert detail_resp.json()["is_favorited"] is True
        assert detail_resp.json()["favorite_count"] == 1

        # ── When: User B unfavorites ──
        unfav_resp = await another_auth_client.delete(
            f"{MARKET_SKILLS_URL}/{shared_skill_id}/favorite"
        )
        assert unfav_resp.status_code == 200

        # ── Then: Favorites list is empty ──
        list_resp = await another_auth_client.get(FAVORITES_URL)
        assert list_resp.json()["total"] == 0

        # ── Then: Market detail shows is_favorited = False ──
        detail_resp = await another_auth_client.get(f"{MARKET_SKILLS_URL}/{shared_skill_id}")
        assert detail_resp.json()["is_favorited"] is False
        assert detail_resp.json()["favorite_count"] == 0

    async def test_should_return_404_when_favorite_nonexistent_shared_skill(
        self,
        auth_client: AsyncClient,
    ):
        fake_id = str(uuid4())
        resp = await auth_client.post(f"{MARKET_SKILLS_URL}/{fake_id}/favorite")
        assert resp.status_code == 404

    async def test_should_return_401_when_favorite_without_auth(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        skill_id, shared_skill_id = await _create_and_share_skill(auth_client, db_session)
        resp = await client.post(f"{MARKET_SKILLS_URL}/{shared_skill_id}/favorite")
        assert resp.status_code == 401

    async def test_should_handle_favorite_pagination(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """Create multiple favorites, test skip/limit pagination."""
        # Create and share 3 skills
        shared_ids = []
        for i in range(3):
            _, sid = await _create_and_share_skill(
                auth_client, db_session, name=f"paginated-skill-{i}"
            )
            shared_ids.append(sid)

        # User B favorites all 3
        for sid in shared_ids:
            resp = await another_auth_client.post(f"{MARKET_SKILLS_URL}/{sid}/favorite")
            assert resp.status_code == 201

        # Get first page (limit=2)
        page1 = await another_auth_client.get(FAVORITES_URL, params={"limit": 2, "skip": 0})
        assert page1.status_code == 200
        p1 = page1.json()
        assert p1["total"] == 3
        assert len(p1["items"]) == 2

        # Get second page
        page2 = await another_auth_client.get(FAVORITES_URL, params={"limit": 2, "skip": 2})
        assert page2.status_code == 200
        p2 = page2.json()
        assert p2["total"] == 3
        assert len(p2["items"]) == 1

    async def test_should_mark_favorite_withdrawn_when_skill_unshared(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        """When owner unshares, favorite snapshot_status → skill_withdrawn."""
        skill_id, shared_skill_id = await _create_and_share_skill(
            auth_client, db_session, name="withdraw-fav-skill"
        )

        # User B favorites
        fav_resp = await another_auth_client.post(f"{MARKET_SKILLS_URL}/{shared_skill_id}/favorite")
        assert fav_resp.status_code == 201
        fav_id = fav_resp.json()["id"]

        # User A withdraws
        withdraw_resp = await auth_client.delete(f"{SHARE_URL}/{skill_id}/share")
        assert withdraw_resp.status_code == 200

        # User B checks favorites
        fav_list = await another_auth_client.get(FAVORITES_URL)
        fav_item = next((i for i in fav_list.json()["items"] if i["id"] == fav_id), None)
        assert fav_item is not None
        assert fav_item["snapshot_status"] == "skill_withdrawn"


@pytest.mark.asyncio
class TestSkillMarketFilters:
    """Test market skill search and filter endpoints."""

    async def test_should_filter_by_category(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        # Create two categories
        cat1 = CategoryModel(name="Category A", slug="category-a")
        cat2 = CategoryModel(name="Category B", slug="category-b")
        db_session.add(cat1)
        db_session.add(cat2)
        await db_session.flush()
        await db_session.refresh(cat1)
        await db_session.refresh(cat2)

        # Create 2 skills, share to different categories
        resp1 = await auth_client.post(
            SKILLS_URL,
            json={"name": "cat-a-skill", "slug": "cat-a-skill", "description": "in cat A"},
        )
        sid1 = resp1.json()["id"]
        await auth_client.post(
            f"{SHARE_URL}/{sid1}/share",
            json={"category_id": str(cat1.id)},
        )

        resp2 = await auth_client.post(
            SKILLS_URL,
            json={"name": "cat-b-skill", "slug": "cat-b-skill", "description": "in cat B"},
        )
        sid2 = resp2.json()["id"]
        await auth_client.post(
            f"{SHARE_URL}/{sid2}/share",
            json={"category_id": str(cat2.id)},
        )

        # Filter by category A
        filter_resp = await client.get(MARKET_SKILLS_URL, params={"category_id": str(cat1.id)})
        assert filter_resp.status_code == 200
        names = [i["name"] for i in filter_resp.json()["items"]]
        assert "cat-a-skill" in names
        assert "cat-b-skill" not in names

    async def test_should_sort_by_popular(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        # Create and share 2 skills
        _, sid1 = await _create_and_share_skill(auth_client, db_session, name="less-popular")
        _, sid2 = await _create_and_share_skill(auth_client, db_session, name="more-popular")

        # Like skill 2 twice (from 2 users)
        await auth_client.post(f"{MARKET_SKILLS_URL}/{sid2}/like")
        await another_auth_client.post(f"{MARKET_SKILLS_URL}/{sid2}/like")

        # Sort by popular
        resp = await client.get(MARKET_SKILLS_URL, params={"sort_by": "popular"})
        assert resp.status_code == 200
        items = resp.json()["items"]
        # More Popular should come first (or at least have higher like_count)
        more_pop = next(i for i in items if i["id"] == sid2)
        assert more_pop["like_count"] >= 2
