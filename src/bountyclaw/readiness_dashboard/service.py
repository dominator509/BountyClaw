"""Phase 18 readiness dashboard and external executor index services.

This subsystem is metadata-only. It joins the local verifiers produced in Phases
9 through 17 into a single external-executor dashboard. It does not execute
hosted CI, package builds, scanners, model providers, MCP/browser runtimes,
active validation, report submission, or production gap closure.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from bountyclaw.closure_gate import verify_closure_gate_readiness
from bountyclaw.evidence_review import verify_evidence_review_readiness
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
from bountyclaw.validation_evidence import verify_validation_evidence_readiness
from bountyclaw.validation_runbook import verify_validation_runbook_readiness

from .models import (
    DashboardSubsystemStatus,
    ExternalExecutorCommand,
    ExternalExecutorIndex,
    ReadinessDashboard,
    ReadinessDashboardCheck,
    ReadinessDashboardExportResult,
    ReadinessDashboardVerificationResult,
)

MANDATORY_PHASE_18_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_17_SUBROADMAP.md",
    "PHASE_18_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
    "MARKDOWN_REVIEW_PHASE18.md",
)

MANDATORY_PHASE_18_SUPPORT_FILES: tuple[str, ...] = (
    "README.md",
    "RELEASE.md",
    "ROLLBACK.md",
    "SECURITY_VALIDATION.md",
    "scripts/phase18_verify.py",
    "src/bountyclaw/readiness_dashboard/models.py",
    "src/bountyclaw/readiness_dashboard/service.py",
    "tests/test_readiness_dashboard_phase18.py",
)

EXPECTED_PHASE_18_GAP_IDS: tuple[str, ...] = ("PGT-118", "PGT-119", "PGT-120")


def _resolve_root(root: Path) -> Path:
    return root.expanduser().resolve(strict=False)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _production_readiness_percent(root: Path) -> int:
    text = _read_text(root / "PRODUCTION_GAP_TRACKER.md")
    match = re.search(r"# Current Production Readiness %\s*\n\s*(\d+)%", text)
    return int(match.group(1)) if match else 0


def _completed_phase_count(root: Path) -> int:
    text = _read_text(root / "PRODUCTION_GAP_TRACKER.md")
    return len(re.findall(r"^- Phase \d+:", text, flags=re.MULTILINE))


def _incomplete_phase_count(root: Path) -> int:
    text = _read_text(root / "PRODUCTION_GAP_TRACKER.md")
    incomplete_section = re.search(
        r"# Current Incomplete Phases\s*(.*?)# Deferred Production Tasks",
        text,
        flags=re.DOTALL,
    )
    if not incomplete_section:
        return 0
    return len(re.findall(r"^- ", incomplete_section.group(1), flags=re.MULTILINE))


def _roadmap_position(root: Path) -> str:
    text = _read_text(root / "ROADMAP.md")
    match = re.search(r"- Current roadmap position:\s*(.+)", text)
    return match.group(1).strip() if match else "UNKNOWN"


def _count(value: Any, attr: str) -> int:
    raw = getattr(value, attr, 0)
    return int(raw) if isinstance(raw, int) else 0


def _bool_attr(value: Any, attr: str, default: bool = False) -> bool:
    raw = getattr(value, attr, default)
    return bool(raw)


def _subsystem(
    *,
    subsystem_id: str,
    kind: str,
    source_phase: str,
    title: str,
    verify_command: str,
    verifier_result: Any,
) -> DashboardSubsystemStatus:
    ready_for_commit = _bool_attr(verifier_result, "ready_for_commit")
    ready_for_codex = _bool_attr(verifier_result, "ready_for_codex", ready_for_commit)
    return DashboardSubsystemStatus(
        subsystem_id=subsystem_id,
        kind=kind,  # type: ignore[arg-type]
        source_phase=source_phase,
        title=title,
        verify_command=verify_command,
        ready_for_commit=ready_for_commit,
        ready_for_codex=ready_for_codex,
        ready_for_production=False,
        passed_count=_count(verifier_result, "passed_count"),
        failed_count=_count(verifier_result, "failed_count"),
        deferred_count=_count(verifier_result, "deferred_count"),
        production_open_items=_count(verifier_result, "required_production_open_items"),
        notes=list(getattr(verifier_result, "notes", []) or []),
    )


def _external_commands(root: Path) -> list[ExternalExecutorCommand]:
    backlog = build_codex_gap_backlog(root)
    high_priority_gap_ids = [item.gap_id for item in backlog.items[:12]]
    return [
        ExternalExecutorCommand(
            command_id="P18-EXEC-001",
            order=1,
            title="Export source validation baseline",
            command="PYTHONPATH=src python -m bountyclaw validation-baseline export --root . --output validation_baseline --json",
            purpose="Bind future external validation evidence to an exact hash-only source snapshot.",
            output_path="validation_baseline/",
            related_phases=["16", "18"],
            related_gap_ids=["PGT-112", "PGT-113", "PGT-114"],
            required_environment="Codex/local/CI repository checkout with Python 3.12+.",
            expected_artifact_kind="Hash-only baseline package.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-002",
            order=2,
            title="Export external validation handoff package",
            command="PYTHONPATH=src python -m bountyclaw handoff export --root . --output validation_handoff --json",
            purpose="Prepare Codex/local/CI/human validation task contracts and expected evidence artifacts.",
            output_path="validation_handoff/",
            related_phases=["11", "18"],
            related_gap_ids=["PGT-097", "PGT-105"],
            required_environment="Codex/local/CI repository checkout with Python 3.12+.",
            expected_artifact_kind="Handoff plan and command package.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-003",
            order=3,
            title="Export validation runbook package",
            command="PYTHONPATH=src python -m bountyclaw validation-runbook export --root . --output validation_runbook_package --json",
            purpose="Create the metadata-only execution runbook and journal template for future external validation.",
            output_path="validation_runbook_package/",
            related_phases=["15", "18"],
            related_gap_ids=["PGT-109", "PGT-110", "PGT-111"],
            required_environment="Codex/local/CI/human validation environment.",
            expected_artifact_kind="Runbook and execution journal template.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-004",
            order=4,
            title="Export validation evidence ledger",
            command="PYTHONPATH=src python -m bountyclaw validation-evidence export-ledger --root . --output validation_evidence_ledger --json",
            purpose="Hash and inventory future external-validation artifacts without inspecting raw evidence contents.",
            output_path="validation_evidence_ledger/",
            related_phases=["12", "18"],
            related_gap_ids=["PGT-100", "PGT-101", "PGT-102"],
            required_environment="Codex/local/CI workspace after validation artifacts are produced under validation_evidence/.",
            expected_artifact_kind="Hash-only evidence ledger.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-005",
            order=5,
            title="Export human evidence-review package",
            command="PYTHONPATH=src python -m bountyclaw evidence-review export-package --root . --output evidence_review_package --json",
            purpose="Prepare and assess metadata-only human evidence-review decisions.",
            output_path="evidence_review_package/",
            related_phases=["13", "18"],
            related_gap_ids=["PGT-103", "PGT-104"],
            required_environment="Human AppSec/release review environment with private access to redacted artifacts.",
            expected_artifact_kind="Evidence-review template/status package.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-006",
            order=6,
            title="Export gap tracker backlog package",
            command="PYTHONPATH=src python -m bountyclaw gap-tracker export --root . --output gap_tracker_package --json",
            purpose="Rebuild Codex/local/CI/human backlog from unresolved production gaps after evidence review.",
            output_path="gap_tracker_package/",
            related_phases=["14", "18"],
            related_gap_ids=high_priority_gap_ids,
            required_environment="Codex/local/CI/human governance workspace.",
            expected_artifact_kind="Gap audit and Codex backlog package.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-007",
            order=7,
            title="Export closure gate package",
            command="PYTHONPATH=src python -m bountyclaw closure-gate export --root . --output closure_gate_package --json",
            purpose="Assess baseline-bound readiness attestations and produce manual gap-update candidates only.",
            output_path="closure_gate_package/",
            related_phases=["17", "18"],
            related_gap_ids=["PGT-115", "PGT-116", "PGT-117"],
            required_environment="Human AppSec/release governance environment after evidence review and run journal metadata exist.",
            expected_artifact_kind="Closure-gate status and readiness-attestation template.",
        ),
        ExternalExecutorCommand(
            command_id="P18-EXEC-008",
            order=8,
            title="Export readiness dashboard package",
            command="PYTHONPATH=src python -m bountyclaw readiness-dashboard export --root . --output readiness_dashboard_package --json",
            purpose="Generate the consolidated external-executor dashboard and status index.",
            output_path="readiness_dashboard_package/",
            related_phases=["18"],
            related_gap_ids=["PGT-118", "PGT-119", "PGT-120"],
            required_environment="Codex/local/CI governance workspace.",
            expected_artifact_kind="Dashboard JSON, Markdown summary, and external executor index.",
        ),
    ]


def build_external_executor_index(root: Path) -> ExternalExecutorIndex:
    """Build an ordered external-executor command index without running it."""

    resolved_root = _resolve_root(root)
    commands = _external_commands(resolved_root)
    return ExternalExecutorIndex(
        repository_root=str(resolved_root),
        command_count=len(commands),
        commands=commands,
        ready_for_external_executor=bool(commands),
        notes=[
            "The index is a command plan only; commands must be run in a future authorized external environment.",
            "No command in the index closes gaps or changes production readiness by itself.",
        ],
    )


def build_readiness_dashboard(root: Path) -> ReadinessDashboard:
    """Build the consolidated local readiness dashboard."""

    resolved_root = _resolve_root(root)
    release = verify_release_controls(resolved_root)
    hardening = verify_local_hardening(resolved_root)
    handoff = verify_handoff_readiness(resolved_root)
    validation_evidence = verify_validation_evidence_readiness(resolved_root)
    evidence_review = verify_evidence_review_readiness(resolved_root)
    gap_tracker = verify_gap_tracker_governance(resolved_root)
    validation_runbook = verify_validation_runbook_readiness(resolved_root)
    validation_baseline = verify_validation_baseline_readiness(resolved_root)
    closure_gate = verify_closure_gate_readiness(resolved_root)
    audit = audit_gap_tracker(resolved_root)
    backlog = build_codex_gap_backlog(resolved_root)

    subsystem_statuses = [
        _subsystem(
            subsystem_id="release-controls",
            kind="release",
            source_phase="9",
            title="Release controls and packaging definitions",
            verify_command="PYTHONPATH=src python -m bountyclaw release verify --root . --json",
            verifier_result=release,
        ),
        _subsystem(
            subsystem_id="hardening-controls",
            kind="hardening",
            source_phase="10",
            title="Local hardening and external validation plan",
            verify_command="PYTHONPATH=src python -m bountyclaw hardening verify --root . --json",
            verifier_result=hardening,
        ),
        _subsystem(
            subsystem_id="external-handoff",
            kind="handoff",
            source_phase="11",
            title="External validation handoff package",
            verify_command="PYTHONPATH=src python -m bountyclaw handoff verify --root . --json",
            verifier_result=handoff,
        ),
        _subsystem(
            subsystem_id="validation-evidence-ledger",
            kind="validation_evidence",
            source_phase="12",
            title="Validation evidence ledger",
            verify_command="PYTHONPATH=src python -m bountyclaw validation-evidence verify --root . --json",
            verifier_result=validation_evidence,
        ),
        _subsystem(
            subsystem_id="evidence-review-workflow",
            kind="evidence_review",
            source_phase="13",
            title="Human evidence review workflow",
            verify_command="PYTHONPATH=src python -m bountyclaw evidence-review verify --root . --json",
            verifier_result=evidence_review,
        ),
        _subsystem(
            subsystem_id="gap-tracker-governance",
            kind="gap_tracker",
            source_phase="14",
            title="Gap tracker audit and Codex backlog",
            verify_command="PYTHONPATH=src python -m bountyclaw gap-tracker verify --root . --json",
            verifier_result=gap_tracker,
        ),
        _subsystem(
            subsystem_id="validation-runbook",
            kind="validation_runbook",
            source_phase="15",
            title="External validation runbook and execution journal",
            verify_command="PYTHONPATH=src python -m bountyclaw validation-runbook verify --root . --json",
            verifier_result=validation_runbook,
        ),
        _subsystem(
            subsystem_id="validation-baseline",
            kind="validation_baseline",
            source_phase="16",
            title="Validation baseline source snapshot binding",
            verify_command="PYTHONPATH=src python -m bountyclaw validation-baseline verify --root . --json",
            verifier_result=validation_baseline,
        ),
        _subsystem(
            subsystem_id="closure-gate",
            kind="closure_gate",
            source_phase="17",
            title="Closure gate and readiness attestation governance",
            verify_command="PYTHONPATH=src python -m bountyclaw closure-gate verify --root . --json",
            verifier_result=closure_gate,
        ),
    ]
    commands = _external_commands(resolved_root)
    ready_for_commit = all(status.ready_for_commit for status in subsystem_statuses)
    ready_for_codex = (
        all(status.ready_for_codex for status in subsystem_statuses) and backlog.ready_for_codex
    )
    return ReadinessDashboard(
        repository_root=str(resolved_root),
        roadmap_position=_roadmap_position(resolved_root),
        production_readiness_percent=_production_readiness_percent(resolved_root),
        completed_phase_count=_completed_phase_count(resolved_root),
        incomplete_phase_count=_incomplete_phase_count(resolved_root),
        gap_entry_count=audit.entry_count,
        high_risk_gap_count=backlog.high_risk_count,
        medium_risk_gap_count=backlog.medium_risk_count,
        low_risk_gap_count=backlog.low_risk_count,
        unknown_risk_gap_count=backlog.unknown_risk_count,
        subsystem_statuses=subsystem_statuses,
        external_executor_commands=commands,
        ready_for_commit=ready_for_commit,
        ready_for_codex=ready_for_codex,
        ready_for_external_executor=ready_for_commit and ready_for_codex and bool(commands),
        notes=[
            "Phase 18 dashboard is metadata-only and consolidates existing local governance verifiers.",
            "Production readiness remains a governance estimate and is not raised by dashboard generation.",
            "External validation, evidence review, gap closure, and readiness recalculation remain future human/Codex/CI work.",
        ],
    )


def _dashboard_markdown(dashboard: ReadinessDashboard) -> str:
    lines = [
        "# Phase 18 Readiness Dashboard",
        "",
        f"- Production readiness estimate: {dashboard.production_readiness_percent}%",
        f"- Roadmap position: {dashboard.roadmap_position}",
        f"- Gap entries: {dashboard.gap_entry_count}",
        f"- Ready for commit: {dashboard.ready_for_commit}",
        f"- Ready for Codex/external executor: {dashboard.ready_for_external_executor}",
        f"- Ready for production: {dashboard.ready_for_production}",
        "",
        "## Governance Subsystems",
        "",
    ]
    for status in dashboard.subsystem_statuses:
        lines.extend(
            [
                f"### {status.subsystem_id}",
                "",
                f"- Phase: {status.source_phase}",
                f"- Verify command: `{status.verify_command}`",
                f"- Ready for commit: {status.ready_for_commit}",
                f"- Ready for Codex: {status.ready_for_codex}",
                f"- Ready for production: {status.ready_for_production}",
                f"- Passed/failed/deferred: {status.passed_count}/{status.failed_count}/{status.deferred_count}",
                "",
            ]
        )
    lines.extend(
        [
            "## External Executor Command Index",
            "",
        ]
    )
    for command in dashboard.external_executor_commands:
        lines.extend(
            [
                f"### {command.command_id}: {command.title}",
                "",
                f"- Command: `{command.command}`",
                f"- Purpose: {command.purpose}",
                f"- Output path: `{command.output_path}`",
                f"- Required environment: {command.required_environment}",
                f"- Closes gaps: {command.closes_gaps}",
                f"- Changes production readiness: {command.changes_production_readiness}",
                "",
            ]
        )
    lines.append(
        "This dashboard does not inspect raw evidence, execute validation, close gaps, or prove production readiness."
    )
    return "\n".join(lines)


def _index_markdown(index: ExternalExecutorIndex) -> str:
    lines = [
        "# Phase 18 External Executor Index",
        "",
        "Run these commands in order only in an authorized Codex/local/CI/human validation environment.",
        "",
    ]
    for command in index.commands:
        lines.extend(
            [
                f"## {command.order}. {command.command_id}: {command.title}",
                "",
                f"`{command.command}`",
                "",
                f"Purpose: {command.purpose}",
                f"Expected artifact kind: {command.expected_artifact_kind}",
                f"Related gaps: {', '.join(command.related_gap_ids) if command.related_gap_ids else 'none'}",
                "",
            ]
        )
    lines.append("No index command automatically closes gaps or changes readiness.")
    return "\n".join(lines)


def _commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 18 Readiness Dashboard Commands",
            "",
            "Run these commands after Phase 17 closure-gate tooling is present and before handing off to external validation executors.",
            "",
            "- `python -m bountyclaw readiness-dashboard build --root . --json`",
            "- `python -m bountyclaw readiness-dashboard handoff-index --root . --json`",
            "- `python -m bountyclaw readiness-dashboard export --root . --output readiness_dashboard_package --json`",
            "- `python -m bountyclaw readiness-dashboard verify --root . --json`",
            "- `python scripts/phase18_verify.py --root . --json`",
            "",
            "These commands consolidate local governance metadata. They do not inspect raw evidence, execute external validation, close gaps, alter production readiness, or prove production readiness.",
        ]
    )


def export_readiness_dashboard_package(
    root: Path, output_dir: Path
) -> ReadinessDashboardExportResult:
    """Export the Phase 18 dashboard package."""

    resolved_output = output_dir.expanduser().resolve(strict=False)
    resolved_output.mkdir(parents=True, exist_ok=True)
    dashboard = build_readiness_dashboard(root)
    index = build_external_executor_index(root)
    baseline = build_validation_baseline_manifest(root)
    files = {
        "readiness_dashboard.json": dashboard.model_dump_json(indent=2),
        "external_executor_index.json": index.model_dump_json(indent=2),
        "READINESS_DASHBOARD.md": _dashboard_markdown(dashboard),
        "EXTERNAL_EXECUTOR_INDEX.md": _index_markdown(index),
        "READINESS_DASHBOARD_COMMANDS.md": _commands_markdown(),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))
    index_payload = {
        "phase": "18",
        "source_phase": "17",
        "baseline_id": baseline.baseline_id,
        "production_readiness_percent": dashboard.production_readiness_percent,
        "subsystem_count": len(dashboard.subsystem_statuses),
        "command_count": index.command_count,
        "gap_entry_count": dashboard.gap_entry_count,
        "ready_for_commit": dashboard.ready_for_commit,
        "ready_for_codex": dashboard.ready_for_codex,
        "ready_for_external_executor": dashboard.ready_for_external_executor,
        "ready_for_gap_closure": False,
        "ready_for_production": False,
        "network_used": False,
        "external_actions_executed": False,
        "raw_evidence_contents_included": False,
        "raw_source_contents_included": False,
        "written_files": written_files,
    }
    index_path = resolved_output / "readiness_dashboard_index.json"
    index_path.write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(index_path))
    return ReadinessDashboardExportResult(
        output_directory=str(resolved_output),
        written_files=written_files,
        baseline_id=baseline.baseline_id,
        production_readiness_percent=dashboard.production_readiness_percent,
        subsystem_count=len(dashboard.subsystem_statuses),
        command_count=index.command_count,
        gap_entry_count=dashboard.gap_entry_count,
        ready_for_commit=dashboard.ready_for_commit,
        ready_for_codex=dashboard.ready_for_codex,
        ready_for_external_executor=dashboard.ready_for_external_executor,
        notes=[
            "Dashboard export is local-only and metadata-only.",
            "Exported files do not prove external validation, close production gaps, or raise readiness.",
        ],
    )


def _pass_fail(
    *,
    check_id: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> ReadinessDashboardCheck:
    return ReadinessDashboardCheck(
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
) -> ReadinessDashboardCheck:
    return ReadinessDashboardCheck(
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


def verify_readiness_dashboard(root: Path) -> ReadinessDashboardVerificationResult:
    """Verify Phase 18 dashboard readiness without external execution."""

    resolved_root = _resolve_root(root)
    dashboard = build_readiness_dashboard(resolved_root)
    baseline = build_validation_baseline_manifest(resolved_root)
    checks: list[ReadinessDashboardCheck] = []

    for filename in MANDATORY_PHASE_18_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"DASHBOARD-GOV-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 18 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_18_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"DASHBOARD-SUPPORT-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 18 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    roadmap = _read_text(resolved_root / "ROADMAP.md")
    gaps = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    pyproject = _read_text(resolved_root / "pyproject.toml")
    handoff_service = _read_text(resolved_root / "src" / "bountyclaw" / "handoff" / "service.py")

    checks.extend(
        [
            _pass_fail(
                check_id="DASHBOARD-GOV-ARCH-PHASE18",
                passed="Phase 18" in architecture and "Readiness Dashboard" in architecture,
                summary="ARCHITECTURE.md records Phase 18 readiness-dashboard subsystem.",
                evidence=["Phase 18 architecture marker found"]
                if "Phase 18" in architecture
                else [],
            ),
            _pass_fail(
                check_id="DASHBOARD-GOV-ROADMAP-PHASE18",
                passed="Phase 18" in roadmap
                and "Readiness Dashboard" in roadmap
                and "Completed" in roadmap,
                summary="ROADMAP.md records Phase 18 completion and remaining external validation.",
                evidence=["Phase 18 roadmap marker found"] if "Phase 18" in roadmap else [],
            ),
            _pass_fail(
                check_id="DASHBOARD-GOV-GAPS-PHASE18",
                passed=all(gap_id in gaps for gap_id in EXPECTED_PHASE_18_GAP_IDS),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 18 dashboard/handoff gaps.",
                evidence=list(EXPECTED_PHASE_18_GAP_IDS) if gaps else [],
            ),
            _pass_fail(
                check_id="DASHBOARD-CI-PHASE18-VERIFY-DEFINED",
                passed="python scripts/phase18_verify.py --root ." in workflow,
                summary="CI definition includes Phase 18 readiness-dashboard verification script.",
                evidence=["python scripts/phase18_verify.py --root ."]
                if "phase18_verify.py" in workflow
                else [],
            ),
            _pass_fail(
                check_id="DASHBOARD-PKG-VERSION-CURRENT",
                passed=(
                    ('version = "0.18.0"' in pyproject and 'phase = "18"' in pyproject)
                    or ('version = "0.19.0"' in pyproject and 'phase = "19"' in pyproject)
                ),
                summary="pyproject.toml records Phase 18 non-production version and phase metadata.",
                evidence=["version=0.19.0", "tool.bountyclaw.phase=19"]
                if "0.19.0" in pyproject
                else ["version=0.18.0", "tool.bountyclaw.phase=18"]
                if "0.18.0" in pyproject
                else [],
            ),
            _pass_fail(
                check_id="DASHBOARD-HANDOFF-COMMANDS-DEFINED",
                passed="READINESS_DASHBOARD_COMMANDS.md" in handoff_service,
                summary="Phase 11 handoff export includes Phase 18 readiness-dashboard commands.",
                evidence=["READINESS_DASHBOARD_COMMANDS.md"]
                if "READINESS_DASHBOARD_COMMANDS.md" in handoff_service
                else [],
            ),
            _pass_fail(
                check_id="DASHBOARD-SUBSYSTEMS-COMMIT-READY",
                passed=all(status.ready_for_commit for status in dashboard.subsystem_statuses),
                summary="All consolidated governance subsystems remain commit-ready.",
                evidence=[
                    status.subsystem_id
                    for status in dashboard.subsystem_statuses
                    if status.ready_for_commit
                ],
            ),
            _pass_fail(
                check_id="DASHBOARD-NO-AUTO-CLOSURE",
                passed=not dashboard.ready_for_gap_closure and not dashboard.ready_for_production,
                summary="Readiness dashboard cannot close gaps or mark production ready.",
                evidence=["ready_for_gap_closure=false", "ready_for_production=false"],
            ),
            _pass_fail(
                check_id="DASHBOARD-NO-RAW-CONTENT",
                passed=not dashboard.raw_evidence_contents_included
                and not dashboard.raw_source_contents_included,
                summary="Readiness dashboard does not include raw evidence or source contents.",
                evidence=[
                    "raw_evidence_contents_included=false",
                    "raw_source_contents_included=false",
                ],
            ),
            _pass_fail(
                check_id="DASHBOARD-EXTERNAL-INDEX-AVAILABLE",
                passed=len(dashboard.external_executor_commands) >= 8,
                summary="Dashboard includes ordered external-executor command index.",
                evidence=[command.command_id for command in dashboard.external_executor_commands],
            ),
            _deferred(
                check_id="DASHBOARD-EXTERNAL-VALIDATION-STILL-DEFERRED",
                summary="External production validation still requires real Codex/local/CI/human execution.",
                deferred_reason="ChatGPT Project Mode cannot execute hosted CI, external scanners, clean package installs, live provider validation, real MCP/browser runtimes, branch protection, signing, publishing, or human evidence review.",
                future_validation_required="Run Phase 11 through Phase 18 handoff commands in an authorized external environment and attach reviewed evidence before manual gap closure.",
                future_environment_required="Codex/local/CI/human AppSec/release environment with private evidence storage and repository-host controls.",
            ),
        ]
    )

    passed = sum(1 for check in checks if check.status == "pass")
    failed = sum(1 for check in checks if check.status == "fail")
    deferred = sum(1 for check in checks if check.status == "deferred")
    commit_failures = sum(
        1 for check in checks if check.status == "fail" and check.required_for_commit
    )
    codex_failures = sum(
        1 for check in checks if check.status == "fail" and check.required_for_codex
    )
    production_open = sum(
        1 for check in checks if check.status != "pass" and check.required_for_production
    )
    return ReadinessDashboardVerificationResult(
        repository_root=str(resolved_root),
        baseline_id=baseline.baseline_id,
        checks=checks,
        passed_count=passed,
        failed_count=failed,
        deferred_count=deferred,
        required_commit_failures=commit_failures,
        required_codex_failures=codex_failures,
        required_production_open_items=production_open,
        ready_for_commit=commit_failures == 0,
        ready_for_codex=codex_failures == 0 and dashboard.ready_for_codex,
        ready_for_external_executor=codex_failures == 0 and dashboard.ready_for_external_executor,
        notes=[
            "Phase 18 readiness dashboard verification is local-only and metadata-only.",
            "The verifier intentionally remains not production-ready until real external validation, evidence review, and manual gap closure occur.",
        ],
    )
