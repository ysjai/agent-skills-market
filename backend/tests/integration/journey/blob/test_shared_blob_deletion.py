import uuid
from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db


class TestSharedBlobDeletion:
    @pytest_asyncio.fixture
    async def shared_blob_user(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"journey6_{unique_id}@example.com"
        username = f"journey6user_{unique_id}"

        password = "password123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        from src.infra.persistence.models.user_model import UserModel

        user = UserModel(
            email=email,
            username=username,
            password_hash=password_hash,
            is_active=True,
            email_verified=True,
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)
        return user

    @pytest_asyncio.fixture
    async def shared_blob_client(
        self,
        db_session: AsyncSession,
        shared_blob_user,
    ) -> AsyncGenerator[AsyncClient, None]:
        from src.auth import create_access_token
        from src.infra.persistence.db.session import get_db
        from src.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(shared_blob_user.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_should_keep_shared_blob_when_delete_one_skill_given_blob_referenced_by_another(
        self, shared_blob_client: AsyncClient
    ):
        unique_prefix = uuid.uuid4().hex[:8]
        shared_content = f"# Shared {unique_prefix}\n\nShared content"

        response_a = await shared_blob_client.post(
            "/api/skills/import",
            json={
                "name": f"skill-a-{unique_prefix}",
                "slug": f"skill-a-{unique_prefix}",
                "description": "A",
            },
        )
        assert response_a.status_code == 201
        skill_a = response_a.json()
        tree_a_id = skill_a["tree_id"]

        add_a = await shared_blob_client.post(
            f"/api/trees/{tree_a_id}/files",
            json={"path": "README.md", "type": "blob", "content": shared_content},
        )
        assert add_a.status_code == 200
        result_a = add_a.json()
        entries_a = result_a.get("entries", [])
        blob_id_a = next((e["blob_id"] for e in entries_a if e["path"] == "README.md"), None)
        assert blob_id_a is not None, f"Could not find README.md in entries: {entries_a}"

        response_b = await shared_blob_client.post(
            "/api/skills/import",
            json={
                "name": f"skill-b-{unique_prefix}",
                "slug": f"skill-b-{unique_prefix}",
                "description": "B",
            },
        )
        assert response_b.status_code == 201
        skill_b = response_b.json()
        tree_b_id = skill_b["tree_id"]

        add_b = await shared_blob_client.post(
            f"/api/trees/{tree_b_id}/files",
            json={"path": "README.md", "type": "blob", "content": shared_content},
        )
        assert add_b.status_code == 200
        result_b = add_b.json()
        entries_b = result_b.get("entries", [])
        blob_id_b = next((e["blob_id"] for e in entries_b if e["path"] == "README.md"), None)
        assert blob_id_b is not None, f"Could not find README.md in entries: {entries_b}"

        assert blob_id_a == blob_id_b, "Same content should reuse blob"

        await shared_blob_client.delete(f"/api/skills/{skill_a['id']}")

        get_b = await shared_blob_client.get(f"/api/skills/{skill_b['id']}")
        assert get_b.status_code == 200

        download_b = await shared_blob_client.get(f"/api/blobs/{blob_id_b}")
        assert download_b.status_code == 200
        assert download_b.content.decode("utf-8") == shared_content

    @pytest.mark.asyncio
    async def test_should_delete_blob_when_delete_all_skills_given_no_remaining_references(
        self, shared_blob_client: AsyncClient
    ):
        unique_content = f"Unique {uuid.uuid4()}"

        response = await shared_blob_client.post(
            "/api/skills/import",
            json={
                "name": f"unique-{uuid.uuid4().hex[:8]}",
                "slug": f"unique-{uuid.uuid4().hex[:8]}",
                "description": "Test",
            },
        )
        assert response.status_code == 201
        skill = response.json()
        tree_id = skill["tree_id"]

        add_file = await shared_blob_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "unique.txt", "type": "blob", "content": unique_content},
        )
        assert add_file.status_code == 200
        result = add_file.json()
        entries = result.get("entries", [])
        blob_id = next((e["blob_id"] for e in entries if e["path"] == "unique.txt"), None)
        assert blob_id is not None, f"Could not find unique.txt in entries: {entries}"

        delete_response = await shared_blob_client.delete(f"/api/skills/{skill['id']}")
        assert delete_response.status_code == 204

        get_blob = await shared_blob_client.get(f"/api/blobs/{blob_id}")
        assert get_blob.status_code == 404

    @pytest.mark.asyncio
    async def test_should_cleanup_blob_when_delete_imported_skill_given_file_references(
        self, shared_blob_client: AsyncClient
    ):
        content = f"Test {uuid.uuid4()}"

        response = await shared_blob_client.post(
            "/api/skills/import",
            json={
                "name": f"import-{uuid.uuid4().hex[:8]}",
                "slug": f"import-{uuid.uuid4().hex[:8]}",
                "description": "Test",
            },
        )
        assert response.status_code == 201
        skill = response.json()
        tree_id = skill["tree_id"]
        skill_id = skill["id"]

        add_file = await shared_blob_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "content": content},
        )
        assert add_file.status_code == 200
        result = add_file.json()
        entries = result.get("entries", [])
        blob_id = next((e["blob_id"] for e in entries if e["path"] == "test.txt"), None)
        assert blob_id is not None, f"Could not find test.txt in entries: {entries}"

        delete_response = await shared_blob_client.delete(f"/api/skills/{skill_id}")
        assert delete_response.status_code == 204

        get_blob = await shared_blob_client.get(f"/api/blobs/{blob_id}")
        assert get_blob.status_code == 404

    @pytest.mark.asyncio
    async def test_should_remove_shared_blob_when_delete_both_skills_given_no_remaining_references(
        self, shared_blob_client: AsyncClient
    ):
        unique_prefix = uuid.uuid4().hex[:8]
        shared_content = f"# Shared {unique_prefix}\n\nSame content in both skills"

        response_a = await shared_blob_client.post(
            "/api/skills/import",
            json={
                "name": f"shared-a-{unique_prefix}",
                "slug": f"shared-a-{unique_prefix}",
                "description": "A",
            },
        )
        assert response_a.status_code == 201
        skill_a = response_a.json()
        tree_a_id = skill_a["tree_id"]

        add_a = await shared_blob_client.post(
            f"/api/trees/{tree_a_id}/files",
            json={"path": "README.md", "type": "blob", "content": shared_content},
        )
        assert add_a.status_code == 200
        result_a = add_a.json()
        entries_a = result_a.get("entries", [])
        blob_id = next((e["blob_id"] for e in entries_a if e["path"] == "README.md"), None)
        assert blob_id is not None, f"Could not find README.md in entries: {entries_a}"

        response_b = await shared_blob_client.post(
            "/api/skills/import",
            json={
                "name": f"shared-b-{unique_prefix}",
                "slug": f"shared-b-{unique_prefix}",
                "description": "B",
            },
        )
        assert response_b.status_code == 201
        skill_b = response_b.json()
        tree_b_id = skill_b["tree_id"]

        add_b = await shared_blob_client.post(
            f"/api/trees/{tree_b_id}/files",
            json={"path": "README.md", "type": "blob", "content": shared_content},
        )
        assert add_b.status_code == 200
        result_b = add_b.json()
        entries_b = result_b.get("entries", [])
        blob_id_b = next((e["blob_id"] for e in entries_b if e["path"] == "README.md"), None)
        assert blob_id_b is not None, f"Could not find README.md in entries: {entries_b}"

        assert blob_id == blob_id_b, "Should reuse same blob"

        await shared_blob_client.delete(f"/api/skills/{skill_a['id']}")
        await shared_blob_client.delete(f"/api/skills/{skill_b['id']}")

        get_blob = await shared_blob_client.get(f"/api/blobs/{blob_id}")
        assert get_blob.status_code == 404, "Blob should be deleted when all references removed"
