import uuid

import pytest
from httpx import AsyncClient


class TestScenario06MixedFileTypes:

    @pytest.mark.asyncio
    async def test_scenario_6_mixed_file_types(self, business_client: AsyncClient):
        unique_slug = f"mixed-types-{uuid.uuid4().hex[:8]}"

        # Step 1: 导入技能
        response = await business_client.post(
            "/api/skills/import",
            json={
                "name": "mixed-types-skill",
                "slug": unique_slug,
                "description": "Skill with various file types",
            },
        )
        assert response.status_code == 201
        skill_data = response.json()
        tree_id = skill_data["tree_id"]

        # Step 2: 准备各种类型文件
        files_data = {
            "README.md": {
                "content": b"# Mixed Types Skill\n\nThis skill has various file types.",
                "type": "text/markdown",
                "verify": lambda c: c
                == b"# Mixed Types Skill\n\nThis skill has various file types.",
            },
            "config.json": {
                "content": b'{"name": "test", "enabled": true, "count": 42}',
                "type": "application/json",
                "verify": lambda c: b'"name": "test"' in c,
            },
            "script.py": {
                "content": b"def hello():\n    return 'world'\n\nif __name__ == '__main__':\n    print(hello())",
                "type": "text/x-python",
                "verify": lambda c: b"def hello():" in c,
            },
            # PNG: magic number 0x89 0x50 0x4E 0x47 0x0D 0x0A 0x1A 0x0A
            "logo.png": {
                "content": bytes(
                    [
                        0x89,
                        0x50,
                        0x4E,
                        0x47,
                        0x0D,
                        0x0A,
                        0x1A,
                        0x0A,  # PNG signature
                        0x00,
                        0x00,
                        0x00,
                        0x0D,
                        0x49,
                        0x48,
                        0x44,
                        0x52,  # IHDR chunk
                        0x00,
                        0x00,
                        0x00,
                        0x01,
                        0x00,
                        0x00,
                        0x00,
                        0x01,  # 1x1 pixel
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
                ),
                "type": "image/png",
                "verify": lambda c: c[:8] == b"\x89PNG\r\n\x1a\n",
            },
            # PDF: starts with %PDF
            "manual.pdf": {
                "content": b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj
4 0 obj << /Length 44 >> stream
BT /F1 12 Tf 100 700 Td (Test PDF) Tj ET
endstream endobj
xref 0 5
trailer << /Size 5 /Root 1 0 R >>
startxref 308
%%EOF
""",
                "type": "application/pdf",
                "verify": lambda c: c.startswith(b"%PDF"),
            },
            # ZIP: magic number 0x50 0x4B 0x03 0x04
            "resources.zip": {
                "content": bytes(
                    [
                        0x50,
                        0x4B,
                        0x03,
                        0x04,  # ZIP local file header signature
                        0x0A,
                        0x00,
                        0x00,
                        0x00,  # version, flags
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # compression method, time, date
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # CRC-32
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # compressed size
                        0x00,
                        0x00,
                        0x00,
                        0x00,  # uncompressed size
                        0x00,
                        0x00,  # file name length
                        0x00,
                        0x00,  # extra field length
                        0x50,
                        0x4B,
                        0x01,
                        0x02,  # Central directory signature
                        0x14,
                        0x00,
                        0x0A,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x50,
                        0x4B,
                        0x05,
                        0x06,  # End of central directory signature
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                        0x00,
                    ]
                ),
                "type": "application/zip",
                "verify": lambda c: c[:4] == b"PK\x03\x04",
            },
        }

        # Step 3: 上传所有文件
        blob_ids = {}
        for filename, file_info in files_data.items():
            response = await business_client.post(
                "/api/blobs",
                files={"file": (filename, file_info["content"], file_info["type"])},
            )
            assert response.status_code == 201, f"上传 {filename} 失败: {response.text}"
            blob_ids[filename] = response.json()["id"]

        # Step 4: 添加文件到tree
        for filename, blob_id in blob_ids.items():
            response = await business_client.post(
                f"/api/trees/{tree_id}/files",
                json={"path": filename, "type": "blob", "blob_id": blob_id},
            )
            assert response.status_code == 200, f"添加 {filename} 失败"
        response = await business_client.get(f"/api/trees/{tree_id}")
        assert response.status_code == 200
        tree_data = response.json()
        entries = tree_data.get("entries", [])

        for filename, file_info in files_data.items():
            entry = next((e for e in entries if e["path"] == filename), None)
            assert entry is not None, f"应该能找到 {filename}"

            blob_id = entry["blob_id"]
            response = await business_client.get(f"/api/blobs/{blob_id}")
            assert response.status_code == 200, f"下载 {filename} 失败"

            downloaded_content = response.content
            assert file_info["verify"](downloaded_content), f"{filename} 内容验证失败"
