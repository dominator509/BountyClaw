"""Built-in Python static scanner adapter.

This adapter performs a small deterministic AST-based pass for high-signal local
code-risk patterns. It does not execute target code, import target modules,
persist source contents, access networks, or include raw source excerpts in
findings.
"""

from __future__ import annotations

import ast
import hashlib
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from bountyclaw.repository.intake import IGNORED_DIRECTORIES

from .models import PreliminaryFinding, ScannerContext, ScannerSpec

SCANNER_ID = "builtin.python.static"
SCANNER_VERSION = "0.3.0"


@dataclass(frozen=True)
class RuleDefinition:
    """Static rule metadata used to normalize findings."""

    rule_id: str
    title: str
    description: str
    severity: str
    confidence: str
    cwe: str | None
    remediation_hint: str


RULES: dict[str, RuleDefinition] = {
    "python.eval-call": RuleDefinition(
        rule_id="python.eval-call",
        title="Use of eval detected",
        description="eval can execute attacker-controlled Python code when reachable with untrusted input.",
        severity="high",
        confidence="medium",
        cwe="CWE-95",
        remediation_hint="Replace eval with explicit parsing, allowlisted dispatch, or safe literal parsing where appropriate.",
    ),
    "python.exec-call": RuleDefinition(
        rule_id="python.exec-call",
        title="Use of exec detected",
        description="exec can execute attacker-controlled Python code when reachable with untrusted input.",
        severity="high",
        confidence="medium",
        cwe="CWE-95",
        remediation_hint="Avoid exec; use explicit control flow or constrained interpreters with strict input validation.",
    ),
    "python.subprocess-shell-true": RuleDefinition(
        rule_id="python.subprocess-shell-true",
        title="Subprocess invoked with shell=True",
        description="shell=True can enable command injection when command strings include untrusted input.",
        severity="high",
        confidence="high",
        cwe="CWE-78",
        remediation_hint="Pass argument lists with shell=False and validate any user-controlled arguments.",
    ),
    "python.os-system": RuleDefinition(
        rule_id="python.os-system",
        title="os.system command execution detected",
        description="os.system can enable command injection when command strings include untrusted input.",
        severity="high",
        confidence="medium",
        cwe="CWE-78",
        remediation_hint="Use subprocess with argument lists, shell=False, and explicit input validation.",
    ),
    "python.pickle-load": RuleDefinition(
        rule_id="python.pickle-load",
        title="Pickle deserialization detected",
        description="pickle load operations can execute code when deserializing attacker-controlled data.",
        severity="high",
        confidence="medium",
        cwe="CWE-502",
        remediation_hint="Avoid pickle for untrusted data; use safe formats such as JSON with schema validation.",
    ),
    "python.yaml-load-unsafe": RuleDefinition(
        rule_id="python.yaml-load-unsafe",
        title="Potentially unsafe YAML loading detected",
        description="yaml.load without a safe loader may construct arbitrary Python objects from untrusted input.",
        severity="medium",
        confidence="medium",
        cwe="CWE-502",
        remediation_hint="Use yaml.safe_load or pass SafeLoader explicitly when processing untrusted YAML.",
    ),
    "python.tempfile-mktemp": RuleDefinition(
        rule_id="python.tempfile-mktemp",
        title="Insecure temporary filename generation detected",
        description="tempfile.mktemp can create race conditions because the file is not opened atomically.",
        severity="low",
        confidence="high",
        cwe="CWE-377",
        remediation_hint="Use tempfile.NamedTemporaryFile or tempfile.mkstemp for atomic temporary file creation.",
    ),
    "python.hashlib-md5": RuleDefinition(
        rule_id="python.hashlib-md5",
        title="MD5 hashing detected",
        description="MD5 is collision-prone and unsafe for security-sensitive integrity or password use cases.",
        severity="low",
        confidence="medium",
        cwe="CWE-327",
        remediation_hint="Use SHA-256 or a password-specific hashing function depending on context.",
    ),
}


class BuiltInPythonStaticAdapter:
    """Small deterministic Python static scanner."""

    @property
    def spec(self) -> ScannerSpec:
        return ScannerSpec(
            scanner_id=SCANNER_ID,
            name="Built-in Python static pattern scanner",
            version=SCANNER_VERSION,
            adapter_family="builtin.static.python",
            execution_mode="local_builtin",
        )

    def supports(self, context: ScannerContext) -> bool:
        return any(_iter_python_files(context.repository_root))

    def scan(self, context: ScannerContext) -> list[PreliminaryFinding]:
        findings: list[PreliminaryFinding] = []
        for path in _iter_python_files(context.repository_root):
            if path.stat().st_size > context.max_file_bytes:
                continue
            relative_path = path.relative_to(context.repository_root).as_posix()
            try:
                source = path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source, filename=relative_path)
            except SyntaxError:
                continue

            import_index = _ImportIndex.from_tree(tree)
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                rule = _match_call_rule(node, import_index)
                if rule is None:
                    continue
                findings.append(_finding_for_rule(rule, context, relative_path, node.lineno))

        findings.sort(key=lambda item: (item.file_path, item.line_number or 0, item.rule_id))
        return findings


@dataclass(frozen=True)
class _ImportIndex:
    """Map local import aliases to fully qualified names for call matching."""

    aliases: dict[str, str]

    @classmethod
    def from_tree(cls, tree: ast.AST) -> _ImportIndex:
        aliases: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for imported in node.names:
                    root_name = imported.name.split(".")[0]
                    aliases[imported.asname or root_name] = imported.name
            elif isinstance(node, ast.ImportFrom) and node.module:
                for imported in node.names:
                    aliases[imported.asname or imported.name] = f"{node.module}.{imported.name}"
        return cls(aliases=aliases)

    def expand(self, name: str) -> str:
        return self.aliases.get(name, name)


def _iter_python_files(root: Path) -> Iterable[Path]:
    stack = [root]
    while stack:
        directory = stack.pop()
        entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
        child_dirs: list[Path] = []
        for entry in entries:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if entry.name in IGNORED_DIRECTORIES:
                    continue
                child_dirs.append(entry)
            elif entry.is_file() and entry.suffix.lower() == ".py":
                yield entry
        stack.extend(reversed(child_dirs))


def _match_call_rule(node: ast.Call, import_index: _ImportIndex) -> RuleDefinition | None:
    call_name = _call_name(node.func, import_index)
    if call_name in {"eval", "builtins.eval"}:
        return RULES["python.eval-call"]
    if call_name in {"exec", "builtins.exec"}:
        return RULES["python.exec-call"]
    if call_name == "os.system":
        return RULES["python.os-system"]
    if call_name in {
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
        "subprocess.run",
    } and _keyword_is_true(node, "shell"):
        return RULES["python.subprocess-shell-true"]
    if call_name in {"pickle.load", "pickle.loads"}:
        return RULES["python.pickle-load"]
    if call_name == "yaml.load" and not _yaml_load_uses_safe_loader(node, import_index):
        return RULES["python.yaml-load-unsafe"]
    if call_name == "tempfile.mktemp":
        return RULES["python.tempfile-mktemp"]
    if call_name == "hashlib.md5":
        return RULES["python.hashlib-md5"]
    return None


def _call_name(expr: ast.expr, import_index: _ImportIndex) -> str:
    if isinstance(expr, ast.Name):
        return import_index.expand(expr.id)
    if isinstance(expr, ast.Attribute):
        parent = _call_name(expr.value, import_index)
        return f"{parent}.{expr.attr}"
    return "<dynamic>"


def _keyword_is_true(node: ast.Call, name: str) -> bool:
    for keyword in node.keywords:
        if keyword.arg == name and isinstance(keyword.value, ast.Constant):
            return keyword.value.value is True
    return False


def _yaml_load_uses_safe_loader(node: ast.Call, import_index: _ImportIndex) -> bool:
    loader_names = {"yaml.SafeLoader", "yaml.CSafeLoader", "SafeLoader", "CSafeLoader"}
    for keyword in node.keywords:
        if keyword.arg == "Loader":
            return _call_name(keyword.value, import_index) in loader_names
    if len(node.args) >= 2:
        return _call_name(node.args[1], import_index) in loader_names
    return False


def _finding_for_rule(
    rule: RuleDefinition,
    context: ScannerContext,
    relative_path: str,
    line_number: int,
) -> PreliminaryFinding:
    stable_source = "|".join(
        [
            context.repository_fingerprint_id,
            SCANNER_ID,
            rule.rule_id,
            relative_path,
            str(line_number),
        ]
    )
    digest = hashlib.sha256(stable_source.encode("utf-8")).hexdigest()[:16]
    return PreliminaryFinding(
        finding_id=f"finding-{digest}",
        scanner_id=SCANNER_ID,
        scanner_version=SCANNER_VERSION,
        rule_id=rule.rule_id,
        title=rule.title,
        description=rule.description,
        severity=rule.severity,  # type: ignore[arg-type]
        confidence=rule.confidence,  # type: ignore[arg-type]
        target=str(context.repository_root),
        file_path=relative_path,
        line_number=line_number,
        evidence_summary=(
            f"Rule {rule.rule_id} matched at {relative_path}:{line_number}; "
            "raw source content was not captured or persisted."
        ),
        cwe=rule.cwe,
        remediation_hint=rule.remediation_hint,
        metadata={"phase": "3", "source_excerpt_policy": "omitted_until_redaction_layer_exists"},
    )
