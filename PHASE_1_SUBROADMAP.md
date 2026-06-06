# Phase 1 Subroadmap: CLI Skeleton and Safety Gate Foundation

## 1. Phase Status

Status: Completed.

Production readiness after phase: 8%.

## 2. Objectives

Completed objectives:

- Created the minimal local Python CLI skeleton for BountyClaw.
- Implemented configuration loading with local-first safety defaults.
- Implemented a structured scope manifest schema.
- Implemented deny-by-default scope validation for privileged actions.
- Implemented an initial local audit event model and JSONL writer.
- Added CLI smoke tests and scope-gate unit tests.
- Preserved the prohibition on scanners, LLM calls, MCP tools, browser automation, network scanning, and automated report submission.

## 3. Deliverables

Completed deliverables:

- `README.md`
- `pyproject.toml`
- `src/bountyclaw/__init__.py`
- `src/bountyclaw/__main__.py`
- `src/bountyclaw/cli.py`
- `src/bountyclaw/config.py`
- `src/bountyclaw/audit.py`
- `src/bountyclaw/scope/__init__.py`
- `src/bountyclaw/scope/models.py`
- `src/bountyclaw/scope/loader.py`
- `src/bountyclaw/scope/gate.py`
- `tests/test_cli.py`
- `tests/test_scope_gate.py`

Deferred deliverables:

- Scanner adapters.
- Repository fingerprinting.
- Findings normalization.
- Evidence persistence.
- Secret-redaction engine.
- LLM model router.
- MCP gateway.
- Headless browser controller.
- CI/CD pipeline.
- Release packaging validation.

## 4. Subsystem Boundaries

Phase 1 touched only:

- CLI Orchestrator foundation.
- Configuration loading foundation.
- Scope and Policy Gate foundation.
- Initial audit event model.
- Tests for the above.
- Governance documents required for phase completion.

Phase 1 did not implement:

- Scanner Adapter Layer beyond no-op absence.
- LLM Reasoning Agents.
- Model Router provider calls.
- MCP Gateway.
- Headless Browser Controller.
- Findings Normalization Engine.
- Evidence Store persistence beyond initial audit JSONL helper.
- Cloud deployment.
- External target interaction.

## 5. Dependencies

Required prerequisites satisfied:

- `ARCHITECTURE.md` exists and defines local-first CLI architecture.
- `ROADMAP.md` marked Phase 1 as next before work began.
- `PHASE_0_SUBROADMAP.md` is completed.
- `AGENTS.md` defines deny-by-default and halt conditions.
- `PRODUCTION_GAP_TRACKER.md` identified the missing scope gate as the highest-risk gap.

Runtime/tooling dependencies used:

- Python 3.13.5 in this environment, compatible with the Python 3.12+ requirement.
- Typer for CLI routing.
- Rich for console output.
- Pydantic for schema validation.
- PyYAML for YAML configuration and scope manifests.
- pytest for local tests.

## 6. Implementation Sequence

Completed:

1. Created this Phase 1 subroadmap before implementation.
2. Created minimal Python package metadata.
3. Created package/module skeleton.
4. Added configuration model with disabled-by-default network, LLM, MCP, and browser flags.
5. Added scope manifest models requiring explicit authorization confirmation.
6. Added scope manifest loader with YAML/JSON support.
7. Added scope gate evaluator that fails closed for missing, invalid, out-of-scope, unknown, network, and prohibited actions.
8. Added initial audit event and JSONL writer model.
9. Added CLI commands:
   - `doctor`
   - `scope validate`
   - `scope check`
10. Added pytest coverage for CLI smoke behavior and safety-gate decisions.
11. Ran local validation.
12. Updated `ARCHITECTURE.md`, `AGENTS.md`, `ROADMAP.md`, `PHASE_1_SUBROADMAP.md`, and `PRODUCTION_GAP_TRACKER.md`.

## 7. Validation Sequence

Completed local validation:

- Imported package through test execution.
- Ran CLI help with `PYTHONPATH=src python -m bountyclaw --help`.
- Ran `doctor` command with `PYTHONPATH=src python -m bountyclaw doctor`.
- Ran pytest with `PYTHONPATH=src pytest -q`.
- Ran Python compile check with `PYTHONPATH=src python -m compileall -q src tests`.
- Verified `scope validate` accepts valid manifests.
- Verified `scope validate` rejects invalid manifests.
- Verified missing manifests fail closed.
- Verified unconfirmed authorization fails validation.
- Verified out-of-scope repository targets are denied.
- Verified prohibited actions are denied.
- Verified domain/network targets are denied in Phase 1.
- Verified approved local repository action can be allowed when explicitly scoped.
- Verified audit JSONL writer appends structured local events.

Validation result:

- `15 passed` via pytest.

Validation not performed:

- Package install from built wheel/sdist.
- External scanner validation.
- Real CI/CD validation.
- Security scanner validation with bandit/pip-audit.
- Real bug bounty program validation.
- Browser/MCP/LLM runtime validation.

## 8. Rollback Strategy

Rollback consists of removing Phase 1 runtime files and reverting governance updates:

- Remove `README.md` if it should not be retained.
- Remove `pyproject.toml`.
- Remove `src/bountyclaw/`.
- Remove `tests/`.
- Remove `PHASE_1_SUBROADMAP.md`.
- Revert `ROADMAP.md`, `ARCHITECTURE.md`, `AGENTS.md`, and `PRODUCTION_GAP_TRACKER.md` to Phase 0 state.

No database schema, infrastructure, cloud resource, external account, secret, scanner install, model credential, or persistent production state was introduced in Phase 1.

## 9. Drift-Prevention Constraints

Phase 1 complied with these constraints:

- Did not add scanner execution.
- Did not add external network actions.
- Did not add browser automation.
- Did not add MCP integration.
- Did not add LLM provider calls.
- Did not add automated bounty submission.
- Did not allow model or CLI output to modify scope safety controls.
- Did not accept implicit authorization.
- Did not continue past failed validation.

## 10. Environment Limitations

Observed limitations inside ChatGPT Project Mode/local workspace:

- External CI/CD could not be executed.
- Package publishing could not be validated.
- External scanner availability was not assumed.
- Live bug bounty authorization could not be verified by the environment.
- Real LLM provider credentials were unavailable.
- Browser and MCP runtimes remain deferred.
- Full dependency/security scanning tools such as ruff, mypy, bandit, and pip-audit were not available in this environment.

All unresolved environment limitations remain tracked in `PRODUCTION_GAP_TRACKER.md`.

## 11. Unresolved Gaps After Phase 1

Known unresolved gaps after Phase 1:

- No repository intake or scan planning yet.
- No scanner adapters yet.
- No findings normalization yet.
- No evidence store yet.
- No secret-redaction engine yet.
- No LLM model router yet.
- No prompt-injection validation yet.
- No report generator yet.
- No MCP/browser integrations yet.
- No CI/CD pipeline yet.
- No package artifact validation yet.
- No external production validation yet.
- Future privileged subsystems must still be wired through the scope gate before they are enabled.

## 12. Expected Future Continuation Tasks

The next phase must create `PHASE_2_SUBROADMAP.md` before implementation.

Expected Phase 2 tasks:

1. Implement read-only local repository intake.
2. Detect languages, frameworks, and package manifests.
3. Generate deterministic scan plans without executing scanners.
4. Require scope-gate approval before reading repository metadata.
5. Add fixture repositories.
6. Add tests for read-only behavior and deterministic planning.
7. Update roadmap, subroadmap, and gap tracker.

## 13. Phase Completion Notes

Phase 1 completed with a minimal executable local CLI and a fail-closed scope gate foundation. The product is not production-ready. The next safest phase is read-only local repository intake and deterministic scan planning.
