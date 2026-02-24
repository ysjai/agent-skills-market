from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from src.domain.exceptions import ResourceConflictError, ResourceNotFoundError, ValidationError
from src.domain.value_objects.path import Path

if TYPE_CHECKING:
    pass


ENTRY_TYPE_BLOB = "blob"
ENTRY_TYPE_TREE = "tree"


@dataclass
class TreeEntry:
    path: Path
    entry_type: str  # "blob" or "tree"
    blob_id: UUID | None = None

    def __post_init__(self) -> None:
        if self.entry_type not in (ENTRY_TYPE_BLOB, ENTRY_TYPE_TREE):
            raise ValidationError(f"Invalid entry type: {self.entry_type}")

        if self.entry_type == ENTRY_TYPE_BLOB and self.blob_id is None:
            raise ValidationError("Blob entry must have a blob_id")

        if self.entry_type == ENTRY_TYPE_TREE and self.blob_id is not None:
            raise ValidationError("Tree entry cannot have a blob_id")

    def is_file(self) -> bool:
        return self.entry_type == ENTRY_TYPE_BLOB

    def is_directory(self) -> bool:
        return self.entry_type == ENTRY_TYPE_TREE

    def to_dict(self) -> dict:
        result = {
            "path": str(self.path),
            "type": self.entry_type,
        }
        if self.blob_id:
            result["blob_id"] = str(self.blob_id)
        return result

    @classmethod
    def from_dict(cls, data: dict) -> TreeEntry:
        return cls(
            path=Path(data["path"]),
            entry_type=data["type"],
            blob_id=UUID(data["blob_id"]) if data.get("blob_id") else None,
        )


@dataclass
class Tree:
    id: UUID = field(default_factory=uuid4)
    entries: list[TreeEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def create(cls, entries: list[dict] | None = None) -> Tree:
        tree = cls()
        if entries:
            for entry_data in entries:
                tree._add_entry_from_dict(entry_data)
        return tree

    def add_entry(
        self,
        path: str,
        entry_type: str,
        blob_id: UUID | None = None,
    ) -> None:
        validated_path = Path(path)

        if self._find_entry_by_path(str(validated_path)) is not None:
            raise ResourceConflictError(f"Entry with path '{path}' already exists")

        entry = TreeEntry(
            path=validated_path,
            entry_type=entry_type,
            blob_id=blob_id,
        )
        self.entries.append(entry)

    def delete_entry(self, path: str) -> list[UUID]:
        validated_path = Path(path)
        normalized_path = str(validated_path).rstrip("/")
        path_prefix = normalized_path + "/"

        entries_to_delete = []
        blob_ids_to_deref = []

        for entry in self.entries:
            entry_path = str(entry.path).rstrip("/")
            if entry_path == normalized_path or entry_path.startswith(path_prefix):
                entries_to_delete.append(entry)
                if entry.blob_id:
                    blob_ids_to_deref.append(entry.blob_id)

        if not entries_to_delete:
            raise ValidationError(f"Entry '{path}' not found")

        deleted_paths = {str(e.path).rstrip("/") for e in entries_to_delete}
        self.entries = [e for e in self.entries if str(e.path).rstrip("/") not in deleted_paths]

        return blob_ids_to_deref

    def rename_entry(self, old_path: str, new_path: str) -> None:
        if not new_path:
            raise ValidationError("New path cannot be empty")

        if old_path == new_path:
            raise ValidationError("New path must be different from old path")

        _ = Path(old_path)
        new_path_obj = Path(new_path)

        if self._find_entry_by_path(str(new_path_obj)) is not None:
            raise ResourceConflictError(f"Entry with path '{new_path}' already exists")

        old_path_prefix = old_path if old_path.endswith("/") else old_path + "/"
        entry_found = False
        entries_to_rename = []

        for entry in self.entries:
            entry_path_str = str(entry.path)
            if entry_path_str == old_path:
                entries_to_rename.append((entry, new_path))
                entry_found = True
            elif entry_path_str.startswith(old_path_prefix):
                new_child_path = new_path + entry_path_str[len(old_path) :]
                entries_to_rename.append((entry, new_child_path))

        if not entry_found:
            raise ResourceNotFoundError(f"Entry '{old_path}' not found")

        new_paths = {new_path for _, new_path in entries_to_rename}
        for entry in self.entries:
            current_path = str(entry.path)
            if (
                current_path in new_paths
                or current_path.startswith(old_path + "/")
                or current_path == old_path
            ):
                continue
            if current_path == new_path or current_path.startswith(new_path + "/"):
                raise ResourceConflictError(f"Entry with path '{new_path}' already exists")

        for entry, new_path_str in entries_to_rename:
            entry.path = Path(new_path_str)

    def move_entry(self, source: str, target: str) -> None:
        if not target:
            raise ValidationError("Target path cannot be empty")

        _ = Path(source)
        target_path = Path(target)

        source_prefix = source if source.endswith("/") else source + "/"
        entry_found = False
        entries_to_move = []

        for entry in self.entries:
            entry_path_str = str(entry.path)
            if entry_path_str == source:
                entries_to_move.append((entry, target))
                entry_found = True
            elif entry_path_str.startswith(source_prefix):
                new_child_path = target + entry_path_str[len(source) :]
                entries_to_move.append((entry, new_child_path))

        if not entry_found:
            raise ResourceNotFoundError(f"Entry '{source}' not found")

        source_paths = {str(entry.path) for entry, _ in entries_to_move}
        for entry in self.entries:
            current_path = str(entry.path)
            if current_path in source_paths or current_path.startswith(source + "/"):
                continue
            if current_path == target or current_path.startswith(target + "/"):
                raise ResourceConflictError(f"Entry with path '{target}' already exists")

        for entry, new_path in entries_to_move:
            entry.path = Path(new_path)

    def update_entry_content(self, path: str, new_blob_id: UUID) -> UUID | None:
        entry = self._find_entry_by_path(path)

        if entry is None:
            raise ResourceNotFoundError(f"Entry '{path}' not found")

        if not entry.is_file():
            raise ValidationError(f"Entry '{path}' is not a file")

        old_blob_id = entry.blob_id
        entry.blob_id = new_blob_id

        return old_blob_id

    def get_entry(self, path: str) -> TreeEntry | None:
        return self._find_entry_by_path(path)

    def list_entries(self) -> list[TreeEntry]:
        return list(self.entries)

    def to_dict(self) -> dict:
        return {"entries": [entry.to_dict() for entry in self.entries]}

    def _find_entry_by_path(self, path: str) -> TreeEntry | None:
        normalized = path.rstrip("/")
        for entry in self.entries:
            if str(entry.path).rstrip("/") == normalized:
                return entry
        return None

    def _add_entry_from_dict(self, data: dict) -> None:
        entry = TreeEntry.from_dict(data)
        self.entries.append(entry)
