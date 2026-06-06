# BountyClaw Roadmap

## 1. Roadmap Governance

BountyClaw development follows this mandatory sequence:

DISCOVER -> RECONCILE -> PLAN -> PATCH -> VALIDATE -> GAP ANALYSIS -> REVIEW -> COMMIT-READY

Before every task, agents must reread:

1. `ARCHITECTURE.md`
2. `ROADMAP.md`
3. active `PHASE_X_SUBROADMAP.md`
4. `AGENTS.md`
5. `PRODUCTION_GAP_TRACKER.md`

No implementation phase may begin until its phase subroadmap exists.

## 2. Current Status

- Current project: BountyClaw.
- Current roadmap position: Phase 19 completed in ChatGPT Project Mode; external production validation execution, source-baseline-bound evidence production, human evidence review, readiness attestation creation, Phase 14/15 backlog execution, Phase 18 dashboard handoff execution, Phase 19 quality-gate hosted enforcement, evidence-based manual gap closure, and readiness recalculation remain for Codex/local/CI/human environments.
- Current production readiness: 94%.
- Current implementation state: minimal executable local CLI, configuration model, scope manifest schema, deny-by-default scope gate, initial audit event model, read-only repository intake, deterministic scan planning, scanner adapter interfaces, controlled subprocess wrapper, built-in local Python static scanner, preliminary finding records, canonical findings normalization, deterministic deduplication, redaction engine, local SQLite evidence store, findings CLI commands, provider-neutral model router metadata, deterministic mock provider, prompt-safety envelope builder, prompt-injection signal detection, mocked model triage command, human triage review state, non-submitting report draft generation, report draft persistence, report CLI commands, local policy summary reader, fixture-only MCP registry/tool allowlist, fixture-only browser policy ingestion commands, local memory store, non-executing skill templates, memory/skill CLI commands, release-control models, release checklist/verification/rollback CLI commands, CI workflow definitions, release documentation, Phase 10 hardening models, deterministic redaction/prompt-safety corpora, external-validation planning, hardening CLI commands, Phase 11 handoff plan/evidence-template/export/verify commands, Phase 12 validation-evidence ledger/gap-readiness/export/verify commands, hash-only future artifact inventory, gap-to-evidence mapping, Phase 12 Markdown review ledger, evidence-review template/status/closure-proposals/export/verify commands, metadata-only human review decision schema, gap-closure proposal generation, Phase 13 Markdown review ledger, Phase 14 Markdown review ledger, gap tracker audit commands, Codex backlog export commands, Phase 15 Markdown review ledger, external validation runbook commands, metadata-only execution journal template/status commands, validation runbook export commands, hash-only validation-baseline commands, closure-gate readiness-attestation commands, readiness-dashboard commands, external executor index, Phase 19 quality-gates commands, local ruff/mypy/Bandit/package gate remediation, and tests.
- Current risk posture: High, because Phase 19 quality-gate tooling, Phase 18 readiness-dashboard tooling, Phase 17 closure-gate tooling, Phase 16 validation-baseline tooling, and Phase 15 validation-runbook tooling are complete locally but external runbook execution, execution journal metadata, external evidence artifacts, human evidence review execution, evidence-based gap closure, hosted CI execution, clean package install validation, artifact signing/provenance, branch protection, real MCP/browser runtime validation, program-specific policy ingestion validation, production memory/privacy retention review, program-specific report quality validation, dependency/advisory scanning, live provider validation, external scanner validation, sandbox validation, memory/evidence-store migration/backup validation, realistic redaction/model-payload validation, performance tests, rollback drills, and external production validations are not yet complete.

## 3. Phase Summary

| Phase | Name | Status | Production Readiness Contribution | Notes |
|---|---|---:|---:|---|
| 0 | Governance and Architecture Initialization | Completed | 2% | Mandatory control files created. |
| 1 | CLI Skeleton and Safety Gate Foundation | Completed | +6% achieved | Local CLI, config model, scope manifest schema, deny-by-default scope gate, audit event model, and tests created. |
| 2 | Local Repository Intake and Deterministic Scan Planning | Completed | +6% achieved | Read-only repo fingerprinting and deterministic non-executing scan plan generation. |
| 3 | Static Scanner Adapter MVP | Completed | +8% achieved | Added scanner adapter framework, controlled subprocess wrapper, built-in local Python static scanner, preliminary findings, CLI command, feature gate, and tests. |
| 4 | Findings Normalization and Evidence Store | Completed | +8% achieved | Canonical finding schema, deterministic deduplication, redaction-first SQLite evidence store, findings CLI, and tests. |
| 5 | LLM Model Router and Prompt-Safety Layer | Completed | +8% achieved | Provider catalog, routing policy, prompt-safety envelopes, mocked provider, mocked triage CLI, and tests. |
| 6 | Triage and Report Drafting Workflow | Completed | +10% achieved | Human triage review state, non-submitting markdown report drafts, report persistence, CLI commands, and tests. |
| 7 | MCP and Headless Browser Integration | Completed | +8% achieved | Fixture-only MCP registry/tool allowlist and local policy ingestion; no live browser, network, target contact, or submission. |
| 8 | Memory, Skills, and Workflow Learning | Completed | +6% achieved | Local memory store, explicit approval, export/delete, non-executing skill templates, and tests. |
| 9 | CI/CD, Packaging, and Release Controls | Completed | +8% achieved | Local release checks, CI workflow definitions, security/quality gate definitions, release docs, rollback docs, and tests; hosted execution deferred. |
| 10 | Production Hardening and External Validation | Completed in ChatGPT Project Mode | +8% achieved locally; external validation still deferred | Local hardening verifier, redaction corpus, prompt-safety corpus, external-validation plan, CI hook, docs, and tests; hosted CI, clean installs, scanners, sandbox, live providers, real MCP/browser, performance, rollback, signing, publishing, and human review remain deferred. |
| 11 | External Validation Handoff Package | Completed in ChatGPT Project Mode | +4% achieved locally; external execution still deferred | Codex/local/CI/human handoff plan, evidence templates, export package, handoff verifier, CI hook, docs, and tests; does not execute external validation. |
| 12 | Validation Evidence Ledger and Gap-Closure Readiness | Completed in ChatGPT Project Mode | +2% achieved locally; evidence review still deferred | Hash-only evidence artifact ledger, gap-to-artifact readiness mapping, ledger export, Phase 12 verifier, handoff-command update, docs, and tests; does not validate artifacts or close gaps. |
| 13 | Evidence Review Workflow and Gap-Closure Governance | Completed in ChatGPT Project Mode | +2% achieved locally; human review and gap closure still deferred | Metadata-only review decision templates, hash-bound review status, gap-closure proposals, review package export, Phase 13 verifier, handoff-command update, docs, and tests; does not inspect evidence, close gaps, or raise readiness from proposals. |
| 14 | Gap Tracker Governance and Codex Backlog Export | Completed in ChatGPT Project Mode | +2% achieved locally; external backlog execution still deferred | Metadata-only gap tracker parser, required-field audit, Codex backlog export, gap tracker package export, Phase 14 verifier, handoff-command update, docs, and tests; does not close gaps or raise readiness. |
| 15 | External Validation Runbook and Execution Journal | Completed in ChatGPT Project Mode | +2% achieved locally; external runbook execution still deferred | Metadata-only runbook derived from unresolved gaps/backlog, execution journal template/status, runbook package export, Phase 15 verifier, handoff-command update, docs, and tests; does not execute validation, inspect evidence, close gaps, or raise readiness. |
| 16 | Validation Baseline Manifest and Source Snapshot Binding | Completed in ChatGPT Project Mode | +1% achieved locally; baseline-bound external evidence still deferred | Hash-only source snapshot manifest, baseline export, Phase 16 verifier, handoff-command update, docs, and tests; does not inspect evidence, close gaps, or raise readiness. |
| 17 | Closure Gate and Readiness Attestation Governance | Completed in ChatGPT Project Mode | +1% achieved locally; human attestation and manual gap closure still deferred | Metadata-only readiness attestation template/status/export/verify, handoff-command update, docs, and tests; does not inspect evidence, close gaps, or raise readiness. |
| 18 | Readiness Dashboard and External Executor Index | Completed in ChatGPT Project Mode | +1% achieved locally; external dashboard execution still deferred | Metadata-only dashboard over Phase 9-17 verifiers, ordered executor index, dashboard export, Phase 18 verifier, handoff-command update, docs, and tests; does not execute validation, inspect evidence, close gaps, or raise readiness. |
| 19 | Local Quality/Security Gate Execution and Remediation | Completed in ChatGPT Project Mode | +1% achieved locally; online dependency audit and hosted enforcement still deferred | Executed and remediated local tests, compile, ruff, mypy, Bandit, build, clean-install gates; added quality-gates CLI/export/verifier; pip-audit attempted but DNS-blocked; no gap closure or production claim. |

Readiness percentages are governance estimates, not claims of production validation.

## 4. Phase 0: Governance and Architecture Initialization

Status: Completed.

Deliverables completed:

- `ARCHITECTURE.md`
- `AGENTS.md`
- `ROADMAP.md`
- `PHASE_0_SUBROADMAP.md`
- `PRODUCTION_GAP_TRACKER.md`

Validation completed:

- Mandatory governance file presence check.
- Required gap tracker section presence check.
- Phase 0 subroadmap completion status check.

Deferred:

- No application code created.
- No runtime validation possible.
- No CI/CD validation possible.
- No scanner validation possible.
- No LLM provider validation possible.

## 5. Phase 1: CLI Skeleton and Safety Gate Foundation

Status: Completed.

Subroadmap completed:

- `PHASE_1_SUBROADMAP.md`

Objectives completed:

1. Created minimal Python project skeleton.
2. Added CLI entrypoint.
3. Added configuration loading with disabled-by-default risky capabilities.
4. Added scope manifest schema.
5. Added deny-by-default scope validation.
6. Added initial audit event and JSONL writer model.
7. Added tests for safety gate and CLI smoke behavior.

Phase 1 must not include:

- scanner integrations beyond placeholders
- LLM provider calls
- network scanning
- headless browser automation
- MCP integrations
- automated bounty submission

Completion criteria completed:

- CLI runs locally through `python -m bountyclaw`.
- `doctor` reports environment and disabled capability state.
- `scope validate` rejects invalid manifests.
- `scope check` rejects missing manifests, out-of-scope repositories, prohibited actions, unallowlisted actions, and network/domain targets.
- Tests pass locally: 15 pytest tests.
- New and remaining gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 6. Phase 2: Local Repository Intake and Deterministic Scan Planning

Status: Completed.

Subroadmap completed:

- `PHASE_2_SUBROADMAP.md`

Objectives completed:

- Read local repository metadata after scope-gate approval.
- Detect languages and package/configuration manifests deterministically.
- Generate deterministic scan plans without executing scanners.
- Keep operations read-only and avoid source-content persistence.
- Add local tests for repository intake, scope enforcement, read-only behavior, deterministic planning, and CLI output.

Completion criteria completed:

- `bountyclaw repo inspect` inspects an allowlisted local repository with metadata-only reads.
- `bountyclaw repo plan` emits a deterministic scan plan with `scanners_execute=false`.
- Scope-denied repository targets fail closed before intake or planning.
- Local pytest validation passes with 36 tests.
- Phase 2 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 7. Phase 3: Static Scanner Adapter MVP

Status: Completed.

Subroadmap completed:

- `PHASE_3_SUBROADMAP.md`

Objectives completed:

- Added scanner adapter interface and runtime context models.
- Added controlled subprocess wrapper and command policy for future external scanners.
- Integrated the first local scanner adapter behind explicit `--enable-local-scanner` feature gating and scanner allowlisting.
- Normalized scanner output into preliminary finding records without raw source excerpts.
- Added `bountyclaw scan repo` CLI command.
- Tested fixture outputs, scope-gate denial, feature-gate denial, read-only behavior, deterministic output, and controlled subprocess policy.

Completion criteria completed:

- `bountyclaw scan repo` requires a valid scope manifest.
- Scanner execution requires both `repo.read` and `scan.local_static` authorization.
- Scanner execution requires explicit `--enable-local-scanner` acknowledgement.
- Built-in Python static scanner emits deterministic preliminary findings.
- Scanner output records no network, LLM, MCP, browser, active validation, or report-submission use.
- Local pytest validation passes with 48 tests.
- Phase 3 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 8. Phase 4: Findings Normalization and Evidence Store

Status: Completed.

Subroadmap completed:

- `PHASE_4_SUBROADMAP.md`

Objectives completed:

- Defined canonical finding and redacted evidence schemas.
- Added deterministic canonical finding IDs and deduplication rules.
- Added a local SQLite evidence store for scan runs, canonical findings, and redacted evidence records.
- Added a deterministic secret redaction path before persistence.
- Added `bountyclaw findings collect` and `bountyclaw findings list` CLI commands.
- Added scope-gated `findings.write` authorization for persistence.
- Added tests for redaction, deduplication, no-raw-secret persistence, store-path safety, CLI collection/listing, and Phase 3 JSON rollback fallback.

Completion criteria completed:

- Preliminary scanner findings are converted into canonical records.
- Duplicate preliminary findings are collapsed under stable canonical finding IDs.
- Evidence text is redacted before SQLite persistence.
- Store paths inside the target repository are rejected.
- Canonical findings remain human-triage-only and are not report submissions.
- Local pytest validation passes with 56 tests.
- Phase 4 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 9. Phase 5: LLM Model Router and Prompt-Safety Layer

Status: Completed.

Subroadmap completed:

- `PHASE_5_SUBROADMAP.md`

Objectives completed:

- Added provider-neutral model provider catalog and routing decision models.
- Added fail-closed routing policy that executes only the deterministic `mock.local` provider in Phase 5.
- Added provider metadata for mock, OpenAI, Anthropic, Google, Mistral, Cohere, Groq, and Ollama/local-style providers without enabling live calls.
- Added prompt-safety envelopes with trusted policy sections and explicitly delimited untrusted content.
- Added defense-in-depth redaction before model payload construction.
- Added prompt-injection signal detection for common instruction override, prompt extraction, role impersonation, tool/network instruction, and jailbreak patterns.
- Added scope-gated `model.triage` mocked triage over redacted stored findings.
- Added `bountyclaw model providers`, `bountyclaw model route`, and `bountyclaw model triage` CLI commands.
- Added tests for mocked routing, live-provider denial, no-secret payload construction, prompt-injection isolation, scope enforcement, feature gating, CLI JSON output, and mocked triage behavior.

Completion criteria completed:

- Live provider calls remain disabled and fail closed.
- Mock provider routing succeeds deterministically.
- Prompt payloads are redacted and untrusted content is isolated.
- `model.triage` requires explicit scope action and `--enable-mock-model`.
- Local pytest validation passes with 66 tests.
- Phase 5 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 10. Phase 6: Triage and Report Drafting Workflow

Status: Completed.

Subroadmap completed:

- `PHASE_6_SUBROADMAP.md`

Objectives completed:

- Added human triage review state for canonical findings.
- Added `triage.review` scope action and preserved `report.draft` authorization.
- Added report draft models, report draft result models, and local SQLite report persistence.
- Added deterministic markdown report draft generation from redacted evidence and human triage rationale.
- Added optional inclusion of Phase 5 mocked model triage output as advisory context.
- Added `bountyclaw report review`, `bountyclaw report draft`, and `bountyclaw report list` CLI commands.
- Added tests proving report drafts require approved human review, remain non-submitting, avoid active-validation claims, and preserve local-only safety boundaries.

Completion criteria completed:

- Report drafting requires `report.draft` scope authorization.
- Human triage review requires `triage.review` scope authorization.
- Draft generation requires `review_status=approved_for_draft`.
- Drafts record `submission_allowed=false`, `active_validation_used=false`, and `validation_status=not_validated_static_only`.
- Local pytest validation passes with 72 tests.
- Phase 6 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 11. Phase 7: MCP and Headless Browser Integration

Status: Completed.

Subroadmap completed:

- `PHASE_7_SUBROADMAP.md`

Objectives completed:

- Added local policy summary models and redaction-first policy reader.
- Added fixture-only MCP server registry metadata.
- Added MCP tool allowlisting with unregistered tool denial.
- Added in-process fixture MCP policy summary tool.
- Added browser workflow plan with live browser and network disabled.
- Added fixture-only browser policy ingestion from local files.
- Added scope actions `mcp.tool.invoke` and `browser.policy_ingest`.
- Added CLI commands: `mcp servers`, `mcp tools`, `mcp invoke`, `browser plan`, and `browser policy-ingest`.
- Added tests for feature gates, scope gates, unregistered tool denial, prohibited MCP/browser actions, redaction, no-network behavior, no live browser/server use, and no report submission.

Validation completed:

- Local pytest validation passes with 82 tests.
- Compile validation passed.
- CLI smoke checks for MCP/browser commands passed.

Deferred:

- Real MCP server protocol/runtime validation remains deferred.
- Real Playwright/headless browser validation remains deferred.
- Live policy-page fetching remains disabled and deferred.
- Policy parsing quality against real bounty programs remains deferred.
- Phase 7 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 12. Phase 8: Memory, Skills, and Workflow Learning

Status: Completed.

Subroadmap completed:

- `PHASE_8_SUBROADMAP.md`

Objectives completed:

- Added local SQLite memory store.
- Added explicit human approval for memory writes and deletes.
- Added redaction-first memory persistence and default rejection for secret-like/raw-evidence content.
- Added memory list/export/delete workflows.
- Added reusable non-executing skill templates.
- Added skill proposals that evaluate required scope actions without executing tools.
- Added tests for memory approval, scope gating, secret rejection, export/delete, store-path safety, non-executing skills, and CLI smoke behavior.

Completion criteria completed:

- `bountyclaw memory remember` requires `memory.write`, explicit `--approve-memory-write`, and redacted content checks.
- `bountyclaw memory list`, `memory export`, and `memory delete` are scope-gated.
- `bountyclaw skills list` exposes non-executing templates.
- `bountyclaw skills propose` requires `skill.propose` and does not execute underlying workflow actions.
- Local pytest validation passes with 91 tests.
- Phase 8 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

## 13. Phase 9: CI/CD, Packaging, and Release Controls

Status: Completed.

Subroadmap completed:

- `PHASE_9_SUBROADMAP.md`

Objectives completed:

- Added local release-control models and service functions.
- Added `bountyclaw release checklist`, `bountyclaw release verify`, and `bountyclaw release rollback-plan` CLI commands.
- Added deterministic local release-control verification script: `scripts/phase9_verify.py`.
- Added GitHub Actions workflow definition for test, compile, lint, type, security, dependency, and package smoke gates.
- Added Dependabot configuration for future dependency/action update monitoring.
- Added release, rollback, and security-validation documentation.
- Added future dev-gate dependencies and tool configuration in `pyproject.toml`.
- Added tests for release checks, deferred external gates, rollback plan, workflow content, and CLI JSON output.

Completion criteria completed inside ChatGPT Project Mode:

- Release controls are locally represented and testable.
- Workflow definitions are present and least-privilege by default.
- External CI execution is explicitly marked unexecuted.
- Clean package installation and artifact publishing are explicitly marked deferred.
- Local pytest, compileall, CLI smoke checks, phase verification, and ZIP extraction validation pass.
- Phase 9 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Hosted GitHub Actions execution.
- Clean wheel/sdist install validation.
- Ruff/mypy/bandit/pip-audit execution where tools are unavailable.
- Package signing/provenance.
- Package registry publishing dry run.
- Branch protection or repository ruleset enforcement.

## 14. Phase 10: Production Hardening and External Validation

Status: Completed in ChatGPT Project Mode.

Subroadmap completed:

- `PHASE_10_SUBROADMAP.md`

Objectives completed inside ChatGPT Project Mode:

- Added local Phase 10 hardening models and service functions.
- Added `bountyclaw hardening checklist`, `bountyclaw hardening verify`, `bountyclaw hardening redaction-corpus`, `bountyclaw hardening prompt-corpus`, and `bountyclaw hardening external-plan` CLI commands.
- Added deterministic local redaction fixture corpus.
- Added deterministic local prompt-safety fixture corpus.
- Added explicit external-validation plan for hosted CI, clean install, security tools, external scanners, sandbox/egress, live providers, real MCP/browser runtimes, report quality, performance, retention, backup/restore, rollback drills, and release governance.
- Added deterministic `scripts/phase10_verify.py`.
- Added Phase 10 verifier step to CI workflow definition.
- Updated security-validation documentation and governance files.
- Added tests for hardening services, corpus behavior, external deferrals, CLI JSON output, and CI workflow content.

Completion criteria completed inside ChatGPT Project Mode:

- Local hardening verification reports commit-ready with deferred external production tasks.
- Redaction and prompt-safety deterministic corpora pass.
- Release verification remains commit-ready.
- Local pytest, compileall, CLI smoke checks, phase verification, and ZIP extraction validation pass.
- Phase 10 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Hosted CI execution.
- Clean wheel/sdist build and install validation in a fresh environment.
- Ruff/mypy/bandit/pip-audit execution where tools are unavailable.
- External scanner binary validation.
- OS/container sandbox and network-egress validation.
- Live model provider validation.
- Real MCP/browser runtime validation.
- Real bounty-program report quality validation.
- Performance/load validation.
- Evidence/report/memory backup, restore, retention, export/delete, and rollback drills.
- Artifact signing/provenance and package publishing validation.
- Branch protection and repository-host release governance.

## 15. Phase 11: External Validation Handoff Package

Status: Completed in ChatGPT Project Mode.

Subroadmap completed:

- `PHASE_11_SUBROADMAP.md`

Objectives completed inside ChatGPT Project Mode:

- Added local Phase 11 handoff models and service functions.
- Added `bountyclaw handoff plan`, `bountyclaw handoff evidence-template`, `bountyclaw handoff export`, and `bountyclaw handoff verify` CLI commands.
- Added deterministic Codex/local/CI/human external-validation task plan.
- Added deterministic evidence artifact template for future gap closure.
- Added deterministic local handoff package export.
- Added `scripts/phase11_verify.py`.
- Added Phase 11 verifier step to CI workflow definition.
- Updated release, rollback, security-validation, architecture, agent, roadmap, README, and production gap tracker documents.
- Added tests for handoff plan coverage, evidence templates, exports, verification, CLI JSON output, and CI workflow content.

Completion criteria completed inside ChatGPT Project Mode:

- Local handoff verification reports commit-ready and Codex-ready.
- Handoff plan covers hosted CI, clean install, static/security tools, external scanner/sandbox, live provider safety, MCP/browser runtime, human report quality, operations drills, and release governance tasks.
- Evidence template enumerates future artifacts and sensitive-handling rules.
- Local pytest, compileall, CLI smoke checks, phase verification, and ZIP extraction validation pass.
- Phase 11 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Execution of all handoff tasks in real Codex/local/CI/human environments.
- Production evidence artifact generation.
- Closure of external validation gaps.
- Readiness increase beyond local handoff readiness.

## 16. Phase 12: Validation Evidence Ledger and Gap-Closure Readiness

Status: Completed in ChatGPT Project Mode.

Subroadmap completed:

- `PHASE_12_SUBROADMAP.md`

Objectives completed:

- Unzipped and reviewed every Markdown file from the Phase 11 source bundle before coding.
- Added a local `validation_evidence` subsystem.
- Added hash-only inventory of expected Phase 11 evidence artifacts.
- Added mapping from evidence artifacts to production-gap IDs.
- Added gap-closure readiness reporting that never closes gaps automatically.
- Added validation evidence ledger export.
- Added `bountyclaw validation-evidence ledger`, `gap-readiness`, `export-ledger`, and `verify` CLI commands.
- Added `scripts/phase12_verify.py` and CI workflow hook definition.
- Updated Phase 11 handoff output with evidence-ledger commands.
- Added tests proving no raw evidence content is included and production readiness remains false.

Completion criteria completed:

- Validation evidence ledger builds from the Phase 11 evidence template.
- Present artifacts are SHA-256 hashed without content inspection or raw-content output.
- Gap readiness maps expected artifacts to production gaps.
- No gap is marked closeable by Phase 12 tooling alone.
- Local pytest, compileall, CLI smoke checks, Phase 9/10/11 verifier regressions, and ZIP extraction validation pass.
- Phase 12 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Real external artifacts are not produced inside ChatGPT Project Mode.
- Human evidence review is not performed.
- Production gaps are not closed.
- Hosted CI, clean install, static/security tools, scanner sandbox, live providers, real MCP/browser, performance, backup/restore, signing/provenance, publishing, branch protection, report quality, and manual submission validations remain deferred.

## 17. Phase 13: Evidence Review Workflow and Gap-Closure Governance

Status: Completed in ChatGPT Project Mode.

Subroadmap completed:

- `PHASE_13_SUBROADMAP.md`

Objectives completed:

- Unzipped and reviewed every Markdown file from the Phase 12 source bundle before coding.
- Added local `evidence_review` subsystem.
- Added metadata-only human review decision templates.
- Added hash-bound review status checks against the Phase 12 evidence ledger.
- Added gap-closure proposal generation that never edits governance files and never auto-closes gaps.
- Added evidence-review package export.
- Added `bountyclaw evidence-review template`, `status`, `closure-proposals`, `export-package`, and `verify` CLI commands.
- Added `scripts/phase13_verify.py` and CI workflow hook definition.
- Updated Phase 11 handoff output with evidence-review commands.
- Added tests proving no raw evidence contents are included, hash mismatches block proposals, and production readiness remains false.

Completion criteria completed:

- Evidence review template covers every Phase 12 ledger artifact.
- Review status accepts only metadata records with matching artifact hashes, reviewer identity, timestamp, and rationale.
- Gap closure proposals are generated only for human governance updates and do not close gaps.
- Local pytest, compileall, CLI smoke checks, Phase 9/10/11/12 verifier regressions, and ZIP extraction validation pass.
- Phase 13 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Real external artifacts are still not produced inside ChatGPT Project Mode.
- Human evidence review decisions are still not produced inside ChatGPT Project Mode.
- Production gaps are not closed.
- Production readiness is not raised based on review metadata or proposal output.
- Hosted CI, clean install, static/security tools, scanner sandbox, live providers, real MCP/browser, performance, backup/restore, signing/provenance, publishing, branch protection, report quality, and manual submission validations remain deferred.


## 18. Phase 14: Gap Tracker Governance and Codex Backlog Export

Status: Completed in ChatGPT Project Mode.

Subroadmap completed:

- `PHASE_14_SUBROADMAP.md`

Objectives completed:

- Unzipped and reviewed every Markdown file from the Phase 13 source bundle before coding.
- Added local `gap_tracker` subsystem.
- Added metadata-only parsing of `PRODUCTION_GAP_TRACKER.md` entries.
- Added required-field, duplicate-ID, malformed-entry, and readiness checks.
- Added deterministic Codex/local/CI/human backlog generation from unresolved gaps.
- Added gap tracker governance package export.
- Added `bountyclaw gap-tracker audit`, `backlog`, `export`, and `verify` CLI commands.
- Added `scripts/phase14_verify.py` and CI workflow hook definition.
- Updated Phase 11 handoff output with gap tracker commands.
- Added tests proving no raw evidence contents are included, gap entries are not auto-closed, and production readiness remains false.

Completion criteria completed:

- Gap tracker audit parses unresolved `PGT-*` entries and validates all mandatory fields.
- Codex backlog covers every unresolved production gap entry.
- Gap tracker export writes deterministic JSON and Markdown artifacts.
- Local pytest, compileall, CLI smoke checks, Phase 9/10/11/12/13 verifier regressions, and ZIP extraction validation pass.
- Phase 14 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Real external validation artifacts are still not produced inside ChatGPT Project Mode.
- Human evidence review decisions are still not produced inside ChatGPT Project Mode.
- Production gaps are not closed.
- Production readiness is not raised based on audit or backlog output.
- Hosted CI, clean install, static/security tools, scanner sandbox, live providers, real MCP/browser, performance, backup/restore, signing/provenance, publishing, branch protection, report quality, and manual submission validations remain deferred.


## 19. Phase 15: External Validation Runbook and Execution Journal

Status: Completed in ChatGPT Project Mode.

Subroadmap completed:

- `PHASE_15_SUBROADMAP.md`

Objectives completed:

- Unzipped and reviewed every Markdown file from the Phase 14 source bundle before coding.
- Added a local `validation_runbook` subsystem.
- Added a deterministic external validation runbook derived from unresolved production gaps and Phase 14 Codex backlog items.
- Added a metadata-only future execution journal template.
- Added journal-status assessment based on run IDs, task IDs, gap IDs, artifact IDs, and SHA-256 hashes only.
- Added runbook package export.
- Added `bountyclaw validation-runbook build`, `journal-template`, `journal-status`, `export`, and `verify` CLI commands.
- Added `scripts/phase15_verify.py` and CI workflow hook definition.
- Updated Phase 11 handoff output with validation-runbook commands.
- Added tests proving the runbook/journal workflow is metadata-only, non-executing, non-closing, and production-not-ready.

Completion criteria completed:

- Runbook covers unresolved gap backlog items.
- Journal template is metadata-only and forbids raw evidence content, automatic gap closure, and production-readiness changes.
- Journal status never closes gaps or marks production ready.
- Local pytest, compileall, CLI smoke checks, Phase 9/10/11/12/13/14 verifier regressions, and ZIP extraction validation pass.
- Phase 15 unresolved production gaps are recorded in `PRODUCTION_GAP_TRACKER.md`.

Deferred:

- Real runbook execution is still not performed inside ChatGPT Project Mode.
- Execution journal metadata is not produced by real external executors inside ChatGPT Project Mode.
- Evidence artifacts are not produced, reviewed, or accepted inside ChatGPT Project Mode.
- Production gaps are not closed.
- Production readiness is not raised based on runbook or journal metadata.
- Hosted CI, clean install, static/security tools, scanner sandbox, live providers, real MCP/browser, performance, backup/restore, signing/provenance, publishing, branch protection, report quality, and manual submission validations remain deferred.

## 20. Post-Phase 15 External Production Completion Path

The next safest task is external production validation and evidence review in Codex/local/CI/human environments:

1. Reread all governance files and preserve Phase 10 local hardening behavior as the rollback fallback.
2. Execute hosted CI, clean package build/install, and static/security gates in a real repository or local/CI environment.
3. Validate external scanners, sandbox/egress controls, real MCP/browser runtimes, live/local model providers, broader redaction corpora, adversarial prompt/model safety, report quality, performance, retention, backup/restore, and rollback drills as applicable.
4. Configure branch protection, signing/provenance, and publishing controls only after human release approval.
5. Do not claim production deployment, package publishing, live provider readiness, external scanner readiness, signing/provenance, or enterprise readiness unless actually validated.
6. Store validation artifacts under `validation_evidence/`, run Phase 12 validation-evidence ledger commands, create human-reviewed `evidence_review_decisions.json`, run Phase 13 evidence-review commands, run Phase 14 gap-tracker audit/backlog commands, then update governance files manually before closing any gap.
7. Update `ROADMAP.md`, `PRODUCTION_GAP_TRACKER.md`, `SECURITY_VALIDATION.md`, `RELEASE.md`, `ROLLBACK.md`, and release evidence with exact validation results.

## 20. Anti-Drift Controls

- Do not implement or expand scanners without scope-gate integration, explicit feature gating, allowlisted adapters, and tests.
- Do not enable live LLM calls before live-provider validation, no-secret payload validation, provider credential controls, and model-output safety evaluation are complete.
- Do not implement browser or MCP tools before tool allowlisting exists.
- Do not implement autonomous external actions in MVP.
- Do not claim production readiness from mocked tests, hash-only ledgers, unreviewed evidence artifacts, or evidence-review proposal metadata.
- Do not add cloud deployment unless a later roadmap update explicitly approves it.


## 20. Phase 16: Validation Baseline Manifest and Source Snapshot Binding

Status: Completed inside ChatGPT Project Mode.

Implemented:

- `PHASE_16_SUBROADMAP.md`.
- `MARKDOWN_REVIEW_PHASE16.md`.
- `src/bountyclaw/validation_baseline/`.
- `scripts/phase16_verify.py`.
- `tests/test_validation_baseline_phase16.py`.
- `bountyclaw validation-baseline manifest`.
- `bountyclaw validation-baseline export`.
- `bountyclaw validation-baseline verify`.
- Handoff package update with validation-baseline commands.
- CI workflow hook for Phase 16 verification.

Validation status:

- Local tests and CLI smoke checks executed in ChatGPT Project Mode.
- External validation remains deferred.

Boundaries preserved:

- Hash-only baseline metadata.
- No raw evidence inspection.
- No raw source export.
- No hosted CI execution.
- No clean package install claim.
- No gap closure or production readiness increase based on baseline metadata alone.

## 21. Post-Phase 16 External Production Completion

Remaining work must be performed outside ChatGPT Project Mode by Codex/local/CI/human executors. Future evidence artifacts should reference the Phase 16 baseline ID, then proceed through the Phase 12 validation-evidence ledger, Phase 13 evidence-review workflow, Phase 14 gap tracker backlog, and Phase 15 runbook/journal governance before any production gap is manually closed.


## 22. Phase 17: Closure Gate and Readiness Attestation Governance

Status: Completed inside ChatGPT Project Mode.

Implemented:

- `PHASE_17_SUBROADMAP.md`.
- `MARKDOWN_REVIEW_PHASE17.md`.
- `src/bountyclaw/closure_gate/`.
- `scripts/phase17_verify.py`.
- `tests/test_closure_gate_phase17.py`.
- `bountyclaw closure-gate attestation-template`.
- `bountyclaw closure-gate status`.
- `bountyclaw closure-gate export`.
- `bountyclaw closure-gate verify`.
- Handoff package update with closure-gate commands.
- CI workflow hook for Phase 17 verification.

Validation status:

- Local tests, compile checks, CLI smoke checks, and verifier regressions executed in ChatGPT Project Mode.
- External validation remains deferred.

Boundaries preserved:

- Metadata-only attestations.
- No raw evidence inspection.
- No raw source export.
- No external validation execution.
- No hosted CI execution.
- No gap closure or production readiness increase based on attestation metadata alone.



## 23. Phase 18: Readiness Dashboard and External Executor Index

Status: Completed inside ChatGPT Project Mode.

Implemented:

- `PHASE_18_SUBROADMAP.md`.
- `MARKDOWN_REVIEW_PHASE18.md`.
- `src/bountyclaw/readiness_dashboard/`.
- `scripts/phase18_verify.py`.
- `tests/test_readiness_dashboard_phase18.py`.
- `bountyclaw readiness-dashboard build`.
- `bountyclaw readiness-dashboard handoff-index`.
- `bountyclaw readiness-dashboard export`.
- `bountyclaw readiness-dashboard verify`.
- Handoff package update with readiness-dashboard commands.
- CI workflow hook for Phase 18 verification.

Validation status:

- Local tests, compile checks, CLI smoke checks, regression verifiers, gap tracker audit, and ZIP validation executed in ChatGPT Project Mode.
- External validation remains deferred.

Boundaries preserved:

- Metadata-only dashboard.
- No raw evidence inspection.
- No raw source export by the dashboard.
- No hosted CI execution claim.
- No clean package install claim.
- No external scanner execution.
- No live model provider use.
- No real MCP/browser runtime use.
- No active validation.
- No package publishing, signing/provenance, branch protection configuration, or bounty submission.
- No production gap closure or production readiness increase based on dashboard output alone.

Rollback:

- Remove the Phase 18 dashboard subsystem, script, tests, CLI additions, handoff command addition, CI hook, and governance updates.
- Return to the Phase 17 closure-gate baseline.

## 24. Phase 19: Local Quality/Security Gate Execution and Remediation

Status: Completed inside ChatGPT Project Mode.

Phase 19 converted previously defined quality/security gates into locally executed checks and remediated source issues discovered by ruff, mypy, and Bandit.

Deliverables:

- `PHASE_19_SUBROADMAP.md`.
- `MARKDOWN_REVIEW_PHASE19.md`.
- `QUALITY_GATES_PHASE19.md`.
- `src/bountyclaw/quality_gates/`.
- `scripts/phase19_verify.py`.
- `tests/test_quality_gates_phase19.py`.
- CI workflow hook for ruff format and Phase 19 verification.
- Handoff update with `QUALITY_GATES_COMMANDS.md`.

Validation completed locally:

- tests;
- compileall;
- ruff format check;
- ruff lint;
- mypy;
- Bandit;
- wheel/sdist build;
- clean wheel install and installed CLI smoke.

Environment-limited validation:

- `pip-audit --progress-spinner off` was executed locally in an isolated environment; no third-party vulnerabilities were reported. `bountyclaw` itself remains a local editable install and is currently not auditable by PyPI package metadata alone. Hostile advisory coverage and package-distribution-level dependency audit closure remain tracked as external completion gaps.

Rollback:

- Revert Phase 19 docs, quality-gates subsystem, script, tests, CI hook, handoff command addition, version metadata, and source remediation changes. Phase 18 readiness-dashboard tooling remains rollback-safe.

## 25. Post-Phase 19 External Production Completion

Remaining work must be performed outside ChatGPT Project Mode by Codex/local/CI/human executors. Future evidence artifacts should reference the Phase 16/17 baseline ID, then proceed through the Phase 12 validation-evidence ledger, Phase 13 evidence-review workflow, Phase 14 gap tracker backlog, Phase 15 runbook/journal governance, Phase 17 closure gate, Phase 18 readiness dashboard/index, and Phase 19 quality-gate evidence workflow before any production gap is manually closed.
