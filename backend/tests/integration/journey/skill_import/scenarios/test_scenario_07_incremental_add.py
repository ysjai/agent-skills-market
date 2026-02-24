import uuid

import pytest
from httpx import AsyncClient

class TestScenario07IncrementalAdd:

    @pytest.mark.asyncio
    async def test_scenario_7_incremental_file_addition(self, business_client: AsyncClient):
        unique_slug = f"incremental-{uuid.uuid4().hex[:8]}"

        # Step 1: 导入技能
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "incremental-update-skill",
                "slug": unique_slug,
                "description": "Skill for testing incremental updates",
            },
        )
        assert response.status_code == 201
        skill_data = response.json()
        skill_id = skill_data["id"]
        tree_id = skill_data["tree_id"]

        # Step 2: 创建初始目录和文件
        initial_dirs = ["src/", "docs/"]
        for directory in initial_dirs:
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": directory, "type": "tree"},
            )
            assert response.status_code == 200

        initial_files = {
            "src/main.py": b"def main(): pass",
            "docs/README.md": b"# Initial README",
        }

        initial_blob_ids = {}
        for filepath, content in initial_files.items():
            response = await business_client.post(
                "/api/blobs",
                files={"file": (filepath, content, "text/plain")},
            )
            assert response.status_code == 201
            blob_id = response.json()["id"]
            initial_blob_ids[filepath] = blob_id

            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filepath, "type": "blob", "blob_id": blob_id},
            )
            assert response.status_code == 200
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        initial_tree = response.json()
        initial_entries = initial_tree.get("entries", [])
        initial_paths = [e["path"] for e in initial_entries]

        for filepath in initial_files.keys():
            assert filepath in initial_paths, f"初始文件 {filepath} 应该存在"

        # Step 3: 增量添加新目录和文件
        new_dirs = ["tests/", "examples/"]
        for directory in new_dirs:
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": directory, "type": "tree"},
            )
            assert response.status_code == 200

        new_files = {
            "tests/test_main.py": b"def test_main(): assert True",
            "docs/advanced.md": b"# Advanced Guide",
            "examples/basic.py": b"# Basic example",
        }

        new_blob_ids = {}
        for filepath, content in new_files.items():
            response = await business_client.post(
                "/api/blobs",
                files={"file": (filepath, content, "text/plain")},
            )
            assert response.status_code == 201
            blob_id = response.json()["id"]
            new_blob_ids[filepath] = blob_id

            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filepath, "type": "blob", "blob_id": blob_id},
            )
            assert response.status_code == 200
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        final_tree = response.json()
        final_entries = final_tree.get("entries", [])
        final_paths = [e["path"] for e in final_entries]

        for filepath in initial_files.keys():
            assert filepath in final_paths, f"原有文件 {filepath} 应该仍然存在"
        for filepath in new_files.keys():
            assert filepath in final_paths, f"新文件 {filepath} 应该存在"
        for directory in new_dirs:
            assert directory in final_paths, f"新目录 {directory} 应该存在"
        all_files = {**initial_files, **new_files}
        all_blob_ids = {**initial_blob_ids, **new_blob_ids}

        for filepath, expected_content in all_files.items():
            entry = next((e for e in final_entries if e["path"] == filepath), None)
            assert entry is not None

            blob_id = entry["blob_id"]
            response = await business_client.get(f"/api/blobs/{blob_id}")
            assert response.status_code == 200
            assert response.content == expected_content
        response = await business_client.get(f"/api/skills/{skill_id}/files")
        assert response.status_code == 200
        files_data = response.json()
        files_list = files_data.get("files", [])
        file_paths = [f["path"] for f in files_list]

        for filepath in all_files.keys():
            assert filepath in file_paths, f"{filepath} 应该在文件列表中"

        # 只统计文件（排除目录）
        file_count = len([f for f in files_list if f.get("type") == "blob"])
        assert file_count == len(all_files), (
            f"文件列表应该包含 {len(all_files)} 个文件，实际 {file_count} 个"
        )

