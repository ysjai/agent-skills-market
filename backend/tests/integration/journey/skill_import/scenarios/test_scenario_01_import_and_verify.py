import uuid

import pytest
from httpx import AsyncClient

class TestScenario01ImportAndVerify:

    @pytest.mark.asyncio
    async def test_scenario_1_import_skill_files_fully_accessible(
        self, business_client: AsyncClient
    ):
        # Step 1: 导入技能
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "fully-accessible-skill",
                "slug": f"fully-accessible-{uuid.uuid4().hex[:8]}",
                "description": "Test skill for full accessibility",
            },
        )
        assert response.status_code == 201, f"导入技能失败: {response.text}"
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # Step 2: 创建目录结构
        folders = ["src/", "docs/"]
        for folder in folders:
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": folder, "type": "tree"},
            )
            assert response.status_code == 200, f"创建目录 {folder} 失败"

        # Step 3: 上传文件到blob
        files_to_upload = {
            "SKILL.md": b"# My Skill\n\nThis is the skill description.",
            "config.json": b'{"name": "test-skill", "version": "1.0.0"}',
            "src/main.py": b"def main():\n    print('Hello World')",
            "docs/README.md": b"# Documentation\n\nHow to use this skill.",
        }

        blob_ids = {}
        for filename, content in files_to_upload.items():
            response = await business_client.post(
                "/api/blobs",
                files={"file": (filename, content, "application/octet-stream")},
            )
            assert response.status_code == 201, f"上传 {filename} 失败"
            blob_ids[filename] = response.json()["id"]

        # Step 4: 将文件添加到tree
        for filename, blob_id in blob_ids.items():
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filename, "type": "blob", "blob_id": blob_id},
            )
            assert response.status_code == 200, f"添加 {filename} 到tree失败"
        response = await business_client.get("/api/skills")
        assert response.status_code == 200
        skills_list = response.json()["items"]
        skill_ids = [s["id"] for s in skills_list]
        assert str(skill_id) in skill_ids, "技能应该出现在列表中"
        response = await business_client.get(f"/api/skills/{skill_id}")
        assert response.status_code == 200
        skill_detail = response.json()
        assert skill_detail["name"] == "fully-accessible-skill"
        assert skill_detail["id"] == str(skill_id)
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        assert "SKILL.md" in paths
        assert "config.json" in paths
        assert "src/" in paths
        assert "docs/" in paths
        assert "src/main.py" in paths
        assert "docs/README.md" in paths
        response = await business_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200
        files_data = response.json()
        files_list = files_data.get("files", [])
        file_paths = [f["path"] for f in files_list]
        assert "SKILL.md" in file_paths
        assert "src/main.py" in file_paths
        for filename, expected_content in files_to_upload.items():
            blob_id = blob_ids[filename]
            response = await business_client.get(f"/api/blobs/{blob_id}")
            assert response.status_code == 200, f"下载 {filename} 失败"
            assert response.content == expected_content, f"{filename} 内容不匹配"

