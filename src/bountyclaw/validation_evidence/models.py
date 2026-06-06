"""Validation evidence ledger models for Phase 12.

The Phase 12 ledger records future external-validation artifacts without reading,
printing, or trusting their contents. It hashes files and maps them to Phase 11
handoff tasks and production-gap IDs so Codex/local/CI/human executors can close
gaps only with reviewed evidence.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

EvidenceArtifactStatus = Literal["present", "missing"]
EvidenceCheckStatus = Literal["pass", "fail", "deferred"]
EvidenceReviewStatus = Literal["not_reviewed", "reviewed_redacted", "rejected_sensitive"]


class ValidationEvidenceArtifact(BaseModel):
    """One expected or present external-validation evidence artifact."""

    artifact_id: str
    filename: str
    producer_task_id: str
    validates_gap_ids: list[str] = Field(default_factory=list)
    expected_path: str
    status: EvidenceArtifactStatus
    required_for_production: bool = True
    sensitive_handling: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    sha256: str | None = None
    byte_count: int | None = None
    review_status: EvidenceReviewStatus = "not_reviewed"
    content_inspected: Literal[False] = False
    raw_content_included: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed_by_ledger: Literal[False] = False


class ValidationEvidenceLedger(BaseModel):
    """Local inventory of Phase 11 expected validation evidence artifacts."""

    ledger_version: Literal["1"] = "1"
    phase: Literal["12"] = "12"
    source_phase: Literal["11"] = "11"
    title: str = "BountyClaw Validation Evidence Ledger"
    repository_root: str
    evidence_directory: str
    artifacts: list[ValidationEvidenceArtifact] = Field(default_factory=list)
    artifact_count: int
    present_count: int
    missing_count: int
    reviewed_count: int
    rejected_count: int
    gaps_with_present_evidence: list[str] = Field(default_factory=list)
    gaps_without_present_evidence: list[str] = Field(default_factory=list)
    ready_for_evidence_review: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed_by_ledger: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class GapEvidenceStatus(BaseModel):
    """Evidence coverage for one production gap."""

    gap_id: str
    expected_artifact_ids: list[str] = Field(default_factory=list)
    present_artifact_ids: list[str] = Field(default_factory=list)
    missing_artifact_ids: list[str] = Field(default_factory=list)
    reviewed_artifact_ids: list[str] = Field(default_factory=list)
    rejected_artifact_ids: list[str] = Field(default_factory=list)
    evidence_present: bool
    all_expected_artifacts_present: bool
    human_review_required: Literal[True] = True
    can_close_gap: Literal[False] = False
    closure_blocker: str


class GapClosureReadinessResult(BaseModel):
    """Gap closure readiness summary derived from the local evidence ledger."""

    result_version: Literal["1"] = "1"
    phase: Literal["12"] = "12"
    source_phase: Literal["11"] = "11"
    repository_root: str
    evidence_directory: str
    gap_statuses: list[GapEvidenceStatus] = Field(default_factory=list)
    gap_count: int
    gaps_with_any_evidence: int
    gaps_with_all_expected_evidence: int
    gaps_ready_for_human_review: int
    gaps_ready_for_closure: Literal[0] = 0
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed_by_ledger: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationEvidenceExportResult(BaseModel):
    """Result from exporting a local validation evidence ledger package."""

    result_version: Literal["1"] = "1"
    phase: Literal["12"] = "12"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    artifact_count: int
    present_count: int
    missing_count: int
    gap_count: int
    ready_for_evidence_review: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed_by_ledger: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationEvidenceCheck(BaseModel):
    """One local Phase 12 evidence-ledger readiness check."""

    check_id: str
    status: EvidenceCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class ValidationEvidenceVerificationResult(BaseModel):
    """Aggregated Phase 12 verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["12"] = "12"
    source_phase: Literal["11"] = "11"
    repository_root: str
    evidence_directory: str
    checks: list[ValidationEvidenceCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed_by_ledger: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    live_provider_validation_executed: Literal[False] = False
    mcp_browser_runtime_validation_executed: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
