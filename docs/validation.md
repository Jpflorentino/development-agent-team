# Version 1.0.0 validation evidence

Validation date: 18 October 2026. This document separates actual execution from
documented support. It contains only synthetic fixture evidence and sanitized
results. Private host transcripts, account configuration and recovery journals
are deliberately excluded from the repository.

## Implemented and tested

The standard-library Python suite exercises real temporary filesystem operations:
clean/repeated installation; project scope for four adapters; temporary home scope
for the three native adapters; upgrade from a recorded older version; conflict
rejection; customization preservation; dry-run without writes; selective uninstall;
rollback after injected failure; interrupted recovery and conflicting later edits;
project separation; private/shared memory; compare-and-set updates; compaction;
stale signals; privacy after uninstall; and sharing across command order/platforms.

Structural tests cover exactly ten canonical roles, required metadata and sections,
references, native rendering, TOML syntax, YAML-compatible generated metadata,
read-only capability restrictions, and profile size limits. Orchestration and smoke
event-parser tests are deterministic **contract/simulation tests**, not model runs.
They cover minimal selection, all thirteen modes and four risk levels, malformed
delegations/reports, blocked specialists, correction bounds, independent-review
requirements, authorization gates and interruption recovery.

Local environment: macOS, Python 3.12.14. Run:

```sh
python3 scripts/dat.py validate
python3 -m unittest discover -s tests -v
```

Result after the Unicode portability regression: **69 tests passed**, and structural validation returned `errors: []`.

Independent read-only implementation review identified four defects: unsafe
Windows stale-lock probing, privacy exclusions disappearing on uninstall,
contradictory context-sharing ignores and disabled reviewer safety metadata being
accepted by validation. All four were corrected with regression coverage and
independently re-reviewed. Native Windows unlocking remains deliberately disabled;
the defensive branch is covered through simulation, not a Windows model runtime.

## Real native-client tests

### Claude Code 2.1.251, macOS

The real client initialization event listed all ten `dat-*` agents from a fresh
temporary project. Thus native discovery/loading was **SUPPORTED_AND_TESTED**.
The invocation then returned `authentication_failed` / `Not logged in`; it spawned
zero subagents. Model invocation, delegation, permissions enforcement and parallel
execution were **not tested**. No authentication was configured by the framework.

### Codex CLI 0.153.4, macOS

The real authenticated client read synthetic source and both context files and
returned the marker `DAT_CONTEXT_1_0_0`. Its delegation tool did not expose a named
profile selector. The exact `dat-code-review-engineer` profile invocation was
therefore **BLOCKED**; generating TOML files did not prove native profile loading.

The supplied-role fallback used a real native child with the full canonical role,
actual source and delegation envelope. Persisted host events recorded a started
and completed `SubAgentActivity`, an actual `spawn_agent` tool result and a child
report returned to the leader. The child identified `average([])` dividing by zero
in `fixture.py:2`, with the expected context marker. This is independent static
review of synthetic source; it is not an executed functional test of that function.

An initial child returned objects instead of arrays in `EVIDENCE` and `TESTS`.
The typed response instructions, leader correction rule and evidence parser were
strengthened so a process exit code or model success claim cannot pass this check.
The final typed-envelope smoke **passed**: one native child started, one completed,
one structured child report received, and zero contract errors. The assessor
checked host lifecycle events and the actual child response rather than accepting
the leader's final success claim. Named-profile loading remains unverified.

The fallback runs under a read-only parent. It does not load the named profile or
inherit its profile-specific feature reductions. Read-only configuration was used;
deliberately denied writes, intrusive security testing and parallel isolation were
not exercised. Ephemeral Codex sessions failed child registration in this client;
the smoke uses a normal session. Synthetic prompts can remain in host history.

### Other surfaces

Copilot CLI was absent; no authenticated IDE or cloud invocation was performed.
ChatGPT files were exported and checked locally; no Project or Custom GPT was
created, uploaded or tested. Real Figma, deployment and database connectors were
not exercised. Their discovery/approval contracts are implemented in agent
instructions; no integration success is claimed.

## Reproduce opt-in native tests

These commands use the selected client's configured account and quota. They create
only synthetic temporary projects. Inspect actual tool events and the returned
`assessment` before promoting a capability; exit code zero alone is insufficient.

```sh
python3 scripts/native_smoke.py --platform codex --dispatch role-envelope --execute
python3 scripts/native_smoke.py --platform codex --dispatch profile --execute
python3 scripts/native_smoke.py --platform claude-code --execute
```

Raw transcripts stay outside the repository. Codex normal sessions can persist in
the host's private session store. The role-envelope assessor reads only the exact
session ID created by that smoke to confirm child lifecycle and typed report.

## Publication and portability

`scripts/publication_check.py` scans the intended tracked files for known secret
patterns, private artifacts and local home paths. This is a heuristic check and
must accompany review of staged content and intended visibility. It does not
prove that arbitrary confidential data is absent.

The [completed nine-job CI run](https://github.com/Jpflorentino/development-agent-team/actions/runs/39105411048)
passed on Linux, macOS and Windows with Python 3.11, 3.12 and 3.13, testing code
commit `a335b4b237fa6d7deb9facdb68b36eeb3a25a768`. All jobs passed structural
validation, the offline suite and the publication scanner. Each Linux/macOS job
passed 69 tests. Each Windows job registered 69 tests: 68 passed and one symlink
creation case was explicitly skipped because Windows privileges vary. No failures
were ignored. These OS runs exercise the framework, not native AI clients.

The first remote run passed all six Linux/macOS jobs and exposed two test-file
encoding assumptions on Windows. Explicit UTF-8 fixture reads/writes replaced
locale defaults, and Unicode roundtrip/ASCII-console regressions were added before
the full matrix was repeated. Installer/memory filesystem scenarios passed in that
first Windows run; test encoding failures were not treated as a successful suite.

The final evidence-only documentation update was structurally validated and
scanned locally; application code and tests are identical to that successful CI
revision. No private host configuration or native raw transcripts were published.

## Remaining limitations

- Named-profile invocation in the tested Codex client is not verified.
- Authenticated Claude delegation, all Copilot model surfaces and manual ChatGPT
  use remain untested.
- Parallel worktree integration and enforced denied-write behavior were not
  validated in native host tests.
- Profiles and policy helpers do not create a universal command firewall. Native
  host permissions and authorized integration controls remain essential.
- ChatGPT global filesystem installation is not supported; manual export and
  sequential role passes do not provide independent review.
- Model quality, token cost and task completion are not benchmarked across a
  representative workload. The smoke is intentionally small and synthetic.

## Conversation-phase audit — 22 October 2026

The instructions now separate architecture discussion/approval, task allocation and execution approval, implementation, and a later or explicitly requested deployment/cost discussion. Main-conversation instructions omit internal report field schemas, while delegated profiles and canonical references retain them. Both READMEs show ordinary project descriptions without an activation phrase.

Local checks on macOS/Python 3.12: **79 tests passed** and structural validation returned no errors. Five new harness tests simulate CLI events to check same-session read-only continuation, stopping on usage failure or project mutation, session mismatch rejection and opt-in execution. A separate adapter regression checks that user-facing instructions omit internal schemas while preserving runtime policy and complete delegated contracts. These deterministic tests do not establish model behavior.

An actual four-turn Codex test was attempted with synthetic data: a natural Portuguese brief, an informational architecture question, architecture-only approval and a later deployment/cost discussion. The model began reading context and consulting architecture, then the account usage limit interrupted the first turn before its final response. The synthetic project remained unchanged. **Multi-turn phase compliance is NOT VERIFIED**; do not classify the attempted run as passed. Raw account/session transcripts remain outside the repository.

Run the opt-in test when account quota is available:

```sh
python3 scripts/native_phase_smoke.py --execute --timeout 240
```

Review the emitted checklist and actual native tool/dispatch/completion events. Successful automatic format/hash checks alone do not prove phase semantics, approval enforcement, independent consultation or correct current cost advice.

## Functioning audit — 23 October 2026

The [agent audit](agent-audit.md) records five findings, four corrected local defects and one remaining host-enforcement limitation. **85 tests passed**, structural validation returned no errors, and the four user-facing phases completed in one synthetic Codex session after resuming an account-limited deployment turn. Architecture delegation start/completion was observed. No accepted independent DevOps result was obtained; the leader disclosed its sequential fallback. All synthetic project file hashes remained unchanged. The test now accepts explanatory follow-ups without requiring a question mark. These observations do not prove behavior for every role/platform or mechanically enforce approvals.

## Central project brain — 28 October 2026

Project installs now create one `agents/<project>-context.md` file and personalize all role instructions with its stable path. Existing shared context is migrated conservatively; private legacy archives and original shared files are preserved. Normal updates/uninstall retain user-edited knowledge. Privacy/share opt-ins, path safety, multi-platform reuse, folder renames, missing/ambiguous contexts, transactional conflicts, secret checks, timestamp updates and Windows line endings are covered by real filesystem tests. **101 tests passed** on macOS/Python 3.12.14 and structural validation returned no errors. Other operating systems have not yet run these new regressions in CI.

An account-backed Codex test used a synthetic writable Python project and a user prompt that requested only a greeting change and verification. Observed commands read the central brain first, then the assigned source, and ran an exact equality assertion. The model changed only the assigned source and the central brain, retained the original context marker, recorded the implemented/tested result and recovery state, and refreshed an intentionally old timestamp. All final native-memory checks passed. No memory-update reminder, consumer source, credentials or publication was used. Raw transcripts remain outside the repository.

```sh
python3 scripts/native_memory_smoke.py --execute --timeout 180
```

This establishes one native event-driven maintenance example, not a background watcher or a guarantee of every future response. When filesystem writes are blocked or context is only an uploaded ChatGPT snapshot, agents must disclose unsaved updates instead of claiming synchronization.

## Specialist context and first-use analysis — 2026-10-28

The final local suite passed **113 tests** on macOS/Python 3.12.14. Structural validation rendered all supported platform/scope combinations without errors. New filesystem regressions cover ten role templates, real domain-note/source requirements, supplementary context references that cannot replace application evidence, preservation on update/uninstall, offline provider signals, missing/partial scan evidence, mandatory Git exclusions, tracked-artifact refusal without index changes, and unreadable Git metadata. Other hosts/operating systems have not executed these new native scenarios.

An opt-in account-backed Codex session exercised a natural small code-change request in a writable synthetic existing application. Initial trials exposed same-turn implementation and incomplete role notes; the entry point and protocol now explicitly end the first turn after analysis, require domain notes, and resolve non-applicable role files. The last observed session left application/README files unchanged, wrote only shared/role contexts and onboarding metadata, tested the existing behavior, and answered in Portuguese that implementation remained pending. It honestly labelled Backend/QA work as sequential leader passes rather than independent agents. No external integration was needed or installed.

The last session also linked its written role artifacts alongside actual inspected application sources. Its retained artifacts were reassessed with the final validator: role links are allowed only as supplementary references; a completed role still needs an actual application/documentation source. All five smoke checks then passed, and manual transcript/context review confirmed substantive domain notes and no application edits. The original trial assessments and final reassessment remain outside the repository; do not present the earlier failed trials as successful runs.

The bounded offline scanner checks selected provider configuration filenames and JavaScript dependency prefixes. It is not comprehensive technology discovery or a plugin catalog. Native model analysis must establish actual use and inspect the current host's supported capabilities/catalog before proposing any missing integration. No real provider installation/authentication path was tested. Instruction compliance and stored evidence are not a host-enforced execution gate or a guarantee for future sessions.

A separate native maintenance scenario used an established synthetic baseline with genuine domain notes and inspected source references. An earlier all-not-applicable fixture was correctly treated as incomplete analysis; the harness now seeds relevant technical notes honestly, without claiming model participation. A first maintenance trial updated only shared/leader memory, exposing stale specialist notes. The contract now explicitly refreshes affected technical context even for a small task performed by the leader. In the final native run, the requested greeting change and equality assertion passed; prior shared knowledge was retained, the shared timestamp refreshed, and Backend/QA/Leader technical contexts updated. All nine maintenance checks passed, with writes limited to the assigned application and memory files. Manual review confirmed the affected contract and behavior notes reflect the new return value. These are synthetic Codex examples, not a background watcher or cross-host guarantee.

## Connected task management — 2026-10-29

The local suite passed **119 tests** on macOS/Python 3.12.14, including installation of the task-management protocol across every supported adapter/scope. Synthetic fixture regressions cover empty-page continuation, creation retry deduplication, project isolation, stale revisions, identified reversible trash and the opt-in native harness. Structural validation passed; generated Copilot profiles remain under their existing size guard. Repeated prose was consolidated without removing approval phases or specialist report field types.

An account-backed Codex test used a temporary, local stdio MCP task manager with five known tools and synthetic state. In the first attempt the host denied the initial read because the noninteractive process could not approve it; the leader accurately reported no tasks read or changed. The successful test preauthorized only that fixture server's tools for that process, preserving the application sandbox and real-provider permissions/configuration. It fetched the board/schema, followed an empty page's continuation, created exactly one requested task, updated the identified task using its revision, and moved only the specifically requested obsolete task to reversible Trash. All ten checks passed. Manual review confirmed a Portuguese response reporting actual operations, blocked and unmapped-status tasks, and no done transitions. Unrelated tasks and application files were unchanged; the injected task instruction to copy private memory was not followed. Only local shared/leader memory changed, with actual operation outcomes and authorization scope recorded.

This is real native Codex tool execution against a **synthetic MCP fixture**, not a live Notion account or a test of every provider. No user task data was fetched, created, edited or deleted. Real provider access remains dependent on the selected workspace/board, connector capabilities, authentication, per-operation permissions and user authorization. Runtime instructions do not install a universal command gate. Raw synthetic transcripts remain outside the repository. The fixture's stdio framing follows the [MCP transport specification](https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/transports.mdx).
