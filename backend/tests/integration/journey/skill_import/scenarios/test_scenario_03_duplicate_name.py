import uuid

import pytest
from httpx import AsyncClient


class TestScenario03DuplicateName:

    @pytest.mark.asyncio
    async def test_scenario_3_duplicate_skill_name_conflict(self, business_client: AsyncClient):
        unique_slug = f"unique-skill-{uuid.uuid4().hex[:8]}"

        # Step 1: 第一次导入技能
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "unique-skill",
                "slug": unique_slug,
                "description": "First import",
            },
        )
        assert response.status_code == 201, f"第一次导入失败: {response.text}"
        response.json()

        # Step 2: 再次导入同名技能，应该失败
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "unique-skill",
                "slug": unique_slug,
                "description": "Second import attempt",
            },
        )
        # 期望返回 409 Conflict 或 400 Bad Request
        assert response.status_code in [400, 409], (
            f"重复导入应该返回400或409，但返回了{response.status_code}"
        )
        error_data = response.json()
        error_message = str(error_data).lower()
        assert any(
            keyword in error_message
            for keyword in ["exist", "duplicate", "already", "conflict", "exists"]
        ), f"错误信息应该表明技能已存在: {error_data}"

        # Step 3: 使用不同slug导入应该成功
        different_slug = f"different-skill-{uuid.uuid4().hex[:8]}"
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "different-skill",
                "slug": different_slug,
                "description": "Different slug import",
            },
        )
        assert response.status_code == 201, f"不同slug导入应该成功: {response.text}"
        response = await business_client.get("/api/skills")
        assert response.status_code == 200
        skills = response.json()["items"]
        slugs = [s["slug"] for s in skills]
        assert unique_slug in slugs
        assert different_slug in slugs
