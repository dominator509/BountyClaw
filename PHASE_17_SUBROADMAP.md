# Phase 17 Subroadmap: Closure Gate and Readiness Attestation Governance

## Objectives

- Add a metadata-only closure gate for future external validation evidence.
- Bind future manual readiness attestations to the Phase 16 validation baseline ID.
- Join Phase 12 validation-evidence metadata, Phase 13 evidence-review metadata, Phase 14 gap tracker governance, and Phase 15 execution-journal metadata without trusting or inspecting raw evidence.
- Generate future human AppSec/release attestation templates.
- Preserve the invariant that no ChatGPT Project Mode output closes production gaps or raises production readiness.

## Deliverables

- `MARKDOWN_REVIEW_PHASE17.md` documenting full Markdown review.
- `src/bountyclaw/closure_gate/` subsystem.
- `scripts/phase17_verify.py`.
- `tests/test_closure_gate_phase17.py`.
- CLI commands:
  - `bountyclaw closure-gate attestation-template`
  - `bountyclaw closure-gate status`
  - `bountyclaw closure-gate export`
  - `bountyclaw closure-gate verify`
- Handoff export update with `CLOSURE_GATE_COMMANDS.md`.
- CI workflow definition hook for Phase 17 verification.
- Governance, release, rollback, security-validation, roadmap, and gap tracker updates.

## Subsystem Boundaries

### In Scope

- Metadata-only readiness attestation templates.
- Metadata-only attestation status assessment.
- Baseline-ID matching against Phase 16 source snapshot metadata.
- SHA-256 field validation for referenced evidence review, execution journal, and gap tracker artifacts.
- Candidate manual gap-update reporting.
- Local verifier and export package.

### Out of Scope

- Raw validation evidence inspection.
- Raw source export.
- External validation execution.
- Hosted CI execution.
- Clean package install validation.
- External scanner execution.
- Live model provider calls.
- Real MCP/browser runtime launch.
- Active validation or exploit execution.
- Automated bounty submission.
- Automatic gap closure.
- Production readiness increase.

## Dependencies

- Phase 16 validation-baseline subsystem.
- Phase 15 validation-runbook subsystem.
- Phase 14 gap-tracker subsystem.
- Phase 13 evidence-review subsystem.
- Phase 12 validation-evidence subsystem.
- Phase 11 handoff subsystem.
- Existing release and hardening verifiers.

## Implementation Sequence

1. Unzip the Phase 16 repository bundle.
2. Fully review every Markdown file and record the review ledger.
3. Add closure-gate models.
4. Add closure-gate service functions.
5. Add closure-gate CLI commands and renderers.
6. Add Phase 17 verification script.
7. Add tests for metadata-only behavior, attestation validation, handoff command inclusion, and non-closure invariants.
8. Update handoff package export.
9. Update CI workflow definitions.
10. Update governance and gap tracker files.
11. Validate locally.

## Validation Sequence

- Run targeted Phase 17 tests.
- Run full pytest suite where feasible.
- Run compileall for `src`, `tests`, and `scripts`.
- Run CLI smoke checks for all Phase 17 commands.
- Run regression verifiers for Phases 9 through 17.
- Validate gap tracker structure and duplicate IDs.
- Validate ZIP extraction and Phase 17 verifier from the delivered artifact.

## Rollback Strategy

To roll back Phase 17:

- Remove `PHASE_17_SUBROADMAP.md`.
- Remove `MARKDOWN_REVIEW_PHASE17.md`.
- Remove `src/bountyclaw/closure_gate/`.
- Remove `scripts/phase17_verify.py`.
- Remove `tests/test_closure_gate_phase17.py`.
- Revert `bountyclaw closure-gate` CLI additions.
- Revert the Phase 17 CI workflow hook.
- Revert Phase 11 handoff additions for `CLOSURE_GATE_COMMANDS.md`.
- Revert version/phase metadata from `0.17.0` / Phase 17 to the Phase 16 baseline.
- Revert Phase 17 governance, README, release, rollback, security-validation, and gap-tracker updates.

Phase 16 validation-baseline tooling remains the rollback-safe baseline.

## Drift-Prevention Constraints

- Do not parse, print, classify, or trust raw evidence contents.
- Do not close any `PGT-*` entry automatically.
- Do not raise production readiness from metadata-only outputs.
- Do not treat candidate gap IDs as accepted closures.
- Do not execute external validators.
- Do not launch live providers, real MCP servers, real browsers, external scanners, active validation, or report submission.
- Do not allow scope expansion from attestation metadata.

## Environment Limitations

ChatGPT Project Mode cannot execute hosted CI, clean install validation, real scanner/sandbox/egress validation, live provider safety validation, real MCP/browser runtime validation, human evidence review, branch protection, signing/provenance, package publishing, operational drills, or real bounty-program report quality review.

## Expected Unresolved Gaps

- Real readiness attestations still require external validation evidence and human AppSec/release review.
- Closure-gate outputs still require hosted CI enforcement.
- Production readiness cannot increase until evidence-backed manual gap closure occurs.

## Expected Future Continuation Tasks

- Execute external validation runbook steps in Codex/local/CI/human environments.
- Produce baseline-bound evidence artifacts.
- Populate execution journals and evidence review decisions.
- Create metadata-only readiness attestations after human review.
- Run the Phase 17 closure gate.
- Manually update `PRODUCTION_GAP_TRACKER.md` only with reviewed evidence and rollback notes.

## Status

Completed inside ChatGPT Project Mode. External validation, evidence review, readiness attestation, manual gap closure, and production readiness recalculation remain deferred.
