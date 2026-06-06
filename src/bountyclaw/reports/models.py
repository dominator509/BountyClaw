"""Human-reviewed triage and report-drafting models for Phase 6.

Phase 6 converts redacted stored findings into deterministic bounty-report
_drafts_. Drafts are never submissions. They intentionally preserve uncertainty,
record whether active validation was performed, and require manual human review.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from bountyclaw.scanning.models import Confidence, Severity

TriageReviewStatus = Literal[
    "needs_review",
    "needs_more_evidence",
    "approved_for_draft",
    "rejected_false_positive",
]
DraftFormat = Literal["markdown"]
ReportValidationStatus = Literal["not_validated_static_only"]
ReportDraftStatus = Literal["draft_requires_human_review"]


class TriageReview(BaseModel):
    """Human-supplied review state for one canonical finding."""

    review_version: Literal["1"] = "1"
    canonical_finding_id: str
    review_status: TriageReviewStatus
    reviewer: str = Field(min_length=1)
    rationale: str = Field(min_length=12)
    impact_assessment: str | None = None
    recommended_action: str | None = None
    reviewed_at: str
    model_triage_request_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReportDraft(BaseModel):
    """Deterministic, non-submitting bounty report draft."""

    draft_version: Literal["1"] = "1"
    report_draft_id: str
    canonical_finding_id: str
    repository: str
    store_path: str
    draft_format: DraftFormat = "markdown"
    draft_status: ReportDraftStatus = "draft_requires_human_review"
    title: str
    executive_summary: str
    affected_asset: str
    vulnerability_class: str
    severity: Severity
    confidence: Confidence
    evidence_summary: str
    technical_details: str
    safe_reproduction_checklist: list[str] = Field(default_factory=list)
    impact_statement: str
    remediation: str
    validation_status: ReportValidationStatus = "not_validated_static_only"
    human_review_status: TriageReviewStatus
    human_review_required: Literal[True] = True
    submission_allowed: Literal[False] = False
    automated_submission_used: Literal[False] = False
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    evidence_ids: list[str] = Field(default_factory=list)
    model_triage_summary: str | None = None
    content_markdown: str
    notes: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class StoredReportDraftSummary(BaseModel):
    """Summary row for locally persisted report drafts."""

    report_draft_id: str
    canonical_finding_id: str
    title: str
    severity: Severity
    confidence: Confidence
    draft_status: ReportDraftStatus
    validation_status: ReportValidationStatus
    submission_allowed: Literal[False]
    created_at: str


class ReportDraftResult(BaseModel):
    """Phase 6 report-drafting service result."""

    result_version: Literal["1"] = "1"
    triage_review: TriageReview
    report_draft: ReportDraft
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
