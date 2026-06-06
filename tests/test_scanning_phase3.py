from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.scanning import (
    CommandPolicyError,
    ControlledCommandPolicy,
    ControlledSubprocessRunner,
    ScannerAuthorizationError,
    ScannerFeatureGateError,
    ScannerSelectionError,
    scan_authorized_repository,
)
from bountyclaw.scope import load_scope_manifest

runner = CliRunner()


def make_python_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "app.py").write_text(
        """
import os
import pickle
import subprocess
import tempfile
import yaml
from hashlib import md5


def dangerous(payload, blob):
    eval(payload)
    exec(payload)
    subprocess.run(payload, shell=True)
    os.system(payload)
    pickle.loads(blob)
    yaml.load(blob)
    tempfile.mktemp()
    md5(blob)
""".lstrip(),
        encoding="utf-8",
    )
    (repo / "src" / "safe.py").write_text(
        "import yaml\n\n\ndef safe(blob):\n    return yaml.safe_load(blob)\n",
        encoding="utf-8",
    )
    (repo / "pyproject.toml").write_text("[project]\nname='scan-fixture'\n", encoding="utf-8")
    return repo


def write_manifest(
    tmp_path: Path,
    repo_path: Path,
    *,
    allowed_actions: list[str] | None = None,
) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {"name": "Scanner Fixture Program", "policy_file": "policy.md"},
        "authorization": {
            "operator": "scanner-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for scanner testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo_path),
                    "allowed_actions": allowed_actions or ["repo.read", "scan.local_static"],
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


def test_builtin_python_scanner_produces_preliminary_findings_without_source_excerpts(
    tmp_path: Path,
) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    result = scan_authorized_repository(
        loaded_scope,
        repo,
        local_scanner_enabled=True,
    )

    assert result.scanners_execute is True
    assert result.network_used is False
    assert result.llm_used is False
    assert result.mcp_used is False
    assert result.browser_used is False
    assert {adapter.scanner_id for adapter in result.adapters} == {"builtin.python.static"}
    rules = {finding.rule_id for finding in result.findings}
    assert rules == {
        "python.eval-call",
        "python.exec-call",
        "python.hashlib-md5",
        "python.os-system",
        "python.pickle-load",
        "python.subprocess-shell-true",
        "python.tempfile-mktemp",
        "python.yaml-load-unsafe",
    }
    assert all(finding.source_excerpt_included is False for finding in result.findings)
    assert all("payload" not in finding.evidence_summary for finding in result.findings)
    assert all(finding.file_path == "src/app.py" for finding in result.findings)


def test_builtin_python_scanner_is_deterministic(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    first = scan_authorized_repository(loaded_scope, repo, local_scanner_enabled=True)
    second = scan_authorized_repository(loaded_scope, repo, local_scanner_enabled=True)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_scanner_service_requires_explicit_feature_gate(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(ScannerFeatureGateError):
        scan_authorized_repository(loaded_scope, repo)


def test_scanner_service_requires_scope_gate_scan_action(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, allowed_actions=["repo.read"])
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(ScannerAuthorizationError) as exc:
        scan_authorized_repository(loaded_scope, repo, local_scanner_enabled=True)

    assert exc.value.decision.action == "scan.local_static"
    assert exc.value.decision.allowed is False


def test_scanner_service_denies_unknown_scanner_before_execution(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(ScannerSelectionError):
        scan_authorized_repository(
            loaded_scope,
            repo,
            scanner_ids=["unknown.scanner"],
            local_scanner_enabled=True,
        )


def test_scanner_does_not_write_inside_repository(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    scan_authorized_repository(loaded_scope, repo, local_scanner_enabled=True)

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert before == after
    assert not (repo / ".bountyclaw").exists()


def test_scan_repo_cli_requires_explicit_feature_gate(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app, ["scan", "repo", "--manifest", str(manifest_path), "--repo", str(repo)]
    )

    assert result.exit_code == 2
    assert "DENY: local scanner execution is not enabled" in result.output


def test_scan_repo_cli_outputs_json_findings_when_authorized_and_enabled(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        [
            "scan",
            "repo",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--enable-local-scanner",
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["scanners_execute"] is True
    assert payload["network_used"] is False
    assert payload["adapters"][0]["scanner_id"] == "builtin.python.static"
    assert {finding["rule_id"] for finding in payload["findings"]} >= {
        "python.eval-call",
        "python.subprocess-shell-true",
    }


def test_scan_repo_cli_denies_unallowlisted_repo_before_scan(tmp_path: Path) -> None:
    allowed_repo = make_python_repo(tmp_path)
    other_repo = tmp_path / "other"
    other_repo.mkdir()
    (other_repo / "app.py").write_text("eval('1')\n", encoding="utf-8")
    manifest_path = write_manifest(tmp_path, allowed_repo)

    result = runner.invoke(
        app,
        [
            "scan",
            "repo",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(other_repo),
            "--enable-local-scanner",
        ],
    )

    assert result.exit_code == 2
    assert "DENY: repo.read" in result.output
    assert "not allowlisted" in result.output


def test_scan_repo_cli_writes_audit_log(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    audit_path = tmp_path / "audit" / "events.jsonl"

    result = runner.invoke(
        app,
        [
            "scan",
            "repo",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--enable-local-scanner",
            "--audit-log",
            str(audit_path),
        ],
    )

    assert result.exit_code == 0
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event_type"] == "scan.repo"
    assert payload["decision"] == "allow"


def test_controlled_subprocess_runner_allows_only_policy_approved_local_commands(
    tmp_path: Path,
) -> None:
    policy = ControlledCommandPolicy(
        allowed_executables=frozenset({Path(sys.executable).name}),
        allowed_cwd_parent=tmp_path,
        max_timeout_seconds=5,
    )
    runner = ControlledSubprocessRunner(policy)

    result = runner.run([sys.executable, "-c", "print('scanner-wrapper-ok')"], cwd=tmp_path)

    assert result.return_code == 0
    assert result.stdout.strip() == "scanner-wrapper-ok"
    assert result.cwd == str(tmp_path.resolve())


def test_controlled_subprocess_runner_denies_network_or_unallowlisted_commands(
    tmp_path: Path,
) -> None:
    policy = ControlledCommandPolicy(
        allowed_executables=frozenset({Path(sys.executable).name}),
        allowed_cwd_parent=tmp_path,
        max_timeout_seconds=5,
    )
    runner = ControlledSubprocessRunner(policy)

    with pytest.raises(CommandPolicyError, match="network-oriented"):
        runner.run([sys.executable, "-c", "print('x')", "https://example.com"], cwd=tmp_path)

    with pytest.raises(CommandPolicyError, match="not allowlisted"):
        runner.run(["curl", "https://example.com"], cwd=tmp_path)

    outside = tmp_path.parent
    with pytest.raises(CommandPolicyError, match="outside the allowed repository"):
        runner.run([sys.executable, "-c", "print('x')"], cwd=outside)
