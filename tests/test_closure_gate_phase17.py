from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.closure_gate import (
    ReadinessAttestationFile,
    ReadinessAttestationRecord,
    assess_closure_gate_status,
    build_readiness_attestation_template,
    export_closure_gate_package,
    verify_closure_gate_readiness,
)
from bountyclaw.gap_tracker import audit_gap_tracker
from bountyclaw.handoff import export_handoff_package
from bountyclaw.validation_baseline import build_validation_baseline_manifest

runner = CliRunner()


def test_attestation_template_is_metadata_only_and_non_closing() -> None:
    result = build_readiness_attestation_template(Path("."))

    assert result.phase == "17"
    assert result.source_phase == "16"
    assert result.ready_for_human_attestation is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.raw_evidence_contents_included is False
    assert result.raw_source_contents_included is False
    assert result.template.auto_gap_closure_allowed is False
    assert result.template.production_readiness_increase_allowed is False
    assert result.template.attestations[0].decision == "pending"


def test_missing_attestation_blocks_candidate_gaps_without_external_claims(tmp_path: Path) -> None:
    result = assess_closure_gate_status(Path("."), attestation_file=tmp_path / "missing.json")

    assert result.phase == "17"
    assert result.attestation_count == 0
    assert result.accepted_attestation_count == 0
    assert result.candidate_gap_ids == []
    assert result.ready_for_human_gap_update_review is False
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.raw_evidence_contents_included is False
    assert result.raw_source_contents_included is False


def test_approved_attestation_can_create_manual_update_candidate_without_closing_gap(
    tmp_path: Path,
) -> None:
    baseline = build_validation_baseline_manifest(Path("."))
    gap_id = audit_gap_tracker(Path(".")).entries[0].gap_id
    attestation = ReadinessAttestationFile(
        attestations=[
            ReadinessAttestationRecord(
                attestation_id="ATTEST-001",
                baseline_id=baseline.baseline_id,
                decision="approved_for_manual_gap_update",
                reviewer="appsec-reviewer",
                reviewed_at_utc="2026-06-02T00:00:00Z",
                rationale="Human AppSec reviewer approved metadata for manual gap tracker update only.",
                approved_gap_ids=[gap_id],
                referenced_evidence_artifact_ids=["ARTIFACT-001"],
                referenced_run_ids=["RUN-001"],
                evidence_review_decision_sha256="a" * 64,
                execution_journal_sha256="b" * 64,
                gap_tracker_sha256="c" * 64,
            )
        ]
    )
    path = tmp_path / "readiness_attestations.json"
    path.write_text(attestation.model_dump_json(indent=2), encoding="utf-8")

    result = assess_closure_gate_status(Path("."), attestation_file=path)

    assert result.accepted_attestation_count == 1
    assert result.candidate_gap_ids == [gap_id]
    assert result.ready_for_human_gap_update_review is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    status = result.attestation_statuses[0]
    assert status.status == "candidate"
    assert status.accepted_for_manual_gap_update_proposal is True
    assert status.auto_gap_closure_allowed is False
    assert status.production_readiness_increase_allowed is False


def test_attestation_baseline_mismatch_blocks_candidate(tmp_path: Path) -> None:
    gap_id = audit_gap_tracker(Path(".")).entries[0].gap_id
    attestation = ReadinessAttestationFile(
        attestations=[
            ReadinessAttestationRecord(
                attestation_id="ATTEST-BAD-BASELINE",
                baseline_id="0" * 64,
                decision="approved_for_manual_gap_update",
                reviewer="appsec-reviewer",
                reviewed_at_utc="2026-06-02T00:00:00Z",
                rationale="Human reviewer metadata fixture with intentionally mismatched baseline.",
                approved_gap_ids=[gap_id],
                referenced_evidence_artifact_ids=["ARTIFACT-001"],
                referenced_run_ids=["RUN-001"],
                evidence_review_decision_sha256="a" * 64,
                execution_journal_sha256="b" * 64,
                gap_tracker_sha256="c" * 64,
            )
        ]
    )
    path = tmp_path / "attestation.json"
    path.write_text(attestation.model_dump_json(indent=2), encoding="utf-8")

    result = assess_closure_gate_status(Path("."), attestation_file=path)

    assert result.accepted_attestation_count == 0
    assert result.candidate_gap_ids == []
    assert result.attestation_statuses[0].status == "blocked"
    assert "baseline_id" in "; ".join(result.attestation_statuses[0].blockers)


def test_attestation_models_reject_raw_content_and_auto_closure_flags() -> None:
    with pytest.raises(ValidationError):
        ReadinessAttestationRecord(
            attestation_id="ATTEST-BAD",
            raw_evidence_contents_included=True,  # type: ignore[arg-type]
        )
    with pytest.raises(ValidationError):
        ReadinessAttestationFile(
            auto_gap_closure_allowed=True,  # type: ignore[arg-type]
        )


def test_closure_gate_export_and_handoff_include_commands(tmp_path: Path) -> None:
    output = tmp_path / "closure_gate"
    result = export_closure_gate_package(Path("."), output)

    assert result.phase == "17"
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    written = {Path(path).name for path in result.written_files}
    assert {
        "readiness_attestation_template.json",
        "closure_gate_status.json",
        "CLOSURE_GATE.md",
        "CLOSURE_GATE_COMMANDS.md",
        "closure_gate_index.json",
    }.issubset(written)
    commands = (output / "CLOSURE_GATE_COMMANDS.md").read_text(encoding="utf-8")
    assert "closure-gate verify" in commands
    assert "do not inspect raw evidence" in commands.lower()

    handoff_output = tmp_path / "handoff"
    handoff = export_handoff_package(Path("."), handoff_output)
    assert "CLOSURE_GATE_COMMANDS.md" in {Path(path).name for path in handoff.written_files}
    handoff_commands = (handoff_output / "CLOSURE_GATE_COMMANDS.md").read_text(encoding="utf-8")
    assert "phase17_verify.py" in handoff_commands


def test_closure_gate_verifier_is_commit_ready_but_not_production_ready() -> None:
    result = verify_closure_gate_readiness(Path("."))

    assert result.phase == "17"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.raw_evidence_contents_included is False
    assert result.raw_source_contents_included is False


def test_closure_gate_cli_json_smoke(tmp_path: Path) -> None:
    commands = [
        ["closure-gate", "attestation-template", "--root", ".", "--json"],
        [
            "closure-gate",
            "status",
            "--root",
            ".",
            "--attestation-file",
            str(tmp_path / "missing.json"),
            "--json",
        ],
        ["closure-gate", "export", "--root", ".", "--output", str(tmp_path / "export"), "--json"],
        ["closure-gate", "verify", "--root", ".", "--json"],
    ]
    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["phase"] == "17"
        assert payload["ready_for_production"] is False
