import uuid

import pytest
from httpx import AsyncClient

class TestScenario05ComplexStructure:

    @pytest.mark.asyncio
    async def test_scenario_5_complex_directory_structure(self, business_client: AsyncClient):
        unique_slug = f"complex-{uuid.uuid4().hex[:8]}"

        # Step 1: 导入技能
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "complex-structure-skill",
                "slug": unique_slug,
                "description": "Skill with deep directory structure",
            },
        )
        assert response.status_code == 201
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # Step 2: 创建多级目录结构
        directories = [
            "src/",
            "src/components/",
            "src/utils/",
            "tests/",
            "tests/unit/",
            "tests/integration/",
            "docs/",
            "docs/api/",
            "docs/guide/",
        ]

        for directory in directories:
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": directory, "type": "tree"},
            )
            assert response.status_code == 200, f"创建目录 {directory} 失败"

        # Step 3: 准备文件内容
        files_structure = {
            "src/components/Button.tsx": b"export const Button = () => <button>Click</button>",
            "src/components/Modal.tsx": b"export const Modal = () => <div>Modal</div>",
            "src/utils/helpers.ts": b"export const helper = () => 'help'",
            "tests/unit/button.test.ts": b"test('button works', () => {})",
            "tests/integration/app.test.ts": b"test('app works', () => {})",
            "docs/api/reference.md": b"# API Reference",
            "docs/guide/getting-started.md": b"# Getting Started",
        }

        # Step 4: 上传文件
        blob_ids = {}
        for filepath, content in files_structure.items():
            response = await business_client.post(
                "/api/blobs",
                files={"file": (filepath, content, "application/octet-stream")},
            )
            assert response.status_code == 201, f"上传 {filepath} 失败"
            blob_ids[filepath] = response.json()["id"]

        # Step 5: 添加文件到tree
        for filepath, blob_id in blob_ids.items():
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filepath, "type": "blob", "blob_id": blob_id},
            )
            assert response.status_code == 200, f"添加 {filepath} 失败"
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        tree_data = response.json()
        entries = tree_data.get("entries", [])
        paths = [e["path"] for e in entries]
        for directory in directories:
            assert directory in paths, f"目录 {directory} 应该存在"
        for filepath in files_structure.keys():
            assert filepath in paths, f"文件 {filepath} 应该存在"

        response = await business_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200
        files_data = response.json()
        files_list = files_data.get("files", [])
        file_paths = [f["path"] for f in files_list]

        for filepath in files_structure.keys():
            assert filepath in file_paths, f"文件 {filepath} 应该在文件列表中"
        for filepath, expected_content in files_structure.items():
            entry = next((e for e in entries if e["path"] == filepath), None)
            assert entry is not None, f"应该能找到 {filepath} 的entry"

            blob_id = entry["blob_id"]
            response = await business_client.get(f"/api/blobs/{blob_id}")
            assert response.status_code == 200, f"下载 {filepath} 失败"
            assert response.content == expected_content, f"{filepath} 内容不匹配"

