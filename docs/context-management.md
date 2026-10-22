# Context management

The Team Leader consolidates persistent context. Specialists propose updates in `CONTEXT_UPDATES`; concurrent specialists do not rewrite context independently. Repository code, tests and effective configuration remain authoritative. If memory conflicts with them, inspect the discrepancy before proceeding.

Each project uses `.ai-team/context.md` for shareable technical context and `.ai-team/context.local.md` for private operational context. Keep shared context compact, initially around 1,500–3,000 tokens where practical. Record project identity, stack, architecture, components, conventions, constraints, approved decisions, current state, known issues and references to source evidence. Private context may describe local recovery state and environment constraints, but never credentials, API keys, tokens or unnecessary personal information.

```sh
python3 scripts/dat.py memory init --target /path/to/project
python3 scripts/dat.py memory show --target /path/to/project
python3 scripts/dat.py memory add --target /path/to/project --section DECISIONS --text 'Preserve the existing PostgreSQL schema contract.' --status APPROVED
python3 scripts/dat.py memory add --target /path/to/project --section CURRENT_STATE --text 'Validation bug reproduced locally; correction pending.' --status VERIFIED --local
python3 scripts/dat.py memory compact --target /path/to/project
python3 scripts/dat.py memory stale --target /path/to/project --days 30
```

`memory show` returns the content and its hash. Pass that hash as `--expected-hash HASH` when adding an update to reject a stale writer. If rejected, reread the current file, reconcile both changes and retry with the new hash. Cross-process locking prevents cooperating CLI writers from silently colliding. Lock files do not prevent an unrelated editor from writing; use the hash check and the Team Leader's single-writer rule together.

Use explicit evidence labels: `VERIFIED` for inspected evidence, `INFERRED` for reasoned conclusions, `PROPOSED` for recommendations, `APPROVED` for authorized decisions, `IMPLEMENTED` for actual changes, `TESTED` for checks actually run, and `BLOCKED` for a concrete limitation. A CLI label records a statement; it does not prove the statement or grant authorization.

Retain compact approval records with their actual scope: architecture/technologies, task-plan execution, provider/budget, paid resources or deployment, as applicable. Architecture-only approval permits task planning; it does not approve implementation or deployment. Include material choices and the actual authorization reference (for example a dated conversation approval or exposed turn reference). Keep the full plan and specialist progress reports in the conversation. Distinguish approval of choices from implementation and validation evidence. On recovery, an installed profile or code artifact does not establish who made a historical decision or whether an agent received a task; mark missing history unverified rather than reconstructing it as fact.

Compaction removes only identical entry lines within the same section; it does not summarize, truncate or delete approved decisions. Stale detection is an age signal, not proof that a fact is wrong. Recheck older entries against current source files and record meaningful changes. An interrupted session resumes by reading context, inspecting the worktree, checking current authorizations and dependencies, then running relevant checks; it must not trust a previous `completed` claim without evidence.

Initialization keeps both context files local unless sharing is explicitly opted into with `--share-context`. Review shared context before versioning and keep `.ai-team/context.local.md` ignored. Ignore rules do not encrypt files or prevent manual upload. Uninstall preserves memory to support recovery and future sessions. Delete memory only through a deliberate user decision.

Context sharing is a project-wide persistent opt-in. An explicit `--share-context`
on installation or memory initialization survives subsequent default commands and
other platform installs. `.ai-team/.gitignore` retains local context and recovery
backup exclusions even after uninstall. Existing user ignore rules and already
tracked files still require manual inspection before any publication.
