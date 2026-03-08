from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import pytest

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.aggregates.skill import Skill
from src.domain.aggregates.tree import Tree, TreeEntry
from src.domain.entities.blob import Blob
from src.domain.exceptions import ResourceNotFoundError
from src.domain.value_objects.path import Path


@pytest.fixture
def shared_skill_repo():
    return AsyncMock()


@pytest.fixture
def skill_repo():
    return AsyncMock()


@pytest.fixture
def tree_repo():
    return AsyncMock()


@pytest.fixture
def blob_repo():
    return AsyncMock()


class TestGetMarketBlobHandler:
    @pytest.mark.asyncio
    async def test_should_return_blob_when_given_valid_shared_skill_and_blob(
        self, shared_skill_repo, skill_repo, tree_repo, blob_repo
    ):
        from src.application.handlers.get_market_blob_handler import (
            handle_get_market_blob,
        )

        blob_id = uuid.uuid4()
        tree_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        shared_skill_id = uuid.uuid4()

        shared_skill = SharedSkill(id=shared_skill_id, skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=tree_id)
        tree = Tree(
            id=tree_id,
            entries=[
                TreeEntry(path=Path("SKILL.md"), blob_id=blob_id, entry_type="blob"),
            ],
        )
        blob = Blob.create(content=b"# Hello")

        # Override the id to match our expected blob_id
        blob.id = blob_id

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill
        tree_repo.get_by_id.return_value = tree
        blob_repo.get_by_id.return_value = blob

        result = await handle_get_market_blob(
            shared_skill_id=shared_skill_id,
            blob_id=blob_id,
            shared_skill_repo=shared_skill_repo,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert result.id == blob_id

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_blob_not_in_tree(
        self, shared_skill_repo, skill_repo, tree_repo, blob_repo
    ):
        from src.application.handlers.get_market_blob_handler import (
            handle_get_market_blob,
        )

        tree_id = uuid.uuid4()
        skill_id = uuid.uuid4()
        shared_skill_id = uuid.uuid4()

        shared_skill = SharedSkill(id=shared_skill_id, skill_id=skill_id, status="active")
        skill = Skill(id=skill_id, tree_id=tree_id)
        tree = Tree(id=tree_id, entries=[])

        shared_skill_repo.find_by_id.return_value = shared_skill
        skill_repo.get_by_id.return_value = skill
        tree_repo.get_by_id.return_value = tree

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_blob(
                shared_skill_id=shared_skill_id,
                blob_id=uuid.uuid4(),
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_shared_skill_not_found(
        self, shared_skill_repo, skill_repo, tree_repo, blob_repo
    ):
        from src.application.handlers.get_market_blob_handler import (
            handle_get_market_blob,
        )

        shared_skill_repo.find_by_id.return_value = None

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_blob(
                shared_skill_id=uuid.uuid4(),
                blob_id=uuid.uuid4(),
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_shared_skill_has_no_skill_id(
        self, shared_skill_repo, skill_repo, tree_repo, blob_repo
    ):
        from src.application.handlers.get_market_blob_handler import (
            handle_get_market_blob,
        )

        shared_skill = SharedSkill(id=uuid.uuid4(), skill_id=None, status="withdrawn")
        shared_skill_repo.find_by_id.return_value = shared_skill

        with pytest.raises(ResourceNotFoundError):
            await handle_get_market_blob(
                shared_skill_id=shared_skill.id,
                blob_id=uuid.uuid4(),
                shared_skill_repo=shared_skill_repo,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )
