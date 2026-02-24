"""
Update Tree File Content Handler Integration Tests

Tests the handle_update_tree_file_content function to cover:
- Successfully updating file content with new blob
- Reusing existing blob when content checksum matches
- Creating new blob when content is different
- Handling non-existent tree
"""

import hashlib
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.update_tree_file_content_handler import (
    handle_update_tree_file_content,
)
from src.domain.exceptions import ResourceNotFoundError
from src.infra.persistence.models.blob_model import BlobModel
from src.infra.persistence.models.tree_model import TreeModel
from src.infra.persistence.repositories.sql_blob_repository import SqlBlobRepository
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository


@pytest_asyncio.fixture
async def test_blob(db_session: AsyncSession) -> BlobModel:
    """Create a test blob with known content."""
    content = b"existing blob content"
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
async def test_tree_with_file(db_session: AsyncSession, test_blob: BlobModel) -> TreeModel:
    """Create a tree with an existing file entry."""
    tree = TreeModel(
        id=uuid4(),
        data={
            "entries": [
                {
                    "path": "test.txt",
                    "type": "blob",
                    "blob_id": str(test_blob.id),
                }
            ]
        },
    )
    db_session.add(tree)
    await db_session.flush()
    await db_session.refresh(tree)
    return tree


class TestUpdateTreeFileContentHandler:
    """Update Tree File Content Handler integration tests."""

    @pytest.mark.asyncio
    async def test_should_successfully_update_file_content_with_new_blob(
        self,
        db_session: AsyncSession,
        test_tree_with_file: TreeModel,
        test_blob: BlobModel,
    ):
        """Given a tree with a file, when updating with new content, then new blob is created and file is updated."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        new_content = "new content for the file"

        # When
        result = await handle_update_tree_file_content(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_with_file.id,
            path="test.txt",
            content=new_content,
        )
        await db_session.flush()

        # Then
        assert result is not None
        # Verify the entry still exists
        assert len(result.entries) == 1
        # Verify a new blob was created for the new content
        new_content_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
        result_blob = await db_session.execute(
            select(BlobModel).where(BlobModel.content_hash == new_content_hash)
        )
        saved_blob = result_blob.scalar_one_or_none()
        assert saved_blob is not None
        assert saved_blob.content == new_content.encode("utf-8")

    @pytest.mark.asyncio
    async def test_should_reuse_existing_blob_when_checksum_matches(
        self,
        db_session: AsyncSession,
        test_tree_with_file: TreeModel,
        test_blob: BlobModel,
    ):
        """Given content that matches existing blob, when updating, then existing blob is reused."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        # Use the same content as the existing blob
        existing_content = test_blob.content.decode("utf-8")

        # When
        result = await handle_update_tree_file_content(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_with_file.id,
            path="test.txt",
            content=existing_content,
        )
        await db_session.flush()

        # Then
        assert result is not None
        assert len(result.entries) == 1
        # Verify the existing blob ID is reused
        assert result.entries[0].blob_id == test_blob.id

    @pytest.mark.asyncio
    async def test_should_raise_resource_not_found_when_tree_does_not_exist(
        self,
        db_session: AsyncSession,
    ):
        """Given a non-existent tree ID, when updating file content, then ResourceNotFoundError is raised."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        non_existent_tree_id = uuid4()

        # When / Then
        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_update_tree_file_content(
                tree_repo=tree_repo,
                blob_repo=blob_repo,
                tree_id=non_existent_tree_id,
                path="file.txt",
                content="some content",
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        assert str(non_existent_tree_id) in exc_info.value.message

    @pytest.mark.asyncio
    async def test_should_save_tree_after_updating_file_content(
        self,
        db_session: AsyncSession,
        test_tree_with_file: TreeModel,
    ):
        """Given valid update, when processing completes, then tree changes are persisted."""
        # Given
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        new_content = "persisted content"

        # When
        result = await handle_update_tree_file_content(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_with_file.id,
            path="test.txt",
            content=new_content,
        )
        await db_session.flush()

        # Then - Verify tree is persisted with updated blob
        retrieved_tree = await tree_repo.get_by_id(test_tree_with_file.id)
        assert retrieved_tree is not None
        assert len(retrieved_tree.entries) == 1
        # Verify the blob was updated
        new_content_hash = hashlib.sha256(new_content.encode("utf-8")).hexdigest()
        result_blob = await db_session.execute(
            select(BlobModel).where(BlobModel.content_hash == new_content_hash)
        )
        saved_blob = result_blob.scalar_one_or_none()
        assert saved_blob is not None
        assert retrieved_tree.entries[0].blob_id == saved_blob.id
