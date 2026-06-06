# Phase 3 Subroadmap: Static Scanner Adapter MVP

## 1. Phase Status

Status: Completed.

Phase 3 created the first scope-gated local static scanner execution path for BountyClaw. The implementation remains local-only, read-only against inspected repositories, feature-gated, and bounded to authorized local repositories.

## 2. Objectives

1. Create a scanner adapter subsystem with stable interfaces.
2. Add a controlled subprocess wrapper for future external scanner adapters.
3. Register the first safe local scanner adapter behind an explicit feature gate and scanner allowlist.
4. Normalize scanner output into preliminary finding records without persisting raw source excerpts.
5. Add CLI support for scope-gated local static scanning.
6. Add tests proving scanner execution cannot bypass scope authorization or feature-gate requirements.
7. Preserve Phase 2 repository planning as the rollback fallback.
8. Update roadmap, active subroadmap, and production gap tracker at phase completion.

## 3. Deliverables

Completed deliverables:

- `src/bountyclaw/scanning/` scanner subsystem.
- Scanner adapter protocol and context models.
- Preliminary finding and scanner-run result models.
- Built-in deterministic Python static scanner adapter.
- Controlled subprocess runner and command policy for future external scanners.
- Scanner registry with explicit allowlisted adapter IDs.
- Scope-gated scanner service.
- CLI command: `bountyclaw scan repo`.
- Explicit CLI feature gate: `--enable-local-scanner`.
- JSON and table output for scanner results.
- Audit logging for scanner allow/deny outcomes.
- Phase 3 tests for scanner behavior, CLI behavior, authorization, feature gating, read-only operation, and subprocess policy.

## 4. Subsystem Boundaries

### In Scope

- Local static scanner adapter interfaces.
- Local built-in Python AST/static pattern scanner.
- Preliminary finding normalization.
- Controlled subprocess policy abstraction.
- Scope-gated scanner service.
- CLI wiring for local static scanner execution.
- Tests using fixture repositories and local subprocess-wrapper checks.

### Out of Scope

- Network scanning.
- Active exploitation.
- Destructive validation.
- Credential harvesting or secret exfiltration.
- Browser automation.
- MCP tools.
- LLM provider calls.
- Automated report submission.
- Persistent evidence database.
- Raw source excerpt persistence.
- External scanner binary installation or live validation.
- Container sandbox validation.
- Production CI/CD validation.

## 5. Dependencies

Satisfied prerequisites:

- Phase 0 governance files exist.
- Phase 1 CLI and scope gate exist.
- Phase 2 repository intake and scan planning exist.
- `scan.local_static` authorization action exists.
- Local test suite exists.

Deferred dependencies:

- Phase 4 evidence store and canonical findings engine.
- Secret-redaction engine.
- External scanner binaries.
- Container or OS sandboxing.
- CI/CD pipeline.
- Real bug bounty program fixtures and authorized repositories.

## 6. Implementation Sequence

Completed sequence:

1. Reconciled Phase 2 source bundle as the current source of truth.
2. Validated Phase 2 baseline tests before patching.
3. Created scanner subsystem package.
4. Added scanner models and adapter protocol.
5. Implemented deterministic built-in Python static scanner.
6. Implemented controlled subprocess runner with command/cwd/timeout/network-argument policy checks.
7. Added scanner registry and allowlisted default adapter.
8. Added scope-gated scanner service requiring both `repo.read` and `scan.local_static`.
9. Added explicit local scanner feature gate.
10. Added `scan repo` CLI command.
11. Added scanner tests and subprocess policy tests.
12. Updated governance documents and gap tracker.
13. Re-ran validation.

## 7. Validation Sequence

Completed validation:

- Phase 2 baseline pytest before patching: passed.
- Full pytest after Phase 3 implementation: passed.
- Python compile validation: passed.
- CLI help smoke validation: passed.
- CLI doctor smoke validation: passed.
- CLI `scan repo --help` smoke validation: passed.
- Authorized fixture scan with JSON output: passed.

Validated behaviors:

- Scanner service requires explicit feature gate.
- Scanner service requires `repo.read` scope approval.
- Scanner service requires `scan.local_static` scope approval.
- Unknown scanner IDs are denied.
- Built-in Python scanner produces deterministic preliminary findings.
- Built-in Python scanner omits raw source excerpts.
- Scanner run result records no network, LLM, MCP, browser, active validation, or report submission use.
- Scanner execution does not write inside target repositories.
- Controlled subprocess wrapper denies network-oriented arguments.
- Controlled subprocess wrapper denies unallowlisted executables.
- Controlled subprocess wrapper denies working directories outside the allowed repository boundary.

## 8. Rollback Strategy

Rollback to Phase 2 requires:

1. Remove `PHASE_3_SUBROADMAP.md`.
2. Remove `src/bountyclaw/scanning/`.
3. Revert `scan_app` CLI additions in `src/bountyclaw/cli.py`.
4. Revert version changes in `src/bountyclaw/__init__.py` and `pyproject.toml`.
5. Remove `tests/test_scanning_phase3.py`.
6. Revert Phase 3 updates to `ARCHITECTURE.md`, `AGENTS.md`, `ROADMAP.md`, `README.md`, and `PRODUCTION_GAP_TRACKER.md`.
7. Preserve Phase 2 `repo inspect` and `repo plan` as the known-good fallback.

No database, cloud resource, external scanner installation, secret, or external account state was introduced.

## 9. Drift-Prevention Constraints

- Scanner execution must remain local-only.
- Scanner execution must require a valid scope manifest.
- Scanner execution must require explicit `scan.local_static` authorization.
- Scanner execution must require the explicit local scanner feature gate.
- Scanner adapters must be registered through an allowlist.
- Scanner adapters must not use arbitrary shell execution.
- Scanner adapters must not perform network activity.
- Scanner adapters must not write to target repositories.
- Findings must not contain raw source excerpts until redaction and evidence controls exist.
- Scanner output must be treated as untrusted input.
- Phase 3 must not claim real external scanner validation.

## 10. Environment Limitations

The following were not fully executable in ChatGPT Project Mode:

- Real external scanner binary installation validation.
- Real semgrep/bandit/trivy/gitleaks/etc. execution validation.
- Containerized scanner sandbox validation.
- OS-level network egress blocking validation.
- CI/CD execution.
- Multi-platform installation validation.
- Scans against real authorized bounty repositories.
- Independent security review.

## 11. Expected Unresolved Gaps After Phase 3

- No canonical persistent findings store yet.
- No redaction engine yet.
- Preliminary findings are not persisted.
- No evidence database exists.
- No dependency vulnerability scanner exists.
- No secret scanner exists.
- No external scanner binary validation exists.
- No real scanner sandboxing validation exists.
- No model routing or prompt safety exists.
- No report generation exists.
- No CI/CD gates exist.
- No package artifact installation validation exists.

## 12. Expected Future Continuation Tasks

The next phase must create `PHASE_4_SUBROADMAP.md` before implementation.

Expected Phase 4 tasks:

1. Define canonical finding schema beyond preliminary scanner findings.
2. Add deterministic finding deduplication.
3. Add local evidence store and scan-run persistence.
4. Implement secret redaction before persistence.
5. Ensure scanner outputs are treated as untrusted input.
6. Add tests proving raw secrets/source excerpts are not persisted.
7. Update roadmap, Phase 4 subroadmap, and production gap tracker.

## 13. Phase Completion Notes

Phase 3 completed with a local-only static scanner MVP. The scanner path requires a valid scope manifest, `repo.read`, `scan.local_static`, and the explicit `--enable-local-scanner` feature gate. The initial built-in Python scanner performs deterministic AST-based detection of selected risky code patterns and emits normalized preliminary findings without raw source excerpts.

Validation completed:

- `PYTHONPATH=src pytest -q` -> 48 passed.
- `PYTHONPATH=src python -m compileall -q src tests` -> passed.
- `PYTHONPATH=src python -m bountyclaw --help` -> passed.
- `PYTHONPATH=src python -m bountyclaw doctor` -> passed.
- `PYTHONPATH=src python -m bountyclaw scan repo --help` -> passed.
- Authorized fixture `scan repo --enable-local-scanner --json` command -> passed.

Deferred validations remain recorded in `PRODUCTION_GAP_TRACKER.md`.
