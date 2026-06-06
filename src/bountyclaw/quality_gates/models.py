"""Local quality/security gate models for Phase 19.

Phase 19 records locally executable gate definitions and verification metadata.
It does not contact targets, inspect raw validation evidence, close production
contexts, or claim hosted CI/online dependency audit completion.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

QualityGateStatus = Literal["pass", "fail", "deferred"]
QualityGateKind = Literal[
    "test",
    "compile",
    "format",
    "lint",
    "typecheck",
    "security",
    "dependency_audit",
    "package_build",
    "clean_install",
]


class QualityGateDefinition(BaseModel):
    """One local quality/security gate command definition."""

    gate_id: str
    kind: QualityGateKind
    title: str
    command: str
    local_execution_status: QualityGateStatus
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    environment_limitation: str | None = None
    evidence_summary: str | None = None
    remediation_summary: str | None = None


class QualityGateChecklist(BaseModel):
    """Phase 19 quality/security gate checklist."""

    result_version: Literal["1"] = "1"
    phase: Literal["19"] = "19"
    source_phase: Literal["18"] = "18"
    repository_root: str
    gates: list[QualityGateDefinition] = Field(default_factory=list)
    gate_count: int
    passed_count: int
    failed_count: int
    deferred_count: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class QualityGateVerificationCheck(BaseModel):
    """One metadata verification check for Phase 19 gate readiness."""

    check_id: str
    status: QualityGateStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class QualityGateVerificationResult(BaseModel):
    """Phase 19 quality/security gate readiness verification."""

    result_version: Literal["1"] = "1"
    phase: Literal["19"] = "19"
    source_phase: Literal["18"] = "18"
    repository_root: str
    checks: list[QualityGateVerificationCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class QualityGateExportResult(BaseModel):
    """Export result for Phase 19 local gate artifacts."""

    result_version: Literal["1"] = "1"
    phase: Literal["19"] = "19"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    gate_count: int
    passed_count: int
    failed_count: int
    deferred_count: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
