"""Scope-gated human triage and report drafting service for Phase 6."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path
from textwrap import dedent

from bountyclaw.findings import EvidenceStore, ensure_store_path_outside_repository, redact_text
from bountyclaw.model_router import (
    ModelTriageResult,
    triage_authorized_finding,
)
from bountyclaw.scope import ScopeGate, Target, TargetKind
from bountyclaw.scope.loader import LoadedScopeManifest
from bountyclaw.scope.models import ScopeDecision

from .models import ReportDraft, ReportDraftResult, TriageReview, TriageReviewStatus
from .store import ReportStore


class ReportAuthorizationError(RuntimeError):
    """Raised when report/triage actions are not scope-authorized."""

    def __init__(self, decision: ScopeDecision) -> None:
        self.decision = decision
        super().__init__("; ".join(decision.reasons))


class ReportFindingNotFoundError(RuntimeError):
    """Raised when the requested canonical finding is not in the evidence store."""


class ReportDraftReadinessError(RuntimeError):
    """Raised when a report draft would violate human-review requirements."""


class ReportSafetyError(RuntimeError):
    """Raised when report output fails Phase 6 safety invariants."""


def record_triage_review(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    finding_id: str,
    review_status: TriageReviewStatus,
    reviewer: str,
    rationale: str,
    impact_assessment: str | None = None,
    recommended_action: str | None = None,
    model_triage_request_id: str | None = None,
) -> TriageReview:
    """Persist a human-supplied triage review for a stored finding."""

    _require_allowed(loaded_scope, repo, action="triage.review")
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    if EvidenceStore(resolved_store).get_finding_bundle(finding_id) is None:
        raise ReportFindingNotFoundError(f"finding not found in evidence store: {finding_id}")

    review = TriageReview(
        canonical_finding_id=finding_id,
        review_status=review_status,
        reviewer=reviewer,
        rationale=rationale,
        impact_assessment=impact_assessment,
        recommended_action=recommended_action,
        reviewed_at=datetime.now(UTC).isoformat(),
        model_triage_request_id=model_triage_request_id,
        metadata={
            "phase": "6",
            "human_supplied": True,
            "network_used": False,
            "report_submission_allowed": False,
        },
    )
    ReportStore(resolved_store).upsert_triage_review(review)
    return review


def draft_authorized_report(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    finding_id: str,
    include_mock_triage: bool = False,
    mock_model_enabled: bool = False,
    provider_id: str | None = None,
) -> ReportDraftResult:
    """Create a deterministic report draft for a human-approved finding.

    The draft is local-only and explicitly non-submitting. It never performs live
    provider calls, network actions, MCP/browser use, or active validation.
    """

    _require_allowed(loaded_scope, repo, action="report.draft")
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    evidence_store = EvidenceStore(resolved_store)
    bundle = evidence_store.get_finding_bundle(finding_id)
    if bundle is None:
        raise ReportFindingNotFoundError(f"finding not found in evidence store: {finding_id}")

    report_store = ReportStore(resolved_store)
    review = report_store.get_triage_review(finding_id)
    if review is None:
        raise ReportDraftReadinessError(
            "report drafting requires an explicit human triage review before draft generation"
        )
    if review.review_status != "approved_for_draft":
        raise ReportDraftReadinessError(
            f"report drafting requires review_status=approved_for_draft; got {review.review_status}"
        )

    model_triage: ModelTriageResult | None = None
    if include_mock_triage:
        model_triage = triage_authorized_finding(
            loaded_scope,
            repo,
            store_path=resolved_store,
            finding_id=finding_id,
            provider_id=provider_id,
            mock_model_enabled=mock_model_enabled,
        )

    draft = _build_report_draft(
        repo=repo,
        store_path=resolved_store,
        program_name=loaded_scope.manifest.program.name,
        review=review,
        finding=bundle.finding,
        evidence_records=bundle.evidence_records,
        model_triage=model_triage,
    )
    _assert_report_safety(draft)
    report_store.write_report_draft(draft)
    return ReportDraftResult(
        triage_review=review,
        report_draft=draft,
        live_llm_provider_used=False,
        notes=[
            "Scope-approved Phase 6 report draft created for human review only.",
            "Draft generation used redacted stored evidence and did not submit a report.",
            "No active validation, network access, MCP tools, browser automation, or live LLM provider call was used.",
        ],
    )


def _build_report_draft(
    *,
    repo: Path,
    store_path: Path,
    program_name: str,
    review: TriageReview,
    finding,
    evidence_records,
    model_triage: ModelTriageResult | None,
) -> ReportDraft:
    evidence_ids = [evidence.evidence_id for evidence in evidence_records]
    evidence_summary = _summarize_evidence(evidence_records)
    model_triage_summary = None
    if model_triage is not None:
        model_triage_summary = str(
            model_triage.response.content.get("summary", "Mock triage completed")
        )

    title = f"[Draft] {finding.title}"
    affected_asset = _location(finding.file_path, finding.line_number)
    executive_summary = (
        f"A potential {finding.vulnerability_class} was identified in {affected_asset} "
        f"during authorized local static analysis for {program_name}. "
        "This report is a draft only: exploitability and business impact have not been confirmed through active testing."
    )
    technical_details = (
        f"Finding ID: {finding.canonical_finding_id}\n"
        f"Rule(s): {', '.join(finding.scanner_rule_ids) or 'unknown'}\n"
        f"Scanner(s): {', '.join(finding.scanner_ids) or 'unknown'}\n"
        f"Description: {finding.description}\n"
        f"Redacted evidence summary:\n{evidence_summary}"
    )
    impact_statement = _impact_statement(finding.severity, review.impact_assessment)
    remediation = finding.remediation_guidance or _fallback_remediation(finding.vulnerability_class)
    checklist = [
        "Confirm the affected code path manually inside the authorized local repository.",
        "Validate exploitability only within the program's written rules and safe-harbor boundaries.",
        "Attach only redacted, non-sensitive evidence to the final report.",
        "Update this draft with confirmed reproduction details before any manual submission.",
        "Do not submit automatically; a human must approve the final report.",
    ]
    notes = [
        "Draft is based on redacted local evidence and human triage state.",
        "Validation status is not_validated_static_only.",
        "Automated submission is disabled by design.",
    ]
    if model_triage_summary:
        notes.append("Mock model triage summary was included as advisory, untrusted assistance.")

    draft_id = _draft_id(
        finding.canonical_finding_id, review.reviewed_at, evidence_ids, model_triage_summary
    )
    content_markdown = _render_markdown(
        title=title,
        executive_summary=executive_summary,
        affected_asset=affected_asset,
        finding=finding,
        review=review,
        evidence_summary=evidence_summary,
        technical_details=technical_details,
        impact_statement=impact_statement,
        remediation=remediation,
        checklist=checklist,
        model_triage_summary=model_triage_summary,
        notes=notes,
    )

    redacted_markdown = redact_text(content_markdown).redacted_text
    return ReportDraft(
        report_draft_id=draft_id,
        canonical_finding_id=finding.canonical_finding_id,
        repository=str(repo.expanduser().resolve(strict=False)),
        store_path=str(store_path),
        title=redact_text(title).redacted_text,
        executive_summary=redact_text(executive_summary).redacted_text,
        affected_asset=redact_text(affected_asset).redacted_text,
        vulnerability_class=redact_text(finding.vulnerability_class).redacted_text,
        severity=finding.severity,
        confidence=finding.confidence,
        evidence_summary=redact_text(evidence_summary).redacted_text,
        technical_details=redact_text(technical_details).redacted_text,
        safe_reproduction_checklist=[redact_text(item).redacted_text for item in checklist],
        impact_statement=redact_text(impact_statement).redacted_text,
        remediation=redact_text(remediation).redacted_text,
        human_review_status=review.review_status,
        evidence_ids=evidence_ids,
        model_triage_summary=redact_text(model_triage_summary).redacted_text
        if model_triage_summary
        else None,
        content_markdown=redacted_markdown,
        notes=notes,
        metadata={
            "phase": "6",
            "program_name": redact_text(program_name).redacted_text,
            "model_triage_included": model_triage is not None,
            "unperformed_validation_claims_allowed": False,
            "manual_submission_only": True,
        },
    )


def _assert_report_safety(draft: ReportDraft) -> None:
    forbidden_phrases = (
        "exploit confirmed",
        "submitted automatically",
        "submission allowed: true",
    )
    lowered = draft.content_markdown.lower()
    for phrase in forbidden_phrases:
        if phrase in lowered:
            raise ReportSafetyError(f"report draft contains forbidden unvalidated claim: {phrase}")
    if draft.submission_allowed is not False or draft.report_submission_used is not False:
        raise ReportSafetyError("report draft must remain non-submitting")
    if draft.active_validation_used is not False or draft.network_used is not False:
        raise ReportSafetyError("report draft must not claim active validation or network use")


def _require_allowed(
    loaded_scope: LoadedScopeManifest, repo: Path, *, action: str
) -> ScopeDecision:
    decision = ScopeGate(loaded_scope).evaluate(
        action=action,
        target=Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise ReportAuthorizationError(decision)
    return decision


def _summarize_evidence(evidence_records) -> str:
    if not evidence_records:
        return "No persisted evidence records were available; additional evidence is required."
    lines: list[str] = []
    for index, evidence in enumerate(evidence_records, start=1):
        lines.append(
            f"{index}. {evidence.summary} -- {evidence.content} "
            f"(redaction_status={evidence.redaction_status}, redactions={evidence.redaction_count})"
        )
    return "\n".join(lines)


def _impact_statement(severity: str, human_assessment: str | None) -> str:
    if human_assessment:
        return (
            f"Human triage assessment: {human_assessment}. "
            "Impact remains unconfirmed until authorized validation is completed."
        )
    return (
        f"The scanner assigned severity={severity}. "
        "Business impact is unconfirmed by active testing and must be reviewed manually."
    )


def _fallback_remediation(vulnerability_class: str) -> str:
    return (
        f"Review the affected {vulnerability_class} code path, remove unsafe patterns, "
        "add regression tests, and re-run authorized local validation before submission."
    )


def _render_markdown(
    *,
    title: str,
    executive_summary: str,
    affected_asset: str,
    finding,
    review: TriageReview,
    evidence_summary: str,
    technical_details: str,
    impact_statement: str,
    remediation: str,
    checklist: list[str],
    model_triage_summary: str | None,
    notes: list[str],
) -> str:
    checklist_md = "\n".join(f"- {item}" for item in checklist)
    notes_md = "\n".join(f"- {note}" for note in notes)
    model_section = model_triage_summary or "Not included."
    return dedent(
        f"""
        # {title}

        ## Executive Summary
        {executive_summary}

        ## Affected Asset
        {affected_asset}

        ## Finding Metadata
        - Canonical finding ID: {finding.canonical_finding_id}
        - Vulnerability class: {finding.vulnerability_class}
        - Severity input: {finding.severity}
        - Confidence input: {finding.confidence}
        - Validation status: not_validated_static_only
        - Human review status: {review.review_status}
        - Submission allowed: false

        ## Human Triage Rationale
        {review.rationale}

        ## Technical Details
        {technical_details}

        ## Redacted Evidence
        {evidence_summary}

        ## Safe Reproduction Checklist
        {checklist_md}

        ## Impact Statement
        {impact_statement}

        ## Remediation Guidance
        {remediation}

        ## Mock Model Triage Summary
        {model_section}

        ## Safety and Limitations
        {notes_md}
        """
    ).strip()


def _location(file_path: str, line_number: int | None) -> str:
    if line_number is None:
        return file_path
    return f"{file_path}:{line_number}"


def _draft_id(
    finding_id: str, reviewed_at: str, evidence_ids: list[str], model_triage_summary: str | None
) -> str:
    material = "|".join(
        [finding_id, reviewed_at, *evidence_ids, model_triage_summary or "no-model-triage"]
    )
    return f"bcreport-sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:32]}"
