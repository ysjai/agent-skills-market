from collections.abc import AsyncGenerator

import httpx
import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.conftest import create_override_get_db

class TestJourneyImport:
    @pytest_asyncio.fixture
    async def import_user(self, db_session: AsyncSession):
        import uuid

        import bcrypt

        unique_id = str(uuid.uuid4())[:8]
        email = f"journey-import_{unique_id}@example.com"
        username = f"journeyimport_{unique_id}"

        password = "password123"
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt).decode()

        from app.infra.persistence.models.user_model import UserModel

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
    async def import_client(
        self,
        db_session: AsyncSession,
        import_user,
    ) -> AsyncGenerator[AsyncClient, None]:
        from app.auth import create_access_token
        from app.infra.persistence.db.session import get_db
        from app.main import app

        app.dependency_overrides[get_db] = create_override_get_db(db_session)
        token = create_access_token({"sub": str(import_user.id)})

        async with AsyncClient(
            base_url="http://test",
            transport=httpx.ASGITransport(app=app),
            headers={"Authorization": f"Bearer {token}"},
        ) as ac:
            yield ac

    @pytest.mark.asyncio
    async def test_should_import_complex_skill_and_verify_structure_when_import_given_valid_data(
        self, import_client: AsyncClient
    ):
        response = await import_client.post(
            "/api/skills/import",
            json={
                "name": "imported-complex-skill",
                "slug": "imported-complex-skill-journey",
                "description": "Imported complex skill",
            },
        )
        assert response.status_code == 201, f"导入失败: {response.text}"
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        response = await import_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200, f"导入后查询 tree 失败: {response.text}"
        tree_data = response.json()
        assert tree_data["id"] == tree_id, "Tree ID 不匹配"

        folders = ["scripts/", "docs/", "assets/", "resources/"]
        for folder in folders:
            response = await import_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": folder, "type": "tree"},
            )
            assert response.status_code == 200, f"创建目录 {folder} 失败: {response.text}"

        root_files = {
            "SKILL.md": b"# My Skill\n\nThis is a complex skill.",
            "config.json": b'{"name": "complex-skill", "version": "1.0.0"}',
            "main.py": b"print('Hello')",
            "requirements.txt": b"requests>=2.28.0\n",
        }

        scripts_files = {
            "scripts/setup.py": b"from setuptools import setup\nsetup(name='test')",
            "scripts/run.py": b"print('Running')",
        }

        docs_files = {
            "docs/README.md": b"# Documentation",
            "docs/API.md": b"# API Reference",
        }

        png_content = bytes(
            [
                0x89,
                0x50,
                0x4E,
                0x47,
                0x0D,
                0x0A,
                0x1A,
                0x0A,
                0x00,
                0x00,
                0x00,
                0x0D,
                0x49,
                0x48,
                0x44,
                0x52,
                0x00,
                0x00,
                0x00,
                0x01,
                0x00,
                0x00,
                0x00,
                0x01,
                0x08,
                0x02,
                0x00,
                0x00,
                0x00,
                0x90,
                0x77,
                0x53,
                0xDE,
                0x00,
                0x00,
                0x00,
                0x0C,
                0x49,
                0x44,
                0x41,
                0x54,
                0x08,
                0xD7,
                0x63,
                0xF8,
                0xFF,
                0xFF,
                0x3F,
                0x00,
                0x05,
                0xFE,
                0x02,
                0xFE,
                0xDC,
                0xCC,
                0x59,
                0xE7,
                0x00,
                0x00,
                0x00,
                0x00,
                0x49,
                0x45,
                0x4E,
                0x44,
                0xAE,
                0x42,
                0x60,
                0x82,
            ]
        )
        assets_files = {"assets/logo.png": png_content}

        pdf_content = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 44 >> stream
BT /F1 12 Tf 100 700 Td (Test) Tj ET
endstream endobj
xref 0 5
trailer << /Size 5 /Root 1 0 R >>
startxref 308
%%EOF
"""
        resources_files = {"resources/manual.pdf": pdf_content}

        all_files = {**root_files, **scripts_files, **docs_files, **assets_files, **resources_files}

        blob_ids = {}
        for filename, content in all_files.items():
            content_type = "application/octet-stream"
            if filename.endswith(".png"):
                content_type = "image/png"
            elif filename.endswith(".pdf"):
                content_type = "application/pdf"
            elif filename.endswith(".md"):
                content_type = "text/markdown"
            elif filename.endswith(".json"):
                content_type = "application/json"
            elif filename.endswith(".py"):
                content_type = "text/x-python"
            elif filename.endswith(".txt"):
                content_type = "text/plain"

            response = await import_client.post(
                "/api/blobs",
                files={"file": (filename, content, content_type)},
            )
            assert response.status_code == 201, f"上传 {filename} 失败: {response.text}"
            blob_ids[filename] = response.json()["id"]


        for filename, blob_id in blob_ids.items():
            response = await import_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filename, "type": "blob", "blob_id": blob_id},
            )
            assert response.status_code == 200, f"添加 {filename} 失败: {response.text}"


        response = await import_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]

        assert "SKILL.md" in paths
        assert "config.json" in paths
        assert "main.py" in paths
        assert "requirements.txt" in paths
        assert "scripts/" in paths
        assert "docs/" in paths
        assert "assets/" in paths
        assert "resources/" in paths
        assert "scripts/setup.py" in paths
        assert "scripts/run.py" in paths
        assert "docs/README.md" in paths
        assert "docs/API.md" in paths
        assert "assets/logo.png" in paths
        assert "resources/manual.pdf" in paths


        png_entry = next(e for e in entries if e["path"] == "assets/logo.png")
        response = await import_client.get(f"/api/blobs/{png_entry['blob_id']}")
        assert response.status_code == 200
        assert response.content[:8] == b"\x89PNG\x0d\x0a\x1a\x0a"

        pdf_entry = next(e for e in entries if e["path"] == "resources/manual.pdf")
        response = await import_client.get(f"/api/blobs/{pdf_entry['blob_id']}")
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF")

        response = await import_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200
        skill_files = response.json()
        files_list = skill_files.get("files", skill_files)
        assert len(files_list) >= 13


    @pytest.mark.asyncio
    async def test_should_persist_data_when_import_skill_given_valid_data(
        self, import_client: AsyncClient
    ):
        response = await import_client.post(
            "/api/skills/import",
            json={"name": "persist-test", "slug": "persist-test-journey", "description": "Test"},
        )
        assert response.status_code == 201
        tree_id = response.json()["tree_id"]

        response = await import_client.post(
            "/api/blobs",
            files={"file": ("test.txt", b"test data", "text/plain")},
        )
        blob_id = response.json()["id"]

        response = await import_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "blob_id": blob_id},
        )
        assert response.status_code == 200

        response = await import_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        assert len(entries) >= 1


    @pytest.mark.asyncio
    async def test_should_commit_transaction_when_import_skill_given_valid_data(
        self, db_session: AsyncSession, import_client: AsyncClient
    ):
        # Step 1: 导入 skill
        response = await import_client.post(
            "/api/skills/import",
            json={
                "name": "transaction-test",
                "slug": "transaction-test",
                "description": "Test transaction commit",
            },
        )
        assert response.status_code == 201
        tree_id = response.json()["tree_id"]

        # Step 2: 使用全新的独立 session 查询数据库
        # 这会模拟线上环境，验证数据是否真的提交了
        from sqlalchemy import text

        from app.infra.persistence.db.session import AsyncSessionLocal

        async with AsyncSessionLocal() as fresh_db:
            result = await fresh_db.execute(
                text("SELECT id FROM trees WHERE id = :tree_id"), {"tree_id": str(tree_id)}
            )
            row = result.fetchone()
            assert row is not None, "数据未提交到数据库！"
            assert str(row[0]) == str(tree_id)


    @pytest.mark.asyncio
    async def test_should_verify_blob_content_when_import_skill_given_file_upload(
        self, import_client: AsyncClient
    ):
        # 导入 skill
        response = await import_client.post(
            "/api/skills/import",
            json={
                "name": "verify-content",
                "slug": "verify-content-journey",
                "description": "Verify blob content",
            },
        )
        assert response.status_code == 201
        tree_id = response.json()["tree_id"]

        # 上传文件
        test_content = b"Hello, World! This is test content."
        response = await import_client.post(
            "/api/blobs",
            files={"file": ("test.txt", test_content, "text/plain")},
        )
        assert response.status_code == 201
        blob_id = response.json()["id"]
        response = await import_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "blob_id": blob_id},
        )
        assert response.status_code == 200

        # 关键验证：下载文件并验证内容
        response = await import_client.get(f"/api/blobs/{blob_id}")
        assert response.status_code == 200, f"下载失败: {response.text}"
        assert response.content == test_content, "文件内容不匹配"

