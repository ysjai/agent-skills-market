"""
Update Tree Handler Integration Tests

Tests the handle_update_tree function to cover all execution paths:
- Successfully updating tree with new entries
- Handling non-existent tree
- Clearing existing entries before adding new ones
- Saving tree after updates
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.update_tree_handler import handle_update_tree
from src.domain.exceptions import ResourceNotFoundError
from src.infra.persistence.models.blob_model import BlobModel
from src.infra.persistence.models.tree_model import TreeModel
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository


@pytest_asyncio.fixture
async def test_blob(db_session: AsyncSession) -> BlobModel:
    """Create a test blob for entry references."""
    import hashlib

    content = b"test content"
    content_hash = hashlib.sha256(content).hexdigest()

    blob = BlobModel(
        id=uuid4(),
        content=content,
        content_hash=content_hash,
        size=len(content),
        compressed=False,
        reference_count=1,
    )
    db_session.add(blob)
    await db_session.flush()
    await db_session.refresh(blob)
    return blob


@pytest_asyncio.fixture
async def test_tree_with_entries(db_session: AsyncSession, test_blob: BlobModel) -> TreeModel:
    """Create a tree with existing entries."""
    tree = TreeModel(
        id=uuid4(),
        data={
            "entries": [
                {
                    "path": "old_file.txt",
                    "type": "blob",
                    "blob_id": str(test_blob.id),
                },
                {
                    "path": "another_old.py",
                    "type": "blob",
                    "blob_id": str(test_blob.id),
                },
            ]
        },
    )
    db_session.add(tree)
    await db_session.flush()
    await db_session.refresh(tree)
    return tree


@pytest_asyncio.fixture
async def test_tree_empty(db_session: AsyncSession) -> TreeModel:
    """Create an empty tree."""
    tree = TreeModel(
        id=uuid4(),
        data={"entries": []},
    )
    db_session.add(tree)
    await db_session.flush()
    await db_session.refresh(tree)
    return tree


class TestUpdateTreeHandler:
    """Update Tree Handler integration tests."""

    @pytest.mark.asyncio
    async def test_should_successfully_update_tree_with_new_entries(
        self,
        db_session: AsyncSession,
        test_tree_empty: TreeModel,
        test_blob: BlobModel,
    ):
        """Given an empty tree, when updating with new entries, then entries are added and tree is returned."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        new_entries = [
            {
                "path": "SKILL.md",
                "type": "blob",
                "blob_id": str(test_blob.id),
            },
            {
                "path": "examples/example.py",
                "type": "blob",
                "blob_id": str(test_blob.id),
            },
        ]

        # When
        result = await handle_update_tree(
            tree_repo=tree_repo,
            tree_id=test_tree_empty.id,
            entries=new_entries,
        )
        await db_session.flush()

        # Then
        assert result is not None
        assert len(result.entries) == 2
        paths = [str(entry.path) for entry in result.entries]
        assert "SKILL.md" in paths
        assert "examples/example.py" in paths

    @pytest.mark.asyncio
    async def test_should_clear_existing_entries_before_adding_new_ones(
        self,
        db_session: AsyncSession,
        test_tree_with_entries: TreeModel,
        test_blob: BlobModel,
    ):
        """Given a tree with existing entries, when updating, then old entries are cleared and replaced."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        assert len(test_tree_with_entries.data["entries"]) == 2  # Verify old entries exist

        new_entries = [
            {
                "path": "new_file.md",
                "type": "blob",
                "blob_id": str(test_blob.id),
            }
        ]

        # When
        result = await handle_update_tree(
            tree_repo=tree_repo,
            tree_id=test_tree_with_entries.id,
            entries=new_entries,
        )
        await db_session.flush()

        # Then
        assert result is not None
        assert len(result.entries) == 1
        assert str(result.entries[0].path) == "new_file.md"

    @pytest.mark.asyncio
    async def test_should_raise_resource_not_found_when_tree_does_not_exist(
        self,
        db_session: AsyncSession,
        test_blob: BlobModel,
    ):
        """Given a non-existent tree ID, when updating, then ResourceNotFoundError is raised."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        non_existent_tree_id = uuid4()
        entries = [
            {
                "path": "file.txt",
                "type": "blob",
                "blob_id": str(test_blob.id),
            }
        ]

        # When / Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_update_tree(
                tree_repo=tree_repo,
                tree_id=non_existent_tree_id,
                entries=entries,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        assert str(non_existent_tree_id) in exc_info.value.message

    @pytest.mark.asyncio
    async def test_should_save_tree_to_repository_after_updating(
        self,
        db_session: AsyncSession,
        test_tree_empty: TreeModel,
        test_blob: BlobModel,
    ):
        """Given valid entries, when updating tree, then changes are persisted to repository."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        new_entries = [
            {
                "path": "templates/template.py",
                "type": "blob",
                "blob_id": str(test_blob.id),
            }
        ]

        # When
        await handle_update_tree(
            tree_repo=tree_repo,
            tree_id=test_tree_empty.id,
            entries=new_entries,
        )
        await db_session.flush()

        # Then - Verify tree can be retrieved with new entries
        retrieved_tree = await tree_repo.get_by_id(test_tree_empty.id)
        assert retrieved_tree is not None
        assert len(retrieved_tree.entries) == 1
        assert str(retrieved_tree.entries[0].path) == "templates/template.py"
