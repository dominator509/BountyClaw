# Phase 9 Subroadmap: CI/CD, Packaging, and Release Controls

## Objectives

Phase 9 establishes deterministic release-engineering controls that are codeable inside ChatGPT Project Mode while explicitly separating local definition/validation from external CI execution and production release activities.

Primary objectives:

1. Define CI/CD workflow artifacts for tests, compile checks, linting, type checking, security scanning, dependency scanning, and package smoke validation.
2. Add local release-control verification commands that can run without network access.
3. Add packaging/release documentation and rollback documentation.
4. Update dependency metadata for future CI execution without claiming unavailable tools were run locally.
5. Preserve Phase 8 memory/skill behavior as rollback-safe fallback.
6. Record all environment-limited Codex/local/CI tasks in `PRODUCTION_GAP_TRACKER.md`.

## Deliverables

Created:

- `.github/workflows/ci.yml`
- `.github/dependabot.yml`
- `RELEASE.md`
- `ROLLBACK.md`
- `SECURITY_VALIDATION.md`
- `scripts/phase9_verify.py`
- `src/bountyclaw/release/__init__.py`
- `src/bountyclaw/release/models.py`
- `src/bountyclaw/release/service.py`
- `tests/test_release_phase9.py`

Updated:

- `ARCHITECTURE.md`
- `AGENTS.md`
- `ROADMAP.md`
- `PRODUCTION_GAP_TRACKER.md`
- `README.md`
- `pyproject.toml`
- `src/bountyclaw/__init__.py`
- `src/bountyclaw/cli.py`
- `src/bountyclaw/config.py`

## Subsystem Boundaries

### In Scope

- Local release-control models.
- Local release checklist generation.
- Local release-control definition verification.
- Deterministic rollback plan generation.
- GitHub Actions workflow definition.
- Dependabot configuration definition.
- Packaging metadata and dev-gate declarations.
- Documentation for release, rollback, and security-validation gates.
- Tests for release-control artifacts and CLI commands.

### Out of Scope

- Executing hosted GitHub Actions.
- Creating a GitHub repository.
- Enabling branch protection.
- Publishing packages.
- Signing artifacts.
- Generating provenance attestations.
- Running clean virtualenv package installs with internet-fetched dependencies.
- Running ruff, mypy, bandit, or pip-audit when unavailable in the ChatGPT container.
- Cloud deployment.
- Live model provider calls.
- Real MCP/browser runtimes.
- Active validation.
- Report submission.

## Dependencies

Required completed dependencies:

- Phase 0 governance files.
- Phase 1 CLI/scope gate.
- Phase 2 repository intake.
- Phase 3 scanner framework.
- Phase 4 findings/evidence persistence.
- Phase 5 model-router/prompt-safety foundations.
- Phase 6 report drafting.
- Phase 7 MCP/browser fixture foundations.
- Phase 8 memory/skill foundations.
- Existing pytest suite.
- Existing `pyproject.toml` package metadata.

## Implementation Sequence

1. Reconcile Phase 8 repository bundle and mandatory governance files.
2. Create `PHASE_9_SUBROADMAP.md` before implementation.
3. Add release-control models and service functions.
4. Add CLI commands under `bountyclaw release`.
5. Add GitHub Actions and Dependabot definitions.
6. Add release, rollback, and security-validation documentation.
7. Update `pyproject.toml` with Phase 9 version and future dev-gate dependencies.
8. Add tests for release-control definitions, CLI JSON output, rollback plan, and deferred external gates.
9. Validate with pytest, compileall, CLI smoke checks, and ZIP extraction test.
10. Update roadmap, architecture, agents, README, and production gap tracker.

## Validation Sequence

Local validation required and completed:

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -m compileall -q src tests`
- `PYTHONPATH=src python -m bountyclaw --help`
- `PYTHONPATH=src python -m bountyclaw doctor`
- `PYTHONPATH=src python -m bountyclaw release checklist --root . --json`
- `PYTHONPATH=src python -m bountyclaw release verify --root . --json`
- `PYTHONPATH=src python -m bountyclaw release rollback-plan --json`
- `PYTHONPATH=src python scripts/phase9_verify.py --root . --json`
- Extract generated repository ZIP and rerun pytest/compileall.

Environment-limited validation recorded as gaps:

- Hosted GitHub Actions execution.
- Clean install from wheel/sdist in fresh environment.
- Ruff/mypy/bandit/pip-audit execution where tools are unavailable.
- Package signing/provenance.
- Package publishing dry run.
- Branch protection/repository ruleset enforcement.

## Rollback Strategy

Rollback target: Phase 8 memory/skills baseline.

Rollback steps:

1. Remove `PHASE_9_SUBROADMAP.md`.
2. Remove `.github/workflows/ci.yml` and `.github/dependabot.yml`.
3. Remove `RELEASE.md`, `ROLLBACK.md`, and `SECURITY_VALIDATION.md`.
4. Remove `scripts/phase9_verify.py`.
5. Remove `src/bountyclaw/release/`.
6. Remove `tests/test_release_phase9.py`.
7. Revert release CLI additions in `src/bountyclaw/cli.py`.
8. Revert Phase 9 updates in `pyproject.toml`, `src/bountyclaw/__init__.py`, and `src/bountyclaw/config.py`.
9. Revert Phase 9 governance and gap-tracker updates.

No external resources need cleanup because Phase 9 creates no cloud infrastructure, registry artifacts, hosted CI state, live provider calls, MCP/browser runtimes, or bounty submissions.

## Drift-Prevention Constraints

- Do not claim CI execution unless a real CI runner executed it.
- Do not claim package install validation unless a clean environment performed it.
- Do not claim security scans ran unless tools actually executed.
- Do not enable live model providers.
- Do not enable live MCP/browser runtimes.
- Do not add active validation or report submission.
- Preserve local-first CLI behavior.
- Preserve Phase 8 memory/skill controls.
- Keep release commands informational and non-networked.

## Environment Limitations

ChatGPT Project Mode cannot provide:

- hosted repository CI execution
- branch protection
- clean package install from indexes
- package publishing credentials
- signing/provenance infrastructure
- external scanner/runtime validation
- real deployment target
- real rollback drills over production state

## Expected Unresolved Gaps

- Hosted CI execution remains unperformed.
- Clean wheel/sdist install validation remains unperformed.
- Static quality/security gates are defined but may require Codex/local/CI tooling to execute.
- Artifact signing/provenance remains unimplemented.
- Package registry publishing/dry run remains unperformed.
- Branch protection and repository governance remain unconfigured.
- Production deployment and external hardening remain Phase 10 work.

## Expected Future Continuation Tasks

- Execute GitHub Actions or equivalent CI in a real repository.
- Install dev dependencies and run ruff, mypy, bandit, and pip-audit.
- Build wheel/sdist and clean-install the wheel in a fresh environment.
- Add lockfile/dependency pinning strategy if chosen.
- Add branch protection/rulesets.
- Evaluate package signing/provenance.
- Execute Phase 10 production-hardening and external-validation tasks.

## Completion Status

Completed in ChatGPT Project Mode.

Phase 9 completion means release controls are defined and locally validated where possible. It does not mean external CI, clean packaging, security-tool execution, artifact publishing, signing, deployment, or production rollback validation has been completed.
