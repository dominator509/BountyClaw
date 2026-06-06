"""Deterministic Phase 11 external-validation handoff services.

These services are local-only. They prepare a future executor to close external
production gaps, but they do not run hosted CI, install packages, contact model
providers, launch scanners, use MCP/browser runtimes, perform active validation,
or submit bounty reports.
"""

from __future__ import annotations

import json
from pathlib import Path

from bountyclaw.hardening import build_external_validation_plan, verify_local_hardening
from bountyclaw.release import verify_release_controls

from .models import (
    CodexHandoffPlan,
    EvidenceArtifactTemplate,
    EvidenceTemplate,
    HandoffCheck,
    HandoffExportResult,
    HandoffTask,
    HandoffVerificationResult,
)

MANDATORY_PHASE_11_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_10_SUBROADMAP.md",
    "PHASE_11_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
)

MANDATORY_PHASE_11_SUPPORT_FILES: tuple[str, ...] = (
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

EXPECTED_HANDOFF_TASK_IDS: tuple[str, ...] = (
    "P11-HANDOFF-001",
    "P11-HANDOFF-002",
    "P11-HANDOFF-003",
    "P11-HANDOFF-004",
    "P11-HANDOFF-005",
    "P11-HANDOFF-006",
    "P11-HANDOFF-007",
    "P11-HANDOFF-008",
    "P11-HANDOFF-009",
    "P11-HANDOFF-010",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _pass_fail(
    *,
    check_id: str,
    category: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> HandoffCheck:
    return HandoffCheck(
        check_id=check_id,
        category=category,  # type: ignore[arg-type]
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
    category: str,
    summary: str,
    deferred_reason: str,
    future_validation_required: str,
    future_environment_required: str,
    required_for_commit: bool = False,
    required_for_codex: bool = False,
    required_for_production: bool = True,
) -> HandoffCheck:
    return HandoffCheck(
        check_id=check_id,
        category=category,  # type: ignore[arg-type]
        status="deferred",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_codex=required_for_codex,
        required_for_production=required_for_production,
        deferred_reason=deferred_reason,
        future_validation_required=future_validation_required,
        future_environment_required=future_environment_required,
    )


def build_codex_handoff_plan(root: Path) -> CodexHandoffPlan:
    """Build a deterministic post-Phase-10 external-validation handoff plan."""

    resolved_root = root.expanduser().resolve(strict=False)
    tasks = [
        HandoffTask(
            task_id="P11-HANDOFF-001",
            category="governance",
            title="Baseline reconciliation and rollback snapshot",
            purpose="Confirm the future executor starts from the Phase 11 handoff bundle and preserves Phase 10 local hardening as rollback fallback.",
            related_gap_ids=["PGT-087", "PGT-097"],
            prerequisite_files=[
                "ARCHITECTURE.md",
                "ROADMAP.md",
                "PRODUCTION_GAP_TRACKER.md",
                "ROLLBACK.md",
            ],
            environment_required="Codex/local workspace with repository checkout and Python 3.12+.",
            recommended_future_agent_type="Deterministic SDLC controller / Codex orchestration agent",
            risk_level="medium",
            exact_commands_or_steps=[
                "python -m bountyclaw doctor",
                "python -m bountyclaw release verify --root . --json",
                "python -m bountyclaw hardening verify --root . --json",
                "python -m bountyclaw handoff verify --root . --json",
                "Archive the Phase 11 source ZIP and current git commit SHA before external changes.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/baseline_reconciliation.json",
                "validation_evidence/rollback_snapshot.txt",
            ],
            completion_criteria=[
                "Future executor confirms Phase 11 bundle hash or commit SHA.",
                "Release, hardening, and handoff verifiers are commit-ready.",
                "Rollback target is documented before external execution starts.",
            ],
            blocked_in_chatgpt_reason="ChatGPT Project Mode cannot access the future repository commit, git remote, or external executor state.",
            prohibited_claims_until_complete=[
                "Do not claim external validation has started.",
                "Do not claim a repository-host baseline until a real commit or bundle hash is recorded.",
            ],
            rollback_considerations="Return to the Phase 10 local hardening baseline and source ZIP if external setup diverges.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-002",
            category="ci_cd",
            title="Hosted CI execution proof",
            purpose="Run the defined CI workflow on a real repository runner and archive logs.",
            related_gap_ids=["PGT-018", "PGT-083", "PGT-088"],
            prerequisite_files=[
                ".github/workflows/ci.yml",
                "scripts/phase9_verify.py",
                "scripts/phase10_verify.py",
                "scripts/phase11_verify.py",
            ],
            environment_required="GitHub Actions or equivalent hosted/self-hosted CI runner.",
            recommended_future_agent_type="DevSecOps/Codex release agent",
            risk_level="high",
            exact_commands_or_steps=[
                "Open a pull request or push to a protected validation branch.",
                "Run the BountyClaw CI workflow in the repository host.",
                "Confirm validate and package jobs complete or fail deterministically.",
                "Attach workflow URL, job logs, Python versions, and artifact summaries to the evidence ledger.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/hosted_ci_run.json",
                "validation_evidence/hosted_ci_logs.txt",
            ],
            completion_criteria=[
                "Hosted CI run URL is recorded.",
                "All required jobs pass or failures are remediated and rerun.",
                "Workflow evidence is linked from PRODUCTION_GAP_TRACKER.md.",
            ],
            blocked_in_chatgpt_reason="ChatGPT Project Mode has no hosted repository runner or repository-host API authority.",
            prohibited_claims_until_complete=[
                "Do not claim CI passed until the hosted run URL and logs exist."
            ],
            rollback_considerations="Keep local pytest/compileall/verify scripts as baseline if hosted CI fails.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-003",
            category="packaging",
            title="Clean wheel/sdist build and install validation",
            purpose="Prove the package installs and runs without PYTHONPATH in a fresh environment.",
            related_gap_ids=["PGT-084", "PGT-089"],
            prerequisite_files=["pyproject.toml", "README.md"],
            environment_required="Codex/local/CI environment with package-index access or an approved local wheelhouse.",
            recommended_future_agent_type="Release-engineering agent",
            risk_level="high",
            exact_commands_or_steps=[
                "python -m pip install --upgrade pip build",
                "python -m build",
                "python -m venv <tempdir>/bountyclaw-clean-install",
                "<tempdir>/bountyclaw-clean-install/bin/python -m pip install dist/*.whl",
                "<tempdir>/bountyclaw-clean-install/bin/bountyclaw doctor",
                "<tempdir>/bountyclaw-clean-install/bin/bountyclaw handoff verify --root . --json",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/package_build_install.txt",
                "validation_evidence/wheel_metadata.json",
            ],
            completion_criteria=[
                "Wheel and sdist are built.",
                "Fresh install works without PYTHONPATH.",
                "CLI entrypoint smoke checks pass from the installed package.",
            ],
            blocked_in_chatgpt_reason="Dependency installation and clean venv package-index behavior cannot be guaranteed in this environment.",
            prohibited_claims_until_complete=[
                "Do not claim package release readiness until clean install logs exist."
            ],
            rollback_considerations="Do not publish a package if build/install validation fails; retain source checkout execution.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-004",
            category="security_tools",
            title="Static quality and security gate execution",
            purpose="Run the configured lint, type, dependency, and security tools with real dependencies installed.",
            related_gap_ids=["PGT-032", "PGT-090"],
            prerequisite_files=["pyproject.toml", ".github/workflows/ci.yml"],
            environment_required="Codex/local/CI environment with dev dependencies installed.",
            recommended_future_agent_type="AppSec and quality agent",
            risk_level="high",
            exact_commands_or_steps=[
                "python -m pip install -e '.[dev]'",
                "ruff check src tests scripts",
                "mypy src",
                "bandit -q -r src",
                "pip-audit --progress-spinner off",
                "Record all findings, remediations, and accepted-risk decisions.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/static_quality_security_gates.json",
                "validation_evidence/dependency_audit.txt",
            ],
            completion_criteria=[
                "Ruff passes or documented fixes are applied.",
                "Type checking passes or accepted risks are documented.",
                "Bandit and pip-audit pass or no unresolved high/critical findings remain.",
            ],
            blocked_in_chatgpt_reason="Optional dev/security tools may not be installed or fetchable in ChatGPT Project Mode.",
            prohibited_claims_until_complete=[
                "Do not claim security gates passed until tool output is archived."
            ],
            rollback_considerations="Block release if high/critical findings remain unresolved.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-005",
            category="scanner_sandbox",
            title="External scanner and sandbox/egress validation",
            purpose="Validate real scanner binaries only inside a controlled non-network sandbox.",
            related_gap_ids=["PGT-016", "PGT-038", "PGT-039", "PGT-091"],
            prerequisite_files=["src/bountyclaw/scanning/", "PRODUCTION_GAP_TRACKER.md"],
            environment_required="Local/Codex/CI system with approved scanner binaries, container/OS sandbox, and egress logging.",
            recommended_future_agent_type="AppSec scanner-integration agent",
            risk_level="critical",
            exact_commands_or_steps=[
                "Install approved scanner binaries in a disposable sandbox.",
                "Run scanner fixtures against intentionally vulnerable local repositories only.",
                "Prove outbound network egress is denied and target code is not executed.",
                "Normalize scanner output through the findings store and compare expected findings.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/external_scanner_fixture_results.json",
                "validation_evidence/scanner_sandbox_egress_denial.txt",
            ],
            completion_criteria=[
                "Scanner fixture results match expected canonical findings.",
                "Sandbox and egress-denial logs are archived.",
                "External scanners remain disabled if sandbox proof fails.",
            ],
            blocked_in_chatgpt_reason="Real scanner binaries, containers, and egress firewall evidence are unavailable here.",
            prohibited_claims_until_complete=[
                "Do not claim external scanner readiness or sandbox safety until logs exist."
            ],
            rollback_considerations="Disable external scanner adapters and keep the built-in static scanner fallback.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-006",
            category="ai_safety",
            title="Live/local model provider safety validation",
            purpose="Validate provider credentials, no-secret payload controls, prompt-injection resilience, and model-output boundaries before any live provider use.",
            related_gap_ids=["PGT-014", "PGT-015", "PGT-047", "PGT-049", "PGT-092"],
            prerequisite_files=["src/bountyclaw/model_router/", "SECURITY_VALIDATION.md"],
            environment_required="Governed local/CI environment with approved provider credentials or local model runtime and egress controls.",
            recommended_future_agent_type="AI safety/AppSec validation agent",
            risk_level="critical",
            exact_commands_or_steps=[
                "Run expanded redaction corpus before provider payload construction.",
                "Capture no-secret payload logs for each approved provider or local model server.",
                "Run adversarial prompt-injection and model-output safety fixtures.",
                "Verify model output cannot invoke tools, expand scope, validate exploits, or submit reports.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/live_provider_no_secret_payloads.json",
                "validation_evidence/model_output_safety_eval.json",
            ],
            completion_criteria=[
                "No raw secrets appear in provider payload logs.",
                "Injection attempts are detected or bounded.",
                "Model outputs remain advisory and non-executing.",
            ],
            blocked_in_chatgpt_reason="Live providers require credentials, governed egress, and telemetry capture not available here.",
            prohibited_claims_until_complete=[
                "Do not enable or claim live-provider readiness until validation evidence exists."
            ],
            rollback_considerations="Keep deterministic mock.local provider only if any live/local provider validation fails.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-007",
            category="mcp_browser",
            title="Real MCP/browser runtime validation",
            purpose="Validate approved MCP servers and browser runtimes under strict allowlists and sandboxing.",
            related_gap_ids=["PGT-069", "PGT-070", "PGT-071", "PGT-072", "PGT-073", "PGT-093"],
            prerequisite_files=[
                "src/bountyclaw/mcp_gateway/",
                "src/bountyclaw/browser_controller/",
            ],
            environment_required="Codex/local/CI with approved MCP servers, Playwright/browser runtime, sandbox, and egress controls.",
            recommended_future_agent_type="Platform/AppSec runtime agent",
            risk_level="critical",
            exact_commands_or_steps=[
                "Launch only allowlisted MCP/browser fixtures in a sandbox.",
                "Prove unregistered MCP tools fail closed.",
                "Prove browser live target contact and form submission remain denied.",
                "Treat all MCP/browser output as untrusted and verify downstream redaction.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/mcp_runtime_allowlist_results.json",
                "validation_evidence/browser_runtime_sandbox_results.json",
            ],
            completion_criteria=[
                "Registered fixtures work only within policy.",
                "Unregistered tools and live submissions fail closed.",
                "Sandbox/egress logs are archived.",
            ],
            blocked_in_chatgpt_reason="Real MCP servers, browser runtimes, sandboxes, and egress controls are unavailable here.",
            prohibited_claims_until_complete=[
                "Do not claim real MCP/browser readiness until runtime logs exist."
            ],
            rollback_considerations="Keep fixture-only MCP/browser paths if real runtime validation fails.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-008",
            category="report_quality",
            title="Human report-quality and manual-submission validation",
            purpose="Validate draft usefulness against authorized bounty-program expectations while preserving manual submission only.",
            related_gap_ids=["PGT-057", "PGT-063", "PGT-064", "PGT-065", "PGT-094"],
            prerequisite_files=["src/bountyclaw/reports/", "SECURITY_VALIDATION.md"],
            environment_required="Human AppSec review workflow with authorized program policy and sanitized evidence.",
            recommended_future_agent_type="Human AppSec/report-review agent",
            risk_level="high",
            exact_commands_or_steps=[
                "Select only authorized program fixtures or owned assets.",
                "Generate report drafts from redacted canonical findings.",
                "Human reviewer evaluates accuracy, impact wording, remediation, and program fit.",
                "Document that submission remains manual and not automated.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/human_report_quality_review.md",
                "validation_evidence/manual_submission_control_attestation.md",
            ],
            completion_criteria=[
                "Human reviewer signs off or records remediation tasks.",
                "No fabricated exploitability, impact, or validation claims exist.",
                "Manual submission control remains enforced.",
            ],
            blocked_in_chatgpt_reason="Requires human security judgment, real program policies, and authorized evidence context.",
            prohibited_claims_until_complete=[
                "Do not claim payout optimization or program acceptance without human review evidence."
            ],
            rollback_considerations="Keep reports as internal drafts if human quality review fails.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-009",
            category="operations",
            title="Operations, performance, retention, backup/restore, and rollback drills",
            purpose="Validate local-state durability and operational behavior over representative repositories.",
            related_gap_ids=["PGT-043", "PGT-044", "PGT-075", "PGT-076", "PGT-080", "PGT-095"],
            prerequisite_files=[
                "ROLLBACK.md",
                "src/bountyclaw/findings/",
                "src/bountyclaw/memory/",
            ],
            environment_required="Local/CI/staging-like environment with representative repositories and storage tooling.",
            recommended_future_agent_type="SRE/platform validation agent",
            risk_level="medium",
            exact_commands_or_steps=[
                "Run repository inspection, scan, findings collection, triage, report drafting, memory export/delete, and handoff verification on representative data.",
                "Measure runtime and resource use.",
                "Perform backup/restore and retention/export/delete drills for evidence/report/memory stores.",
                "Perform rollback drill from Phase 11 to Phase 10 baseline.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/performance_baseline.json",
                "validation_evidence/backup_restore_retention_drill.md",
                "validation_evidence/rollback_drill.md",
            ],
            completion_criteria=[
                "Performance baseline is recorded.",
                "Backup/restore and delete/export controls pass.",
                "Rollback drill succeeds without external cleanup surprises.",
            ],
            blocked_in_chatgpt_reason="Requires representative datasets, storage decisions, and drill execution outside this ephemeral environment.",
            prohibited_claims_until_complete=[
                "Do not claim operational readiness until drill evidence exists."
            ],
            rollback_considerations="Disable memory/evidence persistence for enterprise workflows if restore or retention validation fails.",
        ),
        HandoffTask(
            task_id="P11-HANDOFF-010",
            category="release_governance",
            title="Repository release governance, signing, provenance, and publishing dry run",
            purpose="Configure release governance only after external validation and human approval.",
            related_gap_ids=["PGT-085", "PGT-086", "PGT-096", "PGT-098", "PGT-099"],
            prerequisite_files=["RELEASE.md", "ROLLBACK.md", ".github/dependabot.yml"],
            environment_required="Repository-host admin environment, package registry, signing/provenance tooling, and human release authority.",
            recommended_future_agent_type="Release engineering and repository governance agent",
            risk_level="high",
            exact_commands_or_steps=[
                "Configure branch protection or rulesets with required CI status checks.",
                "Perform package publishing dry run to approved registry or test index.",
                "Generate and verify signatures/provenance if approved.",
                "Record human release approval and rollback plan before any publish action.",
            ],
            expected_evidence_artifacts=[
                "validation_evidence/branch_protection_rules.json",
                "validation_evidence/signing_provenance_attestation.txt",
                "validation_evidence/package_publish_dry_run.txt",
            ],
            completion_criteria=[
                "Branch protection requires validation gates.",
                "Dry-run publish succeeds without leaking credentials.",
                "Signing/provenance artifacts are generated and verifiable.",
            ],
            blocked_in_chatgpt_reason="Requires repository admin permissions, package registry credentials, signing infrastructure, and human release authority.",
            prohibited_claims_until_complete=[
                "Do not claim signed/published/release-governed artifacts until evidence exists."
            ],
            rollback_considerations="Do not publish externally if governance, signing, provenance, or dry-run validation fails.",
        ),
    ]
    return CodexHandoffPlan(
        repository_root=str(resolved_root),
        tasks=tasks,
        task_count=len(tasks),
        ready_for_codex=all(task.task_id in EXPECTED_HANDOFF_TASK_IDS for task in tasks),
        notes=[
            "Phase 11 handoff planning is local-only and non-networked.",
            "The plan intentionally keeps ready_for_production=false until future evidence artifacts are produced outside ChatGPT Project Mode.",
            f"Phase 10 hardening external-plan currently lists {build_external_validation_plan().task_count} environment-limited tasks.",
        ],
    )


def build_evidence_template(root: Path | None = None) -> EvidenceTemplate:
    """Build deterministic evidence artifact expectations for future validators."""

    plan = build_codex_handoff_plan(root or Path("."))
    artifacts: list[EvidenceArtifactTemplate] = []
    for task in plan.tasks:
        for index, filename in enumerate(task.expected_evidence_artifacts, start=1):
            artifacts.append(
                EvidenceArtifactTemplate(
                    artifact_id=f"{task.task_id}-EVID-{index:02d}",
                    filename=filename,
                    producer_task_id=task.task_id,
                    validates_gap_ids=task.related_gap_ids,
                    sensitive_handling=(
                        "Redact secrets and private program details before committing. Store raw logs only in approved private evidence storage."
                    ),
                    acceptance_criteria=[
                        "Artifact is produced by the named future environment, not by ChatGPT Project Mode.",
                        "Artifact includes timestamp, executor identity or CI run URL where applicable, and exact command/tool versions.",
                        "Artifact does not contain raw secrets, unauthorized target data, provider credentials, or submission tokens.",
                    ],
                )
            )
    return EvidenceTemplate(
        artifacts=artifacts,
        artifact_count=len(artifacts),
        notes=[
            "Evidence template is a non-executing contract for future validators.",
            "Completion of evidence artifacts must be reflected in PRODUCTION_GAP_TRACKER.md before production claims change.",
        ],
    )


def _markdown_plan(plan: CodexHandoffPlan, evidence_template: EvidenceTemplate) -> str:
    lines = [
        "# BountyClaw Codex / External Validation Handoff",
        "",
        "This package was generated locally by Phase 11. It does not prove external validation has run.",
        "",
        f"- Source phase: {plan.source_phase}",
        f"- Handoff phase: {plan.phase}",
        f"- Ready for Codex/local/CI continuation: {plan.ready_for_codex}",
        f"- Ready for production: {plan.ready_for_production}",
        f"- External actions executed by generator: {plan.external_actions_executed}",
        "",
        "## Mandatory Rules",
        "",
        "- Do not contact live targets unless a later authorized environment explicitly approves it.",
        "- Do not enable live model providers before no-secret payload validation and output-safety review.",
        "- Do not run real MCP/browser runtimes without allowlists, sandboxing, and egress controls.",
        "- Do not submit bounty reports automatically.",
        "- Update PRODUCTION_GAP_TRACKER.md with exact evidence before closing any gap.",
        "",
        "## Tasks",
        "",
    ]
    for task in plan.tasks:
        lines.extend(
            [
                f"### {task.task_id}: {task.title}",
                "",
                f"- Category: {task.category}",
                f"- Risk: {task.risk_level}",
                f"- Related gaps: {', '.join(task.related_gap_ids)}",
                f"- Environment: {task.environment_required}",
                f"- Future agent: {task.recommended_future_agent_type}",
                f"- Why blocked here: {task.blocked_in_chatgpt_reason}",
                "- Commands / steps:",
            ]
        )
        lines.extend(f"  - `{step}`" for step in task.exact_commands_or_steps)
        lines.append("- Evidence artifacts:")
        lines.extend(f"  - `{artifact}`" for artifact in task.expected_evidence_artifacts)
        lines.append("- Completion criteria:")
        lines.extend(f"  - {criterion}" for criterion in task.completion_criteria)
        lines.append(f"- Rollback: {task.rollback_considerations}")
        lines.append("")
    lines.extend(
        [
            "## Evidence Artifact Count",
            "",
            f"Expected artifacts: {evidence_template.artifact_count}",
            "",
        ]
    )
    return "\n".join(lines)


def _commands_markdown(plan: CodexHandoffPlan) -> str:
    lines = ["# BountyClaw Future Validation Commands", ""]
    for task in plan.tasks:
        lines.append(f"## {task.task_id}: {task.title}")
        lines.append("")
        for step in task.exact_commands_or_steps:
            lines.append(f"- `{step}`")
        lines.append("")
    return "\n".join(lines)


def _gap_closure_markdown(plan: CodexHandoffPlan) -> str:
    lines = [
        "# Gap Closure Checklist",
        "",
        "A gap is not closed until evidence exists and governance files are updated.",
        "",
    ]
    for task in plan.tasks:
        lines.append(f"## {task.task_id}")
        lines.append("")
        for gap_id in task.related_gap_ids:
            lines.append(f"- [ ] {gap_id}: evidence from `{task.task_id}` attached and reviewed")
        lines.append("")
    return "\n".join(lines)


def _evidence_ledger_commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 12 Validation Evidence Ledger Commands",
            "",
            "Run these commands after future Codex/local/CI/human executors produce external-validation artifacts under `validation_evidence/`.",
            "",
            "- `python -m bountyclaw validation-evidence ledger --root . --evidence-dir validation_evidence --json`",
            "- `python -m bountyclaw validation-evidence gap-readiness --root . --evidence-dir validation_evidence --json`",
            "- `python -m bountyclaw validation-evidence export-ledger --root . --evidence-dir validation_evidence --output validation_evidence_ledger --json`",
            "- `python -m bountyclaw validation-evidence verify --root . --evidence-dir validation_evidence --json`",
            "- `python scripts/phase12_verify.py --root . --evidence-dir validation_evidence --json`",
            "",
            "These commands hash and map artifacts; they do not inspect contents, close gaps, execute external validation, or prove production readiness.",
        ]
    )


def _evidence_review_commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 13 Evidence Review and Gap-Closure Proposal Commands",
            "",
            "Run these commands after external artifacts exist and the Phase 12 ledger has hashed them.",
            "",
            "- `python -m bountyclaw evidence-review template --root . --evidence-dir validation_evidence --json`",
            "- Create `validation_evidence/evidence_review_decisions.json` only after a human release/AppSec reviewer privately reviews redacted artifacts.",
            "- `python -m bountyclaw evidence-review status --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`",
            "- `python -m bountyclaw evidence-review closure-proposals --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`",
            "- `python -m bountyclaw evidence-review export-package --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --output validation_evidence_review --json`",
            "- `python -m bountyclaw evidence-review verify --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`",
            "- `python scripts/phase13_verify.py --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`",
            "",
            "These commands validate review metadata and draft gap-closure proposals; they do not inspect raw evidence, edit gap files, close gaps, or prove production readiness.",
        ]
    )


def _gap_tracker_commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 14 Gap Tracker Governance Commands",
            "",
            "Run these commands after Phase 12/13 evidence ledger and review work changes `PRODUCTION_GAP_TRACKER.md`.",
            "",
            "- `python -m bountyclaw gap-tracker audit --root . --json`",
            "- `python -m bountyclaw gap-tracker backlog --root . --json`",
            "- `python -m bountyclaw gap-tracker export --root . --output gap_tracker_package --json`",
            "- `python -m bountyclaw gap-tracker verify --root . --json`",
            "- `python scripts/phase14_verify.py --root . --json`",
            "",
            "These commands audit and queue unresolved gaps; they do not inspect raw evidence, edit gap files, close gaps, or prove production readiness.",
        ]
    )


def _validation_runbook_commands_markdown() -> str:
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


def _validation_baseline_commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 16 Validation Baseline Commands",
            "",
            "Run these commands before and after future external validation to bind evidence to the exact source snapshot under review.",
            "",
            "- `python -m bountyclaw validation-baseline manifest --root . --json`",
            "- `python -m bountyclaw validation-baseline export --root . --output validation_baseline --json`",
            "- `python -m bountyclaw validation-baseline verify --root . --json`",
            "- `python scripts/phase16_verify.py --root . --json`",
            "",
            "These commands create hash-only source baseline metadata. They do not execute external validation, inspect raw evidence, close gaps, or prove production readiness.",
        ]
    )


def _closure_gate_commands_markdown() -> str:
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
            "These commands create readiness-attestation templates and metadata-only closure-gate status reports. They do not inspect raw evidence, close gaps, change production readiness, execute external validation, or prove production readiness.",
        ]
    )


def _quality_gates_commands_markdown() -> str:
    lines = [
        "# BountyClaw Quality Gate Commands",
        "",
        "Run these commands after Phase 19 or in hosted CI to verify local quality/security gates.",
        "",
        "```bash",
        "PYTHONPATH=src python -m bountyclaw quality-gates checklist --root . --json",
        "PYTHONPATH=src python -m bountyclaw quality-gates export --root . --output quality_gates_package --json",
        "PYTHONPATH=src python -m bountyclaw quality-gates verify --root . --json",
        "PYTHONPATH=src python scripts/phase19_verify.py --root . --json",
        "ruff format --check src tests scripts",
        "ruff check src tests scripts",
        "PYTHONPATH=src mypy --no-incremental --cache-dir <tmp> src",
        "PYTHONPATH=src bandit -q -r src",
        "python -m build",
        "pip-audit --progress-spinner off",
        "```",
        "",
        "These commands verify local quality/security metadata and local gates. They do not contact targets, inspect raw evidence, close gaps, change readiness, or prove production readiness. Online dependency-audit completion requires DNS/network access or an approved mirror.",
    ]
    return "\n".join(lines)


def _readiness_dashboard_commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 18 Readiness Dashboard Commands",
            "",
            "Run these commands to produce a consolidated metadata-only external executor dashboard.",
            "",
            "- `python -m bountyclaw readiness-dashboard build --root . --json`",
            "- `python -m bountyclaw readiness-dashboard handoff-index --root . --json`",
            "- `python -m bountyclaw readiness-dashboard export --root . --output readiness_dashboard_package --json`",
            "- `python -m bountyclaw readiness-dashboard verify --root . --json`",
            "- `python scripts/phase18_verify.py --root . --json`",
            "",
            "These commands consolidate metadata from release, hardening, handoff, evidence, review, gap tracker, runbook, baseline, and closure-gate tooling. They do not inspect raw evidence, execute external validation, close gaps, change readiness, or prove production readiness.",
        ]
    )


def export_handoff_package(root: Path, output_dir: Path) -> HandoffExportResult:
    """Write a deterministic local handoff package to an output directory."""

    resolved_output = output_dir.expanduser().resolve(strict=False)
    resolved_output.mkdir(parents=True, exist_ok=True)
    plan = build_codex_handoff_plan(root)
    template = build_evidence_template(root)

    files: dict[str, str] = {
        "codex_handoff_plan.json": plan.model_dump_json(indent=2),
        "evidence_template.json": template.model_dump_json(indent=2),
        "CODEX_HANDOFF.md": _markdown_plan(plan, template),
        "VALIDATION_COMMANDS.md": _commands_markdown(plan),
        "GAP_CLOSURE_CHECKLIST.md": _gap_closure_markdown(plan),
        "EVIDENCE_LEDGER_COMMANDS.md": _evidence_ledger_commands_markdown(),
        "EVIDENCE_REVIEW_COMMANDS.md": _evidence_review_commands_markdown(),
        "GAP_TRACKER_COMMANDS.md": _gap_tracker_commands_markdown(),
        "VALIDATION_RUNBOOK_COMMANDS.md": _validation_runbook_commands_markdown(),
        "VALIDATION_BASELINE_COMMANDS.md": _validation_baseline_commands_markdown(),
        "CLOSURE_GATE_COMMANDS.md": _closure_gate_commands_markdown(),
        "READINESS_DASHBOARD_COMMANDS.md": _readiness_dashboard_commands_markdown(),
        "QUALITY_GATES_COMMANDS.md": _quality_gates_commands_markdown(),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))

    manifest_path = resolved_output / "handoff_manifest.json"
    manifest_payload = {
        "phase": "11",
        "ready_for_codex": plan.ready_for_codex,
        "ready_for_production": False,
        "task_count": plan.task_count,
        "artifact_count": template.artifact_count,
        "written_files": written_files,
        "network_used": False,
        "external_actions_executed": False,
    }
    manifest_path.write_text(
        json.dumps(manifest_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(manifest_path))

    return HandoffExportResult(
        output_directory=str(resolved_output),
        written_files=written_files,
        task_count=plan.task_count,
        artifact_count=template.artifact_count,
        ready_for_codex=plan.ready_for_codex,
        notes=[
            "Handoff package generation is local-only.",
            "Generated artifacts are templates/plans; they do not prove external validation has completed.",
        ],
    )


def verify_handoff_readiness(root: Path) -> HandoffVerificationResult:
    """Verify Phase 11 handoff artifacts are commit-ready and Codex-ready."""

    resolved_root = root.expanduser().resolve(strict=False)
    checks: list[HandoffCheck] = []

    for filename in MANDATORY_PHASE_11_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"HANDOFF-GOV-{filename}",
                category="governance",
                passed=path.exists(),
                summary=f"Mandatory Phase 11 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_11_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"HANDOFF-SUPPORT-{filename}",
                category="governance",
                passed=path.exists(),
                summary=f"Phase 11 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    roadmap = _read_text(resolved_root / "ROADMAP.md")
    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    gaps = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    checks.extend(
        [
            _pass_fail(
                check_id="HANDOFF-GOV-ROADMAP-PHASE11",
                category="governance",
                passed="Phase 11" in roadmap and "External Validation Handoff" in roadmap,
                summary="ROADMAP.md records Phase 11 handoff completion and remaining external validation.",
                evidence=["Phase 11 roadmap marker found"] if "Phase 11" in roadmap else [],
            ),
            _pass_fail(
                check_id="HANDOFF-GOV-ARCH-PHASE11",
                category="governance",
                passed="Phase 11" in architecture and "handoff" in architecture.lower(),
                summary="ARCHITECTURE.md records Phase 11 handoff subsystem.",
                evidence=["Phase 11 architecture marker found"]
                if "Phase 11" in architecture
                else [],
            ),
            _pass_fail(
                check_id="HANDOFF-GOV-GAPS-PHASE11",
                category="governance",
                passed=all(gap_id in gaps for gap_id in ("PGT-097", "PGT-098", "PGT-099")),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 11 handoff gaps.",
                evidence=["PGT-097..PGT-099 markers expected"] if gaps else [],
            ),
        ]
    )

    plan = build_codex_handoff_plan(resolved_root)
    task_ids = {task.task_id for task in plan.tasks}
    checks.append(
        _pass_fail(
            check_id="HANDOFF-PLAN-TASK-COVERAGE",
            category="governance",
            passed=set(EXPECTED_HANDOFF_TASK_IDS).issubset(task_ids) and plan.ready_for_codex,
            summary="Codex handoff plan includes all expected Phase 11 external-validation tasks.",
            evidence=sorted(task_ids),
        )
    )
    template = build_evidence_template(resolved_root)
    checks.append(
        _pass_fail(
            check_id="HANDOFF-EVIDENCE-TEMPLATE-COVERAGE",
            category="governance",
            passed=template.artifact_count >= plan.task_count,
            summary="Evidence template covers future validation tasks.",
            evidence=[f"artifact_count={template.artifact_count}", f"task_count={plan.task_count}"],
        )
    )

    release_result = verify_release_controls(resolved_root)
    checks.append(
        _pass_fail(
            check_id="HANDOFF-RELEASE-VERIFY-COMMIT-READY",
            category="release_governance",
            passed=release_result.ready_for_commit and release_result.failed_count == 0,
            summary="Phase 9 release-control verifier remains commit-ready.",
            evidence=[
                f"passed={release_result.passed_count}",
                f"failed={release_result.failed_count}",
                f"deferred={release_result.deferred_count}",
            ],
        )
    )

    hardening_result = verify_local_hardening(resolved_root)
    checks.append(
        _pass_fail(
            check_id="HANDOFF-HARDENING-VERIFY-COMMIT-READY",
            category="security_tools",
            passed=hardening_result.ready_for_commit and hardening_result.failed_count == 0,
            summary="Phase 10 hardening verifier remains commit-ready.",
            evidence=[
                f"passed={hardening_result.passed_count}",
                f"failed={hardening_result.failed_count}",
                f"deferred={hardening_result.deferred_count}",
            ],
        )
    )

    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    checks.append(
        _pass_fail(
            check_id="HANDOFF-CI-PHASE11-VERIFY-DEFINED",
            category="ci_cd",
            passed="python scripts/phase11_verify.py --root ." in workflow,
            summary="CI definition includes Phase 11 handoff verification script.",
            evidence=["python scripts/phase11_verify.py --root ."]
            if "phase11_verify.py" in workflow
            else [],
        )
    )
    checks.append(
        _pass_fail(
            check_id="HANDOFF-CI-PHASE12-LEDGER-VERIFY-DEFINED",
            category="ci_cd",
            passed="python scripts/phase12_verify.py --root ." in workflow,
            summary="CI definition includes Phase 12 validation-evidence ledger verification script.",
            evidence=["python scripts/phase12_verify.py --root ."]
            if "phase12_verify.py" in workflow
            else [],
        )
    )
    checks.append(
        _pass_fail(
            check_id="HANDOFF-CI-PHASE13-REVIEW-VERIFY-DEFINED",
            category="ci_cd",
            passed="python scripts/phase13_verify.py --root ." in workflow,
            summary="CI definition includes Phase 13 evidence-review verification script.",
            evidence=["python scripts/phase13_verify.py --root ."]
            if "phase13_verify.py" in workflow
            else [],
        )
    )
    checks.append(
        _pass_fail(
            check_id="HANDOFF-CI-PHASE14-GAP-TRACKER-VERIFY-DEFINED",
            category="ci_cd",
            passed="python scripts/phase14_verify.py --root ." in workflow,
            summary="CI definition includes Phase 14 gap tracker governance verification script.",
            evidence=["python scripts/phase14_verify.py --root ."]
            if "phase14_verify.py" in workflow
            else [],
        )
    )
    checks.append(
        _pass_fail(
            check_id="HANDOFF-CI-PHASE15-RUNBOOK-VERIFY-DEFINED",
            category="ci_cd",
            passed="python scripts/phase15_verify.py --root ." in workflow,
            summary="CI definition includes Phase 15 validation-runbook verification script.",
            evidence=["python scripts/phase15_verify.py --root ."]
            if "phase15_verify.py" in workflow
            else [],
        )
    )
    checks.append(
        _pass_fail(
            check_id="HANDOFF-CI-PHASE16-BASELINE-VERIFY-DEFINED",
            category="ci_cd",
            passed="python scripts/phase16_verify.py --root ." in workflow,
            summary="CI definition includes Phase 16 validation-baseline verification script.",
            evidence=["python scripts/phase16_verify.py --root ."]
            if "phase16_verify.py" in workflow
            else [],
        )
    )

    checks.append(
        _deferred(
            check_id="HANDOFF-EXTERNAL-VALIDATION-STILL-OPEN",
            category="operations",
            summary="Phase 11 handoff is Codex-ready but external production validation still has not run.",
            deferred_reason="ChatGPT Project Mode cannot run hosted CI, clean package installs, external scanner sandboxes, live providers, real MCP/browser runtimes, human report review, operational drills, branch protection, signing, provenance, or publishing.",
            future_validation_required="Execute the handoff plan tasks and attach the evidence artifacts named by the evidence template.",
            future_environment_required="Codex/local/CI/human production-validation environment with approved credentials, runners, scanners, sandboxing, and release authority.",
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
    return HandoffVerificationResult(
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
            "Phase 11 handoff verification is local-only and non-networked.",
            "ready_for_codex may be true while ready_for_production remains false because external evidence is still missing.",
            "Phase 12 validation-evidence ledger commands map future artifacts to gaps; Phase 13 evidence-review commands prepare human-reviewed gap-update proposals; Phase 14 gap tracker commands audit unresolved gap entries and export Codex backlog tasks.",
            "No hosted CI, clean install, live provider, real MCP/browser, active validation, or report submission was executed by this verifier.",
        ],
    )
