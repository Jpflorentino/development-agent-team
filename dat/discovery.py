"""Bounded, read-only technology evidence; no network/plugin installation calls."""
import json
import os
from pathlib import Path

SKIP = {".git", ".ai-team", ".codex", ".claude", ".copilot", "node_modules", ".venv", "venv",
        "bin", "obj", "dist", "build", "coverage", ".next", ".wrangler", "__pycache__"}
CONFIGS = {"vercel.json": "Vercel", "wrangler.toml": "Cloudflare", "wrangler.json": "Cloudflare",
           "wrangler.jsonc": "Cloudflare", "netlify.toml": "Netlify", "firebase.json": "Firebase",
           "railway.json": "Railway", "railway.toml": "Railway"}
PACKAGES = {"@vercel/": "Vercel", "@cloudflare/": "Cloudflare", "wrangler": "Cloudflare",
            "@supabase/": "Supabase", "stripe": "Stripe", "@stripe/": "Stripe", "resend": "Resend",
            "vercel": "Vercel", "@aws-sdk/": "AWS", "@azure/": "Azure", "@google-cloud/": "Google Cloud"}


def scan(target: Path, max_files=10000):
    if max_files < 1:
        raise ValueError("Scan limit must be positive")
    if not target.is_dir() or target.is_symlink():
        raise ValueError("Choose an existing project directory")
    evidence, warnings, code_files, inspected = {}, [], 0, 0
    def found(provider, path, kind):
        evidence.setdefault(provider, []).append({"path": path, "basis": kind})
    stop = False
    for folder, dirs, files in os.walk(target, followlinks=False,
                                     onerror=lambda error: warnings.append("Could not inspect a directory; coverage is partial")):
        base = Path(folder)
        dirs[:] = sorted(d for d in dirs if d not in SKIP and not (base / d).is_symlink()
                         and (base / d).relative_to(target).as_posix() not in ("agents/contexts", ".github/agents"))
        for name in sorted(files):
            path = base / name
            relative = path.relative_to(target).as_posix()
            if path.is_symlink() or name.startswith(".env") or name.endswith((".pem", ".key", "-context.md")):
                continue
            inspected += 1
            if inspected > max_files:
                warnings.append("File scan limit reached; coverage is partial")
                stop = True
                break
            if path.suffix in (".py", ".js", ".ts", ".tsx", ".jsx", ".cs", ".go", ".java", ".rs", ".php", ".vue", ".svelte"):
                code_files += 1
            if name in CONFIGS:
                found(CONFIGS[name], relative, "configuration filename; use is not runtime-verified")
            if relative.endswith("supabase/config.toml"):
                found("Supabase", relative, "configuration filename; use is not runtime-verified")
            if name == "package.json":
                if path.stat().st_size > 2_000_000:
                    warnings.append(f"Skipped oversized manifest: {relative}")
                    continue
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    if not isinstance(data, dict):
                        raise ValueError("Manifest is not an object")
                    for group in ("dependencies", "devDependencies", "optionalDependencies"):
                        deps = data.get(group, {})
                        if not isinstance(deps, dict):
                            continue
                        for package in deps:
                            for prefix, provider in PACKAGES.items():
                                if (package.startswith(prefix) if prefix.endswith("/") else package == prefix):
                                    found(provider, relative, f"declared dependency matching {prefix}; not proof of active use")
                except (ValueError, OSError, UnicodeError):
                    warnings.append(f"Could not parse manifest: {relative}")
        if stop:
            break
    return {"application_detected": code_files > 0, "inspected_file_count": min(inspected, max_files),
            "code_file_count": code_files, "warnings": warnings,
            "integration_candidates": [{"provider": provider, "evidence": refs,
                "status": "detected", "catalog_availability": "not_checked", "installed": "not_checked",
                "connected": "not_checked", "installation_authorized": False} for provider, refs in sorted(evidence.items())],
            "limitations": "Dependency/config evidence only. Verify actual use, host catalog, exact identifiers, permissions and consent; no installation/network calls occur."}
