# Phase 8 Subroadmap: Memory, Skills, and Workflow Learning

## Status

Status: Completed.

## Objectives

1. Add a local-only memory subsystem for human-approved project notes.
2. Add reusable, non-executing skill templates for repeatable bug-bounty workflows.
3. Require explicit human approval before memory writes and deletes.
4. Redact and inspect memory content before persistence.
5. Reject secrets, credential-like content, and raw/sensitive evidence by default.
6. Provide memory list, export, and delete support.
7. Prevent memory and skills from expanding scope or triggering tools.
8. Preserve Phase 7 MCP/browser fixture behavior as rollback fallback.

## Deliverables

Completed:

- `src/bountyclaw/memory/` subsystem.
- SQLite-backed memory store.
- Memory record, approval, export, delete, skill template, and skill proposal models.
- Scope-gated actions:
  - `memory.read`
  - `memory.write`
  - `memory.export`
  - `memory.delete`
  - `skill.propose`
- CLI commands:
  - `bountyclaw memory remember`
  - `bountyclaw memory list`
  - `bountyclaw memory export`
  - `bountyclaw memory delete`
  - `bountyclaw skills list`
  - `bountyclaw skills propose`
- Built-in non-executing skill templates:
  - `local-static-triage-draft`
  - `policy-fixture-ingestion`
  - `memory-hygiene-review`
- Tests for memory approval, scope gating, secret rejection, store-path safety, export/delete support, non-executing skill plans, and CLI smoke behavior.

## Subsystem Boundaries

Phase 8 may:

- Persist local memory records outside target repositories.
- Store only redacted, human-approved notes.
- Export and delete local memory records.
- List and propose reusable workflow templates.
- Evaluate required scope actions for skill proposals.

Phase 8 must not:

- Store raw secrets.
- Store raw vulnerability evidence by default.
- Expand scope based on memory, skills, reports, policies, model output, MCP output, or browser output.
- Execute scanners through skills.
- Invoke models through skills.
- Invoke MCP/browser tools through skills.
- Contact networks.
- Launch real MCP servers.
- Launch real browser runtimes.
- Perform active validation.
- Submit bounty reports.

## Dependencies

- Phase 1 scope gate.
- Phase 4 redaction engine and store-path safety helper.
- Phase 6 human-review safety model.
- Phase 7 MCP/browser fixture boundaries.

## Implementation Sequence

Completed:

1. Created `PHASE_8_SUBROADMAP.md`.
2. Added Phase 8 scope actions.
3. Added memory models and local SQLite memory store.
4. Added redaction-first memory write service.
5. Added memory list/export/delete services.
6. Added built-in non-executing skill templates.
7. Added skill proposal service with required-action scope decisions.
8. Added CLI commands for memory and skills.
9. Added Phase 8 tests.
10. Updated governance files and gap tracker.

## Validation Sequence

Completed:

1. Baseline Phase 7 tests passed before implementation.
2. Full pytest suite passed after implementation.
3. Compile validation passed.
4. CLI smoke checks passed for memory and skills commands.
5. Governance artifacts were updated.

Executed validation:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q
PYTHONPATH=src python -m compileall -q src tests
PYTHONPATH=src python -m bountyclaw memory remember --manifest <scope.yaml> --repo <repo> --store <memory.sqlite> --content "..." --approved-by reviewer --approval-note "..." --approve-memory-write --json
PYTHONPATH=src python -m bountyclaw memory list --manifest <scope.yaml> --repo <repo> --store <memory.sqlite> --json
PYTHONPATH=src python -m bountyclaw memory export --manifest <scope.yaml> --repo <repo> --store <memory.sqlite> --json
PYTHONPATH=src python -m bountyclaw skills list --json
PYTHONPATH=src python -m bountyclaw skills propose --manifest <scope.yaml> --repo <repo> --skill-id local-static-triage-draft --json
PYTHONPATH=src python -m bountyclaw memory delete --manifest <scope.yaml> --repo <repo> --store <memory.sqlite> --memory-id <id> --approve-delete --json
```

## Rollback Strategy

Rollback is straightforward:

1. Remove `PHASE_8_SUBROADMAP.md`.
2. Remove `src/bountyclaw/memory/`.
3. Remove `tests/test_memory_phase8.py`.
4. Revert Phase 8 CLI additions in `src/bountyclaw/cli.py`.
5. Revert Phase 8 scope actions in `src/bountyclaw/scope/models.py`.
6. Revert Phase 8 version/config updates.
7. Revert documentation and gap-tracker updates.

Rollback-safe fallback:

- Phase 7 MCP/browser fixture foundations remain usable.
- Phase 6 report drafting remains usable.
- Phase 4 evidence store remains usable.

## Drift-Prevention Constraints

- Memory writes require explicit human approval.
- Memory deletes require explicit human approval.
- Memory and skill commands are local-only.
- Memory store paths inside target repositories are rejected.
- Memory cannot authorize actions or expand target scope.
- Skill proposals cannot execute tools.
- Required skill actions are only evaluated and reported; they are not run.
- Secrets and raw evidence are rejected by default.

## Environment Limitations

Still not executable inside ChatGPT Project Mode:

- Organization-specific retention policy review.
- Legal/privacy review of long-term memory semantics.
- Encrypted memory-store validation.
- Backup/restore/migration drills.
- Multi-user memory permission testing.
- CI/CD security and quality gates.
- Clean package installation validation.

## Expected Unresolved Gaps

Remaining gaps are recorded in `PRODUCTION_GAP_TRACKER.md`, especially:

- realistic redaction corpus validation
- memory privacy/retention review
- encrypted storage and migration validation
- skill quality validation against real workflows
- CI/CD and release controls
- external penetration/security review

## Expected Future Continuation Tasks

Next phase: Phase 9, CI/CD, Packaging, and Release Controls.

Recommended Phase 9 tasks:

1. Create `PHASE_9_SUBROADMAP.md`.
2. Add CI workflow definitions.
3. Add lint/type/test/security gates.
4. Add package build validation.
5. Add release checklist and rollback documentation.
6. Keep live network/provider/MCP/browser/deployment validations tracked as environment-limited tasks unless performed in a real external environment.
