# PHASE_19_SUBROADMAP.md

# Phase 19: Local Quality/Security Gate Execution and Remediation

## Objectives

Execute and remediate locally codeable quality, typing, security, packaging, and install gates inside ChatGPT Project Mode without claiming hosted CI, online dependency-audit completion, production validation, or gap closure.

## Deliverables

- Full Markdown review ledger for the Phase 18 source bundle.
- Local quality/security gate execution record.
- Ruff formatting and semantic lint remediation.
- Mypy typing remediation.
- Bandit security remediation or narrow documented nosec annotations.
- Package build and clean wheel install validation.
- Quality gate CLI subsystem.
- Phase 19 verification script.
- Phase 19 tests.
- Handoff package command updates.
- Governance and gap tracker updates.

## Subsystem Boundaries

In scope:

- Local source formatting and linting.
- Local Python type checking.
- Local static source security scanning.
- Local package build and clean install smoke checks.
- Metadata-only quality gate export and verification.
- Documentation and gap tracker updates.

Out of scope:

- Hosted CI execution.
- Branch protection configuration.
- Online dependency audit completion if DNS/network is unavailable.
- External scanner execution.
- Sandbox/egress validation.
- Live provider validation.
- Real MCP/browser runtime validation.
- Evidence acceptance.
- Production gap closure.
- Readiness attestation.
- Package publishing.
- Bounty submission.

## Dependencies

- Phase 18 readiness dashboard and external executor index completed locally.
- Phase 17 closure gate completed locally.
- Phase 16 validation baseline completed locally.
- Phase 14 gap tracker governance completed locally.
- Existing `pyproject.toml` dev dependency declarations.

## Implementation Sequence

1. Unzip the latest Phase 18 repository bundle.
2. Fully review every Markdown file in the archive.
3. Run baseline tests and compile checks.
4. Install local gate tooling where available in this environment.
5. Execute `ruff format`, `ruff check`, `mypy`, `bandit`, `python -m build`, clean wheel install, and `pip-audit` attempt.
6. Remediate source issues discovered by local gates.
7. Create `quality_gates` subsystem.
8. Add `bountyclaw quality-gates` CLI commands.
9. Add `scripts/phase19_verify.py` and tests.
10. Update handoff commands, CI workflow, governance, release, rollback, security validation, and gap tracker files.
11. Validate tests, compile, local gates, CLI smoke, and ZIP extraction.

## Validation Sequence

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -m compileall -q src tests scripts`
- `ruff format --check src tests scripts`
- `ruff check src tests scripts`
- `PYTHONPATH=src mypy --no-incremental --cache-dir <tmp> src`
- `PYTHONPATH=src bandit -q -r src`
- `python -m build`
- clean wheel install and installed CLI smoke
- `pip-audit --progress-spinner off` attempt
- `PYTHONPATH=src python -m bountyclaw quality-gates checklist --root . --json`
- `PYTHONPATH=src python -m bountyclaw quality-gates verify --root . --json`
- `PYTHONPATH=src python scripts/phase19_verify.py --root . --json`
- Regression verifiers for Phases 9 through 18.
- ZIP extraction validation.

## Rollback Strategy

To revert Phase 19:

- Remove `PHASE_19_SUBROADMAP.md`.
- Remove `MARKDOWN_REVIEW_PHASE19.md`.
- Remove `QUALITY_GATES_PHASE19.md`.
- Remove `src/bountyclaw/quality_gates/`.
- Remove `scripts/phase19_verify.py`.
- Remove `tests/test_quality_gates_phase19.py`.
- Revert `bountyclaw quality-gates` CLI additions.
- Revert Phase 19 CI workflow hook.
- Revert Phase 19 formatting/lint/type/security remediation if necessary.
- Revert version/phase metadata from `0.19.0` / Phase 19 to `0.18.0` / Phase 18.
- Revert Phase 19 governance, README, release, rollback, security-validation, and gap-tracker updates.

Phase 18 readiness-dashboard tooling remains the rollback-safe baseline.

## Drift-Prevention Constraints

- Do not enable network target contact.
- Do not execute external scanners.
- Do not enable live model providers.
- Do not enable real MCP/browser runtimes.
- Do not inspect raw external validation evidence.
- Do not close production gaps.
- Do not raise readiness based on unreviewed evidence.
- Do not claim hosted CI or online dependency audit completion unless actually executed.

## Environment Limitations

ChatGPT Project Mode can run local tests, compile, ruff, mypy, Bandit, build, and clean install checks after local tooling installation. It cannot prove hosted CI enforcement, branch protection, or repository-host rules. Online dependency audit may be blocked by DNS/network restrictions.

## Expected Unresolved Gaps

- `pip-audit` completion remains deferred if DNS/network remains unavailable.
- Hosted CI enforcement remains deferred.
- Evidence review and production gap closure remain deferred.

## Expected Future Continuation Tasks

- Re-run Phase 19 gates in hosted CI.
- Complete `pip-audit` with approved internet access or internal advisory mirror.
- Attach Phase 19 artifacts through Phase 12/13/17 evidence and closure workflows.
- Enforce Phase 19 gates through repository branch protection.

## Status

Completed inside ChatGPT Project Mode. Hosted CI, online dependency audit completion, branch protection, evidence review, and production gap closure remain deferred.
