# Phase 15 Subroadmap: External Validation Runbook and Execution Journal

## Objectives

- Preserve Phase 14 gap tracker governance as the rollback baseline.
- Convert unresolved `PRODUCTION_GAP_TRACKER.md` entries and Phase 14 `CODEX-PGT-*` backlog items into a deterministic external validation runbook.
- Provide a metadata-only execution journal template for Codex/local/CI/human executors.
- Assess future execution journal metadata without inspecting raw evidence, closing gaps, or raising production readiness.
- Export a runbook package that connects Phase 11 handoff, Phase 12 evidence ledger, Phase 13 evidence review, and Phase 14 gap tracker backlog workflows.
- Update handoff and gap files thoroughly for work that cannot be completed inside ChatGPT Project Mode.

## Deliverables

- `MARKDOWN_REVIEW_PHASE15.md` documenting the mandatory full Markdown review of the unzipped Phase 14 source bundle.
- `src/bountyclaw/validation_runbook/` subsystem.
- `bountyclaw validation-runbook build` command.
- `bountyclaw validation-runbook journal-template` command.
- `bountyclaw validation-runbook journal-status` command.
- `bountyclaw validation-runbook export` command.
- `bountyclaw validation-runbook verify` command.
- `scripts/phase15_verify.py`.
- Phase 11 handoff-package update with Phase 15 runbook commands.
- CI workflow hook definition for Phase 15 verification.
- Tests for runbook generation, metadata-only journal validation, export, handoff-command integration, and verification.
- Governance and gap tracker updates.

## Subsystem Boundaries

### In Scope

- Metadata-only runbook generation from existing unresolved gaps and Codex backlog items.
- Metadata-only future execution journal schema and template.
- Journal-status assessment based on task IDs, gap IDs, artifact IDs, and SHA-256 hashes only.
- Local package export for future Codex/local/CI/human executors.
- Local verification that Phase 15 tooling remains commit-ready and Codex-ready.
- Handoff command updates.
- Gap tracker updates for remaining external execution/review work.

### Out of Scope

- Hosted CI execution.
- External scanner execution.
- Clean package install validation.
- OS/container sandbox validation.
- Network-egress validation.
- Live provider calls.
- Real MCP/browser runtimes.
- Active validation.
- Exploit execution.
- Raw evidence inspection.
- Human evidence approval.
- Production gap closure.
- Production readiness increase from runbook or journal metadata.
- Package publishing, signing, provenance, branch protection, or bounty submission.

## Dependencies

- Completed Phase 14 gap tracker governance and Codex backlog export.
- Completed Phase 13 evidence-review workflow.
- Completed Phase 12 validation-evidence ledger.
- Completed Phase 11 handoff package.
- Completed Phase 10 hardening checks.
- Existing `PRODUCTION_GAP_TRACKER.md` entries with mandatory fields.

## Implementation Sequence

1. Unzip the Phase 14 repository bundle.
2. Fully review all Markdown source documents before coding.
3. Create this Phase 15 subroadmap.
4. Add `validation_runbook` models and service functions.
5. Add CLI commands and script entrypoint.
6. Update Phase 11 handoff output with runbook commands.
7. Add local tests.
8. Update CI workflow definition.
9. Update governance, release, rollback, security-validation, handoff, and gap files.
10. Run local validation.
11. Package the Phase 15 repository bundle.

## Validation Sequence

- Run the full test suite locally.
- Run compile validation for `src`, `tests`, and `scripts`.
- Run CLI smoke checks for Phase 15 commands.
- Run `scripts/phase15_verify.py`.
- Re-run release, hardening, handoff, validation-evidence, evidence-review, and gap tracker verifiers.
- Validate the ZIP extraction artifact.
- Confirm no `__pycache__`, `.pyc`, or `.pytest_cache` artifacts are shipped.

## Rollback Strategy

Rollback to Phase 14 by removing:

- `PHASE_15_SUBROADMAP.md`
- `MARKDOWN_REVIEW_PHASE15.md`
- `src/bountyclaw/validation_runbook/`
- `scripts/phase15_verify.py`
- `tests/test_validation_runbook_phase15.py`
- `bountyclaw validation-runbook` CLI additions
- Phase 15 CI workflow hook
- Phase 15 governance, documentation, and gap tracker updates

Phase 14 gap tracker governance remains the rollback-safe baseline.

## Drift-Prevention Constraints

- Do not execute the runbook inside ChatGPT Project Mode.
- Do not read or print raw external evidence contents.
- Do not close gaps from journal metadata.
- Do not increase production readiness from unreviewed metadata.
- Do not enable network, live providers, real MCP/browser runtime, active validation, or automated submission.
- Treat all future journal entries as untrusted until Phase 12/13/14 governance workflows process reviewed artifacts.

## Environment Limitations

ChatGPT Project Mode cannot complete hosted CI execution, package install validation, scanner/sandbox validation, live provider validation, real MCP/browser runtime validation, private evidence review, branch protection, signing/provenance, package publishing, or human manual submission review. Phase 15 records these as future Codex/local/CI/human tasks.

## Expected Unresolved Gaps

- Real runbook execution remains external.
- Journal metadata has not been produced by future executors.
- Evidence artifacts have not been produced, hashed, reviewed, or linked to gap closures.
- Hosted enforcement and branch protection remain external.
- Production readiness remains below 100% until real evidence is reviewed and gaps are closed manually.

## Expected Future Continuation Tasks

- Execute the Phase 15 runbook in Codex/local/CI/human environments.
- Record metadata-only execution journal entries.
- Store and hash reviewed/redacted evidence artifacts.
- Process evidence with Phase 12 ledger tooling.
- Process review metadata with Phase 13 tooling.
- Re-audit the gap tracker with Phase 14 tooling.
- Close gaps only with human-reviewed evidence and rollback notes.

## Completion Status

Completed inside ChatGPT Project Mode. External execution remains deferred and explicitly tracked.
