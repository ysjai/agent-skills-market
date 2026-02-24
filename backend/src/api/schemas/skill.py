from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.aggregates.skill import Skill


class CreateSkillReq(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    name: str = Field(
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
        description="Skill name - only lowercase letters, numbers and hyphens allowed",
    )
    slug: str = Field(min_length=1, max_length=255)
    description: str = Field(
        min_length=1,
        max_length=1000,
        description="Skill description - required",
    )


class CreateSkillResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    slug: str
    description: str | None
    tree_id: UUID | None
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, skill: Skill) -> CreateSkillResp:
        return cls(
            id=skill.id,
            user_id=skill.user_id,
            name=skill.name,
            slug=skill.slug.value,
            description=skill.description,
            tree_id=skill.tree_id,
            is_public=skill.is_public,
            version=skill.version,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )


class UpdateSkillReq(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        pattern=r"^[a-z0-9-]+$",
    )
    slug: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    tree_id: UUID | None = None
    is_public: bool | None = None


class UpdateSkillResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    slug: str
    description: str | None
    tree_id: UUID | None
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, skill: Skill) -> UpdateSkillResp:
        return cls(
            id=skill.id,
            user_id=skill.user_id,
            name=skill.name,
            slug=skill.slug.value,
            description=skill.description,
            tree_id=skill.tree_id,
            is_public=skill.is_public,
            version=skill.version,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )


class GetSkillResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    name: str
    slug: str
    description: str | None
    tree_id: UUID | None
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, skill: Skill) -> GetSkillResp:
        return cls(
            id=skill.id,
            user_id=skill.user_id,
            name=skill.name,
            slug=skill.slug.value,
            description=skill.description,
            tree_id=skill.tree_id,
            is_public=skill.is_public,
            version=skill.version,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )


class ListSkillsItemResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    is_public: bool
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, skill: Skill) -> ListSkillsItemResp:
        return cls(
            id=skill.id,
            name=skill.name,
            slug=skill.slug.value,
            description=skill.description,
            is_public=skill.is_public,
            version=skill.version,
            created_at=skill.created_at,
            updated_at=skill.updated_at,
        )


class SkillFileEntry(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    path: str
    type: str
    blob_id: UUID | None = None


class ListSkillFilesResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    skill_id: UUID
    skill_name: str
    files: list[SkillFileEntry]

    @classmethod
    def from_domain(cls, skill: Skill, entries: list) -> ListSkillFilesResp:
        files = [
            SkillFileEntry(
                path=str(entry.path),
                type=entry.entry_type,
                blob_id=entry.blob_id,
            )
            for entry in entries
        ]
        return cls(
            skill_id=skill.id,
            skill_name=skill.name,
            files=files,
        )
