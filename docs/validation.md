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

The GitHub Actions workflow runs structural validation and the offline suite on
Linux, macOS and Windows, with Python 3.11, 3.12 and 3.13. Configuration alone is
not evidence of a successful remote run. Actual CI results are recorded after
publication. These OS runs exercise the framework, not native AI clients.

The first remote run passed all six Linux/macOS jobs and exposed two test-file
encoding assumptions on Windows. Explicit UTF-8 fixture reads/writes replaced
locale defaults, and Unicode roundtrip/ASCII-console regressions were added before
the full matrix was repeated. Installer/memory filesystem scenarios passed in that
first Windows run; test encoding failures were not treated as a successful suite.

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
