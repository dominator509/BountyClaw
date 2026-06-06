# Phase 10 Subroadmap: Production Hardening and External Validation

## Objectives

Phase 10 codifies production-hardening controls that can be implemented and locally validated inside ChatGPT Project Mode while preserving a precise ledger for every validation that requires Codex, local, CI, repository-host, sandbox, browser, model-provider, or human-review environments.

Primary objectives:

1. Add a local hardening-verification subsystem that checks governance, release-control continuity, safety invariants, scope action coverage, redaction fixtures, prompt-safety fixtures, and packaging metadata.
2. Add deterministic redaction and prompt-safety fixture corpora that are safe to run locally without external services.
3. Add explicit external-validation planning artifacts for hosted CI, clean package install, security tools, scanners, sandbox/egress, live providers, MCP/browser runtimes, report quality, performance, retention, and rollback drills.
4. Add CLI commands and a deterministic script for local Phase 10 verification.
5. Preserve Phase 9 release-control behavior as rollback-safe fallback.
6. Record all environment-limited Codex/local/CI/human tasks in `PRODUCTION_GAP_TRACKER.md` without claiming they were performed.

## Deliverables

Created:

- `PHASE_10_SUBROADMAP.md`
- `src/bountyclaw/hardening/__init__.py`
- `src/bountyclaw/hardening/models.py`
- `src/bountyclaw/hardening/service.py`
- `scripts/phase10_verify.py`
- `tests/test_hardening_phase10.py`

Updated:

- `ARCHITECTURE.md`
- `AGENTS.md`
- `ROADMAP.md`
- `PRODUCTION_GAP_TRACKER.md`
- `README.md`
- `SECURITY_VALIDATION.md`
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `src/bountyclaw/__init__.py`
- `src/bountyclaw/cli.py`
- `src/bountyclaw/config.py`
- `src/bountyclaw/scope/gate.py`
- `src/bountyclaw/scope/models.py`

## Subsystem Boundaries

### In Scope

- Local hardening checklist generation.
- Local hardening verification.
- Deterministic redaction fixture corpus.
- Deterministic prompt-safety fixture corpus.
- External validation handoff plan.
- CLI commands under `bountyclaw hardening`.
- Deterministic script `scripts/phase10_verify.py`.
- Tests for hardening result semantics, safety invariants, external deferrals, and CLI JSON output.
- Governance, security-validation, and gap-tracker updates.

### Out of Scope

- Hosted CI execution.
- Clean install from wheel/sdist in a fresh external environment.
- Ruff, mypy/pyright, bandit, pip-audit execution when tools are unavailable.
- External scanner binary installation or execution.
- Container/OS sandbox validation.
- Network-egress validation.
- Live model provider calls.
- Real MCP server/runtime validation.
- Real headless browser launch or navigation.
- Active validation, exploit execution, or live target contact.
- Automated bounty submission.
- Package signing/provenance or package publishing.
- Production deployment.

## Dependencies

Required completed dependencies:

- Phase 0 governance files.
- Phase 1 CLI/scope gate.
- Phase 2 repository intake.
- Phase 3 scanner framework.
- Phase 4 findings/evidence persistence and redaction engine.
- Phase 5 model-router and prompt-safety foundations.
- Phase 6 report drafting.
- Phase 7 MCP/browser fixture foundations.
- Phase 8 memory/skill foundations.
- Phase 9 release-control foundations.
- Existing pytest suite and release verifier.

## Implementation Sequence

1. Reconcile Phase 9 repository bundle and mandatory governance files.
2. Create `PHASE_10_SUBROADMAP.md` before implementation.
3. Add hardening models and service functions.
4. Add redaction and prompt-safety fixture corpus runners.
5. Add external validation plan generation.
6. Add CLI commands under `bountyclaw hardening`.
7. Add `scripts/phase10_verify.py` and CI workflow definition hook.
8. Update configuration, scope text, version metadata, and doctor output to Phase 10.
9. Add tests for hardening services and CLI commands.
10. Validate with pytest, compileall, CLI smoke checks, hardening verification, and ZIP extraction test.
11. Update roadmap, architecture, agents, README, security-validation ledger, and production gap tracker.

## Validation Sequence

Local validation required and completed:

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -m compileall -q src tests scripts`
- `PYTHONPATH=src python -m bountyclaw --help`
- `PYTHONPATH=src python -m bountyclaw doctor`
- `PYTHONPATH=src python -m bountyclaw hardening checklist --root . --json`
- `PYTHONPATH=src python -m bountyclaw hardening redaction-corpus --json`
- `PYTHONPATH=src python -m bountyclaw hardening prompt-corpus --json`
- `PYTHONPATH=src python -m bountyclaw hardening external-plan --json`
- `PYTHONPATH=src python -m bountyclaw hardening verify --root . --json`
- `PYTHONPATH=src python scripts/phase10_verify.py --root . --json`
- Extract generated repository ZIP and rerun pytest, compileall, and hardening verification.

Environment-limited validation recorded as gaps:

- Hosted CI execution.
- Clean package build/install validation.
- Ruff/mypy/bandit/pip-audit execution where tools are unavailable.
- External scanner binary validation.
- OS/container sandbox and network-egress validation.
- Real MCP/browser runtime validation.
- Live model provider validation.
- Human report quality and manual submission validation.
- Backup/restore, retention, performance, and rollback drills.
- Package signing/provenance and publishing validation.

## Rollback Strategy

Rollback target: Phase 9 release-control baseline.

Rollback steps:

1. Remove `PHASE_10_SUBROADMAP.md`.
2. Remove `src/bountyclaw/hardening/`.
3. Remove `scripts/phase10_verify.py`.
4. Remove `tests/test_hardening_phase10.py`.
5. Revert hardening CLI additions in `src/bountyclaw/cli.py`.
6. Revert Phase 10 version/config/scope text updates.
7. Revert `.github/workflows/ci.yml` Phase 10 verification step.
8. Revert Phase 10 governance, README, security-validation, and gap-tracker updates.

No external resources need cleanup because Phase 10 codeable work creates no cloud infrastructure, registry artifacts, hosted CI state, live provider calls, MCP/browser runtimes, active validation state, or bounty submissions.

## Drift-Prevention Constraints

- Do not claim hosted CI execution unless a real CI runner executed it.
- Do not claim clean package install validation unless a fresh environment performed it.
- Do not claim security scans ran unless tools actually executed.
- Do not enable live model providers.
- Do not enable live MCP/browser runtimes.
- Do not enable network target contact.
- Do not add active validation or report submission.
- Do not convert hardening plans into autonomous external actions.
- Preserve local-first CLI behavior and scope-gate authority.
- Preserve Phase 9 release controls as rollback fallback.

## Environment Limitations

ChatGPT Project Mode cannot provide:

- hosted repository CI execution
- branch protection
- clean package install from indexes
- package publishing credentials
- signing/provenance infrastructure
- real scanner binaries and sandbox runtimes
- real network egress firewall validation
- live LLM provider credentials and provider telemetry
- real MCP servers
- real browser runtime validation
- real bounty platform accounts
- human legal/security review
- production rollback drills over real production state

## Expected Unresolved Gaps

- Hosted CI execution remains unperformed.
- Clean package build/install validation remains unperformed.
- Static quality/security gates are defined but not executed here if tools are unavailable.
- External scanner binary validation remains unperformed.
- OS/container sandbox and egress validation remain unperformed.
- Real MCP/browser runtime validation remains unperformed.
- Live model provider validation remains unperformed.
- Broader redaction and prompt-safety validation remain unperformed.
- Real bounty-program report quality review remains unperformed.
- Operational performance, backup/restore, retention, and rollback drills remain unperformed.
- Package signing/provenance and package publishing remain unperformed.

## Expected Future Continuation Tasks

- Run hosted CI in a real repository.
- Run clean package build and install validation.
- Install dev dependencies and execute ruff, mypy/pyright, bandit, and pip-audit.
- Validate external scanner adapters in sandboxed environments.
- Validate network-egress controls.
- Validate redaction and prompt-safety against broader adversarial corpora.
- Validate live/local model providers only after no-secret payload checks.
- Validate real MCP and browser runtimes only after sandbox and allowlist enforcement.
- Perform human report quality review against authorized program policies.
- Execute performance, retention, backup/restore, and rollback drills.
- Add branch protection, signing/provenance, and publishing controls only after human release approval.

## Completion Status

Completed in ChatGPT Project Mode.

Phase 10 completion means local hardening controls, deterministic safety corpora, external validation planning, CLI commands, and local tests are implemented. It does not mean hosted CI, clean packaging, external scanner validation, sandbox validation, live provider validation, real MCP/browser validation, human report review, operational drills, package publishing, or enterprise deployment validation has been completed.
