from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.persistence.models.skill_model import SkillModel
from src.infra.persistence.models.user_model import UserModel


@pytest_asyncio.fixture
async def test_skill(db_session: AsyncSession, test_user: UserModel) -> SkillModel:
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="test-skill",
        slug="test-skill",
        description="A test skill",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


@pytest_asyncio.fixture
async def another_skill(db_session: AsyncSession, another_user: UserModel) -> SkillModel:
    skill = SkillModel(
        id=uuid4(),
        user_id=another_user.id,
        name="another-skill",
        slug="another-skill",
        description="Another user's skill",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


class TestCreateSkill:
    @pytest.mark.asyncio
    async def should_return_201_when_create_skill_given_valid_input(
        self,
        auth_client: AsyncClient,
    ):
        response = await auth_client.post(
            "/api/skills",
            json={
                "name": "my-skill",
                "slug": "my-skill",
                "description": "A new skill",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "my-skill"
        assert data["slug"] == "my-skill"
        assert data["description"] == "A new skill"
        assert "id" in data
        assert "user_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    @pytest.mark.asyncio
    async def should_return_401_when_create_skill_given_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/skills",
            json={
                "name": "my-skill",
                "slug": "my-skill",
                "description": "A new skill",
            },
        )
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["message"]


class TestImportSkill:
    @pytest.mark.asyncio
    async def should_return_201_when_import_skill_given_valid_input(self, auth_client: AsyncClient):
        response = await auth_client.post(
            "/api/skills/import",
            json={
                "name": "imported-skill",
                "slug": "imported-skill",
                "description": "An imported skill",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "imported-skill"
        assert data["slug"] == "imported-skill"
        assert data["description"] == "An imported skill"
        assert "id" in data
        assert "tree_id" in data

    @pytest.mark.asyncio
    async def should_accept_custom_slug_when_import_skill_given_custom_slug(
        self, auth_client: AsyncClient
    ):
        response = await auth_client.post(
            "/api/skills/import",
            json={
                "name": "auto-slug-skill",
                "slug": "custom-slug",
                "description": "Skill with custom slug",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["slug"] == "custom-slug"

    @pytest.mark.asyncio
    async def should_return_409_when_import_skill_given_duplicate_slug(
        self, auth_client: AsyncClient
    ):
        response = await auth_client.post(
            "/api/skills/import",
            json={
                "name": "duplicate-skill",
                "slug": "duplicate-skill",
                "description": "First skill",
            },
        )
        assert response.status_code == 201

        response = await auth_client.post(
            "/api/skills/import",
            json={
                "name": "duplicate-skill",
                "slug": "duplicate-skill",
                "description": "Second skill",
            },
        )
        assert response.status_code == 409  # CONFLICT is correct for duplicate resources
        assert (
            "already exists" in response.json()["message"].lower()
            or "conflict" in response.json()["message"].lower()
        )

    @pytest.mark.asyncio
    async def should_return_422_when_import_skill_given_invalid_name(
        self, auth_client: AsyncClient
    ):
        response = await auth_client.post(
            "/api/skills/import",
            json={
                "name": "Invalid Name!",
                "slug": "invalid",
                "description": "Invalid name",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def should_return_401_when_import_skill_given_no_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/skills/import",
            json={
                "name": "imported-skill",
                "slug": "imported-skill",
                "description": "An imported skill",
            },
        )
        assert response.status_code == 401


class TestListSkills:
    @pytest.mark.asyncio
    async def should_return_skills_list_when_list_skills_given_authenticated(
        self,
        client: AsyncClient,
        auth_token: str,
        test_skill: SkillModel,
    ):
        response = await client.get(
            "/api/skills",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        skill_ids = [item["id"] for item in data["items"]]
        assert str(test_skill.id) in skill_ids

    @pytest.mark.asyncio
    async def should_return_empty_list_when_list_skills_given_no_skills(
        self, client: AsyncClient, auth_token: str
    ):
        response = await client.get(
            "/api/skills",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    @pytest.mark.asyncio
    async def should_return_401_when_list_skills_given_no_auth(self, client: AsyncClient):
        response = await client.get("/api/skills")
        assert response.status_code == 401


class TestGetSkill:
    @pytest.mark.asyncio
    async def should_return_skill_when_get_skill_given_valid_id(
        self,
        client: AsyncClient,
        auth_token: str,
        test_skill: SkillModel,
    ):
        response = await client.get(
            f"/api/skills/{test_skill.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_skill.id)
        assert data["name"] == test_skill.name
        assert data["slug"] == test_skill.slug
        assert data["description"] == test_skill.description

    @pytest.mark.asyncio
    async def should_return_404_when_get_skill_given_nonexistent_id(
        self,
        client: AsyncClient,
        auth_token: str,
    ):
        non_existent_id = uuid4()
        response = await client.get(
            f"/api/skills/{non_existent_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_401_when_get_skill_given_no_auth(
        self,
        client: AsyncClient,
        test_skill: SkillModel,
    ):
        response = await client.get(f"/api/skills/{test_skill.id}")
        assert response.status_code == 401


class TestUpdateSkill:
    @pytest.mark.asyncio
    async def should_update_skill_when_update_own_skill_given_owner(
        self,
        auth_client: AsyncClient,
        test_skill: SkillModel,
    ):
        response = await auth_client.put(
            f"/api/skills/{test_skill.id}",
            json={
                "name": "updated-skill",
                "description": "Updated description",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "updated-skill"
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def should_return_403_when_update_skill_given_not_owner(
        self,
        another_auth_client: AsyncClient,
        test_skill: SkillModel,
    ):
        response = await another_auth_client.put(
            f"/api/skills/{test_skill.id}",
            json={"name": "hacked-skill"},
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_404_when_update_skill_given_nonexistent_id(
        self,
        auth_client: AsyncClient,
    ):
        non_existent_id = uuid4()
        response = await auth_client.put(
            f"/api/skills/{non_existent_id}",
            json={"name": "updated-skill"},
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def should_return_401_when_update_skill_given_no_auth(
        self,
        client: AsyncClient,
        test_skill: SkillModel,
    ):
        response = await client.put(
            f"/api/skills/{test_skill.id}",
            json={"name": "updated-skill"},
        )
        assert response.status_code == 401


class TestDeleteSkill:
    @pytest.mark.asyncio
    async def should_delete_skill_when_delete_own_skill_given_owner(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
        auth_token: str,
        test_skill: SkillModel,
    ):
        response = await auth_client.delete(
            f"/api/skills/{test_skill.id}",
        )
        assert response.status_code == 204

        get_response = await client.get(
            f"/api/skills/{test_skill.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def should_return_403_when_delete_skill_given_not_owner(
        self,
        another_auth_client: AsyncClient,
        test_skill: SkillModel,
    ):
        response = await another_auth_client.delete(
            f"/api/skills/{test_skill.id}",
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["message"].lower()

    @pytest.mark.asyncio
    async def should_return_404_when_delete_skill_given_nonexistent_id(
        self,
        auth_client: AsyncClient,
    ):
        non_existent_id = uuid4()
        response = await auth_client.delete(
            f"/api/skills/{non_existent_id}",
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def should_return_401_when_delete_skill_given_no_auth(
        self,
        client: AsyncClient,
        test_skill: SkillModel,
    ):
        response = await client.delete(f"/api/skills/{test_skill.id}")
        assert response.status_code == 401
