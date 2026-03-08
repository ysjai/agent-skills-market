"""Integration tests for sharing APIs and shared-skill cleanup behavior."""

from uuid import UUID, uuid4
from typing import TypedDict, cast

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.category_model import CategoryModel
from src.infra.persistence.models.shared_skill_model import SharedSkillModel
from src.infra.persistence.models.user_model import UserModel


MARKET_SKILLS_URL = "/api/market/skills"


class SkillResponse(TypedDict):
    id: str
    description: str | None


class CategoryItem(TypedDict):
    id: str


class SharedSkillResponse(TypedDict):
    id: str
    skill_id: str | None
    category_id: str
    share_message: str | None
    status: str
    like_count: int
    favorite_count: int


class MarketSkillResponse(TypedDict):
    id: str
    skill_id: str | None
    user_id: str
    name: str


class MarketSkillListResponse(TypedDict):
    items: list[MarketSkillResponse]
    total: int


def _unique_name(base: str) -> str:
    return f"{base}-{uuid4().hex[:8]}"


def _skill_payload(name: str) -> dict[str, str]:
    return {
        "name": name,
        "slug": name,
        "description": f"Description for {name}",
    }


async def _create_skill(auth_client: AsyncClient, name: str) -> SkillResponse:
    response = await auth_client.post("/api/skills", json=_skill_payload(name))
    assert response.status_code == 201
    return cast(SkillResponse, response.json())


async def _get_category_id(auth_client: AsyncClient, db_session: AsyncSession) -> str:
    response = await auth_client.get("/api/categories")
    assert response.status_code == 200
    data = cast(dict[str, list[CategoryItem]], response.json())
    items = data["items"]

    if not items:
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
        data = cast(dict[str, list[CategoryItem]], response.json())
        items = data["items"]

    return items[0]["id"]


async def _share_skill(
    auth_client: AsyncClient, skill_id: str, category_id: str
) -> SharedSkillResponse:
    response = await auth_client.post(
        f"/api/skills/{skill_id}/share",
        json={"category_id": category_id, "share_message": "share message"},
    )
    assert response.status_code == 201
    return cast(SharedSkillResponse, response.json())


class TestShareSkillApi:
    @pytest.mark.asyncio
    async def test_should_return_201_when_share_skill_given_valid_skill_and_category(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ):
        name = _unique_name("share-skill")
        skill = await _create_skill(auth_client, name)
        category_id = await _get_category_id(auth_client, db_session)

        response = await auth_client.post(
            f"/api/skills/{skill['id']}/share",
            json={"category_id": category_id, "share_message": "share message"},
        )

        assert response.status_code == 201
        data = cast(SharedSkillResponse, response.json())
        assert data["skill_id"] == skill["id"]
        assert data["category_id"] == category_id
        assert data["share_message"] == "share message"
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_should_return_409_when_share_skill_given_same_skill_twice(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ):
        skill = await _create_skill(auth_client, _unique_name("duplicate-share"))
        category_id = await _get_category_id(auth_client, db_session)
        _ = await _share_skill(auth_client, skill["id"], category_id)

        response = await auth_client.post(
            f"/api/skills/{skill['id']}/share",
            json={"category_id": category_id, "share_message": "share message"},
        )

        assert response.status_code == 409
        error = cast(dict[str, str], response.json())
        assert "already exists" in error["message"].lower()


class TestUnshareSkillApi:
    @pytest.mark.asyncio
    async def test_should_return_200_when_unshare_skill_given_owner_shared_skill(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ):
        skill = await _create_skill(auth_client, _unique_name("unshare-skill"))
        category_id = await _get_category_id(auth_client, db_session)
        shared_skill = await _share_skill(auth_client, skill["id"], category_id)

        response = await auth_client.delete(f"/api/skills/{skill['id']}/share")

        assert response.status_code == 200
        data = cast(SharedSkillResponse, response.json())
        assert data["id"] == shared_skill["id"]
        assert data["skill_id"] == skill["id"]
        assert data["status"] == "withdrawn"

    @pytest.mark.asyncio
    async def test_should_return_403_when_unshare_skill_given_another_users_shared_skill(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        skill = await _create_skill(auth_client, _unique_name("forbidden-unshare"))
        category_id = await _get_category_id(auth_client, db_session)
        _ = await _share_skill(auth_client, skill["id"], category_id)

        response = await another_auth_client.delete(f"/api/skills/{skill['id']}/share")

        assert response.status_code == 403
        error = cast(dict[str, str], response.json())
        assert "not authorized" in error["message"].lower()


class TestDeleteSkillSharingCleanup:
    @pytest.mark.asyncio
    async def test_should_clear_shared_skill_association_when_delete_skill_given_shared_skill_exists(
        self,
        auth_client: AsyncClient,
        db_session: AsyncSession,
    ):
        skill = await _create_skill(auth_client, _unique_name("delete-shared-skill"))
        category_id = await _get_category_id(auth_client, db_session)
        shared_skill = await _share_skill(auth_client, skill["id"], category_id)

        response = await auth_client.delete(f"/api/skills/{skill['id']}")

        assert response.status_code == 204

        result = await db_session.execute(
            select(SharedSkillModel).where(SharedSkillModel.skill_id == UUID(skill["id"]))
        )
        assert result.scalar_one_or_none() is None

        saved_shared_skill = await db_session.get(SharedSkillModel, UUID(shared_skill["id"]))
        assert saved_shared_skill is not None
        assert saved_shared_skill.skill_id is None


class TestListSharedSkillsApi:
    @pytest.mark.asyncio
    async def test_should_return_current_users_shared_skill_when_list_market_skills_given_owned_share(
        self,
        auth_client: AsyncClient,
        test_user: UserModel,
        db_session: AsyncSession,
    ):
        name = _unique_name("list-shared-skill")
        skill = await _create_skill(auth_client, name)
        category_id = await _get_category_id(auth_client, db_session)
        shared_skill = await _share_skill(auth_client, skill["id"], category_id)

        response = await auth_client.get(f"{MARKET_SKILLS_URL}?keyword={name}&skip=0&limit=20")

        assert response.status_code == 200
        data = cast(MarketSkillListResponse, response.json())
        assert data["total"] >= 1
        assert any(
            item["id"] == shared_skill["id"]
            and item["skill_id"] == skill["id"]
            and item["user_id"] == str(test_user.id)
            and item["name"] == name
            for item in data["items"]
        )
