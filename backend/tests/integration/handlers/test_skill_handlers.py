"""
Skill Handlers Integration Tests

测试 Skill 相关的 Handler，提升覆盖率到 85%+

需覆盖场景:
- update_skill_handler: 名称冲突、权限验证、部分字段更新
- delete_skill_handler: 级联删除、权限验证、Blob引用计数管理
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.delete_skill_handler import handle_delete_skill
from src.application.handlers.update_skill_handler import handle_update_skill
from src.domain.exceptions import ForbiddenError, ResourceConflictError
from src.infra.persistence.models.blob_model import BlobModel
from src.infra.persistence.models.skill_model import SkillModel
from src.infra.persistence.models.tree_model import TreeModel
from src.infra.persistence.models.user_model import UserModel
from src.infra.persistence.repositories.sql_blob_repository import SqlBlobRepository
from src.infra.persistence.repositories.sql_skill_repository import SqlSkillRepository
from src.infra.persistence.repositories.sql_tree_repository import SqlTreeRepository


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
    db_session: AsyncSession, test_user: UserModel
) -> tuple[SkillModel, TreeModel]:
    """创建带 Tree 的测试 Skill"""
    tree = TreeModel(
        id=uuid4(),
        data={"entries": []},
    )
    db_session.add(tree)
    await db_session.flush()
    await db_session.refresh(tree)
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="test-skill-with-tree",
        slug="test-skill-with-tree",
        description="A test skill with tree",
        tree_id=tree.id,
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)

    return skill, tree

@pytest_asyncio.fixture
async def test_another_skill(db_session: AsyncSession, test_user: UserModel) -> SkillModel:
    """创建用户的另一个 Skill（用于名称冲突测试）"""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="another-existing-skill",
        slug="another-existing-skill",
        description="Another existing skill",
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill

@pytest_asyncio.fixture
async def test_other_user_skill(db_session: AsyncSession, another_user: UserModel) -> SkillModel:
    """创建其他用户的 Skill（用于权限测试）"""
    skill = SkillModel(
        id=uuid4(),
        user_id=another_user.id,
        name="other-user-skill",
        slug="other-user-skill",
        description="Other user's skill",
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

@pytest_asyncio.fixture
async def test_tree_with_blob(db_session: AsyncSession, test_blob: BlobModel) -> TreeModel:
    """创建包含 Blob 引用的 Tree"""
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

class TestUpdateSkillHandler:
    """Update Skill Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_update_name_conflict_raises_resource_conflict_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
        test_another_skill: SkillModel,
    ):
        """场景1: 更新名称时与其他 Skill 冲突 → ResourceConflictError"""
        skill_repo = SqlSkillRepository(db_session)

        # 尝试将 skill 的名称改为 another_skill 的名称（冲突）
        with pytest.raises(ResourceConflictError) as exc_info:
            await handle_update_skill(
                skill_id=test_skill_no_tree.id,
                user_id=test_user.id,
                name=test_another_skill.name,  # 已存在的名称
                description=None,
                is_public=None,
                tree_id=None,
                skill_repo=skill_repo,
            )

        assert exc_info.value.code == "RESOURCE_CONFLICT"
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_others_skill_raises_forbidden_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_other_user_skill: SkillModel,
    ):
        """场景2: 无权更新他人 Skill → ForbiddenError"""
        skill_repo = SqlSkillRepository(db_session)

        # 尝试更新其他用户的 Skill
        with pytest.raises(ForbiddenError) as exc_info:
            await handle_update_skill(
                skill_id=test_other_user_skill.id,
                user_id=test_user.id,  # 当前用户 ID
                name="new-name",
                description=None,
                is_public=None,
                tree_id=None,
                skill_repo=skill_repo,
            )

        assert exc_info.value.code == "FORBIDDEN"
        assert "not authorized" in exc_info.value.message.lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_update_description_only(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
    ):
        """场景3: 仅更新 description → 只更新 description 字段"""
        skill_repo = SqlSkillRepository(db_session)

        original_name = test_skill_no_tree.name
        original_slug = test_skill_no_tree.slug
        original_is_public = test_skill_no_tree.is_public
        original_tree_id = test_skill_no_tree.tree_id

        updated_skill = await handle_update_skill(
            skill_id=test_skill_no_tree.id,
            user_id=test_user.id,
            name=None,
            description="Updated description only",
            is_public=None,
            tree_id=None,
            skill_repo=skill_repo,
        )
        assert updated_skill.description == "Updated description only"
        assert updated_skill.name == original_name
        assert str(updated_skill.slug) == original_slug
        assert updated_skill.is_public == original_is_public
        assert updated_skill.tree_id == original_tree_id
        await db_session.flush()
        result = await db_session.execute(
            select(SkillModel).where(SkillModel.id == test_skill_no_tree.id)
        )
        saved_skill = result.scalar_one()
        assert saved_skill.description == "Updated description only"
        assert saved_skill.name == original_name

    @pytest.mark.asyncio
    async def test_update_is_public_only(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
    ):
        """场景4: 仅更新 is_public → 只更新公开状态"""
        skill_repo = SqlSkillRepository(db_session)
        assert test_skill_no_tree.is_public is False

        original_name = test_skill_no_tree.name
        original_description = test_skill_no_tree.description

        updated_skill = await handle_update_skill(
            skill_id=test_skill_no_tree.id,
            user_id=test_user.id,
            name=None,
            description=None,
            is_public=True,  # 设置为公开
            tree_id=None,
            skill_repo=skill_repo,
        )
        assert updated_skill.is_public is True
        assert updated_skill.name == original_name
        assert updated_skill.description == original_description
        await db_session.flush()
        result = await db_session.execute(
            select(SkillModel).where(SkillModel.id == test_skill_no_tree.id)
        )
        saved_skill = result.scalar_one()
        assert saved_skill.is_public is True

    @pytest.mark.asyncio
    async def test_update_tree_id_only(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
        test_tree_with_blob: TreeModel,
    ):
        """场景5: 仅更新 tree_id → 只关联新 Tree"""
        skill_repo = SqlSkillRepository(db_session)
        assert test_skill_no_tree.tree_id is None

        original_name = test_skill_no_tree.name
        original_description = test_skill_no_tree.description
        original_is_public = test_skill_no_tree.is_public

        updated_skill = await handle_update_skill(
            skill_id=test_skill_no_tree.id,
            user_id=test_user.id,
            name=None,
            description=None,
            is_public=None,
            tree_id=test_tree_with_blob.id,  # 关联新 Tree
            skill_repo=skill_repo,
        )
        assert updated_skill.tree_id == test_tree_with_blob.id
        assert updated_skill.name == original_name
        assert updated_skill.description == original_description
        assert updated_skill.is_public == original_is_public
        await db_session.flush()
        result = await db_session.execute(
            select(SkillModel).where(SkillModel.id == test_skill_no_tree.id)
        )
        saved_skill = result.scalar_one()
        assert saved_skill.tree_id == test_tree_with_blob.id

class TestDeleteSkillHandler:
    """Delete Skill Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_delete_skill_with_tree_decrements_blob_ref_count(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景1: 删除带 Tree 的 Skill → 递减 Blob 引用计数，删除 Tree"""
        import hashlib

        content = b"content for ref count test"
        content_hash = hashlib.sha256(content).hexdigest()

        blob = BlobModel(
            id=uuid4(),
            content=content,
            content_hash=content_hash,
            size=len(content),
            compressed=False,
            reference_count=2,  # 初始引用计数为 2
        )
        db_session.add(blob)
        await db_session.flush()
        tree = TreeModel(
            id=uuid4(),
            data={
                "entries": [
                    {
                        "path": "test.txt",
                        "type": "blob",
                        "blob_id": str(blob.id),
                    }
                ]
            },
        )
        db_session.add(tree)
        await db_session.flush()
        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-with-tree",
            slug="skill-with-tree",
            description="Skill with tree",
            tree_id=tree.id,
        )
        db_session.add(skill)
        await db_session.flush()

        # 执行删除
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        await handle_delete_skill(
            skill_id=skill.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )
        await db_session.flush()
        result = await db_session.execute(select(SkillModel).where(SkillModel.id == skill.id))
        assert result.scalar_one_or_none() is None
        result = await db_session.execute(select(TreeModel).where(TreeModel.id == tree.id))
        assert result.scalar_one_or_none() is None
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == blob.id))
        saved_blob = result.scalar_one()
        assert saved_blob.reference_count == 1  # 2 - 1 = 1

    @pytest.mark.asyncio
    async def test_delete_skill_without_tree_only_deletes_skill(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景2: 删除无 Tree 的 Skill → 仅删除 Skill"""
        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-no-tree",
            slug="skill-no-tree",
            description="Skill without tree",
            tree_id=None,
        )
        db_session.add(skill)
        await db_session.flush()

        # 执行删除
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        await handle_delete_skill(
            skill_id=skill.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )
        await db_session.flush()
        result = await db_session.execute(select(SkillModel).where(SkillModel.id == skill.id))
        assert result.scalar_one_or_none() is None

    @pytest.mark.asyncio
    async def test_delete_others_skill_raises_forbidden_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_other_user_skill: SkillModel,
    ):
        """场景3: 无权删除他人 Skill → ForbiddenError"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        # 尝试删除其他用户的 Skill
        with pytest.raises(ForbiddenError) as exc_info:
            await handle_delete_skill(
                skill_id=test_other_user_skill.id,
                user_id=test_user.id,  # 当前用户 ID
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )

        assert exc_info.value.code == "FORBIDDEN"
        assert "not authorized" in exc_info.value.message.lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_delete_skill_deletes_blob_when_ref_count_zero(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景4: Blob 引用计数归零后删除 → 调用 blob_repo.delete(blob_id)"""
        import hashlib

        content = b"content to be deleted"
        content_hash = hashlib.sha256(content).hexdigest()

        blob = BlobModel(
            id=uuid4(),
            content=content,
            content_hash=content_hash,
            size=len(content),
            compressed=False,
            reference_count=1,  # 初始引用计数为 1，删除后归零
        )
        db_session.add(blob)
        await db_session.flush()
        tree = TreeModel(
            id=uuid4(),
            data={
                "entries": [
                    {
                        "path": "delete-me.txt",
                        "type": "blob",
                        "blob_id": str(blob.id),
                    }
                ]
            },
        )
        db_session.add(tree)
        await db_session.flush()
        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-delete-blob",
            slug="skill-delete-blob",
            description="Skill that will delete blob",
            tree_id=tree.id,
        )
        db_session.add(skill)
        await db_session.flush()

        # 执行删除
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        await handle_delete_skill(
            skill_id=skill.id,
            user_id=test_user.id,
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )
        await db_session.flush()
        result = await db_session.execute(select(SkillModel).where(SkillModel.id == skill.id))
        assert result.scalar_one_or_none() is None
        result = await db_session.execute(select(TreeModel).where(TreeModel.id == tree.id))
        assert result.scalar_one_or_none() is None
        result = await db_session.execute(select(BlobModel).where(BlobModel.id == blob.id))
        assert result.scalar_one_or_none() is None
