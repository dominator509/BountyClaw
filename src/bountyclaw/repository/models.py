"""Repository intake and deterministic scan-plan models.

Phase 2 stores metadata only. It does not persist source contents, execute
scanners, call models, access networks, or create evidence records.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class LanguageSummary(BaseModel):
    """Detected programming language metadata."""

    language: str
    file_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)


class PackageManifest(BaseModel):
    """Detected package, build, or configuration manifest."""

    path: str
    ecosystem: str
    kind: str


class RepositoryFingerprint(BaseModel):
    """Deterministic read-only repository fingerprint."""

    fingerprint_version: Literal["1"] = "1"
    fingerprint_id: str
    root: str
    root_name: str
    file_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    language_summaries: list[LanguageSummary] = Field(default_factory=list)
    package_manifests: list[PackageManifest] = Field(default_factory=list)
    ignored_directories: list[str] = Field(default_factory=list)


class ScanPlanStep(BaseModel):
    """A future scanner/review recommendation that is not executed in Phase 2."""

    step_id: str
    name: str
    action: str
    adapter_family: str
    reason: str
    execution_status: Literal["planned_not_executed"] = "planned_not_executed"
    requires_scope_action: str


class ScanPlan(BaseModel):
    """Deterministic scan plan generated from repository metadata."""

    plan_version: Literal["1"] = "1"
    repository: str
    repository_fingerprint_id: str
    scanners_execute: Literal[False] = False
    network_required: Literal[False] = False
    llm_required: Literal[False] = False
    mcp_required: Literal[False] = False
    browser_required: Literal[False] = False
    steps: list[ScanPlanStep] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
