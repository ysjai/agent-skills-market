import pytest
from uuid import uuid4
from src.domain.aggregates.prompt_favorite import PromptFavorite
from src.domain.factories.prompt_favorite_factory import PromptFavoriteFactory
from unittest.mock import MagicMock


def test_create_prompt_favorite():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="# Hello",
        snapshot_description="A test prompt",
        snapshot_tags=["python", "test"],
        snapshot_author_name="user1",
        snapshot_version=3,
    )
    assert pf.snapshot_status == "active"
    assert pf.snapshot_version == 3


def test_mark_prompt_withdrawn():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="content",
        snapshot_author_name="user1",
        snapshot_version=1,
    )
    pf.mark_prompt_withdrawn()
    assert pf.snapshot_status == "prompt_withdrawn"


def test_mark_prompt_deleted():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="content",
        snapshot_author_name="user1",
        snapshot_version=1,
    )
    pf.mark_prompt_deleted()
    assert pf.snapshot_status == "prompt_deleted"
    assert pf.shared_prompt_id is None


def test_is_version_stale():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Test",
        snapshot_content="content",
        snapshot_author_name="user1",
        snapshot_version=3,
    )
    assert pf.is_version_stale(5) is True
    assert pf.is_version_stale(3) is False
    assert pf.is_version_stale(2) is False


def test_refresh_snapshot():
    pf = PromptFavorite(
        user_id=uuid4(),
        shared_prompt_id=uuid4(),
        snapshot_title="Old Title",
        snapshot_content="Old Content",
        snapshot_description="Old Desc",
        snapshot_tags=["old"],
        snapshot_author_name="user1",
        snapshot_version=1,
    )
    pf.refresh_snapshot(
        title="New Title",
        content="New Content",
        description="New Desc",
        tags=["new", "updated"],
        version=5,
    )
    assert pf.snapshot_title == "New Title"
    assert pf.snapshot_content == "New Content"
    assert pf.snapshot_description == "New Desc"
    assert pf.snapshot_tags == ["new", "updated"]
    assert pf.snapshot_version == 5


def test_factory_create():
    prompt = MagicMock()
    prompt.title = "My Prompt"
    prompt.content = "# Hello World"
    prompt.description = "A great prompt"
    prompt.tags = ["python"]
    prompt.version = 3

    user = MagicMock()
    user.username = "author1"

    shared_prompt_id = uuid4()
    user_id = uuid4()

    pf = PromptFavoriteFactory.create(
        user_id=user_id,
        shared_prompt_id=shared_prompt_id,
        prompt=prompt,
        author=user,
    )
    assert pf.user_id == user_id
    assert pf.shared_prompt_id == shared_prompt_id
    assert pf.snapshot_title == "My Prompt"
    assert pf.snapshot_content == "# Hello World"
    assert pf.snapshot_tags == ["python"]
    assert pf.snapshot_version == 3
    assert pf.snapshot_author_name == "author1"
