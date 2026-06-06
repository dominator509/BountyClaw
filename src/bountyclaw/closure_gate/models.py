"""Phase 17 closure-gate and readiness-attestation models.

The closure gate is local-only governance tooling. It joins hash-only baseline
metadata, execution-journal status, validation-evidence metadata, human-review
metadata, and gap-tracker structure into a manual readiness gate. It never
inspects raw evidence contents, closes gaps, recalculates production readiness,
runs external validation, contacts targets, or submits bounty reports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ClosureGateCheckStatus = Literal["pass", "fail", "deferred"]
AttestationDecision = Literal[
    "pending",
    "approved_for_manual_gap_update",
    "rejected",
    "needs_remediation",
]
AttestationStatus = Literal["pending", "candidate", "blocked", "rejected", "needs_remediation"]


class ReadinessAttestationRecord(BaseModel):
    """Metadata-only human readiness attestation record.

    The record may support a future human gap-tracker update, but it cannot close
    gaps or raise production readiness by itself.
    """

    attestation_id: str
    baseline_id: str | None = None
    decision: AttestationDecision = "pending"
    reviewer: str | None = None
    reviewed_at_utc: str | None = None
    rationale: str | None = None
    approved_gap_ids: list[str] = Field(default_factory=list)
    referenced_evidence_artifact_ids: list[str] = Field(default_factory=list)
    referenced_run_ids: list[str] = Field(default_factory=list)
    evidence_review_decision_sha256: str | None = None
    execution_journal_sha256: str | None = None
    gap_tracker_sha256: str | None = None
    notes: list[str] = Field(default_factory=list)
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    prod_gap_closed_by_attestation: Literal[False] = False
    prod_readiness_changed_by_attestation: Literal[False] = False


class ReadinessAttestationFile(BaseModel):
    """Metadata-only attestation file for future human release/AppSec review."""

    file_version: Literal["1"] = "1"
    phase: Literal["17"] = "17"
    source_phase: Literal["16"] = "16"
    attestations: list[ReadinessAttestationRecord] = Field(default_factory=list)
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    auto_gap_closure_allowed: Literal[False] = False
    production_readiness_increase_allowed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ReadinessAttestationTemplateResult(BaseModel):
    """Template output for future readiness attestations."""

    result_version: Literal["1"] = "1"
    phase: Literal["17"] = "17"
    source_phase: Literal["16"] = "16"
    repository_root: str
    attestation_file: str
    baseline_id: str
    template: ReadinessAttestationFile
    candidate_gap_ids: list[str] = Field(default_factory=list)
    ready_for_human_attestation: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ClosureGateAttestationStatus(BaseModel):
    """Validation status for one metadata-only attestation record."""

    attestation_id: str
    decision: AttestationDecision
    status: AttestationStatus
    baseline_id: str | None = None
    baseline_matches_current: bool
    approved_gap_ids: list[str] = Field(default_factory=list)
    accepted_gap_ids: list[str] = Field(default_factory=list)
    referenced_evidence_artifact_ids: list[str] = Field(default_factory=list)
    referenced_run_ids: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    accepted_for_manual_gap_update_proposal: bool
    auto_gap_closure_allowed: Literal[False] = False
    production_readiness_increase_allowed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False


class ClosureGateStatusResult(BaseModel):
    """Aggregate closure-gate status.

    A positive `ready_for_human_gap_update_review` means only that metadata is
    ready for a future human/manual governance update review. It does not close
    gaps or mark production ready.
    """

    result_version: Literal["1"] = "1"
    phase: Literal["17"] = "17"
    source_phase: Literal["16"] = "16"
    repository_root: str
    baseline_id: str
    attestation_file: str
    attestation_statuses: list[ClosureGateAttestationStatus] = Field(default_factory=list)
    attestation_count: int
    accepted_attestation_count: int
    candidate_gap_ids: list[str] = Field(default_factory=list)
    gap_tracker_entry_count: int
    evidence_artifact_count: int
    present_evidence_artifact_count: int
    accepted_review_artifact_count: int
    journal_steps_with_metadata_count: int
    ready_for_human_gap_update_review: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ClosureGateExportResult(BaseModel):
    """Result from exporting the Phase 17 closure-gate package."""

    result_version: Literal["1"] = "1"
    phase: Literal["17"] = "17"
    output_directory: str
    baseline_id: str
    written_files: list[str] = Field(default_factory=list)
    attestation_count: int
    candidate_gap_count: int
    ready_for_human_gap_update_review: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ClosureGateCheck(BaseModel):
    """One local Phase 17 closure-gate readiness check."""

    check_id: str
    status: ClosureGateCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class ClosureGateVerificationResult(BaseModel):
    """Aggregated local Phase 17 closure-gate verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["17"] = "17"
    source_phase: Literal["16"] = "16"
    repository_root: str
    baseline_id: str
    checks: list[ClosureGateCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_human_gap_update_review: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    live_provider_validation_executed: Literal[False] = False
    mcp_browser_runtime_validation_executed: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
