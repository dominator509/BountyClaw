from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.validation_baseline import (
    build_validation_baseline_manifest,
    export_validation_baseline_package,
    verify_validation_baseline_readiness,
)

runner = CliRunner()


def _minimal_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src" / "bountyclaw").mkdir(parents=True)
    (root / "tests").mkdir()
    (root / "scripts").mkdir()
    (root / ".github" / "workflows").mkdir(parents=True)
    for name in (
        "ARCHITECTURE.md",
        "AGENTS.md",
        "ROADMAP.md",
        "PHASE_15_SUBROADMAP.md",
        "PHASE_16_SUBROADMAP.md",
        "PRODUCTION_GAP_TRACKER.md",
        "MARKDOWN_REVIEW_PHASE16.md",
        "README.md",
        "RELEASE.md",
        "ROLLBACK.md",
        "SECURITY_VALIDATION.md",
    ):
        (root / name).write_text(
            "# " + name + "\nPhase 16 Validation Baseline Completed\nPGT-112 PGT-113 PGT-114\n",
            encoding="utf-8",
        )
    (root / "pyproject.toml").write_text(
        '[project]\nversion = "0.17.0"\n[tool.bountyclaw]\nphase = "17"\n', encoding="utf-8"
    )
    (root / ".github" / "workflows" / "ci.yml").write_text(
        "python scripts/phase16_verify.py --root .\n", encoding="utf-8"
    )
    (root / "src" / "bountyclaw" / "__init__.py").write_text(
        '__version__ = "0.17.0"\n', encoding="utf-8"
    )
    (root / "tests" / "test_example.py").write_text(
        "def test_example():\n    assert True\n", encoding="utf-8"
    )
    for i in range(9, 17):
        (root / "scripts" / f"phase{i}_verify.py").write_text("print('ok')\n", encoding="utf-8")
    return root


def test_baseline_manifest_is_hash_only_and_deterministic(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "validation_evidence").mkdir()
    (root / "validation_evidence" / "secret.txt").write_text(
        "do-not-hash-this-evidence", encoding="utf-8"
    )
    first = build_validation_baseline_manifest(root)
    second = build_validation_baseline_manifest(root)
    assert first.baseline_id == second.baseline_id
    assert first.raw_evidence_contents_included is False
    assert first.raw_source_contents_included is False
    assert all("validation_evidence" not in record.path for record in first.files)
    assert all(record.raw_contents_included is False for record in first.files)
    assert first.ready_for_external_validation_reference is True


def test_baseline_export_writes_manifest_without_raw_contents(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    output = tmp_path / "baseline_out"
    result = export_validation_baseline_package(root, output)
    assert result.ready_for_external_validation_reference is True
    manifest_payload = json.loads(
        (output / "validation_baseline_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest_payload["baseline_id"] == result.baseline_id
    assert "raw_source_contents_included" in manifest_payload
    assert "VALIDATION_BASELINE_COMMANDS.md" in {Path(path).name for path in result.written_files}


def test_baseline_cli_manifest_json_current_repo() -> None:
    result = runner.invoke(app, ["validation-baseline", "manifest", "--root", ".", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["phase"] == "16"
    assert payload["raw_evidence_contents_included"] is False
    assert payload["raw_source_contents_included"] is False


def test_baseline_cli_export_json_current_repo(tmp_path: Path) -> None:
    output = tmp_path / "export"
    result = runner.invoke(
        app,
        ["validation-baseline", "export", "--root", ".", "--output", str(output), "--json"],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["phase"] == "16"
    assert (output / "validation_baseline_manifest.json").exists()


def test_baseline_verify_current_repo() -> None:
    result = verify_validation_baseline_readiness(Path("."))
    assert result.phase == "16"
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.raw_evidence_contents_included is False
    assert result.raw_source_contents_included is False


def test_baseline_cli_verify_json_current_repo() -> None:
    result = runner.invoke(app, ["validation-baseline", "verify", "--root", ".", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["phase"] == "16"
    assert payload["ready_for_production"] is False


def test_baseline_excludes_archives_and_cache_dirs(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "build").mkdir()
    (root / "build" / "artifact.py").write_text("print('exclude')", encoding="utf-8")
    (root / "bundle.zip").write_bytes(b"zip placeholder")
    manifest = build_validation_baseline_manifest(root)
    paths = {record.path for record in manifest.files}
    assert "bundle.zip" not in paths
    assert "build/artifact.py" not in paths
