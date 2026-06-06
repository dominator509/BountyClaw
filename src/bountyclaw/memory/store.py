"""SQLite store for Phase 8 local memory records."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import MemoryApproval, MemoryExport, MemoryRecord

SCHEMA_VERSION = "1"


class MemoryStoreError(RuntimeError):
    """Base memory-store exception."""


class MemoryStore:
    """Small SQLite-backed store for redacted project memory."""

    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().resolve(strict=False)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS memory_schema_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                INSERT INTO memory_schema_info(key, value)
                VALUES ('schema_version', '1')
                ON CONFLICT(key) DO UPDATE SET value = excluded.value;

                CREATE TABLE IF NOT EXISTS memories (
                    memory_id TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source TEXT NOT NULL,
                    content TEXT NOT NULL,
                    redaction_status TEXT NOT NULL,
                    redaction_count INTEGER NOT NULL,
                    retention_policy TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    approval_note TEXT NOT NULL,
                    explicit_approval INTEGER NOT NULL,
                    scope_expansion_allowed INTEGER NOT NULL,
                    tool_execution_allowed INTEGER NOT NULL,
                    network_used INTEGER NOT NULL,
                    live_llm_provider_used INTEGER NOT NULL,
                    mcp_used INTEGER NOT NULL,
                    browser_used INTEGER NOT NULL,
                    active_validation_used INTEGER NOT NULL,
                    report_submission_used INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                """
            )

    def write_memory(self, memory: MemoryRecord) -> None:
        self.initialize()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO memories(
                    memory_id,
                    repository,
                    category,
                    source,
                    content,
                    redaction_status,
                    redaction_count,
                    retention_policy,
                    approved_by,
                    approval_note,
                    explicit_approval,
                    scope_expansion_allowed,
                    tool_execution_allowed,
                    network_used,
                    live_llm_provider_used,
                    mcp_used,
                    browser_used,
                    active_validation_used,
                    report_submission_used,
                    created_at,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(memory_id) DO UPDATE SET
                    repository = excluded.repository,
                    category = excluded.category,
                    source = excluded.source,
                    content = excluded.content,
                    redaction_status = excluded.redaction_status,
                    redaction_count = excluded.redaction_count,
                    retention_policy = excluded.retention_policy,
                    approved_by = excluded.approved_by,
                    approval_note = excluded.approval_note,
                    explicit_approval = excluded.explicit_approval,
                    metadata_json = excluded.metadata_json
                """,
                (
                    memory.memory_id,
                    memory.repository,
                    memory.category,
                    memory.source,
                    memory.content,
                    memory.redaction_status,
                    memory.redaction_count,
                    memory.retention_policy,
                    memory.approval.approved_by,
                    memory.approval.approval_note,
                    int(memory.approval.explicit_approval),
                    int(memory.scope_expansion_allowed),
                    int(memory.tool_execution_allowed),
                    int(memory.network_used),
                    int(memory.live_llm_provider_used),
                    int(memory.mcp_used),
                    int(memory.browser_used),
                    int(memory.active_validation_used),
                    int(memory.report_submission_used),
                    memory.created_at,
                    _json(memory.metadata),
                ),
            )

    def list_memories(
        self,
        *,
        repository: str | None = None,
        category: str | None = None,
        limit: int = 100,
    ) -> list[MemoryRecord]:
        self.initialize()
        with self._connect() as connection:
            if repository is not None and category is not None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM memories
                    WHERE repository = ? AND category = ?
                    ORDER BY created_at DESC, memory_id ASC
                    LIMIT ?
                    """,
                    (repository, category, limit),
                ).fetchall()
            elif repository is not None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM memories
                    WHERE repository = ?
                    ORDER BY created_at DESC, memory_id ASC
                    LIMIT ?
                    """,
                    (repository, limit),
                ).fetchall()
            elif category is not None:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM memories
                    WHERE category = ?
                    ORDER BY created_at DESC, memory_id ASC
                    LIMIT ?
                    """,
                    (category, limit),
                ).fetchall()
            else:
                rows = connection.execute(
                    """
                    SELECT *
                    FROM memories
                    ORDER BY created_at DESC, memory_id ASC
                    LIMIT ?
                    """,
                    (limit,),
                ).fetchall()
        return [_row_to_memory(row) for row in rows]

    def delete_memory(self, memory_id: str) -> bool:
        self.initialize()
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM memories WHERE memory_id = ?", (memory_id,))
        return cursor.rowcount > 0

    def export_memories(self, *, repository: str | None = None) -> MemoryExport:
        memories = self.list_memories(repository=repository, limit=10000)
        return MemoryExport(
            store_path=str(self.path),
            repository=repository or "all",
            memory_records=memories,
            notes=[
                "Memory export contains redacted local records only.",
                "Exported memory cannot expand scope or execute tools.",
            ],
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection


def _row_to_memory(row: sqlite3.Row) -> MemoryRecord:
    return MemoryRecord(
        memory_id=row["memory_id"],
        repository=row["repository"],
        category=row["category"],
        source=row["source"],
        content=row["content"],
        redaction_status=row["redaction_status"],
        redaction_count=row["redaction_count"],
        retention_policy=row["retention_policy"],
        approval=MemoryApproval(
            approved_by=row["approved_by"],
            approval_note=row["approval_note"],
            explicit_approval=True,
        ),
        scope_expansion_allowed=False,
        tool_execution_allowed=False,
        network_used=False,
        live_llm_provider_used=False,
        mcp_used=False,
        browser_used=False,
        active_validation_used=False,
        report_submission_used=False,
        created_at=row["created_at"],
        metadata=json.loads(row["metadata_json"]),
    )


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
