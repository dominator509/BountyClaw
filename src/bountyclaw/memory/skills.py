"""Built-in non-executing reusable skill templates for Phase 8."""

from __future__ import annotations

from .models import SkillTemplate


def list_skill_templates() -> list[SkillTemplate]:
    """Return deterministic built-in skill templates.

    Templates are intentionally advisory. They never execute scanners, models,
    MCP tools, browser workflows, active validation, or report submission.
    """

    return [
        SkillTemplate(
            skill_id="local-static-triage-draft",
            title="Local static finding triage and draft workflow",
            objective="Collect redacted static findings, record human triage, and produce a non-submitting report draft.",
            required_scope_actions=[
                "repo.read",
                "scan.local_static",
                "findings.write",
                "triage.review",
                "report.draft",
            ],
            workflow_steps=[
                "Run repository inspection and deterministic planning.",
                "Run explicit local static scanner execution if authorized.",
                "Persist canonical redacted findings outside the target repository.",
                "Record human triage before draft generation.",
                "Generate a local report draft marked as non-submitting.",
            ],
            prohibited_capabilities=[
                "network scanning",
                "active exploitation",
                "live model provider calls",
                "MCP/browser runtime use",
                "automated bounty submission",
            ],
            output_artifacts=[
                "canonical findings",
                "redacted evidence",
                "human triage state",
                "markdown report draft",
            ],
            notes=["Each workflow step must be invoked separately and pass the scope gate."],
        ),
        SkillTemplate(
            skill_id="policy-fixture-ingestion",
            title="Local policy fixture ingestion workflow",
            objective="Summarize a local policy file through fixture MCP/browser boundaries without live target contact.",
            required_scope_actions=["mcp.tool.invoke", "browser.policy_ingest"],
            workflow_steps=[
                "Invoke the allowlisted local MCP policy summary fixture.",
                "Ingest the same local policy file through the browser safety boundary.",
                "Compare advisory policy signals manually before changing scope manifests.",
            ],
            prohibited_capabilities=[
                "live MCP server invocation",
                "browser navigation to live targets",
                "policy-based automatic scope expansion",
                "form submission",
            ],
            output_artifacts=["redacted policy summary", "advisory policy signals"],
            notes=["Policy output cannot expand executable scope automatically."],
        ),
        SkillTemplate(
            skill_id="memory-hygiene-review",
            title="Memory hygiene review workflow",
            objective="Review, export, and delete local project memory without retaining secrets or raw evidence.",
            required_scope_actions=["memory.read", "memory.export", "memory.delete"],
            workflow_steps=[
                "List repository-associated memory records.",
                "Export redacted records for human review.",
                "Delete obsolete or overly sensitive memory records after explicit approval.",
            ],
            prohibited_capabilities=[
                "secret retention",
                "scope expansion",
                "tool execution",
                "network access",
            ],
            output_artifacts=["redacted memory export", "memory deletion result"],
            notes=["Memory records are local-only and cannot trigger tools."],
        ),
    ]


def get_skill_template(skill_id: str) -> SkillTemplate | None:
    """Return one built-in template by ID."""

    for template in list_skill_templates():
        if template.skill_id == skill_id:
            return template
    return None
