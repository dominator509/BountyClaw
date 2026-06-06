"""Initial local audit event model for BountyClaw."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

AuditDecision = Literal["allow", "deny", "require_human_approval", "informational"]


class AuditEvent(BaseModel):
    """Structured local audit event.

    Phase 1 introduced this model; Phase 6 adds human-reviewed report drafting on top of the local redaction-first evidence store. This establishes the
    immutable shape future runtime actions must use for redacted local logging.
    """

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_type: str
    action: str | None = None
    decision: AuditDecision = "informational"
    target_kind: str | None = None
    target: str | None = None
    reasons: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_json_line(self) -> str:
        """Serialize the event as one JSONL line."""

        return self.model_dump_json() + "\n"


class AuditLogWriter:
    """Append-only local JSONL audit writer."""

    def __init__(self, path: Path) -> None:
        self.path = path

    def append(self, event: AuditEvent) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(event.to_json_line())
