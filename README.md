# BountyClaw

BountyClaw is a local-first, CLI-first, authorized bug bounty research assistant. It is designed for legitimate, scoped security research over owned or explicitly authorized assets.

Current ChatGPT Project Mode state: **Phase 19 completed locally**.

Phase 19 executes and records local quality/security gates. Tests, compile checks, ruff formatting, ruff lint, mypy, Bandit, package build, clean wheel install, and installed CLI smoke checks passed after remediation. `pip-audit` was installed and attempted but remains deferred because DNS resolution to `pypi.org` failed in this environment. Phase 19 does not claim hosted CI, branch protection, online dependency audit completion, evidence acceptance, gap closure, production deployment, active validation, live provider use, real MCP/browser runtime use, or automated bounty submission.

## Local validation

Run from the repository root:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests scripts
PYTHONPATH=src python -m bountyclaw doctor
PYTHONPATH=src python -m bountyclaw release verify --root . --json
PYTHONPATH=src python -m bountyclaw hardening verify --root . --json
PYTHONPATH=src python -m bountyclaw handoff verify --root . --json
PYTHONPATH=src python -m bountyclaw validation-evidence verify --root . --json
PYTHONPATH=src python -m bountyclaw evidence-review verify --root . --json
PYTHONPATH=src python -m bountyclaw gap-tracker verify --root . --json
PYTHONPATH=src python -m bountyclaw validation-runbook verify --root . --json
PYTHONPATH=src python -m bountyclaw validation-baseline manifest --root . --json
PYTHONPATH=src python -m bountyclaw validation-baseline export --root . --output validation_baseline --json
PYTHONPATH=src python -m bountyclaw validation-baseline verify --root . --json
PYTHONPATH=src python scripts/phase9_verify.py --root . --json
PYTHONPATH=src python scripts/phase10_verify.py --root . --json
PYTHONPATH=src python scripts/phase11_verify.py --root . --json
PYTHONPATH=src python scripts/phase12_verify.py --root . --json
PYTHONPATH=src python scripts/phase13_verify.py --root . --json
PYTHONPATH=src python scripts/phase14_verify.py --root . --json
PYTHONPATH=src python scripts/phase15_verify.py --root . --json
```


Additional Phase 19 quality/security gates:

```bash
ruff format --check src tests scripts
ruff check src tests scripts
PYTHONPATH=src mypy --no-incremental --cache-dir /tmp/bountyclaw-mypy src
PYTHONPATH=src bandit -q -r src
python -m build
PYTHONPATH=src python -m bountyclaw quality-gates checklist --root . --json
PYTHONPATH=src python -m bountyclaw quality-gates verify --root . --json
PYTHONPATH=src python scripts/phase19_verify.py --root . --json
```

`pip-audit --progress-spinner off` must be rerun in hosted CI or a local environment with approved DNS/network or internal advisory mirror access.

## Representative workflow commands

All target-facing operations require a valid scope manifest and local repository allowlist.

```bash
PYTHONPATH=src python -m bountyclaw scope validate --manifest scope.yaml
PYTHONPATH=src python -m bountyclaw repo inspect --manifest scope.yaml --repo /path/to/repo --json
PYTHONPATH=src python -m bountyclaw repo plan --manifest scope.yaml --repo /path/to/repo --json
PYTHONPATH=src python -m bountyclaw scan repo --manifest scope.yaml --repo /path/to/repo --enable-local-scanner --json
PYTHONPATH=src python -m bountyclaw findings collect --manifest scope.yaml --repo /path/to/repo --store state/evidence.sqlite --enable-local-scanner --json
PYTHONPATH=src python -m bountyclaw model triage --manifest scope.yaml --repo /path/to/repo --store state/evidence.sqlite --finding-id <finding-id> --enable-mock-model --json
PYTHONPATH=src python -m bountyclaw report review --manifest scope.yaml --repo /path/to/repo --store state/evidence.sqlite --finding-id <finding-id> --reviewer <name> --rationale "human review rationale" --status approved_for_draft --json
PYTHONPATH=src python -m bountyclaw report draft --manifest scope.yaml --repo /path/to/repo --store state/evidence.sqlite --finding-id <finding-id> --json
```

## External validation handoff, runbook, and evidence review

Future Codex/local/CI/human executors should use the handoff, runbook, evidence ledger, evidence-review workflow, and gap tracker workflow in order:

```bash
PYTHONPATH=src python -m bountyclaw handoff export --root . --output validation_handoff --json
PYTHONPATH=src python -m bountyclaw gap-tracker audit --root . --json
PYTHONPATH=src python -m bountyclaw gap-tracker backlog --root . --json
PYTHONPATH=src python -m bountyclaw gap-tracker export --root . --output gap_tracker_package --json
PYTHONPATH=src python -m bountyclaw validation-runbook build --root . --json
PYTHONPATH=src python -m bountyclaw validation-runbook journal-template --root . --json
PYTHONPATH=src python -m bountyclaw validation-runbook export --root . --output validation_runbook --json
PYTHONPATH=src python -m bountyclaw validation-runbook journal-status --root . --journal validation_runs/execution_journal.json --json
PYTHONPATH=src python -m bountyclaw validation-evidence ledger --root . --evidence-dir validation_evidence --json
PYTHONPATH=src python -m bountyclaw validation-evidence gap-readiness --root . --evidence-dir validation_evidence --json
PYTHONPATH=src python -m bountyclaw validation-evidence export-ledger --root . --evidence-dir validation_evidence --output validation_evidence_ledger --json
PYTHONPATH=src python -m bountyclaw evidence-review template --root . --evidence-dir validation_evidence --json
PYTHONPATH=src python -m bountyclaw evidence-review status --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json
PYTHONPATH=src python -m bountyclaw evidence-review closure-proposals --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json
PYTHONPATH=src python -m bountyclaw evidence-review export-package --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --output validation_evidence_review --json
PYTHONPATH=src python -m bountyclaw gap-tracker verify --root . --json
```

The `validation_runs/execution_journal.json` file must contain metadata only: task IDs, gap IDs, executor metadata, artifact IDs, and artifact SHA-256 hashes. The `evidence_review_decisions.json` file must be created only after a human release/AppSec reviewer privately reviews external validation artifacts. Hashes, journal metadata, review metadata, and backlog output do not close gaps automatically.

## Scope manifest actions

Current non-destructive scope actions include:

- `scope.validate`
- `repo.read`
- `scan.local_static`
- `findings.write`
- `model.triage`
- `triage.review`
- `report.draft`
- `mcp.tool.invoke`
- `browser.policy_ingest`
- `memory.read`
- `memory.write`
- `memory.export`
- `memory.delete`
- `skill.propose`

Release, hardening, handoff, validation-evidence, evidence-review, gap-tracker, and validation-runbook commands are local governance workflows and do not act on bounty targets.

## Safety posture

- Network actions are disabled.
- Live LLM providers are disabled.
- Real MCP/browser runtimes are disabled.
- Active validation and exploit execution are disabled.
- Automated bounty submission is disabled.
- Report drafts are human-review-only and non-submitting.
- Evidence review tooling is metadata-only and cannot close gaps or raise readiness.
- Gap tracker tooling is metadata-only and cannot close gaps or raise readiness.
- Validation runbook tooling is metadata-only and cannot execute external validation, inspect evidence, close gaps, or raise readiness.


## Phase 16 validation baseline

Phase 16 adds hash-only source snapshot binding for future external validation evidence:

```bash
PYTHONPATH=src python -m bountyclaw validation-baseline manifest --root . --json
PYTHONPATH=src python -m bountyclaw validation-baseline export --root . --output validation_baseline --json
PYTHONPATH=src python -m bountyclaw validation-baseline verify --root . --json
```

The baseline ID is a source snapshot reference only. It is not external validation evidence, does not inspect raw evidence, does not close gaps, and does not prove production readiness.


## Phase 17 closure gate

Phase 17 adds metadata-only readiness attestation and closure-gate commands:

```bash
PYTHONPATH=src python -m bountyclaw closure-gate attestation-template --root . --json
PYTHONPATH=src python -m bountyclaw closure-gate status --root . --json
PYTHONPATH=src python -m bountyclaw closure-gate export --root . --output closure_gate_package --json
PYTHONPATH=src python -m bountyclaw closure-gate verify --root . --json
```

These commands do not inspect raw evidence, run external validation, close gaps, raise readiness, contact targets, or submit reports. They prepare future human AppSec/release reviewers to manually assess baseline-bound validation metadata.


## Phase 18 readiness dashboard

Phase 18 adds a metadata-only dashboard and external executor index:

```bash
PYTHONPATH=src python -m bountyclaw readiness-dashboard build --root . --json
PYTHONPATH=src python -m bountyclaw readiness-dashboard handoff-index --root . --json
PYTHONPATH=src python -m bountyclaw readiness-dashboard export --root . --output readiness_dashboard_package --json
PYTHONPATH=src python -m bountyclaw readiness-dashboard verify --root . --json
PYTHONPATH=src python scripts/phase18_verify.py --root . --json
```

These commands consolidate local governance metadata from release controls, hardening, handoff, evidence ledger, evidence review, gap tracker, validation runbook, validation baseline, and closure gate tooling. They do not execute external validation, inspect raw evidence, close gaps, change readiness, or prove production readiness.
