"""Validation evidence ledger services for Phase 12.

These services are local-only. They inventory future validation artifacts that a
Codex/local/CI/human executor may produce, hash present files, and map evidence
to production gaps. They do not inspect artifact contents, execute external
validation, close gaps, contact networks, or claim production readiness.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from bountyclaw.handoff import build_evidence_template, verify_handoff_readiness
from bountyclaw.hardening import verify_local_hardening
from bountyclaw.release import verify_release_controls

from .models import (
    GapClosureReadinessResult,
    GapEvidenceStatus,
    ValidationEvidenceArtifact,
    ValidationEvidenceCheck,
    ValidationEvidenceExportResult,
    ValidationEvidenceLedger,
    ValidationEvidenceVerificationResult,
)

MANDATORY_PHASE_12_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_11_SUBROADMAP.md",
    "PHASE_12_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
)

MANDATORY_PHASE_12_SUPPORT_FILES: tuple[str, ...] = (
    "RELEASE.md",
    "ROLLBACK.md",
    "SECURITY_VALIDATION.md",
    "scripts/phase9_verify.py",
    "scripts/phase10_verify.py",
    "scripts/phase11_verify.py",
    "scripts/phase12_verify.py",
)

EXPECTED_PHASE_12_GAP_IDS: tuple[str, ...] = ("PGT-100", "PGT-101", "PGT-102")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _pass_fail(
    *,
    check_id: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> ValidationEvidenceCheck:
    return ValidationEvidenceCheck(
        check_id=check_id,
        status="pass" if passed else "fail",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_codex=required_for_codex,
        required_for_production=required_for_production,
        evidence=evidence or [],
    )


def _deferred(
    *,
    check_id: str,
    summary: str,
    deferred_reason: str,
    future_validation_required: str,
    future_environment_required: str,
    required_for_commit: bool = False,
    required_for_codex: bool = False,
    required_for_production: bool = True,
) -> ValidationEvidenceCheck:
    return ValidationEvidenceCheck(
        check_id=check_id,
        status="deferred",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_codex=required_for_codex,
        required_for_production=required_for_production,
        deferred_reason=deferred_reason,
        future_validation_required=future_validation_required,
        future_environment_required=future_environment_required,
    )


def _sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    byte_count = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            byte_count += len(chunk)
            digest.update(chunk)
    return digest.hexdigest(), byte_count


def _artifact_path(evidence_dir: Path, filename: str) -> Path:
    relative = Path(filename)
    if relative.parts and relative.parts[0] == evidence_dir.name:
        relative = Path(*relative.parts[1:]) if len(relative.parts) > 1 else Path(relative.name)
    return evidence_dir / relative


def build_validation_evidence_ledger(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
) -> ValidationEvidenceLedger:
    """Build a local artifact inventory from the Phase 11 evidence template.

    Present files are hashed in streaming mode. File contents are not printed,
    parsed, summarized, classified, or trusted by this ledger.
    """

    resolved_root = root.expanduser().resolve(strict=False)
    resolved_evidence_dir = evidence_dir.expanduser()
    if not resolved_evidence_dir.is_absolute():
        resolved_evidence_dir = resolved_root / resolved_evidence_dir
    resolved_evidence_dir = resolved_evidence_dir.resolve(strict=False)

    template = build_evidence_template(resolved_root)
    artifacts: list[ValidationEvidenceArtifact] = []
    gaps_expected: set[str] = set()
    gaps_present: set[str] = set()

    for expected in template.artifacts:
        expected_path = _artifact_path(resolved_evidence_dir, expected.filename)
        path_is_file = expected_path.exists() and expected_path.is_file()
        sha256: str | None = None
        byte_count: int | None = None
        if path_is_file:
            sha256, byte_count = _sha256_file(expected_path)
            gaps_present.update(expected.validates_gap_ids)
        gaps_expected.update(expected.validates_gap_ids)
        artifacts.append(
            ValidationEvidenceArtifact(
                artifact_id=expected.artifact_id,
                filename=expected.filename,
                producer_task_id=expected.producer_task_id,
                validates_gap_ids=expected.validates_gap_ids,
                expected_path=str(expected_path),
                status="present" if path_is_file else "missing",
                required_for_production=expected.required_for_production,
                sensitive_handling=expected.sensitive_handling,
                acceptance_criteria=expected.acceptance_criteria,
                sha256=sha256,
                byte_count=byte_count,
            )
        )

    present_count = sum(1 for artifact in artifacts if artifact.status == "present")
    missing_count = sum(1 for artifact in artifacts if artifact.status == "missing")
    reviewed_count = sum(
        1 for artifact in artifacts if artifact.review_status == "reviewed_redacted"
    )
    rejected_count = sum(
        1 for artifact in artifacts if artifact.review_status == "rejected_sensitive"
    )
    return ValidationEvidenceLedger(
        repository_root=str(resolved_root),
        evidence_directory=str(resolved_evidence_dir),
        artifacts=artifacts,
        artifact_count=len(artifacts),
        present_count=present_count,
        missing_count=missing_count,
        reviewed_count=reviewed_count,
        rejected_count=rejected_count,
        gaps_with_present_evidence=sorted(gaps_present),
        gaps_without_present_evidence=sorted(gaps_expected - gaps_present),
        ready_for_evidence_review=present_count > 0 and rejected_count == 0,
        notes=[
            "Validation evidence ledger generation is local-only and non-networked.",
            "Artifact files are hashed but not content-inspected, trusted, or printed.",
            "ready_for_gap_closure remains false until a human release/AppSec reviewer approves evidence and governance files are updated.",
        ],
    )


def assess_gap_closure_readiness(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
) -> GapClosureReadinessResult:
    """Map expected evidence artifacts to production-gap closure readiness."""

    ledger = build_validation_evidence_ledger(root, evidence_dir)
    expected_by_gap: dict[str, list[str]] = defaultdict(list)
    present_by_gap: dict[str, list[str]] = defaultdict(list)
    missing_by_gap: dict[str, list[str]] = defaultdict(list)
    reviewed_by_gap: dict[str, list[str]] = defaultdict(list)
    rejected_by_gap: dict[str, list[str]] = defaultdict(list)

    for artifact in ledger.artifacts:
        for gap_id in artifact.validates_gap_ids:
            expected_by_gap[gap_id].append(artifact.artifact_id)
            if artifact.status == "present":
                present_by_gap[gap_id].append(artifact.artifact_id)
            else:
                missing_by_gap[gap_id].append(artifact.artifact_id)
            if artifact.review_status == "reviewed_redacted":
                reviewed_by_gap[gap_id].append(artifact.artifact_id)
            if artifact.review_status == "rejected_sensitive":
                rejected_by_gap[gap_id].append(artifact.artifact_id)

    statuses: list[GapEvidenceStatus] = []
    for gap_id in sorted(expected_by_gap):
        expected = sorted(expected_by_gap[gap_id])
        present = sorted(present_by_gap.get(gap_id, []))
        missing = sorted(missing_by_gap.get(gap_id, []))
        rejected = sorted(rejected_by_gap.get(gap_id, []))
        if rejected:
            blocker = "one or more evidence artifacts were rejected as sensitive"
        elif missing:
            blocker = "one or more expected evidence artifacts are missing"
        elif present:
            blocker = "human release/AppSec review is required before closing this gap"
        else:
            blocker = "no evidence artifacts are present"
        statuses.append(
            GapEvidenceStatus(
                gap_id=gap_id,
                expected_artifact_ids=expected,
                present_artifact_ids=present,
                missing_artifact_ids=missing,
                reviewed_artifact_ids=sorted(reviewed_by_gap.get(gap_id, [])),
                rejected_artifact_ids=rejected,
                evidence_present=bool(present),
                all_expected_artifacts_present=not missing and bool(expected),
                closure_blocker=blocker,
            )
        )

    gaps_with_any_evidence = sum(1 for status in statuses if status.evidence_present)
    gaps_with_all_expected_evidence = sum(
        1 for status in statuses if status.all_expected_artifacts_present
    )
    gaps_ready_for_human_review = sum(
        1
        for status in statuses
        if status.all_expected_artifacts_present and not status.rejected_artifact_ids
    )
    return GapClosureReadinessResult(
        repository_root=ledger.repository_root,
        evidence_directory=ledger.evidence_directory,
        gap_statuses=statuses,
        gap_count=len(statuses),
        gaps_with_any_evidence=gaps_with_any_evidence,
        gaps_with_all_expected_evidence=gaps_with_all_expected_evidence,
        gaps_ready_for_human_review=gaps_ready_for_human_review,
        notes=[
            "Gap readiness is evidence-presence mapping only.",
            "No gap is closed by this command. Update PRODUCTION_GAP_TRACKER.md only after real evidence review.",
        ],
    )


def _ledger_markdown(ledger: ValidationEvidenceLedger, readiness: GapClosureReadinessResult) -> str:
    lines = [
        "# BountyClaw Validation Evidence Ledger",
        "",
        "This ledger inventories expected future validation artifacts. It does not prove external validation has run and does not close production gaps.",
        "",
        f"- Phase: {ledger.phase}",
        f"- Source phase: {ledger.source_phase}",
        f"- Evidence directory: `{ledger.evidence_directory}`",
        f"- Artifact count: {ledger.artifact_count}",
        f"- Present artifacts: {ledger.present_count}",
        f"- Missing artifacts: {ledger.missing_count}",
        f"- Ready for evidence review: {ledger.ready_for_evidence_review}",
        f"- Ready for gap closure: {ledger.ready_for_gap_closure}",
        f"- Ready for production: {ledger.ready_for_production}",
        "",
        "## Artifact Inventory",
        "",
        "| Artifact ID | Task | Status | SHA-256 | Gaps |",
        "|---|---|---:|---|---|",
    ]
    for artifact in ledger.artifacts:
        sha = artifact.sha256 or "missing"
        gaps = ", ".join(artifact.validates_gap_ids)
        lines.append(
            f"| {artifact.artifact_id} | {artifact.producer_task_id} | {artifact.status} | `{sha}` | {gaps} |"
        )
    lines.extend(
        [
            "",
            "## Gap Readiness",
            "",
            "| Gap | Present | Missing | Can Close | Blocker |",
            "|---|---:|---:|---:|---|",
        ]
    )
    for status in readiness.gap_statuses:
        lines.append(
            f"| {status.gap_id} | {len(status.present_artifact_ids)} | {len(status.missing_artifact_ids)} | {status.can_close_gap} | {status.closure_blocker} |"
        )
    lines.extend(
        [
            "",
            "## Mandatory Closure Rule",
            "",
            "No gap may be closed by this ledger alone. A human release/AppSec reviewer must confirm evidence provenance, redaction, acceptance criteria, and rollback implications before governance files are updated.",
        ]
    )
    return "\n".join(lines)


def export_validation_evidence_ledger(
    root: Path,
    evidence_dir: Path,
    output_dir: Path,
) -> ValidationEvidenceExportResult:
    """Export a deterministic evidence-ledger package without external actions."""

    resolved_output = output_dir.expanduser().resolve(strict=False)
    resolved_output.mkdir(parents=True, exist_ok=True)
    ledger = build_validation_evidence_ledger(root, evidence_dir)
    readiness = assess_gap_closure_readiness(root, evidence_dir)

    files = {
        "validation_evidence_ledger.json": ledger.model_dump_json(indent=2),
        "gap_closure_readiness.json": readiness.model_dump_json(indent=2),
        "VALIDATION_EVIDENCE_LEDGER.md": _ledger_markdown(ledger, readiness),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))

    manifest_path = resolved_output / "validation_evidence_manifest.json"
    manifest = {
        "phase": "12",
        "source_phase": "11",
        "artifact_count": ledger.artifact_count,
        "present_count": ledger.present_count,
        "missing_count": ledger.missing_count,
        "gap_count": readiness.gap_count,
        "ready_for_evidence_review": ledger.ready_for_evidence_review,
        "ready_for_gap_closure": False,
        "ready_for_production": False,
        "network_used": False,
        "external_actions_executed_by_ledger": False,
        "written_files": written_files,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(manifest_path))

    return ValidationEvidenceExportResult(
        output_directory=str(resolved_output),
        written_files=written_files,
        artifact_count=ledger.artifact_count,
        present_count=ledger.present_count,
        missing_count=ledger.missing_count,
        gap_count=readiness.gap_count,
        ready_for_evidence_review=ledger.ready_for_evidence_review,
        notes=[
            "Validation evidence export is local-only.",
            "Generated ledger files contain hashes and metadata only; they are not production validation evidence by themselves.",
        ],
    )


def verify_validation_evidence_readiness(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
) -> ValidationEvidenceVerificationResult:
    """Verify Phase 12 evidence-ledger readiness without closing gaps."""

    resolved_root = root.expanduser().resolve(strict=False)
    checks: list[ValidationEvidenceCheck] = []

    for filename in MANDATORY_PHASE_12_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"EVIDENCE-GOV-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 12 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_12_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"EVIDENCE-SUPPORT-{filename}",
                passed=path.exists(),
                summary=f"Phase 12 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    roadmap = _read_text(resolved_root / "ROADMAP.md")
    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    gaps = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    handoff_doc = _read_text(resolved_root / "PHASE_11_SUBROADMAP.md")
    phase12_doc = _read_text(resolved_root / "PHASE_12_SUBROADMAP.md")
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    checks.extend(
        [
            _pass_fail(
                check_id="EVIDENCE-GOV-ROADMAP-PHASE12",
                passed="Phase 12" in roadmap and "Validation Evidence Ledger" in roadmap,
                summary="ROADMAP.md records Phase 12 evidence-ledger completion and remaining external validation.",
                evidence=["Phase 12 roadmap marker found"] if "Phase 12" in roadmap else [],
            ),
            _pass_fail(
                check_id="EVIDENCE-GOV-ARCH-PHASE12",
                passed="Phase 12" in architecture and "Validation Evidence Ledger" in architecture,
                summary="ARCHITECTURE.md records Phase 12 validation evidence ledger subsystem.",
                evidence=["Phase 12 architecture marker found"]
                if "Phase 12" in architecture
                else [],
            ),
            _pass_fail(
                check_id="EVIDENCE-GOV-GAPS-PHASE12",
                passed=all(gap_id in gaps for gap_id in EXPECTED_PHASE_12_GAP_IDS),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 12 evidence-ledger gaps.",
                evidence=list(EXPECTED_PHASE_12_GAP_IDS) if gaps else [],
            ),
            _pass_fail(
                check_id="EVIDENCE-GOV-HANDOFF-UPDATED",
                passed="validation evidence ledger" in handoff_doc.lower()
                or "Phase 12" in handoff_doc,
                summary="Phase 11 handoff documentation references Phase 12 evidence-ledger continuation.",
                evidence=["PHASE_11_SUBROADMAP.md references evidence-ledger continuation"]
                if handoff_doc
                else [],
            ),
            _pass_fail(
                check_id="EVIDENCE-GOV-PHASE12-COMPLETE",
                passed="Completed in ChatGPT Project Mode" in phase12_doc,
                summary="PHASE_12_SUBROADMAP.md records local completion status.",
                evidence=["PHASE_12_SUBROADMAP.md completion marker found"] if phase12_doc else [],
            ),
            _pass_fail(
                check_id="EVIDENCE-CI-PHASE12-VERIFY-DEFINED",
                passed="python scripts/phase12_verify.py --root ." in workflow,
                summary="CI definition includes Phase 12 validation-evidence verification script.",
                evidence=["python scripts/phase12_verify.py --root ."]
                if "phase12_verify.py" in workflow
                else [],
            ),
        ]
    )

    template = build_evidence_template(resolved_root)
    ledger = build_validation_evidence_ledger(resolved_root, evidence_dir)
    readiness = assess_gap_closure_readiness(resolved_root, evidence_dir)
    checks.extend(
        [
            _pass_fail(
                check_id="EVIDENCE-TEMPLATE-COVERAGE",
                passed=template.artifact_count == ledger.artifact_count
                and ledger.artifact_count >= 20,
                summary="Validation evidence ledger covers every Phase 11 evidence-template artifact.",
                evidence=[
                    f"template_artifacts={template.artifact_count}",
                    f"ledger_artifacts={ledger.artifact_count}",
                ],
            ),
            _pass_fail(
                check_id="EVIDENCE-GAP-MAPPING-COVERAGE",
                passed=readiness.gap_count >= 20
                and all(status.expected_artifact_ids for status in readiness.gap_statuses),
                summary="Evidence ledger maps expected artifacts back to production gap IDs.",
                evidence=[f"gap_count={readiness.gap_count}"],
            ),
            _pass_fail(
                check_id="EVIDENCE-NO-CONTENT-INSPECTION",
                passed=all(
                    not artifact.content_inspected and not artifact.raw_content_included
                    for artifact in ledger.artifacts
                ),
                summary="Evidence ledger does not include raw artifact contents or content inspection output.",
                evidence=["raw_content_included=false for all artifacts"],
            ),
        ]
    )

    release_result = verify_release_controls(resolved_root)
    checks.append(
        _pass_fail(
            check_id="EVIDENCE-RELEASE-VERIFY-COMMIT-READY",
            passed=release_result.ready_for_commit and release_result.failed_count == 0,
            summary="Phase 9 release-control verifier remains commit-ready.",
            evidence=[
                f"passed={release_result.passed_count}",
                f"failed={release_result.failed_count}",
            ],
        )
    )
    hardening_result = verify_local_hardening(resolved_root)
    checks.append(
        _pass_fail(
            check_id="EVIDENCE-HARDENING-VERIFY-COMMIT-READY",
            passed=hardening_result.ready_for_commit and hardening_result.failed_count == 0,
            summary="Phase 10 hardening verifier remains commit-ready.",
            evidence=[
                f"passed={hardening_result.passed_count}",
                f"failed={hardening_result.failed_count}",
            ],
        )
    )
    handoff_result = verify_handoff_readiness(resolved_root)
    checks.append(
        _pass_fail(
            check_id="EVIDENCE-HANDOFF-VERIFY-CODEX-READY",
            passed=handoff_result.ready_for_commit
            and handoff_result.ready_for_codex
            and handoff_result.failed_count == 0,
            summary="Phase 11 handoff verifier remains Codex-ready.",
            evidence=[
                f"passed={handoff_result.passed_count}",
                f"failed={handoff_result.failed_count}",
            ],
        )
    )

    checks.append(
        _deferred(
            check_id="EVIDENCE-EXTERNAL-ARTIFACTS-STILL-OPEN",
            summary="Evidence ledger is ready, but external validation artifacts and human review are still open.",
            deferred_reason="ChatGPT Project Mode cannot produce hosted CI logs, clean install proof, scanner sandbox evidence, live provider telemetry, real MCP/browser runtime logs, report-quality approvals, branch-protection settings, signing/provenance, or publishing dry-run evidence.",
            future_validation_required="Execute Phase 11 handoff tasks, store produced artifacts under validation_evidence/, run Phase 12 ledger commands, and perform human release/AppSec review before closing gaps.",
            future_environment_required="Codex/local/CI/human production-validation environment with approved private evidence storage and release authority.",
        )
    )

    passed_count = sum(1 for check in checks if check.status == "pass")
    failed_count = sum(1 for check in checks if check.status == "fail")
    deferred_count = sum(1 for check in checks if check.status == "deferred")
    required_commit_failures = sum(
        1 for check in checks if check.required_for_commit and check.status == "fail"
    )
    required_codex_failures = sum(
        1 for check in checks if check.required_for_codex and check.status == "fail"
    )
    required_production_open_items = sum(
        1
        for check in checks
        if check.required_for_production and check.status in {"fail", "deferred"}
    )
    return ValidationEvidenceVerificationResult(
        repository_root=str(resolved_root),
        evidence_directory=ledger.evidence_directory,
        checks=checks,
        passed_count=passed_count,
        failed_count=failed_count,
        deferred_count=deferred_count,
        required_commit_failures=required_commit_failures,
        required_codex_failures=required_codex_failures,
        required_production_open_items=required_production_open_items,
        ready_for_commit=required_commit_failures == 0,
        ready_for_codex=required_codex_failures == 0,
        notes=[
            "Phase 12 verification is local-only and non-networked.",
            "ready_for_codex may be true while ready_for_gap_closure and ready_for_production remain false because external evidence and human review are still missing.",
            "No hosted CI, clean install, live provider, real MCP/browser, active validation, or report submission was executed by this verifier.",
        ],
    )
