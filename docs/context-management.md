# Shared and specialist project memory

Each project has shared facts in `agents/<project>-context.md`, for example `agents/homemotion-context.md`, plus eleven technical files in `agents/contexts/<role>-context.md`. Each role reads the shared file and its own context first; other role files are consulted only when relevant. Shared decisions have one authoritative location; technical details stay with their owner and refer back to those decisions.

## Contents, ownership and updates

The shared context covers product goals, requirements, business rules, accepted architecture/stack, cross-domain contracts, integration/deployment/cost decisions, approval scope and references, implementation/test state, issues and recovery. It indexes the technical contexts. The Team Leader is its sole logical writer and owns `agents/contexts/team-leader-context.md`.

Specialist files hold technical paths, boundaries, contracts, conventions, commands/results, risks and recovery for their domain. Their headings are role-specific: Architect records boundaries and technology tradeoffs; Database records schema, invariants and migrations; DevOps records environments, delivery, providers/costs and recovery. Writable specialists own only their assigned technical file. Security, Code Review and Code Optimization remain read-only: they propose findings and the leader saves those notes. Serialize writers to the same role file; a shared directory is not isolation.

Update affected files after user corrections/decisions, accepted work, relevant tests, blockers and phase transitions, and before handoff/session end. Record actual-clock timestamps and source references. Distinguish verified implementation, proposals, documented approval and unknown history. Preserve rationale; organize and deduplicate instead of copying source, full transcripts or secrets. No update is needed just to say nothing changed.

This is an event-driven obligation during agent execution, not a background watcher. Without write access, return unsaved proposals and say they were not saved. ChatGPT attachments are snapshots: shared and relevant specialist documents require manual replacement unless a verified writable connector exists.

Memory provides general context. Inspect task-relevant source/configuration/tests to implement, review or verify facts, or when memory is missing/stale. Current evidence and user corrections outrank stale notes. No completion flag or remembered approval substitutes for actual evidence and authorization.

## Creation and first execution

Project installation/upgrade creates missing shared/role templates and `.ai-team/.dat/onboarding.json` with pending analysis. Templates are not completed context. In an existing application, the first execution analyzes the code and populates domain notes while leaving application behavior unchanged. It records relevant roles, actual participation, evidence and reasoned `not_applicable` roles, then reviews useful host integrations with the user. See the [first-use and integration protocol](onboarding.md).

For a new empty project, start product and architecture discussion instead; do not invent implemented facts to fill templates. Existing architecture is observed state, not proof it was approved. Architecture approval and task execution approval remain separate.

The shared filename defaults to a normalized project folder name; `.ai-team/.dat/context-path` keeps it stable after folder renames. One existing `agents/*-context.md` is reused without overwriting it. With several candidates, select explicitly:

```sh
python3 scripts/dat.py install --platform codex --target /path/to/project --context-file agents/fit-escola-context.md --dry-run
python3 scripts/dat.py install --platform codex --target /path/to/project --context-file agents/fit-escola-context.md
```

Existing `.ai-team/context.md` content is conservatively copied into a missing shared brain without deleting the original. `.ai-team/context.local.md` stays unchanged for sanitized consolidation; agents do not routinely read legacy archives. New installations create no legacy context files. Memory contents are outside adapter ownership hashes, so normal context edits survive updates without ownership conflicts. Uninstall preserves shared/role memories, onboarding/path metadata and privacy exclusions. Global profiles use separate project memory, not one home-directory brain.

## Maintenance commands

```sh
python3 scripts/dat.py memory init --target /path/to/project
python3 scripts/dat.py memory show --target /path/to/project
python3 scripts/dat.py memory add --target /path/to/project --section DECISIONS --text 'Preserve the approved public API contract.' --status APPROVED
python3 scripts/dat.py memory compact --target /path/to/project
python3 scripts/dat.py memory stale --target /path/to/project --days 30
python3 scripts/dat.py onboard scan --target /path/to/project
python3 scripts/dat.py onboard status --target /path/to/project
```

`memory show` returns shared content/path/hash. `memory add --expected-hash HASH` rejects stale cooperating writers; reread and reconcile. These commands maintain shared memory; role notes use the assigned file tools. Compaction removes identical entries without summarizing decisions. Stale detection requests revalidation without deleting facts. Locks and transactional rollback do not prevent unrelated editors from writing files. `--local` only accesses a retained legacy private archive. An `APPROVED` label cannot itself grant approval.

## External task state

The live task manager is authoritative for its current tasks. Shared INTEGRATIONS and leader COORDINATION notes retain the selected board/project, verified capabilities, status mapping, scoped authorization, relevant task references, actual last-sync time and uncertain recovery actions. Read the live backlog on resumption; do not mirror it wholesale or upload private contexts. See [task management](task-management.md).

## Privacy

Installed consumer profiles, shared/role context and `.ai-team/` records stay local. Persistent managed exclusions in root and context ignore files remain after update/uninstall; old `--share-agents` and `--share-context` options are rejected. This policy concerns installed consumer copies: the framework's canonical role definitions remain versioned in its own source repository.

Project install/update and memory initialization check Git-tracked protected artifacts before writing private data. If any are tracked, resolve the reported conflict through reviewed untracking/history actions; the tool never silently changes the Git index or history. Ignore rules alone cannot unpublish tracked files, remove historical remote copies, prevent force-add/manual uploads or provide encryption. Never store credentials or unnecessary personal data, even in ignored files.

Keep task plans in the conversation and durable decisions/results in memory. Do not create separate per-task protocol or progress documents.


The optimization role adds private technical memory at `agents/contexts/code-optimization-engineer-context.md`. Updates migrate existing ten-role onboarding records by preserving prior evidence and adding only this pending domain; see [cleanup and optimization](code-optimization.md#memory-and-upgrades).
