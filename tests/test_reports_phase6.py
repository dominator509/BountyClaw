from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.findings import EvidenceStore, collect_authorized_findings
from bountyclaw.reports import (
    ReportAuthorizationError,
    ReportDraftReadinessError,
    ReportStore,
    draft_authorized_report,
    record_triage_review,
)
from bountyclaw.scope import load_scope_manifest

runner = CliRunner()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text(
        "import subprocess\n"
        "def handler(value):\n"
        "    eval(value)\n"
        "    subprocess.run(value, shell=True)\n",
        encoding="utf-8",
    )
    return repo


def write_manifest(tmp_path: Path, repo: Path, *, allowed_actions: list[str] | None = None) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {
            "name": "Authorized Phase 6 Fixture",
            "policy_file": "policy.md",
            "disclosure_rules": ["manual report submission only"],
        },
        "authorization": {
            "operator": "phase6-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for report testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo),
                    "label": "fixture",
                    "allowed_actions": allowed_actions
                    or [
                        "repo.read",
                        "scan.local_static",
                        "findings.write",
                        "model.triage",
                        "triage.review",
                        "report.draft",
                    ],
                }
            ],
            "domains": [],
            "out_of_scope": [],
        },
        "controls": {
            "network_access_enabled": False,
            "require_human_approval_for_active_validation": True,
        },
    }
    path = tmp_path / "scope.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def prepare_store(tmp_path: Path) -> tuple[Path, Path, Path, str]:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)
    store = tmp_path / "state" / "evidence.sqlite"
    result = collect_authorized_findings(
        loaded_scope,
        repo,
        store_path=store,
        local_scanner_enabled=True,
    )
    assert result.canonical_findings
    return repo, manifest_path, store, result.canonical_findings[0].canonical_finding_id


def approve_for_draft(manifest_path: Path, repo: Path, store: Path, finding_id: str):
    loaded_scope = load_scope_manifest(manifest_path)
    return record_triage_review(
        loaded_scope,
        repo,
        store_path=store,
        finding_id=finding_id,
        review_status="approved_for_draft",
        reviewer="human-reviewer",
        rationale="Human reviewer approved this static finding for draft generation only.",
        impact_assessment="Potential code-execution risk if untrusted input reaches this sink.",
        recommended_action="Prepare a conservative draft and validate manually before submission.",
    )


def test_record_triage_review_requires_scope_action(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_with_review = write_manifest(tmp_path, repo)
    loaded_with_review = load_scope_manifest(manifest_with_review)
    store = tmp_path / "state" / "evidence.sqlite"
    collection = collect_authorized_findings(
        loaded_with_review,
        repo,
        store_path=store,
        local_scanner_enabled=True,
    )
    manifest_without_review = write_manifest(
        tmp_path,
        repo,
        allowed_actions=["repo.read", "scan.local_static", "findings.write", "report.draft"],
    )
    loaded_without_review = load_scope_manifest(manifest_without_review)

    with pytest.raises(ReportAuthorizationError) as exc:
        record_triage_review(
            loaded_without_review,
            repo,
            store_path=store,
            finding_id=collection.canonical_findings[0].canonical_finding_id,
            review_status="approved_for_draft",
            reviewer="human-reviewer",
            rationale="Human reviewer approved the draft path for fixture testing.",
        )

    assert exc.value.decision.action == "triage.review"
    assert exc.value.decision.allowed is False


def test_report_draft_requires_approved_human_review(tmp_path: Path) -> None:
    repo, manifest_path, store, finding_id = prepare_store(tmp_path)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(ReportDraftReadinessError):
        draft_authorized_report(
            loaded_scope,
            repo,
            store_path=store,
            finding_id=finding_id,
        )

    record_triage_review(
        loaded_scope,
        repo,
        store_path=store,
        finding_id=finding_id,
        review_status="needs_more_evidence",
        reviewer="human-reviewer",
        rationale="Human reviewer needs more evidence before draft generation.",
    )

    with pytest.raises(ReportDraftReadinessError):
        draft_authorized_report(
            loaded_scope,
            repo,
            store_path=store,
            finding_id=finding_id,
        )


def test_report_draft_is_deterministic_non_submitting_and_static_only(tmp_path: Path) -> None:
    repo, manifest_path, store, finding_id = prepare_store(tmp_path)
    loaded_scope = load_scope_manifest(manifest_path)
    approve_for_draft(manifest_path, repo, store, finding_id)

    result = draft_authorized_report(
        loaded_scope,
        repo,
        store_path=store,
        finding_id=finding_id,
    )

    draft = result.report_draft
    assert draft.submission_allowed is False
    assert draft.report_submission_used is False
    assert draft.active_validation_used is False
    assert draft.network_used is False
    assert draft.live_llm_provider_used is False
    assert draft.validation_status == "not_validated_static_only"
    assert draft.human_review_required is True
    assert "Submission allowed: false" in draft.content_markdown
    assert "not_validated_static_only" in draft.content_markdown
    assert "exploit confirmed" not in draft.content_markdown.lower()
    assert "confirmed through active testing" in draft.content_markdown.lower()

    stored = ReportStore(store).get_report_draft(draft.report_draft_id)
    assert stored is not None
    assert stored.content_markdown == draft.content_markdown


def test_report_draft_can_include_mock_triage_without_live_provider(tmp_path: Path) -> None:
    repo, manifest_path, store, finding_id = prepare_store(tmp_path)
    loaded_scope = load_scope_manifest(manifest_path)
    approve_for_draft(manifest_path, repo, store, finding_id)

    result = draft_authorized_report(
        loaded_scope,
        repo,
        store_path=store,
        finding_id=finding_id,
        include_mock_triage=True,
        mock_model_enabled=True,
    )

    assert result.report_draft.model_triage_summary is not None
    assert result.report_draft.live_llm_provider_used is False
    assert result.report_draft.metadata["model_triage_included"] is True
    assert "Mock model triage summary" in result.report_draft.content_markdown


def test_report_review_cli_outputs_json(tmp_path: Path) -> None:
    repo, manifest_path, store, finding_id = prepare_store(tmp_path)

    result = runner.invoke(
        app,
        [
            "report",
            "review",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--finding-id",
            finding_id,
            "--reviewer",
            "human-reviewer",
            "--rationale",
            "Human reviewer approved this fixture for draft generation only.",
            "--status",
            "approved_for_draft",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["review_status"] == "approved_for_draft"
    assert payload["canonical_finding_id"] == finding_id
    findings = EvidenceStore(store).list_findings()
    assert findings[0].report_readiness_status == "ready_for_report_draft"


def test_report_draft_cli_outputs_json_and_list(tmp_path: Path) -> None:
    repo, manifest_path, store, finding_id = prepare_store(tmp_path)
    approve_for_draft(manifest_path, repo, store, finding_id)

    draft_result = runner.invoke(
        app,
        [
            "report",
            "draft",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--finding-id",
            finding_id,
            "--json",
        ],
    )

    assert draft_result.exit_code == 0, draft_result.output
    payload = json.loads(draft_result.output)
    draft = payload["report_draft"]
    assert draft["submission_allowed"] is False
    assert draft["active_validation_used"] is False
    assert draft["human_review_status"] == "approved_for_draft"

    list_result = runner.invoke(
        app,
        ["report", "list", "--store", str(store), "--json"],
    )
    assert list_result.exit_code == 0, list_result.output
    drafts = json.loads(list_result.output)
    assert drafts
    assert drafts[0]["submission_allowed"] is False
