"""Scanner adapter models for Phase 3.

Phase 3 supports controlled, local-only static scanner execution. Findings are
preliminary and intentionally avoid storing raw source excerpts because the full
secret-redaction and evidence-store layers are deferred to later phases.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, Protocol

from pydantic import BaseModel, Field

Severity = Literal["info", "low", "medium", "high", "critical"]
Confidence = Literal["low", "medium", "high"]


class ScannerSpec(BaseModel):
    """Stable metadata for a registered scanner adapter."""

    scanner_id: str
    name: str
    version: str
    adapter_family: str
    execution_mode: Literal["local_builtin", "external_subprocess"]
    network_required: Literal[False] = False
    llm_required: Literal[False] = False
    mcp_required: Literal[False] = False
    browser_required: Literal[False] = False
    writes_to_repository: Literal[False] = False


class PreliminaryFinding(BaseModel):
    """A normalized preliminary finding emitted by a Phase 3 scanner adapter."""

    finding_version: Literal["1"] = "1"
    finding_id: str
    scanner_id: str
    scanner_version: str
    rule_id: str
    title: str
    description: str
    severity: Severity
    confidence: Confidence
    target: str
    file_path: str
    line_number: int | None = Field(default=None, ge=1)
    evidence_kind: Literal[
        "redacted_line_reference",
        "metadata_only",
        "normalized_scanner_output",
    ] = "redacted_line_reference"
    evidence_summary: str
    source_excerpt_included: Literal[False] = False
    redaction_status: Literal[
        "no_raw_secret_values_captured",
        "external_output_unredacted_blocked",
    ] = "no_raw_secret_values_captured"
    cwe: str | None = None
    remediation_hint: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScannerRunResult(BaseModel):
    """Result of a controlled local static scanner run."""

    result_version: Literal["1"] = "1"
    scan_execution_id: str
    repository: str
    repository_fingerprint_id: str
    scanners_execute: Literal[True] = True
    network_used: Literal[False] = False
    llm_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    adapters: list[ScannerSpec] = Field(default_factory=list)
    findings: list[PreliminaryFinding] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class ScannerContext:
    """Runtime context passed to scanner adapters."""

    repository_root: Path
    repository_fingerprint_id: str
    max_file_bytes: int = 1_048_576


class ScannerAdapter(Protocol):
    """Protocol every scanner adapter must implement."""

    @property
    def spec(self) -> ScannerSpec:
        """Return immutable scanner metadata."""

    def supports(self, context: ScannerContext) -> bool:
        """Return whether this adapter should run for the current context."""

    def scan(self, context: ScannerContext) -> list[PreliminaryFinding]:
        """Execute the scanner and return normalized preliminary findings."""
