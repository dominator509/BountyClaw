"""BountyClaw command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .audit import AuditEvent, AuditLogWriter
from .browser_controller import (
    BrowserAuthorizationError,
    BrowserFeatureGateError,
    BrowserPolicyIngestionResult,
    build_policy_ingestion_plan,
    ingest_authorized_policy,
)
from .closure_gate import (
    ClosureGateExportResult,
    ClosureGateStatusResult,
    ClosureGateVerificationResult,
    ReadinessAttestationTemplateResult,
    assess_closure_gate_status,
    build_readiness_attestation_template,
    export_closure_gate_package,
    verify_closure_gate_readiness,
)
from .config import load_config
from .evidence_review import (
    EvidenceReviewExportResult,
    EvidenceReviewStatusResult,
    EvidenceReviewTemplateResult,
    EvidenceReviewVerificationResult,
    GapClosureProposalResult,
    assess_evidence_review_status,
    build_evidence_review_template,
    build_gap_closure_proposals,
    export_evidence_review_package,
    verify_evidence_review_readiness,
)
from .findings import (
    EvidenceStore,
    EvidenceStorePathError,
    FindingsAuthorizationError,
    FindingsCollectionResult,
    StoredFindingSummary,
    collect_authorized_findings,
)
from .gap_tracker import (
    CodexBacklogResult,
    GapTrackerAuditResult,
    GapTrackerExportResult,
    GapTrackerVerificationResult,
    audit_gap_tracker,
    build_codex_gap_backlog,
    export_gap_tracker_package,
    verify_gap_tracker_governance,
)
from .handoff import (
    CodexHandoffPlan,
    EvidenceTemplate,
    HandoffExportResult,
    HandoffVerificationResult,
    build_codex_handoff_plan,
    build_evidence_template,
    export_handoff_package,
    verify_handoff_readiness,
)
from .hardening import (
    ExternalValidationPlan,
    HardeningChecklistResult,
    HardeningVerificationResult,
    PromptSafetyCorpusResult,
    RedactionCorpusResult,
    build_external_validation_plan,
    build_hardening_checklist,
    run_prompt_safety_corpus,
    run_redaction_corpus,
    verify_local_hardening,
)
from .mcp_gateway import (
    POLICY_LOCAL_FILE_TOOL_ID,
    McpAuthorizationError,
    McpFeatureGateError,
    McpToolInvocationResult,
    McpToolSelectionError,
    invoke_authorized_mcp_tool,
    list_mcp_servers,
    list_mcp_tools,
)
from .memory import (
    MemoryApprovalError,
    MemoryAuthorizationError,
    MemoryDeleteResult,
    MemoryExport,
    MemoryNotFoundError,
    MemoryRecord,
    MemorySafetyError,
    MemoryWriteResult,
    SkillProposal,
    SkillSelectionError,
    delete_authorized_memory,
    export_authorized_memories,
    list_authorized_memories,
    list_skill_templates,
    propose_authorized_skill,
    remember_authorized_memory,
)
from .model_router import (
    ModelAuthorizationError,
    ModelFeatureGateError,
    ModelFindingNotFoundError,
    ModelRoutingError,
    ModelRoutingRequest,
    ModelTriageResult,
    provider_catalog,
    route_model_request,
    triage_authorized_finding,
)
from .policy import PolicyDocumentError, PolicyDocumentSummary
from .quality_gates import (
    QualityGateChecklist,
    QualityGateExportResult,
    QualityGateVerificationResult,
    build_quality_gate_checklist,
    export_quality_gate_package,
    verify_quality_gate_readiness,
)
from .readiness_dashboard import (
    ExternalExecutorIndex,
    ReadinessDashboard,
    ReadinessDashboardExportResult,
    ReadinessDashboardVerificationResult,
    build_external_executor_index,
    build_readiness_dashboard,
    export_readiness_dashboard_package,
    verify_readiness_dashboard,
)
from .release import (
    ReleaseChecklistResult,
    ReleaseRollbackPlan,
    ReleaseVerificationResult,
    build_release_checklist,
    build_release_rollback_plan,
    verify_release_controls,
)
from .reports import (
    ReportAuthorizationError,
    ReportDraftReadinessError,
    ReportDraftResult,
    ReportFindingNotFoundError,
    ReportStore,
    TriageReview,
    draft_authorized_report,
    record_triage_review,
)
from .repository import (
    RepositoryAuthorizationError,
    RepositoryFingerprint,
    ScanPlan,
    inspect_authorized_repository,
    plan_authorized_repository_scan,
)
from .scanning import (
    ScannerAuthorizationError,
    ScannerFeatureGateError,
    ScannerRunResult,
    ScannerSelectionError,
    scan_authorized_repository,
)
from .scope import ScopeGate, Target, TargetKind, load_scope_manifest
from .validation_baseline import (
    ValidationBaselineExportResult,
    ValidationBaselineManifest,
    ValidationBaselineVerificationResult,
    build_validation_baseline_manifest,
    export_validation_baseline_package,
    verify_validation_baseline_readiness,
)
from .validation_evidence import (
    GapClosureReadinessResult,
    ValidationEvidenceExportResult,
    ValidationEvidenceLedger,
    ValidationEvidenceVerificationResult,
    assess_gap_closure_readiness,
    build_validation_evidence_ledger,
    export_validation_evidence_ledger,
    verify_validation_evidence_readiness,
)
from .validation_runbook import (
    ExternalValidationRunbook,
    ValidationRunbookExportResult,
    ValidationRunbookVerificationResult,
    ValidationRunJournalFile,
    ValidationRunJournalStatusResult,
    assess_run_journal_status,
    build_external_validation_runbook,
    build_run_journal_template,
    export_validation_runbook_package,
    verify_validation_runbook_readiness,
)

console = Console()
app = typer.Typer(
    name="bountyclaw",
    help="Local-first authorized bug bounty research assistant.",
    no_args_is_help=True,
)
scope_app = typer.Typer(help="Validate authorization scope manifests.")
repo_app = typer.Typer(help="Read-only local repository intake and deterministic scan planning.")
scan_app = typer.Typer(help="Scope-gated local static scanner execution.")
findings_app = typer.Typer(help="Canonical findings and redacted local evidence storage.")
model_app = typer.Typer(help="Offline model routing and prompt-safety validation.")
report_app = typer.Typer(help="Human-reviewed triage and report draft generation.")
mcp_app = typer.Typer(help="Policy-bound MCP gateway foundation.")
browser_app = typer.Typer(help="Fixture-only headless browser policy ingestion foundation.")
memory_app = typer.Typer(help="Local memory with explicit approval and redaction controls.")
skills_app = typer.Typer(help="Non-executing reusable workflow skill templates.")
release_app = typer.Typer(help="CI/CD, packaging, and release-control checks.")
hardening_app = typer.Typer(help="Production hardening and external-validation planning.")
handoff_app = typer.Typer(help="Codex/local/CI external-validation handoff package.")
validation_evidence_app = typer.Typer(
    help="External-validation evidence ledger and gap-readiness checks."
)
evidence_review_app = typer.Typer(
    help="Human evidence-review metadata and gap-closure proposal checks."
)
gap_tracker_app = typer.Typer(help="Production gap tracker audit and Codex backlog export.")
validation_runbook_app = typer.Typer(
    help="External validation runbook and metadata-only execution journal."
)
validation_baseline_app = typer.Typer(
    help="Hash-only source baseline manifest for external validation evidence binding."
)
closure_gate_app = typer.Typer(
    help="Metadata-only closure gate and readiness attestation governance."
)
readiness_dashboard_app = typer.Typer(
    help="Metadata-only readiness dashboard and external executor index."
)
quality_gates_app = typer.Typer(
    help="Local quality/security gate checklist and metadata verification."
)
app.add_typer(scope_app, name="scope")
app.add_typer(repo_app, name="repo")
app.add_typer(scan_app, name="scan")
app.add_typer(findings_app, name="findings")
app.add_typer(model_app, name="model")
app.add_typer(report_app, name="report")
app.add_typer(mcp_app, name="mcp")
app.add_typer(browser_app, name="browser")
app.add_typer(memory_app, name="memory")
app.add_typer(skills_app, name="skills")
app.add_typer(release_app, name="release")
app.add_typer(hardening_app, name="hardening")
app.add_typer(handoff_app, name="handoff")
app.add_typer(validation_evidence_app, name="validation-evidence")
app.add_typer(evidence_review_app, name="evidence-review")
app.add_typer(gap_tracker_app, name="gap-tracker")
app.add_typer(validation_runbook_app, name="validation-runbook")
app.add_typer(validation_baseline_app, name="validation-baseline")
app.add_typer(closure_gate_app, name="closure-gate")
app.add_typer(readiness_dashboard_app, name="readiness-dashboard")
app.add_typer(quality_gates_app, name="quality-gates")

AuditDecisionText = Literal["allow", "deny", "require_human_approval", "informational"]


def _print_decision(decision_text: str, reasons: list[str]) -> None:
    console.print(decision_text)
    for reason in reasons:
        console.print(f"- {reason}")


def _write_audit(
    audit_log: Path | None,
    *,
    event_type: str,
    action: str,
    decision: AuditDecisionText,
    target_kind: str | None,
    target: str | None,
    reasons: list[str],
) -> None:
    if audit_log is None:
        return
    AuditLogWriter(audit_log).append(
        AuditEvent(
            event_type=event_type,
            action=action,
            decision=decision,
            target_kind=target_kind,
            target=target,
            reasons=reasons,
        )
    )


def _render_fingerprint_table(fingerprint: RepositoryFingerprint) -> None:
    summary = Table(title="Repository Fingerprint")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Root", fingerprint.root)
    summary.add_row("Fingerprint", fingerprint.fingerprint_id)
    summary.add_row("Files", str(fingerprint.file_count))
    summary.add_row("Total bytes", str(fingerprint.total_bytes))
    console.print(summary)

    languages = Table(title="Detected Languages")
    languages.add_column("Language")
    languages.add_column("Files")
    languages.add_column("Bytes")
    for language in fingerprint.language_summaries:
        languages.add_row(language.language, str(language.file_count), str(language.total_bytes))
    console.print(languages)

    manifests = Table(title="Detected Manifests")
    manifests.add_column("Path")
    manifests.add_column("Ecosystem")
    manifests.add_column("Kind")
    for manifest in fingerprint.package_manifests:
        manifests.add_row(manifest.path, manifest.ecosystem, manifest.kind)
    console.print(manifests)


def _render_scan_plan_table(plan: ScanPlan) -> None:
    summary = Table(title="Deterministic Scan Plan")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Repository", plan.repository)
    summary.add_row("Fingerprint", plan.repository_fingerprint_id)
    summary.add_row("Scanners execute", str(plan.scanners_execute))
    summary.add_row("Network required", str(plan.network_required))
    console.print(summary)

    steps = Table(title="Planned Steps (Not Executed)")
    steps.add_column("Step ID")
    steps.add_column("Adapter Family")
    steps.add_column("Reason")
    for step in plan.steps:
        steps.add_row(step.step_id, step.adapter_family, step.reason)
    console.print(steps)

    for note in plan.notes:
        console.print(f"- {note}")


def _render_scanner_result_table(result: ScannerRunResult) -> None:
    summary = Table(title="Local Static Scanner Result")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Repository", result.repository)
    summary.add_row("Fingerprint", result.repository_fingerprint_id)
    summary.add_row("Execution ID", result.scan_execution_id)
    summary.add_row(
        "Adapters", ", ".join(adapter.scanner_id for adapter in result.adapters) or "none"
    )
    summary.add_row("Findings", str(len(result.findings)))
    summary.add_row("Network used", str(result.network_used))
    console.print(summary)

    findings = Table(title="Preliminary Findings")
    findings.add_column("Rule")
    findings.add_column("Severity")
    findings.add_column("Confidence")
    findings.add_column("Location")
    findings.add_column("Title")
    for finding in result.findings:
        location = finding.file_path
        if finding.line_number is not None:
            location = f"{location}:{finding.line_number}"
        findings.add_row(
            finding.rule_id, finding.severity, finding.confidence, location, finding.title
        )
    console.print(findings)

    for note in result.notes:
        console.print(f"- {note}")


def _render_findings_collection_table(result: FindingsCollectionResult) -> None:
    summary = Table(title="Findings Collection Result")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Store", result.store_path)
    summary.add_row("Repository", result.repository)
    summary.add_row("Scan execution", result.scan_execution_id)
    summary.add_row("Canonical findings", str(len(result.canonical_findings)))
    summary.add_row("Evidence records", str(len(result.evidence_records)))
    summary.add_row("Redactions", str(result.redaction_count))
    console.print(summary)

    findings = Table(title="Canonical Findings")
    findings.add_column("Finding ID")
    findings.add_column("Severity")
    findings.add_column("Confidence")
    findings.add_column("Location")
    findings.add_column("Title")
    for finding in result.canonical_findings:
        location = finding.file_path
        if finding.line_number is not None:
            location = f"{location}:{finding.line_number}"
        findings.add_row(
            finding.canonical_finding_id,
            finding.severity,
            finding.confidence,
            location,
            finding.title,
        )
    console.print(findings)

    for note in result.notes:
        console.print(f"- {note}")


def _render_stored_findings_table(findings: list[StoredFindingSummary]) -> None:
    table = Table(title="Stored Canonical Findings")
    table.add_column("Finding ID")
    table.add_column("Severity")
    table.add_column("Confidence")
    table.add_column("Location")
    table.add_column("Evidence")
    table.add_column("Report Status")
    table.add_column("Title")
    for finding in findings:
        location = finding.file_path
        if finding.line_number is not None:
            location = f"{location}:{finding.line_number}"
        table.add_row(
            finding.canonical_finding_id,
            finding.severity,
            finding.confidence,
            location,
            str(finding.evidence_count),
            finding.report_readiness_status,
            finding.title,
        )
    console.print(table)


def _render_model_triage_table(result: ModelTriageResult) -> None:
    summary = Table(title="Mocked Model Triage Result")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Finding ID", result.canonical_finding_id)
    summary.add_row("Provider", result.routing_decision.provider_id)
    summary.add_row("Model", result.routing_decision.model_id)
    summary.add_row("Live provider used", str(result.live_llm_provider_used))
    summary.add_row("Prompt redactions", str(result.prompt_safety.total_redaction_count))
    summary.add_row("Injection signals", str(result.prompt_safety.injection_signal_count))
    console.print(summary)

    content = result.response.content
    triage = Table(title="Deterministic Mock Triage")
    triage.add_column("Field")
    triage.add_column("Value")
    triage.add_row("Status", str(content.get("triage_status", "unknown")))
    triage.add_row("Summary", str(content.get("summary", "")))
    triage.add_row("Severity input", str(content.get("severity_input", "unknown")))
    triage.add_row("Confidence input", str(content.get("confidence_input", "unknown")))
    console.print(triage)

    for note in result.notes + result.response.notes:
        console.print(f"- {note}")


def _render_triage_review_table(review: TriageReview) -> None:
    table = Table(title="Human Triage Review")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Finding ID", review.canonical_finding_id)
    table.add_row("Review status", review.review_status)
    table.add_row("Reviewer", review.reviewer)
    table.add_row("Reviewed at", review.reviewed_at)
    table.add_row("Rationale", review.rationale)
    if review.impact_assessment:
        table.add_row("Impact assessment", review.impact_assessment)
    if review.recommended_action:
        table.add_row("Recommended action", review.recommended_action)
    console.print(table)


def _render_report_draft_table(result: ReportDraftResult) -> None:
    draft = result.report_draft
    summary = Table(title="Report Draft Result")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Draft ID", draft.report_draft_id)
    summary.add_row("Finding ID", draft.canonical_finding_id)
    summary.add_row("Human review status", draft.human_review_status)
    summary.add_row("Validation status", draft.validation_status)
    summary.add_row("Submission allowed", str(draft.submission_allowed))
    summary.add_row("Active validation used", str(draft.active_validation_used))
    summary.add_row("Live LLM provider used", str(draft.live_llm_provider_used))
    console.print(summary)
    console.print(draft.content_markdown)
    for note in result.notes:
        console.print(f"- {note}")


def _render_report_draft_summaries_table(drafts) -> None:
    table = Table(title="Stored Report Drafts")
    table.add_column("Draft ID")
    table.add_column("Finding ID")
    table.add_column("Severity")
    table.add_column("Confidence")
    table.add_column("Validation")
    table.add_column("Submission Allowed")
    table.add_column("Title")
    for draft in drafts:
        table.add_row(
            draft.report_draft_id,
            draft.canonical_finding_id,
            draft.severity,
            draft.confidence,
            draft.validation_status,
            str(draft.submission_allowed),
            draft.title,
        )
    console.print(table)


def _render_policy_summary_table(summary: PolicyDocumentSummary) -> None:
    table = Table(title="Local Policy Summary")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Source", summary.source_path)
    table.add_row("Lines", str(summary.line_count))
    table.add_row("Bytes", str(summary.byte_count))
    table.add_row("Redactions", str(summary.redaction_count))
    table.add_row("Scope expansion allowed", str(summary.scope_expansion_allowed))
    table.add_row("Network used", str(summary.network_used))
    console.print(table)

    signals = Table(title="Policy Signals (Advisory Only)")
    signals.add_column("Kind")
    signals.add_column("Line")
    signals.add_column("Text")
    for signal in summary.signals:
        signals.add_row(signal.kind, str(signal.line_number), signal.text)
    console.print(signals)

    for note in summary.notes:
        console.print(f"- {note}")


def _render_mcp_servers_table() -> None:
    table = Table(title="MCP Server Registry")
    table.add_column("Server")
    table.add_column("Status")
    table.add_column("Transport")
    table.add_column("Network")
    table.add_column("Live Process")
    for server in list_mcp_servers():
        table.add_row(
            server.server_id,
            server.status,
            server.transport,
            str(server.network_allowed),
            str(server.live_process_allowed),
        )
    console.print(table)


def _render_mcp_tools_table() -> None:
    table = Table(title="MCP Tool Allowlist")
    table.add_column("Tool")
    table.add_column("Server")
    table.add_column("Safety")
    table.add_column("Network Required")
    table.add_column("Report Submission")
    for tool in list_mcp_tools():
        table.add_row(
            tool.tool_id,
            tool.server_id,
            tool.safety_level,
            str(tool.network_required),
            str(tool.report_submission_allowed),
        )
    console.print(table)


def _render_mcp_invocation_table(result: McpToolInvocationResult) -> None:
    table = Table(title="MCP Fixture Invocation Result")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Invocation ID", result.invocation_id)
    table.add_row("Tool", result.tool_id)
    table.add_row("Server", result.server_id)
    table.add_row("Repository", result.repository)
    table.add_row("Live MCP server used", str(result.live_mcp_server_used))
    table.add_row("Network used", str(result.network_used))
    table.add_row("Report submission used", str(result.report_submission_used))
    console.print(table)
    _render_policy_summary_table(result.policy_summary)
    for note in result.notes:
        console.print(f"- {note}")


def _render_browser_policy_ingestion_table(result: BrowserPolicyIngestionResult) -> None:
    table = Table(title="Browser Policy Ingestion Result")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Ingestion ID", result.ingestion_id)
    table.add_row("Repository", result.repository)
    table.add_row("Live browser used", str(result.live_browser_used))
    table.add_row("Network used", str(result.network_used))
    table.add_row("Live target contact", str(result.live_target_contact_used))
    table.add_row("Form submission used", str(result.form_submission_used))
    table.add_row("Report submission used", str(result.report_submission_used))
    console.print(table)

    plan = result.workflow_plan
    plan_table = Table(title="Browser Workflow Plan")
    plan_table.add_column("Field")
    plan_table.add_column("Value")
    plan_table.add_row("Workflow", plan.workflow)
    plan_table.add_row("Required action", plan.requires_scope_action)
    plan_table.add_row("Live browser allowed", str(plan.live_browser_allowed))
    plan_table.add_row("Network allowed", str(plan.network_allowed))
    plan_table.add_row("Scope expansion allowed", str(plan.scope_expansion_allowed))
    console.print(plan_table)

    _render_policy_summary_table(result.policy_summary)
    for note in result.notes:
        console.print(f"- {note}")


def _render_release_checklist_table(result: ReleaseChecklistResult) -> None:
    table = Table(title=result.title)
    table.add_column("Item")
    table.add_column("Category")
    table.add_column("Commit")
    table.add_column("External Release")
    table.add_column("Title")
    for item in result.items:
        table.add_row(
            item.item_id,
            item.category,
            str(item.required_for_commit),
            str(item.required_for_external_release),
            item.title,
        )
    console.print(table)
    for note in result.notes:
        console.print(f"- {note}")


def _render_release_verification_table(result: ReleaseVerificationResult) -> None:
    summary = Table(title="Release Verification Summary")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Repository root", result.repository_root)
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for external release", str(result.ready_for_external_release))
    summary.add_row("External CI executed", str(result.external_ci_executed))
    console.print(summary)

    checks = Table(title="Release Checks")
    checks.add_column("Check")
    checks.add_column("Category")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.category, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_release_rollback_plan_table(plan: ReleaseRollbackPlan) -> None:
    summary = Table(title="Phase 9 Rollback Plan")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Rollback target", plan.rollback_target)
    summary.add_row("Rollback ready", str(plan.rollback_ready))
    summary.add_row("External resources created", str(plan.external_resources_created))
    console.print(summary)

    steps = Table(title="Rollback Steps")
    steps.add_column("Order")
    steps.add_column("Step")
    for index, step in enumerate(plan.steps, start=1):
        steps.add_row(str(index), step)
    console.print(steps)
    for note in plan.notes:
        console.print(f"- {note}")


def _render_hardening_checklist_table(result: HardeningChecklistResult) -> None:
    table = Table(title=result.title)
    table.add_column("Item")
    table.add_column("Category")
    table.add_column("Commit")
    table.add_column("Production")
    table.add_column("Title")
    for item in result.items:
        table.add_row(
            item.item_id,
            item.category,
            str(item.required_for_commit),
            str(item.required_for_production),
            item.title,
        )
    console.print(table)
    for note in result.notes:
        console.print(f"- {note}")


def _render_hardening_verification_table(result: HardeningVerificationResult) -> None:
    summary = Table(title="Phase 10 Hardening Verification Summary")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Repository root", result.repository_root)
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for production", str(result.ready_for_production))
    summary.add_row("External validation executed", str(result.external_validation_executed))
    console.print(summary)

    checks = Table(title="Hardening Checks")
    checks.add_column("Check")
    checks.add_column("Category")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.category, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_redaction_corpus_table(result: RedactionCorpusResult) -> None:
    table = Table(title="Phase 10 Redaction Corpus")
    table.add_column("Case")
    table.add_column("Passed")
    table.add_column("Redactions")
    table.add_column("Secret Types")
    for case in result.case_results:
        table.add_row(
            case.case_id,
            str(case.passed),
            str(case.redaction_count),
            ", ".join(case.detected_secret_types),
        )
    console.print(table)
    for note in result.notes:
        console.print(f"- {note}")


def _render_prompt_safety_corpus_table(result: PromptSafetyCorpusResult) -> None:
    table = Table(title="Phase 10 Prompt-Safety Corpus")
    table.add_column("Case")
    table.add_column("Passed")
    table.add_column("Signals")
    table.add_column("Redactions")
    table.add_column("Detected Signal IDs")
    for case in result.case_results:
        table.add_row(
            case.case_id,
            str(case.passed),
            str(case.signal_count),
            str(case.redaction_count),
            ", ".join(case.detected_signal_ids),
        )
    console.print(table)
    for note in result.notes:
        console.print(f"- {note}")


def _render_external_validation_plan_table(plan: ExternalValidationPlan) -> None:
    table = Table(title="Phase 10 External Validation Plan")
    table.add_column("Task")
    table.add_column("Category")
    table.add_column("Risk")
    table.add_column("Title")
    for task in plan.tasks:
        table.add_row(task.task_id, task.category, task.risk_level, task.title)
    console.print(table)
    for note in plan.notes:
        console.print(f"- {note}")


def _render_handoff_plan_table(plan: CodexHandoffPlan) -> None:
    table = Table(title="Phase 11 Codex Handoff Plan")
    table.add_column("Task ID")
    table.add_column("Category")
    table.add_column("Risk")
    table.add_column("Title")
    for task in plan.tasks:
        table.add_row(task.task_id, task.category, task.risk_level, task.title)
    console.print(table)
    console.print(f"ready_for_codex={plan.ready_for_codex}")
    console.print(f"ready_for_production={plan.ready_for_production}")
    for note in plan.notes:
        console.print(f"- {note}")


def _render_evidence_template_table(template: EvidenceTemplate) -> None:
    table = Table(title="Phase 11 Evidence Template")
    table.add_column("Artifact ID")
    table.add_column("Producer")
    table.add_column("Filename")
    for artifact in template.artifacts:
        table.add_row(artifact.artifact_id, artifact.producer_task_id, artifact.filename)
    console.print(table)
    console.print(f"artifact_count={template.artifact_count}")
    for note in template.notes:
        console.print(f"- {note}")


def _render_handoff_export_table(result: HandoffExportResult) -> None:
    table = Table(title="Phase 11 Handoff Export")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Output directory", result.output_directory)
    table.add_row("Task count", str(result.task_count))
    table.add_row("Artifact count", str(result.artifact_count))
    table.add_row("Ready for Codex", str(result.ready_for_codex))
    table.add_row("Ready for production", str(result.ready_for_production))
    console.print(table)
    files = Table(title="Written Files")
    files.add_column("Path")
    for filename in result.written_files:
        files.add_row(filename)
    console.print(files)
    for note in result.notes:
        console.print(f"- {note}")


def _render_handoff_verification_table(result: HandoffVerificationResult) -> None:
    summary = Table(title="Phase 11 Handoff Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_evidence_ledger_table(result: ValidationEvidenceLedger) -> None:
    summary = Table(title="Phase 12 Validation Evidence Ledger")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Evidence directory", result.evidence_directory)
    summary.add_row("Artifacts", str(result.artifact_count))
    summary.add_row("Present", str(result.present_count))
    summary.add_row("Missing", str(result.missing_count))
    summary.add_row("Ready for evidence review", str(result.ready_for_evidence_review))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    artifacts = Table(title="Artifacts")
    artifacts.add_column("Artifact ID")
    artifacts.add_column("Status")
    artifacts.add_column("SHA-256")
    artifacts.add_column("Gaps")
    for artifact in result.artifacts:
        artifacts.add_row(
            artifact.artifact_id,
            artifact.status,
            artifact.sha256 or "missing",
            ", ".join(artifact.validates_gap_ids),
        )
    console.print(artifacts)
    for note in result.notes:
        console.print(f"- {note}")


def _render_gap_closure_readiness_table(result: GapClosureReadinessResult) -> None:
    summary = Table(title="Phase 12 Gap Closure Readiness")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Gaps", str(result.gap_count))
    summary.add_row("Gaps with any evidence", str(result.gaps_with_any_evidence))
    summary.add_row("Gaps with all expected evidence", str(result.gaps_with_all_expected_evidence))
    summary.add_row("Gaps ready for human review", str(result.gaps_ready_for_human_review))
    summary.add_row("Gaps ready for closure", str(result.gaps_ready_for_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    gaps = Table(title="Gap Status")
    gaps.add_column("Gap")
    gaps.add_column("Present")
    gaps.add_column("Missing")
    gaps.add_column("Can close")
    gaps.add_column("Blocker")
    for status in result.gap_statuses:
        gaps.add_row(
            status.gap_id,
            str(len(status.present_artifact_ids)),
            str(len(status.missing_artifact_ids)),
            str(status.can_close_gap),
            status.closure_blocker,
        )
    console.print(gaps)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_evidence_export_table(result: ValidationEvidenceExportResult) -> None:
    table = Table(title="Phase 12 Validation Evidence Export")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Output directory", result.output_directory)
    table.add_row("Artifacts", str(result.artifact_count))
    table.add_row("Present", str(result.present_count))
    table.add_row("Missing", str(result.missing_count))
    table.add_row("Gaps", str(result.gap_count))
    table.add_row("Ready for evidence review", str(result.ready_for_evidence_review))
    table.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    table.add_row("Ready for production", str(result.ready_for_production))
    console.print(table)
    files = Table(title="Written Files")
    files.add_column("Path")
    for filename in result.written_files:
        files.add_row(filename)
    console.print(files)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_evidence_verification_table(
    result: ValidationEvidenceVerificationResult,
) -> None:
    summary = Table(title="Phase 12 Validation Evidence Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_evidence_review_template_table(result: EvidenceReviewTemplateResult) -> None:
    summary = Table(title="Phase 13 Evidence Review Template")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Review file", result.review_file)
    summary.add_row("Decision count", str(result.decision_count))
    summary.add_row("Ready for human review", str(result.ready_for_human_review))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    for note in result.notes:
        console.print(f"- {note}")


def _render_evidence_review_status_table(result: EvidenceReviewStatusResult) -> None:
    summary = Table(title="Phase 13 Evidence Review Status")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Artifacts", str(result.artifact_count))
    summary.add_row("Present", str(result.present_count))
    summary.add_row("Missing", str(result.missing_count))
    summary.add_row("Reviewed", str(result.reviewed_count))
    summary.add_row("Approved", str(result.approved_count))
    summary.add_row("Accepted for proposal", str(result.accepted_for_closure_proposal_count))
    summary.add_row("Ready for human gap update", str(result.ready_for_human_gap_update))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    console.print(summary)

    artifacts = Table(title="Artifact Review States")
    artifacts.add_column("Artifact ID")
    artifacts.add_column("Evidence")
    artifacts.add_column("Decision")
    artifacts.add_column("Accepted")
    artifacts.add_column("Blockers")
    for artifact in result.artifacts[:20]:
        artifacts.add_row(
            artifact.artifact_id,
            artifact.evidence_status,
            artifact.review_decision,
            str(artifact.accepted_for_closure_proposal),
            "; ".join(artifact.blockers) or "none",
        )
    console.print(artifacts)
    for note in result.notes:
        console.print(f"- {note}")


def _render_gap_closure_proposals_table(result: GapClosureProposalResult) -> None:
    summary = Table(title="Phase 13 Gap Closure Proposals")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Proposals", str(result.proposal_count))
    summary.add_row("Ready for human update", str(result.proposals_ready_for_human_update))
    summary.add_row("Blocked", str(result.proposals_blocked))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    proposals = Table(title="Gap Proposal States")
    proposals.add_column("Gap ID")
    proposals.add_column("Status")
    proposals.add_column("Approved")
    proposals.add_column("Missing")
    proposals.add_column("Unreviewed")
    for proposal in result.proposals:
        proposals.add_row(
            proposal.gap_id,
            proposal.proposal_status,
            str(len(proposal.approved_artifact_ids)),
            str(len(proposal.missing_artifact_ids)),
            str(len(proposal.unreviewed_artifact_ids)),
        )
    console.print(proposals)
    for note in result.notes:
        console.print(f"- {note}")


def _render_evidence_review_export_table(result: EvidenceReviewExportResult) -> None:
    summary = Table(title="Phase 13 Evidence Review Export")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Output directory", result.output_directory)
    summary.add_row("Artifact count", str(result.artifact_count))
    summary.add_row("Proposal count", str(result.proposal_count))
    summary.add_row(
        "Proposals ready for human update", str(result.proposals_ready_for_human_update)
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    console.print(summary)
    for written in result.written_files:
        console.print(f"- wrote {written}")
    for note in result.notes:
        console.print(f"- {note}")


def _render_evidence_review_verification_table(result: EvidenceReviewVerificationResult) -> None:
    summary = Table(title="Phase 13 Evidence Review Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_gap_tracker_audit_table(result: GapTrackerAuditResult) -> None:
    summary = Table(title="Phase 14 Gap Tracker Audit")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Entries", str(result.entry_count))
    summary.add_row("Duplicate IDs", str(len(result.duplicate_gap_ids)))
    summary.add_row("Malformed IDs", str(len(result.malformed_entry_ids)))
    summary.add_row("Missing required fields", str(result.missing_required_field_count))
    summary.add_row("Ready for Codex backlog", str(result.ready_for_codex_backlog))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    entries = Table(title="Gap Entries")
    entries.add_column("Gap ID")
    entries.add_column("Risk")
    entries.add_column("Subsystem")
    entries.add_column("Missing fields")
    for entry in result.entries[:30]:
        entries.add_row(
            entry.gap_id,
            entry.risk_level,
            entry.subsystem_association or "unknown",
            ", ".join(entry.missing_required_fields) or "none",
        )
    console.print(entries)
    for note in result.notes:
        console.print(f"- {note}")


def _render_codex_gap_backlog_table(result: CodexBacklogResult) -> None:
    summary = Table(title="Phase 14 Codex Gap Backlog")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Items", str(result.item_count))
    summary.add_row("High/Critical", str(result.high_risk_count))
    summary.add_row("Medium", str(result.medium_risk_count))
    summary.add_row("Low", str(result.low_risk_count))
    summary.add_row("Unknown", str(result.unknown_risk_count))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    items = Table(title="Top Backlog Items")
    items.add_column("Rank")
    items.add_column("Task")
    items.add_column("Risk")
    items.add_column("Agent")
    items.add_column("Subsystem")
    for item in result.items[:30]:
        items.add_row(
            str(item.priority_rank),
            item.task_id,
            item.risk_level,
            item.recommended_future_agent_type,
            item.subsystem_association,
        )
    console.print(items)
    for note in result.notes:
        console.print(f"- {note}")


def _render_gap_tracker_export_table(result: GapTrackerExportResult) -> None:
    summary = Table(title="Phase 14 Gap Tracker Export")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Output directory", result.output_directory)
    summary.add_row("Gap entries", str(result.gap_entry_count))
    summary.add_row("Backlog items", str(result.backlog_item_count))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    for written in result.written_files:
        console.print(f"- wrote {written}")
    for note in result.notes:
        console.print(f"- {note}")


def _render_gap_tracker_verification_table(result: GapTrackerVerificationResult) -> None:
    summary = Table(title="Phase 14 Gap Tracker Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_runbook_table(result: ExternalValidationRunbook) -> None:
    summary = Table(title="Phase 15 External Validation Runbook")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Steps", str(result.step_count))
    summary.add_row("High/Critical", str(result.critical_or_high_count))
    summary.add_row("Medium", str(result.medium_count))
    summary.add_row("Ready for Codex execution", str(result.ready_for_codex_execution))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    steps = Table(title="Top Runbook Steps")
    steps.add_column("Rank")
    steps.add_column("Step")
    steps.add_column("Gap")
    steps.add_column("Risk")
    steps.add_column("Agent")
    for step in result.steps[:30]:
        steps.add_row(
            str(step.priority_rank),
            step.step_id,
            step.gap_id,
            step.risk_level,
            step.recommended_future_agent_type,
        )
    console.print(steps)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_run_journal_template_table(result: ValidationRunJournalFile) -> None:
    summary = Table(title="Phase 15 Execution Journal Template")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Entries", str(len(result.entries)))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_run_journal_status_table(result: ValidationRunJournalStatusResult) -> None:
    summary = Table(title="Phase 15 Execution Journal Status")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Steps", str(result.step_count))
    summary.add_row("Passed with metadata", str(result.passed_with_metadata_count))
    summary.add_row("Failed or blocked", str(result.failed_or_blocked_count))
    summary.add_row("Missing journal", str(result.missing_journal_count))
    summary.add_row("Ready for evidence ledger", str(result.ready_for_evidence_ledger))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    statuses = Table(title="Runbook Step Status")
    statuses.add_column("Step")
    statuses.add_column("Gap")
    statuses.add_column("Status")
    statuses.add_column("Accepted")
    statuses.add_column("Blockers")
    for status in result.step_statuses[:30]:
        statuses.add_row(
            status.step_id,
            status.gap_id,
            status.status,
            str(status.accepted_for_evidence_ledger),
            "; ".join(status.blockers) or "none",
        )
    console.print(statuses)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_runbook_export_table(result: ValidationRunbookExportResult) -> None:
    summary = Table(title="Phase 15 Runbook Export")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Output directory", result.output_directory)
    summary.add_row("Steps", str(result.step_count))
    summary.add_row("Ready for Codex execution", str(result.ready_for_codex_execution))
    summary.add_row("Ready for evidence ledger", str(result.ready_for_evidence_ledger))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    for written in result.written_files:
        console.print(f"- wrote {written}")
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_runbook_verification_table(
    result: ValidationRunbookVerificationResult,
) -> None:
    summary = Table(title="Phase 15 Runbook Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for evidence ledger", str(result.ready_for_evidence_ledger))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_baseline_manifest_table(result: ValidationBaselineManifest) -> None:
    summary = Table(title="Phase 16 Validation Baseline Manifest")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Files", str(result.file_count))
    summary.add_row("Markdown files", str(result.markdown_file_count))
    summary.add_row("Python files", str(result.python_file_count))
    summary.add_row("Governance files", str(result.governance_file_count))
    summary.add_row(
        "Ready for external validation reference",
        str(result.ready_for_external_validation_reference),
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    files = Table(title="Baseline File Samples")
    files.add_column("Path")
    files.add_column("Category")
    files.add_column("SHA-256")
    for record in result.files[:30]:
        files.add_row(record.path, record.category, record.sha256[:16])
    console.print(files)
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_baseline_export_table(result: ValidationBaselineExportResult) -> None:
    summary = Table(title="Phase 16 Validation Baseline Export")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Output directory", result.output_directory)
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Files", str(result.file_count))
    summary.add_row(
        "Ready for external validation reference",
        str(result.ready_for_external_validation_reference),
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    for written in result.written_files:
        console.print(f"- wrote {written}")
    for note in result.notes:
        console.print(f"- {note}")


def _render_validation_baseline_verification_table(
    result: ValidationBaselineVerificationResult,
) -> None:
    summary = Table(title="Phase 16 Validation Baseline Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row(
        "Ready for external validation reference",
        str(result.ready_for_external_validation_reference),
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_readiness_attestation_template_table(
    result: ReadinessAttestationTemplateResult,
) -> None:
    summary = Table(title="Phase 17 Readiness Attestation Template")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Attestation file", result.attestation_file)
    summary.add_row("Candidate gap IDs", str(len(result.candidate_gap_ids)))
    summary.add_row("Ready for human attestation", str(result.ready_for_human_attestation))
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    gaps = Table(title="Candidate Gaps")
    gaps.add_column("Gap ID")
    for gap_id in result.candidate_gap_ids[:30]:
        gaps.add_row(gap_id)
    console.print(gaps)
    for note in result.notes:
        console.print(f"- {note}")


def _render_closure_gate_status_table(result: ClosureGateStatusResult) -> None:
    summary = Table(title="Phase 17 Closure Gate Status")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Attestations", str(result.attestation_count))
    summary.add_row("Accepted attestations", str(result.accepted_attestation_count))
    summary.add_row("Candidate gaps", str(len(result.candidate_gap_ids)))
    summary.add_row("Evidence artifacts present", str(result.present_evidence_artifact_count))
    summary.add_row("Accepted review artifacts", str(result.accepted_review_artifact_count))
    summary.add_row("Journal steps with metadata", str(result.journal_steps_with_metadata_count))
    summary.add_row(
        "Ready for human gap update review", str(result.ready_for_human_gap_update_review)
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    attestations = Table(title="Attestation States")
    attestations.add_column("Attestation")
    attestations.add_column("Decision")
    attestations.add_column("Status")
    attestations.add_column("Accepted Gaps")
    attestations.add_column("Blockers")
    for status in result.attestation_statuses[:30]:
        attestations.add_row(
            status.attestation_id,
            status.decision,
            status.status,
            ", ".join(status.accepted_gap_ids) or "none",
            "; ".join(status.blockers) or "none",
        )
    console.print(attestations)
    for note in result.notes:
        console.print(f"- {note}")


def _render_closure_gate_export_table(result: ClosureGateExportResult) -> None:
    summary = Table(title="Phase 17 Closure Gate Export")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Output directory", result.output_directory)
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Attestations", str(result.attestation_count))
    summary.add_row("Candidate gaps", str(result.candidate_gap_count))
    summary.add_row(
        "Ready for human gap update review", str(result.ready_for_human_gap_update_review)
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)
    for written in result.written_files:
        console.print(f"- wrote {written}")
    for note in result.notes:
        console.print(f"- {note}")


def _render_closure_gate_verification_table(result: ClosureGateVerificationResult) -> None:
    summary = Table(title="Phase 17 Closure Gate Verification")
    summary.add_column("Metric")
    summary.add_column("Value")
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row(
        "Ready for human gap update review", str(result.ready_for_human_gap_update_review)
    )
    summary.add_row("Ready for gap closure", str(result.ready_for_gap_closure))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _render_readiness_dashboard_table(result: ReadinessDashboard) -> None:
    summary = Table(title="Phase 18 Readiness Dashboard")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Production readiness estimate", f"{result.production_readiness_percent}%")
    summary.add_row("Gap entries", str(result.gap_entry_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for external executor", str(result.ready_for_external_executor))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    subsystems = Table(title="Governance Subsystems")
    subsystems.add_column("Subsystem")
    subsystems.add_column("Phase")
    subsystems.add_column("Commit")
    subsystems.add_column("Codex")
    subsystems.add_column("Production")
    subsystems.add_column("Passed/Failed/Deferred")
    for status in result.subsystem_statuses:
        subsystems.add_row(
            status.subsystem_id,
            status.source_phase,
            str(status.ready_for_commit),
            str(status.ready_for_codex),
            str(status.ready_for_production),
            f"{status.passed_count}/{status.failed_count}/{status.deferred_count}",
        )
    console.print(subsystems)

    for note in result.notes:
        console.print(f"- {note}")


def _render_external_executor_index_table(result: ExternalExecutorIndex) -> None:
    summary = Table(title="Phase 18 External Executor Index")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Command count", str(result.command_count))
    summary.add_row("Ready for external executor", str(result.ready_for_external_executor))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    commands = Table(title="Ordered Commands")
    commands.add_column("Order")
    commands.add_column("Command ID")
    commands.add_column("Title")
    commands.add_column("Output")
    for command in result.commands:
        commands.add_row(
            str(command.order), command.command_id, command.title, command.output_path or ""
        )
    console.print(commands)
    for note in result.notes:
        console.print(f"- {note}")


def _render_readiness_dashboard_export_table(result: ReadinessDashboardExportResult) -> None:
    table = Table(title="Phase 18 Readiness Dashboard Export")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Output", result.output_directory)
    table.add_row("Baseline ID", result.baseline_id)
    table.add_row("Readiness estimate", f"{result.production_readiness_percent}%")
    table.add_row("Subsystems", str(result.subsystem_count))
    table.add_row("Commands", str(result.command_count))
    table.add_row("Ready for external executor", str(result.ready_for_external_executor))
    table.add_row("Ready for production", str(result.ready_for_production))
    console.print(table)
    for note in result.notes:
        console.print(f"- {note}")


def _render_readiness_dashboard_verification_table(
    result: ReadinessDashboardVerificationResult,
) -> None:
    summary = Table(title="Phase 18 Readiness Dashboard Verification")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Baseline ID", result.baseline_id)
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for external executor", str(result.ready_for_external_executor))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


def _validate_output_format(output: str) -> str:
    normalized = output.strip().lower()
    if normalized not in {"table", "json"}:
        console.print("DENY: unsupported output format")
        console.print("- expected one of: table, json")
        raise typer.Exit(code=2)
    return normalized


@app.command()
def doctor() -> None:
    """Report local environment and Phase 17 capability state."""

    config = load_config()
    table = Table(title="BountyClaw Doctor")
    table.add_column("Check")
    table.add_column("Status")
    table.add_row("Version", __version__)
    table.add_row(
        "Roadmap phase", "Phase 19: Local Quality/Security Gate Execution and Remediation"
    )
    table.add_row("CLI", "available")
    table.add_row("Scope gate", "available")
    table.add_row("Repository intake", "available: read-only metadata")
    table.add_row("Scan planning", "available: deterministic plan only")
    table.add_row(
        "Local scanner execution",
        "available: built-in static code scanner and dependency manifest scanner; explicit flag required",
    )
    table.add_row(
        "External scanner execution", "framework only; real scanner binaries not validated"
    )
    table.add_row(
        "Findings normalization", "available: deterministic canonical schema and deduplication"
    )
    table.add_row("Evidence store", "available: local SQLite with redaction-before-write controls")
    table.add_row("Network actions", "disabled")
    table.add_row(
        "Model router", "available: provider-neutral metadata and deterministic mock provider"
    )
    table.add_row("Live LLM providers", "disabled")
    table.add_row("Prompt safety", "available: redaction and untrusted-content isolation")
    table.add_row("Report drafting", "available: human-review-only drafts; no submission")
    table.add_row("MCP tools", "available: fixture-only local policy tool; live servers disabled")
    table.add_row(
        "Headless browser", "available: fixture-only local policy ingestion; live browser disabled"
    )
    table.add_row("Memory store", "available: explicit approval and redaction checks required")
    table.add_row("Skill templates", "available: non-executing proposals only")
    table.add_row(
        "Release controls", "available: local verification, CI definitions, rollback plan"
    )
    table.add_row(
        "Hardening controls",
        "available: local redaction/prompt-safety corpus and external validation plan",
    )
    table.add_row("Handoff package", "available: Codex/local/CI evidence plan and export")
    table.add_row(
        "Validation evidence ledger",
        "available: hash-only future artifact inventory; no gap closure",
    )
    table.add_row(
        "Evidence review workflow",
        "available: metadata-only review templates and closure proposals; no auto-closure",
    )
    table.add_row(
        "Gap tracker governance",
        "available: metadata-only audit and Codex backlog export; no auto-closure",
    )
    table.add_row(
        "Validation baseline", "available: hash-only source snapshot binding; no validation claim"
    )
    table.add_row(
        "Closure gate", "available: metadata-only readiness attestations; no auto-closure"
    )
    table.add_row(
        "Readiness dashboard", "available: metadata-only external executor index; no auto-closure"
    )
    table.add_row("External CI execution", "not executed in ChatGPT Project Mode")
    table.add_row("Audit log default", str(config.audit_log))
    console.print(table)


@scope_app.command("validate")
def validate_scope(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
) -> None:
    """Validate a scope manifest without performing any target action."""

    try:
        loaded_scope = load_scope_manifest(manifest)
    except Exception as exc:  # noqa: BLE001 - CLI must show user-facing deny reason.
        console.print("DENY: scope manifest is invalid")
        console.print(f"- {exc}")
        raise typer.Exit(code=2) from exc

    console.print("ALLOW: scope manifest is valid")
    console.print(f"- program: {loaded_scope.manifest.program.name}")
    console.print(f"- source: {loaded_scope.source_path}")


@scope_app.command("check")
def check_scope(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    action: Annotated[str, typer.Option("--action", "-a", help="Requested action.")],
    repo: Annotated[
        Path | None,
        typer.Option("--repo", help="Local repository target for local actions."),
    ] = None,
    domain: Annotated[
        str | None,
        typer.Option(
            "--domain", help="Domain target. Phase 3 still denies network/domain actions."
        ),
    ] = None,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Evaluate a requested action against the scope gate."""

    if repo is not None and domain is not None:
        console.print("DENY: provide exactly one target type")
        console.print("- --repo and --domain cannot be used together")
        raise typer.Exit(code=2)

    target: Target | None
    if repo is not None:
        target = Target(kind=TargetKind.LOCAL_REPO, value=str(repo))
    elif domain is not None:
        target = Target(kind=TargetKind.DOMAIN, value=domain)
    else:
        target = None

    try:
        loaded_scope = load_scope_manifest(manifest)
        decision = ScopeGate(loaded_scope).evaluate(action=action, target=target)
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: scope manifest could not be loaded")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="scope.check",
            action=action,
            decision="deny",
            target_kind=target.kind.value if target else None,
            target=target.value if target else None,
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    label = "ALLOW" if decision.allowed else "DENY"
    _print_decision(f"{label}: {decision.action}", decision.reasons)

    _write_audit(
        audit_log,
        event_type="scope.check",
        action=decision.action,
        decision=decision.decision,
        target_kind=decision.target_kind.value if decision.target_kind else None,
        target=decision.target,
        reasons=decision.reasons,
    )

    if not decision.allowed:
        raise typer.Exit(code=2)


@repo_app.command("inspect")
def inspect_repo(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository to inspect read-only."),
    ],
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Inspect an authorized local repository using metadata-only read access."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        fingerprint = inspect_authorized_repository(loaded_scope, repo)
    except RepositoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="repo.inspect",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: repository intake failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="repo.inspect",
            action="repo.read",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="repo.inspect",
        action="repo.read",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["repository metadata inspected read-only after scope approval"],
    )
    if output_format == "json":
        console.print_json(data=fingerprint.model_dump(mode="json"))
    else:
        _render_fingerprint_table(fingerprint)


@repo_app.command("plan")
def plan_repo(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository to plan for."),
    ],
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Generate a deterministic scan plan without executing scanners."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        plan = plan_authorized_repository_scan(loaded_scope, repo)
    except RepositoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="repo.plan",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: repository scan planning failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="repo.plan",
            action="scan.local_static",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="repo.plan",
        action="scan.local_static",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["deterministic scan plan generated; scanners were not executed"],
    )
    if output_format == "json":
        console.print_json(data=plan.model_dump(mode="json"))
    else:
        _render_scan_plan_table(plan)


@scan_app.command("repo")
def scan_repo(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option(
            "--repo", help="Allowlisted local repository to scan with local static adapters."
        ),
    ],
    scanner: Annotated[
        str | None,
        typer.Option(
            "--scanner",
            help="Allowlisted scanner adapter ID. Omit to run all allowlisted adapters.",
        ),
    ] = None,
    enable_local_scanner: Annotated[
        bool,
        typer.Option(
            "--enable-local-scanner",
            help="Explicitly enable local scanner execution for this command.",
        ),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Run scope-gated local static scanner adapters against an authorized repository."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = scan_authorized_repository(
            loaded_scope,
            repo,
            scanner_ids=[scanner] if scanner else None,
            local_scanner_enabled=enable_local_scanner,
        )
    except ScannerFeatureGateError as exc:
        console.print("DENY: local scanner execution is not enabled")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="scan.repo",
            action="scan.local_static",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except ScannerAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="scan.repo",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except ScannerSelectionError as exc:
        console.print("DENY: scanner adapter selection failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="scan.repo",
            action="scan.local_static",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: local scanner execution failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="scan.repo",
            action="scan.local_static",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="scan.repo",
        action="scan.local_static",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["scope-approved local static scanner execution completed"],
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_scanner_result_table(result)


@findings_app.command("collect")
def collect_findings(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option(
            "--repo", help="Allowlisted local repository to scan and persist findings for."
        ),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store",
            help="SQLite evidence-store path. Must be outside the target repository.",
        ),
    ] = Path(".bountyclaw/evidence.sqlite"),
    scanner: Annotated[
        str | None,
        typer.Option(
            "--scanner",
            help="Allowlisted scanner adapter ID. Omit to run all allowlisted adapters.",
        ),
    ] = None,
    enable_local_scanner: Annotated[
        bool,
        typer.Option(
            "--enable-local-scanner",
            help="Explicitly enable local scanner execution before findings persistence.",
        ),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Normalize scanner findings and persist redacted evidence locally."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = collect_authorized_findings(
            loaded_scope,
            repo,
            store_path=store,
            scanner_ids=[scanner] if scanner else None,
            local_scanner_enabled=enable_local_scanner,
        )
    except FindingsAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="findings.collect",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except EvidenceStorePathError as exc:
        console.print("DENY: evidence store path is unsafe")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="findings.collect",
            action="findings.write",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except ScannerFeatureGateError as exc:
        console.print("DENY: local scanner execution is not enabled")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="findings.collect",
            action="scan.local_static",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except ScannerAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="findings.collect",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except ScannerSelectionError as exc:
        console.print("DENY: scanner adapter selection failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="findings.collect",
            action="scan.local_static",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: findings collection failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="findings.collect",
            action="findings.write",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="findings.collect",
        action="findings.write",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["canonical findings and redacted evidence persisted after scope approval"],
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_findings_collection_table(result)


@findings_app.command("list")
def list_findings(
    store: Annotated[
        Path,
        typer.Option("--store", help="SQLite evidence-store path."),
    ] = Path(".bountyclaw/evidence.sqlite"),
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum findings to show.", min=1, max=1000),
    ] = 100,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List redacted canonical findings from a local evidence store."""

    output_format = _validate_output_format("json" if json_output else output)
    findings = EvidenceStore(store).list_findings(limit=limit)
    if output_format == "json":
        console.print_json(data=[finding.model_dump(mode="json") for finding in findings])
    else:
        _render_stored_findings_table(findings)


@model_app.command("providers")
def model_providers(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List provider metadata. Phase 5 executable provider is mock.local only."""

    output_format = _validate_output_format("json" if json_output else output)
    providers = list(provider_catalog().values())
    if output_format == "json":
        console.print_json(data=[provider.model_dump(mode="json") for provider in providers])
        return

    table = Table(title="Model Provider Catalog")
    table.add_column("Provider")
    table.add_column("Default Model")
    table.add_column("Status")
    table.add_column("Live API")
    for provider in providers:
        table.add_row(
            provider.provider_id,
            provider.default_model,
            provider.status,
            str(provider.supports_live_api),
        )
    console.print(table)


@model_app.command("route")
def model_route(
    task: Annotated[
        str,
        typer.Option("--task", help="Model task type. Example: finding_triage."),
    ] = "finding_triage",
    privacy: Annotated[
        str,
        typer.Option("--privacy", help="Privacy sensitivity: low, medium, high, maximum."),
    ] = "high",
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider",
            help="Optional provider ID. Phase 5 executable provider is mock.local only.",
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Route a model task under Phase 5 fail-closed policy without invoking a provider."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        decision = route_model_request(
            ModelRoutingRequest(
                task_type=task,  # type: ignore[arg-type]
                privacy_sensitivity=privacy,  # type: ignore[arg-type]
                requested_provider_id=provider,
            )
        )
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: model routing failed")
        console.print(f"- {exc}")
        raise typer.Exit(code=2) from exc

    if output_format == "json":
        console.print_json(data=decision.model_dump(mode="json"))
        return

    table = Table(title="Model Routing Decision")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Task", decision.task_type)
    table.add_row("Provider", decision.provider_id)
    table.add_row("Model", decision.model_id)
    table.add_row("Live provider allowed", str(decision.live_provider_call_allowed))
    table.add_row("Live provider used", str(decision.live_provider_call_used))
    console.print(table)
    for reason in decision.reasons:
        console.print(f"- {reason}")


@model_app.command("triage")
def model_triage(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the finding."),
    ],
    finding_id: Annotated[
        str,
        typer.Option("--finding-id", help="Canonical finding ID from the evidence store."),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite evidence-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/evidence.sqlite"),
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider",
            help="Optional provider ID. Phase 5 executable provider is mock.local only.",
        ),
    ] = None,
    enable_mock_model: Annotated[
        bool,
        typer.Option(
            "--enable-mock-model",
            help="Explicitly enable deterministic offline mock model invocation.",
        ),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Run scope-gated mocked model triage for one stored canonical finding."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = triage_authorized_finding(
            loaded_scope,
            repo,
            store_path=store,
            finding_id=finding_id,
            provider_id=provider,
            mock_model_enabled=enable_mock_model,
        )
    except ModelFeatureGateError as exc:
        console.print("DENY: mock model execution is not enabled")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="model.triage",
            action="model.triage",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except ModelAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="model.triage",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except (ModelFindingNotFoundError, ModelRoutingError) as exc:
        console.print("DENY: model triage failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="model.triage",
            action="model.triage",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: model triage failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="model.triage",
            action="model.triage",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="model.triage",
        action="model.triage",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["scope-approved mocked model triage completed; no live provider call used"],
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_model_triage_table(result)


@report_app.command("review")
def report_review(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the finding."),
    ],
    finding_id: Annotated[
        str,
        typer.Option("--finding-id", help="Canonical finding ID from the evidence store."),
    ],
    reviewer: Annotated[
        str,
        typer.Option("--reviewer", help="Human reviewer name or handle."),
    ],
    rationale: Annotated[
        str,
        typer.Option("--rationale", help="Human triage rationale. Minimum 12 characters."),
    ],
    status: Annotated[
        str,
        typer.Option(
            "--status",
            help="Review status: needs_review, needs_more_evidence, approved_for_draft, rejected_false_positive.",
        ),
    ] = "approved_for_draft",
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite evidence-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/evidence.sqlite"),
    impact_assessment: Annotated[
        str | None,
        typer.Option("--impact-assessment", help="Optional human impact assessment."),
    ] = None,
    recommended_action: Annotated[
        str | None,
        typer.Option("--recommended-action", help="Optional recommended next action."),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Record human triage state for a stored canonical finding."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        review = record_triage_review(
            loaded_scope,
            repo,
            store_path=store,
            finding_id=finding_id,
            review_status=status,  # type: ignore[arg-type]
            reviewer=reviewer,
            rationale=rationale,
            impact_assessment=impact_assessment,
            recommended_action=recommended_action,
        )
    except ReportAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="report.review",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except ReportFindingNotFoundError as exc:
        console.print("DENY: report review failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="report.review",
            action="triage.review",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: report review failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="report.review",
            action="triage.review",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="report.review",
        action="triage.review",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["scope-approved human triage review state recorded"],
    )
    if output_format == "json":
        console.print_json(data=review.model_dump(mode="json"))
    else:
        _render_triage_review_table(review)


@report_app.command("draft")
def report_draft(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the finding."),
    ],
    finding_id: Annotated[
        str,
        typer.Option("--finding-id", help="Canonical finding ID from the evidence store."),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite evidence-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/evidence.sqlite"),
    include_mock_triage: Annotated[
        bool,
        typer.Option(
            "--include-mock-triage", help="Include Phase 5 mocked model triage as advisory context."
        ),
    ] = False,
    enable_mock_model: Annotated[
        bool,
        typer.Option(
            "--enable-mock-model",
            help="Explicitly enable deterministic offline mock model invocation.",
        ),
    ] = False,
    provider: Annotated[
        str | None,
        typer.Option(
            "--provider", help="Optional provider ID. Executable provider remains mock.local only."
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table, markdown, or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Create a deterministic human-review-only report draft."""

    selected_output = "json" if json_output else output.strip().lower()
    if selected_output not in {"table", "markdown", "json"}:
        console.print("DENY: unsupported output format")
        console.print("- output format must be table, markdown, or json")
        raise typer.Exit(code=2)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = draft_authorized_report(
            loaded_scope,
            repo,
            store_path=store,
            finding_id=finding_id,
            include_mock_triage=include_mock_triage,
            mock_model_enabled=enable_mock_model,
            provider_id=provider,
        )
    except ReportAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="report.draft",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except (
        ReportFindingNotFoundError,
        ReportDraftReadinessError,
        ModelFindingNotFoundError,
        ModelRoutingError,
    ) as exc:
        console.print("DENY: report draft failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="report.draft",
            action="report.draft",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except ModelFeatureGateError as exc:
        console.print("DENY: mock model execution is not enabled")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="report.draft",
            action="model.triage",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: report draft failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="report.draft",
            action="report.draft",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="report.draft",
        action="report.draft",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["scope-approved report draft created; submission remains disabled"],
    )
    if selected_output == "json":
        console.print_json(data=result.model_dump(mode="json"))
    elif selected_output == "markdown":
        console.print(result.report_draft.content_markdown)
    else:
        _render_report_draft_table(result)


@report_app.command("list")
def report_list(
    store: Annotated[
        Path,
        typer.Option("--store", help="SQLite evidence-store path."),
    ] = Path(".bountyclaw/evidence.sqlite"),
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum report drafts to show.", min=1, max=1000),
    ] = 100,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List locally persisted report drafts."""

    output_format = _validate_output_format("json" if json_output else output)
    drafts = ReportStore(store).list_report_drafts(limit=limit)
    if output_format == "json":
        console.print_json(data=[draft.model_dump(mode="json") for draft in drafts])
    else:
        _render_report_draft_summaries_table(drafts)


@mcp_app.command("servers")
def mcp_servers(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List declared MCP server metadata without launching servers."""

    output_format = _validate_output_format("json" if json_output else output)
    servers = list_mcp_servers()
    if output_format == "json":
        console.print_json(data=[server.model_dump(mode="json") for server in servers])
    else:
        _render_mcp_servers_table()


@mcp_app.command("tools")
def mcp_tools(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List allowlisted MCP tool metadata without invoking tools."""

    output_format = _validate_output_format("json" if json_output else output)
    tools = list_mcp_tools()
    if output_format == "json":
        console.print_json(data=[tool.model_dump(mode="json") for tool in tools])
    else:
        _render_mcp_tools_table()


@mcp_app.command("invoke")
def mcp_invoke(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option(
            "--repo", help="Allowlisted local repository associated with the MCP tool call."
        ),
    ],
    tool: Annotated[
        str,
        typer.Option("--tool", help="Allowlisted MCP tool ID."),
    ] = POLICY_LOCAL_FILE_TOOL_ID,
    policy_file: Annotated[
        Path | None,
        typer.Option(
            "--policy-file", help="Optional local policy file. Defaults to program.policy_file."
        ),
    ] = None,
    enable_mcp_fixture: Annotated[
        bool,
        typer.Option(
            "--enable-mcp-fixture",
            help="Explicitly enable the Phase 7 in-process MCP fixture tool.",
        ),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Invoke an allowlisted fixture MCP tool after scope approval."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = invoke_authorized_mcp_tool(
            loaded_scope,
            repo,
            tool_id=tool,
            policy_file=policy_file,
            fixture_tool_enabled=enable_mcp_fixture,
        )
    except McpFeatureGateError as exc:
        console.print("DENY: MCP fixture tool invocation is not enabled")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="mcp.invoke",
            action="mcp.tool.invoke",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except McpAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="mcp.invoke",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except (McpToolSelectionError, PolicyDocumentError) as exc:
        console.print("DENY: MCP fixture tool invocation failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="mcp.invoke",
            action="mcp.tool.invoke",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: MCP fixture tool invocation failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="mcp.invoke",
            action="mcp.tool.invoke",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="mcp.invoke",
        action="mcp.tool.invoke",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=[
            "scope-approved fixture MCP policy tool completed; no live server or network used"
        ],
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_mcp_invocation_table(result)


@browser_app.command("plan")
def browser_plan(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Show the Phase 7 no-network browser workflow plan."""

    output_format = _validate_output_format("json" if json_output else output)
    plan = build_policy_ingestion_plan()
    if output_format == "json":
        console.print_json(data=plan.model_dump(mode="json"))
        return

    table = Table(title="Browser Workflow Plan")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Workflow", plan.workflow)
    table.add_row("Required action", plan.requires_scope_action)
    table.add_row("Live browser allowed", str(plan.live_browser_allowed))
    table.add_row("Network allowed", str(plan.network_allowed))
    table.add_row("Live target contact allowed", str(plan.live_target_contact_allowed))
    table.add_row("Form submission allowed", str(plan.form_submission_allowed))
    table.add_row("Report submission allowed", str(plan.report_submission_allowed))
    console.print(table)
    for note in plan.notes:
        console.print(f"- {note}")


@browser_app.command("policy-ingest")
def browser_policy_ingest(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option(
            "--repo", help="Allowlisted local repository associated with policy ingestion."
        ),
    ],
    policy_file: Annotated[
        Path | None,
        typer.Option(
            "--policy-file", help="Optional local policy file. Defaults to program.policy_file."
        ),
    ] = None,
    enable_browser_fixture: Annotated[
        bool,
        typer.Option(
            "--enable-browser-fixture", help="Explicitly enable local fixture policy ingestion."
        ),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Ingest a local policy file through the browser safety boundary."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = ingest_authorized_policy(
            loaded_scope,
            repo,
            policy_file=policy_file,
            fixture_browser_enabled=enable_browser_fixture,
        )
    except BrowserFeatureGateError as exc:
        console.print("DENY: browser fixture policy ingestion is not enabled")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="browser.policy_ingest",
            action="browser.policy_ingest",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except BrowserAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="browser.policy_ingest",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except PolicyDocumentError as exc:
        console.print("DENY: browser policy ingestion failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="browser.policy_ingest",
            action="browser.policy_ingest",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: browser policy ingestion failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="browser.policy_ingest",
            action="browser.policy_ingest",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="browser.policy_ingest",
        action="browser.policy_ingest",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=[
            "scope-approved local policy ingestion completed; no live browser or network used"
        ],
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_browser_policy_ingestion_table(result)


def _render_memory_records_table(memories: list[MemoryRecord]) -> None:
    table = Table(title="Local Project Memory")
    table.add_column("Memory ID")
    table.add_column("Category")
    table.add_column("Source")
    table.add_column("Retention")
    table.add_column("Redactions")
    table.add_column("Content")
    for memory in memories:
        table.add_row(
            memory.memory_id,
            memory.category,
            memory.source,
            memory.retention_policy,
            str(memory.redaction_count),
            memory.content,
        )
    console.print(table)


def _render_memory_write_table(result: MemoryWriteResult) -> None:
    summary = Table(title="Memory Write Result")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Store", result.store_path)
    summary.add_row("Memory ID", result.memory.memory_id)
    summary.add_row("Category", result.memory.category)
    summary.add_row("Retention", result.memory.retention_policy)
    summary.add_row("Redactions", str(result.memory.redaction_count))
    summary.add_row("Scope expansion allowed", str(result.memory.scope_expansion_allowed))
    summary.add_row("Tool execution allowed", str(result.memory.tool_execution_allowed))
    console.print(summary)
    for note in result.notes:
        console.print(f"- {note}")


def _render_memory_export_table(export: MemoryExport) -> None:
    summary = Table(title="Memory Export")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Store", export.store_path)
    summary.add_row("Repository", export.repository)
    summary.add_row("Records", str(len(export.memory_records)))
    summary.add_row("Raw secret material included", str(export.raw_secret_material_included))
    summary.add_row("Scope expansion allowed", str(export.scope_expansion_allowed))
    console.print(summary)
    _render_memory_records_table(export.memory_records)
    for note in export.notes:
        console.print(f"- {note}")


def _render_memory_delete_table(result: MemoryDeleteResult) -> None:
    summary = Table(title="Memory Delete Result")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Store", result.store_path)
    summary.add_row("Memory ID", result.memory_id)
    summary.add_row("Deleted", str(result.deleted))
    console.print(summary)
    for note in result.notes:
        console.print(f"- {note}")


def _render_skill_templates_table() -> None:
    table = Table(title="Reusable Skill Templates")
    table.add_column("Skill ID")
    table.add_column("Title")
    table.add_column("Required Actions")
    table.add_column("Executable")
    for template in list_skill_templates():
        table.add_row(
            template.skill_id,
            template.title,
            ", ".join(template.required_scope_actions),
            str(template.executable),
        )
    console.print(table)


def _render_skill_proposal_table(proposal: SkillProposal) -> None:
    summary = Table(title="Skill Proposal")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Proposal ID", proposal.proposal_id)
    summary.add_row("Skill ID", proposal.template.skill_id)
    summary.add_row("Repository", proposal.repository)
    summary.add_row("Executable now", str(proposal.executable_now))
    summary.add_row("Scope expansion allowed", str(proposal.scope_expansion_allowed))
    summary.add_row("Tool execution allowed", str(proposal.tool_execution_allowed))
    summary.add_row(
        "All required actions authorized", str(proposal.all_required_actions_authorized)
    )
    console.print(summary)

    decisions = Table(title="Required Action Decisions")
    decisions.add_column("Action")
    decisions.add_column("Decision")
    decisions.add_column("Reasons")
    for decision in proposal.required_action_decisions:
        decisions.add_row(decision.action, decision.decision, "; ".join(decision.reasons))
    console.print(decisions)
    for note in proposal.notes:
        console.print(f"- {note}")


@memory_app.command("remember")
def memory_remember(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the memory."),
    ],
    content: Annotated[
        str,
        typer.Option(
            "--content", help="Human-approved memory text. Secrets/raw evidence are rejected."
        ),
    ],
    approved_by: Annotated[
        str,
        typer.Option("--approved-by", help="Human approver name or handle."),
    ],
    approval_note: Annotated[
        str,
        typer.Option("--approval-note", help="Explicit memory-write approval rationale."),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite memory-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/memory.sqlite"),
    category: Annotated[
        str,
        typer.Option("--category", help="Memory category."),
    ] = "workflow_observation",
    source: Annotated[
        str,
        typer.Option("--source", help="Memory source."),
    ] = "human_note",
    retention: Annotated[
        str,
        typer.Option("--retention", help="Retention policy: session, project, or persistent."),
    ] = "project",
    approve_memory_write: Annotated[
        bool,
        typer.Option("--approve-memory-write", help="Explicitly approve local memory persistence."),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Write one approved, redacted local memory record."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = remember_authorized_memory(
            loaded_scope,
            repo,
            store_path=store,
            content=content,
            category=category,  # type: ignore[arg-type]
            source=source,  # type: ignore[arg-type]
            retention_policy=retention,  # type: ignore[arg-type]
            approved_by=approved_by,
            approval_note=approval_note,
            approve_memory_write=approve_memory_write,
        )
    except MemoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="memory.remember",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except (MemoryApprovalError, MemorySafetyError, EvidenceStorePathError) as exc:
        console.print("DENY: memory write failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="memory.remember",
            action="memory.write",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: memory write failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="memory.remember",
            action="memory.write",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="memory.remember",
        action="memory.write",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["scope-approved redacted memory write completed"],
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_memory_write_table(result)


@memory_app.command("list")
def memory_list(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the memory."),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite memory-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/memory.sqlite"),
    category: Annotated[
        str | None,
        typer.Option("--category", help="Optional memory category filter."),
    ] = None,
    limit: Annotated[
        int,
        typer.Option("--limit", help="Maximum memories to show.", min=1, max=1000),
    ] = 100,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List redacted local memory records after scope approval."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        memories = list_authorized_memories(
            loaded_scope, repo, store_path=store, category=category, limit=limit
        )
    except MemoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: memory list failed")
        console.print(f"- {exc}")
        raise typer.Exit(code=2) from exc

    if output_format == "json":
        console.print_json(data=[memory.model_dump(mode="json") for memory in memories])
    else:
        _render_memory_records_table(memories)


@memory_app.command("export")
def memory_export(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the memory."),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite memory-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/memory.sqlite"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Export redacted memory records after scope approval."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        export = export_authorized_memories(loaded_scope, repo, store_path=store)
    except MemoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: memory export failed")
        console.print(f"- {exc}")
        raise typer.Exit(code=2) from exc

    if output_format == "json":
        console.print_json(data=export.model_dump(mode="json"))
    else:
        _render_memory_export_table(export)


@memory_app.command("delete")
def memory_delete(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option("--repo", help="Allowlisted local repository associated with the memory."),
    ],
    memory_id: Annotated[
        str,
        typer.Option("--memory-id", help="Memory record ID to delete."),
    ],
    store: Annotated[
        Path,
        typer.Option(
            "--store", help="SQLite memory-store path. Must be outside the target repository."
        ),
    ] = Path(".bountyclaw/memory.sqlite"),
    approve_delete: Annotated[
        bool,
        typer.Option("--approve-delete", help="Explicitly approve memory deletion."),
    ] = False,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Delete one memory record after scope approval and explicit approval."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        result = delete_authorized_memory(
            loaded_scope,
            repo,
            store_path=store,
            memory_id=memory_id,
            approve_delete=approve_delete,
        )
    except MemoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        raise typer.Exit(code=2) from exc
    except (MemoryApprovalError, MemoryNotFoundError) as exc:
        console.print("DENY: memory delete failed")
        console.print(f"- {exc}")
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: memory delete failed")
        console.print(f"- {exc}")
        raise typer.Exit(code=2) from exc

    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_memory_delete_table(result)


@skills_app.command("list")
def skills_list(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """List built-in non-executing reusable skill templates."""

    output_format = _validate_output_format("json" if json_output else output)
    templates = list_skill_templates()
    if output_format == "json":
        console.print_json(data=[template.model_dump(mode="json") for template in templates])
    else:
        _render_skill_templates_table()


@skills_app.command("propose")
def skills_propose(
    manifest: Annotated[
        Path,
        typer.Option("--manifest", "-m", help="Path to a YAML or JSON scope manifest."),
    ],
    repo: Annotated[
        Path,
        typer.Option(
            "--repo", help="Allowlisted local repository associated with the skill proposal."
        ),
    ],
    skill_id: Annotated[
        str,
        typer.Option("--skill-id", help="Built-in skill template ID."),
    ],
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    audit_log: Annotated[
        Path | None,
        typer.Option("--audit-log", help="Optional JSONL audit log path."),
    ] = None,
) -> None:
    """Create a non-executing skill proposal after scope approval."""

    output_format = _validate_output_format("json" if json_output else output)
    try:
        loaded_scope = load_scope_manifest(manifest)
        proposal = propose_authorized_skill(loaded_scope, repo, skill_id=skill_id)
    except MemoryAuthorizationError as exc:
        decision = exc.decision
        _print_decision(f"DENY: {decision.action}", decision.reasons)
        _write_audit(
            audit_log,
            event_type="skills.propose",
            action=decision.action,
            decision=decision.decision,
            target_kind=decision.target_kind.value if decision.target_kind else None,
            target=decision.target,
            reasons=decision.reasons,
        )
        raise typer.Exit(code=2) from exc
    except SkillSelectionError as exc:
        console.print("DENY: skill proposal failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="skills.propose",
            action="skill.propose",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI behavior.
        console.print("DENY: skill proposal failed")
        console.print(f"- {exc}")
        _write_audit(
            audit_log,
            event_type="skills.propose",
            action="skill.propose",
            decision="deny",
            target_kind="local_repo",
            target=str(repo),
            reasons=[str(exc)],
        )
        raise typer.Exit(code=2) from exc

    _write_audit(
        audit_log,
        event_type="skills.propose",
        action="skill.propose",
        decision="allow",
        target_kind="local_repo",
        target=str(repo),
        reasons=["scope-approved non-executing skill proposal created"],
    )
    if output_format == "json":
        console.print_json(data=proposal.model_dump(mode="json"))
    else:
        _render_skill_proposal_table(proposal)


@release_app.command("checklist")
def release_checklist(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Render the Phase 9 release-control checklist without executing external systems."""

    output_format = _validate_output_format("json" if json_output else output)
    result = build_release_checklist(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_release_checklist_table(result)


@release_app.command("verify")
def release_verify(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit checks fail.",
        ),
    ] = True,
) -> None:
    """Verify local Phase 9 release-control definitions and disclose deferred external gates."""

    output_format = _validate_output_format("json" if json_output else output)
    result = verify_release_controls(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_release_verification_table(result)
    if fail_on_commit_blocker and not result.ready_for_commit:
        raise typer.Exit(code=2)


@release_app.command("rollback-plan")
def release_rollback_plan(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Render deterministic rollback steps for Phase 9 release-control artifacts."""

    output_format = _validate_output_format("json" if json_output else output)
    plan = build_release_rollback_plan()
    if output_format == "json":
        console.print_json(data=plan.model_dump(mode="json"))
    else:
        _render_release_rollback_plan_table(plan)


@hardening_app.command("checklist")
def hardening_checklist(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Render the Phase 10 hardening checklist without executing external systems."""

    output_format = _validate_output_format("json" if json_output else output)
    result = build_hardening_checklist(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_hardening_checklist_table(result)


@hardening_app.command("verify")
def hardening_verify(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit checks fail.",
        ),
    ] = True,
) -> None:
    """Verify local Phase 10 hardening controls and disclose deferred external gates."""

    output_format = _validate_output_format("json" if json_output else output)
    result = verify_local_hardening(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_hardening_verification_table(result)
    if fail_on_commit_blocker and not result.ready_for_commit:
        raise typer.Exit(code=2)


@hardening_app.command("redaction-corpus")
def hardening_redaction_corpus(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_failure: Annotated[
        bool,
        typer.Option(
            "--fail-on-failure/--no-fail-on-failure", help="Exit non-zero when corpus cases fail."
        ),
    ] = True,
) -> None:
    """Run deterministic local redaction fixtures without external systems."""

    output_format = _validate_output_format("json" if json_output else output)
    result = run_redaction_corpus()
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_redaction_corpus_table(result)
    if fail_on_failure and not result.passed:
        raise typer.Exit(code=2)


@hardening_app.command("prompt-corpus")
def hardening_prompt_corpus(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_failure: Annotated[
        bool,
        typer.Option(
            "--fail-on-failure/--no-fail-on-failure", help="Exit non-zero when corpus cases fail."
        ),
    ] = True,
) -> None:
    """Run deterministic local prompt-safety fixtures without model calls."""

    output_format = _validate_output_format("json" if json_output else output)
    result = run_prompt_safety_corpus()
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_prompt_safety_corpus_table(result)
    if fail_on_failure and not result.passed:
        raise typer.Exit(code=2)


@hardening_app.command("external-plan")
def hardening_external_plan(
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Render deferred Phase 10 external validation tasks for future agents."""

    output_format = _validate_output_format("json" if json_output else output)
    plan = build_external_validation_plan()
    if output_format == "json":
        console.print_json(data=plan.model_dump(mode="json"))
    else:
        _render_external_validation_plan_table(plan)


@handoff_app.command("plan")
def handoff_plan(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Render the Phase 11 Codex/local/CI external-validation handoff plan."""

    output_format = _validate_output_format("json" if json_output else output)
    plan = build_codex_handoff_plan(root)
    if output_format == "json":
        console.print_json(data=plan.model_dump(mode="json"))
    else:
        _render_handoff_plan_table(plan)


@handoff_app.command("evidence-template")
def handoff_evidence_template(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root used to derive task coverage."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Render expected future evidence artifacts without executing external validation."""

    output_format = _validate_output_format("json" if json_output else output)
    template = build_evidence_template(root)
    if output_format == "json":
        console.print_json(data=template.model_dump(mode="json"))
    else:
        _render_evidence_template_table(template)


@handoff_app.command("export")
def handoff_export(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option("--output", help="Directory where handoff package files will be written."),
    ] = Path(".bountyclaw/handoff"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Write a deterministic local handoff package for Codex/local/CI continuation."""

    output_format = _validate_output_format("json" if json_output else output)
    result = export_handoff_package(root, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_handoff_export_table(result)


@handoff_app.command("verify")
def handoff_verify(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify local Phase 11 handoff artifacts and disclose deferred production validation."""

    output_format = _validate_output_format("json" if json_output else output)
    result = verify_handoff_readiness(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_handoff_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@validation_evidence_app.command("ledger")
def validation_evidence_ledger(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Build a hash-only ledger of expected future validation evidence artifacts."""

    output_format = _validate_output_format("json" if json_output else output)
    result = build_validation_evidence_ledger(root, evidence_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_evidence_ledger_table(result)


@validation_evidence_app.command("gap-readiness")
def validation_evidence_gap_readiness(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Map evidence artifact presence to gap-closure readiness without closing gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = assess_gap_closure_readiness(root, evidence_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_gap_closure_readiness_table(result)


@validation_evidence_app.command("export-ledger")
def validation_evidence_export_ledger(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output", help="Directory where validation evidence ledger files will be written."
        ),
    ] = Path(".bountyclaw/validation-evidence"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Export a deterministic validation evidence ledger package."""

    output_format = _validate_output_format("json" if json_output else output)
    result = export_validation_evidence_ledger(root, evidence_dir, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_evidence_export_table(result)


@validation_evidence_app.command("verify")
def validation_evidence_verify(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 12 validation evidence ledger readiness without closing gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = verify_validation_evidence_readiness(root, evidence_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_evidence_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@evidence_review_app.command("template")
def evidence_review_template(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    review_file: Annotated[
        Path | None,
        typer.Option(
            "--review-file", help="Future JSON metadata file with human evidence-review decisions."
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Build a metadata-only template for future human evidence-review decisions."""

    output_format = _validate_output_format("json" if json_output else output)
    result = build_evidence_review_template(root, evidence_dir, review_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_evidence_review_template_table(result)


@evidence_review_app.command("status")
def evidence_review_status(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    review_file: Annotated[
        Path | None,
        typer.Option(
            "--review-file", help="JSON metadata file with human evidence-review decisions."
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Assess review-decision metadata against the hash-only evidence ledger."""

    output_format = _validate_output_format("json" if json_output else output)
    result = assess_evidence_review_status(root, evidence_dir, review_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_evidence_review_status_table(result)


@evidence_review_app.command("closure-proposals")
def evidence_review_closure_proposals(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    review_file: Annotated[
        Path | None,
        typer.Option(
            "--review-file", help="JSON metadata file with human evidence-review decisions."
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Draft gap-closure proposals without editing governance files or closing gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = build_gap_closure_proposals(root, evidence_dir, review_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_gap_closure_proposals_table(result)


@evidence_review_app.command("export-package")
def evidence_review_export_package(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    review_file: Annotated[
        Path | None,
        typer.Option(
            "--review-file", help="JSON metadata file with human evidence-review decisions."
        ),
    ] = None,
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output", help="Directory where evidence-review package files will be written."
        ),
    ] = Path(".bountyclaw/evidence-review"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Export a metadata-only evidence-review package for human reviewers."""

    output_format = _validate_output_format("json" if json_output else output)
    result = export_evidence_review_package(root, evidence_dir, review_file, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_evidence_review_export_table(result)


@evidence_review_app.command("verify")
def evidence_review_verify(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future external-validation evidence artifacts.",
        ),
    ] = Path("validation_evidence"),
    review_file: Annotated[
        Path | None,
        typer.Option(
            "--review-file", help="JSON metadata file with human evidence-review decisions."
        ),
    ] = None,
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 13 evidence-review workflow readiness without closing gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = verify_evidence_review_readiness(root, evidence_dir, review_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_evidence_review_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@gap_tracker_app.command("audit")
def gap_tracker_audit(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Audit PRODUCTION_GAP_TRACKER.md required fields without closing gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = audit_gap_tracker(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_gap_tracker_audit_table(result)


@gap_tracker_app.command("backlog")
def gap_tracker_backlog(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Build a deterministic Codex/local/CI backlog from unresolved production gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = build_codex_gap_backlog(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_codex_gap_backlog_table(result)


@gap_tracker_app.command("export")
def gap_tracker_export(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output", help="Directory where gap tracker governance files will be written."
        ),
    ] = Path(".bountyclaw/gap-tracker"),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
) -> None:
    """Export a local gap tracker audit and Codex backlog package."""

    output_format = _validate_output_format("json" if json_output else output)
    result = export_gap_tracker_package(root, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_gap_tracker_export_table(result)


@gap_tracker_app.command("verify")
def gap_tracker_verify(
    root: Annotated[
        Path,
        typer.Option("--root", help="Repository root to evaluate."),
    ] = Path("."),
    output: Annotated[
        str,
        typer.Option("--format", help="Output format: table or json."),
    ] = "table",
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Shortcut for --format json."),
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 14 gap tracker governance readiness without closing gaps."""

    output_format = _validate_output_format("json" if json_output else output)
    result = verify_gap_tracker_governance(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_gap_tracker_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@validation_runbook_app.command("build")
def validation_runbook_build(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build the Phase 15 external validation runbook without executing it."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_external_validation_runbook(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_runbook_table(result)


@validation_runbook_app.command("journal-template")
def validation_runbook_journal_template(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build a metadata-only future execution journal template."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_run_journal_template(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_run_journal_template_table(result)


@validation_runbook_app.command("journal-status")
def validation_runbook_journal_status(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    journal_file: Annotated[
        Path | None, typer.Option("--journal", help="Metadata-only future execution journal file.")
    ] = None,
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Assess metadata-only future execution journal status without closing gaps."""
    output_format = _validate_output_format("json" if json_output else output)
    result = assess_run_journal_status(root, journal_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_run_journal_status_table(result)


@validation_runbook_app.command("export")
def validation_runbook_export(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output", help="Directory where validation-runbook package files will be written."
        ),
    ] = Path(".bountyclaw/validation-runbook"),
    journal_file: Annotated[
        Path | None, typer.Option("--journal", help="Metadata-only future execution journal file.")
    ] = None,
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Export the Phase 15 external validation runbook package."""
    output_format = _validate_output_format("json" if json_output else output)
    result = export_validation_runbook_package(root, output_dir, journal_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_runbook_export_table(result)


@validation_runbook_app.command("verify")
def validation_runbook_verify(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    journal_file: Annotated[
        Path | None, typer.Option("--journal", help="Metadata-only future execution journal file.")
    ] = None,
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 15 validation-runbook readiness without executing it."""
    output_format = _validate_output_format("json" if json_output else output)
    result = verify_validation_runbook_readiness(root, journal_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_runbook_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@validation_baseline_app.command("manifest")
def validation_baseline_manifest(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build the Phase 16 hash-only validation baseline manifest."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_validation_baseline_manifest(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_baseline_manifest_table(result)


@validation_baseline_app.command("export")
def validation_baseline_export(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output", help="Directory where validation-baseline package files will be written."
        ),
    ] = Path(".bountyclaw/validation-baseline"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Export the Phase 16 hash-only validation baseline package."""
    output_format = _validate_output_format("json" if json_output else output)
    result = export_validation_baseline_package(root, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_baseline_export_table(result)


@validation_baseline_app.command("verify")
def validation_baseline_verify(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 16 validation-baseline readiness without external execution."""
    output_format = _validate_output_format("json" if json_output else output)
    result = verify_validation_baseline_readiness(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_validation_baseline_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@closure_gate_app.command("attestation-template")
def closure_gate_attestation_template(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    attestation_file: Annotated[
        Path,
        typer.Option("--attestation-file", help="Future metadata-only readiness attestation file."),
    ] = Path("validation_evidence/readiness_attestations.json"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build a metadata-only Phase 17 readiness attestation template."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_readiness_attestation_template(root, attestation_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_readiness_attestation_template_table(result)


@closure_gate_app.command("status")
def closure_gate_status(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future validation evidence metadata/artifacts.",
        ),
    ] = Path("validation_evidence"),
    attestation_file: Annotated[
        Path, typer.Option("--attestation-file", help="Metadata-only readiness attestation file.")
    ] = Path("validation_evidence/readiness_attestations.json"),
    journal_file: Annotated[
        Path,
        typer.Option("--journal", help="Metadata-only external validation execution journal file."),
    ] = Path("validation_runs/execution_journal.json"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Assess Phase 17 closure-gate metadata without closing gaps."""
    output_format = _validate_output_format("json" if json_output else output)
    result = assess_closure_gate_status(root, evidence_dir, attestation_file, journal_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_closure_gate_status_table(result)


@closure_gate_app.command("export")
def closure_gate_export(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output", help="Directory where closure-gate package files will be written."
        ),
    ] = Path(".bountyclaw/closure-gate"),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future validation evidence metadata/artifacts.",
        ),
    ] = Path("validation_evidence"),
    attestation_file: Annotated[
        Path, typer.Option("--attestation-file", help="Metadata-only readiness attestation file.")
    ] = Path("validation_evidence/readiness_attestations.json"),
    journal_file: Annotated[
        Path,
        typer.Option("--journal", help="Metadata-only external validation execution journal file."),
    ] = Path("validation_runs/execution_journal.json"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Export Phase 17 closure-gate templates and status metadata."""
    output_format = _validate_output_format("json" if json_output else output)
    result = export_closure_gate_package(
        root, output_dir, evidence_dir, attestation_file, journal_file
    )
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_closure_gate_export_table(result)


@closure_gate_app.command("verify")
def closure_gate_verify(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    evidence_dir: Annotated[
        Path,
        typer.Option(
            "--evidence-dir",
            help="Directory containing future validation evidence metadata/artifacts.",
        ),
    ] = Path("validation_evidence"),
    attestation_file: Annotated[
        Path, typer.Option("--attestation-file", help="Metadata-only readiness attestation file.")
    ] = Path("validation_evidence/readiness_attestations.json"),
    journal_file: Annotated[
        Path,
        typer.Option("--journal", help="Metadata-only external validation execution journal file."),
    ] = Path("validation_runs/execution_journal.json"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 17 closure-gate readiness without external execution."""
    output_format = _validate_output_format("json" if json_output else output)
    result = verify_closure_gate_readiness(root, evidence_dir, attestation_file, journal_file)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_closure_gate_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


@readiness_dashboard_app.command("build")
def readiness_dashboard_build(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build the Phase 18 consolidated readiness dashboard."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_readiness_dashboard(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_readiness_dashboard_table(result)


@readiness_dashboard_app.command("handoff-index")
def readiness_dashboard_handoff_index(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build the Phase 18 external executor command index without running it."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_external_executor_index(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_external_executor_index_table(result)


@readiness_dashboard_app.command("export")
def readiness_dashboard_export(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option("--output", help="Directory where readiness dashboard files will be written."),
    ] = Path(".bountyclaw/readiness-dashboard"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Export the Phase 18 readiness dashboard package."""
    output_format = _validate_output_format("json" if json_output else output)
    result = export_readiness_dashboard_package(root, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_readiness_dashboard_export_table(result)


@readiness_dashboard_app.command("verify")
def readiness_dashboard_verify(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 18 dashboard readiness without external execution."""
    output_format = _validate_output_format("json" if json_output else output)
    result = verify_readiness_dashboard(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_readiness_dashboard_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)


def _render_quality_gate_checklist_table(result: QualityGateChecklist) -> None:
    summary = Table(title="Phase 19 Quality Gate Checklist")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    gates = Table(title="Gates")
    gates.add_column("Gate ID")
    gates.add_column("Kind")
    gates.add_column("Status")
    gates.add_column("Command")
    for gate in result.gates:
        gates.add_row(gate.gate_id, gate.kind, gate.local_execution_status, gate.command)
    console.print(gates)
    for note in result.notes:
        console.print(f"- {note}")


def _render_quality_gate_export_table(result: QualityGateExportResult) -> None:
    table = Table(title="Phase 19 Quality Gate Export")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Output", result.output_directory)
    table.add_row("Passed", str(result.passed_count))
    table.add_row("Failed", str(result.failed_count))
    table.add_row("Deferred", str(result.deferred_count))
    table.add_row("Ready for commit", str(result.ready_for_commit))
    table.add_row("Ready for production", str(result.ready_for_production))
    console.print(table)
    for note in result.notes:
        console.print(f"- {note}")


def _render_quality_gate_verification_table(result: QualityGateVerificationResult) -> None:
    summary = Table(title="Phase 19 Quality Gate Verification")
    summary.add_column("Field")
    summary.add_column("Value")
    summary.add_row("Passed", str(result.passed_count))
    summary.add_row("Failed", str(result.failed_count))
    summary.add_row("Deferred", str(result.deferred_count))
    summary.add_row("Ready for commit", str(result.ready_for_commit))
    summary.add_row("Ready for Codex", str(result.ready_for_codex))
    summary.add_row("Ready for production", str(result.ready_for_production))
    console.print(summary)

    checks = Table(title="Checks")
    checks.add_column("Check ID")
    checks.add_column("Status")
    checks.add_column("Summary")
    for check in result.checks:
        checks.add_row(check.check_id, check.status, check.summary)
    console.print(checks)
    for note in result.notes:
        console.print(f"- {note}")


@quality_gates_app.command("checklist")
def quality_gates_checklist(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Build the Phase 19 local quality/security gate checklist."""
    output_format = _validate_output_format("json" if json_output else output)
    result = build_quality_gate_checklist(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_quality_gate_checklist_table(result)


@quality_gates_app.command("export")
def quality_gates_export(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output_dir: Annotated[
        Path,
        typer.Option("--output", help="Directory where quality gate files will be written."),
    ] = Path(".bountyclaw/quality-gates"),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
) -> None:
    """Export Phase 19 quality gate metadata artifacts."""
    output_format = _validate_output_format("json" if json_output else output)
    result = export_quality_gate_package(root, output_dir)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_quality_gate_export_table(result)


@quality_gates_app.command("verify")
def quality_gates_verify(
    root: Annotated[Path, typer.Option("--root", help="Repository root to evaluate.")] = Path("."),
    output: Annotated[
        str, typer.Option("--format", help="Output format: table or json.")
    ] = "table",
    json_output: Annotated[
        bool, typer.Option("--json", help="Shortcut for --format json.")
    ] = False,
    fail_on_commit_blocker: Annotated[
        bool,
        typer.Option(
            "--fail-on-commit-blocker/--no-fail-on-commit-blocker",
            help="Exit non-zero when required commit or Codex checks fail.",
        ),
    ] = True,
) -> None:
    """Verify Phase 19 quality/security gate metadata readiness."""
    output_format = _validate_output_format("json" if json_output else output)
    result = verify_quality_gate_readiness(root)
    if output_format == "json":
        console.print_json(data=result.model_dump(mode="json"))
    else:
        _render_quality_gate_verification_table(result)
    if fail_on_commit_blocker and (not result.ready_for_commit or not result.ready_for_codex):
        raise typer.Exit(code=2)
