# BountyClaw Architecture

## 1. System Mission

BountyClaw is a local-first, CLI-first, authorized bug bounty research assistant. Its purpose is to help legitimate security researchers and software owners find, triage, document, and report vulnerabilities in code as quickly and accurately as possible while preserving responsible-disclosure boundaries.

BountyClaw is not an autonomous exploitation platform. It must not be designed or operated for unauthorized scanning, exploitation, stealth, credential theft, persistence, destructive testing, or policy evasion.

## 2. Current Architecture Status

- Project state: Phase 19 completed in ChatGPT Project Mode after governance initialization, safety foundation, repository planning, scanner/finding/report/model/memory/release/hardening/handoff/evidence-review/gap-tracker/runbook foundations, and validation-baseline source snapshot binding, and closure-gate/readiness-attestation governance, and readiness-dashboard/external-executor-index governance, and local quality/security gate execution/remediation.
- Implementation state: minimal local CLI skeleton, configuration model, scope manifest schema, deny-by-default scope gate, audit event model, read-only repository intake, deterministic non-executing scan planning, scanner adapter interfaces, controlled subprocess wrapper, built-in local Python static scanner, preliminary finding models, canonical finding normalization, redaction engine, local SQLite evidence store, findings CLI commands, provider-neutral model router metadata, deterministic mock provider, prompt-safety envelope builder, prompt-injection signal detection, mocked model triage command, human triage review state, report draft models, local report persistence, report CLI commands, local policy summary reader, fixture-only MCP registry/tool allowlist, fixture-only browser policy ingestion, local SQLite memory store, non-executing skill templates, memory/skill CLI commands, local release-control models, release checklist/verification/rollback CLI commands, CI workflow definitions, release documentation, Phase 10 hardening models, deterministic redaction/prompt-safety corpora, hardening CLI commands, external-validation planning, Phase 11 handoff models, evidence template generation, local handoff package export, handoff verification commands, Phase 12 validation-evidence ledger models, hash-only artifact inventory, gap-readiness mapping, ledger export commands, Phase 12 Markdown review ledger, Phase 13 evidence-review models, metadata-only review decision schema, hash-bound review status checks, gap-closure proposal commands, Phase 13 Markdown review ledger, Phase 14 gap tracker governance models, metadata-only `PRODUCTION_GAP_TRACKER.md` audit, Codex gap backlog export, Phase 14 Markdown review ledger, and tests exist.
- Active implementation boundary: local CLI, scope gate, read-only repository metadata intake, planning-only scan recommendations, explicitly feature-gated local static scanning against allowlisted repositories, redaction-first local persistence of canonical findings/evidence, mocked offline model triage over redacted stored findings, human-approved triage review state, non-submitting report draft generation, fixture-only MCP policy tool invocation, fixture-only local policy ingestion, explicit-approval local memory, non-executing skill proposals, non-networked release-control verification, non-networked Phase 10 hardening verification, non-networked Phase 11 handoff package generation, and non-networked Phase 12 validation-evidence ledger generation, non-networked Phase 13 evidence-review proposal generation, and non-networked Phase 14 gap tracker audit/backlog generation, Phase 18 readiness dashboard generation, and Phase 19 local quality/security gate metadata verification.
- Next phase: external production validation execution, source-baseline-bound evidence production, human evidence review, manual governance gap closure, and readiness recalculation in Codex/local/CI/human environments.
- Current production readiness: 94%.

## 3. Principal Architectural Decisions

### 3.1 Product Shape

BountyClaw will begin as a local CLI application to maximize speed, reproducibility, low deployment complexity, and safe researcher control. A web UI, service API, scheduler daemon, or multi-user control plane may be added later only after the local CLI workflow is stable and governed.

### 3.2 Recommended Initial Stack

- Language: Python 3.12+.
- Package/runtime manager: `uv`.
- CLI framework: Typer.
- Console UX: Rich.
- Validation/config models: Pydantic.
- Local database: SQLite through SQLModel or equivalent typed persistence layer.
- Configuration format: YAML plus environment variables for secrets.
- Scanner integration model: adapter-based subprocess execution with normalized JSON findings.
- LLM integration model: provider-neutral model router with per-task routing policy.
- Headless browser model: Playwright, gated to policy ingestion and approved web workflows.
- MCP model: MCP client/server adapters behind tool allowlists.
- Test framework: pytest.
- Static quality gates: ruff, mypy or pyright, bandit, pip-audit or equivalent.

These choices are defaults and may be revised only through a documented architecture update.

### 3.3 Deployment Model

Initial deployment is local-only. No cloud deployment, hosted SaaS, or production multi-user backend is planned for MVP. Enterprise deployment hardening remains tracked as deferred work.

### 3.4 Security Boundary

BountyClaw must operate only on assets that the operator owns or is explicitly authorized to test through a bug bounty program, private engagement, internal audit, or written scope grant.

Mandatory safety controls:

1. Every scan must bind to a scope manifest before execution.
2. All targets must be allowlisted.
3. Network activity is disabled by default until a later governed phase.
4. Active exploitation is disabled by default and must remain human-approved even when future safe PoC support is added.
5. Destructive tests, brute force, denial-of-service, stealth, persistence, malware-like behavior, credential harvesting, secret exfiltration, and out-of-scope probing are prohibited.
6. Report generation must optimize accuracy, reproducibility, evidence clarity, and program fit; it must not fabricate impact or exaggerate evidence.
7. All LLM tool use must be policy-checked, logged, and bounded by the current scope manifest.

## 4. Core Domain Model

### 4.1 Program Scope

A program scope defines the authorized testing boundary.

Expected fields:

- program name
- policy URL or local policy file
- authorized repositories
- authorized domains and URL patterns
- out-of-scope assets
- allowed testing techniques
- prohibited testing techniques
- rate limits
- disclosure rules
- report template preferences
- evidence handling rules
- safe harbor text, if available

### 4.2 Target

A target is a specific repository, package, application, endpoint, or document set that is inside the active program scope.

### 4.3 Finding

A finding is a normalized candidate vulnerability record.

Expected fields:

- finding ID
- scanner/source
- target
- file path or asset locator
- vulnerability class
- confidence
- severity estimate
- evidence
- reproduction notes
- affected component
- exploitability notes
- authorization status
- false-positive analysis
- remediation guidance
- report-readiness status

### 4.4 Evidence

Evidence is the structured, non-destructive proof supporting a finding. Evidence must avoid secret exfiltration and must be redacted before storage or model submission.

### 4.5 Report

A report is a submission-ready vulnerability disclosure draft generated from approved findings and evidence.

Expected report sections:

- summary
- affected asset
- program scope confirmation
- vulnerability class
- impact
- severity rationale
- reproducible steps
- evidence
- recommended remediation
- references
- researcher notes
- disclosure checklist

## 5. Subsystems

### 5.1 CLI Orchestrator

Responsible for command routing, user prompts, run lifecycle, output formatting, and rollback-safe execution.

Initial commands expected in later phases:

- `bountyclaw init`
- `bountyclaw scope validate`
- `bountyclaw scan repo`
- `bountyclaw findings collect`
- `bountyclaw findings list`
- `bountyclaw model route`
- `bountyclaw model triage`
- `bountyclaw report draft`
- `bountyclaw doctor`

Boundary: CLI must not contain scanner-specific or LLM-provider-specific business logic.

Phase 1 implemented the initial `doctor`, `scope validate`, and `scope check` commands. Phase 2 added `repo inspect` and `repo plan`. Phase 3 added `scan repo` for explicitly feature-gated local static scanning. Phase 4 added `findings collect` and `findings list` for canonical finding normalization and redaction-first local SQLite evidence storage. Phase 5 added `model providers`, `model route`, and `model triage` for offline provider cataloging, fail-closed routing, prompt-safety validation, and mocked triage. Phase 6 added `report review`, `report draft`, and `report list` for human triage state and non-submitting report drafts. Phase 7 added `mcp servers`, `mcp tools`, `mcp invoke`, `browser plan`, and `browser policy-ingest` for fixture-only MCP/browser policy ingestion foundations. Phase 8 added `memory remember`, `memory list`, `memory export`, `memory delete`, `skills list`, and `skills propose` for explicit-approval local memory and non-executing workflow templates. Phase 9 added `release checklist`, `release verify`, and `release rollback-plan` for local release-control governance. Phase 10 added `hardening checklist`, `hardening verify`, `hardening redaction-corpus`, `hardening prompt-corpus`, and `hardening external-plan` for local production-hardening verification and future validation planning. Phase 11 added `handoff plan`, `handoff evidence-template`, `handoff export`, and `handoff verify` for Codex/local/CI evidence planning and export. Phase 12 added `validation-evidence ledger`, `validation-evidence gap-readiness`, `validation-evidence export-ledger`, and `validation-evidence verify`. Phase 13 added `evidence-review template`, `evidence-review status`, `evidence-review closure-proposals`, `evidence-review export-package`, and `evidence-review verify`. These commands do not access networks, call live LLM providers, launch live MCP servers, launch live browsers, perform active exploitation, execute skill steps, expand scope, publish packages, execute external CI, inspect raw evidence contents, close production gaps, or submit reports.

### 5.2 Scope and Policy Gate

Responsible for validating that each action is authorized by the active scope manifest.

Boundary: all scanners, browser tools, MCP tools, and LLM agents must call this subsystem before taking action.

Phase 1 implemented a fail-closed local scope gate for manifest validation and local repository action authorization. Phase 5 added `model.triage` authorization for mocked model-assisted analysis. Phase 6 added `triage.review` and `report.draft` controls for human-reviewed report drafting. Phase 7 added `mcp.tool.invoke` and `browser.policy_ingest` controls for fixture-only MCP/browser policy ingestion. Phase 8 added `memory.read`, `memory.write`, `memory.export`, `memory.delete`, and `skill.propose` controls for local memory and non-executing skill proposals. Future privileged subsystems must be explicitly wired through this gate before they are enabled.

### 5.2.1 Repository Intake and Scan Planning

Responsible for read-only local repository metadata collection, deterministic language/manifest detection, and non-executing scan-plan generation.

Boundary: repository intake must call the scope gate before reading metadata, must not persist source contents, must not write inside inspected repositories, must not execute scanners, and must not require network, LLM, MCP, or browser capabilities. Phase 2 implemented this subsystem as a planning-only foundation for Phase 3 scanner adapters.

### 5.3 Scanner Adapter Layer

Responsible for integrating external scanners through stable adapters and normalizing their output.

Expected initial scanner classes:

- static application security testing
- dependency vulnerability scanning
- secret detection with redaction
- configuration/IaC scanning
- language-specific code pattern scanning

Boundary: scanner adapters may execute external tools only through a constrained execution wrapper.

Phase 3 implemented the scanner adapter subsystem, preliminary scanner finding models, a controlled subprocess runner for future external adapters, a scanner registry/allowlist, and a built-in deterministic Python static scanner. The built-in scanner reads Python source files for AST-based pattern matching but does not execute target code, access networks, write to the repository, call models, invoke MCP/browser tools, submit reports, or include raw source excerpts in findings. External scanner binaries were not validated in Phase 3 and remain deferred.

### 5.4 Findings Normalization Engine

Responsible for converting scanner output into a common schema, deduplicating findings, calculating confidence, and preserving traceable evidence.

Boundary: normalization must remain deterministic and testable without LLM calls. Phase 4 implemented deterministic canonical finding IDs, deduplication, redacted evidence records, human-triage report-readiness status, and scanner-result ingestion. Representative real-world evidence quality validation remains deferred to external/Codex/local environments and human review.

### 5.5 Evidence Store

Responsible for local persistence of scope manifests, scan runs, findings, evidence, reports, and audit logs.

Boundary: the evidence store must never persist unredacted secrets by default. Phase 4 implemented a local SQLite store for scan runs, canonical findings, and redacted evidence. The store rejects paths inside the target repository by default and keeps source excerpts disabled. Encryption-at-rest, migrations, backup/restore drills, and realistic large-repository validation remain deferred production work.

### 5.6 Model Router

Responsible for routing model requests to the best configured provider/model for a task.

Routing dimensions:

- task type
- context length
- cost cap
- latency target
- reasoning depth
- privacy sensitivity
- local-vs-cloud policy
- JSON reliability
- user-configured provider preference

Boundary: model router must not execute tools directly. It only selects and invokes model clients through policy-controlled interfaces. Phase 5 implemented provider metadata for mock, OpenAI, Anthropic, Google, Mistral, Cohere, Groq, and Ollama/local-server style providers, but only `mock.local` is executable. Live model/provider calls, credentials, billing, network access, and provider SDK integration remain disabled and deferred. The router fails closed if a live provider is requested under the current policy.

### 5.7 LLM Reasoning Agents

Responsible for assisted triage, false-positive analysis, exploitability explanation, remediation guidance, and report drafting.

Boundary: agents must not bypass the scope gate, execute arbitrary commands, or initiate network actions. Agent prompts must include authorization constraints and secret-handling rules. Phase 5 implemented mocked finding triage over redacted evidence only; output remains advisory and human-review-only. Scanner output, repository content, evidence, policy text, and model output are treated as untrusted.

### 5.7.1 Prompt Safety Layer

Responsible for constructing model payloads from redacted, isolated, explicitly untrusted content.

Boundary: prompt-safety logic must run Phase 4 redaction before model payload construction, detect prompt-injection signals, preserve trusted policy boundaries, and prevent untrusted content from being treated as instructions. Phase 5 implemented deterministic prompt envelopes, untrusted-content delimiters, no-secret-payload tests, and prompt-injection fixture tests. Real live model evaluation remains deferred.

### 5.8 Report Generator

Responsible for producing accurate, thorough, program-aligned bug bounty reports from approved findings and evidence.

Boundary: report generator must not fabricate evidence, inflate severity, or claim validation that did not occur. Phase 6 implemented human triage review persistence, deterministic markdown report drafts, optional mocked triage context, and local report draft listing. Draft generation requires `review_status=approved_for_draft`, records `submission_allowed=false`, and keeps `validation_status=not_validated_static_only`. Real bounty-platform validation, legal/compliance review, and automated submission remain deferred.

### 5.9 MCP Gateway

Responsible for connecting approved MCP servers and exposing narrowly scoped tools to BountyClaw.

Boundary: every MCP tool must be declared, allowlisted, scope-checked, logged, and revocable. Phase 7 implemented registry metadata, tool allowlist metadata, and one in-process fixture tool (`policy.local_file_summary`) that summarizes a local policy file after redaction. Phase 7 does not launch external MCP servers, open stdio/HTTP transports, access networks, interact with live targets, run active validation, or submit reports. Real MCP protocol/runtime validation remains deferred.

### 5.10 Headless Browser Controller

Responsible for approved browser workflows such as reading program policy pages, collecting documentation references, and performing explicitly authorized non-destructive validation.

Boundary: live target interaction remains disabled until a later governed phase and must require human approval plus scope validation. Phase 7 implemented only a no-network browser workflow plan and local policy-file ingestion through the browser safety boundary. It does not launch Playwright, fetch policy URLs, authenticate sessions, submit forms, contact live targets, run active validation, or submit reports. Parsed policy hints are advisory and cannot expand the scope manifest.

### 5.11 Memory and Skill Registry

Responsible for storing reusable procedures, learned scanner patterns, project-specific notes, and workflow templates.

Boundary: memory must not store secrets, private program data without user approval, or sensitive evidence beyond retention settings. Phase 8 implemented a local SQLite memory store, explicit human approval for memory writes/deletes, redaction-first memory persistence, default rejection for secret-like and raw-evidence content, export/delete support, built-in non-executing skill templates, and scope-gated skill proposals. Memory and skills cannot expand scope, execute tools, call providers, invoke MCP/browser runtimes, perform active validation, or submit reports.

### 5.15 Release Controls

Responsible for defining local release checklists, CI/CD workflow expectations, packaging controls, rollback plans, and environment-limited validation disclosure.

Boundary: release-control commands are informational and local-only. They must not publish packages, execute hosted CI, create cloud infrastructure, enable live providers, run live MCP/browser runtimes, perform active validation, or submit reports. Phase 9 implemented release checklist generation, local release-control verification, deterministic rollback-plan output, GitHub Actions/Dependabot definitions, release/security/rollback documentation, and tests. Hosted CI execution, clean install validation, package signing/provenance, and package publishing remain deferred.

### 5.16 Production Hardening and External Validation

Responsible for locally checking production-hardening invariants, running deterministic safety fixture corpora, and producing an explicit external-validation plan for Codex/local/CI/human continuation.

Boundary: hardening commands are informational and local-only. They must not execute hosted CI, install packages from indexes, run unavailable security tools, install external scanner binaries, create sandboxes, contact networks, invoke live providers, launch real MCP/browser runtimes, perform active validation, publish packages, or submit reports. Phase 10 implemented hardening checklist generation, local hardening verification, redaction fixture corpus execution, prompt-safety fixture corpus execution, external-validation plan generation, CI workflow hook definition, security-validation documentation, and tests. Hosted CI, clean install, static/security tool execution, external scanner validation, sandbox/egress validation, live provider validation, real MCP/browser validation, human report quality review, operational drills, signing/provenance, and publishing remain deferred.

### 5.17 External Validation Handoff Package

Responsible for turning Phase 10 deferred validation plans into deterministic Codex/local/CI/human task packages, evidence templates, command runbooks, and gap-closure checklists.

Boundary: handoff commands are informational and local-only. They must not execute hosted CI, install packages, run scanner binaries, configure branch protection, invoke live providers, launch MCP/browser runtimes, contact targets, perform active validation, publish artifacts, sign artifacts, or submit reports. Phase 11 implemented handoff plan generation, evidence-template generation, handoff package export, local handoff-readiness verification, CI workflow hook definition, and tests. All evidence artifacts generated by future environments remain untrusted until reviewed and recorded in `PRODUCTION_GAP_TRACKER.md`.


### 5.18 Validation Evidence Ledger

Responsible for inventorying future external-validation artifacts, hashing present files, mapping artifacts to production-gap IDs, exporting local evidence ledgers, and reporting gap-closure readiness for human review.

Boundary: validation-evidence commands are local-only and metadata-only. They may hash files but must not read, summarize, print, trust, or classify raw artifact contents. They must not execute hosted CI, install packages, run external scanners, launch MCP/browser runtimes, call live providers, contact targets, perform active validation, close production gaps, recalculate production readiness from unreviewed artifacts, publish packages, sign artifacts, or submit reports. Phase 12 implemented validation-evidence ledger generation, gap-readiness mapping, ledger export, local verification, CI workflow hook definition, handoff-command updates, and tests. Future artifact production, private evidence review, and evidence-based gap closure remain deferred.

### 5.19 Evidence Review and Gap-Closure Governance

Responsible for turning Phase 12 hash-only artifact metadata into human-review decision templates, hash-bound review status, and manual gap-closure proposals.

Boundary: evidence-review commands are local-only and metadata-only. They may read a JSON review-decision metadata file and compare reviewer-supplied artifact hashes to the Phase 12 ledger, but they must not read, summarize, print, classify, or trust raw evidence contents. They must not close production gaps, edit `PRODUCTION_GAP_TRACKER.md`, recalculate production readiness, execute external validation, contact networks, run scanners, launch MCP/browser runtimes, call live providers, perform active validation, publish packages, sign artifacts, configure branch protection, or submit reports. Phase 13 implemented evidence-review templates, review status checks, gap-closure proposal generation, review package export, local verification, handoff-command updates, and tests. Future human evidence review execution and manual governance updates remain deferred.


### 5.20 External Validation Runbook and Execution Journal

Phase 15 adds a local-only `validation_runbook` subsystem. It derives deterministic future execution steps from unresolved production gaps and Phase 14 Codex backlog items, emits a metadata-only execution journal template, assesses optional journal metadata, and exports runbook packages for Codex/local/CI/human continuation.

The subsystem is prohibited from executing external validation, reading raw evidence, contacting targets, closing production gaps, or increasing production readiness. Journal entries may reference artifact IDs and SHA-256 hashes only; raw logs, exploit payloads, secrets, screenshots, and sensitive evidence contents are not permitted.

### 5.12 Audit and Telemetry Layer

Responsible for local logs, run manifests, command approvals, model-call metadata, and reproducibility artifacts.

Boundary: no telemetry may be sent externally without explicit opt-in.

## 6. Agentic Workflow Model

A typical future run:

1. Operator initializes a workspace.
2. Operator imports or creates a scope manifest.
3. Scope gate validates assets and allowed actions.
4. Scanner adapters run local, non-destructive analysis.
5. Findings normalization deduplicates and scores results.
6. Mocked/model triage agents review redacted evidence within policy constraints; live model calls remain disabled until a later governed phase.
7. Report generator creates non-submitting drafts for human review.
8. Operator reviews, edits, validates, and manually submits final reports outside BountyClaw.

Automated report submission is not part of the MVP unless a later phase explicitly approves it with program-specific safeguards.

## 7. Security and Abuse-Prevention Requirements

### 7.1 Mandatory Controls

- Scope manifest required before scans.
- Local-only scanning first.
- No public target probing in MVP.
- No destructive actions.
- No stealth mechanisms.
- No credential theft or secret exfiltration.
- Secret redaction before storage and LLM submission.
- Human approval for any future active validation.
- Structured audit log for every run.
- Deterministic findings schema.
- Reproducible report generation.
- Explicit approval and redaction before memory persistence.
- Memory and skill templates must never expand executable scope or trigger tools.

### 7.2 Prompt and Tool Safety

- Prompts must include scope and responsible-disclosure constraints.
- Tool calls must be policy-checked.
- LLM output must be treated as untrusted until validated.
- Prompt-injection risks from repository content, policy pages, and web content must be mitigated.
- Model responses must not be allowed to modify scope or disable safety controls.

### 7.3 Secrets and Sensitive Data

- Secrets must be detected and redacted.
- API keys must come from environment variables or approved local secret storage.
- Secrets must not be persisted in project logs.
- Findings involving exposed credentials must document presence safely without disclosing raw values.

## 8. Validation Strategy

### 8.1 Local Validation

- Unit tests for scope validation, config parsing, findings normalization, redaction, evidence storage, model routing, report templates, MCP fixture tools, browser policy ingestion, memory approval/export/delete, and non-executing skill proposals.
- Integration tests with fixture repositories, local static scanner outputs, and mocked or constrained scanner subprocess behavior.
- Golden-file tests for deterministic report generation.
- Security tests for secret redaction and prompt-injection isolation.
- CLI smoke tests for all commands, including MCP/browser fixture commands, memory/skill commands, and release-control commands.

### 8.2 Deferred Validation

- Real external scanner installation validation.
- Containerized execution validation.
- Full MCP integration validation.
- Headless browser validation against real program pages.
- Hosted CI/CD execution validation.
- Load/performance validation.
- External penetration testing.

Deferred validation must remain tracked in `PRODUCTION_GAP_TRACKER.md`.

## 9. Rollback Strategy

- Every phase must use small reversible patches.
- Configuration changes must be explicit and reviewable.
- Persistent schema changes require migrations and rollback notes.
- Agent/tool enablement must be revocable through configuration.
- New scanners must be added behind adapters and feature flags.
- Any failed validation halts progress until resolved or explicitly deferred in the gap tracker.

## 10. Production-Readiness Definition

BountyClaw is not production-ready until all of the following are complete:

- deterministic local CLI workflow
- mandatory scope gate
- scanner adapter validation, including external scanner binary validation where applicable
- findings normalization tests
- secret redaction validation, including no-raw-secret persistence checks
- report generation validation
- model-router reliability tests
- prompt-injection hardening tests
- local Phase 10 hardening fixture corpora
- Phase 11 external-validation handoff evidence package
- Phase 12 validation evidence ledger
- Phase 13 evidence review and manual gap-closure proposal workflow
- dependency/security scanning
- CI/CD gates with hosted execution evidence
- reproducible packaging and clean install validation
- documented operational runbooks
- external security review or penetration test
- validated rollback procedure

## 11. Current Non-Goals

- Unauthorized vulnerability scanning.
- Autonomous exploitation of public targets.
- Automated bounty submission without human review.
- Cloud-hosted multi-tenant SaaS.
- Stealth, evasion, persistence, or malware-like behavior.
- Denial-of-service testing.
- Credential harvesting.
- Payment or monetization workflow.

## 12. Architecture Change Control

Any change to stack, deployment model, security boundary, agent autonomy, scanner behavior, or production-readiness criteria must update this file, `ROADMAP.md`, the active phase subroadmap, and `PRODUCTION_GAP_TRACKER.md` when it creates or resolves gaps.


## Phase 14 Architecture Update

Phase 14 adds a local-only Gap Tracker Governance and Codex Backlog Export component.

Responsibilities:

- Parse `PRODUCTION_GAP_TRACKER.md` unresolved `PGT-*` entries.
- Validate unique IDs and mandatory required fields.
- Export deterministic Codex/local/CI/human backlog tasks ordered by risk and gap ID.
- Augment the Phase 11 handoff package with Phase 14 gap tracker commands.
- Preserve the invariant that backlog output is not evidence and cannot close gaps or raise readiness.

Non-responsibilities:

- No raw validation evidence inspection.
- No external validation execution.
- No production gap closure.
- No production readiness increase based on audit/backlog output.
- No hosted CI, package publication, signing/provenance, live providers, real MCP/browser runtimes, active validation, or bounty submission.


## Phase 15 Architecture Update

Phase 15 adds the External Validation Runbook and Execution Journal subsystem.

Responsibilities:

- Build deterministic future validation runbook steps from unresolved `PGT-*` gaps and Phase 14 Codex backlog items.
- Generate metadata-only future execution journal templates.
- Assess journal metadata without trusting raw external evidence.
- Export JSON/Markdown runbook packages for Codex/local/CI/human continuation.
- Augment the Phase 11 handoff package with Phase 15 runbook commands.
- Preserve the invariant that runbook and journal output is not evidence, not authorization, and not production readiness.

Non-responsibilities:

- No raw validation evidence inspection.
- No external validation execution.
- No production gap closure.
- No production readiness increase based on runbook or journal output.
- No hosted CI, package publication, signing/provenance, live providers, real MCP/browser runtimes, active validation, target contact, or bounty submission.

Phase 15 preserves all prior no-network, no-active-validation, no-raw-evidence-inspection, no-auto-submission, and no-production-claim constraints.


## Phase 16 Architecture Update

Phase 16 adds the Validation Baseline Manifest and Source Snapshot Binding subsystem.

Responsibilities:

- Build a deterministic hash-only inventory of source, governance, tests, scripts, CI definitions, and package metadata.
- Generate a stable baseline ID from sorted path/hash metadata.
- Exclude caches, archives, build artifacts, private validation evidence, execution journals, and local runtime output directories.
- Export baseline packages that future Codex/local/CI/human executors can reference in evidence journals and evidence-review decisions.
- Preserve the invariant that baseline metadata is not validation evidence by itself and cannot close production gaps.

Non-responsibilities:

- No raw source export.
- No raw validation evidence inspection.
- No hosted CI execution.
- No external scanner, sandbox, live-provider, MCP/browser, active validation, publishing, signing, branch protection, deployment, or bounty submission.
- No production gap closure or readiness increase based on baseline metadata alone.


## Phase 17 Architecture Update

Phase 17 adds the Closure Gate and Readiness Attestation Governance subsystem.

Responsibilities:

- Generate metadata-only readiness-attestation templates for future human AppSec/release reviewers.
- Assess future attestations against the current Phase 16-derived baseline ID, Phase 12 evidence metadata, Phase 13 review metadata, Phase 14 gap tracker structure, and Phase 15 execution-journal metadata.
- Validate SHA-256 field shape for referenced review, journal, and gap tracker artifacts.
- Report candidate manual gap-update IDs without closing gaps.
- Export closure-gate packages and commands for Codex/local/CI/human continuation.

Non-responsibilities:

- No raw evidence inspection.
- No raw source export.
- No external validation execution.
- No hosted CI execution.
- No active validation, exploitation, live provider calls, real MCP/browser runtimes, package publishing, signing/provenance, branch protection, deployment, or bounty submission.
- No production gap closure or readiness increase based on attestation metadata alone.


## Phase 18 Architecture Update

Phase 18 adds the Readiness Dashboard and External Executor Index subsystem.

The subsystem is metadata-only and local-only. It consolidates Phase 9 through Phase 17 verifier outputs into an operator dashboard and produces an ordered external executor command index for Codex/local/CI/human validation workflows. It does not execute external validation, inspect raw evidence, accept evidence, close production gaps, change production readiness, contact targets, launch live providers, invoke real MCP/browser runtimes, perform active validation, publish packages, configure branch protection, or submit bounty reports.

New components:

- `src/bountyclaw/readiness_dashboard/models.py`
- `src/bountyclaw/readiness_dashboard/service.py`
- `scripts/phase18_verify.py`
- `bountyclaw readiness-dashboard build`
- `bountyclaw readiness-dashboard handoff-index`
- `bountyclaw readiness-dashboard export`
- `bountyclaw readiness-dashboard verify`

Rollback baseline: Phase 17 closure-gate/readiness-attestation governance remains the rollback-safe baseline.


## Phase 19 Architecture Update

Phase 19 adds the Local Quality/Security Gate subsystem. It executes and records locally codeable quality gates, including tests, compile checks, ruff formatting and linting, mypy type checks, Bandit security scanning, package build, and clean wheel install smoke validation. It also records the attempted but environment-blocked `pip-audit` dependency audit.

Phase 19 does not expand target-facing capability. It does not contact targets, execute external scanners, enable live model providers, launch MCP/browser runtimes, inspect raw evidence, close production gaps, or claim hosted CI/branch protection.

New local-only component:

- `quality_gates`: deterministic gate checklist, metadata verification, export package, and CLI surface.

Production readiness is updated to 94% as a governance estimate for completed local quality/security remediation only. It remains blocked from production-ready status until hosted CI, online dependency audit, branch protection, evidence review, external scanner/sandbox/provider/runtime validation, and manual gap closure are completed outside ChatGPT Project Mode.
