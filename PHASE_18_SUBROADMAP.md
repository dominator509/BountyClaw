# Phase 18 Subroadmap: Readiness Dashboard and External Executor Index

## Objectives

- Create a consolidated metadata-only readiness dashboard over Phase 9 through Phase 17 governance verifiers.
- Create an ordered external executor command index for Codex/local/CI/human validation workflows.
- Update the Phase 11 handoff export so future executors receive Phase 18 dashboard commands.
- Preserve the no-auto-closure invariant: no evidence acceptance, no production gap closure, no readiness increase, and no production-ready claim.
- Keep all work local-only and executable inside ChatGPT Project Mode.

## Deliverables

- `src/bountyclaw/readiness_dashboard/` models and service layer.
- `bountyclaw readiness-dashboard build` command.
- `bountyclaw readiness-dashboard handoff-index` command.
- `bountyclaw readiness-dashboard export` command.
- `bountyclaw readiness-dashboard verify` command.
- `scripts/phase18_verify.py`.
- `tests/test_readiness_dashboard_phase18.py`.
- `MARKDOWN_REVIEW_PHASE18.md`.
- Phase 11 handoff export update with `READINESS_DASHBOARD_COMMANDS.md`.
- Governance, handoff, release, rollback, security-validation, and gap-tracker updates.

## Subsystem Boundaries

### In Scope

- Metadata-only aggregation of local verifier results.
- Ordered external executor command sequencing.
- Dashboard export package generation.
- Handoff command update.
- Local verification and tests.

### Out of Scope

- Hosted CI execution.
- Clean package install validation.
- Static/security tool execution with installed dependencies.
- External scanner execution.
- OS/container sandbox validation.
- Live provider validation.
- Real MCP/browser runtime validation.
- Raw evidence inspection.
- Evidence acceptance.
- Production gap closure.
- Production readiness increase based on dashboard metadata.
- Package publishing, signing/provenance, branch protection changes, or bounty submission.

## Dependencies

- Phase 17 closure-gate/readiness-attestation governance completed locally.
- Phase 16 validation-baseline source snapshot binding completed locally.
- Phase 15 validation-runbook metadata completed locally.
- Phase 14 gap tracker governance completed locally.
- Phase 13 evidence-review workflow completed locally.
- Phase 12 validation-evidence ledger completed locally.
- Phase 11 handoff package completed locally.
- Phase 10 hardening and Phase 9 release controls completed locally.

## Implementation Sequence

1. Unzip latest repository bundle and review all Markdown files.
2. Create the Phase 18 subroadmap and Markdown review ledger.
3. Add `readiness_dashboard` models.
4. Add dashboard/index/export/verify service functions.
5. Add CLI commands and renderers.
6. Add Phase 18 verification script.
7. Update Phase 11 handoff export with Phase 18 commands.
8. Add tests.
9. Update governance and gap tracker.
10. Validate with tests, compile checks, CLI smoke checks, and ZIP extraction checks.

## Validation Sequence

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -m compileall -q src tests scripts`
- `PYTHONPATH=src python -m bountyclaw readiness-dashboard build --root . --json`
- `PYTHONPATH=src python -m bountyclaw readiness-dashboard handoff-index --root . --json`
- `PYTHONPATH=src python -m bountyclaw readiness-dashboard export --root . --output <tmp> --json`
- `PYTHONPATH=src python -m bountyclaw readiness-dashboard verify --root . --json`
- `PYTHONPATH=src python scripts/phase18_verify.py --root . --json`
- Regression verifier checks for Phases 9 through 17.
- Gap tracker audit/backlog verification.
- ZIP extraction validation.

## Rollback Strategy

To revert Phase 18:

- Remove `PHASE_18_SUBROADMAP.md`.
- Remove `MARKDOWN_REVIEW_PHASE18.md`.
- Remove `src/bountyclaw/readiness_dashboard/`.
- Remove `scripts/phase18_verify.py`.
- Remove `tests/test_readiness_dashboard_phase18.py`.
- Revert `bountyclaw readiness-dashboard` CLI additions.
- Revert Phase 18 CI workflow hook.
- Revert Phase 11 handoff additions for `READINESS_DASHBOARD_COMMANDS.md`.
- Revert version/phase metadata from `0.18.0` / Phase 18 to `0.17.0` / Phase 17.
- Revert Phase 18 governance, README, release, rollback, security-validation, and gap-tracker updates.

Phase 17 closure-gate tooling remains the rollback-safe baseline.

## Drift-Prevention Constraints

- Do not execute external validation.
- Do not inspect raw evidence contents.
- Do not close or mark any production gap complete.
- Do not raise production readiness based on unreviewed dashboard metadata.
- Do not enable network, live LLM, real MCP, real browser, active validation, exploit execution, package publishing, or report submission.
- Preserve all Phase 17 closure-gate invariants.

## Environment Limitations

ChatGPT Project Mode cannot perform hosted CI, clean package install validation, repository branch protection, real scanner runtime validation, OS/container sandbox validation, live-provider validation, real MCP/browser runtime validation, human evidence review, signing/provenance, package publishing, or production deployment.

## Expected Unresolved Gaps

- Real external validation remains unexecuted.
- Dashboard commands remain a handoff/index layer only.
- Hosted enforcement remains deferred.
- Human evidence review and manual gap closure remain deferred.

## Expected Future Continuation Tasks

- Execute dashboard handoff commands in Codex/local/CI/human environments.
- Enforce dashboard verification in hosted CI and branch protection.
- Use dashboard output as an operator index for Phase 11 through Phase 17 validation workflows.
- Update `PRODUCTION_GAP_TRACKER.md` only with real reviewed evidence and rollback notes.

## Status

Completed inside ChatGPT Project Mode. External execution remains deferred.
