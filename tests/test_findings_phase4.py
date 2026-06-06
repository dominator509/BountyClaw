from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.findings import (
    EvidenceStore,
    EvidenceStorePathError,
    FindingsAuthorizationError,
    collect_authorized_findings,
    normalize_scanner_run,
    redact_text,
)
from bountyclaw.scanning import ScannerFeatureGateError, scan_authorized_repository
from bountyclaw.scanning.models import PreliminaryFinding, ScannerRunResult, ScannerSpec
from bountyclaw.scope import load_scope_manifest

runner = CliRunner()

RAW_AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
RAW_GITHUB_TOKEN = "ghp_abcdefghijklmnopqrstuvwxyzABCDE1234567890"
RAW_GENERIC_SECRET = "supersecret123456"


def make_python_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "app.py").write_text(
        "def dangerous(payload):\n    return eval(payload)\n",
        encoding="utf-8",
    )
    (repo / "pyproject.toml").write_text("[project]\nname='phase4-fixture'\n", encoding="utf-8")
    return repo


def write_manifest(
    tmp_path: Path,
    repo_path: Path,
    *,
    allowed_actions: list[str] | None = None,
) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {"name": "Phase 4 Fixture Program", "policy_file": "policy.md"},
        "authorization": {
            "operator": "phase4-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for phase four testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo_path),
                    "allowed_actions": allowed_actions
                    or ["repo.read", "scan.local_static", "findings.write"],
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


def synthetic_scan_result(secret_text: str = RAW_GENERIC_SECRET) -> ScannerRunResult:
    spec = ScannerSpec(
        scanner_id="fixture.scanner",
        name="Fixture Scanner",
        version="1.0.0",
        adapter_family="fixture.static",
        execution_mode="local_builtin",
    )
    finding = PreliminaryFinding(
        finding_id="prelim-1",
        scanner_id="fixture.scanner",
        scanner_version="1.0.0",
        rule_id="fixture.secret-like-evidence",
        title="Fixture candidate finding",
        description="Fixture description",
        severity="medium",
        confidence="high",
        target="/tmp/repo",
        file_path="src/app.py",
        line_number=3,
        evidence_summary=f"Rule matched with api_key={secret_text} and {RAW_AWS_KEY}",
        cwe="CWE-200",
        remediation_hint="Remove token=anothersecretvalue before disclosure.",
    )
    duplicate = finding.model_copy(update={"finding_id": "prelim-2"})
    return ScannerRunResult(
        scan_execution_id="scan-fixture-1",
        repository="/tmp/repo",
        repository_fingerprint_id="repo-fingerprint-1",
        adapters=[spec],
        findings=[finding, duplicate],
        notes=["fixture scan result"],
    )


def test_redaction_redacts_common_secret_shapes_without_metadata_leakage() -> None:
    text = (
        f"aws={RAW_AWS_KEY} github={RAW_GITHUB_TOKEN} "
        f"api_key={RAW_GENERIC_SECRET} Authorization: Bearer abcdefghijklmnopqrstuvwxyz123456"
    )

    result = redact_text(text)

    assert result.redaction_status == "redacted"
    assert result.redaction_count >= 4
    assert RAW_AWS_KEY not in result.redacted_text
    assert RAW_GITHUB_TOKEN not in result.redacted_text
    assert RAW_GENERIC_SECRET not in result.redacted_text
    serialized_metadata = result.model_dump_json()
    assert RAW_AWS_KEY not in serialized_metadata
    assert RAW_GITHUB_TOKEN not in serialized_metadata
    assert RAW_GENERIC_SECRET not in serialized_metadata


def test_normalizer_deduplicates_preliminary_findings_and_redacts_evidence() -> None:
    result = synthetic_scan_result()

    normalized = normalize_scanner_run(result)

    assert len(normalized.canonical_findings) == 1
    canonical = normalized.canonical_findings[0]
    assert canonical.evidence_count == 2
    assert sorted(canonical.source_preliminary_ids) == ["prelim-1", "prelim-2"]
    assert canonical.report_readiness_status == "needs_human_triage"
    assert normalized.redaction_count >= 4
    persisted_payload = normalized.model_dump_json()
    assert RAW_GENERIC_SECRET not in persisted_payload
    assert RAW_AWS_KEY not in persisted_payload
    assert all(
        evidence.source_excerpt_included is False for evidence in normalized.evidence_records
    )


def test_evidence_store_persists_redacted_text_only(tmp_path: Path) -> None:
    scan_result = synthetic_scan_result()
    normalized = normalize_scanner_run(scan_result)
    store = EvidenceStore(tmp_path / "evidence.sqlite")

    store.write_scan_run(scan_result, normalized)

    summaries = store.list_findings()
    assert len(summaries) == 1
    assert summaries[0].evidence_count == 2
    raw_database_text = store.raw_database_text()
    assert RAW_GENERIC_SECRET not in raw_database_text
    assert RAW_AWS_KEY not in raw_database_text
    assert "[REDACTED:" in raw_database_text


def test_collect_authorized_findings_requires_findings_write_scope(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(
        tmp_path, repo, allowed_actions=["repo.read", "scan.local_static"]
    )
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(FindingsAuthorizationError) as exc:
        collect_authorized_findings(
            loaded_scope,
            repo,
            store_path=tmp_path / "evidence.sqlite",
            local_scanner_enabled=True,
        )

    assert exc.value.decision.action == "findings.write"
    assert exc.value.decision.allowed is False


def test_collect_authorized_findings_requires_local_scanner_feature_gate(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(ScannerFeatureGateError):
        collect_authorized_findings(loaded_scope, repo, store_path=tmp_path / "evidence.sqlite")


def test_collect_authorized_findings_writes_store_outside_repository_only(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)
    store_path = tmp_path / "state" / "evidence.sqlite"

    result = collect_authorized_findings(
        loaded_scope,
        repo,
        store_path=store_path,
        local_scanner_enabled=True,
    )

    assert Path(result.store_path).exists()
    assert len(result.canonical_findings) == 1
    assert result.network_used is False
    assert result.llm_used is False
    assert not (repo / ".bountyclaw").exists()
    with pytest.raises(EvidenceStorePathError):
        collect_authorized_findings(
            loaded_scope,
            repo,
            store_path=repo / ".bountyclaw" / "evidence.sqlite",
            local_scanner_enabled=True,
        )


def test_phase4_does_not_change_phase3_scan_json_fallback(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest_path)

    result = scan_authorized_repository(loaded_scope, repo, local_scanner_enabled=True)

    assert result.findings
    assert result.findings[0].source_excerpt_included is False
    assert result.report_submission_used is False


def test_findings_collect_and_list_cli_json(tmp_path: Path) -> None:
    repo = make_python_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    store_path = tmp_path / "store" / "evidence.sqlite"
    audit_path = tmp_path / "audit" / "events.jsonl"

    collect_result = runner.invoke(
        app,
        [
            "findings",
            "collect",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--store",
            str(store_path),
            "--enable-local-scanner",
            "--audit-log",
            str(audit_path),
            "--json",
        ],
    )

    assert collect_result.exit_code == 0
    payload = json.loads(collect_result.output)
    assert payload["network_used"] is False
    assert len(payload["canonical_findings"]) == 1
    assert payload["canonical_findings"][0]["report_readiness_status"] == "needs_human_triage"
    assert store_path.exists()
    audit_payload = json.loads(audit_path.read_text(encoding="utf-8").splitlines()[0])
    assert audit_payload["event_type"] == "findings.collect"
    assert audit_payload["decision"] == "allow"

    list_result = runner.invoke(
        app,
        ["findings", "list", "--store", str(store_path), "--json"],
    )

    assert list_result.exit_code == 0
    listed = json.loads(list_result.output)
    assert len(listed) == 1
    assert listed[0]["evidence_count"] == 1
