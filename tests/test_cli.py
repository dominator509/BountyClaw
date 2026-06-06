from __future__ import annotations

from pathlib import Path

import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app

runner = CliRunner()


def write_manifest(tmp_path: Path, repo_path: Path, *, confirmed: bool = True) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {
            "name": "CLI Fixture Program",
            "policy_file": "policy.md",
        },
        "authorization": {
            "operator": "cli-tester",
            "basis": "own_asset",
            "confirmed": confirmed,
            "confirmation_note": "I confirm this repository is authorized for CLI testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo_path),
                    "allowed_actions": ["repo.read", "scan.local_static"],
                }
            ],
            "domains": [],
            "out_of_scope": [],
        },
        "controls": {"network_access_enabled": False},
    }
    path = tmp_path / "scope.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def test_doctor_smoke() -> None:
    result = runner.invoke(app, ["doctor"])

    assert result.exit_code == 0
    assert "BountyClaw Doctor" in result.output
    assert "Network actions" in result.output
    assert "disabled" in result.output


def test_scope_validate_accepts_valid_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(app, ["scope", "validate", "--manifest", str(manifest_path)])

    assert result.exit_code == 0
    assert "ALLOW: scope manifest is valid" in result.output


def test_scope_validate_rejects_invalid_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo, confirmed=False)

    result = runner.invoke(app, ["scope", "validate", "--manifest", str(manifest_path)])

    assert result.exit_code == 2
    assert "DENY: scope manifest is invalid" in result.output


def test_scope_check_missing_manifest_fails_closed(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    missing_manifest = tmp_path / "missing.yaml"

    result = runner.invoke(
        app,
        [
            "scope",
            "check",
            "--manifest",
            str(missing_manifest),
            "--action",
            "scan.local_static",
            "--repo",
            str(repo),
        ],
    )

    assert result.exit_code == 2
    assert "DENY" in result.output


def test_scope_check_allows_approved_repo_action(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        [
            "scope",
            "check",
            "--manifest",
            str(manifest_path),
            "--action",
            "scan.local_static",
            "--repo",
            str(repo),
        ],
    )

    assert result.exit_code == 0
    assert "ALLOW: scan.local_static" in result.output


def test_scope_check_denies_domain_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        [
            "scope",
            "check",
            "--manifest",
            str(manifest_path),
            "--action",
            "repo.read",
            "--domain",
            "example.com",
        ],
    )

    assert result.exit_code == 2
    assert "DENY: repo.read" in result.output
    assert "network/domain targets are disabled" in result.output


def test_scope_check_writes_audit_log(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo)
    audit_path = tmp_path / "audit.jsonl"

    result = runner.invoke(
        app,
        [
            "scope",
            "check",
            "--manifest",
            str(manifest_path),
            "--action",
            "repo.read",
            "--repo",
            str(repo),
            "--audit-log",
            str(audit_path),
        ],
    )

    assert result.exit_code == 0
    assert audit_path.exists()
    assert "scope.check" in audit_path.read_text(encoding="utf-8")
