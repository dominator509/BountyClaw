"""SQLite evidence store for redacted Phase 4 findings."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from bountyclaw.scanning.models import ScannerRunResult

from .models import (
    CanonicalFinding,
    EvidenceRecord,
    NormalizationResult,
    StoredFindingBundle,
    StoredFindingSummary,
)

SCHEMA_VERSION = "1"


class EvidenceStoreError(RuntimeError):
    """Base exception for evidence-store failures."""


class EvidenceStorePathError(EvidenceStoreError):
    """Raised when a store path would violate repository write boundaries."""


class EvidenceStore:
    """Small SQLite-backed store for scan runs, findings, and evidence."""

    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().resolve(strict=False)

    def initialize(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                CREATE TABLE IF NOT EXISTS schema_info (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                INSERT INTO schema_info(key, value)
                VALUES ('schema_version', '1')
                ON CONFLICT(key) DO UPDATE SET value = excluded.value;

                CREATE TABLE IF NOT EXISTS scan_runs (
                    scan_execution_id TEXT PRIMARY KEY,
                    repository TEXT NOT NULL,
                    repository_fingerprint_id TEXT NOT NULL,
                    scanners_execute INTEGER NOT NULL,
                    network_used INTEGER NOT NULL,
                    llm_used INTEGER NOT NULL,
                    mcp_used INTEGER NOT NULL,
                    browser_used INTEGER NOT NULL,
                    active_validation_used INTEGER NOT NULL,
                    report_submission_used INTEGER NOT NULL,
                    adapters_json TEXT NOT NULL,
                    notes_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS findings (
                    canonical_finding_id TEXT PRIMARY KEY,
                    dedupe_key TEXT NOT NULL,
                    scan_execution_id TEXT NOT NULL,
                    source_preliminary_ids_json TEXT NOT NULL,
                    scanner_ids_json TEXT NOT NULL,
                    scanner_rule_ids_json TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    vulnerability_class TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    target TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    cwe TEXT,
                    affected_component TEXT,
                    remediation_guidance TEXT,
                    authorization_status TEXT NOT NULL,
                    false_positive_analysis TEXT NOT NULL,
                    report_readiness_status TEXT NOT NULL,
                    evidence_ids_json TEXT NOT NULL,
                    evidence_count INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(scan_execution_id) REFERENCES scan_runs(scan_execution_id)
                );

                CREATE TABLE IF NOT EXISTS evidence (
                    evidence_id TEXT PRIMARY KEY,
                    canonical_finding_id TEXT NOT NULL,
                    evidence_kind TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    content TEXT NOT NULL,
                    redaction_status TEXT NOT NULL,
                    redaction_count INTEGER NOT NULL,
                    source_excerpt_included INTEGER NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(canonical_finding_id) REFERENCES findings(canonical_finding_id)
                );
                """
            )

    def write_scan_run(
        self, scan_result: ScannerRunResult, normalization: NormalizationResult
    ) -> None:
        """Persist one scanner run plus normalized records."""

        self.initialize()
        now = _now()
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO scan_runs(
                    scan_execution_id,
                    repository,
                    repository_fingerprint_id,
                    scanners_execute,
                    network_used,
                    llm_used,
                    mcp_used,
                    browser_used,
                    active_validation_used,
                    report_submission_used,
                    adapters_json,
                    notes_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(scan_execution_id) DO UPDATE SET
                    repository = excluded.repository,
                    repository_fingerprint_id = excluded.repository_fingerprint_id,
                    adapters_json = excluded.adapters_json,
                    notes_json = excluded.notes_json
                """,
                (
                    scan_result.scan_execution_id,
                    scan_result.repository,
                    scan_result.repository_fingerprint_id,
                    int(scan_result.scanners_execute),
                    int(scan_result.network_used),
                    int(scan_result.llm_used),
                    int(scan_result.mcp_used),
                    int(scan_result.browser_used),
                    int(scan_result.active_validation_used),
                    int(scan_result.report_submission_used),
                    _json([adapter.model_dump(mode="json") for adapter in scan_result.adapters]),
                    _json(scan_result.notes + normalization.notes),
                    now,
                ),
            )
            for finding in normalization.canonical_findings:
                self._upsert_finding(connection, finding, scan_result.scan_execution_id, now)
            for evidence in normalization.evidence_records:
                self._insert_evidence(connection, evidence, now)

    def list_findings(self, *, limit: int = 100) -> list[StoredFindingSummary]:
        """Return stored finding summaries in deterministic order."""

        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT canonical_finding_id, severity, confidence, title, file_path,
                       line_number, evidence_count, report_readiness_status
                FROM findings
                ORDER BY file_path ASC, line_number ASC, canonical_finding_id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            StoredFindingSummary(
                canonical_finding_id=row["canonical_finding_id"],
                severity=row["severity"],
                confidence=row["confidence"],
                title=row["title"],
                file_path=row["file_path"],
                line_number=row["line_number"],
                evidence_count=row["evidence_count"],
                report_readiness_status=row["report_readiness_status"],
            )
            for row in rows
        ]

    def get_finding_bundle(self, canonical_finding_id: str) -> StoredFindingBundle | None:
        """Return a full redacted finding bundle for prompt construction.

        The returned content is already redacted by the Phase 4 persistence path.
        Phase 5 prompt builders still run redaction again before model payload
        construction as a defense-in-depth control.
        """

        self.initialize()
        with self._connect() as connection:
            finding_row = connection.execute(
                """
                SELECT *
                FROM findings
                WHERE canonical_finding_id = ?
                """,
                (canonical_finding_id,),
            ).fetchone()
            if finding_row is None:
                return None

            evidence_rows = connection.execute(
                """
                SELECT *
                FROM evidence
                WHERE canonical_finding_id = ?
                ORDER BY evidence_id ASC
                """,
                (canonical_finding_id,),
            ).fetchall()

        finding = CanonicalFinding(
            canonical_finding_id=finding_row["canonical_finding_id"],
            dedupe_key=finding_row["dedupe_key"],
            source_preliminary_ids=_json_list(finding_row["source_preliminary_ids_json"]),
            scanner_ids=_json_list(finding_row["scanner_ids_json"]),
            scanner_rule_ids=_json_list(finding_row["scanner_rule_ids_json"]),
            title=finding_row["title"],
            description=finding_row["description"],
            vulnerability_class=finding_row["vulnerability_class"],
            severity=finding_row["severity"],
            confidence=finding_row["confidence"],
            target=finding_row["target"],
            file_path=finding_row["file_path"],
            line_number=finding_row["line_number"],
            cwe=finding_row["cwe"],
            affected_component=finding_row["affected_component"],
            remediation_guidance=finding_row["remediation_guidance"],
            authorization_status=finding_row["authorization_status"],
            false_positive_analysis=finding_row["false_positive_analysis"],
            report_readiness_status=finding_row["report_readiness_status"],
            evidence_ids=_json_list(finding_row["evidence_ids_json"]),
            evidence_count=finding_row["evidence_count"],
            metadata=_json_dict(finding_row["metadata_json"]),
        )
        evidence_records = [
            EvidenceRecord(
                evidence_id=row["evidence_id"],
                canonical_finding_id=row["canonical_finding_id"],
                evidence_kind=row["evidence_kind"],
                summary=row["summary"],
                content=row["content"],
                redaction_status=row["redaction_status"],
                redaction_count=row["redaction_count"],
                source_excerpt_included=False,
                metadata=_json_dict(row["metadata_json"]),
            )
            for row in evidence_rows
        ]
        return StoredFindingBundle(finding=finding, evidence_records=evidence_records)

    def raw_database_text(self) -> str:
        """Return all text persisted in the database for safety tests only."""

        self.initialize()
        fragments: list[str] = []
        with self._connect() as connection:
            for table in ("scan_runs", "findings", "evidence"):
                rows = connection.execute(
                    f"SELECT * FROM {table}"  # nosec B608
                ).fetchall()
                for row in rows:
                    fragments.extend(str(value) for value in tuple(row) if value is not None)
        return "\n".join(fragments)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _upsert_finding(
        self,
        connection: sqlite3.Connection,
        finding: CanonicalFinding,
        scan_execution_id: str,
        now: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO findings(
                canonical_finding_id,
                dedupe_key,
                scan_execution_id,
                source_preliminary_ids_json,
                scanner_ids_json,
                scanner_rule_ids_json,
                title,
                description,
                vulnerability_class,
                severity,
                confidence,
                target,
                file_path,
                line_number,
                cwe,
                affected_component,
                remediation_guidance,
                authorization_status,
                false_positive_analysis,
                report_readiness_status,
                evidence_ids_json,
                evidence_count,
                metadata_json,
                updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(canonical_finding_id) DO UPDATE SET
                scan_execution_id = excluded.scan_execution_id,
                source_preliminary_ids_json = excluded.source_preliminary_ids_json,
                scanner_ids_json = excluded.scanner_ids_json,
                scanner_rule_ids_json = excluded.scanner_rule_ids_json,
                title = excluded.title,
                description = excluded.description,
                severity = excluded.severity,
                confidence = excluded.confidence,
                evidence_ids_json = excluded.evidence_ids_json,
                evidence_count = excluded.evidence_count,
                metadata_json = excluded.metadata_json,
                updated_at = excluded.updated_at
            """,
            (
                finding.canonical_finding_id,
                finding.dedupe_key,
                scan_execution_id,
                _json(finding.source_preliminary_ids),
                _json(finding.scanner_ids),
                _json(finding.scanner_rule_ids),
                finding.title,
                finding.description,
                finding.vulnerability_class,
                finding.severity,
                finding.confidence,
                finding.target,
                finding.file_path,
                finding.line_number,
                finding.cwe,
                finding.affected_component,
                finding.remediation_guidance,
                finding.authorization_status,
                finding.false_positive_analysis,
                finding.report_readiness_status,
                _json(finding.evidence_ids),
                finding.evidence_count,
                _json(finding.metadata),
                now,
            ),
        )

    def _insert_evidence(
        self,
        connection: sqlite3.Connection,
        evidence: EvidenceRecord,
        now: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO evidence(
                evidence_id,
                canonical_finding_id,
                evidence_kind,
                summary,
                content,
                redaction_status,
                redaction_count,
                source_excerpt_included,
                metadata_json,
                created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(evidence_id) DO NOTHING
            """,
            (
                evidence.evidence_id,
                evidence.canonical_finding_id,
                evidence.evidence_kind,
                evidence.summary,
                evidence.content,
                evidence.redaction_status,
                evidence.redaction_count,
                int(evidence.source_excerpt_included),
                _json(evidence.metadata),
                now,
            ),
        )


def ensure_store_path_outside_repository(store_path: Path, repository_root: Path) -> Path:
    """Resolve and validate an evidence-store path.

    BountyClaw scanners must not write into target repositories. The evidence
    database is local state for BountyClaw, not target-repository output.
    """

    resolved_store = store_path.expanduser().resolve(strict=False)
    resolved_repo = repository_root.expanduser().resolve(strict=False)
    try:
        resolved_store.relative_to(resolved_repo)
    except ValueError:
        return resolved_store
    raise EvidenceStorePathError(
        "evidence store path must not be inside the target repository; choose an external --store path"
    )


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str) -> object:
    loaded = json.loads(value)
    return loaded


def _json_list(value: str) -> list[str]:
    return cast(list[str], _json_loads(value))


def _json_dict(value: str) -> dict[str, Any]:
    return cast(dict[str, Any], _json_loads(value))


def _now() -> str:
    return datetime.now(UTC).isoformat()
