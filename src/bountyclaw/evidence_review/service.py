"""Evidence review and gap-closure proposal services for Phase 13.

These services are local-only and metadata-only. They produce review templates,
join human review decisions with the Phase 12 hash-only evidence ledger, and
prepare gap-closure proposals for future human release/AppSec review. They do
not inspect raw evidence contents, close gaps, update production readiness,
execute external validation, contact networks, or submit reports.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from pydantic import ValidationError

from bountyclaw.handoff import verify_handoff_readiness
from bountyclaw.hardening import verify_local_hardening
from bountyclaw.release import verify_release_controls
from bountyclaw.validation_evidence import (
    assess_gap_closure_readiness,
    build_validation_evidence_ledger,
    verify_validation_evidence_readiness,
)

from .models import (
    EvidenceClosureProposalStatus,
    EvidenceReviewArtifactStatus,
    EvidenceReviewCheck,
    EvidenceReviewDecisionFile,
    EvidenceReviewExportResult,
    EvidenceReviewRecord,
    EvidenceReviewStatusResult,
    EvidenceReviewTemplateResult,
    EvidenceReviewVerificationResult,
    GapClosureProposal,
    GapClosureProposalResult,
)

MANDATORY_PHASE_13_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_12_SUBROADMAP.md",
    "PHASE_13_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
)

MANDATORY_PHASE_13_SUPPORT_FILES: tuple[str, ...] = (
    "RELEASE.md",
    "ROLLBACK.md",
    "SECURITY_VALIDATION.md",
    "MARKDOWN_REVIEW_PHASE13.md",
    "scripts/phase9_verify.py",
    "scripts/phase10_verify.py",
    "scripts/phase11_verify.py",
    "scripts/phase12_verify.py",
    "scripts/phase13_verify.py",
)

EXPECTED_PHASE_13_GAP_IDS: tuple[str, ...] = ("PGT-103", "PGT-104", "PGT-105")
DEFAULT_REVIEW_FILENAME = "evidence_review_decisions.json"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _resolve_root(root: Path) -> Path:
    return root.expanduser().resolve(strict=False)


def _resolve_path(root: Path, value: Path) -> Path:
    expanded = value.expanduser()
    if expanded.is_absolute():
        return expanded.resolve(strict=False)
    return (root / expanded).resolve(strict=False)


def default_review_file(root: Path, evidence_dir: Path) -> Path:
    resolved_root = _resolve_root(root)
    return _resolve_path(resolved_root, evidence_dir) / DEFAULT_REVIEW_FILENAME


def _pass_fail(
    *,
    check_id: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> EvidenceReviewCheck:
    return EvidenceReviewCheck(
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
) -> EvidenceReviewCheck:
    return EvidenceReviewCheck(
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


def _load_review_decision_file(review_file: Path) -> EvidenceReviewDecisionFile:
    if not review_file.exists():
        return EvidenceReviewDecisionFile(
            notes=[
                "Review decision file is absent; all artifacts remain pending human review.",
                f"Expected future review file path: {review_file}",
            ]
        )
    try:
        payload = json.loads(review_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Review decision file is not valid JSON: {review_file}") from exc
    try:
        parsed = EvidenceReviewDecisionFile.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Review decision file failed schema validation: {exc}") from exc
    if parsed.raw_evidence_contents_included:
        raise ValueError("Review decision file must not include raw evidence contents")
    return parsed


def build_evidence_review_template(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
    review_file: Path | None = None,
) -> EvidenceReviewTemplateResult:
    """Create a metadata-only template for future human evidence review."""

    resolved_root = _resolve_root(root)
    resolved_evidence_dir = _resolve_path(resolved_root, evidence_dir)
    resolved_review_file = review_file or (resolved_evidence_dir / DEFAULT_REVIEW_FILENAME)
    if not resolved_review_file.is_absolute():
        resolved_review_file = _resolve_path(resolved_root, resolved_review_file)

    ledger = build_validation_evidence_ledger(resolved_root, resolved_evidence_dir)
    decisions = [
        EvidenceReviewRecord(
            artifact_id=artifact.artifact_id,
            decision="pending",
            artifact_sha256=artifact.sha256,
            rationale="PENDING: future human release/AppSec reviewer must inspect the private/redacted artifact and record a decision.",
            redacted_artifact_path=artifact.expected_path,
            sensitive_handling_notes=artifact.sensitive_handling,
        )
        for artifact in ledger.artifacts
    ]
    return EvidenceReviewTemplateResult(
        repository_root=str(resolved_root),
        evidence_directory=str(resolved_evidence_dir),
        review_file=str(resolved_review_file),
        decisions=decisions,
        decision_count=len(decisions),
        ready_for_human_review=ledger.present_count > 0,
        notes=[
            "Evidence review templates are metadata-only and do not include raw evidence contents.",
            "Future reviewers must store private raw artifacts outside source control and commit only reviewed/redacted metadata when appropriate.",
            "This template does not close gaps or change production readiness.",
        ],
    )


def assess_evidence_review_status(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
    review_file: Path | None = None,
) -> EvidenceReviewStatusResult:
    """Join Phase 12 evidence artifact metadata with optional human review decisions."""

    resolved_root = _resolve_root(root)
    resolved_evidence_dir = _resolve_path(resolved_root, evidence_dir)
    resolved_review_file = review_file or (resolved_evidence_dir / DEFAULT_REVIEW_FILENAME)
    if not resolved_review_file.is_absolute():
        resolved_review_file = _resolve_path(resolved_root, resolved_review_file)

    ledger = build_validation_evidence_ledger(resolved_root, resolved_evidence_dir)
    decision_file = _load_review_decision_file(resolved_review_file)
    decisions_by_artifact = {record.artifact_id: record for record in decision_file.decisions}

    statuses: list[EvidenceReviewArtifactStatus] = []
    for artifact in ledger.artifacts:
        record = decisions_by_artifact.get(artifact.artifact_id)
        decision = record.decision if record is not None else "pending"
        blockers: list[str] = []
        if artifact.status != "present":
            blockers.append("evidence artifact is missing")
        if record is None:
            blockers.append("human review decision is missing")
        elif decision == "pending":
            blockers.append("human review decision is pending")
        elif decision == "rejected_sensitive":
            blockers.append("human reviewer rejected artifact as sensitive")
        elif decision == "needs_remediation":
            blockers.append("human reviewer requested remediation")
        sha_matches = bool(
            artifact.sha256
            and record is not None
            and record.artifact_sha256
            and record.artifact_sha256 == artifact.sha256
        )
        if record is not None and decision == "approved_redacted" and not sha_matches:
            blockers.append("reviewed artifact hash does not match ledger hash")
        if record is not None and decision == "approved_redacted":
            if not record.reviewer:
                blockers.append("approved review is missing reviewer identity")
            if not record.reviewed_at_utc:
                blockers.append("approved review is missing reviewed_at_utc")
            if not record.rationale or len(record.rationale.strip()) < 12:
                blockers.append("approved review rationale is missing or too short")

        accepted = (
            artifact.status == "present"
            and decision == "approved_redacted"
            and sha_matches
            and not blockers
        )
        statuses.append(
            EvidenceReviewArtifactStatus(
                artifact_id=artifact.artifact_id,
                filename=artifact.filename,
                validates_gap_ids=artifact.validates_gap_ids,
                evidence_status=artifact.status,
                ledger_sha256=artifact.sha256,
                ledger_byte_count=artifact.byte_count,
                review_decision=decision,
                reviewer=record.reviewer if record else None,
                reviewed_at_utc=record.reviewed_at_utc if record else None,
                reviewed_sha256=record.artifact_sha256 if record else None,
                sha256_matches_ledger=sha_matches,
                accepted_for_closure_proposal=accepted,
                blockers=blockers,
            )
        )

    present_count = sum(1 for artifact in statuses if artifact.evidence_status == "present")
    missing_count = sum(1 for artifact in statuses if artifact.evidence_status == "missing")
    reviewed_count = sum(1 for artifact in statuses if artifact.review_decision != "pending")
    approved_count = sum(
        1 for artifact in statuses if artifact.review_decision == "approved_redacted"
    )
    rejected_count = sum(
        1 for artifact in statuses if artifact.review_decision == "rejected_sensitive"
    )
    needs_remediation_count = sum(
        1 for artifact in statuses if artifact.review_decision == "needs_remediation"
    )
    accepted_count = sum(1 for artifact in statuses if artifact.accepted_for_closure_proposal)

    return EvidenceReviewStatusResult(
        repository_root=str(resolved_root),
        evidence_directory=str(resolved_evidence_dir),
        review_file=str(resolved_review_file),
        artifacts=statuses,
        artifact_count=len(statuses),
        present_count=present_count,
        missing_count=missing_count,
        reviewed_count=reviewed_count,
        approved_count=approved_count,
        rejected_count=rejected_count,
        needs_remediation_count=needs_remediation_count,
        accepted_for_closure_proposal_count=accepted_count,
        ready_for_human_gap_update=accepted_count > 0
        and missing_count == 0
        and rejected_count == 0
        and needs_remediation_count == 0,
        notes=[
            "Evidence review status is derived from metadata and hashes only.",
            "Approved reviewed artifacts may feed human gap-tracker update proposals but cannot close gaps automatically.",
            "ready_for_gap_closure remains false because a human must update governance files explicitly.",
        ],
    )


def build_gap_closure_proposals(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
    review_file: Path | None = None,
) -> GapClosureProposalResult:
    """Create human-actionable gap closure proposals from reviewed evidence metadata."""

    status = assess_evidence_review_status(root, evidence_dir, review_file)
    expected_by_gap: dict[str, list[str]] = defaultdict(list)
    approved_by_gap: dict[str, list[str]] = defaultdict(list)
    missing_by_gap: dict[str, list[str]] = defaultdict(list)
    unreviewed_by_gap: dict[str, list[str]] = defaultdict(list)
    rejected_by_gap: dict[str, list[str]] = defaultdict(list)
    remediation_by_gap: dict[str, list[str]] = defaultdict(list)

    for artifact in status.artifacts:
        for gap_id in artifact.validates_gap_ids:
            expected_by_gap[gap_id].append(artifact.artifact_id)
            if artifact.evidence_status == "missing":
                missing_by_gap[gap_id].append(artifact.artifact_id)
            elif (
                artifact.review_decision == "approved_redacted"
                and artifact.accepted_for_closure_proposal
            ):
                approved_by_gap[gap_id].append(artifact.artifact_id)
            elif artifact.review_decision == "rejected_sensitive":
                rejected_by_gap[gap_id].append(artifact.artifact_id)
            elif artifact.review_decision == "needs_remediation":
                remediation_by_gap[gap_id].append(artifact.artifact_id)
            else:
                unreviewed_by_gap[gap_id].append(artifact.artifact_id)

    proposals: list[GapClosureProposal] = []
    for gap_id in sorted(expected_by_gap):
        expected = sorted(expected_by_gap[gap_id])
        missing = sorted(missing_by_gap.get(gap_id, []))
        rejected = sorted(rejected_by_gap.get(gap_id, []))
        remediation = sorted(remediation_by_gap.get(gap_id, []))
        unreviewed = sorted(unreviewed_by_gap.get(gap_id, []))
        approved = sorted(approved_by_gap.get(gap_id, []))
        proposal_status: EvidenceClosureProposalStatus
        if missing:
            proposal_status = "blocked_missing_artifacts"
        elif rejected:
            proposal_status = "blocked_rejected_artifacts"
        elif remediation or unreviewed or len(approved) < len(expected):
            proposal_status = "blocked_unreviewed_artifacts"
        else:
            proposal_status = "ready_for_human_gap_tracker_update"
        ready_for_update = proposal_status == "ready_for_human_gap_tracker_update"
        proposals.append(
            GapClosureProposal(
                gap_id=gap_id,
                expected_artifact_ids=expected,
                approved_artifact_ids=approved,
                missing_artifact_ids=missing,
                unreviewed_artifact_ids=unreviewed,
                rejected_artifact_ids=rejected,
                needs_remediation_artifact_ids=remediation,
                proposal_status=proposal_status,
                ready_for_human_gap_tracker_update=ready_for_update,
                required_manual_updates=[
                    "Review private evidence contents and redacted artifacts outside this CLI.",
                    "Update PRODUCTION_GAP_TRACKER.md with exact evidence references and closure rationale.",
                    "Update SECURITY_VALIDATION.md, RELEASE.md, and ROLLBACK.md where applicable.",
                    "Recalculate production readiness only after human approval and governance-file updates.",
                ],
                rollback_considerations=(
                    "If reviewed evidence is later invalidated, reopen the associated gap, revert readiness changes, "
                    "and preserve the last safe ChatGPT/Codex-ready bundle as rollback baseline."
                ),
            )
        )

    ready_count = sum(1 for proposal in proposals if proposal.ready_for_human_gap_tracker_update)
    return GapClosureProposalResult(
        repository_root=status.repository_root,
        evidence_directory=status.evidence_directory,
        review_file=status.review_file,
        proposals=proposals,
        proposal_count=len(proposals),
        proposals_ready_for_human_update=ready_count,
        proposals_blocked=len(proposals) - ready_count,
        notes=[
            "Gap closure proposals are advisory and require human release/AppSec action.",
            "This command never edits PRODUCTION_GAP_TRACKER.md and never changes production readiness.",
            "Hash matching only proves that a reviewed metadata record references the same artifact hashed by the Phase 12 ledger; it does not prove evidence quality by itself.",
        ],
    )


def _review_markdown(
    status: EvidenceReviewStatusResult, proposals: GapClosureProposalResult
) -> str:
    lines = [
        "# BountyClaw Evidence Review Package",
        "",
        "This package is metadata-only. It does not include raw evidence contents and does not close gaps automatically.",
        "",
        f"- Artifact count: {status.artifact_count}",
        f"- Present artifacts: {status.present_count}",
        f"- Approved review records: {status.approved_count}",
        f"- Gap proposals ready for human update: {proposals.proposals_ready_for_human_update}",
        f"- Ready for gap closure: {proposals.ready_for_gap_closure}",
        f"- Ready for production: {proposals.ready_for_production}",
        "",
        "## Required Manual Rules",
        "",
        "- Review raw/private evidence only in approved private evidence storage.",
        "- Commit only redacted metadata and reviewed summaries where policy permits.",
        "- Do not close any gap from hashes alone.",
        "- Do not recalculate production readiness until governance files are updated with reviewed evidence.",
        "",
        "## Gap Closure Proposals",
        "",
    ]
    for proposal in proposals.proposals:
        lines.extend(
            [
                f"### {proposal.gap_id}",
                "",
                f"- Status: {proposal.proposal_status}",
                f"- Approved artifacts: {', '.join(proposal.approved_artifact_ids) or 'none'}",
                f"- Missing artifacts: {', '.join(proposal.missing_artifact_ids) or 'none'}",
                f"- Unreviewed artifacts: {', '.join(proposal.unreviewed_artifact_ids) or 'none'}",
                f"- Rejected artifacts: {', '.join(proposal.rejected_artifact_ids) or 'none'}",
                f"- Auto-close allowed: {proposal.auto_close_allowed}",
                "",
            ]
        )
    return "\n".join(lines)


def _review_decision_template_markdown(template: EvidenceReviewTemplateResult) -> str:
    return "\n".join(
        [
            "# Evidence Review Decision Template",
            "",
            "Create the JSON file named below only after a human release/AppSec reviewer privately reviews the matching redacted evidence artifacts.",
            "",
            f"- Review file: `{template.review_file}`",
            f"- Decision count: {template.decision_count}",
            "",
            "Each approved decision must include:",
            "",
            "- `decision`: `approved_redacted`",
            "- `reviewer`: human reviewer identity",
            "- `reviewed_at_utc`: ISO-like UTC timestamp",
            "- `artifact_sha256`: exact SHA-256 from the Phase 12 ledger",
            "- `rationale`: concise approval rationale",
            "- `raw_content_included`: `false`",
            "",
            "Rejected or remediation-needed artifacts must remain blocked until corrected and re-reviewed.",
        ]
    )


def export_evidence_review_package(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
    review_file: Path | None = None,
    output_dir: Path = Path(".bountyclaw/evidence-review"),
) -> EvidenceReviewExportResult:
    """Export a metadata-only evidence review package."""

    resolved_root = _resolve_root(root)
    resolved_output = _resolve_path(resolved_root, output_dir)
    resolved_output.mkdir(parents=True, exist_ok=True)
    template = build_evidence_review_template(resolved_root, evidence_dir, review_file)
    status = assess_evidence_review_status(resolved_root, evidence_dir, review_file)
    proposals = build_gap_closure_proposals(resolved_root, evidence_dir, review_file)

    files: dict[str, str] = {
        "evidence_review_template.json": json.dumps(
            template.model_dump(mode="json"), indent=2, sort_keys=True
        ),
        "evidence_review_status.json": json.dumps(
            status.model_dump(mode="json"), indent=2, sort_keys=True
        ),
        "gap_closure_proposals.json": json.dumps(
            proposals.model_dump(mode="json"), indent=2, sort_keys=True
        ),
        "EVIDENCE_REVIEW_PACKAGE.md": _review_markdown(status, proposals),
        "REVIEW_DECISION_TEMPLATE.md": _review_decision_template_markdown(template),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))

    manifest = {
        "phase": "13",
        "artifact_count": status.artifact_count,
        "proposal_count": proposals.proposal_count,
        "proposals_ready_for_human_update": proposals.proposals_ready_for_human_update,
        "ready_for_gap_closure": False,
        "ready_for_production": False,
        "raw_evidence_contents_included": False,
        "written_files": written_files,
    }
    manifest_path = resolved_output / "evidence_review_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(manifest_path))

    return EvidenceReviewExportResult(
        output_directory=str(resolved_output),
        written_files=written_files,
        artifact_count=status.artifact_count,
        proposal_count=proposals.proposal_count,
        proposals_ready_for_human_update=proposals.proposals_ready_for_human_update,
        notes=[
            "Evidence review export is local-only and metadata-only.",
            "Exported files do not include raw evidence contents and do not close production gaps.",
        ],
    )


def verify_evidence_review_readiness(
    root: Path,
    evidence_dir: Path = Path("validation_evidence"),
    review_file: Path | None = None,
) -> EvidenceReviewVerificationResult:
    """Verify Phase 13 evidence-review workflow readiness without closing gaps."""

    resolved_root = _resolve_root(root)
    resolved_evidence_dir = _resolve_path(resolved_root, evidence_dir)
    resolved_review_file = review_file or (resolved_evidence_dir / DEFAULT_REVIEW_FILENAME)
    if not resolved_review_file.is_absolute():
        resolved_review_file = _resolve_path(resolved_root, resolved_review_file)
    checks: list[EvidenceReviewCheck] = []

    for filename in MANDATORY_PHASE_13_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"EVREVIEW-GOV-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 13 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_13_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"EVREVIEW-SUPPORT-{filename}",
                passed=path.exists(),
                summary=f"Phase 13 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    roadmap = _read_text(resolved_root / "ROADMAP.md")
    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    agents = _read_text(resolved_root / "AGENTS.md")
    gaps = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    phase13 = _read_text(resolved_root / "PHASE_13_SUBROADMAP.md")
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    checks.extend(
        [
            _pass_fail(
                check_id="EVREVIEW-GOV-ROADMAP-PHASE13",
                passed="Phase 13" in roadmap and "Evidence Review" in roadmap,
                summary="ROADMAP.md records Phase 13 evidence review and closure-governance workflow.",
                evidence=["Phase 13 roadmap marker found"] if "Phase 13" in roadmap else [],
            ),
            _pass_fail(
                check_id="EVREVIEW-GOV-ARCH-PHASE13",
                passed="Phase 13" in architecture and "Evidence Review" in architecture,
                summary="ARCHITECTURE.md records Phase 13 evidence review subsystem.",
                evidence=["Phase 13 architecture marker found"]
                if "Phase 13" in architecture
                else [],
            ),
            _pass_fail(
                check_id="EVREVIEW-GOV-AGENTS-PHASE13",
                passed="Evidence Review" in agents and "gap closure" in agents.lower(),
                summary="AGENTS.md records evidence review/gap-closure governance role.",
                evidence=["AGENTS.md evidence review marker found"] if agents else [],
            ),
            _pass_fail(
                check_id="EVREVIEW-GOV-GAPS-PHASE13",
                passed=all(gap_id in gaps for gap_id in EXPECTED_PHASE_13_GAP_IDS),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 13 evidence review gaps.",
                evidence=list(EXPECTED_PHASE_13_GAP_IDS) if gaps else [],
            ),
            _pass_fail(
                check_id="EVREVIEW-GOV-PHASE13-COMPLETE",
                passed="Completed in ChatGPT Project Mode" in phase13,
                summary="PHASE_13_SUBROADMAP.md records local completion status.",
                evidence=["PHASE_13_SUBROADMAP.md completion marker found"] if phase13 else [],
            ),
            _pass_fail(
                check_id="EVREVIEW-CI-PHASE13-VERIFY-DEFINED",
                passed="python scripts/phase13_verify.py --root ." in workflow,
                summary="CI definition includes Phase 13 evidence-review verification script.",
                evidence=["python scripts/phase13_verify.py --root ."]
                if "phase13_verify.py" in workflow
                else [],
            ),
        ]
    )

    ledger = build_validation_evidence_ledger(resolved_root, resolved_evidence_dir)
    readiness = assess_gap_closure_readiness(resolved_root, resolved_evidence_dir)
    template = build_evidence_review_template(
        resolved_root, resolved_evidence_dir, resolved_review_file
    )
    status = assess_evidence_review_status(
        resolved_root, resolved_evidence_dir, resolved_review_file
    )
    proposals = build_gap_closure_proposals(
        resolved_root, resolved_evidence_dir, resolved_review_file
    )
    checks.extend(
        [
            _pass_fail(
                check_id="EVREVIEW-TEMPLATE-COVERAGE",
                passed=template.decision_count == ledger.artifact_count
                and template.decision_count >= 20,
                summary="Evidence review template covers every Phase 12 ledger artifact.",
                evidence=[
                    f"template_decisions={template.decision_count}",
                    f"ledger_artifacts={ledger.artifact_count}",
                ],
            ),
            _pass_fail(
                check_id="EVREVIEW-STATUS-NO-RAW-CONTENT",
                passed=all(
                    not item.raw_content_included and not item.artifact_content_inspected_by_tooling
                    for item in status.artifacts
                ),
                summary="Evidence review status includes no raw artifact contents and no content-inspection output.",
                evidence=["raw_evidence_contents_included=false"],
            ),
            _pass_fail(
                check_id="EVREVIEW-GAP-PROPOSAL-COVERAGE",
                passed=proposals.proposal_count == readiness.gap_count
                and proposals.proposal_count >= 20,
                summary="Gap closure proposals cover every Phase 12 gap-readiness entry.",
                evidence=[
                    f"proposal_count={proposals.proposal_count}",
                    f"gap_count={readiness.gap_count}",
                ],
            ),
            _pass_fail(
                check_id="EVREVIEW-NO-AUTO-CLOSURE",
                passed=not proposals.ready_for_gap_closure
                and not proposals.ready_for_production
                and all(not proposal.auto_close_allowed for proposal in proposals.proposals),
                summary="Evidence review tooling cannot automatically close gaps or raise production readiness.",
                evidence=["ready_for_gap_closure=false", "ready_for_production=false"],
            ),
        ]
    )

    release_result = verify_release_controls(resolved_root)
    checks.append(
        _pass_fail(
            check_id="EVREVIEW-RELEASE-VERIFY-COMMIT-READY",
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
            check_id="EVREVIEW-HARDENING-VERIFY-COMMIT-READY",
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
            check_id="EVREVIEW-HANDOFF-VERIFY-CODEX-READY",
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
    evidence_result = verify_validation_evidence_readiness(resolved_root, resolved_evidence_dir)
    checks.append(
        _pass_fail(
            check_id="EVREVIEW-VALIDATION-EVIDENCE-VERIFY-CODEX-READY",
            passed=evidence_result.ready_for_commit
            and evidence_result.ready_for_codex
            and evidence_result.failed_count == 0,
            summary="Phase 12 validation-evidence verifier remains Codex-ready.",
            evidence=[
                f"passed={evidence_result.passed_count}",
                f"failed={evidence_result.failed_count}",
            ],
        )
    )

    checks.append(
        _deferred(
            check_id="EVREVIEW-HUMAN-REVIEW-STILL-OPEN",
            summary="Evidence review workflow is ready, but real artifacts and human review decisions are still open.",
            deferred_reason="ChatGPT Project Mode cannot produce or privately inspect external validation artifacts, perform human AppSec review, or approve production gap closure.",
            future_validation_required="Execute external validation, store reviewed/redacted artifacts, create evidence review decisions, generate closure proposals, then manually update governance files with approved evidence.",
            future_environment_required="Codex/local/CI/human production-validation environment with private evidence storage and human release/AppSec authority.",
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
    return EvidenceReviewVerificationResult(
        repository_root=str(resolved_root),
        evidence_directory=str(resolved_evidence_dir),
        review_file=str(resolved_review_file),
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
            "Phase 13 verification is local-only and metadata-only.",
            "ready_for_codex may be true while ready_for_gap_closure and ready_for_production remain false because reviewed external evidence and manual governance updates are still missing.",
            "No hosted CI, clean install, live provider, real MCP/browser, active validation, report submission, or gap closure was executed by this verifier.",
        ],
    )
