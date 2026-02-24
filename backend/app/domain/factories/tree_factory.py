from __future__ import annotations

from uuid import UUID

from app.domain.aggregates.tree import Tree
from app.domain.exceptions import ValidationError


class TreeFactory:
    @classmethod
    def create(cls, entries: list[dict] | None = None) -> Tree:
        cls._validate_entries(entries)
        return Tree.create(entries)

    @classmethod
    def create_from_file(
        cls,
        path: str,
        blob_id: UUID,
    ) -> Tree:
        tree = Tree.create()
        tree.add_entry(path=path, entry_type="blob", blob_id=blob_id)
        return tree

    @classmethod
    def _validate_entries(cls, entries: list[dict] | None) -> None:
        if entries is None:
            return

        for entry in entries:
            if "path" not in entry:
                raise ValidationError("Each entry must have 'path' field")
            if "type" not in entry:
                raise ValidationError("Each entry must have 'type' field")

            entry_type = entry["type"]
            if entry_type not in ("blob", "tree"):
                raise ValidationError(f"Invalid entry type: {entry_type}")

            if entry_type == "blob" and "blob_id" not in entry:
                raise ValidationError("Blob entries must have 'blob_id' field")
