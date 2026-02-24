"""
Download Skill Handler Integration Tests

测试 download_skill_handler 的所有场景，提升覆盖率到 85%+

需覆盖场景:
- 无权下载他人 Skill → ForbiddenError
- Skill 无 Tree (claude 格式) → 返回空 markdown
- Skill 无 Tree (zip 格式) → 返回空 zip
- Claude 格式下载 → 返回 markdown 内容
- OpenCode 格式下载 → 返回 zip 内容
"""

import hashlib
import zipfile
from io import BytesIO
from uuid import uuid4

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.handlers.download_skill_handler import handle_download_skill
from src.domain.exceptions import ForbiddenError, ResourceNotFoundError
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
async def test_blob_1(db_session: AsyncSession) -> BlobModel:
    """创建测试 Blob 1"""
    content = b"Hello World from file 1!"
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
async def test_blob_2(db_session: AsyncSession) -> BlobModel:
    """创建测试 Blob 2"""
    content = "Content from file 2 with special chars: ñ 中文 🚀".encode()
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
async def test_tree_with_files(
    db_session: AsyncSession,
    test_blob_1: BlobModel,
    test_blob_2: BlobModel,
) -> TreeModel:
    """创建包含多个文件的 Tree"""
    tree = TreeModel(
        id=uuid4(),
        data={
            "entries": [
                {
                    "path": "README.md",
                    "type": "blob",
                    "blob_id": str(test_blob_1.id),
                },
                {
                    "path": "src/utils.py",
                    "type": "blob",
                    "blob_id": str(test_blob_2.id),
                },
            ]
        },
    )
    db_session.add(tree)
    await db_session.flush()
    await db_session.refresh(tree)
    return tree


@pytest_asyncio.fixture
async def test_skill_with_tree(
    db_session: AsyncSession,
    test_user: UserModel,
    test_tree_with_files: TreeModel,
) -> SkillModel:
    """创建带 Tree 的测试 Skill"""
    skill = SkillModel(
        id=uuid4(),
        user_id=test_user.id,
        name="test-skill-with-tree",
        slug="test-skill-with-tree",
        description="A test skill with tree",
        tree_id=test_tree_with_files.id,
    )
    db_session.add(skill)
    await db_session.flush()
    await db_session.refresh(skill)
    return skill


class TestDownloadSkillHandler:
    """Download Skill Handler 集成测试"""

    @pytest.mark.asyncio
    async def test_download_others_skill_raises_forbidden_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_other_user_skill: SkillModel,
    ):
        """场景1: 无权下载他人 Skill → ForbiddenError"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        with pytest.raises(ForbiddenError) as exc_info:
            await handle_download_skill(
                user_id=test_user.id,
                skill_id=test_other_user_skill.id,
                platform="claude",
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )

        assert exc_info.value.code == "FORBIDDEN"
        assert "not authorized" in exc_info.value.message.lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_download_skill_not_found_raises_resource_not_found_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景: 下载不存在的 Skill → ResourceNotFoundError"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        non_existent_skill_id = uuid4()

        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_download_skill(
                user_id=test_user.id,
                skill_id=non_existent_skill_id,
                platform="claude",
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        assert "not found" in exc_info.value.message.lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_download_skill_no_tree_claude_format_returns_empty_markdown(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
    ):
        """场景2: Skill 无 Tree (claude 格式) → 返回空 markdown"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=test_skill_no_tree.id,
            platform="claude",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert content_bytes == b""
        assert media_type == "text/markdown"
        assert filename == f"{test_skill_no_tree.slug}.md"

    @pytest.mark.asyncio
    async def test_download_skill_no_tree_zip_format_returns_empty_zip(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
    ):
        """场景3: Skill 无 Tree (zip 格式) → 返回空 zip"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=test_skill_no_tree.id,
            platform="opencode",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert content_bytes == b""
        assert media_type == "application/zip"
        assert filename == f"{test_skill_no_tree.slug}.zip"

    @pytest.mark.asyncio
    async def test_download_skill_no_tree_default_platform_returns_zip(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_no_tree: SkillModel,
    ):
        """场景: Skill 无 Tree (默认平台) → 返回空 zip"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=test_skill_no_tree.id,
            platform=None,  # 默认平台
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert content_bytes == b""
        assert media_type == "application/zip"
        assert filename == f"{test_skill_no_tree.slug}.zip"

    @pytest.mark.asyncio
    async def test_download_skill_claude_format_returns_markdown(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_with_tree: SkillModel,
        test_blob_1: BlobModel,
        test_blob_2: BlobModel,
    ):
        """场景4: Claude 格式下载 → 返回 markdown 内容"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=test_skill_with_tree.id,
            platform="claude",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert media_type == "text/markdown"
        assert filename == f"{test_skill_with_tree.slug}.md"

        content_str = content_bytes.decode("utf-8")
        # Verify markdown format
        assert "## File: README.md" in content_str
        assert "## File: src/utils.py" in content_str
        # Verify file contents are included
        assert "Hello World from file 1!" in content_str
        assert "Content from file 2 with special chars" in content_str
        # Verify code blocks
        assert "```" in content_str

    @pytest.mark.asyncio
    async def test_download_skill_opencode_format_returns_zip(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_skill_with_tree: SkillModel,
        test_blob_1: BlobModel,
        test_blob_2: BlobModel,
    ):
        """场景5: OpenCode 格式下载 → 返回 zip 内容"""
        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=test_skill_with_tree.id,
            platform="opencode",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert media_type == "application/zip"
        assert filename == f"{test_skill_with_tree.slug}.zip"

        # Verify zip content
        buffer = BytesIO(content_bytes)
        with zipfile.ZipFile(buffer, "r") as zf:
            file_list = zf.namelist()
            assert "README.md" in file_list
            assert "src/utils.py" in file_list

            # Verify file contents
            readme_content = zf.read("README.md")
            assert readme_content == b"Hello World from file 1!"

            utils_content = zf.read("src/utils.py")
            assert utils_content == "Content from file 2 with special chars: ñ 中文 🚀".encode()

    @pytest.mark.asyncio
    async def test_download_skill_tree_not_found_raises_error(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景: Skill 有 tree_id 但 Tree 不存在 → ResourceNotFoundError"""
        # Create a skill with a non-existent tree_id
        non_existent_tree_id = uuid4()
        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-missing-tree",
            slug="skill-missing-tree",
            description="Skill with missing tree",
            tree_id=non_existent_tree_id,
        )
        db_session.add(skill)
        await db_session.flush()
        await db_session.refresh(skill)

        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        with pytest.raises(ResourceNotFoundError) as exc_info:
            await handle_download_skill(
                user_id=test_user.id,
                skill_id=skill.id,
                platform="claude",
                skill_repo=skill_repo,
                tree_repo=tree_repo,
                blob_repo=blob_repo,
            )

        assert exc_info.value.code == "RESOURCE_NOT_FOUND"
        assert "tree not found" in exc_info.value.message.lower()
        await db_session.rollback()

    @pytest.mark.asyncio
    async def test_download_skill_skips_missing_blobs(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景: Blob 不存在时跳过 → 继续处理其他文件"""
        # Create a blob
        content = b"This blob exists"
        content_hash = hashlib.sha256(content).hexdigest()
        existing_blob = BlobModel(
            id=uuid4(),
            content=content,
            content_hash=content_hash,
            size=len(content),
            compressed=False,
            reference_count=1,
        )
        db_session.add(existing_blob)
        await db_session.flush()

        # Create a tree with one existing blob and one missing blob
        non_existent_blob_id = uuid4()
        tree = TreeModel(
            id=uuid4(),
            data={
                "entries": [
                    {
                        "path": "existing.txt",
                        "type": "blob",
                        "blob_id": str(existing_blob.id),
                    },
                    {
                        "path": "missing.txt",
                        "type": "blob",
                        "blob_id": str(non_existent_blob_id),
                    },
                ]
            },
        )
        db_session.add(tree)
        await db_session.flush()
        await db_session.refresh(tree)

        # Create skill
        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-with-missing-blob",
            slug="skill-with-missing-blob",
            description="Skill with missing blob",
            tree_id=tree.id,
        )
        db_session.add(skill)
        await db_session.flush()
        await db_session.refresh(skill)

        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        # Should succeed, skipping the missing blob
        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=skill.id,
            platform="claude",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert media_type == "text/markdown"
        content_str = content_bytes.decode("utf-8")
        # Should contain the existing file
        assert "## File: existing.txt" in content_str
        assert "This blob exists" in content_str
        # Should not contain the missing file
        assert "## File: missing.txt" not in content_str

    @pytest.mark.asyncio
    async def test_download_skill_with_directories_only_files_included(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
        test_blob_1: BlobModel,
    ):
        """场景: Tree 包含目录和文件 → 只包含文件内容"""
        # Create a tree with both directories and files
        tree = TreeModel(
            id=uuid4(),
            data={
                "entries": [
                    {
                        "path": "src/",
                        "type": "tree",
                    },
                    {
                        "path": "src/main.py",
                        "type": "blob",
                        "blob_id": str(test_blob_1.id),
                    },
                ]
            },
        )
        db_session.add(tree)
        await db_session.flush()
        await db_session.refresh(tree)

        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-with-dirs",
            slug="skill-with-dirs",
            description="Skill with directories",
            tree_id=tree.id,
        )
        db_session.add(skill)
        await db_session.flush()
        await db_session.refresh(skill)

        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        # Test markdown format
        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=skill.id,
            platform="claude",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert media_type == "text/markdown"
        content_str = content_bytes.decode("utf-8")
        # Should contain the file
        assert "## File: src/main.py" in content_str
        # Should not have directory entries (only directory path followed by newline)
        import re

        assert not re.search(r"## File: src/\s*\n", content_str)

        # Test zip format
        zip_bytes, zip_media_type, zip_filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=skill.id,
            platform="opencode",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert zip_media_type == "application/zip"
        buffer = BytesIO(zip_bytes)
        with zipfile.ZipFile(buffer, "r") as zf:
            file_list = zf.namelist()
            assert "src/main.py" in file_list
            # Directories might be implicitly created by zip

    @pytest.mark.asyncio
    async def test_download_skill_with_compressed_blob(
        self,
        db_session: AsyncSession,
        test_user: UserModel,
    ):
        """场景: Blob 是压缩的 → 正确解压内容"""
        import zlib

        # Create compressed blob
        raw_content = b"This content is compressed!"
        compressed_content = zlib.compress(raw_content, level=3)
        content_hash = hashlib.sha256(raw_content).hexdigest()

        compressed_blob = BlobModel(
            id=uuid4(),
            content=compressed_content,
            content_hash=content_hash,
            size=len(compressed_content),
            compressed=True,
            reference_count=1,
        )
        db_session.add(compressed_blob)
        await db_session.flush()

        tree = TreeModel(
            id=uuid4(),
            data={
                "entries": [
                    {
                        "path": "compressed.txt",
                        "type": "blob",
                        "blob_id": str(compressed_blob.id),
                    },
                ]
            },
        )
        db_session.add(tree)
        await db_session.flush()
        await db_session.refresh(tree)

        skill = SkillModel(
            id=uuid4(),
            user_id=test_user.id,
            name="skill-compressed",
            slug="skill-compressed",
            description="Skill with compressed blob",
            tree_id=tree.id,
        )
        db_session.add(skill)
        await db_session.flush()
        await db_session.refresh(skill)

        skill_repo = SqlSkillRepository(db_session)
        tree_repo = SqlTreeRepository(db_session)
        blob_repo = SqlBlobRepository(db_session)

        content_bytes, media_type, filename = await handle_download_skill(
            user_id=test_user.id,
            skill_id=skill.id,
            platform="claude",
            skill_repo=skill_repo,
            tree_repo=tree_repo,
            blob_repo=blob_repo,
        )

        assert media_type == "text/markdown"
        content_str = content_bytes.decode("utf-8")
        # Should contain the decompressed content
        assert "This content is compressed!" in content_str
