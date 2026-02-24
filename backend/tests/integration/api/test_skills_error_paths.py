"""Error path tests for skills router.

Tests error scenarios and exception handling in the skills API.
"""

from uuid import uuid4

import pytest
from httpx import AsyncClient


def _unique_name(base: str) -> str:
    """Generate a unique skill name."""
    return f"{base}-{uuid4().hex[:8]}"


def _skill_payload(name: str) -> dict:
    """Generate a valid skill creation payload."""
    return {
        "name": name,
        "slug": name,
        "description": f"Description for {name}",
    }


class TestCreateSkillErrorPaths:
    """Test error paths for POST /api/skills"""

    @pytest.mark.asyncio
    async def test_should_return_422_when_create_skill_given_empty_name(self, auth_client: AsyncClient):
        """Test creating skill with empty name returns 422"""
        response = await auth_client.post(
            "/api/skills",
            json={"name": "", "slug": "", "description": ""},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_422_when_create_skill_given_invalid_name_format(
        self, auth_client: AsyncClient
    ):
        """Test creating skill with invalid name format returns 422"""
        response = await auth_client.post(
            "/api/skills",
            json={
                "name": "Invalid Name!",  # Invalid characters - uppercase and special chars
                "slug": "invalid-name",
                "description": "Test description",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_409_when_create_skill_given_duplicate_name(
        self, auth_client: AsyncClient
    ):
        """Test creating skill with duplicate name returns 409"""
        unique_name = _unique_name("dup")
        # Create first skill
        response1 = await auth_client.post("/api/skills", json=_skill_payload(unique_name))
        assert response1.status_code == 201

        # Try to create second skill with same name
        response2 = await auth_client.post("/api/skills", json=_skill_payload(unique_name))
        assert response2.status_code == 409


class TestImportSkillErrorPaths:
    """Test error paths for POST /api/skills/import"""

    @pytest.mark.asyncio
    async def test_should_return_422_when_import_skill_given_empty_name(self, auth_client: AsyncClient):
        """Test importing skill with empty name returns 422"""
        response = await auth_client.post(
            "/api/skills/import",
            json={"name": "", "slug": "", "description": ""},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_409_when_import_skill_given_duplicate_slug_same_user(
        self, auth_client: AsyncClient
    ):
        """Test importing skill with duplicate slug for same user returns 409"""
        unique_slug = _unique_name("dupslug")
        # Import first skill
        response1 = await auth_client.post(
            "/api/skills/import",
            json=_skill_payload(unique_slug),
        )
        assert response1.status_code == 201

        # Try to import second skill with same slug
        response2 = await auth_client.post(
            "/api/skills/import",
            json={
                "name": _unique_name("secondsuffix"),
                "slug": unique_slug,
                "description": "Second skill with same slug",
            },
        )
        assert response2.status_code == 409


class TestGetSkillErrorPaths:
    """Test error paths for GET /api/skills/{skill_id}"""

    @pytest.mark.asyncio
    async def test_should_return_422_when_get_skill_given_invalid_uuid_format(
        self, auth_client: AsyncClient
    ):
        """Test getting skill with invalid UUID format returns 422"""
        response = await auth_client.get("/api/skills/not-a-valid-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_skill_given_nonexistent_id(self, auth_client: AsyncClient):
        """Test getting non-existent skill returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.get(f"/api/skills/{random_uuid}")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_should_return_401_when_get_skill_given_no_auth(
        self, client: AsyncClient, auth_client: AsyncClient
    ):
        """Test getting skill without authentication returns 401"""
        # Create skill as authenticated user
        create_response = await auth_client.post(
            "/api/skills",
            json=_skill_payload(_unique_name("authtest")),
        )
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        # Try to get skill without authentication
        response = await client.get(f"/api/skills/{skill_id}")
        assert response.status_code == 401


class TestGetSkillFilesErrorPaths:
    """Test error paths for GET /api/skills/{skill_id}/files"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_get_skill_files_given_nonexistent_skill(
        self, auth_client: AsyncClient
    ):
        """Test getting files of non-existent skill returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.get(f"/api/skills/{random_uuid}/files")
        assert response.status_code == 404


class TestUpdateSkillErrorPaths:
    """Test error paths for PUT /api/skills/{skill_id}"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_update_skill_given_nonexistent_id(
        self, auth_client: AsyncClient
    ):
        """Test updating non-existent skill returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.put(
            f"/api/skills/{random_uuid}",
            json={"name": "updated-name"},
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_should_return_422_when_update_skill_given_invalid_name(
        self, auth_client: AsyncClient
    ):
        """Test updating skill with invalid name returns 422"""
        # First create a skill
        create_response = await auth_client.post(
            "/api/skills",
            json=_skill_payload(_unique_name("updatetest")),
        )
        assert create_response.status_code == 201
        skill_id = create_response.json()["id"]

        # Try to update with invalid name
        response = await auth_client.put(
            f"/api/skills/{skill_id}",
            json={"name": "Invalid Name!@#"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_409_when_update_skill_given_duplicate_name(
        self, auth_client: AsyncClient
    ):
        """Test updating skill with duplicate name returns 409"""
        # Create first skill
        name1 = _unique_name("first")
        response1 = await auth_client.post("/api/skills", json=_skill_payload(name1))
        assert response1.status_code == 201

        # Create second skill
        name2 = _unique_name("second")
        response2 = await auth_client.post("/api/skills", json=_skill_payload(name2))
        assert response2.status_code == 201
        second_skill_id = response2.json()["id"]

        # Try to update second skill with first skill's name
        response3 = await auth_client.put(
            f"/api/skills/{second_skill_id}",
            json={"name": name1},
        )
        assert response3.status_code == 409


class TestDeleteSkillErrorPaths:
    """Test error paths for DELETE /api/skills/{skill_id}"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_delete_skill_given_nonexistent_id(
        self, auth_client: AsyncClient
    ):
        """Test deleting non-existent skill returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.delete(f"/api/skills/{random_uuid}")
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data.get("message", "").lower()

    @pytest.mark.asyncio
    async def test_should_return_422_when_delete_skill_given_invalid_uuid(
        self, auth_client: AsyncClient
    ):
        """Test deleting skill with invalid UUID returns 422"""
        response = await auth_client.delete("/api/skills/not-a-valid-uuid")
        assert response.status_code == 422


class TestDownloadSkillErrorPaths:
    """Test error paths for GET /api/skills/{skill_id}/download"""

    @pytest.mark.asyncio
    async def test_should_return_404_when_download_skill_given_nonexistent_id(
        self, auth_client: AsyncClient
    ):
        """Test downloading non-existent skill returns 404"""
        random_uuid = str(uuid4())
        response = await auth_client.get(f"/api/skills/{random_uuid}/download")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_422_when_download_skill_given_invalid_uuid(
        self, auth_client: AsyncClient
    ):
        """Test downloading skill with invalid UUID returns 422"""
        response = await auth_client.get("/api/skills/not-a-valid-uuid/download")
        assert response.status_code == 422


class TestListSkillsErrorPaths:
    """Test error paths for GET /api/skills"""

    @pytest.mark.asyncio
    async def test_should_return_422_when_list_skills_given_negative_skip(
        self, auth_client: AsyncClient
    ):
        """Test listing skills with negative skip returns 422"""
        response = await auth_client.get("/api/skills?skip=-1")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_422_when_list_skills_given_zero_limit(self, auth_client: AsyncClient):
        """Test listing skills with zero limit returns 422"""
        response = await auth_client.get("/api/skills?limit=0")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_422_when_list_skills_given_excessive_limit(
        self, auth_client: AsyncClient
    ):
        """Test listing skills with excessive limit returns 422"""
        response = await auth_client.get("/api/skills?limit=1000")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_should_return_422_when_list_skills_given_invalid_skip_type(
        self, auth_client: AsyncClient
    ):
        """Test listing skills with non-integer skip returns 422"""
        response = await auth_client.get("/api/skills?skip=abc")
        assert response.status_code == 422
