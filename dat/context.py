"""Stable shared-memory location and specialist technical-context definitions."""
from pathlib import Path
import re
import unicodedata

from .storage import Conflict, read, safe_path

POINTER = ".ai-team/.dat/context-path"
LEGACY_SHARED = ".ai-team/context.md"
LEGACY_PRIVATE = ".ai-team/context.local.md"
PLACEHOLDER = "agents/<project>-context.md"
ROLES = ("team-leader", "software-architect", "ui-ux-designer", "frontend-developer", "backend-developer",
         "database-engineer", "qa-engineer", "security-engineer", "devops-engineer", "code-review-engineer")
ROLE_SECTIONS = {
    "team-leader": ("COORDINATION", "APPROVALS", "DEPENDENCIES", "RECOVERY"),
    "software-architect": ("BOUNDARIES", "TECHNOLOGY_CHOICES", "CONTRACTS", "TRADEOFFS"),
    "ui-ux-designer": ("DESIGN_SYSTEM", "USER_FLOWS", "COMPONENT_STATES", "ACCESSIBILITY"),
    "frontend-developer": ("ROUTES_COMPONENTS", "STATE", "API_CONTRACTS", "BUILD_TESTS"),
    "backend-developer": ("API_CONTRACTS", "BUSINESS_RULES", "AUTHORIZATION", "INTEGRATIONS"),
    "database-engineer": ("SCHEMA", "INVARIANTS", "MIGRATIONS", "QUERIES_RECOVERY"),
    "qa-engineer": ("ACCEPTANCE", "COMMANDS_FIXTURES", "RESULTS", "COVERAGE_GAPS"),
    "security-engineer": ("TRUST_BOUNDARIES", "ACCESS_DATA", "FINDINGS", "VALIDATION"),
    "devops-engineer": ("ENVIRONMENTS", "DELIVERY", "PROVIDERS_COSTS", "OPERATIONS_RECOVERY"),
    "code-review-engineer": ("REVIEW_SCOPE", "CONVENTIONS_CONTRACTS", "FINDINGS", "FOLLOW_UP"),
}


def role_path(role):
    if role not in ROLES:
        raise ValueError("Unknown specialist role")
    return f"agents/contexts/{role}-context.md"


def validate_path(target: Path, value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"agents/[\w][\w.-]*-context\.md", value):
        raise Conflict("Context must be agents/<project>-context.md with no traversal or nested directories.")
    if len(value.encode("utf-8")) > 220:
        raise Conflict("Context path is too long; choose a shorter project name")
    safe_path(target, value)
    return value


def resolve(target: Path, requested=None) -> str:
    recorded = read(target, POINTER)
    if recorded is not None:
        path = validate_path(target, recorded.decode("utf-8").strip())
        if requested is not None and validate_path(target, requested) != path:
            raise Conflict("A different central context is already recorded; preserve and reconcile it before changing paths.")
        return path
    if requested is not None:
        return validate_path(target, requested)
    folder = safe_path(target, "agents")
    if folder.exists() and not folder.is_dir():
        raise Conflict("The project agents path must be a directory")
    candidates = sorted(p.name for p in folder.glob("*-context.md")) if folder.exists() else []
    if len(candidates) > 1:
        raise Conflict("Multiple project context files found; select one with --context-file agents/<project>-context.md.")
    if candidates:
        return validate_path(target, "agents/" + candidates[0])
    name = unicodedata.normalize("NFKD", target.name).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", name).strip("-")[:80].rstrip("-") or "project"
    return validate_path(target, f"agents/{slug}-context.md")
