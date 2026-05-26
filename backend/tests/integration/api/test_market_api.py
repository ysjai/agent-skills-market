from typing import TypedDict, cast
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.category_model import CategoryModel

MARKET_SKILLS_URL = "/api/market/skills"
FAVORITES_URL = "/api/favorites/skills"


class CategoryItemPayload(TypedDict):
    id: str


class CategoriesPayload(TypedDict):
    items: list[CategoryItemPayload]
    total: int


class SharedSkillPayload(TypedDict):
    id: str
    name: str


class MarketSkillItemPayload(TypedDict):
    id: str
    name: str


class MarketSkillListPayload(TypedDict):
    items: list[MarketSkillItemPayload]
    total: int


class MarketSkillDetailPayload(TypedDict):
    id: str
    name: str


class ErrorPayload(TypedDict):
    message: str


class LikePayload(TypedDict):
    shared_skill_id: str
    like_count: int
    message: str


class FavoritePayload(TypedDict):
    shared_skill_id: str | None
    snapshot_name: str


class FavoriteItemPayload(TypedDict):
    shared_skill_id: str | None


class FavoritesListPayload(TypedDict):
    items: list[FavoriteItemPayload]
    total: int


class MessagePayload(TypedDict):
    message: str


class CreateSkillResponsePayload(TypedDict):
    id: str


def _unique_name(base: str) -> str:
    return f"{base}-{uuid4().hex[:8]}"


def _skill_payload(name: str, description: str | None = None) -> dict[str, str]:
    return {
        "name": name,
        "slug": name,
        "description": description or f"Description for {name}",
    }


async def _get_category_id(auth_client: AsyncClient, db_session: AsyncSession) -> str:
    response = await auth_client.get("/api/categories")
    assert response.status_code == 200
    data = cast(CategoriesPayload, response.json())

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
        data = cast(CategoriesPayload, response.json())

    return data["items"][0]["id"]


async def _create_shared_skill(
    auth_client: AsyncClient,
    db_session: AsyncSession,
    *,
    name: str | None = None,
    description: str | None = None,
    share_message: str | None = None,
) -> SharedSkillPayload:
    skill_name = name or _unique_name("market-skill")
    create_response = await auth_client.post(
        "/api/skills",
        json=_skill_payload(skill_name, description=description),
    )
    assert create_response.status_code == 201
    created_skill = cast(CreateSkillResponsePayload, create_response.json())
    skill_id = created_skill["id"]

    category_id = await _get_category_id(auth_client, db_session)
    share_response = await auth_client.post(
        f"/api/skills/{skill_id}/share",
        json={
            "category_id": category_id,
            "share_message": share_message or f"Share message for {skill_name}",
        },
    )
    assert share_response.status_code == 201
    result = cast(SharedSkillPayload, share_response.json())
    # ShareSkillResp doesn't include name; attach it from the skill we created
    result["name"] = skill_name  # type: ignore[typeddict-unknown-key]
    return result


class TestListMarketSkills:
    @pytest.mark.asyncio
    async def test_should_return_200_with_list_when_list_market_skills_public(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)

        response = await client.get(MARKET_SKILLS_URL)

        assert response.status_code == 200
        data = cast(MarketSkillListPayload, response.json())
        assert isinstance(data["items"], list)
        assert data["total"] >= 1
        assert any(item["id"] == shared_skill["id"] for item in data["items"])

    @pytest.mark.asyncio
    async def test_should_return_matching_items_when_list_market_skills_given_keyword(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        keyword = _unique_name("keyword-skill")
        shared_skill = await _create_shared_skill(
            auth_client,
            db_session,
            name=keyword,
            description=f"Description for {keyword}",
        )

        response = await client.get(f"{MARKET_SKILLS_URL}?keyword={keyword}")

        assert response.status_code == 200
        data = cast(MarketSkillListPayload, response.json())
        assert data["total"] >= 1
        assert any(item["id"] == shared_skill["id"] for item in data["items"])
        assert all(keyword in item["name"] for item in data["items"])


class TestGetMarketSkillDetail:
    @pytest.mark.asyncio
    async def test_should_return_200_when_get_market_skill_detail_given_valid_id(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)

        response = await client.get(f"{MARKET_SKILLS_URL}/{shared_skill['id']}")

        assert response.status_code == 200
        data = cast(MarketSkillDetailPayload, response.json())
        assert data["id"] == shared_skill["id"]
        assert data["name"] == shared_skill["name"]

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_market_skill_detail_given_nonexistent_id(
        self,
        client: AsyncClient,
    ):
        response = await client.get(f"{MARKET_SKILLS_URL}/{uuid4()}")

        assert response.status_code == 404
        data = cast(ErrorPayload, response.json())
        assert "not found" in data.get("message", "").lower()


class TestLikeMarketSkill:
    @pytest.mark.asyncio
    async def test_should_return_201_with_like_count_when_like_market_skill(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)

        response = await another_auth_client.post(f"{MARKET_SKILLS_URL}/{shared_skill['id']}/like")

        assert response.status_code == 201
        data = cast(LikePayload, response.json())
        assert data["shared_skill_id"] == shared_skill["id"]
        assert data["like_count"] == 1

    @pytest.mark.asyncio
    async def test_should_return_200_when_unlike_market_skill_given_existing_like(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)
        like_response = await another_auth_client.post(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/like"
        )
        assert like_response.status_code == 201

        response = await another_auth_client.delete(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/like"
        )

        assert response.status_code == 200
        data = cast(LikePayload, response.json())
        assert data["shared_skill_id"] == shared_skill["id"]
        assert data["like_count"] == 0


class TestFavoriteMarketSkill:
    @pytest.mark.asyncio
    async def test_should_return_201_when_favorite_market_skill(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)

        response = await another_auth_client.post(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/favorite"
        )

        assert response.status_code == 201
        data = cast(FavoritePayload, response.json())
        assert data["shared_skill_id"] == shared_skill["id"]
        assert data["snapshot_name"] == shared_skill["name"]

    @pytest.mark.asyncio
    async def test_should_return_200_when_unfavorite_market_skill_given_existing_favorite(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)
        favorite_response = await another_auth_client.post(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/favorite"
        )
        assert favorite_response.status_code == 201

        response = await another_auth_client.delete(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/favorite"
        )

        assert response.status_code == 200
        data = cast(MessagePayload, response.json())
        assert data == {"message": "ok"}

    @pytest.mark.asyncio
    async def test_should_return_200_when_list_favorites_given_existing_favorite(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        shared_skill = await _create_shared_skill(auth_client, db_session)
        favorite_response = await another_auth_client.post(
            f"{MARKET_SKILLS_URL}/{shared_skill['id']}/favorite"
        )
        assert favorite_response.status_code == 201

        response = await another_auth_client.get(FAVORITES_URL)

        assert response.status_code == 200
        data = cast(FavoritesListPayload, response.json())
        assert data["total"] >= 1
        assert any(item["shared_skill_id"] == shared_skill["id"] for item in data["items"])
