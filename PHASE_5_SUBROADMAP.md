# PHASE_5_SUBROADMAP.md

# Phase 5: LLM Model Router and Prompt-Safety Layer

## Phase Status

Completed.

## Objectives

1. Add provider-neutral model-routing interfaces without enabling live provider calls.
2. Add a deterministic offline mock provider for safe validation inside ChatGPT Project Mode.
3. Add routing policy that fails closed for live providers, unknown providers, and policy violations.
4. Add prompt-safety envelopes that separate trusted policy from untrusted repository/scanner/evidence content.
5. Add defense-in-depth redaction before any model payload construction.
6. Add prompt-injection signal detection for common instruction override and prompt-extraction patterns.
7. Add scope-gated mocked finding triage over Phase 4 redacted evidence.
8. Add tests for routing, redaction, prompt isolation, mocked provider behavior, scope enforcement, and CLI behavior.
9. Update `ROADMAP.md`, `ARCHITECTURE.md`, `AGENTS.md`, and `PRODUCTION_GAP_TRACKER.md` at phase completion.

## Deliverables

Completed:

- Provider-neutral model catalog.
- Provider metadata for `mock.local`, OpenAI, Anthropic, Google, Mistral, Cohere, Groq, and Ollama/local-style providers.
- Fail-closed routing policy that only executes `mock.local` in Phase 5.
- Prompt envelope models with trusted policy sections and explicitly delimited untrusted sections.
- Prompt-injection signal detection for fixture-based safety validation.
- Redaction-before-prompt construction path using the Phase 4 redaction engine.
- Deterministic mock provider client.
- Scope-gated `model.triage` action.
- CLI commands:
  - `bountyclaw model providers`
  - `bountyclaw model route`
  - `bountyclaw model triage`
- Tests for Phase 5 behavior.

Deferred:

- Live OpenAI/Anthropic/Google/Mistral/Cohere/Groq/Ollama calls.
- Provider SDK integration.
- Provider credentials and secret management.
- Live model response quality evaluation.
- Live model no-secret payload inspection.
- Cost, latency, quota, retry, rate-limit, and billing controls.
- Model-output adversarial safety evaluation beyond deterministic fixture tests.
- Report generation from model triage output.

## Subsystem Boundaries

### In Scope

- Local CLI extensions for offline model routing and mocked triage.
- Provider metadata and deterministic routing decisions.
- Prompt payload preparation from already-redacted findings/evidence.
- Defense-in-depth redaction before prompt construction.
- Prompt-injection signal detection and untrusted-content isolation.
- Mocked model-provider behavior for local validation.
- Scope-gated `model.triage` authorization.

### Out of Scope

- Live LLM provider calls.
- Provider credentials.
- Network calls.
- MCP tools.
- Browser automation.
- Active vulnerability validation.
- Automated report submission.
- Claims that mocked triage is production model evaluation.
- Claims that pattern-based prompt-injection detection is complete.

## Dependencies

Completed prerequisites:

- Phase 1 scope gate and CLI foundation.
- Phase 2 repository intake and deterministic scan planning.
- Phase 3 local static scanner MVP.
- Phase 4 canonical findings, redaction engine, and SQLite evidence store.

New Phase 5 dependencies added:

- `model.triage` scope action.
- Evidence-store finding-bundle loading.
- Prompt-safety envelope construction from canonical findings and redacted evidence.

## Implementation Sequence

Completed sequence:

1. Reconciled Phase 4 governance and source state.
2. Created `PHASE_5_SUBROADMAP.md` before implementation.
3. Added model-router package and models.
4. Added provider catalog with mock plus metadata-only major providers.
5. Added fail-closed router.
6. Added prompt-safety redaction and injection-signal utilities.
7. Added deterministic mock provider client.
8. Added scope-gated model triage service.
9. Extended evidence store with redacted finding-bundle loading.
10. Added `model.triage` action to the scope manifest model and gate.
11. Added CLI model commands.
12. Added Phase 5 tests.
13. Updated governance files and gap tracker.

## Validation Sequence

Executed and passed:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -m bountyclaw --help
PYTHONPATH=src python -m bountyclaw doctor
PYTHONPATH=src python -m bountyclaw model providers --json
PYTHONPATH=src python -m bountyclaw model route --json
PYTHONPATH=src python -m bountyclaw model triage --manifest <scope.yaml> --repo <repo> --store <evidence.sqlite> --finding-id <id> --enable-mock-model --json
```

Observed results:

- 66 tests passed.
- Compile validation passed.
- CLI smoke validation passed.
- Phase 5 model triage smoke validation passed.

## Rollback Strategy

To revert Phase 5:

1. Remove `PHASE_5_SUBROADMAP.md`.
2. Remove `src/bountyclaw/model_router/`.
3. Remove `tests/test_model_router_phase5.py`.
4. Revert `model.triage` additions in `src/bountyclaw/scope/models.py`.
5. Revert model CLI additions in `src/bountyclaw/cli.py`.
6. Revert evidence-store finding-bundle read additions if no longer needed.
7. Revert version updates in `src/bountyclaw/__init__.py` and `pyproject.toml`.
8. Revert Phase 5 documentation updates in governance files.

Rollback fallback:

- Phase 4 `findings collect` and `findings list` remain the stable fallback.
- No external provider state, credentials, network calls, or production resources were introduced.

## Drift-Prevention Constraints

- Do not enable live provider calls in Phase 5.
- Do not add provider credentials.
- Do not send raw source, raw secrets, or unredacted evidence to any model payload.
- Do not treat untrusted evidence or scanner output as instructions.
- Do not allow model output to trigger tools, scanner execution, browser actions, MCP calls, or report submission.
- Do not claim model validation beyond deterministic mock tests.
- Do not bypass the scope gate for `model.triage`.

## Environment Limitations

ChatGPT Project Mode allowed local Python implementation and tests but did not allow:

- live model-provider account validation
- provider SDK credential validation
- cloud/model billing validation
- network egress validation against live providers
- large corpus prompt-injection evaluation
- realistic red-team model-output evaluation
- full DLP/secret corpus validation
- SOC 2/HIPAA/GDPR compliance review

All such tasks are recorded in `PRODUCTION_GAP_TRACKER.md`.

## Expected Unresolved Gaps

Remaining after Phase 5:

- Live model provider calls are not implemented or validated.
- Prompt-injection testing is fixture-based only.
- Redaction is not validated against realistic secret corpora or live provider payloads.
- Model-output safety evaluation is not externally validated.
- Report generation is not implemented.
- Human triage state machine is not implemented.
- CI/CD and package release gates are missing.

## Expected Future Continuation Tasks

Next phase:

- Create `PHASE_6_SUBROADMAP.md`.
- Implement deterministic human-reviewed triage state and report draft models.
- Consume Phase 4 canonical findings and Phase 5 mocked model triage output.
- Generate report drafts without claiming unperformed validation.
- Preserve manual submission only.

## Completion Summary

Phase 5 completed the provider-neutral model routing and prompt-safety foundation with mocked execution only. It established safe boundaries for future model-assisted triage and reporting while preserving local-first, scope-gated, redaction-first operation.
