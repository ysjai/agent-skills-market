import uuid

import pytest
from httpx import AsyncClient

class TestScenario04DeleteSkill:

    @pytest.mark.asyncio
    async def test_scenario_4_delete_skill_makes_files_inaccessible(
        self, business_client: AsyncClient
    ):
        unique_slug = f"delete-test-{uuid.uuid4().hex[:8]}"

        # Step 1: 导入技能
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "to-be-deleted",
                "slug": unique_slug,
                "description": "This skill will be deleted",
            },
        )
        assert response.status_code == 201
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # Step 2: 添加文件
        response = await business_client.post(
            "/api/blobs",
            files={"file": ("test.txt", b"delete me", "text/plain")},
        )
        assert response.status_code == 201
        blob_id = response.json()["id"]

        response = await business_client.post(
            f"/api/trees/{tree_id}/files",
            json={"path": "test.txt", "type": "blob", "blob_id": blob_id},
        )
        assert response.status_code == 200
        response = await business_client.get(f"/api/skills/{skill_id}")
        assert response.status_code == 200
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200

        # Step 3: 删除技能
        response = await business_client.delete(f"/api/skills/{skill_id}")
        assert response.status_code == 204
        response = await business_client.get("/api/skills")
        assert response.status_code == 200
        skills = response.json()["items"]
        skill_ids = [s["id"] for s in skills]
        assert str(skill_id) not in skill_ids, "已删除技能不应在列表中"
        response = await business_client.get(f"/api/skills/{skill_id}")
        assert response.status_code == 404, "已删除技能应该返回404"
        response = await business_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 404, "已删除技能的文件列表应该返回404"
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 404, "已删除技能的tree应该返回404"

