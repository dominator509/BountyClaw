"""SQLite report state store for Phase 6."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from bountyclaw.findings import EvidenceStore

from .models import ReportDraft, StoredReportDraftSummary, TriageReview

REPORT_SCHEMA_VERSION = "1"


class ReportStoreError(RuntimeError):
    """Base exception for report-store failures."""


class ReportStore:
    """Persist triage reviews and deterministic report drafts in the evidence DB."""

    def __init__(self, path: Path) -> None:
        self.path = path.expanduser().resolve(strict=False)

    def initialize(self) -> None:
        EvidenceStore(self.path).initialize()
        with self._connect() as connection:
            connection.executescript(
                """
                PRAGMA foreign_keys = ON;
                INSERT INTO schema_info(key, value)
                VALUES ('report_schema_version', '1')
                ON CONFLICT(key) DO UPDATE SET value = excluded.value;

                CREATE TABLE IF NOT EXISTS triage_reviews (
                    canonical_finding_id TEXT PRIMARY KEY,
                    review_status TEXT NOT NULL,
                    reviewer TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    impact_assessment TEXT,
                    recommended_action TEXT,
                    reviewed_at TEXT NOT NULL,
                    model_triage_request_id TEXT,
                    metadata_json TEXT NOT NULL,
                    FOREIGN KEY(canonical_finding_id) REFERENCES findings(canonical_finding_id)
                );

                CREATE TABLE IF NOT EXISTS report_drafts (
                    report_draft_id TEXT PRIMARY KEY,
                    canonical_finding_id TEXT NOT NULL,
                    repository TEXT NOT NULL,
                    store_path TEXT NOT NULL,
                    draft_format TEXT NOT NULL,
                    draft_status TEXT NOT NULL,
                    title TEXT NOT NULL,
                    executive_summary TEXT NOT NULL,
                    affected_asset TEXT NOT NULL,
                    vulnerability_class TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    evidence_summary TEXT NOT NULL,
                    technical_details TEXT NOT NULL,
                    safe_reproduction_checklist_json TEXT NOT NULL,
                    impact_statement TEXT NOT NULL,
                    remediation TEXT NOT NULL,
                    validation_status TEXT NOT NULL,
                    human_review_status TEXT NOT NULL,
                    human_review_required INTEGER NOT NULL,
                    submission_allowed INTEGER NOT NULL,
                    automated_submission_used INTEGER NOT NULL,
                    network_used INTEGER NOT NULL,
                    live_llm_provider_used INTEGER NOT NULL,
                    mcp_used INTEGER NOT NULL,
                    browser_used INTEGER NOT NULL,
                    active_validation_used INTEGER NOT NULL,
                    report_submission_used INTEGER NOT NULL,
                    evidence_ids_json TEXT NOT NULL,
                    model_triage_summary TEXT,
                    content_markdown TEXT NOT NULL,
                    notes_json TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(canonical_finding_id) REFERENCES findings(canonical_finding_id)
                );
                """
            )

    def upsert_triage_review(self, review: TriageReview) -> None:
        self.initialize()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO triage_reviews(
                    canonical_finding_id,
                    review_status,
                    reviewer,
                    rationale,
                    impact_assessment,
                    recommended_action,
                    reviewed_at,
                    model_triage_request_id,
                    metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_finding_id) DO UPDATE SET
                    review_status = excluded.review_status,
                    reviewer = excluded.reviewer,
                    rationale = excluded.rationale,
                    impact_assessment = excluded.impact_assessment,
                    recommended_action = excluded.recommended_action,
                    reviewed_at = excluded.reviewed_at,
                    model_triage_request_id = excluded.model_triage_request_id,
                    metadata_json = excluded.metadata_json
                """,
                (
                    review.canonical_finding_id,
                    review.review_status,
                    review.reviewer,
                    review.rationale,
                    review.impact_assessment,
                    review.recommended_action,
                    review.reviewed_at,
                    review.model_triage_request_id,
                    _json(review.metadata),
                ),
            )
            connection.execute(
                """
                UPDATE findings
                SET report_readiness_status = ?, updated_at = ?
                WHERE canonical_finding_id = ?
                """,
                (
                    _finding_readiness_for_review(review.review_status),
                    review.reviewed_at,
                    review.canonical_finding_id,
                ),
            )

    def get_triage_review(self, canonical_finding_id: str) -> TriageReview | None:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM triage_reviews
                WHERE canonical_finding_id = ?
                """,
                (canonical_finding_id,),
            ).fetchone()
        if row is None:
            return None
        return TriageReview(
            canonical_finding_id=row["canonical_finding_id"],
            review_status=row["review_status"],
            reviewer=row["reviewer"],
            rationale=row["rationale"],
            impact_assessment=row["impact_assessment"],
            recommended_action=row["recommended_action"],
            reviewed_at=row["reviewed_at"],
            model_triage_request_id=row["model_triage_request_id"],
            metadata=_json_dict(row["metadata_json"]),
        )

    def write_report_draft(self, draft: ReportDraft) -> None:
        self.initialize()
        now = _now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO report_drafts(
                    report_draft_id,
                    canonical_finding_id,
                    repository,
                    store_path,
                    draft_format,
                    draft_status,
                    title,
                    executive_summary,
                    affected_asset,
                    vulnerability_class,
                    severity,
                    confidence,
                    evidence_summary,
                    technical_details,
                    safe_reproduction_checklist_json,
                    impact_statement,
                    remediation,
                    validation_status,
                    human_review_status,
                    human_review_required,
                    submission_allowed,
                    automated_submission_used,
                    network_used,
                    live_llm_provider_used,
                    mcp_used,
                    browser_used,
                    active_validation_used,
                    report_submission_used,
                    evidence_ids_json,
                    model_triage_summary,
                    content_markdown,
                    notes_json,
                    metadata_json,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(report_draft_id) DO UPDATE SET
                    title = excluded.title,
                    executive_summary = excluded.executive_summary,
                    evidence_summary = excluded.evidence_summary,
                    technical_details = excluded.technical_details,
                    impact_statement = excluded.impact_statement,
                    remediation = excluded.remediation,
                    content_markdown = excluded.content_markdown,
                    notes_json = excluded.notes_json,
                    metadata_json = excluded.metadata_json,
                    created_at = excluded.created_at
                """,
                (
                    draft.report_draft_id,
                    draft.canonical_finding_id,
                    draft.repository,
                    draft.store_path,
                    draft.draft_format,
                    draft.draft_status,
                    draft.title,
                    draft.executive_summary,
                    draft.affected_asset,
                    draft.vulnerability_class,
                    draft.severity,
                    draft.confidence,
                    draft.evidence_summary,
                    draft.technical_details,
                    _json(draft.safe_reproduction_checklist),
                    draft.impact_statement,
                    draft.remediation,
                    draft.validation_status,
                    draft.human_review_status,
                    int(draft.human_review_required),
                    int(draft.submission_allowed),
                    int(draft.automated_submission_used),
                    int(draft.network_used),
                    int(draft.live_llm_provider_used),
                    int(draft.mcp_used),
                    int(draft.browser_used),
                    int(draft.active_validation_used),
                    int(draft.report_submission_used),
                    _json(draft.evidence_ids),
                    draft.model_triage_summary,
                    draft.content_markdown,
                    _json(draft.notes),
                    _json(draft.metadata),
                    now,
                ),
            )

    def list_report_drafts(self, *, limit: int = 100) -> list[StoredReportDraftSummary]:
        self.initialize()
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT report_draft_id, canonical_finding_id, title, severity, confidence,
                       draft_status, validation_status, submission_allowed, created_at
                FROM report_drafts
                ORDER BY created_at DESC, report_draft_id ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            StoredReportDraftSummary(
                report_draft_id=row["report_draft_id"],
                canonical_finding_id=row["canonical_finding_id"],
                title=row["title"],
                severity=row["severity"],
                confidence=row["confidence"],
                draft_status=row["draft_status"],
                validation_status=row["validation_status"],
                submission_allowed=False,
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_report_draft(self, report_draft_id: str) -> ReportDraft | None:
        self.initialize()
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM report_drafts
                WHERE report_draft_id = ?
                """,
                (report_draft_id,),
            ).fetchone()
        if row is None:
            return None
        return ReportDraft(
            report_draft_id=row["report_draft_id"],
            canonical_finding_id=row["canonical_finding_id"],
            repository=row["repository"],
            store_path=row["store_path"],
            draft_format=row["draft_format"],
            draft_status=row["draft_status"],
            title=row["title"],
            executive_summary=row["executive_summary"],
            affected_asset=row["affected_asset"],
            vulnerability_class=row["vulnerability_class"],
            severity=row["severity"],
            confidence=row["confidence"],
            evidence_summary=row["evidence_summary"],
            technical_details=row["technical_details"],
            safe_reproduction_checklist=_json_list(row["safe_reproduction_checklist_json"]),
            impact_statement=row["impact_statement"],
            remediation=row["remediation"],
            validation_status=row["validation_status"],
            human_review_status=row["human_review_status"],
            human_review_required=True,
            submission_allowed=False,
            automated_submission_used=False,
            network_used=False,
            live_llm_provider_used=False,
            mcp_used=False,
            browser_used=False,
            active_validation_used=False,
            report_submission_used=False,
            evidence_ids=_json_list(row["evidence_ids_json"]),
            model_triage_summary=row["model_triage_summary"],
            content_markdown=row["content_markdown"],
            notes=_json_list(row["notes_json"]),
            metadata=_json_dict(row["metadata_json"]),
        )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection


def _finding_readiness_for_review(review_status: str) -> str:
    mapping = {
        "needs_review": "needs_human_triage",
        "needs_more_evidence": "needs_more_evidence",
        "approved_for_draft": "ready_for_report_draft",
        "rejected_false_positive": "rejected_false_positive",
    }
    return mapping.get(review_status, "needs_human_triage")


def _json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _json_loads(value: str) -> object:
    return json.loads(value)


def _json_list(value: str) -> list[str]:
    return cast(list[str], _json_loads(value))


def _json_dict(value: str) -> dict[str, Any]:
    return cast(dict[str, Any], _json_loads(value))


def _now() -> str:
    return datetime.now(UTC).isoformat()
