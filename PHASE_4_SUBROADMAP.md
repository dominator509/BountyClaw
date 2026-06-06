# Phase 4 Subroadmap: Findings Normalization and Evidence Store

## Status

Completed.

## Objectives

1. Define canonical finding and evidence schemas that can outlive scanner-specific output.
2. Normalize Phase 3 preliminary scanner findings deterministically without LLM assistance.
3. Deduplicate equivalent preliminary findings into canonical findings.
4. Redact likely secrets before persistence.
5. Persist scan runs, canonical findings, and redacted evidence in a local SQLite store.
6. Preserve the Phase 3 scanner JSON output path as a rollback-safe fallback.
7. Keep all behavior local-only, scope-gated, non-destructive, and report-submission-free.

## Deliverables

- `src/bountyclaw/findings/models.py`: canonical finding, evidence, redaction, normalization, collection, and listing models.
- `src/bountyclaw/findings/redaction.py`: deterministic built-in redaction patterns for common secret shapes.
- `src/bountyclaw/findings/normalizer.py`: scanner-result normalization, deduplication, and evidence construction.
- `src/bountyclaw/findings/store.py`: local SQLite evidence store with scan-run, finding, and evidence tables.
- `src/bountyclaw/findings/service.py`: scope-gated findings collection service.
- `src/bountyclaw/findings/__init__.py`: stable findings subsystem exports.
- CLI commands:
  - `bountyclaw findings collect`
  - `bountyclaw findings list`
- Phase 4 tests in `tests/test_findings_phase4.py`.
- Updated governance files and production gap tracker.

## Subsystem Boundaries

### In Scope

- Local canonical finding normalization.
- Deterministic deduplication.
- Redacted evidence generation.
- Local SQLite persistence outside the target repository.
- Scope-gated `findings.write` authorization.
- Tests proving redaction, deduplication, store isolation, CLI behavior, and Phase 3 fallback preservation.

### Out of Scope

- LLM triage or report drafting.
- MCP tools.
- Browser automation.
- Network scanning or live target interaction.
- Active exploit validation.
- Automated bounty submission.
- External scanner binary validation.
- Encrypted evidence store, migrations, backup/restore drills, or enterprise deployment.

## Dependencies

- Phase 0 governance completed.
- Phase 1 CLI and scope gate completed.
- Phase 2 repository intake and deterministic scan planning completed.
- Phase 3 scanner adapter MVP completed.
- Valid scope manifests must include `repo.read`, `scan.local_static`, and `findings.write` for `findings collect`.

## Implementation Sequence

1. Reconcile roadmap, architecture, agent governance, and gap tracker.
2. Create this `PHASE_4_SUBROADMAP.md` before declaring Phase 4 complete.
3. Add findings subsystem models.
4. Add redaction utility.
5. Add deterministic normalizer and deduplication.
6. Add local SQLite store.
7. Add scope-gated findings collection service.
8. Add CLI commands.
9. Add tests.
10. Update governance and gap tracker.
11. Validate.
12. Package commit-ready artifact.

## Validation Sequence

Completed validation:

1. `PYTHONPATH=src pytest -q`
2. `PYTHONPATH=src python -m compileall -q src tests`
3. CLI smoke checks:
   - `python -m bountyclaw --help`
   - `python -m bountyclaw doctor`
   - `python -m bountyclaw findings collect --help`
   - `python -m bountyclaw findings list --help`
   - `python -m bountyclaw findings collect` against an authorized local fixture repository
   - `python -m bountyclaw findings list` against the generated local SQLite evidence store

## Rollback Strategy

Rollback-safe fallback is Phase 3 scanner JSON output.

To revert Phase 4:

1. Remove `PHASE_4_SUBROADMAP.md`.
2. Remove `src/bountyclaw/findings/`.
3. Remove `tests/test_findings_phase4.py`.
4. Revert `src/bountyclaw/cli.py` findings commands.
5. Revert `findings.write` action additions in scope models.
6. Revert Phase 4 updates in governance files and version metadata.
7. Retain Phase 3 `bountyclaw scan repo --json` behavior.

No cloud infrastructure, external accounts, production deployment, scanner binary installation, secrets, or hosted state were introduced.

## Drift-Prevention Constraints

- Do not persist raw source excerpts.
- Do not persist raw secret values.
- Do not write evidence stores inside target repositories.
- Do not call LLM providers.
- Do not use MCP/browser tools.
- Do not perform network actions.
- Do not perform active validation.
- Do not submit reports.
- Do not claim scanner correctness beyond validated fixtures.
- Do not weaken scope-gate checks for convenience.

## Environment Limitations

The following cannot be fully completed in ChatGPT Project Mode:

- Real-world large repository evidence-store validation.
- External scanner binary output ingestion validation.
- Redaction validation against representative secret corpora.
- Evidence-store encryption-at-rest validation.
- SQLite migration/backward-compatibility drills.
- Backup/restore drills.
- Cross-platform clean install validation.
- CI/CD quality/security gate execution.
- External AppSec review.

## Expected Unresolved Gaps

- Real external scanner adapters remain unvalidated.
- Redaction rules are baseline patterns and require corpus-based validation.
- Evidence store is not encrypted at rest.
- Evidence store schema migrations are not implemented.
- Backup/restore and retention policies are not validated.
- LLM prompt-safety and model routing are not implemented.
- Report drafting remains unavailable.

## Expected Future Continuation Tasks

1. Create `PHASE_5_SUBROADMAP.md`.
2. Implement provider-neutral model-router interfaces without live model calls at first.
3. Add prompt safety boundaries and prompt-injection fixtures.
4. Ensure only redacted canonical findings/evidence can be sent to model clients.
5. Keep local-only and cloud-model privacy controls explicit.
6. Update `ROADMAP.md`, `PHASE_5_SUBROADMAP.md`, and `PRODUCTION_GAP_TRACKER.md` at Phase 5 completion.

## Completion Criteria

Completed:

- Canonical finding schema implemented.
- Redacted evidence schema implemented.
- Deterministic deduplication implemented.
- SQLite evidence store implemented.
- Store path inside target repository denied.
- Scope-gated `findings.write` required.
- Redaction tests pass.
- Persistence tests pass.
- CLI findings collect/list tests pass.
- Phase 3 scan JSON fallback preserved.
- Governance files updated.
- Gap tracker updated.

## Phase 4 Completion Notes

Phase 4 is complete within ChatGPT Project Mode. Production use remains blocked by unresolved external validation, scanner coverage, evidence-store hardening, CI/CD, and human review requirements recorded in `PRODUCTION_GAP_TRACKER.md`.
