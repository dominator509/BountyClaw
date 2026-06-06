# Phase 14 Subroadmap: Gap Tracker Governance and Codex Backlog Export

## Objectives

- Reconcile the Phase 13 source bundle and all Markdown governance files before coding.
- Add local-only parsing and auditing for `PRODUCTION_GAP_TRACKER.md`.
- Export a deterministic Codex/local/CI/human backlog from unresolved production gaps.
- Update Phase 11 handoff outputs with Phase 14 gap-tracker commands.
- Preserve the invariant that gap auditing, backlog export, and verification never close gaps, raise readiness, inspect raw evidence, or claim external validation.

## Deliverables

- `MARKDOWN_REVIEW_PHASE14.md` documenting the full Markdown review.
- `src/bountyclaw/gap_tracker/` models and service functions.
- CLI commands: `bountyclaw gap-tracker audit`, `backlog`, `export`, and `verify`.
- `scripts/phase14_verify.py`.
- Tests for gap parsing, required-field validation, backlog export, no-auto-closure invariants, and CLI JSON behavior.
- Handoff package update with `GAP_TRACKER_COMMANDS.md`.
- Governance updates to architecture, roadmap, agents, release, rollback, security validation, README, and production gap tracker.

## Subsystem Boundaries

### In Scope

- Local parsing of Markdown governance metadata.
- Required-field and duplicate-ID checks for unresolved `PGT-*` entries.
- Deterministic backlog sorting and export.
- Local verification of Phase 14 artifacts and regression readiness.
- Metadata-only handoff package augmentation.

### Out of Scope

- Closing production gaps.
- Editing gap entries based on evidence.
- Raising production readiness based on backlog generation.
- Inspecting raw validation evidence contents.
- Executing hosted CI, clean package installs, external scanners, live providers, real MCP/browser runtimes, active validation, publishing, branch protection, or report submission.

## Dependencies

- Completed Phase 13 evidence-review workflow.
- `PRODUCTION_GAP_TRACKER.md` entries using the mandatory field format.
- Phase 11 handoff package tooling.
- Phase 12 validation-evidence ledger tooling.
- Phase 13 evidence-review tooling.

## Implementation Sequence

1. Unzip the Phase 13 repository bundle.
2. Fully review every Markdown file in the unzipped bundle.
3. Create the Phase 14 subroadmap before implementation.
4. Implement `gap_tracker` models and parsing service.
5. Implement backlog and export functions.
6. Add CLI commands and Phase 14 verification script.
7. Update handoff export to include Phase 14 commands.
8. Add tests.
9. Update governance and gap tracker files.
10. Validate locally and package a clean ZIP bundle.

## Validation Sequence

- Run full pytest suite.
- Run compileall over source, tests, and scripts.
- Smoke-test Phase 14 CLI commands.
- Run Phase 9/10/11/12/13 regression verifiers.
- Run Phase 14 verifier.
- Validate gap IDs are unique and mandatory fields are present.
- Validate ZIP extraction and rerun tests/verifier from extracted bundle.

## Rollback Strategy

To revert Phase 14:

- Remove `PHASE_14_SUBROADMAP.md`.
- Remove `MARKDOWN_REVIEW_PHASE14.md`.
- Remove `src/bountyclaw/gap_tracker/`.
- Remove `scripts/phase14_verify.py`.
- Remove `tests/test_gap_tracker_phase14.py`.
- Revert `bountyclaw gap-tracker` CLI additions.
- Revert the Phase 14 CI workflow step.
- Revert Phase 11 handoff export additions for `GAP_TRACKER_COMMANDS.md`.
- Revert version/phase metadata from `0.14.0` / Phase 14 to the Phase 13 baseline.
- Revert Phase 14 governance, README, release, rollback, security-validation, and gap-tracker updates.

Phase 13 evidence-review tooling remains the rollback-safe baseline.

## Drift-Prevention Constraints

- Do not parse or print raw validation evidence contents.
- Do not close gaps automatically.
- Do not raise production readiness based on audit or backlog output.
- Do not modify target repositories.
- Do not enable network, live model, real MCP/browser, active validation, or automated submission paths.
- Keep every future task tied to existing `PGT-*` IDs and completion criteria.

## Environment Limitations

ChatGPT Project Mode cannot execute hosted CI, clean package installation, external scanner binaries, sandbox/egress drills, live provider validation, real MCP/browser runtimes, private evidence review, branch protection, signing/provenance, publishing, production deployment, or human report submission approval.

## Expected Unresolved Gaps

- External validation execution remains incomplete.
- Real evidence artifacts remain absent.
- Human evidence review remains incomplete.
- Manual gap closure and readiness recalculation remain incomplete.
- Hosted CI, clean install, static/security gates, scanners, sandboxes, live providers, real MCP/browser runtimes, report quality, performance, rollback, signing, and publishing validation remain unproven.

## Expected Future Continuation Tasks

- Run `bountyclaw gap-tracker audit --root . --json` after every future gap tracker update.
- Run `bountyclaw gap-tracker backlog --root . --json` to refresh Codex/local/CI task sequencing.
- Run `bountyclaw gap-tracker export --root . --output gap_tracker_package --json` for handoff packages.
- Have a human release/AppSec reviewer apply gap closures only after reviewed evidence satisfies each gap completion criterion.

## Completion Status

Completed in ChatGPT Project Mode.

Phase 14 completion means local gap tracker parsing, required-field validation, duplicate-ID validation, Codex backlog export, handoff-command update, verifier script, tests, and governance updates exist. It does not mean external validation, human evidence review, production gap closure, readiness increase, hosted CI execution, clean install validation, external scanner validation, live provider validation, real MCP/browser validation, signing/provenance, publishing, deployment, or bounty submission has completed.
