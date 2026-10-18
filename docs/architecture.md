# Architecture

Development Agent Team is a file-based engineering framework with exactly ten canonical roles, native platform adapters, a small maintenance CLI, hybrid context and deterministic orchestration contracts. It needs no custom orchestration server, central database, message broker, web administration application or permanent process.

## Components and boundaries

| Component | Responsibility |
| --- | --- |
| `agents/*.md` | Platform-independent mission, operational behavior, authority, inputs, outputs and acceptance criteria for each role. |
| `agents/catalog.json` | Versioned stable identifiers, names, descriptions, read-only classification, dependencies and canonical definition paths. |
| `adapters/` and `dat/adapters.py` | Translate canonical definitions into supported platform configuration/instructions; document native behavior and fallback limitations. |
| `dat/policy.py` | Deterministic role selection, protocol shape checks, quality-gate checks, correction and recovery contracts. Does not invoke models. |
| `dat/installer.py`, `dat/storage.py` | Managed installation/update/removal, conflict detection, backups/transaction safety and maintenance state. |
| `dat/memory.py` and `templates/` | Hybrid project context, evidence labels, controlled updates, compaction and stale-entry signals. |
| `scripts/dat.py` | Cross-platform command entry point using Python's standard library. |
| `tests/` | Structural, installation, memory, orchestration contract and available integration validation. |
| `docs/`, `examples/` | Operating procedures, compatibility evidence, practical scenarios and limitations. |

The canonical files contain no platform-exclusive invocation commands. Adapters own platform paths, metadata and tool restrictions. Generated definitions should remain derived from the canonical source to avoid divergent role behavior. A generated file is a configuration artifact; only execution in the target runtime demonstrates loading, delegation or tool enforcement.

## Execution model

The user speaks to the Team Leader. The leader reads current project evidence, classifies risk and mode, chooses the smallest useful specialist set and sends explicit assignments. Specialists perform only authorized work and return structured evidence. The leader evaluates every return, routes corrections, integrates changes, executes proportionate checks and communicates the accepted outcome.

Native delegation and parallel execution depend on the actual installed runtime. The framework does not emulate missing runtime APIs by calling a Markdown file an agent. When native delegation is unavailable, one model can perform documented sequential role passes. That fallback is useful for structured work but is not independent review or real parallelism. HIGH and CRITICAL acceptance requires actual independent review under the contract gate.

Independent parallel tasks require settled contracts, exclusive file ownership and real isolation as well as platform concurrency. The leader serializes shared-memory consolidation. Worktrees and isolated directories may reduce collisions; merely naming two branches in one working directory does not isolate concurrent writes.

## Context and recovery

A consumer project uses two context files: `.ai-team/context.md` for shareable technical facts and `.ai-team/context.local.md` for private operational recovery state. Both remain local by default; sharing technical context or agent configuration is explicit. Context contains references, not copied code or conversation transcripts. Neither file stores secrets.

The leader is the single logical writer. Specialists propose updates through `CONTEXT_UPDATES`. The CLI supports cooperating-writer locks and content-hash checks, but an unrelated editor can still modify files. Re-read and reconcile before retrying a stale write. Compact duplicates, preserve approved decisions, and revalidate aged entries against actual code. See [context management](context-management.md).

On a new session or interruption the leader reads context, inspects the current worktree and checks effective authorizations and dependency state. A stored completion claim never substitutes for present verification. No consumer planning documents, per-agent memory files or per-task protocol files are automatically created.

## Safety and quality

Permissions derive from the user and the environment, not from a role or routing helper. Code Review and Security default to read-only and return findings rather than patching them. Native technical restrictions should enforce this boundary where available. Git publication and sensitive operational changes in consumer projects require authorization. See [security](security.md).

Risk-based quality gates combine localized checks, relevant tests, functional validation, independent review, security assessment and operational rollback requirements as needed. Contract tests check routing and response structure; they cannot establish actual agent quality, delegation or platform tool enforcement. The compatibility matrix distinguishes structural generation from executed runtime validation.

## Design tradeoffs and versioning

The design avoids mandatory third-party Python packages, permanent infrastructure and duplicated platform-specific role content. Native configuration and plain context files are inspectable and portable. The tradeoff is that orchestration intelligence and execution remain with the host model/runtime, and some safety properties depend on host enforcement rather than the CLI.

Version `1.0.0` follows Semantic Versioning: incompatible installation/contracts require a major version; compatible capabilities a minor version; corrective changes a patch. Installed state identifies managed files and their version. Updates must preserve customization and report conflicts rather than silently overwrite unknown content. Uninstall removes managed components and retains project memory. See [installation](installation.md) and [orchestration](orchestration.md).
