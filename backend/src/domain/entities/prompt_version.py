from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4


@dataclass
class PromptVersion:
    id: UUID = field(default_factory=uuid4)
    prompt_id: UUID = field(default_factory=uuid4)
    version_number: int = 1
    title: str = ""
    content: str = ""
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
