"""Scope validation and authorization gate."""

from .gate import ScopeGate
from .loader import LoadedScopeManifest, load_scope_manifest
from .models import Action, ScopeDecision, ScopeManifest, Target, TargetKind

__all__ = [
    "Action",
    "LoadedScopeManifest",
    "ScopeDecision",
    "ScopeGate",
    "ScopeManifest",
    "Target",
    "TargetKind",
    "load_scope_manifest",
]
