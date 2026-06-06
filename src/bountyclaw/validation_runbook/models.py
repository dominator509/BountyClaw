"""External validation runbook and execution-journal models for Phase 15.

Phase 15 is local-only governance tooling. It converts unresolved gap backlog
items into deterministic external runbook steps and provides a metadata-only
execution journal schema for Codex/local/CI/human executors. It does not run
external validations, inspect raw evidence, close gaps, raise production
readiness, contact targets, call live providers, launch MCP/browser runtimes, or
submit reports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

RunbookCheckStatus = Literal["pass", "fail", "deferred"]
RunbookStepStatus = Literal["pending", "recorded", "passed", "failed", "blocked", "needs_review"]
JournalEntryStatus = Literal["planned", "started", "passed", "failed", "blocked", "needs_review"]
RunbookRiskLevel = Literal["critical", "high", "medium", "low", "unknown"]


class ExternalValidationRunbookStep(BaseModel):
    """One future external-validation step derived from a production gap."""

    step_id: str
    source_backlog_task_id: str
    gap_id: str
    priority_rank: int
    risk_level: RunbookRiskLevel
    phase_association: str
    subsystem_association: str
    objective: str
    required_environment: str
    recommended_future_agent_type: str
    prerequisite_summary: str
    command_or_step_summary: str
    expected_evidence_summary: str
    completion_criteria: str
    rollback_considerations: str
    human_review_required: Literal[True] = True
    raw_evidence_content_allowed: Literal[False] = False
    auto_gap_closure_allowed: Literal[False] = False
    production_readiness_increase_allowed: Literal[False] = False


class ExternalValidationRunbook(BaseModel):
    """Deterministic runbook for future Codex/local/CI/human validation."""

    runbook_version: Literal["1"] = "1"
    phase: Literal["15"] = "15"
    source_phase: Literal["14"] = "14"
    title: str = "BountyClaw External Validation Runbook"
    repository_root: str
    steps: list[ExternalValidationRunbookStep] = Field(default_factory=list)
    step_count: int
    critical_or_high_count: int
    medium_count: int
    low_or_unknown_count: int
    ready_for_codex_execution: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationRunJournalEntry(BaseModel):
    """Metadata-only record of one future external-validation task run."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    step_id: str
    source_backlog_task_id: str
    gap_id: str
    status: JournalEntryStatus = "planned"
    executor: str | None = None
    executor_agent_type: str | None = None
    environment: str | None = None
    started_at_utc: str | None = None
    completed_at_utc: str | None = None
    command_summary: str | None = None
    evidence_artifact_ids: list[str] = Field(default_factory=list)
    evidence_sha256: dict[str, str] = Field(default_factory=dict)
    evidence_storage_reference: str | None = None
    reviewer_required: Literal[True] = True
    raw_evidence_contents_included: Literal[False] = False
    production_gap_closed: Literal[False] = False
    production_readiness_changed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_metadata_only(self) -> ValidationRunJournalEntry:
        if self.raw_evidence_contents_included:
            raise ValueError("run journal entries must not include raw evidence contents")
        if self.production_gap_closed:
            raise ValueError("run journal entries must not close production gaps")
        if self.production_readiness_changed:
            raise ValueError("run journal entries must not change production readiness")
        if self.status == "passed":
            if not self.executor:
                raise ValueError("passed journal entries require executor metadata")
            if not self.environment:
                raise ValueError("passed journal entries require environment metadata")
            if not self.completed_at_utc:
                raise ValueError("passed journal entries require completed_at_utc")
            if not self.evidence_artifact_ids:
                raise ValueError("passed journal entries require evidence artifact IDs")
            missing_hashes = [
                artifact_id
                for artifact_id in self.evidence_artifact_ids
                if artifact_id not in self.evidence_sha256
            ]
            if missing_hashes:
                raise ValueError(
                    f"passed journal entries require SHA-256 hashes for artifacts: {missing_hashes}"
                )
        return self


class ValidationRunJournalFile(BaseModel):
    """Metadata-only future execution journal file."""

    model_config = ConfigDict(extra="forbid")

    journal_version: Literal["1"] = "1"
    phase: Literal["15"] = "15"
    source_phase: Literal["14"] = "14"
    entries: list[ValidationRunJournalEntry] = Field(default_factory=list)
    raw_evidence_contents_included: Literal[False] = False
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_no_closure(self) -> ValidationRunJournalFile:
        if self.raw_evidence_contents_included:
            raise ValueError("journal files must not include raw evidence contents")
        if self.ready_for_gap_closure or self.ready_for_production:
            raise ValueError("journal files must not claim gap closure or production readiness")
        return self


class ValidationRunStepStatus(BaseModel):
    """Status of one runbook step after joining optional journal metadata."""

    step_id: str
    source_backlog_task_id: str
    gap_id: str
    risk_level: RunbookRiskLevel
    status: RunbookStepStatus
    journal_run_ids: list[str] = Field(default_factory=list)
    evidence_artifact_ids: list[str] = Field(default_factory=list)
    evidence_sha256: dict[str, str] = Field(default_factory=dict)
    accepted_for_evidence_ledger: bool
    blockers: list[str] = Field(default_factory=list)


class ValidationRunJournalStatusResult(BaseModel):
    """Metadata-only status assessment for future validation run journals."""

    result_version: Literal["1"] = "1"
    phase: Literal["15"] = "15"
    source_phase: Literal["14"] = "14"
    repository_root: str
    journal_file: str
    step_statuses: list[ValidationRunStepStatus] = Field(default_factory=list)
    step_count: int
    passed_with_metadata_count: int
    failed_or_blocked_count: int
    missing_journal_count: int
    ready_for_evidence_ledger: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed_by_status: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationRunbookExportResult(BaseModel):
    """Result from exporting Phase 15 runbook and journal artifacts."""

    result_version: Literal["1"] = "1"
    phase: Literal["15"] = "15"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    step_count: int
    ready_for_codex_execution: bool
    ready_for_evidence_ledger: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationRunbookCheck(BaseModel):
    """One local Phase 15 runbook readiness check."""

    check_id: str
    status: RunbookCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class ValidationRunbookVerificationResult(BaseModel):
    """Aggregated local Phase 15 runbook verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["15"] = "15"
    source_phase: Literal["14"] = "14"
    repository_root: str
    checks: list[ValidationRunbookCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_evidence_ledger: bool
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
