from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from bountyclaw.browser_controller import (
    BrowserAuthorizationError,
    BrowserFeatureGateError,
    ingest_authorized_policy,
)
from bountyclaw.cli import app
from bountyclaw.mcp_gateway import (
    POLICY_LOCAL_FILE_TOOL_ID,
    McpAuthorizationError,
    McpFeatureGateError,
    McpToolSelectionError,
    invoke_authorized_mcp_tool,
    list_mcp_servers,
    list_mcp_tools,
)
from bountyclaw.policy import PolicyDocumentError, read_local_policy_summary
from bountyclaw.scope import ScopeGate, Target, TargetKind, load_scope_manifest

runner = CliRunner()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def handler(value):\n    return value\n", encoding="utf-8")
    return repo


def make_policy(tmp_path: Path) -> Path:
    policy = tmp_path / "policy.md"
    policy.write_text(
        "# Authorized Program Policy\n"
        "Safe harbor applies to good faith testing.\n"
        "In scope targets include the fixture repository only.\n"
        "Out of scope: denial of service, brute force, social engineering, and spam.\n"
        "Disclosure reports must be manually submitted through the program form.\n"
        "api_key = sk-testsecretvalue-that-must-not-leak\n",
        encoding="utf-8",
    )
    return policy


def write_manifest(
    tmp_path: Path,
    repo: Path,
    policy: Path | None = None,
    *,
    allowed_actions: list[str] | None = None,
    use_policy_url_only: bool = False,
) -> Path:
    program = {
        "name": "Authorized Phase 7 Fixture",
        "disclosure_rules": ["manual report submission only"],
    }
    if use_policy_url_only:
        program["policy_url"] = "https://example.invalid/policy"
    else:
        program["policy_file"] = str(policy or make_policy(tmp_path))

    manifest = {
        "manifest_version": "1",
        "program": program,
        "authorization": {
            "operator": "phase7-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for Phase 7 testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo),
                    "label": "fixture",
                    "allowed_actions": allowed_actions
                    or [
                        "repo.read",
                        "mcp.tool.invoke",
                        "browser.policy_ingest",
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


def test_policy_reader_redacts_and_summarizes_without_network(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)

    summary = read_local_policy_summary(loaded_scope)

    assert summary.source_kind == "local_file"
    assert summary.network_used is False
    assert summary.live_browser_used is False
    assert summary.live_mcp_server_used is False
    assert summary.scope_expansion_allowed is False
    assert summary.redaction_count >= 1
    assert "sk-testsecretvalue" not in json.dumps(summary.model_dump())
    assert {signal.kind for signal in summary.signals} >= {
        "safe_harbor_hint",
        "allowed_target_hint",
        "out_of_scope_hint",
        "disclosure_rule_hint",
    }


def test_mcp_registry_is_fixture_only_and_no_network() -> None:
    servers = list_mcp_servers()
    tools = list_mcp_tools()

    assert servers
    assert tools
    assert all(server.network_allowed is False for server in servers)
    assert all(server.live_process_allowed is False for server in servers)
    assert all(tool.network_required is False for tool in tools)
    assert all(tool.report_submission_allowed is False for tool in tools)
    assert POLICY_LOCAL_FILE_TOOL_ID in {tool.tool_id for tool in tools}


def test_mcp_invocation_requires_feature_gate_and_scope_action(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(McpFeatureGateError):
        invoke_authorized_mcp_tool(
            loaded_scope,
            repo,
            tool_id=POLICY_LOCAL_FILE_TOOL_ID,
            fixture_tool_enabled=False,
        )

    manifest_without_mcp = write_manifest(
        tmp_path,
        repo,
        policy,
        allowed_actions=["repo.read", "browser.policy_ingest"],
    )
    loaded_without_mcp = load_scope_manifest(manifest_without_mcp)
    with pytest.raises(McpAuthorizationError) as exc:
        invoke_authorized_mcp_tool(
            loaded_without_mcp,
            repo,
            tool_id=POLICY_LOCAL_FILE_TOOL_ID,
            fixture_tool_enabled=True,
        )

    assert exc.value.decision.action == "mcp.tool.invoke"
    assert exc.value.decision.allowed is False


def test_mcp_invocation_denies_unregistered_tools(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(McpToolSelectionError):
        invoke_authorized_mcp_tool(
            loaded_scope,
            repo,
            tool_id="unregistered.evil_tool",
            fixture_tool_enabled=True,
        )


def test_mcp_invocation_uses_only_fixture_policy_tool(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)

    result = invoke_authorized_mcp_tool(
        loaded_scope,
        repo,
        tool_id=POLICY_LOCAL_FILE_TOOL_ID,
        fixture_tool_enabled=True,
    )

    assert result.fixture_tool_used is True
    assert result.live_mcp_server_used is False
    assert result.external_process_used is False
    assert result.network_used is False
    assert result.live_target_contact_used is False
    assert result.browser_used is False
    assert result.report_submission_used is False
    assert result.submission_allowed is False
    assert result.policy_summary.redaction_count >= 1


def test_browser_policy_ingestion_requires_feature_gate_and_scope_action(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(BrowserFeatureGateError):
        ingest_authorized_policy(loaded_scope, repo, fixture_browser_enabled=False)

    manifest_without_browser = write_manifest(
        tmp_path,
        repo,
        policy,
        allowed_actions=["repo.read", "mcp.tool.invoke"],
    )
    loaded_without_browser = load_scope_manifest(manifest_without_browser)
    with pytest.raises(BrowserAuthorizationError) as exc:
        ingest_authorized_policy(loaded_without_browser, repo, fixture_browser_enabled=True)

    assert exc.value.decision.action == "browser.policy_ingest"
    assert exc.value.decision.allowed is False


def test_browser_policy_ingestion_is_fixture_only_and_non_submitting(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)

    result = ingest_authorized_policy(loaded_scope, repo, fixture_browser_enabled=True)

    assert result.fixture_parser_used is True
    assert result.live_browser_used is False
    assert result.network_used is False
    assert result.live_target_contact_used is False
    assert result.form_submission_used is False
    assert result.active_validation_used is False
    assert result.report_submission_used is False
    assert result.submission_allowed is False
    assert result.workflow_plan.network_allowed is False
    assert result.workflow_plan.scope_expansion_allowed is False


def test_policy_ingestion_refuses_url_only_scope_in_phase7(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, use_policy_url_only=True)
    loaded_scope = load_scope_manifest(manifest_path)

    with pytest.raises(PolicyDocumentError):
        ingest_authorized_policy(loaded_scope, repo, fixture_browser_enabled=True)


def test_scope_gate_denies_prohibited_mcp_browser_and_submission_actions(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)
    loaded_scope = load_scope_manifest(manifest_path)
    gate = ScopeGate(loaded_scope)
    target = Target(kind=TargetKind.LOCAL_REPO, value=str(repo))

    for action in [
        "mcp.unregistered_tool",
        "mcp.external_server.invoke",
        "browser.form_submit",
        "browser.live_target_contact",
        "bounty.submit.auto",
    ]:
        decision = gate.evaluate(action, target)
        assert decision.allowed is False
        assert decision.decision == "deny"


def test_mcp_and_browser_cli_outputs_json(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    policy = make_policy(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, policy)

    servers = runner.invoke(app, ["mcp", "servers", "--json"])
    assert servers.exit_code == 0, servers.output
    assert json.loads(servers.output)[0]["network_allowed"] is False

    tools = runner.invoke(app, ["mcp", "tools", "--json"])
    assert tools.exit_code == 0, tools.output
    assert json.loads(tools.output)[0]["tool_id"] == POLICY_LOCAL_FILE_TOOL_ID

    mcp_result = runner.invoke(
        app,
        [
            "mcp",
            "invoke",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--enable-mcp-fixture",
            "--json",
        ],
    )
    assert mcp_result.exit_code == 0, mcp_result.output
    mcp_payload = json.loads(mcp_result.output)
    assert mcp_payload["live_mcp_server_used"] is False
    assert mcp_payload["network_used"] is False
    assert mcp_payload["report_submission_used"] is False

    browser_result = runner.invoke(
        app,
        [
            "browser",
            "policy-ingest",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--enable-browser-fixture",
            "--json",
        ],
    )
    assert browser_result.exit_code == 0, browser_result.output
    browser_payload = json.loads(browser_result.output)
    assert browser_payload["live_browser_used"] is False
    assert browser_payload["network_used"] is False
    assert browser_payload["form_submission_used"] is False
