# Phase 13 Subroadmap: Evidence Review Workflow and Gap-Closure Governance

## Objectives

Phase 13 converts the Phase 12 hash-only validation-evidence ledger into a metadata-only human evidence-review workflow and gap-closure proposal layer.

The objective is not to review external evidence, close production gaps, or claim production readiness inside ChatGPT Project Mode. The objective is to make future human release/AppSec review decisions deterministic, schema-validated, hash-bound to Phase 12 artifacts, and actionable for manual governance updates.

## Deliverables

Completed deliverables:

- Full review of every Markdown file in the unzipped Phase 12 source bundle before coding.
- `MARKDOWN_REVIEW_PHASE13.md` review ledger with file counts, hashes, and reconciliation notes.
- `src/bountyclaw/evidence_review/` subsystem.
- `EvidenceReviewRecord` model.
- `EvidenceReviewDecisionFile` model.
- `EvidenceReviewTemplateResult` model.
- `EvidenceReviewStatusResult` model.
- `GapClosureProposalResult` model.
- `EvidenceReviewExportResult` model.
- `EvidenceReviewVerificationResult` model.
- `bountyclaw evidence-review template` CLI command.
- `bountyclaw evidence-review status` CLI command.
- `bountyclaw evidence-review closure-proposals` CLI command.
- `bountyclaw evidence-review export-package` CLI command.
- `bountyclaw evidence-review verify` CLI command.
- `scripts/phase13_verify.py` deterministic verifier.
- CI workflow definition hook for Phase 13 verification.
- Phase 11 handoff export update with `EVIDENCE_REVIEW_COMMANDS.md`.
- Tests for review templates, review metadata, hash matching, blocked proposals, export, CLI JSON output, handoff updates, and CI workflow content.
- Governance/documentation updates.
- Production gap tracker updates with Phase 13-specific Codex/local/CI/human evidence-review gaps.

## Subsystem Boundaries

In scope:

- Local-only review-decision template generation.
- Local-only review metadata schema validation.
- Hash-bound comparison between Phase 12 ledger artifacts and future human review decisions.
- Gap-closure proposal generation for manual governance updates.
- Exporting metadata-only review packages.
- Verifying that review tooling cannot auto-close gaps or raise production readiness.
- Updating handoff instructions so future executors know how to run the review workflow.

Out of scope:

- Hosted CI execution.
- External validation artifact production.
- Private raw evidence inspection.
- Human release/AppSec review execution.
- Closing production gaps.
- Editing `PRODUCTION_GAP_TRACKER.md` from CLI output.
- Recalculating readiness from review metadata alone.
- Static/security tool execution when unavailable.
- External scanner execution.
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

Phase 13 depends on:

- Phase 12 validation-evidence ledger and gap-readiness mapping.
- Phase 11 handoff evidence template.
- Phase 10 hardening verifier.
- Phase 9 release verifier.
- `PRODUCTION_GAP_TRACKER.md` as the production-completion ledger.
- Existing CLI framework.
- Existing non-networked local validation environment.

## Implementation Sequence

Completed sequence:

1. Unzipped the latest Phase 12 repository bundle.
2. Reviewed every Markdown file in the unzipped bundle before coding.
3. Reconciled Phase 12 roadmap, architecture, agents, handoff, release, rollback, security-validation, and gap tracker state.
4. Created `PHASE_13_SUBROADMAP.md` before implementation.
5. Added evidence-review models.
6. Added evidence-review service functions.
7. Added evidence-review CLI commands.
8. Added `scripts/phase13_verify.py`.
9. Added CI workflow hook definition.
10. Updated version and phase metadata to `0.13.0` / Phase 13.
11. Updated Phase 11 handoff package generation with evidence-review commands.
12. Added Phase 13 tests.
13. Validated locally.
14. Updated architecture, roadmap, agents, README, release/security/rollback docs, handoff docs, and gap tracker.
15. Built Phase 13 repository bundle.

## Validation Sequence

Completed local validation:

- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
- `PYTHONPATH=src python -m compileall -q src tests scripts`
- `PYTHONPATH=src python -m bountyclaw --help`
- `PYTHONPATH=src python -m bountyclaw doctor`
- `PYTHONPATH=src python -m bountyclaw evidence-review template --root . --json`
- `PYTHONPATH=src python -m bountyclaw evidence-review status --root . --json`
- `PYTHONPATH=src python -m bountyclaw evidence-review closure-proposals --root . --json`
- `PYTHONPATH=src python -m bountyclaw evidence-review export-package --root . --output <tmpdir> --json`
- `PYTHONPATH=src python -m bountyclaw evidence-review verify --root . --json`
- `PYTHONPATH=src python scripts/phase13_verify.py --root . --json`
- Phase 9, Phase 10, Phase 11, and Phase 12 verifier regression checks.
- ZIP extraction validation with pytest, compileall, and Phase 13 verification.

Environment-limited validation remains deferred:

- Hosted CI execution.
- Clean package build/install validation.
- Ruff/mypy/bandit/pip-audit execution where tools are unavailable.
- External scanner binary and sandbox validation.
- Live provider validation.
- Real MCP/browser runtime validation.
- Real external evidence artifact creation.
- Human evidence review and approval.
- Human report quality review.
- Performance, retention, backup/restore, and rollback drills.
- Branch protection, signing/provenance, and publishing dry run.

## Rollback Strategy

Rollback target: Phase 12 validation-evidence ledger baseline.

Rollback steps:

1. Remove `PHASE_13_SUBROADMAP.md`.
2. Remove `MARKDOWN_REVIEW_PHASE13.md`.
3. Remove `src/bountyclaw/evidence_review/`.
4. Remove `scripts/phase13_verify.py`.
5. Remove `tests/test_evidence_review_phase13.py`.
6. Revert `bountyclaw evidence-review` CLI additions.
7. Revert `.github/workflows/ci.yml` Phase 13 verification step.
8. Revert Phase 11 handoff export additions for evidence-review commands.
9. Revert version/phase metadata to Phase 12.
10. Revert Phase 13 documentation and gap-tracker updates.

No external resources need cleanup because Phase 13 creates no cloud infrastructure, registry artifacts, hosted CI state, credentials, live provider calls, MCP/browser runtimes, active validation state, evidence storage service, branch protection, signing/provenance, package publishing, or bounty submissions.

## Drift-Prevention Constraints

- Do not treat review metadata as raw evidence.
- Do not inspect, summarize, print, classify, or trust raw evidence contents.
- Do not close production gaps from hashes or review metadata alone.
- Do not recalculate production readiness from unreviewed or unmerged proposal output.
- Do not claim hosted CI, clean install, scanners, live providers, real MCP/browser runtimes, signing, publishing, branch protection, evidence review, or report review were executed unless future evidence exists.
- Do not enable network target contact.
- Do not enable active validation.
- Do not add automated report submission.
- Preserve Phase 12 validation-evidence ledger controls as rollback fallback.

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
- private evidence storage/access-control policy
- production rollback drills over real state
- human evidence acceptance or production gap closure authority

## Expected Unresolved Gaps

- External validation execution remains unperformed.
- Evidence artifacts are absent until future environments produce them.
- Evidence review decisions are absent until future human reviewers create them.
- Review metadata does not prove evidence quality without human context.
- Evidence-based gap closure remains unperformed.
- Hosted CI and clean install remain unproven.
- Real scanner, sandbox, live provider, MCP/browser, report-quality, performance, rollback, signing, and publishing validation remain unproven.
- Human final authorization and manual submission remain mandatory.

## Expected Future Continuation Tasks

- Run `bountyclaw handoff export --root . --output validation_handoff --json` in a real Codex/local/CI workspace.
- Execute each `P11-HANDOFF-*` task in the required environment.
- Store produced artifacts under `validation_evidence/` using the filenames from `bountyclaw handoff evidence-template --root . --json`.
- Run Phase 12 ledger commands to hash artifacts and map them to gaps.
- Run `bountyclaw evidence-review template --root . --evidence-dir validation_evidence --json`.
- Have a human release/AppSec reviewer inspect private/redacted artifacts and create `validation_evidence/evidence_review_decisions.json`.
- Run `bountyclaw evidence-review status --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`.
- Run `bountyclaw evidence-review closure-proposals --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`.
- Run `bountyclaw evidence-review export-package --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --output validation_evidence_review --json`.
- Have a human release/AppSec reviewer update `PRODUCTION_GAP_TRACKER.md`, `SECURITY_VALIDATION.md`, `RELEASE.md`, and `ROLLBACK.md`, and recalculate production readiness only after real reviewed evidence exists.

## Completion Status

Completed in ChatGPT Project Mode.

Phase 13 completion means Markdown review, evidence-review metadata tooling, hash-bound review decision checks, gap-closure proposal generation, local export, verifier script, CI hook definition, handoff-command update, tests, and governance updates exist. It does not mean any external validation, hosted CI execution, package install, scanner runtime, live provider, real MCP/browser, human evidence review, signing/provenance, publishing, deployment, production gap closure, or production readiness validation has completed.
