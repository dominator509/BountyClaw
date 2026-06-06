from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.quality_gates import (
    build_quality_gate_checklist,
    export_quality_gate_package,
    verify_quality_gate_readiness,
)

runner = CliRunner()
ROOT = Path(__file__).resolve().parents[1]


def test_quality_gate_checklist_records_local_passes_and_pip_audit_deferral() -> None:
    result = build_quality_gate_checklist(ROOT)

    assert result.phase == "19"
    assert result.failed_count == 0
    assert result.passed_count >= 8
    assert result.deferred_count == 1
    assert not result.ready_for_production
    deferred = [gate for gate in result.gates if gate.local_execution_status == "deferred"]
    assert len(deferred) == 1
    assert deferred[0].gate_id == "P19-GATE-009"
    assert "pypi.org" in (deferred[0].environment_limitation or "")


def test_quality_gate_verifier_is_commit_ready_but_not_production_ready() -> None:
    result = verify_quality_gate_readiness(ROOT)

    assert result.phase == "19"
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.ready_for_commit
    assert result.ready_for_codex
    assert not result.ready_for_production
    assert not result.network_used
    assert not result.external_actions_executed
    assert not result.raw_evidence_contents_included


def test_quality_gate_export_is_metadata_only(tmp_path: Path) -> None:
    result = export_quality_gate_package(ROOT, tmp_path / "quality")

    assert result.ready_for_commit
    assert result.ready_for_codex
    assert not result.ready_for_production
    written = {Path(path).name for path in result.written_files}
    assert "quality_gate_checklist.json" in written
    assert "quality_gate_verification.json" in written
    assert "QUALITY_GATES_PHASE19.md" in written


def test_quality_gate_cli_commands_render_json(tmp_path: Path) -> None:
    checklist = runner.invoke(app, ["quality-gates", "checklist", "--root", str(ROOT), "--json"])
    assert checklist.exit_code == 0
    assert '"phase": "19"' in checklist.stdout

    verify = runner.invoke(app, ["quality-gates", "verify", "--root", str(ROOT), "--json"])
    assert verify.exit_code == 0
    assert '"ready_for_commit": true' in verify.stdout
    assert '"ready_for_production": false' in verify.stdout

    export = runner.invoke(
        app,
        [
            "quality-gates",
            "export",
            "--root",
            str(ROOT),
            "--output",
            str(tmp_path / "quality-export"),
            "--json",
        ],
    )
    assert export.exit_code == 0
    assert '"phase": "19"' in export.stdout


def test_quality_gate_ci_hook_present() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "ruff format --check src tests scripts" in workflow
    assert "scripts/phase19_verify.py" in workflow
