"""Prompt Handlers 单元测试套件。

本模块测试所有 10 个 Prompt 应用层 Handler，包括：
- handle_create_prompt — 创建 Prompt
- handle_list_prompts — 列表查询
- handle_get_prompt — 获取单个 Prompt
- handle_update_prompt — 更新 Prompt
- handle_delete_prompt — 删除 Prompt
- handle_publish_prompt_version — 发布版本
- handle_list_prompt_versions — 列出版本
- handle_get_prompt_version — 获取单个版本
- handle_import_prompt — 从 Markdown 导入
- handle_export_prompt — 导出为 Markdown

所有测试使用 AsyncMock/MagicMock 模拟 PromptRepository，不需要真实数据库。
测试设计遵循 Given-When-Then 模式。
"""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.application.handlers.create_prompt_handler import handle_create_prompt
from src.application.handlers.delete_prompt_handler import handle_delete_prompt
from src.application.handlers.export_prompt_handler import handle_export_prompt
from src.application.handlers.get_prompt_handler import handle_get_prompt
from src.application.handlers.get_prompt_version_handler import handle_get_prompt_version
from src.application.handlers.import_prompt_handler import handle_import_prompt
from src.application.handlers.list_prompt_versions_handler import handle_list_prompt_versions
from src.application.handlers.list_prompts_handler import handle_list_prompts
from src.application.handlers.publish_prompt_version_handler import handle_publish_prompt_version
from src.application.handlers.update_prompt_handler import handle_update_prompt
from src.domain.aggregates.prompt import Prompt
from src.domain.entities.prompt_version import PromptVersion
from src.domain.exceptions import ResourceNotFoundError, ValidationError


@pytest.fixture
def mock_prompt_repo():
    """Create a mock PromptRepository with all async methods."""
    repo = AsyncMock()
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.find_by_user = AsyncMock(return_value=[])
    repo.count_by_user = AsyncMock(return_value=0)
    repo.save_version = AsyncMock()
    repo.get_versions = AsyncMock(return_value=[])
    repo.get_version_by_id = AsyncMock(return_value=None)
    return repo


def _make_prompt(user_id=None, **kwargs):
    """Helper to create a Prompt with sensible defaults."""
    return Prompt(
        user_id=user_id or uuid4(),
        title=kwargs.get("title", "Test Prompt"),
        content=kwargs.get("content", "Test content"),
        description=kwargs.get("description"),
        tags=kwargs.get("tags", []),
        **{k: v for k, v in kwargs.items() if k not in ("title", "content", "description", "tags")},
    )


class TestHandleCreatePrompt:
    """handle_create_prompt Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_create_prompt_when_called_given_valid_input(self, mock_prompt_repo):
        # Given
        user_id = uuid4()

        # When
        result = await handle_create_prompt(
            user_id=user_id,
            title="My Prompt",
            content="Prompt content",
            prompt_repo=mock_prompt_repo,
            description="A description",
        )

        # Then
        assert isinstance(result, Prompt)
        assert result.title == "My Prompt"
        assert result.content == "Prompt content"
        assert result.description == "A description"
        assert result.user_id == user_id
        mock_prompt_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_create_prompt_with_tags_when_called_given_tags(self, mock_prompt_repo):
        # Given
        user_id = uuid4()

        # When
        result = await handle_create_prompt(
            user_id=user_id,
            title="Tagged Prompt",
            content="Content",
            prompt_repo=mock_prompt_repo,
            tags=["Python", "AI"],
        )

        # Then
        assert result.tags == ["python", "ai"]  # normalized to lowercase
        mock_prompt_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_create_prompt_without_tags_when_called_given_no_tags(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()

        # When
        result = await handle_create_prompt(
            user_id=user_id,
            title="Simple Prompt",
            content="Content",
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result.tags == []

    @pytest.mark.asyncio
    async def test_should_raise_error_when_called_given_empty_title(self, mock_prompt_repo):
        # Given
        user_id = uuid4()

        # When / Then
        with pytest.raises(ValidationError):
            await handle_create_prompt(
                user_id=user_id,
                title="",
                content="Content",
                prompt_repo=mock_prompt_repo,
            )


class TestHandleListPrompts:
    """handle_list_prompts Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_return_prompts_and_total_when_called_given_valid_user(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompts = [_make_prompt(user_id=user_id), _make_prompt(user_id=user_id)]
        mock_prompt_repo.find_by_user.return_value = prompts
        mock_prompt_repo.count_by_user.return_value = 2

        # When
        result_prompts, total = await handle_list_prompts(
            user_id=user_id,
            offset=0,
            limit=20,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert len(result_prompts) == 2
        assert total == 2
        mock_prompt_repo.find_by_user.assert_awaited_once_with(
            user_id,
            offset=0,
            limit=20,
            tag=None,
            search=None,
        )

    @pytest.mark.asyncio
    async def test_should_pass_tag_filter_when_called_given_tag(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        mock_prompt_repo.find_by_user.return_value = []
        mock_prompt_repo.count_by_user.return_value = 0

        # When
        await handle_list_prompts(
            user_id=user_id,
            offset=0,
            limit=10,
            prompt_repo=mock_prompt_repo,
            tag="python",
        )

        # Then
        mock_prompt_repo.find_by_user.assert_awaited_once_with(
            user_id,
            offset=0,
            limit=10,
            tag="python",
            search=None,
        )

    @pytest.mark.asyncio
    async def test_should_pass_search_filter_when_called_given_search(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        mock_prompt_repo.find_by_user.return_value = []
        mock_prompt_repo.count_by_user.return_value = 0

        # When
        await handle_list_prompts(
            user_id=user_id,
            offset=0,
            limit=10,
            prompt_repo=mock_prompt_repo,
            search="keyword",
        )

        # Then
        mock_prompt_repo.count_by_user.assert_awaited_once_with(
            user_id,
            tag=None,
            search="keyword",
        )

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_called_given_no_prompts(self, mock_prompt_repo):
        # Given
        user_id = uuid4()

        # When
        result_prompts, total = await handle_list_prompts(
            user_id=user_id,
            offset=0,
            limit=20,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result_prompts == []
        assert total == 0


class TestHandleGetPrompt:
    """handle_get_prompt Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_return_prompt_when_called_given_valid_id_and_owner(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        prompt.id = prompt_id
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_get_prompt(
            prompt_id=prompt_id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result.id == prompt_id
        assert result.user_id == user_id

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_id(self, mock_prompt_repo):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_get_prompt(
                prompt_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_wrong_user(self, mock_prompt_repo):
        # Given
        owner_id = uuid4()
        other_user_id = uuid4()
        prompt = _make_prompt(user_id=owner_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_get_prompt(
                prompt_id=prompt.id,
                user_id=other_user_id,
                prompt_repo=mock_prompt_repo,
            )


class TestHandleUpdatePrompt:
    """handle_update_prompt Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_update_title_when_called_given_new_title(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id, title="Old Title")
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_update_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
            title="New Title",
        )

        # Then
        assert result.title == "New Title"
        mock_prompt_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_update_content_when_called_given_new_content(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_update_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
            content="Updated content",
        )

        # Then
        assert result.content == "Updated content"

    @pytest.mark.asyncio
    async def test_should_update_description_when_called_given_new_description(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_update_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
            description="New description",
        )

        # Then
        assert result.description == "New description"

    @pytest.mark.asyncio
    async def test_should_update_tags_when_called_given_new_tags(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_update_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
            tags=["new-tag"],
        )

        # Then
        assert result.tags == ["new-tag"]

    @pytest.mark.asyncio
    async def test_should_update_multiple_fields_when_called_given_all_fields(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_update_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
            title="New Title",
            content="New Content",
            description="New Desc",
            tags=["tag1", "tag2"],
        )

        # Then
        assert result.title == "New Title"
        assert result.content == "New Content"
        assert result.description == "New Desc"
        assert result.tags == ["tag1", "tag2"]

    @pytest.mark.asyncio
    async def test_should_not_change_fields_when_called_given_none_values(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id, title="Original", content="Original content")
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_update_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then - no fields should change
        assert result.title == "Original"
        assert result.content == "Original content"

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_prompt(
        self, mock_prompt_repo
    ):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_update_prompt(
                prompt_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
                title="New Title",
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_wrong_user(self, mock_prompt_repo):
        # Given
        owner_id = uuid4()
        other_user_id = uuid4()
        prompt = _make_prompt(user_id=owner_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_update_prompt(
                prompt_id=prompt.id,
                user_id=other_user_id,
                prompt_repo=mock_prompt_repo,
                title="Hacked Title",
            )


class TestHandleDeletePrompt:
    """handle_delete_prompt Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_delete_prompt_when_called_given_valid_id_and_owner(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        await handle_delete_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        mock_prompt_repo.delete.assert_awaited_once_with(prompt.id)

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_prompt(
        self, mock_prompt_repo
    ):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_delete_prompt(
                prompt_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_wrong_user(self, mock_prompt_repo):
        # Given
        owner_id = uuid4()
        other_user_id = uuid4()
        prompt = _make_prompt(user_id=owner_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_delete_prompt(
                prompt_id=prompt.id,
                user_id=other_user_id,
                prompt_repo=mock_prompt_repo,
            )


class TestHandlePublishPromptVersion:
    """handle_publish_prompt_version Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_publish_version_when_called_given_valid_prompt(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id, title="My Prompt", content="Content")
        original_version = prompt.version
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        version = await handle_publish_prompt_version(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert isinstance(version, PromptVersion)
        assert version.version_number == original_version
        assert version.title == "My Prompt"
        assert version.content == "Content"
        mock_prompt_repo.save_version.assert_awaited_once()
        mock_prompt_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_prompt(
        self, mock_prompt_repo
    ):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_publish_prompt_version(
                prompt_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_wrong_user(self, mock_prompt_repo):
        # Given
        owner_id = uuid4()
        other_user_id = uuid4()
        prompt = _make_prompt(user_id=owner_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_publish_prompt_version(
                prompt_id=prompt.id,
                user_id=other_user_id,
                prompt_repo=mock_prompt_repo,
            )


class TestHandleListPromptVersions:
    """handle_list_prompt_versions Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_return_versions_when_called_given_valid_prompt(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        prompt_id = prompt.id
        versions = [
            PromptVersion(prompt_id=prompt_id, version_number=1),
            PromptVersion(prompt_id=prompt_id, version_number=2),
        ]
        mock_prompt_repo.get_by_id.return_value = prompt
        mock_prompt_repo.get_versions.return_value = versions

        # When
        result = await handle_list_prompt_versions(
            prompt_id=prompt_id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert len(result) == 2
        mock_prompt_repo.get_versions.assert_awaited_once_with(prompt_id)

    @pytest.mark.asyncio
    async def test_should_return_empty_list_when_called_given_no_versions(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt
        mock_prompt_repo.get_versions.return_value = []

        # When
        result = await handle_list_prompt_versions(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result == []

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_prompt(
        self, mock_prompt_repo
    ):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_list_prompt_versions(
                prompt_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
            )


class TestHandleGetPromptVersion:
    """handle_get_prompt_version Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_return_version_when_called_given_valid_ids(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt_id = uuid4()
        version_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        prompt.id = prompt_id
        version = PromptVersion(id=version_id, prompt_id=prompt_id, version_number=1)
        mock_prompt_repo.get_by_id.return_value = prompt
        mock_prompt_repo.get_version_by_id.return_value = version

        # When
        result = await handle_get_prompt_version(
            prompt_id=prompt_id,
            version_id=version_id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result.id == version_id
        assert result.prompt_id == prompt_id

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_prompt(
        self, mock_prompt_repo
    ):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_get_prompt_version(
                prompt_id=uuid4(),
                version_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_version(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt
        mock_prompt_repo.get_version_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_get_prompt_version(
                prompt_id=prompt.id,
                version_id=uuid4(),
                user_id=user_id,
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_version_from_different_prompt(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt_id = uuid4()
        other_prompt_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        prompt.id = prompt_id
        version = PromptVersion(prompt_id=other_prompt_id, version_number=1)
        mock_prompt_repo.get_by_id.return_value = prompt
        mock_prompt_repo.get_version_by_id.return_value = version

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_get_prompt_version(
                prompt_id=prompt_id,
                version_id=version.id,
                user_id=user_id,
                prompt_repo=mock_prompt_repo,
            )


class TestHandleImportPrompt:
    """handle_import_prompt Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_import_prompt_when_called_given_valid_markdown(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        markdown = """---
title: My Imported Prompt
description: A test description
tags: [python, ai]
---

This is the prompt content.
It can span multiple lines."""

        # When
        result = await handle_import_prompt(
            user_id=user_id,
            markdown_content=markdown,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert isinstance(result, Prompt)
        assert result.title == "My Imported Prompt"
        assert result.description == "A test description"
        assert result.tags == ["python", "ai"]
        assert "This is the prompt content." in result.content
        assert "It can span multiple lines." in result.content
        mock_prompt_repo.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_should_import_prompt_when_called_given_title_only(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        markdown = """---
title: Minimal Prompt
---

Content here."""

        # When
        result = await handle_import_prompt(
            user_id=user_id,
            markdown_content=markdown,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result.title == "Minimal Prompt"
        assert result.description is None
        assert result.tags == []

    @pytest.mark.asyncio
    async def test_should_raise_error_when_called_given_missing_frontmatter(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        markdown = "Just some plain text without frontmatter."

        # When / Then
        with pytest.raises(ValidationError):
            await handle_import_prompt(
                user_id=user_id,
                markdown_content=markdown,
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_error_when_called_given_missing_title_in_frontmatter(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        markdown = """---
description: No title here
---

Content."""

        # When / Then
        with pytest.raises(ValidationError):
            await handle_import_prompt(
                user_id=user_id,
                markdown_content=markdown,
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_error_when_called_given_unclosed_frontmatter(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        markdown = """---
title: Broken
This never closes."""

        # When / Then
        with pytest.raises(ValidationError):
            await handle_import_prompt(
                user_id=user_id,
                markdown_content=markdown,
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_import_with_empty_content_when_called_given_no_body(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        markdown = """---
title: No Content Prompt
---
"""

        # When
        result = await handle_import_prompt(
            user_id=user_id,
            markdown_content=markdown,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert result.title == "No Content Prompt"
        assert result.content == ""


class TestHandleExportPrompt:
    """handle_export_prompt Handler 测试场景。"""

    @pytest.mark.asyncio
    async def test_should_export_markdown_when_called_given_valid_prompt(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(
            user_id=user_id,
            title="Export Prompt",
            content="Exported content",
            description="Export description",
            tags=["python", "ai"],
        )
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_export_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert isinstance(result, str)
        assert result.startswith("---\n")
        assert "title: Export Prompt" in result
        assert "description: Export description" in result
        assert "Exported content" in result
        assert "---" in result

    @pytest.mark.asyncio
    async def test_should_include_tags_in_export_when_called_given_prompt_with_tags(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id, tags=["tag1", "tag2"])
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_export_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert "tag1" in result
        assert "tag2" in result

    @pytest.mark.asyncio
    async def test_should_include_version_in_export_when_called_given_prompt(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_export_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert "version:" in result

    @pytest.mark.asyncio
    async def test_should_omit_description_when_called_given_prompt_without_description(
        self, mock_prompt_repo
    ):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id, description=None)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_export_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert "description" not in result

    @pytest.mark.asyncio
    async def test_should_omit_tags_when_called_given_prompt_without_tags(self, mock_prompt_repo):
        # Given
        user_id = uuid4()
        prompt = _make_prompt(user_id=user_id, tags=[])
        mock_prompt_repo.get_by_id.return_value = prompt

        # When
        result = await handle_export_prompt(
            prompt_id=prompt.id,
            user_id=user_id,
            prompt_repo=mock_prompt_repo,
        )

        # Then
        assert "tags" not in result

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_nonexistent_prompt(
        self, mock_prompt_repo
    ):
        # Given
        mock_prompt_repo.get_by_id.return_value = None

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_export_prompt(
                prompt_id=uuid4(),
                user_id=uuid4(),
                prompt_repo=mock_prompt_repo,
            )

    @pytest.mark.asyncio
    async def test_should_raise_not_found_when_called_given_wrong_user(self, mock_prompt_repo):
        # Given
        owner_id = uuid4()
        other_user_id = uuid4()
        prompt = _make_prompt(user_id=owner_id)
        mock_prompt_repo.get_by_id.return_value = prompt

        # When / Then
        with pytest.raises(ResourceNotFoundError):
            await handle_export_prompt(
                prompt_id=prompt.id,
                user_id=other_user_id,
                prompt_repo=mock_prompt_repo,
            )
