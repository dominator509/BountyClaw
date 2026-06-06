"""Phase 17 closure-gate and readiness-attestation services.

The closure-gate subsystem is local-only and metadata-only. It binds future
human readiness attestations to the Phase 16 validation baseline, Phase 15
execution journal metadata, Phase 12 evidence ledger metadata, Phase 13 review
metadata, and Phase 14 gap tracker structure. It never reads raw evidence
contents, closes gaps, changes production readiness, or executes external
validation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import ValidationError

from bountyclaw.evidence_review import (
    assess_evidence_review_status,
    verify_evidence_review_readiness,
)
from bountyclaw.gap_tracker import (
    audit_gap_tracker,
    build_codex_gap_backlog,
    verify_gap_tracker_governance,
)
from bountyclaw.handoff import verify_handoff_readiness
from bountyclaw.hardening import verify_local_hardening
from bountyclaw.release import verify_release_controls
from bountyclaw.validation_baseline import (
    build_validation_baseline_manifest,
    verify_validation_baseline_readiness,
)
from bountyclaw.validation_evidence import (
    build_validation_evidence_ledger,
    verify_validation_evidence_readiness,
)
from bountyclaw.validation_runbook import (
    assess_run_journal_status,
    verify_validation_runbook_readiness,
)

from .models import (
    ClosureGateAttestationStatus,
    ClosureGateCheck,
    ClosureGateExportResult,
    ClosureGateStatusResult,
    ClosureGateVerificationResult,
    ReadinessAttestationFile,
    ReadinessAttestationRecord,
    ReadinessAttestationTemplateResult,
)

DEFAULT_EVIDENCE_DIR = Path("validation_evidence")
DEFAULT_ATTESTATION_FILE = Path("validation_evidence/readiness_attestations.json")
DEFAULT_JOURNAL_FILE = Path("validation_runs/execution_journal.json")

MANDATORY_PHASE_17_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_16_SUBROADMAP.md",
    "PHASE_17_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
    "MARKDOWN_REVIEW_PHASE17.md",
)

MANDATORY_PHASE_17_SUPPORT_FILES: tuple[str, ...] = (
    "README.md",
    "RELEASE.md",
    "ROLLBACK.md",
    "SECURITY_VALIDATION.md",
    "scripts/phase9_verify.py",
    "scripts/phase10_verify.py",
    "scripts/phase11_verify.py",
    "scripts/phase12_verify.py",
    "scripts/phase13_verify.py",
    "scripts/phase14_verify.py",
    "scripts/phase15_verify.py",
    "scripts/phase16_verify.py",
    "scripts/phase17_verify.py",
)

EXPECTED_PHASE_17_GAP_IDS: tuple[str, ...] = ("PGT-115", "PGT-116", "PGT-117")
HASH_LENGTH = 64


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _resolve_root(root: Path) -> Path:
    return root.expanduser().resolve(strict=False)


def _resolve_path(root: Path, value: Path) -> Path:
    expanded = value.expanduser()
    if expanded.is_absolute():
        return expanded.resolve(strict=False)
    return (root / expanded).resolve(strict=False)


def _file_sha256_if_present(path: Path) -> str | None:
    if not path.exists() or not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _pass_fail(
    *,
    check_id: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> ClosureGateCheck:
    return ClosureGateCheck(
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
) -> ClosureGateCheck:
    return ClosureGateCheck(
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


def _load_attestation_file(attestation_file: Path) -> ReadinessAttestationFile:
    if not attestation_file.exists():
        return ReadinessAttestationFile(
            notes=[
                "Readiness attestation file is absent; no human gap-update attestation exists yet.",
                f"Expected future attestation path: {attestation_file}",
            ]
        )
    try:
        payload = json.loads(attestation_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Readiness attestation file is not valid JSON: {attestation_file}"
        ) from exc
    try:
        parsed = ReadinessAttestationFile.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Readiness attestation file failed schema validation: {exc}") from exc
    if parsed.raw_evidence_contents_included or parsed.raw_source_contents_included:
        raise ValueError(
            "Readiness attestation file must not include raw evidence or source contents"
        )
    return parsed


def build_readiness_attestation_template(
    root: Path,
    attestation_file: Path = DEFAULT_ATTESTATION_FILE,
) -> ReadinessAttestationTemplateResult:
    """Build a metadata-only template for future human readiness attestations."""

    resolved_root = _resolve_root(root)
    resolved_attestation_file = _resolve_path(resolved_root, attestation_file)
    baseline = build_validation_baseline_manifest(resolved_root)
    gap_audit = audit_gap_tracker(resolved_root)
    high_risk_gap_ids = [
        entry.gap_id for entry in gap_audit.entries if entry.risk_level in {"critical", "high"}
    ]
    candidate_gap_ids = high_risk_gap_ids[:25]
    record = ReadinessAttestationRecord(
        attestation_id="ATTEST-PENDING-001",
        baseline_id=baseline.baseline_id,
        decision="pending",
        approved_gap_ids=[],
        notes=[
            "Future human release/AppSec reviewer must replace pending fields after private evidence review.",
            "This template must not contain raw evidence, raw source, secrets, exploit payloads, or production data.",
            "Approved attestations support manual governance review only; they do not auto-close gaps.",
        ],
    )
    template = ReadinessAttestationFile(
        attestations=[record],
        notes=[
            "Metadata-only readiness attestation template.",
            "Reviewer must bind any approval to baseline_id, evidence artifact hashes, execution journal hash, and gap tracker hash.",
            "production_readiness_increase_allowed=false and auto_gap_closure_allowed=false are mandatory invariants.",
        ],
    )
    return ReadinessAttestationTemplateResult(
        repository_root=str(resolved_root),
        attestation_file=str(resolved_attestation_file),
        baseline_id=baseline.baseline_id,
        template=template,
        candidate_gap_ids=candidate_gap_ids,
        ready_for_human_attestation=baseline.ready_for_external_validation_reference
        and gap_audit.ready_for_codex_backlog,
        notes=[
            "The attestation template is local-only and metadata-only.",
            "It does not inspect raw evidence, approve gaps, close gaps, or prove production readiness.",
        ],
    )


def _has_valid_hash(value: str | None) -> bool:
    if value is None:
        return False
    return len(value) == HASH_LENGTH and all(
        character in "0123456789abcdef" for character in value.lower()
    )


def _attestation_status(
    *,
    record: ReadinessAttestationRecord,
    current_baseline_id: str,
    known_gap_ids: set[str],
) -> ClosureGateAttestationStatus:
    blockers: list[str] = []
    if record.raw_evidence_contents_included or record.raw_source_contents_included:
        blockers.append("attestation includes raw evidence/source content flags")
    baseline_matches = bool(record.baseline_id and record.baseline_id == current_baseline_id)
    if not baseline_matches:
        blockers.append("attestation baseline_id does not match current Phase 17 source baseline")
    if record.decision != "approved_for_manual_gap_update":
        if record.decision == "pending":
            blockers.append("attestation decision is pending")
        elif record.decision == "rejected":
            blockers.append("attestation decision is rejected")
        elif record.decision == "needs_remediation":
            blockers.append("attestation decision requires remediation")
    if record.decision == "approved_for_manual_gap_update":
        if not record.reviewer:
            blockers.append("approved attestation is missing reviewer identity")
        if not record.reviewed_at_utc:
            blockers.append("approved attestation is missing reviewed_at_utc")
        if not record.rationale or len(record.rationale.strip()) < 20:
            blockers.append("approved attestation rationale is missing or too short")
        if not record.approved_gap_ids:
            blockers.append("approved attestation includes no approved_gap_ids")
        unknown_gap_ids = sorted(set(record.approved_gap_ids) - known_gap_ids)
        if unknown_gap_ids:
            blockers.append(
                "approved_gap_ids include unknown gap IDs: " + ", ".join(unknown_gap_ids)
            )
        if not record.referenced_evidence_artifact_ids:
            blockers.append("approved attestation has no referenced_evidence_artifact_ids")
        if not record.referenced_run_ids:
            blockers.append("approved attestation has no referenced_run_ids")
        if not _has_valid_hash(record.evidence_review_decision_sha256):
            blockers.append(
                "approved attestation has missing or invalid evidence_review_decision_sha256"
            )
        if not _has_valid_hash(record.execution_journal_sha256):
            blockers.append("approved attestation has missing or invalid execution_journal_sha256")
        if not _has_valid_hash(record.gap_tracker_sha256):
            blockers.append("approved attestation has missing or invalid gap_tracker_sha256")
    accepted = record.decision == "approved_for_manual_gap_update" and not blockers
    if accepted:
        status: str = "candidate"
    elif record.decision == "rejected":
        status = "rejected"
    elif record.decision == "needs_remediation":
        status = "needs_remediation"
    elif record.decision == "pending" and blockers == ["attestation decision is pending"]:
        status = "pending"
    else:
        status = "blocked"
    accepted_gap_ids = sorted(set(record.approved_gap_ids) & known_gap_ids) if accepted else []
    return ClosureGateAttestationStatus(
        attestation_id=record.attestation_id,
        decision=record.decision,
        status=status,  # type: ignore[arg-type]
        baseline_id=record.baseline_id,
        baseline_matches_current=baseline_matches,
        approved_gap_ids=record.approved_gap_ids,
        accepted_gap_ids=accepted_gap_ids,
        referenced_evidence_artifact_ids=record.referenced_evidence_artifact_ids,
        referenced_run_ids=record.referenced_run_ids,
        blockers=blockers,
        accepted_for_manual_gap_update_proposal=accepted,
    )


def assess_closure_gate_status(
    root: Path,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
    attestation_file: Path = DEFAULT_ATTESTATION_FILE,
    journal_file: Path = DEFAULT_JOURNAL_FILE,
) -> ClosureGateStatusResult:
    """Assess closure-gate metadata without closing gaps or trusting artifacts."""

    resolved_root = _resolve_root(root)
    resolved_evidence_dir = _resolve_path(resolved_root, evidence_dir)
    resolved_attestation_file = _resolve_path(resolved_root, attestation_file)
    resolved_journal_file = _resolve_path(resolved_root, journal_file)

    baseline = build_validation_baseline_manifest(resolved_root)
    gap_audit = audit_gap_tracker(resolved_root)
    evidence_ledger = build_validation_evidence_ledger(resolved_root, resolved_evidence_dir)
    review_status = assess_evidence_review_status(resolved_root, resolved_evidence_dir)
    journal_status = assess_run_journal_status(resolved_root, resolved_journal_file)
    attestation_file_model = _load_attestation_file(resolved_attestation_file)

    known_gap_ids = {entry.gap_id for entry in gap_audit.entries}
    attestation_statuses = [
        _attestation_status(
            record=record, current_baseline_id=baseline.baseline_id, known_gap_ids=known_gap_ids
        )
        for record in attestation_file_model.attestations
    ]
    accepted = [
        status for status in attestation_statuses if status.accepted_for_manual_gap_update_proposal
    ]
    candidate_gap_ids = sorted(
        {gap_id for status in accepted for gap_id in status.accepted_gap_ids}
    )
    return ClosureGateStatusResult(
        repository_root=str(resolved_root),
        baseline_id=baseline.baseline_id,
        attestation_file=str(resolved_attestation_file),
        attestation_statuses=attestation_statuses,
        attestation_count=len(attestation_statuses),
        accepted_attestation_count=len(accepted),
        candidate_gap_ids=candidate_gap_ids,
        gap_tracker_entry_count=gap_audit.entry_count,
        evidence_artifact_count=evidence_ledger.artifact_count,
        present_evidence_artifact_count=evidence_ledger.present_count,
        accepted_review_artifact_count=review_status.accepted_for_closure_proposal_count,
        journal_steps_with_metadata_count=journal_status.passed_with_metadata_count,
        ready_for_human_gap_update_review=bool(candidate_gap_ids),
        notes=[
            "Closure-gate status is metadata-only and does not inspect raw evidence contents.",
            "Candidate gap IDs require future manual governance-file updates and do not close gaps automatically.",
            "ready_for_gap_closure=false and ready_for_production=false remain invariant in Phase 17.",
        ],
    )


def _closure_gate_markdown(result: ClosureGateStatusResult) -> str:
    lines = [
        "# Phase 17 Closure Gate Status",
        "",
        f"- Baseline ID: `{result.baseline_id}`",
        f"- Attestations: {result.attestation_count}",
        f"- Accepted attestations: {result.accepted_attestation_count}",
        f"- Candidate gaps: {len(result.candidate_gap_ids)}",
        f"- Ready for human gap update review: {str(result.ready_for_human_gap_update_review).lower()}",
        "- Ready for gap closure: false",
        "- Ready for production: false",
        "",
        "## Safety Invariants",
        "",
        "- No raw evidence contents are inspected or exported.",
        "- No gaps are closed automatically.",
        "- Production readiness is not increased by this metadata.",
        "- A human AppSec/release reviewer must manually update governance files after external evidence review.",
        "",
        "## Candidate Gap IDs",
        "",
    ]
    if result.candidate_gap_ids:
        lines.extend(f"- `{gap_id}`" for gap_id in result.candidate_gap_ids)
    else:
        lines.append(
            "No candidate gaps are available because approved baseline-bound attestations are absent."
        )
    return "\n".join(lines)


def _commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 17 Closure Gate Commands",
            "",
            "Run these commands only after Phase 16 baseline export and future external validation evidence/review metadata exist.",
            "",
            "- `python -m bountyclaw closure-gate attestation-template --root . --json`",
            "- Create `validation_evidence/readiness_attestations.json` only after human release/AppSec review of baseline-bound evidence metadata.",
            "- `python -m bountyclaw closure-gate status --root . --evidence-dir validation_evidence --attestation-file validation_evidence/readiness_attestations.json --journal validation_runs/execution_journal.json --json`",
            "- `python -m bountyclaw closure-gate export --root . --output closure_gate_package --json`",
            "- `python -m bountyclaw closure-gate verify --root . --json`",
            "- `python scripts/phase17_verify.py --root . --json`",
            "",
            "These commands do not inspect raw evidence, close gaps, change readiness, execute external validation, or prove production readiness.",
        ]
    )


def export_closure_gate_package(
    root: Path,
    output_dir: Path,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
    attestation_file: Path = DEFAULT_ATTESTATION_FILE,
    journal_file: Path = DEFAULT_JOURNAL_FILE,
) -> ClosureGateExportResult:
    """Export a local Phase 17 closure-gate package."""

    resolved_output = output_dir.expanduser().resolve(strict=False)
    resolved_output.mkdir(parents=True, exist_ok=True)
    template = build_readiness_attestation_template(root, attestation_file)
    status = assess_closure_gate_status(root, evidence_dir, attestation_file, journal_file)
    files = {
        "readiness_attestation_template.json": template.template.model_dump_json(indent=2),
        "closure_gate_status.json": status.model_dump_json(indent=2),
        "CLOSURE_GATE.md": _closure_gate_markdown(status),
        "CLOSURE_GATE_COMMANDS.md": _commands_markdown(),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))
    index_payload = {
        "phase": "17",
        "baseline_id": status.baseline_id,
        "attestation_count": status.attestation_count,
        "candidate_gap_count": len(status.candidate_gap_ids),
        "ready_for_human_gap_update_review": status.ready_for_human_gap_update_review,
        "ready_for_gap_closure": False,
        "ready_for_production": False,
        "network_used": False,
        "external_actions_executed": False,
        "raw_evidence_contents_included": False,
        "raw_source_contents_included": False,
        "written_files": written_files,
    }
    index_path = resolved_output / "closure_gate_index.json"
    index_path.write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(index_path))
    return ClosureGateExportResult(
        output_directory=str(resolved_output),
        baseline_id=status.baseline_id,
        written_files=written_files,
        attestation_count=status.attestation_count,
        candidate_gap_count=len(status.candidate_gap_ids),
        ready_for_human_gap_update_review=status.ready_for_human_gap_update_review,
        notes=[
            "Closure-gate export is local-only and metadata-only.",
            "A candidate gap list is not a gap closure and must be manually reviewed before governance updates.",
        ],
    )


def verify_closure_gate_readiness(
    root: Path,
    evidence_dir: Path = DEFAULT_EVIDENCE_DIR,
    attestation_file: Path = DEFAULT_ATTESTATION_FILE,
    journal_file: Path = DEFAULT_JOURNAL_FILE,
) -> ClosureGateVerificationResult:
    """Verify Phase 17 closure-gate readiness without external execution."""

    resolved_root = _resolve_root(root)
    status = assess_closure_gate_status(resolved_root, evidence_dir, attestation_file, journal_file)
    checks: list[ClosureGateCheck] = []

    for filename in MANDATORY_PHASE_17_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"CLOSURE-GOV-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 17 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_17_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"CLOSURE-SUPPORT-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 17 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    roadmap = _read_text(resolved_root / "ROADMAP.md")
    gap_tracker = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    pyproject = _read_text(resolved_root / "pyproject.toml")
    handoff_service = _read_text(resolved_root / "src" / "bountyclaw" / "handoff" / "service.py")

    checks.extend(
        [
            _pass_fail(
                check_id="CLOSURE-GOV-ARCH-PHASE17",
                passed="Phase 17" in architecture and "Closure Gate" in architecture,
                summary="ARCHITECTURE.md records Phase 17 closure-gate subsystem.",
                evidence=["Phase 17 closure gate architecture marker found"]
                if "Phase 17" in architecture
                else [],
            ),
            _pass_fail(
                check_id="CLOSURE-GOV-ROADMAP-PHASE17",
                passed="Phase 17" in roadmap
                and "Closure Gate" in roadmap
                and "Completed" in roadmap,
                summary="ROADMAP.md records Phase 17 completion and remaining external validation.",
                evidence=["Phase 17 roadmap marker found"] if "Phase 17" in roadmap else [],
            ),
            _pass_fail(
                check_id="CLOSURE-GOV-GAPS-PHASE17",
                passed=all(gap_id in gap_tracker for gap_id in EXPECTED_PHASE_17_GAP_IDS),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 17 closure-gate gaps.",
                evidence=list(EXPECTED_PHASE_17_GAP_IDS) if gap_tracker else [],
            ),
            _pass_fail(
                check_id="CLOSURE-CI-PHASE17-VERIFY-DEFINED",
                passed="python scripts/phase17_verify.py --root ." in workflow,
                summary="CI definition includes Phase 17 closure-gate verification script.",
                evidence=["python scripts/phase17_verify.py --root ."]
                if "phase17_verify.py" in workflow
                else [],
            ),
            _pass_fail(
                check_id="CLOSURE-PKG-VERSION-CURRENT",
                passed=(
                    ('version = "0.17.0"' in pyproject and 'phase = "17"' in pyproject)
                    or ('version = "0.18.0"' in pyproject and 'phase = "18"' in pyproject)
                    or ('version = "0.19.0"' in pyproject and 'phase = "19"' in pyproject)
                ),
                summary="pyproject.toml records current Phase 18 or compatible Phase 17 non-production version and phase metadata.",
                evidence=["version/phase metadata compatible with closure-gate tooling"]
                if ("0.17.0" in pyproject or "0.18.0" in pyproject or "0.19.0" in pyproject)
                else [],
            ),
            _pass_fail(
                check_id="CLOSURE-HANDOFF-COMMANDS-DEFINED",
                passed="CLOSURE_GATE_COMMANDS.md" in handoff_service,
                summary="Phase 11 handoff export includes Phase 17 closure-gate commands.",
                evidence=["CLOSURE_GATE_COMMANDS.md"]
                if "CLOSURE_GATE_COMMANDS.md" in handoff_service
                else [],
            ),
            _pass_fail(
                check_id="CLOSURE-STATUS-NO-RAW-CONTENT",
                passed=not status.raw_evidence_contents_included
                and not status.raw_source_contents_included,
                summary="Closure-gate status does not include raw evidence or raw source contents.",
                evidence=[
                    "raw_evidence_contents_included=false",
                    "raw_source_contents_included=false",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-STATUS-NO-AUTO-CLOSURE",
                passed=not status.ready_for_gap_closure and not status.ready_for_production,
                summary="Closure-gate status cannot close gaps or mark production ready.",
                evidence=["ready_for_gap_closure=false", "ready_for_production=false"],
            ),
        ]
    )

    release_result = verify_release_controls(resolved_root)
    hardening_result = verify_local_hardening(resolved_root)
    handoff_result = verify_handoff_readiness(resolved_root)
    evidence_result = verify_validation_evidence_readiness(
        resolved_root, _resolve_path(resolved_root, evidence_dir)
    )
    review_result = verify_evidence_review_readiness(
        resolved_root, _resolve_path(resolved_root, evidence_dir)
    )
    gap_result = verify_gap_tracker_governance(resolved_root)
    runbook_result = verify_validation_runbook_readiness(
        resolved_root, _resolve_path(resolved_root, journal_file)
    )
    baseline_result = verify_validation_baseline_readiness(resolved_root)
    gap_backlog = build_codex_gap_backlog(resolved_root)
    current_gap_tracker_hash = _file_sha256_if_present(resolved_root / "PRODUCTION_GAP_TRACKER.md")

    checks.extend(
        [
            _pass_fail(
                check_id="CLOSURE-REGRESSION-RELEASE",
                passed=release_result.ready_for_commit,
                summary="Phase 9 release verifier remains commit-ready.",
                evidence=[
                    f"passed={release_result.passed_count}",
                    f"failed={release_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-HARDENING",
                passed=hardening_result.ready_for_commit,
                summary="Phase 10 hardening verifier remains commit-ready.",
                evidence=[
                    f"passed={hardening_result.passed_count}",
                    f"failed={hardening_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-HANDOFF",
                passed=handoff_result.ready_for_commit and handoff_result.ready_for_codex,
                summary="Phase 11 handoff verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={handoff_result.passed_count}",
                    f"failed={handoff_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-EVIDENCE-LEDGER",
                passed=evidence_result.ready_for_commit and evidence_result.ready_for_codex,
                summary="Phase 12 validation-evidence verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={evidence_result.passed_count}",
                    f"failed={evidence_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-EVIDENCE-REVIEW",
                passed=review_result.ready_for_commit and review_result.ready_for_codex,
                summary="Phase 13 evidence-review verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={review_result.passed_count}",
                    f"failed={review_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-GAP-TRACKER",
                passed=gap_result.ready_for_commit
                and gap_result.ready_for_codex
                and gap_backlog.ready_for_codex,
                summary="Phase 14 gap tracker verifier/backlog remain commit-ready and Codex-ready.",
                evidence=[
                    f"passed={gap_result.passed_count}",
                    f"failed={gap_result.failed_count}",
                    f"backlog={gap_backlog.item_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-RUNBOOK",
                passed=runbook_result.ready_for_commit and runbook_result.ready_for_codex,
                summary="Phase 15 validation-runbook verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={runbook_result.passed_count}",
                    f"failed={runbook_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-REGRESSION-BASELINE",
                passed=baseline_result.ready_for_commit and baseline_result.ready_for_codex,
                summary="Phase 16 validation-baseline verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={baseline_result.passed_count}",
                    f"failed={baseline_result.failed_count}",
                    f"baseline_id={baseline_result.baseline_id}",
                ],
            ),
            _pass_fail(
                check_id="CLOSURE-GAP-TRACKER-HASH-AVAILABLE",
                passed=_has_valid_hash(current_gap_tracker_hash),
                summary="Current PRODUCTION_GAP_TRACKER.md has a hash that future attestations can reference.",
                evidence=[f"gap_tracker_sha256={current_gap_tracker_hash}"]
                if current_gap_tracker_hash
                else [],
            ),
        ]
    )

    checks.append(
        _deferred(
            check_id="CLOSURE-EXTERNAL-ATTESTATION-STILL-OPEN",
            summary="Phase 17 closure-gate tooling is ready, but no real external validation attestation has been accepted here.",
            deferred_reason="ChatGPT Project Mode cannot run hosted CI, clean installs, external scanners, sandboxing, live providers, real MCP/browser runtimes, human report review, private evidence review, branch protection, signing, provenance, publishing, or manual governance-file gap closure.",
            future_validation_required="Run external validation, bind artifacts to the Phase 16 baseline ID, complete Phase 12/13/14/15 workflows, create metadata-only readiness attestations, and have a human AppSec/release reviewer manually update gap closures with rollback notes.",
            future_environment_required="Codex/local/CI/human validation environment with approved repository checkout, private evidence storage, release/AppSec review authority, hosted CI, scanners, sandboxing, provider policies, and branch protection controls.",
        )
    )

    passed_count = sum(1 for check in checks if check.status == "pass")
    failed_count = sum(1 for check in checks if check.status == "fail")
    deferred_count = sum(1 for check in checks if check.status == "deferred")
    required_commit_failures = sum(
        1 for check in checks if check.status == "fail" and check.required_for_commit
    )
    required_codex_failures = sum(
        1 for check in checks if check.status == "fail" and check.required_for_codex
    )
    required_production_open_items = sum(
        1
        for check in checks
        if check.required_for_production and check.status in {"fail", "deferred"}
    )
    ready_for_commit = required_commit_failures == 0
    ready_for_codex = ready_for_commit and required_codex_failures == 0
    return ClosureGateVerificationResult(
        repository_root=str(resolved_root),
        baseline_id=status.baseline_id,
        checks=checks,
        passed_count=passed_count,
        failed_count=failed_count,
        deferred_count=deferred_count,
        required_commit_failures=required_commit_failures,
        required_codex_failures=required_codex_failures,
        required_production_open_items=required_production_open_items,
        ready_for_commit=ready_for_commit,
        ready_for_codex=ready_for_codex,
        ready_for_human_gap_update_review=status.ready_for_human_gap_update_review,
        notes=[
            "Phase 17 verification is local-only and metadata-only.",
            "A passing closure-gate verifier means the repository can produce closure-gate templates and status reports for future human review.",
            "It does not mean external validation, human evidence acceptance, production gap closure, or production readiness is complete.",
        ],
    )
