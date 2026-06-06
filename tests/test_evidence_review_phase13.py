from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.evidence_review import (
    assess_evidence_review_status,
    build_evidence_review_template,
    build_gap_closure_proposals,
    export_evidence_review_package,
    verify_evidence_review_readiness,
)
from bountyclaw.handoff import build_evidence_template, export_handoff_package
from bountyclaw.validation_evidence import build_validation_evidence_ledger

runner = CliRunner()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _artifact_path(evidence_dir: Path, filename: str) -> Path:
    relative = Path(filename)
    if relative.parts and relative.parts[0] == evidence_dir.name:
        relative = Path(*relative.parts[1:])
    return evidence_dir / relative


def test_evidence_review_template_is_metadata_only_and_non_closing(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "validation_evidence"
    result = build_evidence_review_template(repo_root(), evidence_dir)

    assert result.phase == "13"
    assert result.source_phase == "12"
    assert result.decision_count >= 20
    assert result.ready_for_human_review is False
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.raw_evidence_contents_included is False
    assert all(decision.decision == "pending" for decision in result.decisions)
    assert all(decision.raw_content_included is False for decision in result.decisions)
    assert all(decision.automated_gap_closure_allowed is False for decision in result.decisions)


def test_evidence_review_status_blocks_missing_and_unreviewed_artifacts(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "validation_evidence"
    status = assess_evidence_review_status(repo_root(), evidence_dir)
    proposals = build_gap_closure_proposals(repo_root(), evidence_dir)

    assert status.phase == "13"
    assert status.artifact_count >= 20
    assert status.present_count == 0
    assert status.missing_count == status.artifact_count
    assert status.approved_count == 0
    assert status.accepted_for_closure_proposal_count == 0
    assert status.ready_for_gap_closure is False
    assert status.ready_for_production is False
    assert all(artifact.raw_content_included is False for artifact in status.artifacts)
    assert proposals.phase == "13"
    assert proposals.proposal_count >= 20
    assert proposals.proposals_ready_for_human_update == 0
    assert proposals.ready_for_gap_closure is False
    assert all(proposal.auto_close_allowed is False for proposal in proposals.proposals)
    assert any(
        proposal.proposal_status == "blocked_missing_artifacts" for proposal in proposals.proposals
    )


def test_approved_matching_review_metadata_creates_human_update_proposal(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "validation_evidence"
    template = build_evidence_template(repo_root())
    first_task_id = template.artifacts[0].producer_task_id
    first_task_artifacts = [
        artifact for artifact in template.artifacts if artifact.producer_task_id == first_task_id
    ]
    assert len(first_task_artifacts) >= 2

    for artifact in first_task_artifacts:
        path = _artifact_path(evidence_dir, artifact.filename)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"reviewed external evidence placeholder for {artifact.artifact_id}\n", encoding="utf-8"
        )

    ledger = build_validation_evidence_ledger(repo_root(), evidence_dir)
    sha_by_artifact = {
        artifact.artifact_id: artifact.sha256
        for artifact in ledger.artifacts
        if artifact.producer_task_id == first_task_id
    }
    review_file = evidence_dir / "evidence_review_decisions.json"
    review_payload = {
        "file_version": "1",
        "phase": "13",
        "decisions": [
            {
                "artifact_id": artifact.artifact_id,
                "decision": "approved_redacted",
                "reviewer": "human-appsec-reviewer",
                "reviewed_at_utc": "2026-06-01T00:00:00Z",
                "artifact_sha256": sha_by_artifact[artifact.artifact_id],
                "rationale": "Reviewed private evidence and approved redacted metadata for closure proposal only.",
                "redacted_artifact_path": artifact.filename,
                "raw_content_included": False,
            }
            for artifact in first_task_artifacts
        ],
    }
    review_file.write_text(json.dumps(review_payload), encoding="utf-8")

    status = assess_evidence_review_status(repo_root(), evidence_dir, review_file)
    proposals = build_gap_closure_proposals(repo_root(), evidence_dir, review_file)

    assert status.approved_count == len(first_task_artifacts)
    assert status.accepted_for_closure_proposal_count == len(first_task_artifacts)
    ready = [
        proposal for proposal in proposals.proposals if proposal.ready_for_human_gap_tracker_update
    ]
    assert ready
    assert {"PGT-087", "PGT-097"}.issubset({proposal.gap_id for proposal in ready})
    assert all(proposal.auto_close_allowed is False for proposal in ready)
    assert proposals.ready_for_gap_closure is False
    assert proposals.ready_for_production is False


def test_review_hash_mismatch_blocks_gap_update(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "validation_evidence"
    artifact = build_evidence_template(repo_root()).artifacts[0]
    path = _artifact_path(evidence_dir, artifact.filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("reviewed external evidence placeholder\n", encoding="utf-8")
    review_file = evidence_dir / "evidence_review_decisions.json"
    review_file.write_text(
        json.dumps(
            {
                "file_version": "1",
                "phase": "13",
                "decisions": [
                    {
                        "artifact_id": artifact.artifact_id,
                        "decision": "approved_redacted",
                        "reviewer": "human-appsec-reviewer",
                        "reviewed_at_utc": "2026-06-01T00:00:00Z",
                        "artifact_sha256": "0" * 64,
                        "rationale": "Reviewed artifact but this hash intentionally does not match.",
                        "raw_content_included": False,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    status = assess_evidence_review_status(repo_root(), evidence_dir, review_file)
    reviewed = next(item for item in status.artifacts if item.artifact_id == artifact.artifact_id)

    assert reviewed.review_decision == "approved_redacted"
    assert reviewed.sha256_matches_ledger is False
    assert reviewed.accepted_for_closure_proposal is False
    assert "reviewed artifact hash does not match ledger hash" in reviewed.blockers


def test_evidence_review_export_and_handoff_include_review_commands(tmp_path: Path) -> None:
    output = tmp_path / "review_export"
    result = export_evidence_review_package(
        repo_root(), tmp_path / "validation_evidence", output_dir=output
    )

    assert result.phase == "13"
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    written_names = {Path(path).name for path in result.written_files}
    assert {
        "evidence_review_template.json",
        "evidence_review_status.json",
        "gap_closure_proposals.json",
        "EVIDENCE_REVIEW_PACKAGE.md",
        "REVIEW_DECISION_TEMPLATE.md",
        "evidence_review_manifest.json",
    }.issubset(written_names)
    manifest = json.loads((output / "evidence_review_manifest.json").read_text(encoding="utf-8"))
    assert manifest["ready_for_gap_closure"] is False
    assert manifest["raw_evidence_contents_included"] is False

    handoff = export_handoff_package(repo_root(), tmp_path / "handoff")
    handoff_names = {Path(path).name for path in handoff.written_files}
    assert "EVIDENCE_REVIEW_COMMANDS.md" in handoff_names
    assert "evidence-review closure-proposals" in (
        tmp_path / "handoff" / "EVIDENCE_REVIEW_COMMANDS.md"
    ).read_text(encoding="utf-8")


def test_evidence_review_verifier_is_codex_ready_but_not_production_ready() -> None:
    result = verify_evidence_review_readiness(repo_root())

    assert result.phase == "13"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.network_used is False
    assert result.external_actions_executed is False
    assert result.raw_evidence_contents_included is False
    check_ids = {check.check_id for check in result.checks}
    assert "EVREVIEW-TEMPLATE-COVERAGE" in check_ids
    assert "EVREVIEW-GAP-PROPOSAL-COVERAGE" in check_ids
    assert "EVREVIEW-HUMAN-REVIEW-STILL-OPEN" in check_ids


def test_evidence_review_cli_commands_render_json(tmp_path: Path) -> None:
    root = str(repo_root())
    evidence_dir = str(tmp_path / "validation_evidence")

    template = runner.invoke(
        app,
        ["evidence-review", "template", "--root", root, "--evidence-dir", evidence_dir, "--json"],
    )
    assert template.exit_code == 0, template.output
    template_payload = json.loads(template.output)
    assert template_payload["phase"] == "13"
    assert template_payload["ready_for_gap_closure"] is False

    status = runner.invoke(
        app,
        ["evidence-review", "status", "--root", root, "--evidence-dir", evidence_dir, "--json"],
    )
    assert status.exit_code == 0, status.output
    status_payload = json.loads(status.output)
    assert status_payload["phase"] == "13"
    assert status_payload["ready_for_production"] is False

    proposals = runner.invoke(
        app,
        [
            "evidence-review",
            "closure-proposals",
            "--root",
            root,
            "--evidence-dir",
            evidence_dir,
            "--json",
        ],
    )
    assert proposals.exit_code == 0, proposals.output
    proposals_payload = json.loads(proposals.output)
    assert proposals_payload["ready_for_gap_closure"] is False

    export = runner.invoke(
        app,
        [
            "evidence-review",
            "export-package",
            "--root",
            root,
            "--evidence-dir",
            evidence_dir,
            "--output",
            str(tmp_path / "review_export"),
            "--json",
        ],
    )
    assert export.exit_code == 0, export.output
    export_payload = json.loads(export.output)
    assert export_payload["phase"] == "13"

    verify = runner.invoke(
        app,
        ["evidence-review", "verify", "--root", root, "--evidence-dir", evidence_dir, "--json"],
    )
    assert verify.exit_code == 0, verify.output
    verify_payload = json.loads(verify.output)
    assert verify_payload["ready_for_commit"] is True
    assert verify_payload["ready_for_codex"] is True
    assert verify_payload["ready_for_production"] is False


def test_ci_workflow_includes_phase13_evidence_review_verifier() -> None:
    workflow = (repo_root() / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "python scripts/phase9_verify.py --root ." in workflow
    assert "python scripts/phase10_verify.py --root ." in workflow
    assert "python scripts/phase11_verify.py --root ." in workflow
    assert "python scripts/phase12_verify.py --root ." in workflow
    assert "python scripts/phase13_verify.py --root ." in workflow
