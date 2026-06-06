"""External validation runbook and execution-journal services for Phase 15.

These services are local-only and metadata-only. They convert the Phase 14
Codex gap backlog into a deterministic validation runbook, generate a future
execution journal template, assess optional journal metadata, and export a
handoff package. They never run external commands, inspect raw evidence, close
production gaps, change production readiness, contact targets, call live model
providers, launch MCP/browser runtimes, or submit reports.
"""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from bountyclaw.evidence_review import verify_evidence_review_readiness
from bountyclaw.gap_tracker import build_codex_gap_backlog, verify_gap_tracker_governance
from bountyclaw.handoff import verify_handoff_readiness
from bountyclaw.hardening import verify_local_hardening
from bountyclaw.release import verify_release_controls
from bountyclaw.validation_evidence import verify_validation_evidence_readiness

from .models import (
    ExternalValidationRunbook,
    ExternalValidationRunbookStep,
    RunbookStepStatus,
    ValidationRunbookCheck,
    ValidationRunbookExportResult,
    ValidationRunbookVerificationResult,
    ValidationRunJournalEntry,
    ValidationRunJournalFile,
    ValidationRunJournalStatusResult,
    ValidationRunStepStatus,
)

MANDATORY_PHASE_15_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_14_SUBROADMAP.md",
    "PHASE_15_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
    "MARKDOWN_REVIEW_PHASE15.md",
)

MANDATORY_PHASE_15_SUPPORT_FILES: tuple[str, ...] = (
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
)

EXPECTED_PHASE_15_GAP_IDS: tuple[str, ...] = ("PGT-109", "PGT-110", "PGT-111")
DEFAULT_JOURNAL_FILE = Path("validation_runs/execution_journal.json")
RISK_WEIGHT = {"critical": 0, "high": 1, "medium": 2, "low": 3, "unknown": 4}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _resolve_root(root: Path) -> Path:
    return root.expanduser().resolve(strict=False)


def _resolve_path(root: Path, value: Path) -> Path:
    expanded = value.expanduser()
    if expanded.is_absolute():
        return expanded.resolve(strict=False)
    return (root / expanded).resolve(strict=False)


def default_journal_file(root: Path) -> Path:
    return _resolve_path(_resolve_root(root), DEFAULT_JOURNAL_FILE)


def _pass_fail(
    *,
    check_id: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> ValidationRunbookCheck:
    return ValidationRunbookCheck(
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
) -> ValidationRunbookCheck:
    return ValidationRunbookCheck(
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


def build_external_validation_runbook(root: Path) -> ExternalValidationRunbook:
    """Build a deterministic future execution runbook from the Phase 14 backlog."""

    resolved_root = _resolve_root(root)
    backlog = build_codex_gap_backlog(resolved_root)
    steps: list[ExternalValidationRunbookStep] = []
    sorted_items = sorted(
        backlog.items, key=lambda item: (RISK_WEIGHT[item.risk_level], item.gap_id)
    )
    for index, item in enumerate(sorted_items, start=1):
        steps.append(
            ExternalValidationRunbookStep(
                step_id=f"P15-RUNBOOK-{index:03d}",
                source_backlog_task_id=item.task_id,
                gap_id=item.gap_id,
                priority_rank=index,
                risk_level=item.risk_level,
                phase_association=item.phase_association,
                subsystem_association=item.subsystem_association,
                objective=item.description,
                required_environment=item.exact_future_tooling_environment_required,
                recommended_future_agent_type=item.recommended_future_agent_type,
                prerequisite_summary=item.dependency_requirements,
                command_or_step_summary=item.exact_future_validation_required,
                expected_evidence_summary=(
                    "Future executor must produce redacted/private evidence artifacts, then register "
                    "artifact IDs and SHA-256 hashes in the Phase 15 execution journal."
                ),
                completion_criteria=item.completion_criteria,
                rollback_considerations=item.rollback_considerations,
            )
        )
    high = sum(1 for step in steps if step.risk_level in {"critical", "high"})
    medium = sum(1 for step in steps if step.risk_level == "medium")
    low_unknown = len(steps) - high - medium
    return ExternalValidationRunbook(
        repository_root=str(resolved_root),
        steps=steps,
        step_count=len(steps),
        critical_or_high_count=high,
        medium_count=medium,
        low_or_unknown_count=low_unknown,
        ready_for_codex_execution=backlog.ready_for_codex and bool(steps),
        notes=[
            "Runbook generation is local-only and derived from PRODUCTION_GAP_TRACKER.md.",
            "Runbook steps are future tasks; BountyClaw does not execute external validation in Phase 15.",
            "Journal metadata can support future evidence review but cannot close gaps automatically.",
        ],
    )


def build_run_journal_template(root: Path) -> ValidationRunJournalFile:
    """Build a metadata-only execution journal template for future executors."""

    runbook = build_external_validation_runbook(root)
    entries = [
        ValidationRunJournalEntry(
            run_id=f"RUN-{step.step_id}",
            step_id=step.step_id,
            source_backlog_task_id=step.source_backlog_task_id,
            gap_id=step.gap_id,
            status="planned",
            executor_agent_type=step.recommended_future_agent_type,
            environment=step.required_environment,
            command_summary=step.command_or_step_summary,
            notes=[
                "Future executor must replace planned metadata after running this task outside ChatGPT Project Mode.",
                "Do not paste raw command output, secrets, exploit payloads, or sensitive evidence into this journal.",
            ],
        )
        for step in runbook.steps
    ]
    return ValidationRunJournalFile(
        entries=entries,
        notes=[
            "This template is metadata-only and safe to store in source control only after review.",
            "Passed entries must reference artifact IDs and SHA-256 hashes, not raw evidence contents.",
            "The journal does not close gaps or change production readiness.",
        ],
    )


def _load_journal(journal_file: Path) -> ValidationRunJournalFile:
    if not journal_file.exists():
        return ValidationRunJournalFile(
            notes=[
                "Execution journal file is absent; all runbook steps remain pending external execution.",
                f"Expected future journal path: {journal_file}",
            ]
        )
    try:
        payload = json.loads(journal_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Execution journal file is not valid JSON: {journal_file}") from exc
    try:
        return ValidationRunJournalFile.model_validate(payload)
    except ValidationError as exc:
        raise ValueError(f"Execution journal file failed schema validation: {exc}") from exc


def assess_run_journal_status(
    root: Path,
    journal_file: Path | None = None,
) -> ValidationRunJournalStatusResult:
    """Assess future execution journal metadata without trusting it or closing gaps."""

    resolved_root = _resolve_root(root)
    resolved_journal = _resolve_path(resolved_root, journal_file or DEFAULT_JOURNAL_FILE)
    runbook = build_external_validation_runbook(resolved_root)
    journal = _load_journal(resolved_journal)
    entries_by_step: dict[str, list[ValidationRunJournalEntry]] = {}
    for entry in journal.entries:
        entries_by_step.setdefault(entry.step_id, []).append(entry)

    statuses: list[ValidationRunStepStatus] = []
    for step in runbook.steps:
        entries = entries_by_step.get(step.step_id, [])
        blockers: list[str] = []
        status: RunbookStepStatus = "pending"
        evidence_artifact_ids: list[str] = []
        evidence_sha256: dict[str, str] = {}
        run_ids: list[str] = []
        if not entries:
            blockers.append("no execution journal entry for this runbook step")
        else:
            run_ids = [entry.run_id for entry in entries]
            passed_entries = [entry for entry in entries if entry.status == "passed"]
            failed_or_blocked_entries = [
                entry for entry in entries if entry.status in {"failed", "blocked"}
            ]
            review_entries = [entry for entry in entries if entry.status == "needs_review"]
            if passed_entries:
                status = "passed"
                for entry in passed_entries:
                    evidence_artifact_ids.extend(entry.evidence_artifact_ids)
                    evidence_sha256.update(entry.evidence_sha256)
                    if not entry.executor or not entry.environment or not entry.completed_at_utc:
                        blockers.append(
                            f"passed run {entry.run_id} is missing executor/environment/completion metadata"
                        )
                    if not entry.evidence_artifact_ids:
                        blockers.append(
                            f"passed run {entry.run_id} is missing evidence artifact IDs"
                        )
            elif failed_or_blocked_entries:
                status = "blocked"
                blockers.append("latest available metadata indicates failed or blocked execution")
            elif review_entries:
                status = "needs_review"
                blockers.append(
                    "execution metadata requires human review before evidence ledger use"
                )
            else:
                status = "recorded"
                blockers.append("execution metadata is recorded but not passed")
        accepted_for_ledger = status == "passed" and bool(evidence_artifact_ids) and not blockers
        statuses.append(
            ValidationRunStepStatus(
                step_id=step.step_id,
                source_backlog_task_id=step.source_backlog_task_id,
                gap_id=step.gap_id,
                risk_level=step.risk_level,
                status=status,
                journal_run_ids=run_ids,
                evidence_artifact_ids=sorted(set(evidence_artifact_ids)),
                evidence_sha256=dict(sorted(evidence_sha256.items())),
                accepted_for_evidence_ledger=accepted_for_ledger,
                blockers=blockers,
            )
        )

    passed_with_metadata = sum(1 for item in statuses if item.accepted_for_evidence_ledger)
    failed_or_blocked_count = sum(1 for item in statuses if item.status in {"failed", "blocked"})
    missing = sum(1 for item in statuses if item.status == "pending")
    return ValidationRunJournalStatusResult(
        repository_root=str(resolved_root),
        journal_file=str(resolved_journal),
        step_statuses=statuses,
        step_count=len(statuses),
        passed_with_metadata_count=passed_with_metadata,
        failed_or_blocked_count=failed_or_blocked_count,
        missing_journal_count=missing,
        ready_for_evidence_ledger=passed_with_metadata > 0,
        notes=[
            "Journal status is metadata-only; it does not inspect evidence artifacts or close gaps.",
            "Accepted journal metadata must still be processed by Phase 12 and Phase 13 review workflows.",
            "Production readiness remains false until human-reviewed evidence updates the gap tracker.",
        ],
    )


def _runbook_markdown(runbook: ExternalValidationRunbook) -> str:
    lines = [
        "# Phase 15 External Validation Runbook",
        "",
        f"Repository root: `{runbook.repository_root}`",
        f"Step count: {runbook.step_count}",
        f"Ready for Codex execution: {runbook.ready_for_codex_execution}",
        "Ready for production: false",
        "",
        "This runbook is metadata-only. It does not execute external validation, inspect raw evidence, close gaps, or raise production readiness.",
        "",
        "## Steps",
    ]
    for step in runbook.steps:
        lines.extend(
            [
                "",
                f"### {step.step_id}: {step.gap_id}",
                "",
                f"- Source backlog task: `{step.source_backlog_task_id}`",
                f"- Risk level: {step.risk_level}",
                f"- Subsystem: {step.subsystem_association}",
                f"- Future agent: {step.recommended_future_agent_type}",
                f"- Required environment: {step.required_environment}",
                f"- Objective: {step.objective}",
                f"- Future validation: {step.command_or_step_summary}",
                f"- Completion criteria: {step.completion_criteria}",
                f"- Rollback: {step.rollback_considerations}",
            ]
        )
    return "\n".join(lines)


def _journal_template_markdown() -> str:
    return "\n".join(
        [
            "# Phase 15 Execution Journal Instructions",
            "",
            "1. Export the runbook with `bountyclaw validation-runbook export`.",
            "2. Execute each runbook step only in the required Codex/local/CI/human environment.",
            "3. Record metadata in `validation_runs/execution_journal.json`.",
            "4. Include artifact IDs and SHA-256 hashes only; do not include raw evidence, secrets, logs, exploit payloads, or screenshots.",
            "5. Run `bountyclaw validation-runbook journal-status --root . --journal validation_runs/execution_journal.json --json`.",
            "6. Feed reviewed artifacts into Phase 12 validation-evidence and Phase 13 evidence-review workflows.",
            "7. Re-run Phase 14 gap tracker audit/backlog before any human gap tracker edit.",
            "",
            "Journal metadata does not close gaps and does not raise production readiness.",
        ]
    )


def export_validation_runbook_package(
    root: Path,
    output_dir: Path,
    journal_file: Path | None = None,
) -> ValidationRunbookExportResult:
    """Export the Phase 15 runbook, journal template, status, and commands."""

    resolved_root = _resolve_root(root)
    resolved_output = _resolve_path(resolved_root, output_dir)
    resolved_output.mkdir(parents=True, exist_ok=True)
    runbook = build_external_validation_runbook(resolved_root)
    template = build_run_journal_template(resolved_root)
    status = assess_run_journal_status(resolved_root, journal_file)
    files = {
        "VALIDATION_RUNBOOK.json": runbook.model_dump_json(indent=2),
        "VALIDATION_RUNBOOK.md": _runbook_markdown(runbook),
        "EXECUTION_JOURNAL_TEMPLATE.json": template.model_dump_json(indent=2),
        "EXECUTION_JOURNAL_INSTRUCTIONS.md": _journal_template_markdown(),
        "EXECUTION_JOURNAL_STATUS.json": status.model_dump_json(indent=2),
        "VALIDATION_RUNBOOK_COMMANDS.md": validation_runbook_commands_markdown(),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))
    manifest = {
        "phase": "15",
        "source_phase": "14",
        "step_count": runbook.step_count,
        "ready_for_codex_execution": runbook.ready_for_codex_execution,
        "ready_for_evidence_ledger": status.ready_for_evidence_ledger,
        "ready_for_gap_closure": False,
        "ready_for_production": False,
        "written_files": written_files,
        "network_used": False,
        "external_actions_executed": False,
        "raw_evidence_contents_included": False,
    }
    manifest_path = resolved_output / "validation_runbook_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(manifest_path))
    return ValidationRunbookExportResult(
        output_directory=str(resolved_output),
        written_files=written_files,
        step_count=runbook.step_count,
        ready_for_codex_execution=runbook.ready_for_codex_execution,
        ready_for_evidence_ledger=status.ready_for_evidence_ledger,
        notes=[
            "Validation runbook package is local-only and metadata-only.",
            "Generated files do not prove external validation has executed.",
            "Future journal entries must be human reviewed before any gap closure proposal is considered.",
        ],
    )


def validation_runbook_commands_markdown() -> str:
    """Return handoff-safe Phase 15 runbook command instructions."""

    return "\n".join(
        [
            "# Phase 15 Validation Runbook Commands",
            "",
            "Run these commands after exporting the Phase 14 gap tracker backlog and before executing external validation tasks.",
            "",
            "- `python -m bountyclaw validation-runbook build --root . --json`",
            "- `python -m bountyclaw validation-runbook journal-template --root . --json`",
            "- `python -m bountyclaw validation-runbook export --root . --output validation_runbook --json`",
            "- `python -m bountyclaw validation-runbook journal-status --root . --journal validation_runs/execution_journal.json --json`",
            "- `python -m bountyclaw validation-runbook verify --root . --json`",
            "- `python scripts/phase15_verify.py --root . --json`",
            "",
            "These commands create and assess metadata-only runbook artifacts. They do not execute external validation, inspect raw evidence, close gaps, or prove production readiness.",
        ]
    )


def verify_validation_runbook_readiness(
    root: Path,
    journal_file: Path | None = None,
) -> ValidationRunbookVerificationResult:
    """Verify Phase 15 runbook readiness without executing future validations."""

    resolved_root = _resolve_root(root)
    checks: list[ValidationRunbookCheck] = []
    for filename in MANDATORY_PHASE_15_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"RUNBOOK-GOV-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 15 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_15_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"RUNBOOK-SUPPORT-{filename}",
                passed=path.exists(),
                summary=f"Phase 15 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    roadmap = _read_text(resolved_root / "ROADMAP.md")
    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    gaps = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    checks.extend(
        [
            _pass_fail(
                check_id="RUNBOOK-GOV-ROADMAP-PHASE15",
                passed="Phase 15" in roadmap and "External Validation Runbook" in roadmap,
                summary="ROADMAP.md records Phase 15 validation-runbook completion and remaining external execution.",
                evidence=["Phase 15 roadmap marker found"] if "Phase 15" in roadmap else [],
            ),
            _pass_fail(
                check_id="RUNBOOK-GOV-ARCH-PHASE15",
                passed="Phase 15" in architecture and "Validation Runbook" in architecture,
                summary="ARCHITECTURE.md records Phase 15 runbook subsystem.",
                evidence=["Phase 15 architecture marker found"]
                if "Phase 15" in architecture
                else [],
            ),
            _pass_fail(
                check_id="RUNBOOK-GOV-GAPS-PHASE15",
                passed=all(gap_id in gaps for gap_id in EXPECTED_PHASE_15_GAP_IDS),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 15 runbook gaps.",
                evidence=list(EXPECTED_PHASE_15_GAP_IDS) if gaps else [],
            ),
            _pass_fail(
                check_id="RUNBOOK-CI-PHASE15-VERIFY-DEFINED",
                passed="python scripts/phase15_verify.py --root ." in workflow,
                summary="CI definition includes Phase 15 validation-runbook verification script.",
                evidence=["python scripts/phase15_verify.py --root ."]
                if "phase15_verify.py" in workflow
                else [],
            ),
        ]
    )

    runbook = build_external_validation_runbook(resolved_root)
    checks.append(
        _pass_fail(
            check_id="RUNBOOK-STEPS-COVER-GAP-BACKLOG",
            passed=runbook.step_count > 0 and runbook.ready_for_codex_execution,
            summary="Phase 15 runbook is derived from unresolved Phase 14 Codex gap backlog items.",
            evidence=[f"step_count={runbook.step_count}"],
        )
    )
    checks.append(
        _pass_fail(
            check_id="RUNBOOK-STEPS-NON-CLOSING",
            passed=all(
                not step.auto_gap_closure_allowed
                and not step.production_readiness_increase_allowed
                and not step.raw_evidence_content_allowed
                for step in runbook.steps
            ),
            summary="Runbook steps prohibit raw evidence content, automatic gap closure, and readiness increases.",
            evidence=["all runbook steps non-closing"],
        )
    )
    template = build_run_journal_template(resolved_root)
    checks.append(
        _pass_fail(
            check_id="RUNBOOK-JOURNAL-TEMPLATE-COVERAGE",
            passed=len(template.entries) == runbook.step_count
            and not template.raw_evidence_contents_included,
            summary="Execution journal template covers each runbook step and excludes raw evidence.",
            evidence=[f"template_entries={len(template.entries)}"],
        )
    )
    status = assess_run_journal_status(resolved_root, journal_file)
    checks.append(
        _pass_fail(
            check_id="RUNBOOK-JOURNAL-STATUS-NON-CLOSING",
            passed=not status.ready_for_gap_closure
            and not status.ready_for_production
            and not status.raw_evidence_contents_included,
            summary="Journal status assessment remains non-closing and production-not-ready.",
            evidence=[f"passed_with_metadata={status.passed_with_metadata_count}"],
        )
    )

    release_result = verify_release_controls(resolved_root)
    hardening_result = verify_local_hardening(resolved_root)
    handoff_result = verify_handoff_readiness(resolved_root)
    evidence_result = verify_validation_evidence_readiness(resolved_root)
    review_result = verify_evidence_review_readiness(resolved_root)
    gap_result = verify_gap_tracker_governance(resolved_root)
    checks.extend(
        [
            _pass_fail(
                check_id="RUNBOOK-REGRESSION-RELEASE",
                passed=release_result.ready_for_commit and release_result.failed_count == 0,
                summary="Phase 9 release verifier remains commit-ready.",
                evidence=[
                    f"passed={release_result.passed_count}",
                    f"failed={release_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="RUNBOOK-REGRESSION-HARDENING",
                passed=hardening_result.ready_for_commit and hardening_result.failed_count == 0,
                summary="Phase 10 hardening verifier remains commit-ready.",
                evidence=[
                    f"passed={hardening_result.passed_count}",
                    f"failed={hardening_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="RUNBOOK-REGRESSION-HANDOFF",
                passed=handoff_result.ready_for_commit
                and handoff_result.ready_for_codex
                and handoff_result.failed_count == 0,
                summary="Phase 11 handoff verifier remains Codex-ready.",
                evidence=[
                    f"passed={handoff_result.passed_count}",
                    f"failed={handoff_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="RUNBOOK-REGRESSION-EVIDENCE-LEDGER",
                passed=evidence_result.ready_for_commit
                and evidence_result.ready_for_codex
                and evidence_result.failed_count == 0,
                summary="Phase 12 validation-evidence verifier remains Codex-ready.",
                evidence=[
                    f"passed={evidence_result.passed_count}",
                    f"failed={evidence_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="RUNBOOK-REGRESSION-EVIDENCE-REVIEW",
                passed=review_result.ready_for_commit
                and review_result.ready_for_codex
                and review_result.failed_count == 0,
                summary="Phase 13 evidence-review verifier remains Codex-ready.",
                evidence=[
                    f"passed={review_result.passed_count}",
                    f"failed={review_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="RUNBOOK-REGRESSION-GAP-TRACKER",
                passed=gap_result.ready_for_commit
                and gap_result.ready_for_codex
                and gap_result.failed_count == 0,
                summary="Phase 14 gap tracker verifier remains Codex-ready.",
                evidence=[f"passed={gap_result.passed_count}", f"failed={gap_result.failed_count}"],
            ),
        ]
    )
    checks.append(
        _deferred(
            check_id="RUNBOOK-EXTERNAL-EXECUTION-DEFERRED",
            summary="Real runbook execution remains deferred to Codex/local/CI/human environments.",
            deferred_reason="ChatGPT Project Mode cannot run hosted CI, clean package installs, external scanner/sandbox validation, live providers, real MCP/browser runtimes, or human evidence review.",
            future_validation_required="Execute the Phase 15 runbook externally, record metadata-only journal entries with artifact hashes, then feed artifacts into Phase 12/13/14 workflows.",
            future_environment_required="Codex/local/CI/human environment with repository host, CI runners, scanner/sandbox/model/MCP/browser tools where explicitly authorized, private evidence storage, and AppSec/release review.",
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
        1 for check in checks if check.required_for_production and check.status != "pass"
    )
    return ValidationRunbookVerificationResult(
        repository_root=str(resolved_root),
        checks=checks,
        passed_count=passed_count,
        failed_count=failed_count,
        deferred_count=deferred_count,
        required_commit_failures=required_commit_failures,
        required_codex_failures=required_codex_failures,
        required_production_open_items=required_production_open_items,
        ready_for_commit=required_commit_failures == 0,
        ready_for_codex=required_codex_failures == 0 and runbook.ready_for_codex_execution,
        ready_for_evidence_ledger=status.ready_for_evidence_ledger,
        notes=[
            "Phase 15 verification is local-only and does not execute the runbook.",
            "ready_for_codex=true means future executors have deterministic instructions, not that validation is complete.",
            "ready_for_production remains false until reviewed evidence closes the relevant gaps.",
        ],
    )
