# BountyClaw Phase 18 Rollback Plan

## Rollback Target

Rollback target: Phase 16 validation-baseline source snapshot binding baseline.

Phase 17 adds metadata-only closure-gate/readiness-attestation governance, local verification script, CLI commands, CI hook definition, handoff-command updates, and governance/gap tracker updates only. It introduces no cloud infrastructure, external credentials, hosted services, live providers, MCP servers, browser runtimes, production databases, package registry artifacts, private evidence-storage service, branch protection, signing/provenance, production gap closure, readiness recalculation, or bounty-platform submissions.

## Rollback Steps

To revert Phase 17 only:

1. Remove `PHASE_17_SUBROADMAP.md`.
2. Remove `MARKDOWN_REVIEW_PHASE17.md`.
3. Remove `src/bountyclaw/closure_gate/`.
4. Remove `scripts/phase17_verify.py`.
5. Remove `tests/test_closure_gate_phase17.py`.
6. Revert `bountyclaw closure-gate` CLI additions.
7. Revert the Phase 17 CI workflow hook.
8. Revert Phase 11 handoff additions for `CLOSURE_GATE_COMMANDS.md`.
9. Revert version/phase metadata from `0.17.0` / Phase 17 to `0.16.0` / Phase 16 in `pyproject.toml`, `src/bountyclaw/__init__.py`, `src/bountyclaw/config.py`, and scope documentation.
10. Revert Phase 17 governance updates in `ARCHITECTURE.md`, `AGENTS.md`, `ROADMAP.md`, `PRODUCTION_GAP_TRACKER.md`, `README.md`, `RELEASE.md`, and `SECURITY_VALIDATION.md`.

## Post-Rollback Validation

After rollback, run:

```bash
PYTHONPATH=src python -m compileall -q src tests scripts
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python scripts/phase16_verify.py --root . --json
```

## Rollback Safety Notes

Phase 16 validation-baseline tooling remains the rollback-safe baseline.

Rollback does not require secret rotation, registry deletion, cloud cleanup, DNS changes, data migrations, database restoration, hosted CI cleanup, evidence-store service cleanup, MCP/browser runtime teardown, live-provider credential revocation, production readiness correction from automated state, or bounty-platform account changes because none of those resources are created in Phase 17.


## Phase 18 Rollback Steps

To revert Phase 18 only:

1. Remove `PHASE_18_SUBROADMAP.md` and `MARKDOWN_REVIEW_PHASE18.md`.
2. Remove `src/bountyclaw/readiness_dashboard/`, `scripts/phase18_verify.py`, and `tests/test_readiness_dashboard_phase18.py`.
3. Revert `bountyclaw readiness-dashboard` CLI additions and the Phase 18 CI workflow hook.
4. Revert Phase 11 handoff additions for `READINESS_DASHBOARD_COMMANDS.md`.
5. Revert version/phase metadata from `0.18.0` / Phase 18 to `0.17.0` / Phase 17.
6. Revert Phase 18 governance, release, security-validation, README, and gap tracker updates.

Phase 17 closure-gate governance remains the rollback-safe baseline. No external accounts, hosted CI state, package artifacts, private evidence stores, live provider calls, MCP/browser runtimes, branch protection settings, signing/provenance, production gap closure, or bounty submissions were introduced by Phase 18.


## Phase 19 Rollback

To roll back Phase 19, remove `src/bountyclaw/quality_gates/`, `scripts/phase19_verify.py`, `tests/test_quality_gates_phase19.py`, `PHASE_19_SUBROADMAP.md`, `MARKDOWN_REVIEW_PHASE19.md`, and `QUALITY_GATES_PHASE19.md`; revert the `bountyclaw quality-gates` CLI additions, Phase 19 CI hook, Phase 19 handoff command addition, version metadata, source formatting/type/security remediation changes, and governance/gap tracker updates.

Phase 18 readiness-dashboard tooling remains the rollback-safe baseline. No external accounts, hosted CI state, package registry artifacts, branch protection, signed artifacts, live targets, providers, MCP/browser runtimes, evidence acceptance, gap closure, or bounty submissions were introduced.
