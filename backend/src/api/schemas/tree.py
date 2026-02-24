from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.domain.aggregates.tree import Tree, TreeEntry

ENTRY_TYPE_BLOB = "blob"
ENTRY_TYPE_TREE = "tree"


class TreeEntryItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    path: str = Field(..., min_length=0, max_length=512)
    blob_id: UUID | None = None
    entry_type: str = Field(
        ...,
        pattern="^(blob|tree)$",
        serialization_alias="type",
    )

    @classmethod
    def from_domain(cls, entry: TreeEntry) -> TreeEntryItem:
        return cls(
            path=entry.path.value,
            blob_id=entry.blob_id,
            entry_type=entry.entry_type,
        )


class CreateTreeReq(BaseModel):
    entries: list[dict[str, Any]] = Field(
        default_factory=list,
        description="List of file/directory entries with path, blob_id, and type",
    )


class CreateTreeResp(BaseModel):
    id: UUID
    entries: list[TreeEntryItem]
    created_at: datetime

    @classmethod
    def from_domain(cls, tree: Tree) -> CreateTreeResp:
        return cls(
            id=tree.id,
            entries=[TreeEntryItem.from_domain(e) for e in tree.entries],
            created_at=tree.created_at,
        )


class UpdateTreeReq(BaseModel):
    entries: list[dict[str, Any]] | None = Field(
        None,
        description="List of file/directory entries with path, blob_id, and type",
    )


class UpdateTreeResp(BaseModel):
    id: UUID
    entries: list[TreeEntryItem]
    created_at: datetime

    @classmethod
    def from_domain(cls, tree: Tree) -> UpdateTreeResp:
        return cls(
            id=tree.id,
            entries=[TreeEntryItem.from_domain(e) for e in tree.entries],
            created_at=tree.created_at,
        )


class GetTreeResp(BaseModel):
    id: UUID
    entries: list[TreeEntryItem]
    created_at: datetime

    @classmethod
    def from_domain(cls, tree: Tree) -> GetTreeResp:
        return cls(
            id=tree.id,
            entries=[TreeEntryItem.from_domain(e) for e in tree.entries],
            created_at=tree.created_at,
        )


class ListTreesItemResp(BaseModel):
    id: UUID
    entry_count: int
    created_at: datetime

    @classmethod
    def from_domain(cls, tree: Tree) -> ListTreesItemResp:
        return cls(
            id=tree.id,
            entry_count=len(tree.entries),
            created_at=tree.created_at,
        )


class AddTreeFileReq(BaseModel):
    path: str = Field(..., min_length=1, max_length=512)
    entry_type: str = Field(
        ...,
        pattern="^(blob|tree)$",
        validation_alias=AliasChoices("entry_type", "type"),
    )
    blob_id: UUID | None = None
    content: str | None = None


class AddTreeFileResp(BaseModel):
    id: UUID
    entries: list[TreeEntryItem]
    created_at: datetime

    @classmethod
    def from_domain(cls, tree: Tree) -> AddTreeFileResp:
        return cls(
            id=tree.id,
            entries=[TreeEntryItem.from_domain(e) for e in tree.entries],
            created_at=tree.created_at,
        )


class DeleteTreeFileReq(BaseModel):
    path: str = Field(..., min_length=1, max_length=512)


class RenameTreeFileReq(BaseModel):
    old_path: str = Field(..., min_length=1, max_length=512)
    new_path: str = Field(..., min_length=1, max_length=512)


class MoveTreeFileReq(BaseModel):
    source: str = Field(..., min_length=1, max_length=512)
    target: str = Field(..., min_length=1, max_length=512)


class UpdateTreeFileContentReq(BaseModel):
    path: str = Field(..., min_length=1, max_length=512)
    content: str = Field(..., min_length=0)


class BatchUploadEntry(BaseModel):
    path: str = Field(..., min_length=1, max_length=512)
    entry_type: str = Field(
        ...,
        pattern="^(blob|tree)$",
        validation_alias=AliasChoices("entry_type", "type"),
    )
    content: str | None = None


class BatchUploadReq(BaseModel):
    entries: list[BatchUploadEntry]


class BatchUploadResp(BaseModel):
    uploaded: int
    failed: int


class FolderUploadEntry(BaseModel):
    path: str = Field(..., min_length=1, max_length=512)
    entry_type: str = Field(
        ...,
        pattern="^(blob|tree)$",
        validation_alias=AliasChoices("entry_type", "type"),
    )
    blob_id: UUID | None = None
    content: str | None = None


class FolderUploadReq(BaseModel):
    base_path: str = Field(..., min_length=0, max_length=512)
    entries: list[FolderUploadEntry]
