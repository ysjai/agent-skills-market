import uuid

import pytest
from httpx import AsyncClient

class TestScenario02SharedFiles:

    @pytest.mark.asyncio
    async def test_scenario_2_shared_files_between_skills(self, business_client: AsyncClient):
        unique_prefix = uuid.uuid4().hex[:8]
        shared_content = f"# Shared Documentation\n\nVersion: {unique_prefix}"

        # Step 1: 导入技能A
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": f"skill-alpha-{unique_prefix}",
                "slug": f"skill-alpha-{unique_prefix}",
                "description": "Skill Alpha with shared file",
            },
        )
        assert response.status_code == 201
        skill_a = response.json()
        tree_a_id = skill_a["tree_id"]
        skill_a_id = skill_a["id"]

        # Step 2: 向技能A添加共享文件
        response = await business_client.post(
            f"/api/trees/{tree_a_id}/files",
            json={
                "path": "README.md",
                "type": "blob",
                "content": shared_content,
            },
        )
        assert response.status_code == 200
        result_a = response.json()
        entries_a = result_a.get("entries", [])
        blob_id = next((e["blob_id"] for e in entries_a if e["path"] == "README.md"), None)
        assert blob_id is not None, "应该能找到 README.md 的 blob_id"

        # Step 3: 导入技能B
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": f"skill-beta-{unique_prefix}",
                "slug": f"skill-beta-{unique_prefix}",
                "description": "Skill Beta with same file",
            },
        )
        assert response.status_code == 201
        skill_b = response.json()
        tree_b_id = skill_b["tree_id"]
        skill_b_id = skill_b["id"]

        # Step 4: 向技能B添加相同内容的文件
        response = await business_client.post(
            f"/api/trees/{tree_b_id}/files",
            json={
                "path": "README.md",
                "type": "blob",
                "content": shared_content,
            },
        )
        assert response.status_code == 200
        result_b = response.json()
        entries_b = result_b.get("entries", [])
        blob_id_b = next((e["blob_id"] for e in entries_b if e["path"] == "README.md"), None)
        assert blob_id_b is not None
        assert blob_id == blob_id_b, "相同内容应该重用同一个blob"
        for skill_name, skill_id in [("A", skill_a_id), ("B", skill_b_id)]:
            response = await business_client.get(f"/api/blobs/{blob_id}")
            assert response.status_code == 200, f"技能{skill_name}下载文件失败"
            assert response.content.decode("utf-8") == shared_content

        # Step 5: 删除技能A
        response = await business_client.delete(f"/api/skills/{skill_a_id}")
        assert response.status_code == 204
        response = await business_client.get(f"/api/skills/{skill_a_id}")
        assert response.status_code == 404, "技能A应该返回404"
        response = await business_client.get(f"/api/skills/{skill_b_id}")
        assert response.status_code == 200, "技能B应该仍然存在"

        response = await business_client.get(f"/api/skills/{skill_b_id}/files")
        assert response.status_code == 200
        files_data = response.json()
        files_list = files_data.get("files", [])
        readme_file = next((f for f in files_list if f["path"] == "README.md"), None)
        assert readme_file is not None, "技能B应该仍有README.md"
        response = await business_client.get(f"/api/blobs/{blob_id}")
        assert response.status_code == 200, "共享文件应该仍然可下载"
        assert response.content.decode("utf-8") == shared_content

