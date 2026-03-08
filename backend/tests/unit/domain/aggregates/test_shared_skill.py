from __future__ import annotations

import pytest
from uuid import uuid4

from src.domain.aggregates.shared_skill import SharedSkill
from src.domain.exceptions import ValidationError


def test_create_shared_skill_without_snapshots():
    skill_id = uuid4()
    user_id = uuid4()
    category_id = uuid4()
    ss = SharedSkill(
        skill_id=skill_id,
        user_id=user_id,
        category_id=category_id,
    )
    assert ss.skill_id == skill_id
    assert ss.user_id == user_id
    assert ss.status == "active"
    assert ss.like_count == 0
    assert "snapshot_name" not in ss.__dataclass_fields__


def test_withdraw_sets_status_and_keeps_skill_id():
    sid = uuid4()
    ss = SharedSkill(skill_id=sid, user_id=uuid4(), category_id=uuid4())
    ss.withdraw()
    assert ss.status == "withdrawn"
    assert ss.skill_id == sid  # withdraw keeps skill_id


def test_withdraw_is_idempotent():
    sid = uuid4()
    ss = SharedSkill(skill_id=sid, user_id=uuid4(), category_id=uuid4())
    ss.withdraw()
    ss.withdraw()
    assert ss.status == "withdrawn"
    assert ss.skill_id == sid  # withdraw keeps skill_id


def test_mark_skill_deleted_clears_skill_id_and_withdraws():
    ss = SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4())
    ss.mark_skill_deleted()
    assert ss.skill_id is None
    assert ss.status == "withdrawn"


def test_mark_skill_deleted_idempotent():
    ss = SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4())
    ss.mark_skill_deleted()
    ss.mark_skill_deleted()
    assert ss.skill_id is None
    assert ss.status == "withdrawn"


def test_increment_decrement_like():
    ss = SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4())
    ss.increment_like_count()
    assert ss.like_count == 1
    ss.decrement_like_count()
    assert ss.like_count == 0


def test_decrement_below_zero_raises():
    ss = SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4())
    with pytest.raises(ValidationError):
        ss.decrement_like_count()


def test_invalid_status_raises():
    with pytest.raises(ValidationError):
        SharedSkill(skill_id=uuid4(), user_id=uuid4(), category_id=uuid4(), status="invalid")
