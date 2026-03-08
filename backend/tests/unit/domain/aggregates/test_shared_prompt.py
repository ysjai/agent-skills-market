import pytest
from uuid import uuid4
from src.domain.aggregates.shared_prompt import SharedPrompt
from src.domain.factories.shared_prompt_factory import SharedPromptFactory


def test_create_shared_prompt():
    prompt_id = uuid4()
    user_id = uuid4()
    sp = SharedPrompt(prompt_id=prompt_id, user_id=user_id)
    assert sp.prompt_id == prompt_id
    assert sp.user_id == user_id
    assert sp.status == "active"
    assert sp.like_count == 0
    assert sp.favorite_count == 0


def test_factory_create():
    prompt_id = uuid4()
    user_id = uuid4()
    sp = SharedPromptFactory.create(prompt_id=prompt_id, user_id=user_id, share_message="hello")
    assert sp.prompt_id == prompt_id
    assert sp.share_message == "hello"


def test_withdraw():
    pid = uuid4()
    sp = SharedPrompt(prompt_id=pid, user_id=uuid4())
    sp.withdraw()
    assert sp.status == "withdrawn"
    assert sp.prompt_id == pid  # withdraw keeps prompt_id


def test_mark_prompt_deleted():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.mark_prompt_deleted()
    assert sp.prompt_id is None
    assert sp.status == "withdrawn"


def test_increment_decrement_like():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.increment_like_count()
    assert sp.like_count == 1
    sp.decrement_like_count()
    assert sp.like_count == 0
    sp.decrement_like_count()
    assert sp.like_count == 0  # should not go negative


def test_increment_decrement_favorite():
    sp = SharedPrompt(prompt_id=uuid4(), user_id=uuid4())
    sp.increment_favorite_count()
    assert sp.favorite_count == 1
    sp.decrement_favorite_count()
    assert sp.favorite_count == 0


def test_invalid_status():
    with pytest.raises(ValueError):
        SharedPrompt(prompt_id=uuid4(), user_id=uuid4(), status="invalid")
