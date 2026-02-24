"""Tests for Skill aggregate remaining coverage."""


import pytest

from src.domain.aggregates.skill import Skill
from src.domain.value_objects.slug import Slug


class TestSkillRemaining:
    """Test Skill aggregate coverage (line 25)."""

    def should_raise_error_when_update_name_given_empty_string(self):
        """Test line 25: raise ValueError when updating with empty name."""
        # Given
        skill = Skill(name="Original Name", slug=Slug.from_name("Original Name"))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            skill.update_name("")

        assert "cannot be empty" in str(exc_info.value).lower()

    def should_raise_error_when_update_name_given_whitespace_only(self):
        """Test line 25: raise ValueError when updating with whitespace only."""
        # Given
        skill = Skill(name="Original Name", slug=Slug.from_name("Original Name"))

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            skill.update_name("   ")

        assert "cannot be empty" in str(exc_info.value).lower()
