# PHASE_6_SUBROADMAP.md

# Phase 6: Triage and Report Drafting Workflow

## Status

Completed.

## Objectives

Phase 6 adds deterministic human-reviewed triage state and bounty report draft generation from already-normalized, redacted local findings. It does not add automated report submission, live LLM provider calls, MCP tools, browser automation, network access, active validation, or exploit execution.

Completed objectives:

1. Reconcile Phase 5 governance and source state before implementation.
2. Create this `PHASE_6_SUBROADMAP.md` before coding.
3. Add explicit `triage.review` scope action while preserving `report.draft` authorization.
4. Add human triage review states:
   - `needs_review`
   - `needs_more_evidence`
   - `approved_for_draft`
   - `rejected_false_positive`
5. Add local SQLite persistence for triage reviews and report drafts.
6. Add deterministic report draft models and markdown rendering.
7. Require `approved_for_draft` before draft generation.
8. Generate report drafts from canonical findings, redacted evidence, human triage rationale, and optional mocked model triage output.
9. Preserve no-unvalidated-claim rules and explicit non-submission controls.
10. Add CLI commands:
    - `bountyclaw report review`
    - `bountyclaw report draft`
    - `bountyclaw report list`
11. Add tests for scope enforcement, human-review requirements, non-submitting report safety, optional mocked triage context, CLI JSON output, and persisted draft listing.
12. Update `ROADMAP.md`, `ARCHITECTURE.md`, `AGENTS.md`, `README.md`, and `PRODUCTION_GAP_TRACKER.md` at phase completion.

## Deliverables

Completed:

- `src/bountyclaw/reports/` subsystem.
- `TriageReview` model.
- `ReportDraft` model.
- `ReportDraftResult` model.
- `ReportStore` SQLite persistence layer.
- Scope-gated triage-review service.
- Scope-gated report-drafting service.
- Deterministic markdown report draft renderer.
- Safety invariants that keep drafts non-submitting and static-only.
- CLI report commands.
- Phase 6 tests.

Deferred:

- Live provider-based report drafting.
- Program-specific template tuning against real bounty platforms.
- Real report quality scoring.
- External bounty-platform API integration.
- Automated submission, intentionally.
- Active validation workflows.
- Compliance/legal review of generated reports.
- Large corpus evaluation for report accuracy and payout outcomes.

## Subsystem Boundaries

### In Scope

- Human triage review state for stored canonical findings.
- Local report draft persistence.
- Deterministic report draft generation from redacted evidence.
- Optional inclusion of Phase 5 mocked model triage output as advisory context.
- Tests proving report drafts are not submissions and do not claim active validation.

### Out of Scope

- Automated bounty submission.
- Live provider calls.
- Network interaction with targets.
- Browser automation.
- MCP tools.
- Active exploit validation.
- Report claims of confirmed exploitability or confirmed impact without human validation.
- Payout optimization claims not supported by evidence.

## Dependencies

Completed prerequisites:

- Phase 1 scope gate and CLI foundation.
- Phase 2 repository intake and deterministic scan planning.
- Phase 3 local static scanner MVP.
- Phase 4 canonical findings, redaction engine, and SQLite evidence store.
- Phase 5 model router, prompt-safety envelope, and deterministic mock triage.

New Phase 6 dependencies added:

- `triage.review` scope action.
- Existing `report.draft` scope action.
- Report persistence tables in the same local SQLite store.
- Human review approval before draft creation.

## Implementation Sequence

Completed sequence:

1. Reconciled uploaded governance files and the Phase 5 repository bundle.
2. Created `PHASE_6_SUBROADMAP.md` before implementation.
3. Added report models.
4. Added report SQLite store.
5. Added scope-gated triage review service.
6. Added scope-gated report drafting service.
7. Extended scope manifest actions with `triage.review`.
8. Added report CLI commands.
9. Added Phase 6 tests.
10. Ran validation.
11. Updated governance files and gap tracker.

## Validation Sequence

Executed and passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -m bountyclaw --help
PYTHONPATH=src python -m bountyclaw doctor
PYTHONPATH=src python -m bountyclaw report review --help
PYTHONPATH=src python -m bountyclaw report draft --help
PYTHONPATH=src python -m bountyclaw findings collect --manifest <scope.yaml> --repo <repo> --store <evidence.sqlite> --enable-local-scanner --json
PYTHONPATH=src python -m bountyclaw report review --manifest <scope.yaml> --repo <repo> --store <evidence.sqlite> --finding-id <id> --reviewer <reviewer> --rationale <rationale> --status approved_for_draft --json
PYTHONPATH=src python -m bountyclaw report draft --manifest <scope.yaml> --repo <repo> --store <evidence.sqlite> --finding-id <id> --include-mock-triage --enable-mock-model --json
PYTHONPATH=src python -m bountyclaw report list --store <evidence.sqlite> --json
```

Observed results:

- 72 tests passed.
- Compile validation passed.
- CLI smoke validation passed.
- Phase 6 end-to-end local fixture smoke validation passed.

## Rollback Strategy

To revert Phase 6:

1. Remove `PHASE_6_SUBROADMAP.md`.
2. Remove `src/bountyclaw/reports/`.
3. Remove `tests/test_reports_phase6.py`.
4. Revert `triage.review` additions in `src/bountyclaw/scope/models.py`.
5. Revert report CLI additions in `src/bountyclaw/cli.py`.
6. Revert Phase 6 version/config text updates.
7. Revert Phase 6 documentation and gap-tracker updates.

Rollback fallback:

- Phase 5 mocked model triage remains available.
- Phase 4 `findings collect` and `findings list` remain available.
- No external state, provider credentials, network calls, bounty-platform actions, or production resources were introduced.

## Drift-Prevention Constraints

- Do not implement report submission in Phase 6.
- Do not call live LLM providers.
- Do not browse or contact targets.
- Do not generate exploit steps beyond a safe manual validation checklist.
- Do not claim active validation, confirmed impact, or confirmed exploitability.
- Do not allow report drafts without `approved_for_draft` human triage state.
- Do not bypass `triage.review` or `report.draft` scope authorization.

## Environment Limitations

ChatGPT Project Mode allowed local Python implementation and tests but did not allow:

- validation against real bounty program report templates
- live bounty-platform submission flow validation
- human legal/compliance review
- payout-quality benchmarking
- external red-team review of report safety
- broad adversarial evaluation for hallucinated impact claims
- integration with live providers, MCP tools, browsers, or platform APIs

All such tasks are recorded in `PRODUCTION_GAP_TRACKER.md`.

## Expected Unresolved Gaps

Remaining after Phase 6:

- Report drafts are local artifacts only and not validated against real bounty program expectations.
- Report quality is fixture-tested only.
- Program-specific policy parsing is not implemented.
- Automated bounty submission remains intentionally absent.
- Live model providers remain disabled.
- MCP and browser workflows are not implemented.
- CI/CD and external validation remain missing.

## Expected Future Continuation Tasks

Next phase:

- Create `PHASE_7_SUBROADMAP.md`.
- Implement policy-bound MCP registry and headless browser foundations, if still desired.
- Keep tool actions allowlisted, scope-gated, local-testable, and non-submitting.
- Preserve Phase 6 report drafting as a rollback-safe fallback.

## Completion Summary

Phase 6 completed deterministic human-reviewed triage state and safe bounty report draft generation. The workflow now moves from local static findings to redacted evidence, mocked advisory triage, human approval, and a non-submitting markdown report draft while preserving authorized-only, local-first, no-network, no-active-validation, and no-automated-submission constraints.
