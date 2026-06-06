# Executive Status Summary

BountyClaw has completed Phases 0 through 19 inside the ChatGPT Project Mode environment. The system is now a local-first CLI with governance controls, deny-by-default scope gating, read-only repository intake, deterministic scan planning, a feature-gated built-in local Python static scanner, canonical findings normalization, redaction-first SQLite evidence persistence, provider-neutral model routing metadata, a deterministic mock model provider, prompt-safety envelopes, mocked model triage, human triage review state, non-submitting report draft generation, fixture-only MCP registry/tool allowlisting, fixture-only local policy ingestion through a browser safety boundary, explicit-approval local memory, redacted memory export/delete support, non-executing skill templates, local release-control verification, CI workflow definitions, release documentation, rollback documentation, deterministic release handoff checks, local production-hardening verification, deterministic redaction and prompt-safety fixture corpora, an explicit external-validation handoff plan, deterministic Codex/local/CI/human handoff tasks, future evidence templates, local handoff package export, handoff-readiness verification, Markdown review ledger, hash-only validation-evidence artifact inventory, gap-to-evidence readiness mapping, local validation-evidence ledger export, validation-evidence readiness verification, metadata-only evidence-review templates, hash-bound review status, manual gap-closure proposal generation, local evidence-review package export, and evidence-review readiness verification, gap tracker required-field auditing, Codex gap backlog export, local gap tracker package export, gap tracker governance verification, metadata-only external validation runbook generation, execution journal template/status checks, local runbook package export, and validation-runbook verification, hash-only validation-baseline source snapshot generation, baseline package export, validation-baseline readiness verification, metadata-only closure-gate status, readiness-attestation templates, closure-gate package export, and closure-gate readiness verification.

The system is not production-ready for enterprise deployment, live bounty-platform automation, live LLM provider use, external scanner orchestration, real MCP server execution, real headless browser automation, organization-grade memory/privacy governance, hosted CI execution, externally reviewed clean package install evidence, artifact signing/provenance, branch protection, external evidence production/review, human review decision creation, Phase 14 backlog execution, Phase 15 runbook execution/journal creation, Phase 16 baseline-bound evidence production, Phase 17 readiness attestation, Phase 18 readiness dashboard handoff execution, Phase 19 hosted quality-gate enforcement, evidence-based gap closure, external security review, performance/load validation, active validation, or automated report submission. All live network actions, live MCP servers, live browser navigation, active validation, live provider calls, and automated bounty submission remain disabled or unimplemented.

# Current Production Readiness %

94%

This percentage is a governance estimate only. It reflects validated local code and tests through Phase 19, including local hardening checks, deterministic redaction/prompt-safety fixture corpora, external-validation handoff package tooling, validation-evidence ledger/gap-readiness tooling, and evidence-review/gap-closure proposal tooling, gap tracker backlog tooling, validation-runbook tooling, hash-only validation-baseline source snapshot tooling, and metadata-only closure-gate/readiness-attestation tooling, and readiness-dashboard/external-executor-index tooling, and local quality/security gate execution/remediation tooling. It does not claim production deployment, live provider validation, external scanner validation, real MCP/browser validation, penetration testing, hosted CI execution, clean packaging validation, artifact signing/provenance, compliance validation, real bounty-program report quality, performance/load validation, or enterprise operational readiness.

# Current Completed Phases

- Phase 0: Governance and Architecture Initialization.
- Phase 1: CLI Skeleton and Safety Gate Foundation.
- Phase 2: Local Repository Intake and Deterministic Scan Planning.
- Phase 3: Static Scanner Adapter MVP.
- Phase 4: Findings Normalization and Evidence Store.
- Phase 5: LLM Model Router and Prompt-Safety Layer.
- Phase 6: Triage and Report Drafting Workflow.
- Phase 7: MCP and Headless Browser Integration Foundations.
- Phase 8: Memory, Skills, and Workflow Learning.
- Phase 9: CI/CD, Packaging, and Release Controls.
- Phase 10: Production Hardening and External Validation, completed locally inside ChatGPT Project Mode.
- Phase 11: External Validation Handoff Package, completed locally inside ChatGPT Project Mode.
- Phase 12: Validation Evidence Ledger and Gap-Closure Readiness, completed locally inside ChatGPT Project Mode.
- Phase 13: Evidence Review Workflow and Gap-Closure Governance, completed locally inside ChatGPT Project Mode.
- Phase 14: Gap Tracker Governance and Codex Backlog Export, completed locally inside ChatGPT Project Mode.
- Phase 15: External Validation Runbook and Execution Journal, completed locally inside ChatGPT Project Mode.
- Phase 16: Validation Baseline Manifest and Source Snapshot Binding, completed locally inside ChatGPT Project Mode.
- Phase 17: Closure Gate and Readiness Attestation Governance, completed locally inside ChatGPT Project Mode.
- Phase 18: Readiness Dashboard and External Executor Index, completed locally inside ChatGPT Project Mode.
- Phase 19: Local Quality/Security Gate Execution and Remediation, completed locally inside ChatGPT Project Mode.

# Current Incomplete Phases

- Post-Phase 19 external production completion: hosted CI, externally reviewed clean install evidence, external scanners, sandbox/egress, live providers, real MCP/browser runtimes, validation evidence production, human evidence review decisions, evidence-based gap closure, readiness recalculation, human report review, performance, rollback, signing/provenance, publishing, branch protection, and enterprise operational validation.

# Deferred Production Tasks

### PGT-052

- Unique ID: PGT-052
- Phase association: Phase 3 through Phase 10
- Subsystem association: Dependency and Supply-Chain Analysis
- Description: Implement dependency/advisory scanning for manifests and lockfiles.
- Status: Local dependency-manifest risk scanner implemented with curated, deterministic offline rules.
- Why incomplete: Full-scale advisory-backed dependency analysis is still incomplete; dependency-manifest heuristics are implemented locally.
- Why blocked in ChatGPT Project Mode: Real advisory DB synchronization, ecosystem breadth, vulnerable-version evidence corpus validation, and external scanner comparison require governed networked tools and runtime environments.
- Risk level: High
- Dependency requirements: Repository manifest detection, scanner adapter framework, advisory data source decision, redaction and findings normalization.
- Exact future validation required: Advisory corpus fixture tests, external advisory-tool comparison, no-network-default behavior tests, and canonical finding normalization checks.
- Exact future tooling/environment required: Python 3.12+, pytest, advisory tooling (OSV/pip-audit/npm-audit/Snyk-style) in approved local or CI environments.
- Recommended future agent type: Supply-chain security agent.
- Estimated production impact: High; dependency vulnerabilities are a major bug bounty signal.
- Completion criteria: Dependency findings are normalized into canonical findings with redacted evidence and no unapproved network calls.
- Rollback considerations: Disable dependency adapters and keep built-in static scanner if advisory validation fails.

### PGT-053

- Unique ID: PGT-053
- Phase association: Phase 8
- Subsystem association: Memory and Skill Registry
- Description: Implement local reusable skills, workflow templates, and memory with retention and secret-safety controls.
- Why incomplete: Basic Phase 8 memory/skills implementation now exists, but production retention policy, privacy review, encrypted storage, multi-user permissioning, and organization-specific memory rules are not complete.
- Why blocked in ChatGPT Project Mode: Basic implementation is possible, but production retention policy, privacy review, and organization-specific memory rules require human review.
- Risk level: Medium
- Dependency requirements: Evidence privacy policy, redaction engine, local storage conventions, skill schema, user approval model.
- Exact future validation required: Realistic redaction corpus tests, privacy review, retention policy review, export/delete acceptance checks, encrypted-store validation, backup/restore/migration tests, unsafe skill regression tests, and evidence that memory cannot expand scope or trigger tools.
- Exact future tooling/environment required: Python 3.12+, pytest, local SQLite or file store, privacy review environment.
- Recommended future agent type: Privacy-conscious agentic workflow engineer.
- Estimated production impact: Medium; improves repeatability but is not required for the current safe MVP path.
- Completion criteria: Memory/skill records are local, redacted, auditable, deletable, written only with explicit user approval, governed by production retention/privacy rules, and validated in local/CI environments.
- Rollback considerations: Disable memory persistence and retain stateless workflows if privacy validation fails.

### PGT-080

- Unique ID: PGT-080
- Phase association: Phase 8 through Phase 10
- Subsystem association: Memory Store Encryption, Retention, and Recovery
- Description: Validate production-grade memory-store privacy controls, encryption-at-rest, retention enforcement, backup/restore, and schema migration behavior.
- Why incomplete: Phase 8 implements a local SQLite memory store with export/delete support, but no encryption, migration framework, retention sweeper, backup/restore drill, or organization policy review exists.
- Why blocked in ChatGPT Project Mode: Requires local/CI filesystem validation, encryption/key-management choice, realistic retention policies, backup storage, and human privacy/legal review.
- Risk level: Medium
- Dependency requirements: Phase 8 memory store, secrets manager/key-management decision, retention policy, backup target, CI/local test runner.
- Exact future validation required: Encrypted-store tests, migration forward/backward tests, backup/restore drill, retention expiry tests, export/delete acceptance tests, and no-secret persistence checks with a realistic corpus.
- Exact future tooling/environment required: Python 3.12+, SQLite tooling, optional SQLCipher or filesystem encryption, backup storage, local/Codex/CI runner, human privacy reviewer.
- Recommended future agent type: Privacy-focused storage and release-engineering agent.
- Estimated production impact: Medium; local CLI can operate without this, but enterprise memory use requires it.
- Completion criteria: Memory records are protected, retainable/deletable by policy, restorable, migratable, and auditable without raw secret persistence.
- Rollback considerations: Disable memory persistence and retain stateless workflows if encryption/retention validation fails.

### PGT-081

- Unique ID: PGT-081
- Phase association: Phase 8 through Phase 10
- Subsystem association: Skill Workflow Quality and Safety Validation
- Description: Validate reusable skill templates against realistic bug bounty workflows and prove they cannot trigger tools, change scope, or imply authorization.
- Why incomplete: Phase 8 implements deterministic built-in non-executing skill templates and proposal tests only. Real workflow quality and misuse review are not complete.
- Why blocked in ChatGPT Project Mode: Requires real user workflows, human AppSec review, possible Codex/local test expansion, and long-running usage evaluation.
- Risk level: Medium
- Dependency requirements: Phase 8 skill templates, scope gate, report workflow, policy ingestion fixtures, human workflow rubric.
- Exact future validation required: Skill template review against real bounty workflows, adversarial tests for unsafe instructions, no-tool-execution regression tests, scope-denial tests, and human usability review.
- Exact future tooling/environment required: Local/Codex workspace, representative bug bounty scenarios, human AppSec reviewers, pytest fixtures.
- Recommended future agent type: Agentic workflow QA agent with AppSec oversight.
- Estimated production impact: Medium; skills improve repeatability but unsafe templates could cause drift.
- Completion criteria: Skill templates are accurate, safe, useful, non-executing, and cannot expand or bypass scope.
- Rollback considerations: Disable unsafe templates individually while preserving memory and core Phase 7/6 workflows.

### PGT-082

- Unique ID: PGT-082
- Phase association: Phase 8 through Phase 10
- Subsystem association: Multi-User and Organization Memory Governance
- Description: Define and validate how memory behaves for teams, enterprises, shared workspaces, least privilege, and auditability.
- Why incomplete: Phase 8 is local single-operator only and has no multi-user authorization, org roles, tenancy model, or shared-memory approval workflow.
- Why blocked in ChatGPT Project Mode: Requires product decisions, identity/auth design, organization policy review, possibly hosted or shared storage, and external access-control validation.
- Risk level: Medium
- Dependency requirements: Future auth/authorization model if multi-user support is adopted, memory store, audit logs, retention/privacy policy.
- Exact future validation required: RBAC/ABAC tests, shared-memory approval workflows, export/delete permissions, audit trails, tenant-isolation tests, and privacy review.
- Exact future tooling/environment required: Local/Codex/CI environment, auth provider or local identity fixtures, multi-user test harness, human governance review.
- Recommended future agent type: Enterprise platform/AppSec authorization agent.
- Estimated production impact: Low for local single-user MVP, high for enterprise rollout.
- Completion criteria: Shared memory is least-privilege, auditable, deletable/exportable by policy, and isolated across users/workspaces.
- Rollback considerations: Keep memory single-user/local-only if enterprise governance is not validated.

### PGT-063

- Unique ID: PGT-063
- Phase association: Phase 6 through Phase 10
- Subsystem association: Report Quality and Program Fit
- Description: Validate report drafts against real bounty-program templates, platform expectations, disclosure rules, and payout-relevant quality criteria without exaggerating evidence.
- Why incomplete: Phase 6 creates deterministic local report drafts only; real program-specific quality validation and payout benchmarking were not performed.
- Why blocked in ChatGPT Project Mode: Requires real program policies, human reviewer judgment, platform-specific examples, legal/compliance review, and possibly private bounty platform access.
- Risk level: High
- Dependency requirements: Phase 6 report drafts, Phase 7 policy ingestion, human review process, report-quality rubric.
- Exact future validation required: Human review of drafts against multiple real program templates, tests for missing required fields, adversarial checks for unvalidated impact claims, and manual acceptance criteria from bounty program reviewers.
- Exact future tooling/environment required: Authorized program documentation, bounty platform accounts where permitted, human AppSec/legal reviewers, local/Codex workspace for fixture expansion.
- Recommended future agent type: Bug bounty report quality specialist with AppSec oversight.
- Estimated production impact: High; report quality directly affects practical utility and accepted submissions.
- Completion criteria: Drafts meet a documented program-specific rubric while preserving `submission_allowed=false` until manual approval and submission.
- Rollback considerations: Keep Phase 6 generic markdown drafts and disable program-specific templates if quality validation fails.

### PGT-068

- Unique ID: PGT-068
- Phase association: Phase 7 through Phase 10
- Subsystem association: Program Policy Parsing Quality
- Description: Validate local policy summary extraction against representative real bounty policies and ensure parsed hints do not incorrectly authorize work.
- Why incomplete: Phase 7 policy parsing uses deterministic keyword hints over local fixture files only.
- Why blocked in ChatGPT Project Mode: Requires representative policy corpus, human comparison, legal/program interpretation review, and possibly private program documents.
- Risk level: High
- Dependency requirements: Phase 7 local policy reader, scope gate, human policy-review workflow, report-quality rubric.
- Exact future validation required: Golden-policy fixtures, human-labeled policy extraction tests, false-positive/false-negative review, and tests proving parsed hints cannot expand scope automatically.
- Exact future tooling/environment required: Authorized policy corpus, local/Codex test workspace, human AppSec/legal reviewers.
- Recommended future agent type: Policy-ingestion QA agent with human AppSec oversight.
- Estimated production impact: High; inaccurate policy interpretation can cause out-of-scope behavior or poor reports.
- Completion criteria: Policy parsing is source-linked, human-verifiable, tested against representative policies, and never changes executable scope without explicit manifest updates.
- Rollback considerations: Disable automated policy hinting and require manual scope manifests if parsing quality is insufficient.

# Environment-Limited Tasks

### PGT-047

- Unique ID: PGT-047
- Phase association: Phase 5 through Phase 10
- Subsystem association: Live Model Provider Integration
- Description: Validate live provider calls for OpenAI, Anthropic, Google, Mistral, Cohere, Groq, Ollama/local servers, or other configured providers.
- Why incomplete: Phases 5 through 7 intentionally execute only deterministic offline `mock.local` provider behavior.
- Why blocked in ChatGPT Project Mode: Requires credentials, provider SDKs, billing/quota configuration, network egress, secret management, and provider-specific safety review.
- Risk level: High
- Dependency requirements: Provider credentials, secrets manager, no-secret payload validation, rate limits, retry policy, cost controls, telemetry controls.
- Exact future validation required: Live-provider smoke tests, no-secret payload inspection, redaction verification, prompt-injection fixtures, timeout/retry tests, cost/quota checks, and audit logs.
- Exact future tooling/environment required: Local/Codex/CI environment with approved network access, provider accounts, sandbox credentials, and secure secret storage.
- Recommended future agent type: LLM platform integration engineer with AppSec review.
- Estimated production impact: High for advanced triage/reporting quality, but not required for current offline-safe workflow.
- Completion criteria: Live provider calls are explicitly opt-in, redacted, logged, rate-limited, and covered by tests.
- Rollback considerations: Keep `mock.local` as fallback and disable live providers through routing policy if validation fails.

### PGT-049

- Unique ID: PGT-049
- Phase association: Phase 5 through Phase 10
- Subsystem association: Model Output Safety Evaluation
- Description: Evaluate model outputs for unsafe instructions, hallucinated impact, unvalidated exploit claims, and prompt-injection susceptibility.
- Why incomplete: Current prompt/model safety tests are fixture-based and deterministic, not broad adversarial model evaluations.
- Why blocked in ChatGPT Project Mode: Requires live or local model variants, adversarial corpora, repeated evaluation, and human review of model behavior.
- Risk level: High
- Dependency requirements: Prompt-safety layer, redaction engine, model router, adversarial fixture suite, live/local model configuration.
- Exact future validation required: Red-team prompt suite, untrusted-evidence injection tests, hallucination checks, report-safety checks, and model-output gating tests.
- Exact future tooling/environment required: Local/Codex/CI environment, model provider access, evaluation harness, human AppSec reviewers.
- Recommended future agent type: AI safety/AppSec evaluation agent.
- Estimated production impact: High if live models are enabled.
- Completion criteria: Model outputs are constrained, logged, rejected when unsafe, and never trigger tools or submissions without human approval.
- Rollback considerations: Disable model-assisted workflows and retain deterministic non-model report drafts if evaluation fails.

### PGT-058

- Unique ID: PGT-058
- Phase association: Phase 7 through Phase 10
- Subsystem association: Live Program Policy Ingestion
- Description: Ingest real bounty policy pages or documents for allowed targets, report rules, and safe-harbor details.
- Why incomplete: Phase 7 implemented local policy-file fixture ingestion only; live page fetching and browser navigation remain disabled.
- Why blocked in ChatGPT Project Mode: Requires browser automation, network access, authentication in some cases, robots/policy respect, and human verification.
- Risk level: Medium
- Dependency requirements: Phase 7 browser/MCP controls, scope gate, policy parser, prompt-safety and redaction controls.
- Exact future validation required: Fixture policy parsing tests, human comparison against real policies, no-network-default tests, and refusal behavior for ambiguous policies.
- Exact future tooling/environment required: Playwright or document parser, approved network/browser environment, authorized program policy pages, human reviewers.
- Recommended future agent type: Policy ingestion and browser automation engineer.
- Estimated production impact: Medium to high; policy accuracy affects safe operation and report fit.
- Completion criteria: Policy data is parsed, source-linked, human-verifiable, and never expands scope automatically.
- Rollback considerations: Require manual scope manifests if automated policy ingestion is unreliable.

### PGT-069

- Unique ID: PGT-069
- Phase association: Phase 7 through Phase 10
- Subsystem association: Real MCP Runtime Validation
- Description: Validate actual MCP server startup, protocol negotiation, tool discovery, tool invocation, timeout behavior, and audit logging.
- Why incomplete: Phase 7 implemented fixture-only in-process MCP metadata and one local policy summary tool; no real MCP process or transport is used.
- Why blocked in ChatGPT Project Mode: Requires MCP-compatible server runtimes, subprocess or network transports, local tool environments, and sandboxing.
- Risk level: High
- Dependency requirements: MCP registry, tool allowlist, scope gate, audit logging, sandbox/egress controls.
- Exact future validation required: Stdio and/or HTTP MCP fixture servers, unregistered-server denial, tool allowlist enforcement, timeout tests, malformed response tests, and no-submission/no-network-default tests.
- Exact future tooling/environment required: Local/Codex/CI environment with MCP servers, process supervision, network controls, and pytest integration fixtures.
- Recommended future agent type: MCP integration engineer with AppSec review.
- Estimated production impact: Medium; required for real MCP extensibility but not for current local workflow.
- Completion criteria: Real MCP tools run only when declared, allowlisted, scope-gated, audited, sandboxed, and revocable.
- Rollback considerations: Disable real MCP transports and retain the Phase 7 builtin fixture registry if validation fails.

### PGT-070

- Unique ID: PGT-070
- Phase association: Phase 7 through Phase 10
- Subsystem association: Real Headless Browser Runtime Validation
- Description: Validate Playwright or equivalent browser runtime for approved policy/document workflows.
- Why incomplete: Phase 7 implemented a no-network browser plan and local policy-file parser only; no browser runtime is launched.
- Why blocked in ChatGPT Project Mode: Requires browser binaries, sandbox support, network controls, approved target pages, and platform-specific runtime validation.
- Risk level: High
- Dependency requirements: Browser controller, scope gate, policy ingestion parser, audit logging, sandbox/egress design.
- Exact future validation required: Browser startup tests, no-network-default tests, local fixture page parsing, robots/rate-limit compliance checks, no-form-submission tests, and live-page tests only under approved authorization.
- Exact future tooling/environment required: Playwright or equivalent, browser sandbox, local/CI runner, controlled network environment, authorized program pages.
- Recommended future agent type: Browser automation engineer with AppSec oversight.
- Estimated production impact: Medium; useful for policy ingestion and documentation workflows but risky if misconfigured.
- Completion criteria: Browser workflows are opt-in, scope-gated, auditable, sandboxed, non-submitting, and denied by default for live targets.
- Rollback considerations: Disable browser runtime and retain local policy-file ingestion if validation fails.

# Missing Infrastructure Tasks

### PGT-039

- Unique ID: PGT-039
- Phase association: Phase 3 through Phase 10
- Subsystem association: Scanner Sandbox and Network Egress Controls
- Description: Validate OS/container-level sandboxing and network-egress denial for scanner execution.
- Why incomplete: Phase 3 added a controlled subprocess wrapper but did not validate OS isolation, containers, seccomp, filesystem jails, or network egress controls.
- Why blocked in ChatGPT Project Mode: Requires local OS/container runtime, network namespace controls, and platform-specific validation.
- Risk level: High
- Dependency requirements: External scanner adapters, container runtime or OS sandbox design, controlled subprocess policy.
- Exact future validation required: Tests proving scanners cannot write outside allowed paths, cannot access network by default, and cannot escape configured sandbox boundaries.
- Exact future tooling/environment required: Docker/Podman or OS sandboxing, Linux/macOS/Windows validation hosts, network egress test harness.
- Recommended future agent type: DevSecOps sandboxing engineer.
- Estimated production impact: High for safe external scanner use.
- Completion criteria: Scanner execution is sandboxed, audited, and denied network/filesystem escape by default.
- Rollback considerations: Disable external scanners and retain built-in scanner if sandbox validation fails.

### PGT-055

- Unique ID: PGT-055
- Phase association: Phase 9 through Phase 10
- Subsystem association: Secrets and Configuration Infrastructure
- Description: Define production-grade secrets handling for future live providers, platform credentials, and deployment settings.
- Why incomplete: No live credentials or cloud deployment exist; current config intentionally rejects risky capabilities.
- Why blocked in ChatGPT Project Mode: Requires chosen secret manager, local/CI integration, credential rotation policy, and production environment design.
- Risk level: High
- Dependency requirements: Deployment model, CI/CD provider, live provider integrations, secrets manager decision.
- Exact future validation required: Secret loading tests, no-secret logging tests, rotation drill, least-privilege review, and failure-mode checks.
- Exact future tooling/environment required: 1Password/Vault/AWS Secrets Manager/Doppler/SOPS or equivalent, CI secrets, local dev secrets workflow.
- Recommended future agent type: DevSecOps secrets-management engineer.
- Estimated production impact: High if live providers, MCP servers, browser sessions, or platform APIs are enabled.
- Completion criteria: Secrets are never stored in repo/state/logs, are injected securely, and are rotatable with auditability.
- Rollback considerations: Disable live integrations if secret controls fail.

### PGT-071

- Unique ID: PGT-071
- Phase association: Phase 7 through Phase 10
- Subsystem association: MCP/Browser Runtime Isolation and Egress Controls
- Description: Validate sandboxing, process isolation, filesystem boundaries, and network-egress denial for future real MCP/browser runtimes.
- Why incomplete: Phase 7 uses in-process/local fixture code only and does not start real MCP servers or browsers.
- Why blocked in ChatGPT Project Mode: Requires OS/container primitives, browser sandboxing, process supervision, and network namespace or firewall controls.
- Risk level: High
- Dependency requirements: MCP runtime design, browser runtime design, scope gate, audit logging, environment-specific sandbox choices.
- Exact future validation required: Tests proving browser/MCP tools cannot access network by default, cannot write outside allowed state directories, cannot submit forms/reports, and cannot execute unregistered tools.
- Exact future tooling/environment required: Docker/Podman or OS sandbox, Playwright, MCP test servers, local/CI runner, egress test harness.
- Recommended future agent type: DevSecOps sandboxing engineer with browser/MCP experience.
- Estimated production impact: High if real MCP/browser runtimes are enabled.
- Completion criteria: Real runtime integrations are sandboxed, audited, and fail closed under egress/filesystem escape tests.
- Rollback considerations: Disable real runtimes and keep fixture-only Phase 7 commands if isolation validation fails.

# Missing Deployment Tasks

### PGT-012

- Unique ID: PGT-012
- Phase association: Phase 9 through Phase 10
- Subsystem association: Production Deployment
- Description: Define and validate production or enterprise deployment path.
- Why incomplete: Project is intentionally local-first and has no cloud/SaaS deployment in current phases.
- Why blocked in ChatGPT Project Mode: Requires infrastructure decisions, runtime hosts, deployment accounts, DNS/certificates if hosted, and operational ownership.
- Risk level: Medium
- Dependency requirements: Packaging, CI/CD, secrets infrastructure, observability, rollback plan.
- Exact future validation required: Clean install, deployment smoke tests, rollback test, environment config validation, and runbook execution.
- Exact future tooling/environment required: Local package manager, GitHub Actions/GitLab CI or equivalent, optional cloud/PaaS/Kubernetes depending on chosen deployment.
- Recommended future agent type: Release engineering and platform agent.
- Estimated production impact: Medium; local CLI can function without hosted deployment, but enterprise rollout needs this.
- Completion criteria: Documented deployment artifacts, installation path, runtime checks, rollback procedure, and operator runbook.
- Rollback considerations: Keep local CLI distribution if hosted deployment is not validated.

### PGT-054

- Unique ID: PGT-054
- Phase association: Phase 9
- Subsystem association: Packaging and Distribution
- Description: Build reproducible package artifacts and installation instructions.
- Why incomplete: Phase 19 successfully built wheel/sdist artifacts and clean-installed the wheel locally, but reproducible hosted CI execution, signed artifacts, provenance, and reviewed release evidence remain incomplete.
- Why blocked in ChatGPT Project Mode: Release-grade reproducibility, hosted enforcement, signing, provenance, and evidence review require a real repository/CI/release environment.
- Risk level: Medium
- Dependency requirements: Stable pyproject, dependency lock strategy, CI/CD, release signing decision.
- Exact future validation required: Repeat wheel/sdist build and clean virtualenv smoke tests in hosted CI or Codex/local release environment, then add checksum/signature/provenance validation if publishing is adopted.
- Exact future tooling/environment required: Python packaging tools, uv/pipx, GitHub Actions or equivalent, signing key management if adopted.
- Recommended future agent type: Python release engineering agent.
- Estimated production impact: Medium; required for reliable handoff/use outside ChatGPT.
- Completion criteria: Reproducible package artifacts install and run `bountyclaw doctor` in a hosted or release-grade clean environment, with reviewed evidence attached.
- Rollback considerations: Continue source checkout workflow if packaging validation fails.

# Missing Security Validations

### PGT-014

- Unique ID: PGT-014
- Phase association: Phase 4 through Phase 10
- Subsystem association: Secret Redaction and DLP Validation
- Description: Validate redaction against realistic secret corpora and live model/report/browser/MCP payloads.
- Why incomplete: Current redaction is deterministic and pattern-based with fixture tests only.
- Why blocked in ChatGPT Project Mode: Requires realistic secret fixtures, DLP review, live provider payload inspection if providers are enabled, external scanner outputs, and browser/MCP payload samples.
- Risk level: High
- Dependency requirements: Redaction engine, evidence store, model router, report generator, policy ingestion, external scanner outputs.
- Exact future validation required: Corpus tests for API keys/tokens/private keys, no-raw-secret persistence checks, no-secret model payload checks, no-secret report draft checks, no-secret policy-ingestion output checks, and false-negative review.
- Exact future tooling/environment required: Local/Codex/CI test corpus, DLP fixtures, human AppSec review, optional live provider/browser/MCP payload capture under safe conditions.
- Recommended future agent type: DLP/AppSec validation agent.
- Estimated production impact: High; secret leakage would be a severe production failure.
- Completion criteria: Redaction passes realistic corpus tests and no raw secret appears in stores, logs, reports, model prompts, MCP output, or browser policy summaries.
- Rollback considerations: Disable persistence/model/report/MCP/browser outputs that cannot prove no-secret behavior.

### PGT-015

- Unique ID: PGT-015
- Phase association: Phase 5 through Phase 10
- Subsystem association: Prompt and Untrusted Content Injection Safety
- Description: Expand prompt-injection and untrusted-content tests for repository content, scanner output, policy text, browser output, MCP output, report drafts, and model outputs.
- Why incomplete: Current tests are deterministic fixtures and do not cover broad adversarial corpora or live model behavior.
- Why blocked in ChatGPT Project Mode: Requires adversarial fixture generation, live/local model evaluation, human review, and repeated regression testing.
- Risk level: High
- Dependency requirements: Prompt-safety layer, policy ingestion, MCP/browser output models, model router, report generator, human review workflow.
- Exact future validation required: Injection fixture suite, browser/MCP untrusted-output tests, model-output rejection tests, report-safety checks, and no-tool-execution-from-untrusted-content tests.
- Exact future tooling/environment required: Local/Codex/CI environment, adversarial corpora, optional provider/model access, human AppSec/AI safety reviewers.
- Recommended future agent type: AI safety and AppSec test engineer.
- Estimated production impact: High if live models, MCP tools, or browser content are enabled.
- Completion criteria: Untrusted content cannot override policy, expand scope, trigger tools, submit reports, or cause unsafe claims.
- Rollback considerations: Disable model/MCP/browser-assisted workflows if injection controls are insufficient.

### PGT-031

- Unique ID: PGT-031
- Phase association: Phase 1 through Phase 10
- Subsystem association: Scope-Gate Integration Coverage
- Description: Prove every privileged subsystem calls the scope gate and fails closed.
- Why incomplete: Scope coverage exists through Phase 8, but future dependency/advisory, live-provider, real MCP/browser, platform, and deployment subsystems are not yet implemented or externally validated.
- Why blocked in ChatGPT Project Mode: Complete coverage requires future subsystems and external runtime environments.
- Risk level: High
- Dependency requirements: Scope gate, all future privileged subsystems, integration tests, audit logs.
- Exact future validation required: Coverage tests for every privileged action, mutation testing or explicit negative fixtures, and audit-log verification.
- Exact future tooling/environment required: Python tests, CI coverage tooling, future live integration testbeds where appropriate.
- Recommended future agent type: AppSec test automation agent.
- Estimated production impact: High; bypass would violate core safety boundary.
- Completion criteria: No privileged action can run without a valid manifest, allowed target, allowed action, and audit trail.
- Rollback considerations: Disable any subsystem whose scope-gate coverage is unproven.

### PGT-057

- Unique ID: PGT-057
- Phase association: Phase 6 through Phase 10
- Subsystem association: Report Safety Validation
- Description: Validate that drafts never overclaim exploitability, confirmed impact, or active validation that did not occur.
- Why incomplete: Phase 6 has local fixture tests only; real findings and program-specific language have not been validated broadly.
- Why blocked in ChatGPT Project Mode: Requires realistic findings, human AppSec/legal review, platform-specific report expectations, and adversarial report prompts.
- Risk level: High
- Dependency requirements: Report generator, human review workflow, model-output safety if mock/live triage is used.
- Exact future validation required: Golden report fixtures, forbidden-claim scans, human review of reports, and tests for static-only validation disclaimers.
- Exact future tooling/environment required: Local/Codex/CI test harness, human report reviewers, representative finding corpus.
- Recommended future agent type: Report safety QA agent.
- Estimated production impact: High; report misrepresentation can harm trust and program compliance.
- Completion criteria: Reports consistently preserve uncertainty, evidence limits, and manual-submission requirements.
- Rollback considerations: Disable report drafting if safety checks fail.

# Missing Runtime Validations

### PGT-016

- Unique ID: PGT-016
- Phase association: Phase 3 through Phase 10
- Subsystem association: External Scanner Runtime Validation
- Description: Validate real external scanner binaries and adapters.
- Why incomplete: Current scanning uses the built-in Python static scanner; external scanner adapters are framework-only.
- Why blocked in ChatGPT Project Mode: Requires scanner installation, version pinning, local execution, possibly containers, and platform-specific checks.
- Risk level: High
- Dependency requirements: Scanner adapter framework, sandbox/egress controls, findings normalization.
- Exact future validation required: Scanner install tests, adapter output parsing tests, timeout/failure-mode tests, no-network-default validation, and canonical finding normalization checks.
- Exact future tooling/environment required: Local/Codex/CI environment with scanner binaries, Python 3.12+, sandbox runtime.
- Recommended future agent type: Static-analysis integration engineer.
- Estimated production impact: High for vulnerability coverage.
- Completion criteria: External scanner adapters run safely, produce normalized findings, and fail closed.
- Rollback considerations: Disable external adapters and retain built-in scanner if validation fails.

### PGT-038

- Unique ID: PGT-038
- Phase association: Phase 3 through Phase 10
- Subsystem association: External Scanner Binary Compatibility
- Description: Validate external scanner versions, output formats, and cross-platform behavior.
- Why incomplete: No external binary execution occurs in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires OS-specific installs, binary availability, and CI matrix.
- Risk level: Medium
- Dependency requirements: Scanner adapter layer, release engineering matrix, sandboxing.
- Exact future validation required: Versioned scanner output fixtures, parse compatibility tests, Linux/macOS/Windows checks if supported.
- Exact future tooling/environment required: CI runners, scanner binaries, package managers, containers if adopted.
- Recommended future agent type: Scanner compatibility engineer.
- Estimated production impact: Medium to high; scanner instability can break findings.
- Completion criteria: Supported scanners have pinned versions, known-good output fixtures, and graceful failure behavior.
- Rollback considerations: Pin or disable incompatible scanner versions.

### PGT-043

- Unique ID: PGT-043
- Phase association: Phase 4 through Phase 10
- Subsystem association: Evidence Store Privacy and Retention
- Description: Define and validate evidence-store retention, encryption, export/delete, and privacy controls.
- Why incomplete: Current SQLite evidence store is local and redaction-first but lacks encryption-at-rest, retention policy, export/delete commands, and privacy review.
- Why blocked in ChatGPT Project Mode: Requires product policy decisions, encryption/key-management choices, privacy review, and backup/restore tooling.
- Risk level: High
- Dependency requirements: Evidence store, secrets manager decision, human privacy requirements, package/deployment model.
- Exact future validation required: Export/delete tests, retention-policy tests, encryption/key rotation tests if adopted, and no-raw-secret persistence checks.
- Exact future tooling/environment required: Local/Codex environment, encryption library if selected, privacy review process.
- Recommended future agent type: Privacy/security engineer.
- Estimated production impact: High for sensitive bug bounty data.
- Completion criteria: Evidence can be retained, exported, deleted, and protected according to documented policy.
- Rollback considerations: Keep store local-only and avoid sensitive persistence if privacy controls are insufficient.

### PGT-044

- Unique ID: PGT-044
- Phase association: Phase 4 through Phase 10
- Subsystem association: Evidence Store Migration and Recovery
- Description: Validate SQLite schema migrations, backup, restore, and rollback behavior.
- Why incomplete: Current schema is initialized in code but no migration framework or recovery drill exists.
- Why blocked in ChatGPT Project Mode: Requires versioned migration tooling, clean environments, and backup/restore simulations.
- Risk level: Medium
- Dependency requirements: Evidence store schema, future migration plan, release process.
- Exact future validation required: Migration tests from old schemas, backup/restore tests, corrupted-store behavior, rollback drill.
- Exact future tooling/environment required: Local/Codex/CI workspace, SQLite fixtures, release engineering support.
- Recommended future agent type: Persistence/release engineer.
- Estimated production impact: Medium; affects data durability and upgrades.
- Completion criteria: Store upgrades and rollbacks are deterministic and documented.
- Rollback considerations: Preserve source ZIP fallback and avoid destructive migrations until validated.

### PGT-072

- Unique ID: PGT-072
- Phase association: Phase 7 through Phase 10
- Subsystem association: MCP/Browser Runtime Output Safety
- Description: Validate real MCP/browser outputs are redacted, treated as untrusted, audited, and unable to trigger unsafe downstream actions.
- Why incomplete: Phase 7 outputs are fixture-only local policy summaries.
- Why blocked in ChatGPT Project Mode: Requires real MCP/browser runtime output samples, adversarial content, live/local model behavior if connected, and human safety review.
- Risk level: High
- Dependency requirements: Real MCP/browser runtimes, redaction engine, prompt-safety layer, report-safety checks, audit logs.
- Exact future validation required: Malicious policy page fixtures, MCP output injection fixtures, no-tool-trigger tests, no-report-submission tests, and audit redaction checks.
- Exact future tooling/environment required: Local/Codex/CI browser/MCP testbed, adversarial fixtures, human AppSec reviewers.
- Recommended future agent type: AppSec/browser/MCP safety test engineer.
- Estimated production impact: High if real MCP/browser integrations are enabled.
- Completion criteria: Browser/MCP outputs cannot override instructions, expand scope, leak secrets, or trigger submissions.
- Rollback considerations: Disable real MCP/browser runtime outputs and retain fixture-only summaries if validation fails.

# Missing CI/CD Validations

### PGT-018

- Unique ID: PGT-018
- Phase association: Phase 9 through Phase 10
- Subsystem association: CI/CD Pipeline
- Description: Execute the Phase 9 CI workflow on a real repository runner and prove that tests, compile checks, static quality/security gates, dependency scan, release-control verification, and packaging smoke validation block unsafe changes.
- Why incomplete: Phase 9 authored `.github/workflows/ci.yml`, but hosted CI was not executed in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires Git hosting, CI provider, runner environment, dependency installation, and repository workflow permissions.
- Risk level: High
- Dependency requirements: Stable source tree, pyproject, dependency lock strategy, release policy, GitHub/GitLab repository, CI runner.
- Exact future validation required: Green CI run on clean checkout, intentionally failing test proving failure blocks, artifact build job, dependency/security gate output, branch protection or equivalent if adopted.
- Exact future tooling/environment required: GitHub Actions/GitLab CI/etc., Python 3.12/3.13 runners, pip/uv, ruff, mypy, bandit, pip-audit, build.
- Recommended future agent type: DevSecOps CI/CD agent.
- Estimated production impact: High; prevents regressions and supports handoff.
- Completion criteria: CI blocks unsafe or failing changes and records validation artifacts from a real repository runner.
- Rollback considerations: Disable broken CI gates temporarily only with documented manual validation fallback; keep `scripts/phase9_verify.py` for local fallback.

### PGT-032

- Unique ID: PGT-032
- Phase association: Phase 9 through Phase 10
- Subsystem association: Static Quality and Security Gates
- Description: Execute and enforce ruff, mypy/pyright, bandit, pip-audit, and equivalent checks.
- Why incomplete: Phase 9 defines dev dependencies, pyproject tool sections, and CI workflow steps, but the ChatGPT container does not include these optional tools and hosted CI did not run.
- Why blocked in ChatGPT Project Mode: Requires dependency installation, tool baselining, package index access, and CI/local runner execution.
- Risk level: Medium
- Dependency requirements: Tooling decisions, pyproject configuration, CI runner, optional lock strategy.
- Exact future validation required: Lint/type/security scan runs, baseline triage, dependency vulnerability scan, fail thresholds, and false-positive suppression review.
- Exact future tooling/environment required: Local/Codex/CI environment with ruff, mypy/pyright, bandit, pip-audit, and package installation access.
- Recommended future agent type: Python quality/security tooling agent.
- Estimated production impact: Medium to high; catches defects and vulnerabilities.
- Completion criteria: Quality/security gates are configured, pass, and fail closed in CI with documented exceptions only.
- Rollback considerations: Keep manual pytest/compile validation while resolving tool configuration issues.

### PGT-083

- Unique ID: PGT-083
- Phase association: Phase 9 through Phase 10
- Subsystem association: Hosted CI Execution Evidence
- Description: Capture proof that the Phase 9 GitHub Actions workflow executes successfully on a real repository.
- Why incomplete: Workflow YAML was authored and locally inspected, but no hosted runner executed it.
- Why blocked in ChatGPT Project Mode: Requires a GitHub/GitLab repository, enabled Actions/CI runner, network access, and package installation.
- Risk level: High
- Dependency requirements: Repository host, CI runner, pyproject dependencies, workflow permissions, branch/PR event.
- Exact future validation required: Successful workflow run logs for validate and package jobs, failure-mode test, artifact/summary retention, and documented CI URL or run ID.
- Exact future tooling/environment required: GitHub Actions or equivalent, Python 3.12/3.13 runners, package index access, repository permissions.
- Recommended future agent type: DevSecOps release agent.
- Estimated production impact: High; release controls are not production-enforcing until executed on a real runner.
- Completion criteria: Real CI run is green and recorded, with failing-test behavior verified.
- Rollback considerations: Disable or adjust misconfigured workflow gates while retaining local verification until CI is fixed.

### PGT-084

- Unique ID: PGT-084
- Phase association: Phase 9 through Phase 10
- Subsystem association: Clean Package Build and Install Validation
- Description: Validate wheel/sdist build and clean installation without `PYTHONPATH`.
- Why incomplete: Phase 19 executed a local wheel/sdist build and fresh virtualenv wheel install successfully, but hosted CI reproduction and reviewed evidence remain incomplete.
- Why blocked in ChatGPT Project Mode: Requires hosted CI or release-grade local environment, dependency resolution, artifact retention, and reviewed evidence workflow.
- Risk level: Medium
- Dependency requirements: pyproject metadata, build tooling, package dependencies, CLI entry point.
- Exact future validation required: Repeat `python -m build`, fresh virtualenv wheel install, `bountyclaw doctor`, release command smoke checks, and import smoke tests without `PYTHONPATH` in hosted CI/release environment and attach reviewed evidence.
- Exact future tooling/environment required: Hosted CI or Codex/local release environment with pip/build access, clean virtualenv support, and evidence retention.
- Recommended future agent type: Python packaging/release engineer.
- Estimated production impact: High for handoff reliability.
- Completion criteria: Built artifacts install and run in hosted/release clean environment, with evidence reviewed through Phase 12-17 governance.
- Rollback considerations: Revert packaging changes and continue source checkout workflow if clean installs fail.

### PGT-085

- Unique ID: PGT-085
- Phase association: Phase 9 through Phase 10
- Subsystem association: Artifact Signing, Provenance, and Publishing
- Description: Define and validate artifact signing/provenance and any package registry publication path.
- Why incomplete: Phase 9 intentionally does not publish packages, create signatures, or generate provenance attestations.
- Why blocked in ChatGPT Project Mode: Requires registry credentials, signing/provenance tooling, key management, release owner approval, and possibly organization policy.
- Risk level: Medium
- Dependency requirements: Clean package build, release policy, signing key or OIDC provenance decision, package registry account, human release approval.
- Exact future validation required: TestPyPI/internal registry dry run, signature/provenance generation and verification, credential isolation, and rollback plan for bad release artifacts.
- Exact future tooling/environment required: Package registry, credentials manager, signing/provenance tooling, CI runner, human release authority.
- Recommended future agent type: Supply-chain release engineering agent.
- Estimated production impact: Medium to high for trusted distribution.
- Completion criteria: Artifacts are signed/provenance-backed or a documented decision explicitly defers signing; publishing remains human-approved.
- Rollback considerations: Yank/delete test artifacts when supported; never publish production artifacts without approval.

### PGT-086

- Unique ID: PGT-086
- Phase association: Phase 9 through Phase 10
- Subsystem association: Repository Branch Protection and Release Governance
- Description: Configure branch protection, required status checks, CODEOWNERS/review rules if adopted, and release approval workflow.
- Why incomplete: Phase 9 can define CI files locally but cannot configure hosted repository rules.
- Why blocked in ChatGPT Project Mode: Requires repository administrator access, hosted VCS settings, and organization policy decisions.
- Risk level: Medium
- Dependency requirements: Hosted repository, CI workflow, review policy, release owner.
- Exact future validation required: Required checks configured, protected branch enforcement verified, unauthorized push blocked, release approval workflow tested.
- Exact future tooling/environment required: GitHub/GitLab/Bitbucket repository administration access and CI integration.
- Recommended future agent type: Repository governance/release manager.
- Estimated production impact: High for enterprise release control.
- Completion criteria: Repository rules enforce CI and review gates before merge/release.
- Rollback considerations: Temporarily relax rules only with documented manual approval and restore enforcement after correction.

# Missing External Integration Tests

### PGT-064

- Unique ID: PGT-064
- Phase association: Phase 6 through Phase 10
- Subsystem association: Bounty Platform Integrations
- Description: Validate any future bounty-platform integration for report templates, policy ingestion, and manual submission workflows.
- Why incomplete: No platform API integration or automated submission exists, intentionally.
- Why blocked in ChatGPT Project Mode: Requires platform accounts, API terms review, credentials, legal approval, and human responsibility.
- Risk level: High
- Dependency requirements: Human review workflow, report drafts, policy ingestion, secret management.
- Exact future validation required: API sandbox tests if available, no-auto-submit tests, manual approval gates, audit logs, and platform-policy compliance review.
- Exact future tooling/environment required: Authorized bounty-platform account/API sandbox, secrets manager, human reviewer.
- Recommended future agent type: Platform integration engineer with legal/AppSec oversight.
- Estimated production impact: Medium; optional for use but high risk if implemented incorrectly.
- Completion criteria: Any platform integration is manual-approval-gated, compliant, audited, and non-submitting by default.
- Rollback considerations: Disable platform integrations and keep manual export/submission.

### PGT-073

- Unique ID: PGT-073
- Phase association: Phase 7 through Phase 10
- Subsystem association: Live Policy Source Integrations
- Description: Validate ingestion from real program policy sources, docs, and allowed reference pages through approved browser or document workflows.
- Why incomplete: Phase 7 only reads local policy files and does not fetch URLs.
- Why blocked in ChatGPT Project Mode: Requires network, browser/document tooling, authorization, rate-limit/robots respect, and human verification.
- Risk level: Medium
- Dependency requirements: Browser policy ingestion, MCP gateway, redaction, policy parsing QA, network controls.
- Exact future validation required: Approved policy URL tests, no-auth-bypass checks, robots/rate-limit respect, source-link fidelity tests, and human diff review.
- Exact future tooling/environment required: Playwright/document fetcher, approved network environment, authorized policy pages, human reviewers.
- Recommended future agent type: Policy source integration engineer.
- Estimated production impact: Medium; improves policy fit but must be safe.
- Completion criteria: Live policy sources are fetched only when authorized, logged, redacted, and human-verifiable.
- Rollback considerations: Return to local policy-file ingestion if live-source validation fails.

# Missing Penetration Tests

### PGT-021

- Unique ID: PGT-021
- Phase association: Phase 10
- Subsystem association: External Security Review and Penetration Testing
- Description: Perform external security review of BountyClaw itself, including scope gate, scanners, evidence store, model prompts, MCP/browser controls, report workflow, and packaging.
- Why incomplete: No external reviewer or test environment exists in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires independent testers, local/runtime environment, and a defined test plan.
- Risk level: High
- Dependency requirements: Stable release candidate, CI/CD, packaging, runtime docs, threat model.
- Exact future validation required: Threat-model review, code review, malicious fixture tests, sandbox escape attempts, prompt/tool injection tests, and report-submission safety tests.
- Exact future tooling/environment required: External AppSec reviewer, local test environment, security tools, optional container/browser/MCP runtime.
- Recommended future agent type: Independent AppSec reviewer / penetration tester.
- Estimated production impact: High; required before enterprise claims.
- Completion criteria: Findings are remediated or accepted with documented risk, and no critical/high unresolved issues remain.
- Rollback considerations: Halt production release until critical/high issues are resolved.

# Missing Observability Validation

### PGT-074

- Unique ID: PGT-074
- Phase association: Phase 8 through Phase 10
- Subsystem association: Audit and Local Observability
- Description: Expand local audit logs, run manifests, export tooling, and operator-visible diagnostics for scanner/model/report/MCP/browser workflows.
- Why incomplete: Current audit logging exists for many commands but lacks full run manifest coverage, export tooling, retention policy, and observability validation.
- Why blocked in ChatGPT Project Mode: Requires product decisions, broader runtime workflows, and possibly external logging choices for enterprise use.
- Risk level: Medium
- Dependency requirements: Audit event model, evidence store, future memory/skills, CI/CD, operator runbooks.
- Exact future validation required: Audit coverage tests for every privileged command, redaction/no-secret audit checks, export tests, and runbook validation.
- Exact future tooling/environment required: Local/Codex/CI environment, audit fixtures, optional observability stack if external telemetry is ever chosen.
- Recommended future agent type: Observability and auditability engineer.
- Estimated production impact: Medium; needed for accountable operations and incident review.
- Completion criteria: All privileged workflows emit redacted, useful, exportable local audit records.
- Rollback considerations: Disable commands whose audit coverage is incomplete.

# Missing Rollback Validation

### PGT-075

- Unique ID: PGT-075
- Phase association: Phase 8 through Phase 10
- Subsystem association: Rollback Drills
- Description: Validate rollback procedures for evidence-store schema changes, memory store changes, scanner adapters, model routing, MCP/browser runtime enablement, and packaging.
- Why incomplete: Rollback notes exist but no live rollback drill has been executed.
- Why blocked in ChatGPT Project Mode: Requires Git repository, clean environments, persisted stores, package artifacts, and runtime state.
- Risk level: Medium
- Dependency requirements: CI/CD, packaging, migration tooling, future runtime integrations.
- Exact future validation required: Revert drills, migration rollback tests, disabled-feature fallback tests, and documented operator procedures.
- Exact future tooling/environment required: Git repo, local/CI runner, backup fixtures, release artifacts.
- Recommended future agent type: Release engineering agent.
- Estimated production impact: Medium; rollback is required for safe production changes.
- Completion criteria: Operators can revert to a prior safe phase without data loss or unsafe enabled features.
- Rollback considerations: This gap defines rollback validation; until complete, production rollout should remain blocked.

# Missing Load/Performance Tests

### PGT-076

- Unique ID: PGT-076
- Phase association: Phase 8 through Phase 10
- Subsystem association: Load and Performance Validation
- Description: Validate performance on large repositories, many findings, large evidence stores, policy documents, reports, and future memory/skill records.
- Why incomplete: Current tests use small fixtures only.
- Why blocked in ChatGPT Project Mode: Requires large fixture repositories, benchmark machines/CI runners, and profiling tooling.
- Risk level: Medium
- Dependency requirements: Repository intake, scanner, findings store, reports, policy ingestion, future memory store.
- Exact future validation required: Large-repo scan timing, memory usage checks, SQLite store scaling checks, policy ingestion limits, report generation timing, and timeout behavior.
- Exact future tooling/environment required: Local benchmark machine or CI runner, large fixture repositories, profiling tools.
- Recommended future agent type: Performance engineering agent.
- Estimated production impact: Medium; performance affects usability.
- Completion criteria: Documented performance bounds and no unacceptable degradation on target-size repos.
- Rollback considerations: Add limits or disable slow adapters if performance is unacceptable.

# Temporary Mock/Stubs To Replace

### PGT-060

- Unique ID: PGT-060
- Phase association: Phase 5 through Phase 10
- Subsystem association: Deterministic Mock Provider
- Description: Replace or augment deterministic `mock.local` with governed live/local providers after safety validation.
- Why incomplete: `mock.local` is intentionally used for offline deterministic tests and is not a production LLM.
- Why blocked in ChatGPT Project Mode: Live/local providers require credentials or model servers, network/compute, and safety evaluation.
- Risk level: Medium
- Dependency requirements: Model router, prompt-safety layer, redaction validation, provider integration tests.
- Exact future validation required: Provider quality, safety, no-secret payload, cost/latency, and failure-mode tests.
- Exact future tooling/environment required: Local/Codex/CI environment with provider access or local model server.
- Recommended future agent type: LLM provider integration engineer.
- Estimated production impact: Medium; report and triage quality may improve with validated providers.
- Completion criteria: Non-mock providers are opt-in, tested, logged, and fail closed.
- Rollback considerations: Revert routing policy to `mock.local` only.

### PGT-077

- Unique ID: PGT-077
- Phase association: Phase 7 through Phase 10
- Subsystem association: Fixture MCP Tool
- Description: Replace or augment the in-process `policy.local_file_summary` fixture with real MCP server/tool integrations after runtime safety validation.
- Why incomplete: Phase 7 intentionally avoids real MCP server execution.
- Why blocked in ChatGPT Project Mode: Requires MCP runtime tools, process/network supervision, transport tests, and sandboxing.
- Risk level: Medium
- Dependency requirements: MCP registry, tool allowlist, scope gate, runtime isolation, audit logs.
- Exact future validation required: Real MCP server fixture tests, unregistered-tool denial, malformed response handling, timeout behavior, no-network/no-submission checks.
- Exact future tooling/environment required: MCP servers, local/CI runner, sandboxing/egress tools.
- Recommended future agent type: MCP integration engineer.
- Estimated production impact: Medium; enables extensibility after safe validation.
- Completion criteria: Real MCP tools are declared, allowlisted, scope-gated, audited, sandboxed, and revocable.
- Rollback considerations: Disable real MCP tools and retain fixture-only MCP registry.

### PGT-078

- Unique ID: PGT-078
- Phase association: Phase 7 through Phase 10
- Subsystem association: Fixture Browser Policy Parser
- Description: Replace or augment fixture-only local policy parsing with validated browser/document ingestion.
- Why incomplete: Phase 7 does not launch browsers or fetch live policy pages.
- Why blocked in ChatGPT Project Mode: Requires Playwright/browser binaries, network controls, approved policy pages, and human review.
- Risk level: Medium
- Dependency requirements: Browser controller, policy parser, egress controls, policy QA corpus.
- Exact future validation required: Local HTML fixture tests, approved live-page tests, no-form-submit tests, no-scope-expansion tests, and policy extraction accuracy review.
- Exact future tooling/environment required: Playwright or equivalent, local/CI browser environment, authorized policy documents/pages.
- Recommended future agent type: Browser automation and policy parsing engineer.
- Estimated production impact: Medium; improves policy ingestion after safe validation.
- Completion criteria: Browser/document ingestion is opt-in, scope-gated, non-submitting, source-linked, and human-verifiable.
- Rollback considerations: Disable live browser ingestion and retain local policy-file summaries.

# Manual Human Tasks Required

### PGT-026

- Unique ID: PGT-026
- Phase association: All phases
- Subsystem association: Human Authorization and Manual Approval
- Description: Human operators must provide valid authorization scope and approve final report submission.
- Why incomplete: This is an intentionally permanent human-control requirement, not an automation gap to eliminate.
- Why blocked in ChatGPT Project Mode: Legal authorization, bounty program participation, and final submission decisions require a human.
- Risk level: High
- Dependency requirements: Scope manifest, program policy, human reviewer identity, audit trail.
- Exact future validation required: Manual review checklist, authorization attestation, and report approval process.
- Exact future tooling/environment required: Human operator, program account, policy documents, local CLI.
- Recommended future agent type: Human AppSec operator assisted by BountyClaw.
- Estimated production impact: High; prevents unauthorized use and unsafe submissions.
- Completion criteria: Every run has explicit authorization and every report submission is human-approved outside automated paths.
- Rollback considerations: Halt workflows if authorization or approval is absent.

### PGT-065

- Unique ID: PGT-065
- Phase association: Phase 6 through Phase 10
- Subsystem association: Human Report Review and Submission
- Description: Human reviewer must validate evidence, edit drafts, confirm program-specific rules, and manually submit reports.
- Why incomplete: Phase 6 produces drafts but cannot perform human verification or final submission.
- Why blocked in ChatGPT Project Mode: Requires human security judgment, program account access, and legal/compliance responsibility.
- Risk level: High
- Dependency requirements: Report draft, program policy, verified evidence, human review checklist.
- Exact future validation required: Human acceptance checklist, final report review, proof of manual submission process, and post-submission audit notes.
- Exact future tooling/environment required: Human bug bounty operator, authorized bounty platform account, local report artifact.
- Recommended future agent type: Human bug bounty researcher / AppSec reviewer.
- Estimated production impact: High; necessary for safe real-world use.
- Completion criteria: Drafts are manually reviewed and submitted only by humans under program rules.
- Rollback considerations: Do not submit reports if human review is incomplete.

# Future Agentic Continuation Tasks

### PGT-079

- Unique ID: PGT-079
- Phase association: Phase 9
- Subsystem association: CI/CD, Packaging, and Release Handoff
- Description: Continue Phase 9 release controls into real Codex/local/CI execution and prepare Phase 10 production hardening.
- Why incomplete: Phase 9 artifacts are authored and locally validated, but real CI execution, clean install validation, package signing/provenance, and branch protection are not complete.
- Why blocked in ChatGPT Project Mode: Real CI execution requires a repository host, runner, dependency installation, and external tooling.
- Risk level: Medium
- Dependency requirements: Stable Phase 9 source tree, pyproject, tests, release checklist, chosen CI provider.
- Exact future validation required: CI green run, clean install, wheel/sdist build, lint/type/test/security gates, artifact checks, and rollback documentation.
- Exact future tooling/environment required: GitHub/GitLab/etc., CI runner, Python 3.12+, package tooling, security scanners.
- Recommended future agent type: Release engineering/DevSecOps implementation agent.
- Estimated production impact: High for reliable production handoff.
- Completion criteria: Real CI and clean package validation complete, Phase 10 subroadmap exists, and all release artifacts remain auditable without false production-readiness claims.
- Rollback considerations: Keep source ZIP handoff if CI setup fails temporarily, but do not claim production release readiness.

### PGT-067

- Unique ID: PGT-067
- Phase association: Phase 9
- Subsystem association: CI/CD and Release Handoff
- Description: Execute future Codex/local/CI continuation for release engineering, packaging, and security gates.
- Why incomplete: Phase 9 definitions exist, but no repository-host CI, clean package build, or external security tool run exists.
- Why blocked in ChatGPT Project Mode: Requires Git repository host, CI runner, package build environment, dependency installation, and external security tools.
- Risk level: Medium
- Dependency requirements: Stable Phase 9 source tree, pyproject, tests, release checklist, chosen CI provider.
- Exact future validation required: CI green run, clean install, artifact build, security scan, and rollback drill.
- Exact future tooling/environment required: GitHub/GitLab/etc., CI runner, Python 3.12+, package tooling.
- Recommended future agent type: Release engineering/DevSecOps agent.
- Estimated production impact: High for reliable production handoff.
- Completion criteria: Future agents can continue from repository state with CI-enforced gates that have executed successfully.
- Rollback considerations: Keep source ZIP handoff if CI setup fails temporarily, but do not claim production release readiness.

### PGT-087

- Unique ID: PGT-087
- Phase association: Phase 10
- Subsystem association: Production Hardening and External Validation Handoff
- Description: Create and execute Phase 10 production-hardening roadmap, including external validations that cannot be completed in ChatGPT Project Mode.
- Why incomplete: Phase 10 local hardening is complete, but the external validations required for production/enterprise readiness remain unexecuted.
- Why blocked in ChatGPT Project Mode: Requires real CI, clean installs, external scanner validation, live-provider/browser/MCP environments if enabled, penetration testing, performance tests, release governance, and human review.
- Risk level: High
- Dependency requirements: Completed Phase 9 release controls, hosted CI execution, release artifacts, production-hardening plan, external reviewers.
- Exact future validation required: Execute external CI/packaging validations, run security review, sandbox/egress tests, performance tests, rollback drill, and final production readiness review.
- Exact future tooling/environment required: Codex/local/CI environment, repository host, CI runner, package tooling, security tools, optional cloud/local runtime targets, human AppSec/release reviewers.
- Recommended future agent type: Production-hardening orchestrator with AppSec and release-engineering oversight.
- Estimated production impact: Critical; Phase 10 is required before enterprise-grade production claims.
- Completion criteria: External validations complete or explicitly accepted with evidence, risk posture recalculated, and production readiness reaches a justified final percentage.
- Rollback considerations: Keep Phase 9 local CLI/release-control baseline if external hardening fails.


### PGT-088

- Unique ID: PGT-088
- Phase association: Phase 10
- Subsystem association: Hosted CI Execution
- Description: Execute Phase 9/10 CI workflow on a real repository runner and archive evidence.
- Why incomplete: CI workflow definitions exist and include Phase 10 verification, but no hosted runner executed them in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires a repository host, Actions or equivalent runner, branch/PR context, and external execution logs.
- Risk level: High
- Dependency requirements: Git repository, CI provider, committed Phase 10 source tree, dependency installation, runner permissions.
- Exact future validation required: Push branch/PR, run CI, verify tests, compile, phase9/phase10 scripts, lint/type/security/package jobs, and failure behavior.
- Exact future tooling/environment required: GitHub Actions/GitLab CI/etc. with Python 3.12+ and package index access where allowed.
- Recommended future agent type: DevSecOps/Codex release agent.
- Estimated production impact: High; hosted CI evidence is required for release confidence.
- Completion criteria: CI run URL/logs recorded, all gates pass or accepted risks documented, gap tracker updated.
- Rollback considerations: Keep Phase 10 local validation baseline if hosted CI fails; do not release until remediated.

### PGT-089

- Unique ID: PGT-089
- Phase association: Phase 10
- Subsystem association: Clean Package Build and Install
- Description: Build wheel/sdist and validate clean installation without `PYTHONPATH`.
- Why incomplete: Phase 19 validated local build backend execution and clean wheel installation, but hosted CI reproduction and release-reviewed install evidence are not complete.
- Why blocked in ChatGPT Project Mode: Requires hosted CI or release-grade local runner, fresh virtualenv, dependency index/local wheelhouse access, artifact retention, and human evidence review.
- Risk level: High
- Dependency requirements: `pyproject.toml`, build backend, dependency resolution, clean virtual environment, CLI entrypoint.
- Exact future validation required: Repeat `python -m build`, install built wheel in a fresh hosted/release environment, run `bountyclaw doctor` and smoke commands without source-tree `PYTHONPATH`, and attach reviewed evidence.
- Exact future tooling/environment required: Hosted CI or Codex/local release environment with Python 3.12+, build tooling, dependency installation capability, and evidence retention.
- Recommended future agent type: Release-engineering agent.
- Estimated production impact: High; package install failure blocks practical distribution.
- Completion criteria: Hosted/release wheel/sdist build succeeds, fresh install succeeds, CLI entrypoint works, logs are retained, and evidence is reviewed through closure governance.
- Rollback considerations: Do not publish package if clean install fails; continue source checkout use only.

### PGT-090

- Unique ID: PGT-090
- Phase association: Phase 10
- Subsystem association: Static Quality and Security Tools
- Description: Execute ruff, mypy/pyright, bandit, pip-audit, and equivalent dependency/security gates.
- Why incomplete: Tools are defined in dev extras and CI, but not installed/executed in this ChatGPT environment.
- Why blocked in ChatGPT Project Mode: Requires optional dev/security tool installation and package index access not available deterministically here.
- Risk level: High
- Dependency requirements: Dev dependencies, Python toolchain, dependency index or local wheelhouse, security-scan policy.
- Exact future validation required: Run all configured static/security gates, remediate findings, or record approved exceptions.
- Exact future tooling/environment required: Codex/local/CI with dev extras installed and dependency-audit access.
- Recommended future agent type: AppSec/quality agent.
- Estimated production impact: High; unresolved tool findings may indicate defects or vulnerabilities.
- Completion criteria: Tool outputs archived, failures fixed or risk-accepted, gate status reflected in security ledger.
- Rollback considerations: Block release on unresolved critical findings; keep local-only handoff until resolved.

### PGT-091

- Unique ID: PGT-091
- Phase association: Phase 10
- Subsystem association: External Scanner and Sandbox Validation
- Description: Validate real external scanner binaries and OS/container sandbox plus network-egress controls.
- Why incomplete: Phase 3 has a controlled subprocess framework and built-in scanner, but real scanner binaries and sandboxes are not validated.
- Why blocked in ChatGPT Project Mode: Requires scanner installation, container/OS sandboxing, and egress controls unavailable here.
- Risk level: Critical
- Dependency requirements: Approved scanner list, sandbox runtime, fixture repositories, egress firewall/logging, scope-gate integration tests.
- Exact future validation required: Run scanner fixtures, prove no repository writes or network egress, normalize results, and record sandbox logs.
- Exact future tooling/environment required: Codex/local/CI environment with scanner binaries, container or OS sandbox, and egress monitoring.
- Recommended future agent type: AppSec scanner-integration agent.
- Estimated production impact: Critical; unsafe scanner execution can create legal and security risk.
- Completion criteria: Scanner adapters pass fixtures, sandbox and egress denial are evidenced, fallback/disable controls documented.
- Rollback considerations: Disable external scanner adapters and keep built-in static scanner if validation fails.

### PGT-092

- Unique ID: PGT-092
- Phase association: Phase 10
- Subsystem association: Live Provider and AI Safety Validation
- Description: Validate live/local model providers against no-secret payload, prompt-injection, and model-output safety requirements before enabling them.
- Why incomplete: Phase 5 implements provider metadata, prompt envelopes, and mock.local only; Phase 10 adds local fixture corpora but no live provider validation.
- Why blocked in ChatGPT Project Mode: Requires approved provider credentials or local model server, secrets management, telemetry capture, and governed egress.
- Risk level: Critical
- Dependency requirements: Provider policy, secrets manager, redaction corpus, adversarial prompt corpus, model-output safety criteria, egress controls.
- Exact future validation required: Prove raw secrets are not sent, injection attempts are bounded, outputs cannot trigger tools/submission, and provider errors fail closed.
- Exact future tooling/environment required: Governed Codex/local/CI environment with approved provider credentials or local model runtime and logs.
- Recommended future agent type: AI safety/AppSec validation agent.
- Estimated production impact: Critical; live provider misuse can leak secrets or amplify unsafe actions.
- Completion criteria: No-secret payload logs, adversarial prompt results, output safety tests, and credential-handling review are complete.
- Rollback considerations: Keep `mock.local` only if live-provider validation fails.

### PGT-093

- Unique ID: PGT-093
- Phase association: Phase 10
- Subsystem association: Real MCP and Browser Runtime Validation
- Description: Validate real MCP protocol clients/servers and headless browser runtimes under allowlists, sandboxing, and egress controls.
- Why incomplete: Phase 7 implements fixture-only MCP/browser foundations; no real MCP server or browser runtime is launched.
- Why blocked in ChatGPT Project Mode: Requires approved MCP servers, Playwright/browser runtime, sandbox, and controlled network environment.
- Risk level: Critical
- Dependency requirements: MCP allowlist, browser runtime, sandbox, policy fixtures, egress monitoring, scope-gate tests.
- Exact future validation required: Prove registered tools work, unregistered tools fail closed, browser submissions/live target contact are denied, and outputs remain untrusted.
- Exact future tooling/environment required: Codex/local/CI environment with MCP/browser runtimes and egress controls.
- Recommended future agent type: Platform/AppSec runtime agent.
- Estimated production impact: Critical; live tool/browser misuse can contact targets or leak data.
- Completion criteria: Runtime fixture tests and denial tests pass with logs; live runtimes remain disabled until validated.
- Rollback considerations: Keep fixture-only MCP/browser support if validation fails.

### PGT-094

- Unique ID: PGT-094
- Phase association: Phase 10
- Subsystem association: Human Report Quality and Manual Submission Validation
- Description: Validate generated report drafts against real authorized bounty program expectations and preserve human-only submission.
- Why incomplete: Phase 6 creates deterministic drafts, but real program fit and human quality review have not occurred.
- Why blocked in ChatGPT Project Mode: Requires authorized program policy, human security judgment, platform account access, and legal/compliance responsibility.
- Risk level: High
- Dependency requirements: Authorized program policy, sanitized finding set, report draft, human reviewer, manual submission workflow.
- Exact future validation required: Human reviewer evaluates accuracy, evidence, impact wording, remediation, non-exaggeration, and program template fit; manual submission process is documented.
- Exact future tooling/environment required: Human AppSec reviewer, authorized bounty platform account, local report artifact.
- Recommended future agent type: Human AppSec/report-review agent.
- Estimated production impact: High; report quality affects usefulness and safe disclosure.
- Completion criteria: Human review checklist passed, no fabricated validation claims, manual submission approval retained.
- Rollback considerations: Keep drafts internal-only if quality review or authorization is incomplete.

### PGT-095

- Unique ID: PGT-095
- Phase association: Phase 10
- Subsystem association: Operations, Performance, Retention, Backup/Restore, and Rollback Drills
- Description: Validate operational behavior over representative repositories and local state stores.
- Why incomplete: Local tests pass, but performance/load baselines, retention enforcement, backup/restore, export/delete, and rollback drills over realistic state have not run.
- Why blocked in ChatGPT Project Mode: Requires representative datasets, larger environments, storage policy decisions, and drill execution with human review.
- Risk level: Medium
- Dependency requirements: Representative repos, evidence/report/memory stores, retention policy, backup strategy, rollback procedure.
- Exact future validation required: Measure scan/collection/draft times, verify backup/restore, retention/delete/export, and perform rollback drill from Phase 10 to Phase 9 baseline.
- Exact future tooling/environment required: Local/CI/staging-like environment with realistic datasets and storage tooling.
- Recommended future agent type: SRE/platform validation agent.
- Estimated production impact: Medium; operational failures can cause data loss or unusable performance.
- Completion criteria: Baselines and drill results recorded, failures remediated, rollback evidence archived.
- Rollback considerations: Preserve local state backups and disable risky features if restore/rollback fails.

### PGT-096

- Unique ID: PGT-096
- Phase association: Phase 10
- Subsystem association: Release Governance, Signing, Provenance, Publishing, and Branch Protection
- Description: Configure repository release governance, artifact signing/provenance, package publishing dry run, and branch protection.
- Why incomplete: Phase 9/10 define release controls, but no repository-host rules, signing, provenance, or publishing validation has occurred.
- Why blocked in ChatGPT Project Mode: Requires repository admin permissions, package registry credentials, signing/provenance tooling, and human release authority.
- Risk level: High
- Dependency requirements: Repository host, branch/ruleset policy, package registry, signing/provenance tools, release approval process.
- Exact future validation required: Configure branch protection, dry-run package publishing to approved registry, generate/verify provenance or signatures, and record release approval evidence.
- Exact future tooling/environment required: GitHub/GitLab/etc., package registry, signing/provenance tooling, credentials manager, human release manager.
- Recommended future agent type: Release engineering and repository governance agent.
- Estimated production impact: High; weak release governance undermines supply-chain trust.
- Completion criteria: Branch protection active, signing/provenance evidence recorded, publishing dry run successful, release approval process documented.
- Rollback considerations: Do not publish externally if signing/provenance or branch protection fails; keep source ZIP handoff only.

### PGT-097

- Unique ID: PGT-097
- Phase association: Phase 11
- Subsystem association: External Validation Handoff Package
- Description: Execute the Phase 11 Codex/local/CI/human handoff plan in a real external environment and attach evidence artifacts.
- Why incomplete: Phase 11 generated the handoff plan, evidence templates, export package, and verifier locally, but no future executor has run the tasks.
- Why blocked in ChatGPT Project Mode: Requires real repository host, CI runner, package environment, security tools, scanners, sandboxing, live-provider or local-model environments, human reviewers, and release authority.
- Risk level: High
- Dependency requirements: Phase 11 source bundle, real repository checkout, Python 3.12+, CI/local toolchain, authorized credentials where needed, and human release owner.
- Exact future validation required: Run `bountyclaw handoff verify`, export the handoff package, execute every `P11-HANDOFF-*` task, produce every named evidence artifact, and update gap closure status.
- Exact future tooling/environment required: Codex/local/CI/human validation environment with repository-host access, package installation capability, security tooling, approved scanner/browser/model runtimes where applicable, and private evidence storage.
- Recommended future agent type: Codex release-validation orchestrator with AppSec and DevSecOps oversight.
- Estimated production impact: High; without executing the handoff, production gaps remain plans rather than evidence.
- Completion criteria: Every handoff task has produced evidence, evidence is reviewed, and governance files are updated with exact results.
- Rollback considerations: Preserve the Phase 11 source bundle and Phase 10 hardening baseline if external handoff execution fails.

### PGT-098

- Unique ID: PGT-098
- Phase association: Phase 11
- Subsystem association: External Validation Evidence Management
- Description: Establish private evidence storage, redaction review, and attachment workflow for future validation artifacts.
- Why incomplete: Phase 11 defines expected evidence artifact names and sensitive-handling rules, but no actual evidence repository or review workflow has been created.
- Why blocked in ChatGPT Project Mode: Requires repository/team policy, private storage, access controls, human review, and potentially confidential CI/security/scanner/model logs.
- Risk level: Medium
- Dependency requirements: Evidence retention policy, private artifact storage, redaction rules, release owner, and AppSec reviewer.
- Exact future validation required: Create evidence storage, upload generated validation artifacts, verify no raw secrets or unauthorized target data are exposed, and link evidence to gap closures.
- Exact future tooling/environment required: Private repository artifacts, encrypted storage or approved document store, CI artifact retention, and human review workflow.
- Recommended future agent type: Release evidence and privacy-governance agent.
- Estimated production impact: Medium; without evidence management, validations may be unauditable or leak sensitive data.
- Completion criteria: Evidence artifacts are stored privately, redacted where required, linked from gap tracker entries, and approved by a human release owner.
- Rollback considerations: Delete or quarantine unsafe evidence artifacts if redaction or access-control review fails.

### PGT-099

- Unique ID: PGT-099
- Phase association: Phase 11
- Subsystem association: Production Gap Closure Governance
- Description: Perform evidence-based closure of production gaps and recalculate readiness after external validation.
- Why incomplete: Phase 11 prepares gap-closure checklists, but no external evidence exists yet to close gaps or raise readiness beyond local handoff readiness.
- Why blocked in ChatGPT Project Mode: Requires completed external validation artifacts, human release authority, and final production-readiness review.
- Risk level: High
- Dependency requirements: Completed PGT-097 handoff execution, PGT-098 evidence management, updated validation logs, and human release approval.
- Exact future validation required: Review each open gap against evidence, mark closed only when completion criteria are satisfied, update risk posture, and recalculate production readiness.
- Exact future tooling/environment required: Governance review workspace, release ledger, evidence repository, and human release/AppSec reviewers.
- Recommended future agent type: Deterministic SDLC controller and human release authority.
- Estimated production impact: High; production-readiness claims depend on accurate gap closure.
- Completion criteria: Every closed gap cites evidence, unresolved gaps remain open, readiness percentage is recalculated, and rollback posture is updated.
- Rollback considerations: Reopen any gap if evidence is incomplete, invalid, sensitive, or contradicted by later validation.


### PGT-100

- Unique ID: PGT-100
- Phase association: Phase 12
- Subsystem association: Validation Evidence Ledger Execution
- Description: Execute the Phase 12 validation-evidence ledger against real external-validation artifacts after Codex/local/CI/human environments produce them.
- Why incomplete: Phase 12 implements hash-only ledger tooling and tests with absent/fixture artifacts only; no real hosted CI, package, scanner, model, MCP/browser, report-quality, operational, signing, provenance, or publishing evidence artifacts exist yet.
- Why blocked in ChatGPT Project Mode: Real evidence artifacts require external runners, scanners, sandboxes, live provider test environments, private evidence storage, and human release/AppSec execution that are unavailable inside ChatGPT Project Mode.
- Risk level: High
- Dependency requirements: Completed Phase 11 handoff task execution, approved private evidence directory, artifact naming that matches the Phase 11 evidence template, and Phase 12 ledger commands.
- Exact future validation required: Place reviewed/redacted artifacts under `validation_evidence/`, run `bountyclaw validation-evidence ledger --root . --evidence-dir validation_evidence --json`, archive SHA-256 hashes, and verify every produced artifact maps to expected handoff tasks and gap IDs.
- Exact future tooling/environment required: Codex/local/CI workspace, private artifact storage, Python 3.12+, generated validation artifacts from hosted CI/package/scanner/model/MCP/browser/report/operations/release tasks.
- Recommended future agent type: Release evidence automation agent with AppSec oversight.
- Estimated production impact: High; evidence traceability is required before credible production-readiness claims.
- Completion criteria: Ledger output lists real artifact hashes, zero unexpected artifact paths are needed for claimed closures, and evidence metadata is archived privately with human-reviewed redaction status.
- Rollback considerations: If ledger output references unsafe, missing, or mismatched artifacts, quarantine those artifacts and leave all affected production gaps open.

### PGT-101

- Unique ID: PGT-101
- Phase association: Phase 12
- Subsystem association: Evidence Review and Redaction Approval
- Description: Perform human release/AppSec review of evidence artifacts before any production gap is closed or readiness percentage is raised.
- Why incomplete: Phase 12 hashes artifacts and maps them to gaps but intentionally does not inspect raw contents, approve redaction, validate provenance, or close gaps.
- Why blocked in ChatGPT Project Mode: Human review requires private artifact access, release authority, AppSec judgment, and potentially confidential CI/security/scanner/model logs.
- Risk level: High
- Dependency requirements: PGT-100 ledger execution, private evidence storage, artifact provenance records, redaction policy, release owner, and AppSec reviewer.
- Exact future validation required: Review each artifact for provenance, timestamp, executor identity or CI URL, tool versions, acceptance criteria, secret/sensitive data exposure, and alignment with the gap completion criteria.
- Exact future tooling/environment required: Private evidence repository or encrypted artifact store, review checklist, release approval workflow, AppSec reviewer, and redaction tooling if raw logs require sanitization.
- Recommended future agent type: Human AppSec reviewer supported by release evidence governance agent.
- Estimated production impact: High; unreviewed evidence could leak secrets or falsely close production gaps.
- Completion criteria: Every artifact used for gap closure has documented human review, redaction approval or rejection, provenance confirmation, and explicit linkage to the related gap IDs.
- Rollback considerations: Reopen any gap and quarantine/remove any artifact if later review finds sensitive leakage, incomplete provenance, or invalid acceptance criteria.

### PGT-102

- Unique ID: PGT-102
- Phase association: Phase 12
- Subsystem association: Evidence-Based Readiness Recalculation
- Description: Close production gaps and recalculate readiness only after reviewed evidence satisfies each gap completion criterion.
- Why incomplete: Phase 12 produces gap-readiness reports but intentionally returns `ready_for_gap_closure=false` and `ready_for_production=false` until external evidence exists and is reviewed.
- Why blocked in ChatGPT Project Mode: Closure requires real validation evidence, private review, human release authority, and final governance updates that cannot be truthfully completed here.
- Risk level: High
- Dependency requirements: Completed PGT-100 ledger execution, completed PGT-101 evidence review, updated `SECURITY_VALIDATION.md`, `RELEASE.md`, `ROLLBACK.md`, and release evidence artifacts.
- Exact future validation required: For each candidate gap, compare evidence against the gap completion criteria, update the gap tracker with artifact hashes and review decisions, mark only satisfied gaps closed, recalculate readiness, and preserve unresolved gaps.
- Exact future tooling/environment required: Governance review workspace, release evidence ledger, private artifact store, deterministic SDLC controller, AppSec reviewer, and human release authority.
- Recommended future agent type: Deterministic SDLC controller with human release authority.
- Estimated production impact: High; production readiness depends on accurate evidence-based closure rather than optimistic local tooling.
- Completion criteria: Closed gaps cite reviewed evidence artifacts, unresolved gaps remain open, readiness percentage is recalculated with rationale, and rollback posture is updated.
- Rollback considerations: Reopen any gap and lower readiness if evidence is incomplete, invalid, sensitive, stale, or contradicted by later validation.

### PGT-103

- Unique ID: PGT-103
- Phase association: Phase 13
- Subsystem association: Evidence Review Decision Execution
- Description: Execute the Phase 13 human evidence-review decision workflow against real Phase 12 evidence artifacts.
- Why incomplete: Phase 13 implements metadata-only review templates and status checks, but no real external artifacts or human review decisions exist inside ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires private artifact access, human release/AppSec judgment, redaction approval, provenance review, and possibly confidential CI/security/scanner/model logs.
- Risk level: High
- Dependency requirements: Completed Phase 11 handoff task execution, completed Phase 12 evidence ledger with real artifact hashes, approved private evidence storage, AppSec reviewer, release owner, and review decision file path.
- Exact future validation required: Produce `validation_evidence/evidence_review_decisions.json` after human review, run `bountyclaw evidence-review status --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`, verify reviewed hashes match the Phase 12 ledger, and archive review metadata.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, private evidence storage, redacted artifact copies, human release/AppSec reviewer, and governance review workspace.
- Recommended future agent type: Human AppSec reviewer supported by deterministic evidence-review agent.
- Estimated production impact: High; evidence cannot safely close gaps without reviewed decisions and hash-bound metadata.
- Completion criteria: Every artifact used for any gap proposal has reviewer identity, reviewed timestamp, matching SHA-256, rationale, redacted artifact reference, and explicit non-inclusion of raw contents.
- Rollback considerations: Reject or quarantine any review decision if hashes mismatch, sensitive content is exposed, provenance is unclear, or reviewer approval is absent.

### PGT-104

- Unique ID: PGT-104
- Phase association: Phase 13
- Subsystem association: Gap Closure Proposal Review
- Description: Use Phase 13 gap-closure proposals to perform manual governance updates for production gaps only after reviewed evidence exists.
- Why incomplete: Phase 13 can draft proposals, but it intentionally does not edit `PRODUCTION_GAP_TRACKER.md`, close gaps, or raise readiness.
- Why blocked in ChatGPT Project Mode: Requires real reviewed evidence, human release authority, governance review, and careful risk/readiness recalculation that cannot be truthfully completed without external artifacts.
- Risk level: High
- Dependency requirements: Completed PGT-100, PGT-101, PGT-102, PGT-103, Phase 13 closure proposal output, `SECURITY_VALIDATION.md`, `RELEASE.md`, `ROLLBACK.md`, and production gap tracker review.
- Exact future validation required: Run `bountyclaw evidence-review closure-proposals --root . --evidence-dir validation_evidence --review-file validation_evidence/evidence_review_decisions.json --json`, compare each proposal to gap completion criteria, manually update only gaps with complete reviewed evidence, and preserve unresolved gaps.
- Exact future tooling/environment required: Governance review workspace, release evidence ledger, private artifact store, deterministic SDLC controller, AppSec reviewer, and human release authority.
- Recommended future agent type: Deterministic SDLC controller with human release authority.
- Estimated production impact: High; accurate production gap closure is required for credible production-readiness claims.
- Completion criteria: Every closed gap cites reviewed artifacts and rationale, every unresolved gap remains open, readiness is recalculated with a written basis, and rollback posture is updated.
- Rollback considerations: Reopen any gap and lower readiness if evidence is incomplete, invalid, sensitive, stale, or contradicted by later validation.

### PGT-105

- Unique ID: PGT-105
- Phase association: Phase 13
- Subsystem association: Evidence Review Handoff Execution
- Description: Execute the updated Phase 11 handoff package containing Phase 12 ledger commands and Phase 13 evidence-review commands in a future Codex/local/CI/human environment.
- Why incomplete: Phase 13 updates handoff package generation with evidence-review commands, but future executors have not exported and executed the updated package against real evidence.
- Why blocked in ChatGPT Project Mode: Requires a persistent repository workspace, external validation artifacts, private evidence storage, and human review authority.
- Risk level: Medium
- Dependency requirements: Phase 13 source bundle, `bountyclaw handoff export`, Phase 12 ledger commands, Phase 13 evidence-review commands, and private evidence review process.
- Exact future validation required: Run `bountyclaw handoff export --root . --output validation_handoff --json`, confirm `EVIDENCE_REVIEW_COMMANDS.md` exists, execute listed Phase 12/13 commands after artifacts exist, and archive command outputs.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, generated validation artifacts, private artifact store, and human AppSec/release review process.
- Recommended future agent type: Codex handoff orchestration agent with AppSec oversight.
- Estimated production impact: Medium; improves deterministic continuation and reduces risk of evidence-review drift.
- Completion criteria: Updated handoff package is exported, evidence-review commands are executed against real reviewed metadata, and results are archived without raw evidence disclosure.
- Rollback considerations: Preserve the Phase 12 ledger-only handoff package if Phase 13 review workflow has defects; do not close gaps until corrected.


### PGT-106

- Unique ID: PGT-106
- Phase association: Phase 14
- Subsystem association: Gap Tracker Governance Execution
- Description: Execute Phase 14 gap tracker audit and Codex backlog export after real external validation, evidence review, and manual gap tracker edits occur.
- Why incomplete: Phase 14 implements local audit/backlog tooling, but no future external validation evidence, human review decisions, or manual gap tracker updates exist yet.
- Why blocked in ChatGPT Project Mode: Requires external Codex/local/CI/human validation outputs, private evidence storage, reviewed evidence decisions, and real governance edits outside ChatGPT Project Mode.
- Risk level: Medium
- Dependency requirements: Completed Phase 11 handoff task execution, completed Phase 12 evidence ledger, completed Phase 13 evidence review decisions, manually updated `PRODUCTION_GAP_TRACKER.md`, and Phase 14 gap tracker commands.
- Exact future validation required: Run `bountyclaw gap-tracker audit --root . --json`, `bountyclaw gap-tracker backlog --root . --json`, and `bountyclaw gap-tracker verify --root . --json` after every manual production gap update; archive command outputs with reviewed evidence.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, private evidence store, reviewed evidence metadata, updated governance files, and human release/AppSec reviewer.
- Recommended future agent type: Deterministic gap governance and Codex orchestration agent.
- Estimated production impact: Medium; without rerunning the audit/backlog after edits, future executors may act on stale or malformed gap data.
- Completion criteria: Phase 14 audit passes against a real externally updated gap tracker, backlog reflects current unresolved gaps, and outputs are archived without raw evidence disclosure.
- Rollback considerations: Revert manual gap tracker edits and rerun Phase 14 audit if malformed entries, duplicate IDs, stale closure claims, or unsupported readiness increases are detected.

### PGT-107

- Unique ID: PGT-107
- Phase association: Phase 14
- Subsystem association: Codex Gap Backlog Execution
- Description: Execute the Codex/local/CI/human backlog derived from unresolved production gaps and keep results synchronized with reviewed evidence.
- Why incomplete: Phase 14 can generate `CODEX-PGT-*` backlog items, but it cannot execute external tasks, validate artifacts, or confirm human-reviewed closure outcomes inside ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires real repository host, CI runners, package build environments, scanner/sandbox/model/MCP/browser tooling, private evidence review, and human release authority.
- Risk level: High
- Dependency requirements: Phase 14 backlog export, Phase 11 handoff plan, Phase 12 evidence ledger, Phase 13 evidence review package, and human-approved task sequencing.
- Exact future validation required: Export the Phase 14 gap tracker package, assign backlog items to appropriate future agents, execute tasks in required environments, attach reviewed evidence to each related `PGT-*` entry, and rerun Phase 14 audit/backlog commands after updates.
- Exact future tooling/environment required: Codex/local/CI execution environment, repository-hosted CI, approved scanners/sandboxes/model/browser/MCP runtimes where applicable, private artifact store, and human release/AppSec reviewers.
- Recommended future agent type: Codex release-validation orchestrator with AppSec oversight.
- Estimated production impact: High; generated backlog is the deterministic bridge from local governance to external production completion.
- Completion criteria: Each executed backlog task has associated reviewed evidence, unresolved tasks remain open, and no gap is closed without matching completion criteria and rollback notes.
- Rollback considerations: Reopen any gap and regenerate backlog if task evidence is incomplete, stale, sensitive, contradictory, or missing human approval.

### PGT-108

- Unique ID: PGT-108
- Phase association: Phase 14
- Subsystem association: Gap Tracker CI and Branch-Protection Enforcement
- Description: Enforce Phase 14 gap tracker audit/backlog verification in hosted CI and branch protection before production gap changes are merged.
- Why incomplete: Phase 14 defines local verification and CI workflow hooks, but no hosted CI run, branch protection rule, required status check, or repository governance enforcement has been configured.
- Why blocked in ChatGPT Project Mode: Requires repository administrator permissions, hosted CI execution, branch/ruleset configuration, and human release governance authority.
- Risk level: High
- Dependency requirements: Real repository host, `.github/workflows/ci.yml`, Phase 14 verifier, branch protection/ruleset policy, and release owner approval.
- Exact future validation required: Run hosted CI with `scripts/phase14_verify.py`, configure the Phase 14 check as required for protected branches, test that malformed gap tracker changes are blocked, and archive repository-rule evidence.
- Exact future tooling/environment required: GitHub/GitLab/etc., hosted or self-hosted CI runner, branch protection/ruleset administration, Python 3.12+, and release manager approval.
- Recommended future agent type: DevSecOps repository governance agent.
- Estimated production impact: High; without enforcement, future gap tracker drift or unsupported readiness claims can enter the repository unchecked.
- Completion criteria: Hosted CI proves Phase 14 verification runs, branch protection requires it, malformed gap tracker fixtures fail, and governance evidence is linked from release/security validation documents.
- Rollback considerations: Disable the required check only if it blocks emergency fixes, preserve manual AppSec review, and restore enforcement after remediation.


### PGT-109

- Unique ID: PGT-109
- Phase association: Phase 15
- Subsystem association: External Validation Runbook Execution
- Description: Execute Phase 15 external validation runbook steps in the required Codex/local/CI/human environments and record metadata-only execution journal entries.
- Why incomplete: Phase 15 implements runbook and journal tooling locally, but no real external executor has run the tasks or produced journal metadata.
- Why blocked in ChatGPT Project Mode: Requires hosted CI runners, local package environments, scanner/sandbox/model/MCP/browser tooling where authorized, private evidence storage, and human release/AppSec oversight that are unavailable in ChatGPT Project Mode.
- Risk level: High
- Dependency requirements: Phase 14 Codex backlog, Phase 15 runbook package, approved execution environments, private evidence storage, and human release/AppSec reviewer.
- Exact future validation required: Run `bountyclaw validation-runbook export --root . --output validation_runbook --json`, execute each runbook step in the required environment, record only task IDs, gap IDs, artifact IDs, SHA-256 hashes, executor metadata, and completion metadata in `validation_runs/execution_journal.json`, then run `bountyclaw validation-runbook journal-status --root . --journal validation_runs/execution_journal.json --json`.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, repository-hosted CI, approved scanners/sandbox tools/model/MCP/browser runtimes where applicable, private artifact storage, and human release/AppSec reviewer.
- Recommended future agent type: Codex external-validation execution orchestrator with AppSec oversight.
- Estimated production impact: High; without real execution journal metadata and artifacts, Phase 12/13/14 workflows cannot close external validation gaps.
- Completion criteria: Every applicable runbook step has a metadata-only journal entry, corresponding private/redacted evidence artifacts exist, artifact hashes match future ledger outputs, and no raw evidence contents are committed.
- Rollback considerations: Discard or quarantine malformed journal entries, preserve Phase 14 backlog and Phase 15 runbook export as the rollback baseline, and rerun runbook generation after correcting stale gap data.

### PGT-110

- Unique ID: PGT-110
- Phase association: Phase 15
- Subsystem association: Execution Journal Governance and Evidence Linkage
- Description: Validate that execution journal metadata links correctly to Phase 12 evidence artifacts, Phase 13 human review decisions, and Phase 14 gap tracker backlog items.
- Why incomplete: Phase 15 can assess journal metadata shape, but no real evidence artifacts or human review decisions exist yet.
- Why blocked in ChatGPT Project Mode: Requires external artifacts, private evidence storage, human review metadata, and gap tracker updates produced after real external validation execution.
- Risk level: High
- Dependency requirements: Completed PGT-109 runbook execution, populated `validation_runs/execution_journal.json`, Phase 12 evidence artifacts, Phase 13 review decisions, and Phase 14 gap tracker audit/backlog reruns.
- Exact future validation required: Compare journal artifact IDs and SHA-256 hashes to Phase 12 ledger outputs, confirm Phase 13 review decisions match the same hashes, confirm gap IDs map to unresolved `PGT-*` entries, and archive metadata-only verification outputs.
- Exact future tooling/environment required: Codex/local/CI workspace, `validation_runs/execution_journal.json`, `validation_evidence/` artifact directory, `validation_evidence/evidence_review_decisions.json`, Python 3.12+, and human AppSec/release reviewer.
- Recommended future agent type: Evidence linkage governance agent.
- Estimated production impact: High; prevents stale, mismatched, or unverifiable execution metadata from being used to justify gap closure.
- Completion criteria: Journal status, Phase 12 ledger, Phase 13 review status, and Phase 14 gap tracker audit all agree on task IDs, gap IDs, artifact IDs, and SHA-256 hashes without raw evidence disclosure.
- Rollback considerations: Reopen or block any closure proposal if journal hashes, evidence ledger hashes, review decisions, or gap IDs diverge.

### PGT-111

- Unique ID: PGT-111
- Phase association: Phase 15
- Subsystem association: Hosted Enforcement of Validation Runbook Governance
- Description: Enforce Phase 15 validation-runbook verification in hosted CI and branch protection before external execution journal or gap tracker changes are merged.
- Why incomplete: Phase 15 defines local verification and CI workflow hooks, but no hosted CI run, branch protection rule, required status check, or repository governance enforcement has been configured.
- Why blocked in ChatGPT Project Mode: Requires repository administrator permissions, hosted CI execution, branch/ruleset configuration, and human release governance authority.
- Risk level: High
- Dependency requirements: Real repository host, `.github/workflows/ci.yml`, `scripts/phase15_verify.py`, branch protection/ruleset policy, and release owner approval.
- Exact future validation required: Run hosted CI with `scripts/phase15_verify.py`, configure the Phase 15 check as required for protected branches, test that raw evidence or auto-closing journal metadata is blocked, and archive repository-rule evidence.
- Exact future tooling/environment required: GitHub/GitLab/etc., hosted or self-hosted CI runner, branch protection/ruleset administration, Python 3.12+, and release manager approval.
- Recommended future agent type: DevSecOps repository governance agent.
- Estimated production impact: High; without enforcement, unsafe journal metadata or unsupported readiness claims can enter the repository unchecked.
- Completion criteria: Hosted CI proves Phase 15 verification runs, branch protection requires it, malformed journal/gap tracker fixtures fail, and governance evidence is linked from release/security validation documents.
- Rollback considerations: Disable the required check only for emergency fixes with manual AppSec review, then restore enforcement after remediation.

### PGT-112

- Unique ID: PGT-112
- Phase association: Phase 16
- Subsystem association: Validation Baseline Manifest and Source Snapshot Binding
- Description: Execute Phase 16 validation-baseline export in the real external validation repository state and require future evidence artifacts to reference the resulting baseline ID.
- Why incomplete: Phase 16 can generate hash-only source baseline metadata locally, but no real external validation run has referenced a baseline ID yet.
- Why blocked in ChatGPT Project Mode: Requires a real repository checkout or commit, hosted/local validation environment, produced external evidence artifacts, and future execution journal metadata outside ChatGPT Project Mode.
- Risk level: High
- Dependency requirements: Phase 16 baseline tooling, Phase 15 runbook execution, Phase 12 evidence ledger, Phase 13 evidence review workflow, Phase 14 gap tracker governance, private evidence storage, and human release/AppSec review.
- Exact future validation required: Run `bountyclaw validation-baseline export --root . --output validation_baseline --json` in the external validation environment, record the baseline ID in execution journal entries and evidence review decisions, and confirm later evidence hashes are bound to the same baseline ID.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, repository checkout or signed source bundle, private evidence storage, and human release/AppSec reviewer.
- Recommended future agent type: Codex validation-baseline and evidence-governance agent.
- Estimated production impact: High; without a source baseline, future evidence may be stale or impossible to tie to the exact code under validation.
- Completion criteria: A baseline manifest and index exist for the external validation source state, all future evidence/journal/review metadata references the same baseline ID, and no raw source or evidence contents are committed.
- Rollback considerations: Regenerate the baseline after reverting to the approved source snapshot if the baseline ID changes unexpectedly or evidence references a stale snapshot.

### PGT-113

- Unique ID: PGT-113
- Phase association: Phase 16
- Subsystem association: Evidence-to-Baseline Binding Governance
- Description: Validate that Phase 12 ledger artifacts, Phase 13 human review decisions, Phase 14 backlog updates, and Phase 15 execution journal entries all reference the Phase 16 baseline ID before any gap closure proposal is accepted.
- Why incomplete: Phase 16 defines the baseline manifest but no real artifact set, journal, review decision file, or gap closure proposal has been produced against it yet.
- Why blocked in ChatGPT Project Mode: Requires real future evidence artifacts, private evidence storage, external execution journal metadata, human review decisions, and manually prepared gap closure proposals.
- Risk level: High
- Dependency requirements: Completed PGT-112, populated `validation_runs/execution_journal.json`, Phase 12 evidence ledger output, Phase 13 evidence review decisions, Phase 14 gap tracker audit/backlog rerun, and human AppSec/release review.
- Exact future validation required: Compare baseline IDs across validation baseline export, execution journal entries, evidence ledger metadata, evidence review decisions, closure proposals, and gap tracker updates; reject any item with a missing or mismatched baseline ID.
- Exact future tooling/environment required: Codex/local/CI workspace, Python 3.12+, validation baseline package, validation journal metadata, validation evidence directory, evidence review decision file, and human AppSec/release reviewer.
- Recommended future agent type: Evidence integrity and release-governance agent.
- Estimated production impact: High; baseline mismatch could lead to unsafe or incorrect production readiness claims.
- Completion criteria: All evidence and closure metadata references one reviewed baseline ID, mismatches fail verification, and manual gap updates include the approved baseline reference.
- Rollback considerations: Quarantine mismatched artifacts and reopen any proposed closure until evidence is regenerated against the approved baseline.

### PGT-114

- Unique ID: PGT-114
- Phase association: Phase 16
- Subsystem association: Hosted Enforcement of Validation Baseline Governance
- Description: Enforce Phase 16 validation-baseline verification in hosted CI and branch protection before external evidence, execution journals, review decisions, or gap tracker closure updates are merged.
- Why incomplete: Phase 16 defines local verification and a CI workflow hook, but no hosted CI run, required status check, branch protection rule, or repository governance rule has been configured.
- Why blocked in ChatGPT Project Mode: Requires repository administrator permissions, hosted CI execution, branch/ruleset configuration, and human release-governance authority.
- Risk level: High
- Dependency requirements: Real repository host, `.github/workflows/ci.yml`, `scripts/phase16_verify.py`, branch protection/ruleset policy, release owner approval, and Phase 16 baseline workflow adoption.
- Exact future validation required: Run hosted CI with `scripts/phase16_verify.py`, configure the Phase 16 check as required for protected branches, test that missing baseline files or stale version metadata fail, and archive repository-rule evidence.
- Exact future tooling/environment required: GitHub/GitLab/etc., hosted or self-hosted CI runner, branch protection/ruleset administration, Python 3.12+, and release manager approval.
- Recommended future agent type: DevSecOps repository governance agent.
- Estimated production impact: High; without hosted enforcement, evidence or gap updates may be merged without source-baseline integrity.
- Completion criteria: Hosted CI proves Phase 16 verification runs, branch protection requires it, malformed baseline fixtures fail, and governance evidence is linked from release/security validation documents.
- Rollback considerations: Disable the required check only for emergency fixes with manual AppSec review, then restore enforcement after remediation.

### PGT-115

- Unique ID: PGT-115
- Phase association: Phase 17
- Subsystem association: Closure Gate and Readiness Attestation Governance
- Description: Execute Phase 17 closure-gate assessment against real baseline-bound validation metadata and human readiness attestations.
- Why incomplete: Phase 17 implements templates, metadata checks, export, and verifier logic only; no real external validation evidence, execution journal, review decisions, or readiness attestations exist in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires external validation artifacts, private evidence storage, human AppSec/release review, and approved readiness attestation metadata produced outside this environment.
- Risk level: High
- Dependency requirements: Completed Phase 16 baseline export, Phase 15 execution journal, Phase 12 evidence ledger, Phase 13 evidence-review decisions, Phase 14 gap tracker audit/backlog, and reviewed external validation evidence.
- Exact future validation required: Run `bountyclaw closure-gate status` with real `validation_evidence/readiness_attestations.json`, verify baseline IDs and SHA-256 references, confirm candidate gaps are only manual-update candidates, and archive closure-gate output.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, reviewed validation artifacts, metadata-only execution journal, metadata-only evidence-review decisions, and human AppSec/release reviewer authority.
- Recommended future agent type: Release governance / AppSec review agent.
- Estimated production impact: High; prevents unreviewed external validation metadata from being converted into production-readiness claims.
- Completion criteria: Closure-gate status runs against real reviewed metadata, reports no schema/hash/baseline blockers for intended manual gap-update candidates, and records `ready_for_gap_closure=false` until human governance updates are manually applied.
- Rollback considerations: Discard readiness attestation metadata and return to Phase 16 baseline-bound evidence workflow if closure-gate checks fail or artifact references are inconsistent.

### PGT-116

- Unique ID: PGT-116
- Phase association: Phase 17
- Subsystem association: Manual Gap Closure Governance
- Description: Perform human review of Phase 17 closure-gate candidates before any production gap closure or readiness recalculation.
- Why incomplete: Phase 17 can identify metadata candidates but cannot perform human AppSec/release acceptance, update governance files, or recalculate production readiness.
- Why blocked in ChatGPT Project Mode: Requires accountable human review of private evidence, organizational release approval, rollback acceptance, and manual governance-file updates in a real repository workflow.
- Risk level: High
- Dependency requirements: Completed PGT-115, human-reviewed evidence artifacts, matching baseline ID, matching execution journal hashes, matching evidence-review decision hashes, matching gap tracker hash, and release owner approval.
- Exact future validation required: Human reviewer must compare closure-gate candidate gap IDs with private reviewed evidence, verify rollback notes and completion criteria, approve or reject each candidate, then manually update `PRODUCTION_GAP_TRACKER.md` with evidence references only for approved gaps.
- Exact future tooling/environment required: Private evidence review environment, repository branch/PR workflow, AppSec/release approval process, hosted CI, and protected governance-file review.
- Recommended future agent type: Human AppSec/release reviewer assisted by deterministic governance agent.
- Estimated production impact: High; prevents premature or unsupported production gap closure.
- Completion criteria: Every gap closure has human approval, evidence references, baseline ID, rollback considerations, updated readiness calculation, passing gap-tracker audit, and reviewed PR history.
- Rollback considerations: Reopen manually closed gaps and revert readiness percentage if evidence review, baseline linkage, or rollback criteria are later found invalid.

### PGT-117

- Unique ID: PGT-117
- Phase association: Phase 17
- Subsystem association: Hosted Enforcement of Closure Gate
- Description: Enforce Phase 17 closure-gate verification in hosted CI and branch protection before readiness-attestation or gap-closure updates are merged.
- Why incomplete: Phase 17 updates the CI workflow definition locally, but hosted CI and branch protection have not run or been configured in this environment.
- Why blocked in ChatGPT Project Mode: Requires repository-host administration, branch protection settings, hosted runner execution, and release-owner policy decisions outside ChatGPT Project Mode.
- Risk level: High
- Dependency requirements: Real repository host, hosted CI runner, branch protection policy, Phase 17 verifier command, gap tracker audit command, and human release approval.
- Exact future validation required: Run hosted CI with `python scripts/phase17_verify.py --root .`, require it as a protected status check, and prove readiness-attestation/gap-tracker PRs cannot merge when closure-gate or gap-tracker verification fails.
- Exact future tooling/environment required: GitHub/GitLab/Bitbucket or equivalent repository host, protected branches, CI secrets policy, Python 3.12+ runner, and release-engineering admin access.
- Recommended future agent type: DevSecOps release-governance agent.
- Estimated production impact: High; ensures closure-gate governance is enforced rather than advisory.
- Completion criteria: Hosted CI evidence shows Phase 17 verification passing, branch protection requires it, failure-mode tests block merge, and enforcement evidence is linked in `PRODUCTION_GAP_TRACKER.md`.
- Rollback considerations: Temporarily remove Phase 17 as a required check only through emergency release governance if verifier defects block urgent fixes, then restore enforcement after remediation.


### PGT-118

- Unique ID: PGT-118
- Phase association: Phase 18
- Subsystem association: Readiness Dashboard External Execution
- Description: Execute Phase 18 readiness-dashboard exports in the real external validation repository state and use the dashboard as the authoritative operator index for Phase 11 through Phase 17 validation workflows.
- Why incomplete: Phase 18 implements local dashboard, index, export, verifier, and handoff command updates only; no real external validation workspace has executed the dashboard package.
- Why blocked in ChatGPT Project Mode: Requires a real repository checkout, Codex/local/CI executor, external validation artifacts, and human review state that do not exist inside ChatGPT Project Mode.
- Risk level: Medium
- Dependency requirements: Completed Phase 18 bundle, real repository checkout, Phase 16 baseline export, Phase 11 handoff package, Phase 15 runbook package, Phase 12 evidence ledger package, Phase 13 review package, Phase 14 gap tracker package, and Phase 17 closure-gate package.
- Exact future validation required: Run `bountyclaw readiness-dashboard export --root . --output readiness_dashboard_package --json` and `bountyclaw readiness-dashboard verify --root . --json` in the external validation environment, archive dashboard outputs, and link artifact hashes to the validation evidence ledger.
- Exact future tooling/environment required: Codex/local/CI workspace with Python 3.12+, repository checkout, private validation evidence storage, and access to produced Phase 11 through Phase 17 governance artifacts.
- Recommended future agent type: Codex release-governance orchestration agent.
- Estimated production impact: Medium; improves external executor coordination and reduces handoff drift but does not itself validate runtime production readiness.
- Completion criteria: External dashboard package exists, command index matches the current baseline and runbook artifacts, verifier passes in the external workspace, and hashes are recorded in the evidence ledger.
- Rollback considerations: Discard Phase 18 dashboard artifacts and fall back to Phase 17 closure-gate plus Phase 15 runbook outputs if dashboard commands or index metadata are inconsistent.

### PGT-119

- Unique ID: PGT-119
- Phase association: Phase 18
- Subsystem association: Dashboard-to-Gap Tracker Synchronization
- Description: Validate that Phase 18 dashboard gap counts, high-risk summary, and external executor index remain synchronized with `PRODUCTION_GAP_TRACKER.md` after real evidence review and manual gap updates.
- Why incomplete: Phase 18 can read the current gap tracker locally, but no real external evidence review or manual gap closure updates have occurred.
- Why blocked in ChatGPT Project Mode: Requires human-reviewed evidence artifacts, manual governance-file edits in a repository workflow, rerun Phase 14 gap audit/backlog, and release-owner approval.
- Risk level: High
- Dependency requirements: Completed PGT-118, human-reviewed evidence decisions, Phase 14 gap tracker audit/backlog rerun, Phase 17 closure-gate candidate review, and manual updates to `PRODUCTION_GAP_TRACKER.md`.
- Exact future validation required: After any manual gap tracker update, rerun Phase 14, Phase 17, and Phase 18 verifiers, compare dashboard gap counts and high-risk summaries to the gap tracker, and attach the verifier outputs to the evidence ledger.
- Exact future tooling/environment required: Protected repository branch, hosted CI, Codex/local governance agent, human AppSec/release reviewer, and private evidence storage.
- Recommended future agent type: Governance consistency agent with human AppSec reviewer.
- Estimated production impact: High; prevents stale dashboards from misleading future readiness and closure decisions.
- Completion criteria: Dashboard, gap tracker audit, closure gate, and runbook outputs agree after manual updates; hosted CI enforces Phase 18 verification; human reviewer approves the synchronization evidence.
- Rollback considerations: Revert manual gap tracker changes and dashboard artifacts if counts or risk summaries diverge from reviewed evidence.

### PGT-120

- Unique ID: PGT-120
- Phase association: Phase 18
- Subsystem association: Hosted Enforcement of Readiness Dashboard
- Description: Enforce Phase 18 readiness-dashboard verification in hosted CI and branch protection before handoff, evidence, runbook, closure-gate, or gap tracker governance changes are merged.
- Why incomplete: Phase 18 updates the CI workflow definition locally, but hosted CI and branch protection have not run or been configured in this environment.
- Why blocked in ChatGPT Project Mode: Requires repository-host administration, hosted CI runner execution, branch protection settings, and release-owner policy decisions outside ChatGPT Project Mode.
- Risk level: High
- Dependency requirements: Real repository host, hosted CI runner, branch protection policy, Phase 18 verifier command, Phase 14 gap tracker verifier, Phase 17 closure-gate verifier, and human release approval.
- Exact future validation required: Run hosted CI with `python scripts/phase18_verify.py --root .`, require it as a protected status check, and prove governance-change PRs cannot merge when Phase 18 dashboard verification fails.
- Exact future tooling/environment required: GitHub/GitLab/Bitbucket or equivalent repository host, protected branches, CI runner, Python 3.12+, and release-engineering admin access.
- Recommended future agent type: DevSecOps release-governance agent.
- Estimated production impact: High; ensures the external executor dashboard remains enforced rather than advisory.
- Completion criteria: Hosted CI evidence shows Phase 18 verification passing, branch protection requires it, failure-mode tests block merge, and enforcement evidence is linked in `PRODUCTION_GAP_TRACKER.md`.
- Rollback considerations: Temporarily remove Phase 18 as a required check only through emergency release governance if verifier defects block urgent fixes, then restore enforcement after remediation.

### PGT-121

- Unique ID: PGT-121
- Phase association: Phase 19
- Subsystem association: Dependency Audit / Supply Chain Security
- Description: Complete `pip-audit` dependency vulnerability scanning after Phase 19 local gate remediation.
- Status: Completed in a clean isolated virtual environment.
- Why incomplete: Environment-only `bountyclaw` remains unauditable because it is not published on PyPI in this checkout.
- Why blocked in ChatGPT Project Mode: Requires package-distribution or hosted CI artifact evidence flow for `bountyclaw` before this can be formally closed.
- Risk level: High
- Dependency requirements: Phase 19 quality gate tooling, dependency metadata, approved advisory database access, and reviewed evidence storage.
- Exact future validation required: Reconcile this executed result in `validation_evidence/` through Phase 12–17 evidence workflows and obtain release governance acceptance for the local-package audit limitation.
- Exact future tooling/environment required: Hosted CI or local/Codex environment with project-build artifact publication, `pip-audit`, private evidence storage, and human evidence review.
- Recommended future agent type: Supply-chain security agent.
- Estimated production impact: High; dependency vulnerability visibility is required before production release claims.
- Completion criteria: Reviewed evidence shows `pip-audit` executed, third-party dependency vulnerabilities are tracked, and release governance accepts the local-package audit limitation or project-distributed package audit replacement.
- Rollback considerations: If dependency audit reveals blocking vulnerabilities, halt release, keep Phase 19 local gates as baseline, remediate dependencies or pin safe versions, then rerun all quality/security gates.

### PGT-122

- Unique ID: PGT-122
- Phase association: Phase 19
- Subsystem association: Hosted CI and Branch Protection for Quality Gates
- Description: Enforce Phase 19 local quality/security gates in hosted CI and protected branch rules.
- Why incomplete: Phase 19 updates the CI workflow definition locally, but hosted CI and branch protection were not executed or configured in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires repository-host administration, hosted CI runner execution, protected branch/ruleset configuration, and release-owner approval.
- Risk level: High
- Dependency requirements: Real repository host, committed Phase 19 workflow, hosted CI runners, branch protection/rulesets, and release governance.
- Exact future validation required: Run hosted CI for Phase 19 gates, require the checks in branch protection, and prove failing ruff/mypy/Bandit/tests/package gates block merges.
- Exact future tooling/environment required: GitHub/GitLab/Bitbucket or equivalent, CI runners, Python 3.12/3.13, repository admin access, and branch protection configuration rights.
- Recommended future agent type: DevSecOps release-engineering agent.
- Estimated production impact: High; local gates are not sufficient unless enforced in shared repository workflows.
- Completion criteria: Hosted CI evidence shows Phase 19 gates pass, branch protection requires them, failure-mode tests block merge, and reviewed evidence is linked in governance files.
- Rollback considerations: If Phase 19 CI gates cause false positives, revert only the failing gate configuration through release governance while preserving local verifier and remediation evidence.

### PGT-123

- Unique ID: PGT-123
- Phase association: Phase 19
- Subsystem association: Quality Gate Evidence Review and Gap Closure
- Description: Attach Phase 19 quality/security gate evidence to the Phase 12-17 evidence, review, closure, and gap tracker governance workflow before closing related quality/security gaps.
- Why incomplete: Phase 19 records local gate results, but human AppSec/release review and evidence-based gap closure were not performed in ChatGPT Project Mode.
- Why blocked in ChatGPT Project Mode: Requires private evidence artifact storage, human AppSec/release review, hosted CI evidence, dependency-audit completion, and manual governance updates.
- Risk level: Medium
- Dependency requirements: Completed PGT-121 and PGT-122 where applicable, Phase 12 validation-evidence ledger, Phase 13 evidence-review decisions, Phase 17 closure gate, and Phase 14 gap tracker audit.
- Exact future validation required: Store Phase 19 quality/security gate logs under `validation_evidence/`, hash them through Phase 12, review them through Phase 13, assess readiness through Phase 17, and manually update `PRODUCTION_GAP_TRACKER.md` with reviewed evidence and rollback notes.
- Exact future tooling/environment required: Codex/local/CI workspace, private evidence storage, AppSec/release reviewer, Phase 12-17 CLI workflows, and protected repository branch.
- Recommended future agent type: Release evidence governance agent with human AppSec reviewer.
- Estimated production impact: Medium; prevents local gate claims from being treated as production gap closures without reviewed evidence.
- Completion criteria: Reviewed Phase 19 evidence artifacts are linked to relevant gaps, closure proposals are approved by a human reviewer, and gap tracker readiness is recalculated only after governance updates.
- Rollback considerations: Reopen any gap closed on invalidated gate evidence, revert readiness changes, and preserve the Phase 19 bundle as the last known local validation baseline.

# Highest-Risk Remaining Gaps

1. PGT-121 / PGT-122 / PGT-123: Dependency audit execution is now run locally in an isolated environment, but hosted enforcement, reviewed evidence handoff, and manual closure steps remain incomplete.
2. PGT-118 / PGT-119 / PGT-120: Phase 18 readiness-dashboard tooling is locally ready, but real external dashboard execution, dashboard-gap synchronization, hosted enforcement, and reviewed manual updates are not complete.
2. PGT-115 / PGT-116 / PGT-117: Phase 17 closure-gate tooling is locally ready, but real readiness attestations, human manual gap-closure approval, hosted enforcement, and reviewed production readiness recalculation are not complete.
2. PGT-112 / PGT-113 / PGT-114: Phase 16 validation-baseline tooling is locally ready, but real source-baseline-bound evidence, metadata linkage, hosted enforcement, and manually reviewed gap updates are not complete.
3. PGT-109 / PGT-110 / PGT-111: Phase 15 runbook tooling is locally ready, but real runbook execution, journal metadata, evidence linkage, hosted enforcement, and manually reviewed gap updates are not complete.
4. PGT-106 / PGT-107 / PGT-108: Phase 14 gap tracker tooling is locally ready, but real external validation execution, backlog execution, hosted enforcement, and manually reviewed gap updates are not complete.
5. PGT-103 / PGT-104 / PGT-105: Phase 13 evidence-review tooling is locally ready, but real human review decisions, manual gap updates, and updated handoff execution are not complete.
6. PGT-100 / PGT-101 / PGT-102: Phase 12 evidence-ledger tooling is locally ready, but real artifact production, human evidence review, and evidence-based gap closure are not complete.
7. PGT-097 / PGT-098 / PGT-099: Phase 11 handoff is locally ready, but future execution evidence, evidence storage, and evidence-based gap closure are not complete.
8. PGT-018 / PGT-083 / PGT-088: Hosted CI workflow execution is defined but not run on a real repository runner.
9. PGT-084 / PGT-085 / PGT-086 / PGT-089 / PGT-096: Clean package install, artifact signing/provenance, package publishing dry run, branch protection, and release governance are not validated.
10. PGT-091: External scanner binaries and OS/container scanner sandboxing are not validated.
11. PGT-092: Live provider/no-secret payload/model-output safety validation is not complete.
12. PGT-093: Real MCP/browser runtimes and sandbox/egress controls are not validated.
13. PGT-014 / PGT-015 / PGT-049 / PGT-072: Redaction, prompt-injection, model-output, MCP-output, and browser-output safety need broader adversarial/live evaluation beyond deterministic fixtures.
14. PGT-094 / PGT-063 / PGT-065: Real bounty-program report quality, human review, and manual submission controls remain unvalidated.
15. PGT-095 / PGT-080: Operational performance, retention, backup/restore, export/delete, and rollback drills are not validated.
16. PGT-031: Scope-gate integration coverage for future dependency/advisory, live-provider, real MCP/browser, platform, and deployment subsystems remains critical.
17. PGT-026 / PGT-065: Human authorization, review, and manual submission remain mandatory and cannot be automated away.

# Recommended Next Production Phase

Post-Phase 19 External Production Completion, Quality-Gate-Enforced Dashboard-Guided Source-Baseline-Bound Evidence Production, Validation Runbook Execution, Evidence Review, Gap Tracker Backlog Execution, Closure-Gate Readiness Attestation, Readiness Dashboard Synchronization, and Manual Gap Closure.

Recommended next action:

1. Preserve the Phase 19 quality-gates bundle, Phase 18 readiness-dashboard bundle, Phase 17 closure-gate bundle, Phase 16 validation-baseline bundle, Phase 15 runbook bundle, Phase 14 gap tracker bundle, Phase 13 review bundle, Phase 12 ledger bundle, Phase 11 handoff bundle, and Phase 10 local hardening baseline as rollback-safe artifacts.
2. Run `bountyclaw handoff export --root . --output validation_handoff --json`, then execute hosted CI, release-grade clean install reproduction, packaging, and static/security gates in a real Codex/local/CI environment.
3. Run external scanner, sandbox/egress, MCP/browser, live-provider, redaction, prompt-safety, report-quality, performance, retention, backup/restore, and rollback validations where applicable.
4. Store produced artifacts under `validation_evidence/`, run Phase 12 validation-evidence commands, create human-reviewed `validation_evidence/evidence_review_decisions.json`, then run Phase 13 evidence-review status, closure-proposals, and export-package commands, then run Phase 14 gap-tracker audit/backlog/export/verify commands, then run Phase 15 validation-runbook build/export/verify commands, then run Phase 16 validation-baseline manifest/export/verify commands, record the baseline ID in future evidence metadata, then run Phase 17 closure-gate attestation-template/status/export/verify commands after human readiness attestations are prepared, then run Phase 19 quality-gates checklist/export/verify commands and Phase 18 readiness-dashboard build/handoff-index/export/verify commands to synchronize the operator index before any manual gap updates are merged.
5. Configure branch protection, signing/provenance, package publishing dry run, and release governance only with human release approval.
6. Do not claim production deployment, live provider readiness, external scanner readiness, signing/provenance, package publishing, human evidence review, closure-gate acceptance, gap closure, baseline-bound evidence acceptance, runbook execution, journal acceptance, readiness increase, or enterprise readiness unless actually validated with reviewed evidence and manual governance updates.
7. Update this gap tracker with closure evidence for every completed handoff/review task, rerun Phase 14 gap-tracker audit/backlog verification, and do not close any gap without reviewed evidence, human approval, and rollback notes.
