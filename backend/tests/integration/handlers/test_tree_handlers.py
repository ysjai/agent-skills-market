"""
Tree Handlers Integration Tests

测试 Tree 相关的 Handler，提升覆盖率到 85%+

需覆盖场景:
- add_tree_file_handler: 使用 blob_id/content 添加文件、复用 Blob
- delete_tree_file_handler: 删除文件、保护 SKILL.md、级联删除、Blob 引用计数管理
- delete_tree_handler: 删除存在的 Tree、删除不存在的 Tree
- list_skill_files_handler: Skill 不存在、无 tree_id、获取文件列表
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.add_tree_file_handler import handle_add_tree_file
from src.application.handlers.delete_tree_file_handler import handle_delete_tree_file
from src.application.handlers.delete_tree_handler import handle_delete_tree
from src.application.handlers.list_skill_files_handler import handle_list_skill_files
from src.domain.exceptions import ResourceNotFoundError, ValidationError
from src.infra.persistence.models.blob_model import BlobModel
from src.infra.persistence.models.skill_model import SkillModel
from src.infra.persistence.models.tree_model import TreeModel
from src.infra.persistence.models.user_model import UserModel
from src.infra.persistence.repositories.sql_blob_repository import SqlBlobRepository
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository

@pytest_asyncio.fixture
async def test_tree_empty(db_session: AsyncSession) -> TreeModel:
    """创建空的测试 Tree"""
    tree = TreeModel(
        id=uuid4(),
        data={"entries": []},
    )
    db_session.add(tree)
    await db_session.flush()
    await db_session.refresh(tree)
    return tree

@pytest_asyncio.fixture
async def test_tree_with_entries(db_session: AsyncSession, test_blob: BlobModel) -> TreeModel:
    """创建包含 SKILL.md 和普通文件的测试 Tree"""
    tree = TreeModel(
        id=uuid4(),
        data={
            "entries": [
                {
                    "path": "SKILL.md",
                    "type": "blob",
                    "blob_id": str(test_blob.id),
                },
                {
                    "path": "examples/example1.py",
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
async def test_tree_with_directory(db_session: AsyncSession, test_blob: BlobModel) -> TreeModel:
    """创建包含目录结构的测试 Tree"""
    tree = TreeModel(
        id=uuid4(),
        data={
            "entries": [
                {
                    "path": "SKILL.md",
                    "type": "blob",
                    "blob_id": str(test_blob.id),
                },
                {
                    "path": "templates/",
                    "type": "tree",
                    "blob_id": None,
                },
                {
                    "path": "templates/template1.py",
                    "type": "blob",
                    "blob_id": str(test_blob.id),
                },
                {
                    "path": "templates/template2.py",
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
async def test_skill_no_tree(db_session: AsyncSession, test_user: UserModel) -> SkillModel:
    """创建无 Tree 的测试 Skill"""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="test-skill-no-tree",
        slug="test-skill-no-tree",
        description="A test skill without tree",
        tree_id=None,
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill

@pytest_asyncio.fixture
async def test_skill_with_tree(
    db_session: AsyncSession, test_user: UserModel, test_tree_with_entries: TreeModel
) -> SkillModel:
    """创建带 Tree 的测试 Skill"""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="test-skill-with-tree",
        slug="test-skill-with-tree",
        description="A test skill with tree",
        tree_id=test_tree_with_entries.id,
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill

@pytest_asyncio.fixture
async def test_blob(db_session: AsyncSession) -> BlobModel:
    """创建测试 Blob"""
    import hashlib

    content = b"test content for blob"
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

class TestAddTreeFileHandler:
    """Add Tree File Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_add_file_with_blob_id_increments_reference_count(
        self,
        db_session: AsyncSession,
        test_tree_empty: TreeModel,
        test_blob: BlobModel,
    ):
        """场景1: 使用 blob_id 添加文件 → 添加条目，递增引用计数"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        initial_ref_count = test_blob.reference_count

        updated_tree = await handle_add_tree_file(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_empty.id,
            path="new-file.txt",
            entry_type="blob",
            blob_id=test_blob.id,
            content=None,
        )
        await db_session.flush()
        assert len(updated_tree.entries) == 1
        assert str(updated_tree.entries[0].path) == "new-file.txt"
        assert updated_tree.entries[0].blob_id == test_blob.id
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == test_blob.id))
        saved_blob = result.scalar_one()
        assert saved_blob.reference_count == initial_ref_count + 1

    @pytest.mark.asyncio
    async def test_add_file_with_content_creates_new_blob(
        self,
        db_session: AsyncSession,
        test_tree_empty: TreeModel,
    ):
        """场景2: 使用 content 添加文件 → 创建新 Blob，添加条目"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content = "new file content to be hashed"

        updated_tree = await handle_add_tree_file(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_empty.id,
            path="content-file.txt",
            entry_type="blob",
            blob_id=None,
            content=content,
        )
        await db_session.flush()
        assert len(updated_tree.entries) == 1
        assert str(updated_tree.entries[0].path) == "content-file.txt"
        assert updated_tree.entries[0].blob_id is not None
        blob_id = updated_tree.entries[0].blob_id
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == blob_id))
        saved_blob = result.scalar_one()
        assert saved_blob.reference_count == 1

    @pytest.mark.asyncio
    async def test_add_file_with_existing_content_reuses_blob(
        self,
        db_session: AsyncSession,
        test_tree_empty: TreeModel,
        test_blob: BlobModel,
    ):
        """场景3: 相同 content 已存在 → 复用现有 Blob，递增引用计数"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        # 使用已存在 Blob 的内容
        existing_content = test_blob.content.decode("utf-8")
        initial_ref_count = test_blob.reference_count

        updated_tree = await handle_add_tree_file(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_empty.id,
            path="reused-content.txt",
            entry_type="blob",
            blob_id=None,
            content=existing_content,
        )
        await db_session.flush()
        assert len(updated_tree.entries) == 1
        assert str(updated_tree.entries[0].path) == "reused-content.txt"
        assert updated_tree.entries[0].blob_id == test_blob.id
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == test_blob.id))
        saved_blob = result.scalar_one()
        assert saved_blob.reference_count == initial_ref_count + 1

    @pytest.mark.asyncio
    async def test_add_file_to_nonexistent_tree_raises_not_found(
        self,
        db_session: AsyncSession,
    ):
        """场景4: Tree 不存在 → 抛出 ResourceNotFoundError"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_add_tree_file(
                tree_repo=tree_repo,
                blob_repo=blob_repo,
                tree_id=uuid4(),  # 不存在的 Tree ID
                path="file.txt",
                entry_type="blob",
                blob_id=uuid4(),
                content=None,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        await db_session.rollback()

class TestDeleteTreeFileHandler:
    """Delete Tree File Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_delete_file_decrements_reference_count(
        self,
        db_session: AsyncSession,
        test_tree_with_entries: TreeModel,
        test_blob: BlobModel,
    ):
        """场景1: 删除普通文件 → 删除条目，递减引用计数"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        test_blob.reference_count = 2
        await db_session.flush()

        updated_tree = await handle_delete_tree_file(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_with_entries.id,
            path="examples/example1.py",
        )
        await db_session.flush()
        assert len(updated_tree.entries) == 1
        assert str(updated_tree.entries[0].path) == "SKILL.md"
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == test_blob.id))
        saved_blob = result.scalar_one()
        assert saved_blob.reference_count == 1

    @pytest.mark.asyncio
    async def test_delete_skill_md_raises_validation_error(
        self,
        db_session: AsyncSession,
        test_tree_with_entries: TreeModel,
    ):
        """场景2: 尝试删除 SKILL.md → 抛出 ValidationError"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        with pytest.raises(ValidationError) as exc_info:
            await handle_delete_tree_file(
                tree_repo=tree_repo,
                blob_repo=blob_repo,
                tree_id=test_tree_with_entries.id,
                path="SKILL.md",
            )

        assert "Cannot delete SKILL.md" in str(exc_info.value)
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_directory_cascade_deletes_entries(
        self,
        db_session: AsyncSession,
        test_tree_with_directory: TreeModel,
        test_blob: BlobModel,
    ):
        """场景3: 删除目录 → 级联删除，返回所有 blob_ids"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        test_blob.reference_count = 3
        await db_session.flush()

        updated_tree = await handle_delete_tree_file(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_with_directory.id,
            path="templates/",
        )
        await db_session.flush()
        assert len(updated_tree.entries) == 1
        assert str(updated_tree.entries[0].path) == "SKILL.md"
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == test_blob.id))
        saved_blob = result.scalar_one()
        assert saved_blob.reference_count == 1  # 3 - 2 = 1

    @pytest.mark.asyncio
    async def test_delete_file_deletes_blob_when_ref_count_zero(
        self,
        db_session: AsyncSession,
        test_tree_with_entries: TreeModel,
    ):
        """场景4: Blob 引用计数归零 → 调用 blob_repo.delete"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)
        import hashlib

        content = b"content to be deleted"
        content_hash = hashlib.sha256(content).hexdigest()

        blob_to_delete = BlobModel(
            id=uuid4(),
            content=content,
            content_hash=content_hash,
            size=len(content),
            compressed=False,
            reference_count=1,
        )
        db_session.add(blob_to_delete)
        await db_session.flush()
        test_tree_with_entries.data = {
            "entries": [
                {
                    "path": "SKILL.md",
                    "type": "blob",
                    "blob_id": str(blob_to_delete.id),
                },
                {
                    "path": "delete-me.txt",
                    "type": "blob",
                    "blob_id": str(blob_to_delete.id),
                },
            ]
        }
        await db_session.flush()

        updated_tree = await handle_delete_tree_file(
            tree_repo=tree_repo,
            blob_repo=blob_repo,
            tree_id=test_tree_with_entries.id,
            path="delete-me.txt",
        )
        await db_session.flush()
        assert len(updated_tree.entries) == 1
        assert str(updated_tree.entries[0].path) == "SKILL.md"
        result = await db_session.execute(
            select(BlobModel).where(BlobModel.id == blob_to_delete.id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_file_from_nonexistent_tree_raises_not_found(
        self,
        db_session: AsyncSession,
    ):
        """场景5: Tree 不存在 → 抛出 ResourceNotFoundError"""
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_delete_tree_file(
                tree_repo=tree_repo,
                blob_repo=blob_repo,
                tree_id=uuid4(),  # 不存在的 Tree ID
                path="file.txt",
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        await db_session.rollback()

class TestDeleteTreeHandler:
    """Delete Tree Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_delete_existing_tree_succeeds(
        self,
        db_session: AsyncSession,
        test_tree_empty: TreeModel,
    ):
        """场景1: 删除存在的 Tree → 调用 tree_repo.delete"""
        tree_repo = SqlTreeRepository(db_session)
        result = await db_session.execute(
            select(TreeModel).where(TreeModel.id == test_tree_empty.id)
        )
        assert result.scalar_one_or_none() is not None
        await handle_delete_tree(
            tree_repo=tree_repo,
            tree_id=test_tree_empty.id,
        )
        await db_session.flush()
        result = await db_session.execute(
            select(TreeModel).where(TreeModel.id == test_tree_empty.id)
        )
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_tree_raises_not_found(
        self,
        db_session: AsyncSession,
    ):
        """场景2: 删除不存在的 Tree → 抛出 ResourceNotFoundError"""
        tree_repo = SqlTreeRepository(db_session)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_delete_tree(
                tree_repo=tree_repo,
                tree_id=uuid4(),  # 不存在的 Tree ID
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        await db_session.rollback()

class TestListSkillFilesHandler:
    """List Skill Files Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_list_files_skill_not_found_raises_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景1: Skill 不存在 → 抛出 ResourceNotFoundError"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_list_skill_files(
                skill_id=uuid4(),  # 不存在的 Skill ID
                user_id=test_user.id,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_list_files_other_users_skill_raises_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        another_user: UserModel,
        test_tree_with_entries: TreeModel,
    ):
        """场景2: Skill 属于其他用户 → 抛出 ResourceNotFoundError"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        other_skill = SkillModel(
            id=uuid4(),
            user_id=another_user.id,
            name="other-user-skill",
            slug="other-user-skill",
            description="Other user's skill",
            tree_id=test_tree_with_entries.id,
        )
        db_session.add(other_skill)
        await db_session.flush()

        # 尝试用 test_user 访问 other_user 的 Skill
        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_list_skill_files(
                skill_id=other_skill.id,
                user_id=test_user.id,
                skill_repo=skill_repo,
                tree_repo=tree_repo,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_list_files_no_tree_id_returns_empty_list(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
    ):
        """场景3: Skill 无 tree_id → 返回 (skill, [])"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)

        skill, entries = await handle_list_skill_files(
            skill_id=test_skill_no_tree.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )
        assert skill.id == test_skill_no_tree.id
        assert skill.name == test_skill_no_tree.name
        assert entries == []

    @pytest.mark.asyncio
    async def test_list_files_success_returns_entries(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_with_tree: SkillModel,
        test_tree_with_entries: TreeModel,
    ):
        """场景4: 成功获取文件列表 → 返回 (skill, tree.entries)"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)

        skill, entries = await handle_list_skill_files(
            skill_id=test_skill_with_tree.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )
        assert skill.id == test_skill_with_tree.id
        assert skill.name == test_skill_with_tree.name
        assert len(entries) == 2
        paths = [str(entry.path) for entry in entries]
        assert "SKILL.md" in paths
        assert "examples/example1.py" in paths

    @pytest.mark.asyncio
    async def test_list_files_tree_not_found_returns_empty_list(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景5: tree_id 对应的 Tree 不存在 → 返回 (skill, [])"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        nonexistent_tree_id = uuid4()
        skill_with_invalid_tree = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="invalid-tree-skill",
            slug="invalid-tree-skill",
            description="Skill with non-existent tree",
            tree_id=nonexistent_tree_id,
        )
        db_session.add(skill_with_invalid_tree)
        await db_session.flush()

        skill, entries = await handle_list_skill_files(
            skill_id=skill_with_invalid_tree.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
        )
        assert skill.id == skill_with_invalid_tree.id
        assert entries == []
