from __future__ import annotations

import hashlib
import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.handoff import build_evidence_template
from bountyclaw.validation_evidence import (
    assess_gap_closure_readiness,
    build_validation_evidence_ledger,
    export_validation_evidence_ledger,
    verify_validation_evidence_readiness,
)

runner = CliRunner()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_validation_evidence_ledger_is_hash_only_and_non_production_ready(tmp_path: Path) -> None:
    ledger = build_validation_evidence_ledger(repo_root(), tmp_path / "validation_evidence")

    assert ledger.phase == "12"
    assert ledger.source_phase == "11"
    assert ledger.artifact_count >= 20
    assert ledger.present_count == 0
    assert ledger.missing_count == ledger.artifact_count
    assert ledger.ready_for_evidence_review is False
    assert ledger.ready_for_gap_closure is False
    assert ledger.ready_for_production is False
    assert ledger.network_used is False
    assert ledger.external_actions_executed_by_ledger is False
    assert all(artifact.content_inspected is False for artifact in ledger.artifacts)
    assert all(artifact.raw_content_included is False for artifact in ledger.artifacts)


def test_validation_evidence_ledger_hashes_present_artifacts_without_content_output(
    tmp_path: Path,
) -> None:
    evidence_dir = tmp_path / "validation_evidence"
    expected = build_evidence_template(repo_root()).artifacts[0]
    relative = Path(expected.filename)
    if relative.parts and relative.parts[0] == evidence_dir.name:
        relative = Path(*relative.parts[1:])
    artifact_path = evidence_dir / relative
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    payload = b"external validation log placeholder without secrets\n"
    artifact_path.write_bytes(payload)

    ledger = build_validation_evidence_ledger(repo_root(), evidence_dir)
    present = next(
        artifact for artifact in ledger.artifacts if artifact.artifact_id == expected.artifact_id
    )

    assert ledger.present_count == 1
    assert ledger.ready_for_evidence_review is True
    assert present.status == "present"
    assert present.sha256 == hashlib.sha256(payload).hexdigest()
    assert present.byte_count == len(payload)
    assert present.raw_content_included is False
    assert present.content_inspected is False
    assert "external validation log" not in present.model_dump_json()


def test_gap_closure_readiness_maps_evidence_but_never_closes_gaps(tmp_path: Path) -> None:
    evidence_dir = tmp_path / "validation_evidence"
    expected = build_evidence_template(repo_root()).artifacts[0]
    relative = Path(expected.filename)
    if relative.parts and relative.parts[0] == evidence_dir.name:
        relative = Path(*relative.parts[1:])
    artifact_path = evidence_dir / relative
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text("future external evidence placeholder\n", encoding="utf-8")

    readiness = assess_gap_closure_readiness(repo_root(), evidence_dir)

    assert readiness.phase == "12"
    assert readiness.gap_count >= 20
    assert readiness.gaps_with_any_evidence >= 1
    assert readiness.ready_for_gap_closure is False
    assert readiness.ready_for_production is False
    impacted = [
        status
        for status in readiness.gap_statuses
        if expected.artifact_id in status.present_artifact_ids
    ]
    assert impacted
    assert all(status.can_close_gap is False for status in impacted)
    assert all(status.human_review_required is True for status in impacted)


def test_validation_evidence_export_writes_ledger_files(tmp_path: Path) -> None:
    result = export_validation_evidence_ledger(
        repo_root(),
        tmp_path / "validation_evidence",
        tmp_path / "ledger_export",
    )

    assert result.phase == "12"
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    written_names = {Path(path).name for path in result.written_files}
    assert {
        "validation_evidence_ledger.json",
        "gap_closure_readiness.json",
        "VALIDATION_EVIDENCE_LEDGER.md",
        "validation_evidence_manifest.json",
    }.issubset(written_names)
    manifest = json.loads(
        (tmp_path / "ledger_export" / "validation_evidence_manifest.json").read_text()
    )
    assert manifest["ready_for_gap_closure"] is False
    assert manifest["ready_for_production"] is False


def test_validation_evidence_verifier_is_codex_ready_but_not_production_ready() -> None:
    result = verify_validation_evidence_readiness(repo_root())

    assert result.phase == "12"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.network_used is False
    assert result.external_actions_executed_by_ledger is False
    assert result.hosted_ci_executed is False
    assert result.clean_install_validation_executed is False
    assert result.live_provider_validation_executed is False
    assert result.mcp_browser_runtime_validation_executed is False
    assert result.active_validation_used is False
    assert result.report_submission_used is False
    check_ids = {check.check_id for check in result.checks}
    assert "EVIDENCE-TEMPLATE-COVERAGE" in check_ids
    assert "EVIDENCE-GAP-MAPPING-COVERAGE" in check_ids
    assert "EVIDENCE-EXTERNAL-ARTIFACTS-STILL-OPEN" in check_ids


def test_validation_evidence_cli_commands_render_json(tmp_path: Path) -> None:
    root = str(repo_root())
    evidence_dir = str(tmp_path / "validation_evidence")

    ledger = runner.invoke(
        app,
        ["validation-evidence", "ledger", "--root", root, "--evidence-dir", evidence_dir, "--json"],
    )
    assert ledger.exit_code == 0, ledger.output
    ledger_payload = json.loads(ledger.output)
    assert ledger_payload["phase"] == "12"
    assert ledger_payload["ready_for_gap_closure"] is False

    readiness = runner.invoke(
        app,
        [
            "validation-evidence",
            "gap-readiness",
            "--root",
            root,
            "--evidence-dir",
            evidence_dir,
            "--json",
        ],
    )
    assert readiness.exit_code == 0, readiness.output
    readiness_payload = json.loads(readiness.output)
    assert readiness_payload["phase"] == "12"
    assert readiness_payload["ready_for_gap_closure"] is False

    export = runner.invoke(
        app,
        [
            "validation-evidence",
            "export-ledger",
            "--root",
            root,
            "--evidence-dir",
            evidence_dir,
            "--output",
            str(tmp_path / "exported"),
            "--json",
        ],
    )
    assert export.exit_code == 0, export.output
    export_payload = json.loads(export.output)
    assert export_payload["phase"] == "12"
    assert export_payload["ready_for_production"] is False

    verify = runner.invoke(
        app,
        ["validation-evidence", "verify", "--root", root, "--evidence-dir", evidence_dir, "--json"],
    )
    assert verify.exit_code == 0, verify.output
    verify_payload = json.loads(verify.output)
    assert verify_payload["ready_for_commit"] is True
    assert verify_payload["ready_for_codex"] is True
    assert verify_payload["ready_for_production"] is False


def test_ci_workflow_includes_phase12_validation_evidence_verifier() -> None:
    workflow = (repo_root() / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "python scripts/phase9_verify.py --root ." in workflow
    assert "python scripts/phase10_verify.py --root ." in workflow
    assert "python scripts/phase11_verify.py --root ." in workflow
    assert "python scripts/phase12_verify.py --root ." in workflow
