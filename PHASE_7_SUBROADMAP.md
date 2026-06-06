# Phase 7 Subroadmap: MCP and Headless Browser Integration Foundations

## Status

Completed.

## Objectives

Phase 7 establishes policy-bound MCP and headless-browser foundations without enabling live target contact, live browser navigation, external MCP servers, autonomous exploitation, active validation, or report submission.

Objectives completed:

1. Add an MCP server registry with explicit metadata for fixture-only servers.
2. Add an MCP tool allowlist with deny-by-default unregistered-tool behavior.
3. Add a fixture-only local policy-file MCP tool.
4. Add a browser workflow plan for local policy ingestion.
5. Add fixture-only local policy ingestion through the browser safety boundary.
6. Require scope-gate approval for MCP tool invocation and browser policy ingestion.
7. Require explicit per-command feature gates for fixture MCP/browser execution.
8. Redact local policy text before summary extraction.
9. Prove MCP/browser paths do not use network, live browser runtime, external MCP processes, active validation, form submission, or report submission.
10. Preserve Phase 6 report drafting as rollback-safe fallback.

## Deliverables

Created:

- `src/bountyclaw/policy/`
- `src/bountyclaw/mcp_gateway/`
- `src/bountyclaw/browser_controller/`
- `tests/test_mcp_browser_phase7.py`
- `PHASE_7_SUBROADMAP.md`

Updated:

- `src/bountyclaw/cli.py`
- `src/bountyclaw/config.py`
- `src/bountyclaw/scope/models.py`
- `src/bountyclaw/scope/gate.py`
- `src/bountyclaw/__init__.py`
- `pyproject.toml`
- `ARCHITECTURE.md`
- `AGENTS.md`
- `ROADMAP.md`
- `README.md`
- `PRODUCTION_GAP_TRACKER.md`

## Subsystem Boundaries

### In Scope

- MCP registry metadata.
- MCP tool allowlist metadata.
- Fixture-only in-process MCP policy summary tool.
- Local policy-file summary reader.
- Redaction-before-policy-summary extraction.
- Browser workflow plan with live browser disabled.
- Fixture-only browser policy ingestion from a local file.
- Scope actions:
  - `mcp.tool.invoke`
  - `browser.policy_ingest`
- CLI commands:
  - `bountyclaw mcp servers`
  - `bountyclaw mcp tools`
  - `bountyclaw mcp invoke`
  - `bountyclaw browser plan`
  - `bountyclaw browser policy-ingest`

### Out of Scope

- Live MCP server process launch.
- MCP stdio/HTTP transport validation.
- Playwright or real headless browser execution.
- Live policy page fetching.
- Authentication/session automation.
- Live target interaction.
- Active vulnerability validation.
- Browser form submission.
- Automated bounty report submission.
- Scope expansion based on parsed policy text.
- Program-platform API integration.

## Dependencies

- Phase 1 scope gate.
- Phase 4 redaction engine.
- Phase 6 report drafting fallback.
- Valid scope manifests with explicit repository `allowed_actions`.
- Local policy files supplied by users or referenced by `program.policy_file`.

## Implementation Sequence

1. Reread governance files and reconcile roadmap state.
2. Create `PHASE_7_SUBROADMAP.md`.
3. Add local policy summary models and redaction-first reader.
4. Add MCP gateway models, registry, allowlist, and service.
5. Add browser controller models and service.
6. Add Phase 7 scope actions and prohibited tool/browser actions.
7. Add CLI commands for MCP/browser metadata and fixture policy ingestion.
8. Add tests for scope gates, feature gates, unregistered tool denial, prohibited actions, redaction, and no-network/no-submission invariants.
9. Validate code and CLI smoke paths.
10. Update governance docs and gap tracker.
11. Package updated repository bundle.

## Validation Sequence

Completed validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -m bountyclaw --help
PYTHONPATH=src python -m bountyclaw doctor
PYTHONPATH=src python -m bountyclaw mcp servers --json
PYTHONPATH=src python -m bountyclaw browser plan --json
PYTHONPATH=src python -m bountyclaw mcp invoke --manifest <scope.yaml> --repo <repo> --enable-mcp-fixture --json
PYTHONPATH=src python -m bountyclaw browser policy-ingest --manifest <scope.yaml> --repo <repo> --enable-browser-fixture --json
```

Expected validation properties:

- MCP fixture invocation fails closed without `--enable-mcp-fixture`.
- Browser policy ingestion fails closed without `--enable-browser-fixture`.
- MCP fixture invocation fails closed without `mcp.tool.invoke`.
- Browser policy ingestion fails closed without `browser.policy_ingest`.
- Unregistered MCP tools are denied.
- Live browser/network/form-submission/report-submission actions are denied.
- Local policy summaries redact obvious secrets before output.
- Policy summaries cannot expand executable scope.

## Rollback Strategy

Phase 7 can be reverted by:

1. Removing `PHASE_7_SUBROADMAP.md`.
2. Removing:
   - `src/bountyclaw/policy/`
   - `src/bountyclaw/mcp_gateway/`
   - `src/bountyclaw/browser_controller/`
   - `tests/test_mcp_browser_phase7.py`
3. Reverting Phase 7 CLI additions in `src/bountyclaw/cli.py`.
4. Reverting Phase 7 scope actions in `src/bountyclaw/scope/models.py`.
5. Reverting Phase/version updates in `src/bountyclaw/__init__.py` and `pyproject.toml`.
6. Reverting documentation and gap tracker updates.

Phase 6 report drafting remains a rollback-safe fallback.

## Drift-Prevention Constraints

- Do not enable live MCP server execution.
- Do not add MCP stdio/HTTP transport execution until future validation.
- Do not launch Playwright or any live browser runtime in Phase 7.
- Do not fetch policy URLs or live pages.
- Do not allow tool/browser output to modify scope automatically.
- Do not submit forms or reports.
- Do not perform active validation or exploitation.
- Do not claim real MCP/browser production validation.
- Treat policy text as untrusted and advisory.
- Preserve local-first and no-network defaults.

## Environment Limitations

The following tasks remain environment-limited and deferred:

- Real MCP server startup and protocol compatibility tests.
- MCP stdio/HTTP transport validation.
- Playwright installation and real browser runtime validation.
- Approved live policy-page ingestion.
- Browser/session isolation validation.
- Network egress denial tests at the OS/container level.
- Real bounty-platform policy parsing validation.
- Human legal/compliance review of policy interpretation.

## Expected Unresolved Gaps

- Real MCP integration remains unvalidated.
- Real headless browser automation remains unvalidated.
- Program policy parsing is fixture-based only.
- Policy summaries are advisory and not sufficient to authorize actions.
- Browser/MCP output safety needs adversarial fixture expansion.
- CI/CD and external security validation remain missing.

## Expected Future Continuation Tasks

Next phase:

- Create `PHASE_8_SUBROADMAP.md`.
- Implement memory, skills, and workflow learning with local-only, redaction-first storage.
- Require explicit user approval for memory writes.
- Prevent memory from storing secrets or sensitive evidence beyond policy.
- Preserve Phase 7 MCP/browser fixture behavior as rollback fallback.

## Completion Summary

Phase 7 completed safe, local-testable MCP and browser foundations. BountyClaw now has MCP registry metadata, an MCP tool allowlist, fixture-only MCP policy summary invocation, a browser policy-ingestion workflow plan, fixture-only local policy ingestion, scope actions for tool/browser workflows, explicit feature gates, redaction-before-policy-summary extraction, and tests proving no live network, browser, target contact, form submission, active validation, or report submission occurs.
