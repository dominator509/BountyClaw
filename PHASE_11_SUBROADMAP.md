# Phase 11 Subroadmap: External Validation Handoff Package

## Objectives

Phase 11 converts the Phase 10 external-validation plan into a deterministic handoff package for Codex, local, CI, and human production-validation environments.

The objective is not to execute external validation inside ChatGPT Project Mode. The objective is to make the remaining environment-limited work unambiguous, auditable, evidence-driven, and safe for future executors.

## Deliverables

Completed deliverables:

- `src/bountyclaw/handoff/` subsystem.
- `CodexHandoffPlan` model.
- `EvidenceTemplate` model.
- `HandoffExportResult` model.
- `HandoffVerificationResult` model.
- `bountyclaw handoff plan` CLI command.
- `bountyclaw handoff evidence-template` CLI command.
- `bountyclaw handoff export` CLI command.
- `bountyclaw handoff verify` CLI command.
- `scripts/phase11_verify.py` deterministic verifier.
- CI workflow definition hook for Phase 11 verification.
- Tests for handoff plan coverage, evidence templates, local export, verification, and CLI JSON output.
- Governance/documentation updates.
- Production gap tracker updates with Phase 11-specific Codex/local/CI/human handoff gaps.

## Subsystem Boundaries

In scope:

- Local-only deterministic handoff planning.
- Local-only evidence artifact templates.
- Local-only handoff package export.
- Local-only handoff-readiness verification.
- Codex/local/CI/human future execution instructions.
- Explicit deferred validation tracking.

Out of scope:

- Hosted CI execution.
- Clean package install execution.
- External scanner binary execution.
- OS/container sandbox validation.
- Network-egress validation.
- Live model provider validation.
- Real MCP server execution.
- Real browser runtime execution.
- Active validation.
- Package publishing.
- Signing/provenance generation.
- Branch protection configuration.
- Automated bounty submission.

## Dependencies

Phase 11 depends on:

- Phase 9 release-control verifier.
- Phase 10 hardening verifier.
- `PRODUCTION_GAP_TRACKER.md` as the production-completion ledger.
- Existing CLI framework.
- Existing non-networked local validation environment.

## Implementation Sequence

Completed sequence:

1. Reread governance files and latest Phase 10 bundle.
2. Create `PHASE_11_SUBROADMAP.md` before implementation.
3. Add handoff models.
4. Add handoff service functions.
5. Add handoff CLI commands.
6. Add `scripts/phase11_verify.py`.
7. Add CI workflow hook definition.
8. Update version and phase metadata to `0.11.0` / Phase 11.
9. Add Phase 11 tests.
10. Validate locally.
11. Update architecture, roadmap, agents, README, release/security/rollback docs, and gap tracker.
12. Build Phase 11 repository bundle.

## Validation Sequence

Completed local validation:

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -m compileall -q src tests scripts`
- `PYTHONPATH=src python -m bountyclaw --help`
- `PYTHONPATH=src python -m bountyclaw doctor`
- `PYTHONPATH=src python -m bountyclaw handoff plan --root . --json`
- `PYTHONPATH=src python -m bountyclaw handoff evidence-template --root . --json`
- `PYTHONPATH=src python -m bountyclaw handoff export --root . --output <tmpdir> --json`
- `PYTHONPATH=src python -m bountyclaw handoff verify --root . --json`
- `PYTHONPATH=src python scripts/phase11_verify.py --root . --json`
- ZIP extraction validation with pytest, compileall, and handoff verification.

Environment-limited validation remains deferred:

- Hosted CI execution.
- Clean package build/install validation.
- Ruff/mypy/bandit/pip-audit execution where tools are unavailable.
- External scanner binary and sandbox validation.
- Live provider validation.
- Real MCP/browser runtime validation.
- Human report quality review.
- Performance, retention, backup/restore, and rollback drills.
- Branch protection, signing/provenance, and publishing dry run.

## Rollback Strategy

Rollback target: Phase 10 local production-hardening baseline.

Rollback steps:

1. Remove `PHASE_11_SUBROADMAP.md`.
2. Remove `src/bountyclaw/handoff/`.
3. Remove `scripts/phase11_verify.py`.
4. Remove `tests/test_handoff_phase11.py`.
5. Revert `bountyclaw handoff` CLI additions.
6. Revert `.github/workflows/ci.yml` Phase 11 verification step.
7. Revert version/phase metadata to Phase 10.
8. Revert Phase 11 documentation and gap-tracker updates.

No external resources need cleanup because Phase 11 creates no cloud infrastructure, registry artifacts, hosted CI state, credentials, live provider calls, MCP/browser runtimes, active validation state, or bounty submissions.

## Drift-Prevention Constraints

- Do not convert handoff instructions into automatic external actions.
- Do not claim hosted CI, clean install, scanners, live providers, real MCP/browser runtimes, signing, publishing, or branch protection were executed unless future evidence exists.
- Do not enable network target contact.
- Do not enable active validation.
- Do not add automated report submission.
- Preserve Phase 10 hardening controls as rollback fallback.
- Treat all generated handoff artifacts as plans, not validation evidence.

## Environment Limitations

ChatGPT Project Mode cannot provide:

- hosted repository CI execution
- real repository branch protection
- clean package index install proof
- package publishing credentials
- signing/provenance infrastructure
- scanner binary sandboxes and egress logs
- live LLM provider credentials and telemetry
- real MCP servers
- real browser runtime validation
- bounty platform accounts
- human legal/security/report review
- production rollback drills over real state

## Expected Unresolved Gaps

- External validation execution remains unperformed.
- Evidence artifacts are templates until future environments produce them.
- Hosted CI and clean install remain unproven.
- Real scanner, sandbox, live provider, MCP/browser, report-quality, performance, rollback, signing, and publishing validation remain unproven.
- Human final authorization and manual submission remain mandatory.

## Expected Future Continuation Tasks

- Run `bountyclaw handoff verify --root . --json` after checkout in Codex/local/CI.
- Run `bountyclaw handoff export --root . --output validation_handoff --json` and attach generated files to the release evidence package.
- Execute each `P11-HANDOFF-*` task in the required environment.
- Produce each named evidence artifact.
- Store reviewed/redacted future artifacts under `validation_evidence/` using the names from the Phase 11 evidence template.
- Run `bountyclaw validation-evidence ledger --root . --evidence-dir validation_evidence --json`.
- Run `bountyclaw validation-evidence gap-readiness --root . --evidence-dir validation_evidence --json`.
- Run `bountyclaw validation-evidence export-ledger --root . --evidence-dir validation_evidence --output validation_evidence_ledger --json`.
- Update `PRODUCTION_GAP_TRACKER.md`, `SECURITY_VALIDATION.md`, `RELEASE.md`, and `ROLLBACK.md` with exact human-reviewed evidence results.
- Recalculate production readiness only after real evidence exists and has been reviewed.

## Completion Status

Completed in ChatGPT Project Mode.

Phase 11 completion means deterministic external-validation handoff tooling, evidence templates, export package generation, local handoff verification, CI hook definition, tests, and governance updates exist. Phase 12 adds the next local evidence-ledger layer for hash-only artifact inventory and gap-readiness mapping. It does not mean any external validation, hosted CI execution, package install, scanner runtime, live provider, real MCP/browser, human review, signing/provenance, publishing, deployment, or production readiness validation has completed.
