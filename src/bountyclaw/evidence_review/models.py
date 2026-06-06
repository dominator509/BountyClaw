"""Evidence review and gap-closure proposal models for Phase 13.

Phase 13 is a local-only governance layer. It validates review-decision metadata
for future external-validation evidence artifacts, then drafts closure proposals
for human release/AppSec reviewers. It does not inspect raw evidence contents,
close production gaps, update readiness percentages, or claim production
readiness.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

EvidenceReviewDecision = Literal[
    "pending", "approved_redacted", "rejected_sensitive", "needs_remediation"
]
EvidenceReviewCheckStatus = Literal["pass", "fail", "deferred"]
EvidenceClosureProposalStatus = Literal[
    "blocked_missing_artifacts",
    "blocked_unreviewed_artifacts",
    "blocked_rejected_artifacts",
    "ready_for_human_gap_tracker_update",
]


class EvidenceReviewRecord(BaseModel):
    """One human review decision for one evidence artifact.

    The record is metadata only. It may reference artifact hashes and reviewer
    details, but it must never contain raw artifact contents.
    """

    artifact_id: str
    decision: EvidenceReviewDecision = "pending"
    reviewer: str | None = None
    reviewed_at_utc: str | None = None
    artifact_sha256: str | None = None
    rationale: str | None = None
    redacted_artifact_path: str | None = None
    sensitive_handling_notes: str | None = None
    raw_content_included: Literal[False] = False
    artifact_content_inspected_by_tooling: Literal[False] = False
    human_review_required: Literal[True] = True
    automated_gap_closure_allowed: Literal[False] = False


class EvidenceReviewDecisionFile(BaseModel):
    """Metadata-only review decision file produced by a future human reviewer."""

    file_version: Literal["1"] = "1"
    phase: Literal["13"] = "13"
    title: str = "BountyClaw Evidence Review Decisions"
    decisions: list[EvidenceReviewRecord] = Field(default_factory=list)
    raw_evidence_contents_included: Literal[False] = False
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class EvidenceReviewArtifactStatus(BaseModel):
    """Joined status for an evidence artifact and its optional review record."""

    artifact_id: str
    filename: str
    validates_gap_ids: list[str] = Field(default_factory=list)
    evidence_status: Literal["present", "missing"]
    ledger_sha256: str | None = None
    ledger_byte_count: int | None = None
    review_decision: EvidenceReviewDecision
    reviewer: str | None = None
    reviewed_at_utc: str | None = None
    reviewed_sha256: str | None = None
    sha256_matches_ledger: bool = False
    accepted_for_closure_proposal: bool = False
    blockers: list[str] = Field(default_factory=list)
    raw_content_included: Literal[False] = False
    artifact_content_inspected_by_tooling: Literal[False] = False


class EvidenceReviewTemplateResult(BaseModel):
    """Template for future human review decisions."""

    result_version: Literal["1"] = "1"
    phase: Literal["13"] = "13"
    source_phase: Literal["12"] = "12"
    repository_root: str
    evidence_directory: str
    review_file: str
    decisions: list[EvidenceReviewRecord] = Field(default_factory=list)
    decision_count: int
    ready_for_human_review: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class EvidenceReviewStatusResult(BaseModel):
    """Review status summary for future evidence artifacts."""

    result_version: Literal["1"] = "1"
    phase: Literal["13"] = "13"
    source_phase: Literal["12"] = "12"
    repository_root: str
    evidence_directory: str
    review_file: str
    artifacts: list[EvidenceReviewArtifactStatus] = Field(default_factory=list)
    artifact_count: int
    present_count: int
    missing_count: int
    reviewed_count: int
    approved_count: int
    rejected_count: int
    needs_remediation_count: int
    accepted_for_closure_proposal_count: int
    ready_for_human_gap_update: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class GapClosureProposal(BaseModel):
    """Draft closure proposal for one production gap.

    This object is only a proposal. It never mutates PRODUCTION_GAP_TRACKER.md.
    """

    gap_id: str
    expected_artifact_ids: list[str] = Field(default_factory=list)
    approved_artifact_ids: list[str] = Field(default_factory=list)
    missing_artifact_ids: list[str] = Field(default_factory=list)
    unreviewed_artifact_ids: list[str] = Field(default_factory=list)
    rejected_artifact_ids: list[str] = Field(default_factory=list)
    needs_remediation_artifact_ids: list[str] = Field(default_factory=list)
    proposal_status: EvidenceClosureProposalStatus
    ready_for_human_gap_tracker_update: bool
    auto_close_allowed: Literal[False] = False
    production_readiness_increase_allowed: Literal[False] = False
    required_manual_updates: list[str] = Field(default_factory=list)
    rollback_considerations: str


class GapClosureProposalResult(BaseModel):
    """Aggregate gap closure proposal result."""

    result_version: Literal["1"] = "1"
    phase: Literal["13"] = "13"
    source_phase: Literal["12"] = "12"
    repository_root: str
    evidence_directory: str
    review_file: str
    proposals: list[GapClosureProposal] = Field(default_factory=list)
    proposal_count: int
    proposals_ready_for_human_update: int
    proposals_blocked: int
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class EvidenceReviewExportResult(BaseModel):
    """Result from exporting a review package."""

    result_version: Literal["1"] = "1"
    phase: Literal["13"] = "13"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    artifact_count: int
    proposal_count: int
    proposals_ready_for_human_update: int
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class EvidenceReviewCheck(BaseModel):
    """One local Phase 13 evidence-review readiness check."""

    check_id: str
    status: EvidenceReviewCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class EvidenceReviewVerificationResult(BaseModel):
    """Aggregated Phase 13 verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["13"] = "13"
    source_phase: Literal["12"] = "12"
    repository_root: str
    evidence_directory: str
    review_file: str
    checks: list[EvidenceReviewCheck] = Field(default_factory=list)
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
    external_actions_executed: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    live_provider_validation_executed: Literal[False] = False
    mcp_browser_runtime_validation_executed: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
