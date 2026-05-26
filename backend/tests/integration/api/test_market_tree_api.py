from __future__ import annotations

import uuid
from typing import TypedDict, cast

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.category_model import CategoryModel

MARKET_SKILLS_URL = "/api/market/skills"


class CategoryItemPayload(TypedDict):
    id: str


class CategoriesPayload(TypedDict):
    items: list[CategoryItemPayload]
    total: int


class SharedSkillPayload(TypedDict):
    id: str
    snapshot_name: str


class CreateSkillResponsePayload(TypedDict):
    id: str


class TreePayload(TypedDict):
    id: str
    entries: list[dict]


class ErrorPayload(TypedDict):
    message: str


def _unique_name(base: str) -> str:
    return f"{base}-{uuid.uuid4().hex[:8]}"


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
            slug=f"testing-{uuid.uuid4().hex[:8]}",
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


async def _create_shared_skill_with_tree(
    auth_client: AsyncClient,
    db_session: AsyncSession,
) -> tuple[str, str]:
    """Create a shared skill with a file tree. Returns (shared_skill_id, tree_id)."""
    # Create skill
    skill_name = _unique_name("tree-skill")
    create_response = await auth_client.post(
        "/api/skills",
        json=_skill_payload(skill_name),
    )
    assert create_response.status_code == 201
    skill_id = cast(CreateSkillResponsePayload, create_response.json())["id"]

    # Create tree with entries
    tree_response = await auth_client.post(
        "/api/trees",
        json={
            "entries": [
                {
                    "path": "SKILL.md",
                    "type": "blob",
                    "blob_id": "7318cec3-d2e4-4117-816e-ca12e361f762",
                },
                {
                    "path": "examples/",
                    "type": "tree",
                },
            ]
        },
    )
    assert tree_response.status_code == 201
    tree_id = cast(TreePayload, tree_response.json())["id"]

    # Associate tree with skill
    update_response = await auth_client.put(
        f"/api/skills/{skill_id}",
        json={"tree_id": tree_id},
    )
    assert update_response.status_code == 200

    # Share skill
    category_id = await _get_category_id(auth_client, db_session)
    share_response = await auth_client.post(
        f"/api/skills/{skill_id}/share",
        json={
            "category_id": category_id,
            "share_message": f"Share message for {skill_name}",
        },
    )
    assert share_response.status_code == 201
    shared_skill_id = cast(SharedSkillPayload, share_response.json())["id"]

    return shared_skill_id, tree_id


class TestGetMarketSkillTree:
    @pytest.mark.asyncio
    async def test_should_return_tree_when_get_market_skill_tree_given_shared_skill_with_tree(
        self, auth_client: AsyncClient, db_session: AsyncSession
    ):
        shared_skill_id, tree_id = await _create_shared_skill_with_tree(auth_client, db_session)

        response = await auth_client.get(f"{MARKET_SKILLS_URL}/{shared_skill_id}/tree")
        assert response.status_code == 200
        data = cast(TreePayload, response.json())
        assert data["id"] == tree_id
        assert "entries" in data

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_market_skill_tree_given_nonexistent_shared_skill(
        self, auth_client: AsyncClient
    ):
        fake_id = str(uuid.uuid4())
        response = await auth_client.get(f"{MARKET_SKILLS_URL}/{fake_id}/tree")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_tree_when_get_market_skill_tree_given_unauthenticated_user(
        self, auth_client: AsyncClient, client: AsyncClient, db_session: AsyncSession
    ):
        """Market skill tree should be accessible without authentication."""
        shared_skill_id, tree_id = await _create_shared_skill_with_tree(auth_client, db_session)

        response = await client.get(f"{MARKET_SKILLS_URL}/{shared_skill_id}/tree")
        assert response.status_code == 200
        data = cast(TreePayload, response.json())
        assert data["id"] == tree_id
