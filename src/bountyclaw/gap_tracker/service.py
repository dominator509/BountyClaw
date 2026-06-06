"""Gap tracker governance and Codex backlog services for Phase 14.

The services in this module are local-only and metadata-only. They parse
PRODUCTION_GAP_TRACKER.md, audit entry shape, and export a deterministic future
executor backlog. They never close production gaps, raise production readiness,
inspect raw external evidence, execute external validation, contact targets, or
submit bounty reports.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from bountyclaw.evidence_review import verify_evidence_review_readiness
from bountyclaw.handoff import verify_handoff_readiness
from bountyclaw.hardening import verify_local_hardening
from bountyclaw.release import verify_release_controls
from bountyclaw.validation_evidence import verify_validation_evidence_readiness

from .models import (
    CodexBacklogItem,
    CodexBacklogResult,
    GapRiskLevel,
    GapTrackerAuditResult,
    GapTrackerCheck,
    GapTrackerEntry,
    GapTrackerExportResult,
    GapTrackerVerificationResult,
)

REQUIRED_GAP_FIELDS: tuple[str, ...] = (
    "Unique ID",
    "Phase association",
    "Subsystem association",
    "Description",
    "Why incomplete",
    "Why blocked in ChatGPT Project Mode",
    "Risk level",
    "Dependency requirements",
    "Exact future validation required",
    "Exact future tooling/environment required",
    "Recommended future agent type",
    "Estimated production impact",
    "Completion criteria",
    "Rollback considerations",
)

FIELD_ATTRIBUTE_MAP: dict[str, str] = {
    "Unique ID": "unique_id",
    "Phase association": "phase_association",
    "Subsystem association": "subsystem_association",
    "Description": "description",
    "Why incomplete": "why_incomplete",
    "Why blocked in ChatGPT Project Mode": "why_blocked_in_chatgpt_project_mode",
    "Risk level": "risk_level",
    "Dependency requirements": "dependency_requirements",
    "Exact future validation required": "exact_future_validation_required",
    "Exact future tooling/environment required": "exact_future_tooling_environment_required",
    "Recommended future agent type": "recommended_future_agent_type",
    "Estimated production impact": "estimated_production_impact",
    "Completion criteria": "completion_criteria",
    "Rollback considerations": "rollback_considerations",
}

MANDATORY_PHASE_14_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_13_SUBROADMAP.md",
    "PHASE_14_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
    "MARKDOWN_REVIEW_PHASE14.md",
)

MANDATORY_PHASE_14_SUPPORT_FILES: tuple[str, ...] = (
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
)

EXPECTED_PHASE_14_GAP_IDS: tuple[str, ...] = ("PGT-106", "PGT-107", "PGT-108")
RISK_SORT_ORDER: dict[GapRiskLevel, int] = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "unknown": 4,
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _normalize_risk(value: str | None) -> GapRiskLevel:
    if not value:
        return "unknown"
    lower = value.strip().lower()
    if lower in {"critical", "high", "medium", "low"}:
        return lower  # type: ignore[return-value]
    return "unknown"


def _current_section(lines: list[str], start_index: int) -> str:
    section = "Unknown"
    for i in range(start_index, -1, -1):
        line = lines[i].strip()
        if line.startswith("# ") or line.startswith("## "):
            section = line.lstrip("#").strip()
            break
    return section


def _parse_gap_block(block_lines: list[str]) -> dict[str, str]:
    fields: dict[str, str] = {}
    current_field: str | None = None
    for line in block_lines:
        stripped = line.strip()
        if stripped.startswith("- ") and ":" in stripped:
            key, value = stripped[2:].split(":", 1)
            key = key.strip()
            if key in REQUIRED_GAP_FIELDS:
                fields[key] = value.strip()
                current_field = key
            else:
                current_field = None
        elif current_field and stripped:
            fields[current_field] = f"{fields[current_field]} {stripped}".strip()
    return fields


def _iter_gap_blocks(lines: list[str]) -> list[tuple[str, int, int, str, list[str]]]:
    headers: list[tuple[int, str]] = []
    for idx, line in enumerate(lines):
        match = re.match(r"^###\s+(PGT-\d+)\s*$", line.strip())
        if match:
            headers.append((idx, match.group(1)))
    blocks: list[tuple[str, int, int, str, list[str]]] = []
    top_level_boundaries = [
        idx
        for idx, line in enumerate(lines)
        if line.startswith("# ") and not re.match(r"^###\s+PGT-\d+\s*$", line.strip())
    ]
    for pos, (start_idx, gap_id) in enumerate(headers):
        next_gap_idx = headers[pos + 1][0] if pos + 1 < len(headers) else len(lines)
        next_section_idx = min(
            (idx for idx in top_level_boundaries if idx > start_idx), default=len(lines)
        )
        end_idx = min(next_gap_idx, next_section_idx)
        section = _current_section(lines, start_idx)
        blocks.append((gap_id, start_idx + 1, end_idx, section, lines[start_idx:end_idx]))
    return blocks


def audit_gap_tracker(root: Path) -> GapTrackerAuditResult:
    """Parse and audit PRODUCTION_GAP_TRACKER.md without mutating it."""

    resolved_root = root.expanduser().resolve(strict=False)
    tracker_path = resolved_root / "PRODUCTION_GAP_TRACKER.md"
    text = _read_text(tracker_path)
    lines = text.splitlines()
    entries: list[GapTrackerEntry] = []
    for gap_id, line_start, line_end, section, block_lines in _iter_gap_blocks(lines):
        parsed = _parse_gap_block(block_lines)
        missing = [field for field in REQUIRED_GAP_FIELDS if not parsed.get(field)]
        entries.append(
            GapTrackerEntry(
                gap_id=gap_id,
                source_section=section,
                line_start=line_start,
                line_end=line_end,
                unique_id=parsed.get("Unique ID"),
                phase_association=parsed.get("Phase association"),
                subsystem_association=parsed.get("Subsystem association"),
                description=parsed.get("Description"),
                why_incomplete=parsed.get("Why incomplete"),
                why_blocked_in_chatgpt_project_mode=parsed.get(
                    "Why blocked in ChatGPT Project Mode"
                ),
                risk_level=_normalize_risk(parsed.get("Risk level")),
                dependency_requirements=parsed.get("Dependency requirements"),
                exact_future_validation_required=parsed.get("Exact future validation required"),
                exact_future_tooling_environment_required=parsed.get(
                    "Exact future tooling/environment required"
                ),
                recommended_future_agent_type=parsed.get("Recommended future agent type"),
                estimated_production_impact=parsed.get("Estimated production impact"),
                completion_criteria=parsed.get("Completion criteria"),
                rollback_considerations=parsed.get("Rollback considerations"),
                missing_required_fields=missing,
                raw_field_count=len(parsed),
            )
        )

    counts = Counter(entry.gap_id for entry in entries)
    duplicate_ids = sorted(gap_id for gap_id, count in counts.items() if count > 1)
    malformed_ids = sorted(
        entry.gap_id
        for entry in entries
        if entry.unique_id is None or entry.unique_id.strip() != entry.gap_id
    )
    entries_with_missing = sorted(
        entry.gap_id for entry in entries if entry.missing_required_fields
    )
    missing_required_count = sum(len(entry.missing_required_fields) for entry in entries)
    return GapTrackerAuditResult(
        repository_root=str(resolved_root),
        gap_tracker_path=str(tracker_path),
        entries=entries,
        entry_count=len(entries),
        duplicate_gap_ids=duplicate_ids,
        missing_required_field_count=missing_required_count,
        entries_with_missing_required_fields=entries_with_missing,
        malformed_entry_ids=malformed_ids,
        ready_for_codex_backlog=bool(entries)
        and not duplicate_ids
        and not malformed_ids
        and missing_required_count == 0,
        notes=[
            "Phase 14 gap tracker audit parses governance metadata only.",
            "The audit does not close production gaps, inspect raw validation evidence, or raise production readiness.",
        ],
    )


def build_codex_gap_backlog(root: Path) -> CodexBacklogResult:
    """Build a deterministic future-executor backlog from unresolved gaps."""

    audit = audit_gap_tracker(root)
    sorted_entries = sorted(
        audit.entries,
        key=lambda entry: (RISK_SORT_ORDER[entry.risk_level], entry.gap_id),
    )
    items: list[CodexBacklogItem] = []
    for rank, entry in enumerate(sorted_entries, start=1):
        codex_ready = not entry.missing_required_fields
        items.append(
            CodexBacklogItem(
                task_id=f"CODEX-{entry.gap_id}",
                gap_id=entry.gap_id,
                priority_rank=rank,
                risk_level=entry.risk_level,
                phase_association=entry.phase_association or "UNKNOWN",
                subsystem_association=entry.subsystem_association or "UNKNOWN",
                description=entry.description or "UNKNOWN",
                blocked_in_chatgpt_project_mode=entry.why_blocked_in_chatgpt_project_mode
                or "UNKNOWN",
                recommended_future_agent_type=entry.recommended_future_agent_type or "UNKNOWN",
                dependency_requirements=entry.dependency_requirements or "UNKNOWN",
                exact_future_validation_required=entry.exact_future_validation_required
                or "UNKNOWN",
                exact_future_tooling_environment_required=entry.exact_future_tooling_environment_required
                or "UNKNOWN",
                estimated_production_impact=entry.estimated_production_impact or "UNKNOWN",
                completion_criteria=entry.completion_criteria or "UNKNOWN",
                rollback_considerations=entry.rollback_considerations or "UNKNOWN",
                codex_ready=codex_ready,
            )
        )
    risk_counts = Counter(item.risk_level for item in items)
    return CodexBacklogResult(
        repository_root=audit.repository_root,
        gap_tracker_path=audit.gap_tracker_path,
        items=items,
        item_count=len(items),
        high_risk_count=risk_counts.get("critical", 0) + risk_counts.get("high", 0),
        medium_risk_count=risk_counts.get("medium", 0),
        low_risk_count=risk_counts.get("low", 0),
        unknown_risk_count=risk_counts.get("unknown", 0),
        ready_for_codex=audit.ready_for_codex_backlog and all(item.codex_ready for item in items),
        notes=[
            "Backlog items are derived from unresolved gap entries and are intended for future Codex/local/CI/human execution.",
            "Backlog export does not execute validation, inspect evidence, close gaps, or raise production readiness.",
        ],
    )


def _backlog_markdown(backlog: CodexBacklogResult) -> str:
    lines = [
        "# BountyClaw Codex Gap Backlog",
        "",
        "Generated by Phase 14 gap tracker governance tooling.",
        "",
        "This file is a deterministic future-executor queue. It does not close production gaps, claim validation evidence, or raise production readiness.",
        "",
        f"- Backlog item count: {backlog.item_count}",
        f"- High/critical risk count: {backlog.high_risk_count}",
        f"- Medium risk count: {backlog.medium_risk_count}",
        f"- Low risk count: {backlog.low_risk_count}",
        f"- Ready for Codex assignment: {str(backlog.ready_for_codex).lower()}",
        "",
    ]
    for item in backlog.items:
        lines.extend(
            [
                f"## {item.task_id}: {item.subsystem_association}",
                "",
                f"- Gap ID: {item.gap_id}",
                f"- Priority rank: {item.priority_rank}",
                f"- Risk level: {item.risk_level}",
                f"- Phase association: {item.phase_association}",
                f"- Recommended future agent type: {item.recommended_future_agent_type}",
                f"- Description: {item.description}",
                f"- Blocked in ChatGPT Project Mode: {item.blocked_in_chatgpt_project_mode}",
                f"- Dependencies: {item.dependency_requirements}",
                f"- Future validation required: {item.exact_future_validation_required}",
                f"- Future tooling/environment required: {item.exact_future_tooling_environment_required}",
                f"- Completion criteria: {item.completion_criteria}",
                f"- Rollback considerations: {item.rollback_considerations}",
                f"- Auto gap closure allowed: {str(item.auto_gap_closure_allowed).lower()}",
                f"- Production readiness increase allowed: {str(item.production_readiness_increase_allowed).lower()}",
                "",
            ]
        )
    return "\n".join(lines).strip() + "\n"


def _audit_markdown(audit: GapTrackerAuditResult) -> str:
    lines = [
        "# Phase 14 Gap Tracker Audit",
        "",
        "This audit is metadata-only and local-only.",
        "",
        f"- Entry count: {audit.entry_count}",
        f"- Duplicate gap IDs: {', '.join(audit.duplicate_gap_ids) if audit.duplicate_gap_ids else 'none'}",
        f"- Malformed entry IDs: {', '.join(audit.malformed_entry_ids) if audit.malformed_entry_ids else 'none'}",
        f"- Missing required field count: {audit.missing_required_field_count}",
        f"- Ready for Codex backlog: {str(audit.ready_for_codex_backlog).lower()}",
        "",
        "No production gaps were closed by this audit.",
        "",
    ]
    return "\n".join(lines)


def export_gap_tracker_package(root: Path, output_dir: Path) -> GapTrackerExportResult:
    """Export local gap tracker audit and Codex backlog artifacts."""

    resolved_root = root.expanduser().resolve(strict=False)
    resolved_output = output_dir.expanduser().resolve(strict=False)
    resolved_output.mkdir(parents=True, exist_ok=True)

    audit = audit_gap_tracker(resolved_root)
    backlog = build_codex_gap_backlog(resolved_root)
    files: dict[str, str] = {
        "GAP_TRACKER_AUDIT.json": json.dumps(
            audit.model_dump(mode="json"), indent=2, sort_keys=True
        ),
        "GAP_TRACKER_AUDIT.md": _audit_markdown(audit),
        "CODEX_GAP_BACKLOG.json": json.dumps(
            backlog.model_dump(mode="json"), indent=2, sort_keys=True
        ),
        "CODEX_GAP_BACKLOG.md": _backlog_markdown(backlog),
        "GAP_TRACKER_COMMANDS.md": "\n".join(
            [
                "# Phase 14 Gap Tracker Commands",
                "",
                "Run these after external validation/evidence-review work changes `PRODUCTION_GAP_TRACKER.md`.",
                "",
                "```bash",
                "PYTHONPATH=src python -m bountyclaw gap-tracker audit --root . --json",
                "PYTHONPATH=src python -m bountyclaw gap-tracker backlog --root . --json",
                "PYTHONPATH=src python -m bountyclaw gap-tracker export --root . --output gap_tracker_package --json",
                "PYTHONPATH=src python -m bountyclaw gap-tracker verify --root . --json",
                "```",
                "",
                "These commands do not close gaps automatically. Human release/AppSec review remains mandatory.",
            ]
        ),
    }
    written: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content, encoding="utf-8")
        written.append(str(path))
    return GapTrackerExportResult(
        output_directory=str(resolved_output),
        written_files=written,
        gap_entry_count=audit.entry_count,
        backlog_item_count=backlog.item_count,
        ready_for_codex=audit.ready_for_codex_backlog and backlog.ready_for_codex,
        notes=[
            "Exported gap tracker audit and Codex backlog are local governance artifacts.",
            "No external validation, evidence inspection, gap closure, or production readiness update was performed.",
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
) -> GapTrackerCheck:
    return GapTrackerCheck(
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
) -> GapTrackerCheck:
    return GapTrackerCheck(
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


def verify_gap_tracker_governance(root: Path) -> GapTrackerVerificationResult:
    """Verify Phase 14 gap tracker governance readiness."""

    resolved_root = root.expanduser().resolve(strict=False)
    checks: list[GapTrackerCheck] = []

    for filename in MANDATORY_PHASE_14_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"GAPTRACKER-GOV-{filename.replace('/', '-').replace('.', '-').upper()}",
                passed=path.exists(),
                summary=f"Mandatory Phase 14 governance file exists: {filename}",
                evidence=[filename] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_14_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"GAPTRACKER-SUPPORT-{filename.replace('/', '-').replace('.', '-').upper()}",
                passed=path.exists(),
                summary=f"Mandatory Phase 14 support file exists: {filename}",
                evidence=[filename] if path.exists() else [],
            )
        )

    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    roadmap = _read_text(resolved_root / "ROADMAP.md")
    agents = _read_text(resolved_root / "AGENTS.md")
    phase14 = _read_text(resolved_root / "PHASE_14_SUBROADMAP.md")
    tracker = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    workflow = _read_text(resolved_root / ".github/workflows/ci.yml")
    handoff_service = _read_text(resolved_root / "src/bountyclaw/handoff/service.py")

    checks.extend(
        [
            _pass_fail(
                check_id="GAPTRACKER-ARCHITECTURE-PHASE14-MARKER",
                passed="Phase 14" in architecture and "gap tracker" in architecture.lower(),
                summary="Architecture records Phase 14 gap tracker governance boundary.",
                evidence=["ARCHITECTURE.md mentions Phase 14 gap tracker governance"]
                if "Phase 14" in architecture
                else [],
            ),
            _pass_fail(
                check_id="GAPTRACKER-ROADMAP-PHASE14-MARKER",
                passed="Phase 14" in roadmap and "Gap Tracker" in roadmap,
                summary="Roadmap records Phase 14 as completed locally and updates the continuation path.",
                evidence=["ROADMAP.md Phase 14 section found"] if "Phase 14" in roadmap else [],
            ),
            _pass_fail(
                check_id="GAPTRACKER-AGENTS-PHASE14-MARKER",
                passed="Gap Tracker Governance Agent" in agents,
                summary="Agent governance records the Phase 14 Gap Tracker Governance Agent.",
                evidence=["AGENTS.md Gap Tracker Governance Agent found"]
                if "Gap Tracker Governance Agent" in agents
                else [],
            ),
            _pass_fail(
                check_id="GAPTRACKER-SUBROADMAP-COMPLETED",
                passed="Completed in ChatGPT Project Mode" in phase14,
                summary="PHASE_14_SUBROADMAP.md records local completion status.",
                evidence=["PHASE_14_SUBROADMAP.md completion marker found"]
                if "Completed in ChatGPT Project Mode" in phase14
                else [],
            ),
            _pass_fail(
                check_id="GAPTRACKER-CI-PHASE14-VERIFY-DEFINED",
                passed="python scripts/phase14_verify.py --root ." in workflow,
                summary="CI definition includes Phase 14 gap tracker verification script.",
                evidence=["python scripts/phase14_verify.py --root ."]
                if "phase14_verify.py" in workflow
                else [],
            ),
            _pass_fail(
                check_id="GAPTRACKER-HANDOFF-COMMANDS-UPDATED",
                passed="GAP_TRACKER_COMMANDS.md" in handoff_service,
                summary="Phase 11 handoff export includes Phase 14 gap tracker commands.",
                evidence=["GAP_TRACKER_COMMANDS.md"]
                if "GAP_TRACKER_COMMANDS.md" in handoff_service
                else [],
            ),
        ]
    )

    audit = audit_gap_tracker(resolved_root)
    backlog = build_codex_gap_backlog(resolved_root)
    checks.extend(
        [
            _pass_fail(
                check_id="GAPTRACKER-AUDIT-ENTRY-COVERAGE",
                passed=audit.entry_count >= 60,
                summary="Gap tracker audit found the expected unresolved production gap ledger volume.",
                evidence=[f"entry_count={audit.entry_count}"],
            ),
            _pass_fail(
                check_id="GAPTRACKER-AUDIT-REQUIRED-FIELDS",
                passed=audit.missing_required_field_count == 0
                and not audit.entries_with_missing_required_fields,
                summary="All parsed gap entries include the mandatory required fields.",
                evidence=[f"missing_required_field_count={audit.missing_required_field_count}"],
            ),
            _pass_fail(
                check_id="GAPTRACKER-AUDIT-UNIQUE-IDS",
                passed=not audit.duplicate_gap_ids and not audit.malformed_entry_ids,
                summary="Gap tracker IDs are unique and match each entry header.",
                evidence=["duplicate_gap_ids=0", "malformed_entry_ids=0"],
            ),
            _pass_fail(
                check_id="GAPTRACKER-BACKLOG-COVERAGE",
                passed=backlog.item_count == audit.entry_count and backlog.item_count >= 60,
                summary="Codex backlog covers every unresolved production gap entry.",
                evidence=[
                    f"backlog_item_count={backlog.item_count}",
                    f"gap_entry_count={audit.entry_count}",
                ],
            ),
            _pass_fail(
                check_id="GAPTRACKER-NO-AUTO-CLOSURE",
                passed=not audit.ready_for_gap_closure
                and not audit.ready_for_production
                and not backlog.ready_for_gap_closure
                and not backlog.ready_for_production
                and all(not item.auto_gap_closure_allowed for item in backlog.items),
                summary="Gap tracker tooling cannot automatically close gaps or raise production readiness.",
                evidence=["ready_for_gap_closure=false", "ready_for_production=false"],
            ),
            _pass_fail(
                check_id="GAPTRACKER-PHASE14-GAPS-RECORDED",
                passed=all(gap_id in tracker for gap_id in EXPECTED_PHASE_14_GAP_IDS),
                summary="Phase 14 unresolved external-execution gaps are recorded in PRODUCTION_GAP_TRACKER.md.",
                evidence=[gap_id for gap_id in EXPECTED_PHASE_14_GAP_IDS if gap_id in tracker],
            ),
        ]
    )

    release_result = verify_release_controls(resolved_root)
    checks.append(
        _pass_fail(
            check_id="GAPTRACKER-RELEASE-VERIFY-COMMIT-READY",
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
            check_id="GAPTRACKER-HARDENING-VERIFY-COMMIT-READY",
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
            check_id="GAPTRACKER-HANDOFF-VERIFY-CODEX-READY",
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
    evidence_result = verify_validation_evidence_readiness(resolved_root)
    checks.append(
        _pass_fail(
            check_id="GAPTRACKER-VALIDATION-EVIDENCE-VERIFY-CODEX-READY",
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
    review_result = verify_evidence_review_readiness(resolved_root)
    checks.append(
        _pass_fail(
            check_id="GAPTRACKER-EVIDENCE-REVIEW-VERIFY-CODEX-READY",
            passed=review_result.ready_for_commit
            and review_result.ready_for_codex
            and review_result.failed_count == 0,
            summary="Phase 13 evidence-review verifier remains Codex-ready.",
            evidence=[
                f"passed={review_result.passed_count}",
                f"failed={review_result.failed_count}",
            ],
        )
    )

    checks.append(
        _deferred(
            check_id="GAPTRACKER-EXTERNAL-GAP-CLOSURE-STILL-OPEN",
            summary="Gap tracker backlog is ready, but real external validation and human-approved gap closure remain open.",
            deferred_reason="ChatGPT Project Mode cannot run external validations, create real evidence artifacts, perform human evidence review, or apply production gap closures.",
            future_validation_required="Execute Codex/local/CI/human validation tasks, review evidence privately, apply approved gap tracker updates manually, and rerun Phase 14 audit/backlog commands.",
            future_environment_required="Repository-hosted CI, Codex/local execution environment, private evidence storage, and human release/AppSec authority.",
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
    return GapTrackerVerificationResult(
        repository_root=str(resolved_root),
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
            "Phase 14 verification is local-only and metadata-only.",
            "ready_for_codex may be true while ready_for_gap_closure and ready_for_production remain false because external validation evidence and human-approved governance updates are still missing.",
            "No hosted CI, clean install, live provider, real MCP/browser, active validation, report submission, or gap closure was executed by this verifier.",
        ],
    )
