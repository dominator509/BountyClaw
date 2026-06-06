# Phase 2 Subroadmap: Local Repository Intake and Deterministic Scan Planning

## 1. Phase Status

Status: Completed.

Production readiness after phase: 14%.

## 2. Objectives

Phase 2 objectives:

- Implement read-only local repository intake.
- Require Phase 1 scope-gate approval before repository metadata is read.
- Detect repository languages and package/configuration manifests deterministically.
- Generate deterministic scan plans without executing scanners.
- Add fixture repositories and tests for scope enforcement, read-only behavior, and deterministic planning.
- Preserve local-only, no-network, no-LLM, no-MCP, no-browser constraints.

## 3. Deliverables

Completed deliverables:

- `src/bountyclaw/repository/__init__.py`
- `src/bountyclaw/repository/models.py`
- `src/bountyclaw/repository/intake.py`
- `src/bountyclaw/repository/planner.py`
- `src/bountyclaw/repository/service.py`
- CLI commands for repository inspection and scan planning.
- Tests for repository intake and scan planning.
- Governance updates to `ROADMAP.md`, `ARCHITECTURE.md`, `AGENTS.md`, and `PRODUCTION_GAP_TRACKER.md`.

Deferred deliverables:

- Scanner adapter execution.
- External scanner installation validation.
- Secret redaction engine.
- Findings normalization.
- Evidence store persistence.
- LLM triage/model routing.
- MCP/browser integrations.
- Network or live target validation.

## 4. Subsystem Boundaries

Phase 2 may touch only:

- CLI Orchestrator for repository intake/plan commands.
- Scope and Policy Gate call sites.
- Repo Intake Agent foundation.
- Deterministic scan-planning data models.
- Tests and governance documents.

Phase 2 must not implement:

- Scanner subprocess execution.
- Network access.
- Browser automation.
- MCP integration.
- LLM provider calls.
- Findings persistence or report generation.
- Active exploitation or live validation.
- Automated bounty submission.

## 5. Dependencies

Required prerequisites:

- Phase 0 governance completed.
- Phase 1 CLI and scope-gate foundation completed.
- `PHASE_2_SUBROADMAP.md` created before implementation.
- A valid scope manifest must authorize the target repository before repository metadata is read.

Runtime/tooling dependencies:

- Python 3.12+.
- Typer and Rich from Phase 1.
- Pydantic from Phase 1.
- pytest for local validation.

## 6. Implementation Sequence

Completed sequence:

1. Reconcile uploaded loose governance files against the completed Phase 1 repo bundle.
2. Create this Phase 2 subroadmap before implementation.
3. Add repository metadata and scan-plan schemas.
4. Add read-only repository walker with deterministic sorting and ignored directory boundaries.
5. Add language and package/configuration manifest detection.
6. Add deterministic scan-plan generator that records future adapter recommendations without executing tools.
7. Add service functions that call the Phase 1 scope gate before repository reads.
8. Add CLI commands for repository inspection and scan planning.
9. Add tests for authorization denial, deterministic planning, read-only behavior, and CLI smoke paths.
10. Run local validation.
11. Update governance files and gap tracker.

## 7. Validation Sequence

Completed validation:

- Run pytest for all Phase 1 and Phase 2 tests.
- Run Python compile check for `src` and `tests`.
- Run CLI help smoke test.
- Run `doctor` command.
- Run repository inspect command against an authorized fixture repository.
- Run repository plan command against an authorized fixture repository.
- Verify denied/out-of-scope repository actions fail closed.
- Verify scan plan generation does not execute scanners.
- Verify repository intake does not create or modify files in the target repository.

## 8. Rollback Strategy

Rollback consists of removing Phase 2 runtime files and reverting governance updates:

- Remove `PHASE_2_SUBROADMAP.md`.
- Remove `src/bountyclaw/repository/`.
- Revert Phase 2 CLI command additions.
- Remove Phase 2 tests.
- Revert updates to `ARCHITECTURE.md`, `AGENTS.md`, `ROADMAP.md`, and `PRODUCTION_GAP_TRACKER.md`.

No database schema, infrastructure, external account, scanner install, model credential, or production runtime state is planned for Phase 2.

## 9. Drift-Prevention Constraints

Phase 2 constraints:

- Do not execute scanners.
- Do not read network targets.
- Do not make network calls.
- Do not call LLM providers.
- Do not connect MCP tools.
- Do not control browsers.
- Do not write into inspected repositories.
- Do not persist raw source contents.
- Do not store secrets or evidence.
- Do not modify authorization scope based on model output.
- Do not continue after failed validation.

## 10. Environment Limitations

Expected limitations:

- Real large-repository performance validation may be environment-limited.
- External scanner validation remains deferred.
- CI/CD execution remains unavailable unless a real repository host is connected.
- Cross-platform file-system validation remains deferred.
- Real bug bounty program validation remains unavailable without human authorization.

## 11. Expected Unresolved Gaps

Expected unresolved gaps after Phase 2:

- No scanner execution yet.
- No controlled subprocess wrapper yet.
- No findings normalization yet.
- No evidence store yet.
- No secret-redaction engine yet.
- No model router or prompt-safety layer yet.
- No report generator yet.
- No MCP/browser integrations yet.
- No CI/CD pipeline yet.
- No production deployment or external validation yet.

## 12. Expected Future Continuation Tasks

The next phase must create `PHASE_3_SUBROADMAP.md` before implementation.

Expected Phase 3 tasks:

1. Define scanner adapter interface and execution wrapper.
2. Register scanner adapters behind feature flags and allowlists.
3. Execute only safe local scanner commands through scope-approved paths.
4. Add mocked scanner output fixtures.
5. Add validation proving scanners cannot bypass scope gate or write outside approved output paths.
6. Update roadmap, active subroadmap, and production gap tracker.


## 13. Phase Completion Notes

Phase 2 completed with read-only local repository fingerprinting and deterministic scan planning. Repository metadata reads require scope-gate approval through `repo.read`, and scan planning requires `scan.local_static` authorization. Scan plans are recommendations only and set `scanners_execute=false`; no scanner, network, LLM, MCP, browser, report submission, or active validation capability was introduced.

Validation completed:

- `PYTHONPATH=src pytest -q` -> 36 passed.
- `PYTHONPATH=src python -m compileall -q src tests` -> passed.
- `PYTHONPATH=src python -m bountyclaw --help` -> passed.
- `PYTHONPATH=src python -m bountyclaw doctor` -> passed.
- Authorized fixture `repo inspect` command -> passed.
- Authorized fixture `repo plan --format json` command -> passed.

The next phase must create `PHASE_3_SUBROADMAP.md` before any scanner adapter implementation begins.
