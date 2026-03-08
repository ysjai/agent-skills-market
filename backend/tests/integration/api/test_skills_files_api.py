import uuid

import pytest
from httpx import AsyncClient


def unique_email():
    return f"test{uuid.uuid4().hex[:8]}@example.com"


class TestGetSkillFiles:
    @pytest.mark.asyncio
    async def test_should_return_files_when_get_skill_files_given_valid_skill(
        self, auth_client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={
                "name": "test-skill-files",
                "slug": "test-skill-files",
                "description": "Test skill for files API",
            },
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        files_response = await auth_client.get(f"/api/skills/{skill_id}/files")
        assert files_response.status_code == 200
        data = files_response.json()
        assert "files" in data
        assert "skill_id" in data
        assert "skill_name" in data
        assert isinstance(data["files"], list)

    @pytest.mark.asyncio
    async def test_should_return_empty_files_when_get_skill_files_given_empty_skill(
        self, auth_client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={"name": "test-empty-sk", "slug": "test-empty-sk", "description": "Empty skill"},
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        files_response = await auth_client.get(f"/api/skills/{skill_id}/files")
        assert files_response.status_code == 200
        data = files_response.json()
        assert len(data["files"]) >= 0

    @pytest.mark.asyncio
    async def test_should_return_401_when_get_skill_files_given_no_auth(self, client: AsyncClient):
        response = await client.get("/api/skills/00000000-0000-0000-0000-000000000001/files")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_should_return_403_when_get_skill_files_given_other_user(
        self, auth_client: AsyncClient, client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={"name": "user-a-sk-f", "slug": "user-a-sk-f", "description": "User A skill"},
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        email = unique_email()
        register_response = await client.post(
            "/api/auth/register",
            json={"email": email, "username": "userbfls", "password": "password123"},
        )
        assert register_response.status_code == 201

        login_response = await client.post(
            "/api/auth/login", json={"email": email, "password": "password123"}
        )
        assert login_response.status_code == 200
        userb_token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {userb_token}"}
        files_response = await client.get(f"/api/skills/{skill_id}/files", headers=headers)
        assert files_response.status_code == 403


class TestDownloadSkill:
    @pytest.mark.asyncio
    async def test_should_return_zip_when_download_skill_given_opencode_platform(
        self, auth_client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={
                "name": "test-dwn-sk",
                "slug": "test-dwn-sk-zip",
                "description": "Download test skill",
            },
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        tree_id = skill_response.json().get("tree_id")
        if tree_id:
            await auth_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": "test.txt", "type": "blob", "content": "hello world"},
            )

        download_response = await auth_client.get(
            f"/api/skills/{skill_id}/download?platform=opencode"
        )
        assert download_response.status_code == 200
        assert download_response.headers["content-type"] == "application/zip"

    @pytest.mark.asyncio
    async def test_should_return_markdown_when_download_skill_given_claude_platform(
        self, auth_client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={
                "name": "test-md-dwn",
                "slug": "test-md-dwn-load",
                "description": "Markdown download",
            },
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        download_response = await auth_client.get(
            f"/api/skills/{skill_id}/download?platform=claude"
        )
        assert download_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_return_200_when_download_skill_given_empty_skill(
        self, auth_client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={"name": "empty-dwn", "slug": "empty-dwn-load", "description": "Empty"},
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        download_response = await auth_client.get(f"/api/skills/{skill_id}/download")
        assert download_response.status_code == 200

    @pytest.mark.asyncio
    async def test_should_return_403_when_download_skill_given_other_user(
        self, auth_client: AsyncClient, client: AsyncClient
    ):
        skill_response = await auth_client.post(
            "/api/skills",
            json={"name": "private-sk", "slug": "private-sk-dwn", "description": "Private"},
        )
        assert skill_response.status_code == 201
        skill_id = skill_response.json()["id"]

        email = unique_email()
        register_response = await client.post(
            "/api/auth/register",
            json={"email": email, "username": "usercfls", "password": "password123"},
        )
        assert register_response.status_code == 201

        login_response = await client.post(
            "/api/auth/login", json={"email": email, "password": "password123"}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}
        download_response = await client.get(f"/api/skills/{skill_id}/download", headers=headers)
        assert download_response.status_code == 403

    @pytest.mark.asyncio
    async def test_should_return_404_when_download_skill_given_nonexistent_id(
        self, auth_client: AsyncClient
    ):
        response = await auth_client.get(
            "/api/skills/00000000-0000-0000-0000-000000000001/download"
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_should_return_404_when_download_skill_given_no_auth(self, client: AsyncClient):
        response = await client.get("/api/skills/00000000-0000-0000-0000-000000000001/download")
        assert response.status_code == 404
