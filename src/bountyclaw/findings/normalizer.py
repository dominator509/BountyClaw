"""Canonical finding normalization for Phase 4."""

from __future__ import annotations

import hashlib
from collections import OrderedDict

from bountyclaw.scanning.models import PreliminaryFinding, ScannerRunResult

from .models import CanonicalFinding, EvidenceRecord, NormalizationResult
from .redaction import redact_text


def normalize_scanner_run(result: ScannerRunResult) -> NormalizationResult:
    """Convert preliminary scanner findings into canonical redacted records.

    Deduplication is deterministic and based on repository fingerprint, scanner,
    rule, file path, and line number. No LLM calls or active validation are used.
    """

    findings_by_id: OrderedDict[str, CanonicalFinding] = OrderedDict()
    evidence_records: list[EvidenceRecord] = []
    total_redactions = 0

    for preliminary in sorted(
        result.findings,
        key=lambda item: (
            item.scanner_id,
            item.rule_id,
            item.file_path,
            item.line_number or 0,
            item.finding_id,
        ),
    ):
        canonical_id, dedupe_key = _canonical_identity(
            result.repository_fingerprint_id, preliminary
        )
        title = redact_text(preliminary.title)
        description = redact_text(preliminary.description)
        remediation = redact_text(preliminary.remediation_hint or "")
        evidence_summary = redact_text(preliminary.evidence_summary)
        total_redactions += (
            title.redaction_count
            + description.redaction_count
            + remediation.redaction_count
            + evidence_summary.redaction_count
        )

        evidence_id = _evidence_id(
            canonical_id, preliminary.finding_id, evidence_summary.redacted_text
        )
        evidence = EvidenceRecord(
            evidence_id=evidence_id,
            canonical_finding_id=canonical_id,
            evidence_kind=preliminary.evidence_kind,
            summary=evidence_summary.redacted_text,
            content=evidence_summary.redacted_text,
            redaction_status=evidence_summary.redaction_status,
            redaction_count=evidence_summary.redaction_count,
            source_excerpt_included=False,
            metadata={
                "source_preliminary_id": preliminary.finding_id,
                "scanner_id": preliminary.scanner_id,
                "scanner_version": preliminary.scanner_version,
                "rule_id": preliminary.rule_id,
                "source_redaction_status": preliminary.redaction_status,
            },
        )
        evidence_records.append(evidence)

        existing = findings_by_id.get(canonical_id)
        if existing is None:
            canonical = CanonicalFinding(
                canonical_finding_id=canonical_id,
                dedupe_key=dedupe_key,
                source_preliminary_ids=[preliminary.finding_id],
                scanner_ids=[preliminary.scanner_id],
                scanner_rule_ids=[preliminary.rule_id],
                title=title.redacted_text,
                description=description.redacted_text,
                vulnerability_class=preliminary.cwe or preliminary.rule_id,
                severity=preliminary.severity,
                confidence=preliminary.confidence,
                target=preliminary.target,
                file_path=preliminary.file_path,
                line_number=preliminary.line_number,
                cwe=preliminary.cwe,
                affected_component=preliminary.file_path,
                remediation_guidance=remediation.redacted_text or None,
                evidence_ids=[evidence_id],
                evidence_count=1,
                metadata={
                    "normalization_source": "phase4.scanner_run",
                    "source_excerpt_included": False,
                    "scanner_versions": {preliminary.scanner_id: preliminary.scanner_version},
                },
            )
            findings_by_id[canonical_id] = canonical
            continue

        updated_source_ids = sorted({*existing.source_preliminary_ids, preliminary.finding_id})
        updated_scanner_ids = sorted({*existing.scanner_ids, preliminary.scanner_id})
        updated_rule_ids = sorted({*existing.scanner_rule_ids, preliminary.rule_id})
        updated_evidence_ids = sorted({*existing.evidence_ids, evidence_id})
        findings_by_id[canonical_id] = existing.model_copy(
            update={
                "source_preliminary_ids": updated_source_ids,
                "scanner_ids": updated_scanner_ids,
                "scanner_rule_ids": updated_rule_ids,
                "evidence_ids": updated_evidence_ids,
                "evidence_count": len(updated_evidence_ids),
            }
        )

    return NormalizationResult(
        scan_execution_id=result.scan_execution_id,
        repository=result.repository,
        repository_fingerprint_id=result.repository_fingerprint_id,
        canonical_findings=list(findings_by_id.values()),
        evidence_records=evidence_records,
        redaction_count=total_redactions,
        notes=[
            "Phase 4 normalization is deterministic and does not use LLM, MCP, browser, network, active validation, or report submission.",
            "All evidence text passed through the redaction engine before persistence.",
            "Canonical findings require human triage before report drafting.",
        ],
    )


def _canonical_identity(
    repository_fingerprint_id: str, finding: PreliminaryFinding
) -> tuple[str, str]:
    dedupe_key = "|".join(
        [
            repository_fingerprint_id,
            finding.scanner_id,
            finding.rule_id,
            finding.file_path,
            str(finding.line_number or ""),
        ]
    )
    digest = hashlib.sha256(dedupe_key.encode("utf-8")).hexdigest()
    return f"bcfind-sha256:{digest[:32]}", dedupe_key


def _evidence_id(
    canonical_finding_id: str, source_preliminary_id: str, redacted_summary: str
) -> str:
    material = "|".join([canonical_finding_id, source_preliminary_id, redacted_summary])
    return f"bcevidence-sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:32]}"
