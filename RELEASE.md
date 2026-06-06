# BountyClaw Release Controls

Phase 15 defines local external-validation runbook controls that are safe to create in ChatGPT Project Mode and clear about what remains unexecuted in external environments.

## Release Gate Order

1. Reconcile governance files: `ARCHITECTURE.md`, `ROADMAP.md`, active phase subroadmap, `AGENTS.md`, and `PRODUCTION_GAP_TRACKER.md`.
2. Run deterministic local validation:
   - `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q`
   - `PYTHONPATH=src python -m compileall -q src tests scripts`
   - `PYTHONPATH=src python -m bountyclaw release verify --root . --json`
   - `PYTHONPATH=src python -m bountyclaw hardening verify --root . --json`
   - `PYTHONPATH=src python -m bountyclaw handoff verify --root . --json`
   - `PYTHONPATH=src python -m bountyclaw validation-evidence verify --root . --json`
   - `PYTHONPATH=src python -m bountyclaw evidence-review verify --root . --json`
   - `PYTHONPATH=src python -m bountyclaw gap-tracker verify --root . --json`
   - `PYTHONPATH=src python -m bountyclaw validation-runbook verify --root . --json`
   - `PYTHONPATH=src python scripts/phase9_verify.py --root . --json`
   - `PYTHONPATH=src python scripts/phase10_verify.py --root . --json`
   - `PYTHONPATH=src python scripts/phase11_verify.py --root . --json`
   - `PYTHONPATH=src python scripts/phase12_verify.py --root . --json`
   - `PYTHONPATH=src python scripts/phase13_verify.py --root . --json`
   - `PYTHONPATH=src python scripts/phase14_verify.py --root . --json`
   - `PYTHONPATH=src python scripts/phase15_verify.py --root . --json`
3. Run deterministic local safety corpora:
   - `PYTHONPATH=src python -m bountyclaw hardening redaction-corpus --json`
   - `PYTHONPATH=src python -m bountyclaw hardening prompt-corpus --json`
4. Export external completion governance artifacts:
   - `PYTHONPATH=src python -m bountyclaw handoff export --root . --output validation_handoff --json`
   - `PYTHONPATH=src python -m bountyclaw gap-tracker export --root . --output gap_tracker_package --json`
   - `PYTHONPATH=src python -m bountyclaw validation-runbook export --root . --output validation_runbook --json`
5. Execute Phase 15 runbook steps only in real Codex/local/CI/human environments. Record metadata-only journal entries under `validation_runs/execution_journal.json`; do not include raw evidence contents.
6. Store produced artifacts in private approved evidence storage, mirror reviewed/redacted copies under `validation_evidence/`, run Phase 12 ledger commands, run Phase 13 review commands, run Phase 14 gap-tracker commands, and update `PRODUCTION_GAP_TRACKER.md` only with human-reviewed evidence.
7. Run static quality/security gates in a real local/Codex/CI environment with dev dependencies installed:
   - `ruff check src tests scripts`
   - `mypy src`
   - `bandit -q -r src`
   - `pip-audit --progress-spinner off`
8. Build package artifacts in an isolated environment:
   - `python -m build`
   - install the generated wheel into a fresh virtual environment
   - run `bountyclaw doctor` without `PYTHONPATH`
9. Execute the GitHub Actions workflow on a real repository runner.
10. Preserve all unresolved execution, evidence, review, runbook, and closure gaps in `PRODUCTION_GAP_TRACKER.md` until a real environment validates them with evidence and a human release/AppSec reviewer approves closure.

## Release Prohibitions

Phase 15 does not permit package publishing, cloud deployment, live model provider calls, live MCP servers, live browser automation, active validation, exploit execution, platform submission, bounty report submission, raw evidence inspection by tooling, production-gap closure from journal/review metadata, gap-tracker backlog output, or production-readiness increases from runbook/journal/proposal/backlog output.

## Human Approval Required

A human release owner must approve any future artifact publication, version promotion, package registry operation, signing/provenance operation, branch protection enforcement, deployment-like step, live provider enablement, real MCP/browser runtime enablement, evidence artifact acceptance, execution journal acceptance, production-gap closure, readiness recalculation, or report submission. Automated publication and automated bounty submission remain out of scope.


## Phase 16 Release Update

Before any future external validation or release-readiness claim, export the validation baseline and record the baseline ID in execution journal, validation evidence, evidence review, and gap tracker metadata. Phase 16 baseline artifacts are hash-only and must not contain raw source excerpts, raw evidence contents, secrets, exploit payloads, screenshots, or private logs.

Additional local gate:

```bash
PYTHONPATH=src python scripts/phase16_verify.py --root . --json
```

This gate is commit-ready only. Hosted CI, clean install, static/security gates, package signing/provenance, publishing, and branch protection remain deferred until executed in the proper environment.


## Phase 17 Release Update

Phase 17 adds closure-gate and readiness-attestation governance. Release candidates remain blocked from production until external validation evidence is produced, bound to the baseline, reviewed by human AppSec/release owners, processed through the Phase 12/13/14/15/17 governance workflow, and manually reflected in `PRODUCTION_GAP_TRACKER.md`. Closure-gate candidate metadata alone is not release approval.


## Phase 18 Release Update

Phase 18 introduces readiness dashboard release controls. Before any external release candidate can be considered, future executors must run:

```bash
PYTHONPATH=src python -m bountyclaw readiness-dashboard verify --root . --json
PYTHONPATH=src python scripts/phase18_verify.py --root . --json
```

The Phase 18 dashboard is a local metadata consolidation layer only. Release approval still requires hosted CI proof, clean package build/install validation, static/security gate evidence, external scanner and sandbox validation, live-provider safety validation where enabled, real MCP/browser validation where enabled, human evidence review, readiness attestation, closure-gate review, signing/provenance, and branch protection evidence.


## Phase 19 Release Gate Update

Phase 19 executed and remediated local release-adjacent quality/security gates: tests, compileall, ruff format, ruff lint, mypy, Bandit, package build, clean wheel install, and installed CLI smoke checks. `pip-audit` was attempted but remains blocked by DNS/name-resolution failure to `pypi.org` in this environment.

Release remains blocked until hosted CI executes these gates, `pip-audit` completes with approved advisory access, branch protection requires the checks, and Phase 12-17 evidence/review/closure governance accepts reviewed artifacts.
