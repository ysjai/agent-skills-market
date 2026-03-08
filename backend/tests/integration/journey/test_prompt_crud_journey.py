"""
Prompt CRUD + Versions journey tests.

Covers uncovered lines in:
- sql_prompt_repository.py: find_by_user (tag/search filters), count_by_user,
  save, delete, save_version, get_versions, get_version_by_id
- prompt_factory.py: import prompt
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ── helpers ──────────────────────────────────────────────────────────────
async def create_prompt(
    client: AsyncClient,
    title: str = "Test Prompt",
    content: str = "Hello {{name}}",
    description: str = "A test prompt",
    tags: list[str] | None = None,
) -> dict:
    payload: dict = {
        "title": title,
        "content": content,
        "description": description,
    }
    if tags is not None:
        payload["tags"] = tags
    resp = await client.post("/api/prompts", json=payload)
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── tests ────────────────────────────────────────────────────────────────


class TestPromptCRUDJourney:
    """Full CRUD lifecycle for prompts: create, list, filter, update, delete."""

    async def test_create_and_list_prompts(self, auth_client: AsyncClient):
        """Create multiple prompts and list them."""
        p1 = await create_prompt(auth_client, title="Alpha Prompt", tags=["ai", "chat"])
        p2 = await create_prompt(auth_client, title="Beta Prompt", tags=["ai", "code"])
        p3 = await create_prompt(auth_client, title="Gamma Report", tags=["code", "docs"])

        # List all — should get 3
        resp = await auth_client.get("/api/prompts", params={"offset": 0, "limit": 10})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3
        ids = [p["id"] for p in data["items"]]
        assert p1["id"] in ids
        assert p2["id"] in ids
        assert p3["id"] in ids

    async def test_list_prompts_with_tag_filter(self, auth_client: AsyncClient):
        """Filter prompts by tag — covers find_by_user tag filter and count_by_user tag filter."""
        await create_prompt(auth_client, title="Tagged One", tags=["python", "testing"])
        await create_prompt(auth_client, title="Tagged Two", tags=["javascript", "testing"])
        await create_prompt(auth_client, title="No Match", tags=["rust"])

        resp = await auth_client.get(
            "/api/prompts", params={"offset": 0, "limit": 10, "tag": "testing"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 2
        titles = [p["title"] for p in data["items"]]
        assert "Tagged One" in titles
        assert "Tagged Two" in titles
        assert "No Match" not in titles

    async def test_list_prompts_with_search_filter(self, auth_client: AsyncClient):
        """Search prompts by title keyword — covers find_by_user search filter."""
        await create_prompt(auth_client, title="Unique Searchable Title XYZ")
        await create_prompt(auth_client, title="Another Random Title")

        resp = await auth_client.get(
            "/api/prompts", params={"offset": 0, "limit": 10, "search": "Searchable"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        titles = [p["title"] for p in data["items"]]
        assert any("Searchable" in t for t in titles)

    async def test_list_prompts_with_tag_and_search(self, auth_client: AsyncClient):
        """Combine tag + search filters — hits both filter branches."""
        await create_prompt(auth_client, title="Combined Filter Hit", tags=["combo-tag"])
        await create_prompt(auth_client, title="Tag Only Hit", tags=["combo-tag"])
        await create_prompt(auth_client, title="Combined Filter Hit No Tag", tags=["other"])

        resp = await auth_client.get(
            "/api/prompts",
            params={"offset": 0, "limit": 10, "tag": "combo-tag", "search": "Combined"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        titles = [p["title"] for p in data["items"]]
        assert "Combined Filter Hit" in titles
        assert "Tag Only Hit" not in titles

    async def test_get_prompt_detail(self, auth_client: AsyncClient):
        """Get single prompt by ID — covers get_by_id."""
        prompt = await create_prompt(auth_client, title="Detail Prompt", content="Detail content")
        resp = await auth_client.get(f"/api/prompts/{prompt['id']}")
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["title"] == "Detail Prompt"
        assert detail["content"] == "Detail content"

    async def test_update_prompt(self, auth_client: AsyncClient):
        """Update a prompt — covers save (update path)."""
        prompt = await create_prompt(auth_client, title="Before Update")
        resp = await auth_client.put(
            f"/api/prompts/{prompt['id']}",
            json={"title": "After Update", "tags": ["updated"]},
        )
        assert resp.status_code == 200
        updated = resp.json()
        assert updated["title"] == "After Update"

    async def test_delete_prompt(self, auth_client: AsyncClient):
        """Delete a prompt — covers sql_prompt_repository.delete."""
        prompt = await create_prompt(auth_client, title="To Be Deleted")
        resp = await auth_client.delete(f"/api/prompts/{prompt['id']}")
        assert resp.status_code == 204

        # Verify it's gone
        resp = await auth_client.get(f"/api/prompts/{prompt['id']}")
        assert resp.status_code == 404

    async def test_export_prompt(self, auth_client: AsyncClient):
        """Export a prompt as markdown — covers export handler."""
        prompt = await create_prompt(auth_client, title="Export Me", content="Export content here")
        resp = await auth_client.get(f"/api/prompts/{prompt['id']}/export")
        assert resp.status_code == 200
        assert "text/plain" in resp.headers.get("content-type", "")
        assert "Export Me" in resp.text or "Export content here" in resp.text


class TestPromptVersionsJourney:
    """Version management for prompts: publish, list, get."""

    async def test_publish_and_list_versions(self, auth_client: AsyncClient):
        """Publish a version, then list it — covers save_version, get_versions."""
        prompt = await create_prompt(
            auth_client, title="Versioned Prompt", content="Version 1 content"
        )
        prompt_id = prompt["id"]

        # Publish a version (create already generates v1, so this is v2)
        resp = await auth_client.post(f"/api/prompts/{prompt_id}/versions")
        assert resp.status_code == 201, resp.text
        v2 = resp.json()
        assert v2["version_number"] >= 1  # at least version 1

        # Update content and publish another version
        await auth_client.put(
            f"/api/prompts/{prompt_id}",
            json={"content": "Version 3 content"},
        )
        resp = await auth_client.post(f"/api/prompts/{prompt_id}/versions")
        assert resp.status_code == 201
        v3 = resp.json()
        assert v3["version_number"] > v2["version_number"]

        # List versions — should have multiple
        resp = await auth_client.get(f"/api/prompts/{prompt_id}/versions")
        assert resp.status_code == 200
        versions = resp.json()
        assert len(versions) >= 2
        version_numbers = [v["version_number"] for v in versions]
        # Should be ascending
        assert version_numbers == sorted(version_numbers)

    async def test_get_version_by_id(self, auth_client: AsyncClient):
        """Get a specific version by ID — covers get_version_by_id."""
        prompt = await create_prompt(auth_client, title="Version Lookup", content="Some content")
        prompt_id = prompt["id"]

        # Publish a version
        resp = await auth_client.post(f"/api/prompts/{prompt_id}/versions")
        assert resp.status_code == 201
        version = resp.json()

        # Get by version ID
        resp = await auth_client.get(f"/api/prompts/{prompt_id}/versions/{version['id']}")
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["id"] == version["id"]
        assert detail["version_number"] == version["version_number"]

    async def test_version_not_found(self, auth_client: AsyncClient):
        """Get non-existent version — covers get_version_by_id None branch."""
        prompt = await create_prompt(auth_client, title="No Versions")
        import uuid

        fake_version_id = str(uuid.uuid4())
        resp = await auth_client.get(f"/api/prompts/{prompt['id']}/versions/{fake_version_id}")
        assert resp.status_code == 404


class TestPromptImportJourney:
    """Import a prompt from content — covers prompt_factory import path."""

    async def test_import_prompt(self, auth_client: AsyncClient):
        """Import a prompt from markdown with YAML frontmatter."""
        markdown_content = """---
title: Imported Prompt
description: A prompt imported from markdown
tags:
  - imported
  - test
---
This is imported content with {{variable}}
"""
        resp = await auth_client.post(
            "/api/prompts/import",
            json={"content": markdown_content},
        )
        assert resp.status_code in (200, 201), resp.text
        data = resp.json()
        assert "id" in data
        assert data["title"] == "Imported Prompt"


class TestPromptPagination:
    """Test pagination for prompt listing."""

    async def test_list_prompts_pagination(self, auth_client: AsyncClient):
        """Create several prompts and paginate — covers offset/limit paths."""
        for i in range(5):
            await create_prompt(auth_client, title=f"Paginated Prompt {i}")

        # First page
        resp = await auth_client.get("/api/prompts", params={"offset": 0, "limit": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["items"]) == 2
        assert data["total"] >= 5

        # Second page
        resp = await auth_client.get("/api/prompts", params={"offset": 2, "limit": 2})
        assert resp.status_code == 200
        data2 = resp.json()
        assert len(data2["items"]) == 2
        # Different items
        ids1 = {p["id"] for p in data["items"]}
        ids2 = {p["id"] for p in data2["items"]}
        assert ids1.isdisjoint(ids2)
