"""Canonical findings and evidence models for Phase 4.

Phase 4 converts preliminary scanner output into durable, deduplicated,
redaction-safe records. The models intentionally avoid raw source excerpts and
mark every persisted finding as requiring human triage before report drafting.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from bountyclaw.scanning.models import Confidence, Severity

ReportReadinessStatus = Literal[
    "needs_human_triage",
    "needs_more_evidence",
    "ready_for_report_draft",
    "rejected_false_positive",
]
RedactionStatus = Literal["redacted", "no_sensitive_patterns_detected"]


class RedactionMatch(BaseModel):
    """Non-sensitive metadata describing a redaction event.

    Raw secret material, offsets, and hashes are intentionally not stored. A
    hash of a real secret can still become sensitive matching material, so the
    evidence store keeps only the redaction type and placeholder.
    """

    secret_type: str
    placeholder: str


class RedactionResult(BaseModel):
    """Result of redacting one text value."""

    original_text_was_modified: bool
    redacted_text: str
    redaction_status: RedactionStatus
    redactions: list[RedactionMatch] = Field(default_factory=list)

    @property
    def redaction_count(self) -> int:
        return len(self.redactions)


class EvidenceRecord(BaseModel):
    """Redacted evidence persisted for a canonical finding."""

    evidence_version: Literal["1"] = "1"
    evidence_id: str
    canonical_finding_id: str
    evidence_kind: Literal[
        "redacted_line_reference",
        "metadata_only",
        "normalized_scanner_output",
    ]
    summary: str
    content: str
    redaction_status: RedactionStatus
    redaction_count: int = Field(ge=0)
    source_excerpt_included: Literal[False] = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanonicalFinding(BaseModel):
    """Durable, deduplicated finding record."""

    finding_version: Literal["1"] = "1"
    canonical_finding_id: str
    dedupe_key: str
    source_preliminary_ids: list[str] = Field(default_factory=list)
    scanner_ids: list[str] = Field(default_factory=list)
    scanner_rule_ids: list[str] = Field(default_factory=list)
    title: str
    description: str
    vulnerability_class: str
    severity: Severity
    confidence: Confidence
    target: str
    file_path: str
    line_number: int | None = Field(default=None, ge=1)
    cwe: str | None = None
    affected_component: str | None = None
    remediation_guidance: str | None = None
    authorization_status: Literal["scope_approved"] = "scope_approved"
    false_positive_analysis: Literal["not_reviewed"] = "not_reviewed"
    report_readiness_status: ReportReadinessStatus = "needs_human_triage"
    evidence_ids: list[str] = Field(default_factory=list)
    evidence_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)


class NormalizationResult(BaseModel):
    """Canonical findings generated from a scanner run."""

    normalization_version: Literal["1"] = "1"
    scan_execution_id: str
    repository: str
    repository_fingerprint_id: str
    canonical_findings: list[CanonicalFinding] = Field(default_factory=list)
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    redaction_count: int = Field(default=0, ge=0)
    notes: list[str] = Field(default_factory=list)


class FindingsCollectionResult(BaseModel):
    """End-to-end Phase 4 scan-to-store result."""

    collection_version: Literal["1"] = "1"
    store_path: str
    scan_execution_id: str
    repository: str
    repository_fingerprint_id: str
    canonical_findings: list[CanonicalFinding] = Field(default_factory=list)
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
    redaction_count: int = Field(default=0, ge=0)
    network_used: Literal[False] = False
    llm_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class StoredFindingSummary(BaseModel):
    """Summary row returned by the evidence store."""

    canonical_finding_id: str
    severity: Severity
    confidence: Confidence
    title: str
    file_path: str
    line_number: int | None = None
    evidence_count: int = Field(ge=0)
    report_readiness_status: ReportReadinessStatus


class StoredFindingBundle(BaseModel):
    """Full redacted finding bundle loaded for model prompt construction."""

    finding: CanonicalFinding
    evidence_records: list[EvidenceRecord] = Field(default_factory=list)
