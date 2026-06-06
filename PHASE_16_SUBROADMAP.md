# Phase 16 Subroadmap: Validation Baseline Manifest and Source Snapshot Binding

## Objectives

- Create a deterministic, hash-only source baseline manifest for future external validation evidence.
- Bind future Codex/local/CI/human evidence to an exact repository snapshot without storing raw source or evidence contents.
- Add local CLI commands for manifest generation, export, and verification.
- Update handoff and gap governance so future executors reference the Phase 16 baseline ID before claiming validation results.

## Deliverables

- `src/bountyclaw/validation_baseline/` subsystem.
- `scripts/phase16_verify.py`.
- `tests/test_validation_baseline_phase16.py`.
- CLI commands under `bountyclaw validation-baseline`.
- Handoff package update with `VALIDATION_BASELINE_COMMANDS.md`.
- CI workflow hook for Phase 16 verification.
- `MARKDOWN_REVIEW_PHASE16.md` documenting the mandatory Markdown review.
- Updated roadmap, architecture, release, rollback, security-validation, and gap tracker files.

## Subsystem Boundaries

### In Scope

- Hash-only source file inventory.
- Baseline ID generation from sorted path/hash metadata.
- Exclusion of caches, build artifacts, archives, private validation evidence, and local runtime outputs.
- Baseline package export for future external validation reference.
- Local readiness verification.
- Gap tracker and handoff updates for future Codex/local/CI/human evidence binding.

### Out of Scope

- Hosted CI execution.
- Clean package installation.
- External scanner execution.
- OS/container sandbox or egress validation.
- Live model-provider validation.
- Real MCP/browser runtime validation.
- Raw validation evidence inspection.
- Production gap closure.
- Production readiness increase based on unreviewed evidence.
- Package publishing, signing, provenance, branch protection, deployment, or bounty submission.

## Dependencies

- Completed Phase 15 validation runbook and metadata-only journal tooling.
- Completed Phase 14 gap tracker backlog tooling.
- Completed Phase 13 evidence-review proposal tooling.
- Completed Phase 12 validation-evidence ledger tooling.
- Completed Phase 11 handoff package tooling.

## Implementation Sequence

1. Unzip the latest source bundle and review every Markdown file.
2. Create `PHASE_16_SUBROADMAP.md`.
3. Add validation-baseline models and services.
4. Add CLI commands and script entrypoint.
5. Update handoff export and CI verification definitions.
6. Add tests for hash-only behavior, exclusions, export, CLI output, and readiness invariants.
7. Update governance, handoff, release, rollback, security, and gap files.
8. Validate locally without claiming external execution.

## Validation Sequence

- Run Phase 16 tests.
- Run compile validation for `src`, `tests`, and `scripts`.
- Run CLI smoke checks for validation-baseline commands.
- Run regression verifiers for Phases 9 through 16.
- Validate gap tracker structure and duplicate IDs.
- Validate ZIP extraction and clean artifact packaging.

## Rollback Strategy

- Remove `src/bountyclaw/validation_baseline/`.
- Remove `scripts/phase16_verify.py`.
- Remove `tests/test_validation_baseline_phase16.py`.
- Revert `bountyclaw validation-baseline` CLI additions.
- Revert Phase 16 CI workflow hook.
- Revert Phase 11 handoff additions for validation-baseline commands.
- Revert version/phase metadata from `0.16.0` / Phase 16 to the Phase 15 baseline.
- Revert Phase 16 governance, README, release, rollback, security-validation, and gap-tracker updates.

## Drift-Prevention Constraints

- Do not execute external validation.
- Do not inspect raw evidence contents.
- Do not store raw source contents in baseline artifacts.
- Do not close production gaps.
- Do not increase production readiness based on unreviewed evidence.
- Do not enable live providers, real MCP/browser runtimes, active validation, target contact, publishing, signing, branch protection, or bounty submission.

## Environment Limitations

ChatGPT Project Mode cannot provide hosted CI proof, clean install proof, real scanner validation, sandbox/egress validation, live-provider safety validation, MCP/browser runtime validation, private evidence storage, human AppSec/release approval, package publishing, signing/provenance, branch protection, or production deployment.

## Expected Unresolved Gaps

- Real external validation still must be executed outside ChatGPT Project Mode.
- Future evidence must be linked to the Phase 16 baseline ID by Codex/local/CI/human executors.
- Human review is still required before any gap closure or readiness recalculation.
- Hosted enforcement of the baseline verifier is still required.

## Expected Future Continuation Tasks

- Export the validation-baseline package before external validation begins.
- Add the baseline ID to execution journal entries and evidence review decisions.
- Re-run the baseline verifier in hosted CI and branch protection.
- Update `PRODUCTION_GAP_TRACKER.md` only after real reviewed evidence exists.

## Status

Completed inside ChatGPT Project Mode.
