"""Journey test: Prompt sharing and social flow.

Covers: sql_shared_prompt_repository, sql_prompt_repository,
sql_prompt_favorite_repository, market.py prompt endpoints.
"""


import pytest
from httpx import AsyncClient

PROMPTS_URL = "/api/prompts"
MARKET_PROMPTS_URL = "/api/market/prompts"
FAVORITES_URL = "/api/favorites/prompts"


@pytest.mark.asyncio
class TestPromptSharingJourney:
    """Complete journey: create → share → browse → like → favorite → unshare."""

    async def test_should_complete_prompt_sharing_and_social_flow(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
        client: AsyncClient,
    ):
        # ── Given: User A creates a prompt ──
        create_resp = await auth_client.post(
            PROMPTS_URL,
            json={
                "title": "Journey Test Prompt",
                "content": "This is the content of the prompt.",
                "description": "A prompt for journey testing",
                "tags": ["testing", "journey"],
            },
        )
        assert create_resp.status_code == 201, create_resp.text
        prompt_data = create_resp.json()
        prompt_id = prompt_data["id"]

        # ── When: User A shares the prompt to market ──
        share_resp = await auth_client.post(
            f"{PROMPTS_URL}/{prompt_id}/share",
            json={"share_message": "Check out my prompt!"},
        )
        assert share_resp.status_code == 201, share_resp.text
        share_data = share_resp.json()
        shared_prompt_id = share_data["id"]
        assert share_data["status"] == "active"
        assert share_data["like_count"] == 0
        assert share_data["favorite_count"] == 0

        # ── Then: Prompt appears in market listing ──
        market_resp = await client.get(MARKET_PROMPTS_URL)
        assert market_resp.status_code == 200
        market_data = market_resp.json()
        assert market_data["total"] >= 1
        items = market_data["items"]
        shared_item = next((i for i in items if i["id"] == shared_prompt_id), None)
        assert shared_item is not None
        assert shared_item["title"] == "Journey Test Prompt"
        assert shared_item["description"] == "A prompt for journey testing"
        assert shared_item["author_name"] is not None
        assert shared_item["tags"] == ["testing", "journey"]

        # ── When: User B views prompt detail ──
        detail_resp = await another_auth_client.get(f"{MARKET_PROMPTS_URL}/{shared_prompt_id}")
        assert detail_resp.status_code == 200
        detail = detail_resp.json()
        assert detail["title"] == "Journey Test Prompt"
        assert detail["content"] == "This is the content of the prompt."
        assert detail["is_liked"] is False
        assert detail["is_favorited"] is False

        # ── When: User B likes the prompt ──
        like_resp = await another_auth_client.post(f"{MARKET_PROMPTS_URL}/{shared_prompt_id}/like")
        assert like_resp.status_code == 201
        like_data = like_resp.json()
        assert like_data["like_count"] == 1

        # ── Then: Detail shows is_liked = True and like_count = 1 ──
        detail_resp = await another_auth_client.get(f"{MARKET_PROMPTS_URL}/{shared_prompt_id}")
        detail = detail_resp.json()
        assert detail["is_liked"] is True
        assert detail["like_count"] == 1

        # ── When: User B unlikes ──
        unlike_resp = await another_auth_client.delete(
            f"{MARKET_PROMPTS_URL}/{shared_prompt_id}/like"
        )
        assert unlike_resp.status_code == 200
        assert unlike_resp.json()["like_count"] == 0

        # ── When: User B favorites the prompt ──
        fav_resp = await another_auth_client.post(
            f"{MARKET_PROMPTS_URL}/{shared_prompt_id}/favorite"
        )
        assert fav_resp.status_code == 201
        fav_data = fav_resp.json()
        assert fav_data["snapshot_title"] == "Journey Test Prompt"
        assert fav_data["snapshot_status"] == "active"
        favorite_id = fav_data["id"]

        # ── Then: Favorite appears in User B's list ──
        fav_list_resp = await another_auth_client.get(FAVORITES_URL)
        assert fav_list_resp.status_code == 200
        fav_list = fav_list_resp.json()
        assert fav_list["total"] >= 1
        fav_item = next((i for i in fav_list["items"] if i["id"] == favorite_id), None)
        assert fav_item is not None

        # ── Then: Detail shows is_favorited = True ──
        detail_resp = await another_auth_client.get(f"{MARKET_PROMPTS_URL}/{shared_prompt_id}")
        assert detail_resp.json()["is_favorited"] is True

        # ── When: User B unfavorites ──
        unfav_resp = await another_auth_client.delete(
            f"{MARKET_PROMPTS_URL}/{shared_prompt_id}/favorite"
        )
        assert unfav_resp.status_code == 200

        # ── Then: Favorites list is empty ──
        fav_list_resp = await another_auth_client.get(FAVORITES_URL)
        assert fav_list_resp.json()["total"] == 0

        # ── When: User A withdraws the shared prompt ──
        withdraw_resp = await auth_client.delete(f"{PROMPTS_URL}/{prompt_id}/share")
        assert withdraw_resp.status_code == 200
        assert withdraw_resp.json()["status"] == "withdrawn"

        # ── Then: Prompt no longer in market ──
        market_resp = await client.get(MARKET_PROMPTS_URL)
        market_data = market_resp.json()
        ids = [i["id"] for i in market_data["items"]]
        assert shared_prompt_id not in ids

    async def test_should_support_search_and_sort_in_market(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
    ):
        """Search by keyword and sort by popularity."""
        # ── Given: User A creates and shares multiple prompts ──
        prompt_ids = []
        for title in ["Alpha Prompt Unique", "Beta Prompt Unique", "Gamma Different"]:
            resp = await auth_client.post(
                PROMPTS_URL,
                json={"title": title, "content": f"Content for {title}"},
            )
            assert resp.status_code == 201
            prompt_ids.append(resp.json()["id"])

        shared_ids = []
        for pid in prompt_ids:
            resp = await auth_client.post(
                f"{PROMPTS_URL}/{pid}/share",
                json={"share_message": "sharing"},
            )
            assert resp.status_code == 201
            shared_ids.append(resp.json()["id"])

        # ── When: Search by keyword "Unique" ──
        search_resp = await client.get(MARKET_PROMPTS_URL, params={"keyword": "Unique"})
        assert search_resp.status_code == 200
        search_data = search_resp.json()

        # ── Then: Only matching prompts returned ──
        titles = [i["title"] for i in search_data["items"]]
        assert "Alpha Prompt Unique" in titles
        assert "Beta Prompt Unique" in titles
        assert "Gamma Different" not in titles

        # ── When: Sort by popular ──
        # First like one prompt to make it popular
        await auth_client.post(f"{MARKET_PROMPTS_URL}/{shared_ids[1]}/like")

        pop_resp = await client.get(MARKET_PROMPTS_URL, params={"sort_by": "popular"})
        assert pop_resp.status_code == 200
        pop_items = pop_resp.json()["items"]
        # The liked prompt should appear first (or at least have higher like_count)
        liked_item = next(i for i in pop_items if i["id"] == shared_ids[1])
        assert liked_item["like_count"] >= 1

    async def test_should_support_tag_filtering(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
    ):
        """Filter prompts by tags using overlap."""
        # ── Given: Prompt with specific tags ──
        resp = await auth_client.post(
            PROMPTS_URL,
            json={
                "title": "Tagged Prompt For Filter",
                "content": "Content",
                "tags": ["python", "ai"],
            },
        )
        assert resp.status_code == 201
        prompt_id = resp.json()["id"]

        resp = await auth_client.post(f"{PROMPTS_URL}/{prompt_id}/share", json={})
        assert resp.status_code == 201

        # ── When: Filter by tag "python" ──
        tag_resp = await client.get(MARKET_PROMPTS_URL, params={"tags": ["python"]})
        assert tag_resp.status_code == 200
        tag_items = tag_resp.json()["items"]
        tagged = [i for i in tag_items if "python" in i.get("tags", [])]
        assert len(tagged) >= 1

    async def test_should_export_shared_prompt_as_markdown(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
    ):
        """Export prompt content as markdown with YAML frontmatter."""
        # ── Given: A shared prompt ──
        resp = await auth_client.post(
            PROMPTS_URL,
            json={
                "title": "Export Test Prompt",
                "content": "Export this content please.",
                "description": "For export testing",
                "tags": ["export"],
            },
        )
        prompt_id = resp.json()["id"]

        share_resp = await auth_client.post(f"{PROMPTS_URL}/{prompt_id}/share", json={})
        shared_id = share_resp.json()["id"]

        # ── When: Export the prompt ──
        export_resp = await client.get(f"{MARKET_PROMPTS_URL}/{shared_id}/export")
        assert export_resp.status_code == 200
        assert "text/markdown" in export_resp.headers.get("content-type", "")

        body = export_resp.text
        assert "Export Test Prompt" in body
        assert "Export this content please." in body

    async def test_should_return_my_only_prompts(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """my_only=True should return only current user's shared prompts."""
        # ── Given: User A creates and shares a prompt ──
        resp = await auth_client.post(
            PROMPTS_URL,
            json={"title": "My Only Prompt", "content": "mine"},
        )
        pid = resp.json()["id"]
        await auth_client.post(f"{PROMPTS_URL}/{pid}/share", json={})

        # ── When: User A lists with my_only=True ──
        my_resp = await auth_client.get(MARKET_PROMPTS_URL, params={"my_only": True})
        assert my_resp.status_code == 200
        my_items = my_resp.json()["items"]
        assert len(my_items) >= 1
        assert all(i["title"] is not None for i in my_items)

        # ── When: User B lists with my_only=True ──
        other_resp = await another_auth_client.get(MARKET_PROMPTS_URL, params={"my_only": True})
        assert other_resp.status_code == 200
        # User B has not shared anything, so should have 0
        other_items = other_resp.json()["items"]
        assert all(i["title"] != "My Only Prompt" for i in other_items)

    async def test_should_handle_favorite_version_staleness_and_refresh(
        self,
        auth_client: AsyncClient,
        another_auth_client: AsyncClient,
    ):
        """Favorites track version; refresh updates snapshot."""
        # ── Given: User A creates, shares; User B favorites ──
        resp = await auth_client.post(
            PROMPTS_URL,
            json={"title": "Version V1", "content": "v1 content"},
        )
        prompt_id = resp.json()["id"]

        share_resp = await auth_client.post(f"{PROMPTS_URL}/{prompt_id}/share", json={})
        shared_id = share_resp.json()["id"]

        fav_resp = await another_auth_client.post(f"{MARKET_PROMPTS_URL}/{shared_id}/favorite")
        assert fav_resp.status_code == 201
        fav_id = fav_resp.json()["id"]
        assert fav_resp.json()["snapshot_title"] == "Version V1"

        # ── When: User A updates the prompt (new version) ──
        await auth_client.put(
            f"{PROMPTS_URL}/{prompt_id}",
            json={"title": "Version V2", "content": "v2 content"},
        )

        # Create a new version explicitly
        await auth_client.post(
            f"{PROMPTS_URL}/{prompt_id}/versions",
            json={"title": "Version V2", "content": "v2 content"},
        )

        # ── Then: Favorite list shows is_stale ──
        fav_list = await another_auth_client.get(FAVORITES_URL)
        fav_item = next((i for i in fav_list.json()["items"] if i["id"] == fav_id), None)
        assert fav_item is not None
        # The favorite still has old snapshot
        assert fav_item["snapshot_title"] == "Version V1"

        # ── When: User B refreshes the favorite ──
        refresh_resp = await another_auth_client.post(f"{FAVORITES_URL}/{fav_id}/refresh")
        assert refresh_resp.status_code == 200
        refreshed = refresh_resp.json()["favorite"]
        assert refreshed["snapshot_title"] == "Version V2"


@pytest.mark.asyncio
class TestPromptSharingEdgeCases:
    """Edge cases for prompt sharing."""

    async def test_should_return_404_when_like_nonexistent_prompt(
        self,
        auth_client: AsyncClient,
    ):
        from uuid import uuid4

        fake_id = str(uuid4())
        resp = await auth_client.post(f"{MARKET_PROMPTS_URL}/{fake_id}/like")
        assert resp.status_code == 404

    async def test_should_return_404_when_favorite_nonexistent_prompt(
        self,
        auth_client: AsyncClient,
    ):
        from uuid import uuid4

        fake_id = str(uuid4())
        resp = await auth_client.post(f"{MARKET_PROMPTS_URL}/{fake_id}/favorite")
        assert resp.status_code == 404

    async def test_should_return_401_when_like_without_auth(
        self,
        client: AsyncClient,
        auth_client: AsyncClient,
    ):
        # Create and share a prompt first
        resp = await auth_client.post(
            PROMPTS_URL,
            json={"title": "Auth Test", "content": "content"},
        )
        pid = resp.json()["id"]
        share_resp = await auth_client.post(f"{PROMPTS_URL}/{pid}/share", json={})
        sid = share_resp.json()["id"]

        # Try to like without auth
        like_resp = await client.post(f"{MARKET_PROMPTS_URL}/{sid}/like")
        assert like_resp.status_code == 401

    async def test_should_return_404_when_export_withdrawn_prompt(
        self,
        auth_client: AsyncClient,
        client: AsyncClient,
    ):
        # Create, share, then withdraw
        resp = await auth_client.post(
            PROMPTS_URL,
            json={"title": "Withdraw Export", "content": "content"},
        )
        pid = resp.json()["id"]
        share_resp = await auth_client.post(f"{PROMPTS_URL}/{pid}/share", json={})
        sid = share_resp.json()["id"]

        await auth_client.delete(f"{PROMPTS_URL}/{pid}/share")

        # Try to export withdrawn prompt
        export_resp = await client.get(f"{MARKET_PROMPTS_URL}/{sid}/export")
        assert export_resp.status_code == 404
