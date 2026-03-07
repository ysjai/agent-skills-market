from uuid import UUID, uuid4
from typing import TypedDict, cast

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.category_model import CategoryModel
from src.infra.persistence.models.shared_skill_model import SharedSkillModel
from src.infra.persistence.models.skill_favorite_model import SkillFavoriteModel


MARKET_SKILLS_URL = "/api/market/skills"
FAVORITES_URL = "/api/favorites"


class CreateSkillPayload(TypedDict):
    id: str
    description: str | None


class SharedSkillPayload(TypedDict):
    id: str
    skill_id: str | None
    like_count: int
    status: str


class MarketSkillPayload(TypedDict):
    id: str
    skill_id: str | None
    snapshot_name: str
    like_count: int
    is_liked: bool
    is_favorited: bool


class MarketSkillListPayload(TypedDict):
    items: list[MarketSkillPayload]
    total: int


class LikePayload(TypedDict):
    shared_skill_id: str
    like_count: int


class FavoritePayload(TypedDict):
    shared_skill_id: str | None
    snapshot_status: str
    snapshot_name: str


class FavoritesListPayload(TypedDict):
    items: list[FavoritePayload]
    total: int


class RegisterPayload(TypedDict):
    access_token: str


class LoginPayload(TypedDict):
    access_token: str


def _unique_name(base: str) -> str:
    return f"{base}-{uuid4().hex[:8]}"


def _skill_payload(name: str) -> dict[str, str]:
    return {
        "name": name,
        "slug": name,
        "description": f"Description for {name}",
    }


async def _get_category_id(auth_client: AsyncClient, db_session: AsyncSession) -> str:
    response = await auth_client.get("/api/categories")
    assert response.status_code == 200
    data = cast(dict[str, list[dict[str, str]]], response.json())

    if not data["items"]:
        category = CategoryModel(
            name="Testing",
            slug=f"testing-{uuid4().hex[:8]}",
            description="Testing category",
            display_order=1,
            is_active=True,
        )
        db_session.add(category)
        await db_session.flush()

        response = await auth_client.get("/api/categories")
        assert response.status_code == 200
        data = cast(dict[str, list[dict[str, str]]], response.json())

    return data["items"][0]["id"]


async def _create_skill(auth_client: AsyncClient, name: str) -> CreateSkillPayload:
    response = await auth_client.post("/api/skills", json=_skill_payload(name))
    assert response.status_code == 201
    return cast(CreateSkillPayload, response.json())


async def _share_skill(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    skill_id: str,
    share_message: str,
) -> SharedSkillPayload:
    category_id = await _get_category_id(auth_client, db_session)
    response = await auth_client.post(
        f"/api/skills/{skill_id}/share",
        json={"category_id": category_id, "share_message": share_message},
    )
    assert response.status_code == 201
    return cast(SharedSkillPayload, response.json())


async def _create_second_user_headers(client: AsyncClient) -> dict[str, str]:
    unique_id = uuid4().hex[:8]
    email = f"journey-b-{unique_id}@example.com"
    username = f"journey_b_{unique_id}"
    password = "password123"

    register_response = await client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert register_response.status_code == 201
    _ = cast(RegisterPayload, register_response.json())

    login_response = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login_response.status_code == 200
    login_data = cast(LoginPayload, login_response.json())
    return {"Authorization": f"Bearer {login_data['access_token']}"}


def _find_market_item(items: list[MarketSkillPayload], shared_skill_id: str) -> MarketSkillPayload:
    return next(item for item in items if item["id"] == shared_skill_id)


def _find_favorite_item(items: list[FavoritePayload], snapshot_name: str) -> FavoritePayload:
    return next(item for item in items if item["snapshot_name"] == snapshot_name)


class TestSkillSharingJourney:
    @pytest.mark.asyncio
    async def test_should_complete_social_sharing_flow_when_browse_like_and_refresh_given_two_users(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        skill_name = _unique_name("journey-share-like")
        created_skill = await _create_skill(auth_client, skill_name)
        shared_skill = await _share_skill(
            auth_client,
            db_session,
            created_skill["id"],
            "Shared for market browsing",
        )

        user_b_headers = await _create_second_user_headers(client)
        browse_response = await client.get(
            f"{MARKET_SKILLS_URL}?keyword={skill_name}&skip=0&limit=20",
            headers=user_b_headers,
        )
        assert browse_response.status_code == 200
        browse_data = cast(MarketSkillListPayload, browse_response.json())
        market_item = _find_market_item(browse_data["items"], shared_skill["id"])
        assert market_item["snapshot_name"] == skill_name
        assert market_item["skill_id"] == created_skill["id"]
        assert market_item["like_count"] == 0

        like_response = await client.post(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/like",
            headers=user_b_headers,
        )
        assert like_response.status_code == 201
        like_data = cast(LikePayload, like_response.json())
        assert like_data["shared_skill_id"] == shared_skill["id"]
        assert like_data["like_count"] == 1

        owner_view_response = await auth_client.get(
            f"{MARKET_SKILLS_URL}?keyword={skill_name}&skip=0&limit=20"
        )
        assert owner_view_response.status_code == 200
        owner_view_data = cast(MarketSkillListPayload, owner_view_response.json())
        owner_item = _find_market_item(owner_view_data["items"], shared_skill["id"])
        assert owner_item["like_count"] == 1
        assert owner_item["is_liked"] is False

    @pytest.mark.asyncio
    async def test_should_mark_favorite_snapshot_withdrawn_when_owner_unshares_given_favorited_shared_skill(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        skill_name = _unique_name("journey-favorite-withdraw")
        created_skill = await _create_skill(auth_client, skill_name)
        shared_skill = await _share_skill(
            auth_client,
            db_session,
            created_skill["id"],
            "Shared for favorite snapshot flow",
        )

        user_b_headers = await _create_second_user_headers(client)
        favorite_response = await client.post(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/favorite",
            headers=user_b_headers,
        )
        assert favorite_response.status_code == 201
        favorite_data = cast(FavoritePayload, favorite_response.json())
        assert favorite_data["shared_skill_id"] == shared_skill["id"]
        assert favorite_data["snapshot_status"] == "active"

        favorites_response = await client.get(FAVORITES_URL, headers=user_b_headers)
        assert favorites_response.status_code == 200
        favorites_data = cast(FavoritesListPayload, favorites_response.json())
        favorite_item = _find_favorite_item(favorites_data["items"], skill_name)
        assert favorite_item["shared_skill_id"] == shared_skill["id"]
        assert favorite_item["snapshot_status"] == "active"

        unshare_response = await auth_client.delete(f"/api/skills/{created_skill['id']}/share")
        assert unshare_response.status_code == 200
        unshared_data = cast(SharedSkillPayload, unshare_response.json())
        assert unshared_data["id"] == shared_skill["id"]
        assert unshared_data["skill_id"] is None
        assert unshared_data["status"] == "withdrawn"

        refreshed_favorites_response = await client.get(FAVORITES_URL, headers=user_b_headers)
        assert refreshed_favorites_response.status_code == 200
        refreshed_favorites_data = cast(FavoritesListPayload, refreshed_favorites_response.json())
        refreshed_item = _find_favorite_item(refreshed_favorites_data["items"], skill_name)
        assert refreshed_item["shared_skill_id"] == shared_skill["id"]
        assert refreshed_item["snapshot_status"] == "skill_withdrawn"

        saved_favorite = await db_session.execute(
            select(SkillFavoriteModel).where(
                SkillFavoriteModel.shared_skill_id == UUID(shared_skill["id"])
            )
        )
        favorite_model = saved_favorite.scalar_one()
        assert favorite_model.snapshot_status == "skill_withdrawn"

    @pytest.mark.asyncio
    async def test_should_detach_shared_skill_from_source_when_delete_original_skill_given_shared_skill_exists(
        self,
        auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        skill_name = _unique_name("journey-delete-source")
        created_skill = await _create_skill(auth_client, skill_name)
        shared_skill = await _share_skill(
            auth_client,
            db_session,
            created_skill["id"],
            "Shared before deleting original skill",
        )

        delete_response = await auth_client.delete(f"/api/skills/{created_skill['id']}")
        assert delete_response.status_code == 204

        shared_skill_model = await db_session.get(SharedSkillModel, UUID(shared_skill["id"]))
        assert shared_skill_model is not None
        assert shared_skill_model.id == UUID(shared_skill["id"])
        assert shared_skill_model.skill_id is None

        old_link_result = await db_session.execute(
            select(SharedSkillModel).where(SharedSkillModel.skill_id == UUID(created_skill["id"]))
        )
        assert old_link_result.scalar_one_or_none() is None
