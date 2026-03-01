from __future__ import annotations

from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.domain.aggregates.prompt import Prompt
from src.domain.entities.prompt_version import PromptVersion


class CreatePromptReq(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    content: str = Field(default="")
    description: str | None = Field(None, max_length=1000)
    tags: list[str] = Field(default_factory=list)


class CreatePromptResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    content: str
    description: str | None
    tags: list[str]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, prompt: Prompt) -> CreatePromptResp:
        return cls(
            id=prompt.id,
            user_id=prompt.user_id,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )


class UpdatePromptReq(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(None, min_length=1, max_length=200)
    content: str | None = None
    description: str | None = Field(None, max_length=1000)
    tags: list[str] | None = None


class UpdatePromptResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    content: str
    description: str | None
    tags: list[str]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, prompt: Prompt) -> UpdatePromptResp:
        return cls(
            id=prompt.id,
            user_id=prompt.user_id,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )


class GetPromptResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    content: str
    description: str | None
    tags: list[str]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, prompt: Prompt) -> GetPromptResp:
        return cls(
            id=prompt.id,
            user_id=prompt.user_id,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )


class ListPromptsItemResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    title: str
    content: str
    description: str | None
    tags: list[str]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, prompt: Prompt) -> ListPromptsItemResp:
        return cls(
            id=prompt.id,
            user_id=prompt.user_id,
            title=prompt.title,
            content=prompt.content,
            description=prompt.description,
            tags=prompt.tags,
            version=prompt.version,
            created_at=prompt.created_at,
            updated_at=prompt.updated_at,
        )


class ListPromptsResp(BaseModel):
    items: list[ListPromptsItemResp]
    total: int
    offset: int
    limit: int


class PromptVersionResp(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)

    id: UUID
    prompt_id: UUID
    version_number: int
    title: str
    content: str
    description: str | None
    tags: list[str]
    created_at: datetime

    @classmethod
    def from_domain(cls, version: PromptVersion) -> PromptVersionResp:
        return cls(
            id=version.id,
            prompt_id=version.prompt_id,
            version_number=version.version_number,
            title=version.title,
            content=version.content,
            description=version.description,
            tags=version.tags,
            created_at=version.created_at,
        )


class ImportPromptReq(BaseModel):
    content: str
