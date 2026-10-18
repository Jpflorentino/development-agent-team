# Compatibility and validation boundaries

The adapter generator emits native profiles for documented host formats. Capability availability depends on the actual product surface, version, account and enabled tools. A successful local file installation is not an executed native agent integration. See [official sources and research date](platform-sources.md) and the surface-specific instructions in `adapters/`.

Statuses have precise meanings:

- `SUPPORTED_AND_TESTED`: the named behavior was actually executed and observed.
- `SUPPORTED_NOT_TESTED`: documented support and an implementation exist, but this behavior was not exercised in that host.
- `PARTIALLY_SUPPORTED`: support is conditional, surface dependent or a manual fallback.
- `NOT_SUPPORTED`: this framework offers no such mechanism for that surface.
- `NOT_VERIFIED`: current available evidence is insufficient to assert support.

The matrix describes native platform use. Python unit and contract tests are recorded separately; they cannot change native behavior to `SUPPORTED_AND_TESTED`.

| Capability | Claude Code | OpenAI Codex | GitHub Copilot | ChatGPT Projects/manual export |
| --- | --- | --- | --- | --- |
| Custom agent definitions | SUPPORTED_AND_TESTED: all ten loaded; model call blocked | PARTIALLY_SUPPORTED: rendered TOML; named invocation unavailable in tested client | SUPPORTED_NOT_TESTED | PARTIALLY_SUPPORTED: reference roles |
| Real specialist delegation | SUPPORTED_NOT_TESTED: authentication blocked | SUPPORTED_AND_TESTED: supplied-role fallback | PARTIALLY_SUPPORTED: verify CLI/IDE/cloud surface | NOT_SUPPORTED by this adapter |
| Parallel specialist execution | SUPPORTED_NOT_TESTED | SUPPORTED_NOT_TESTED | PARTIALLY_SUPPORTED: host dependent | NOT_SUPPORTED by this adapter |
| Leader/specialist results | SUPPORTED_NOT_TESTED | SUPPORTED_AND_TESTED: one typed child report | PARTIALLY_SUPPORTED | PARTIALLY_SUPPORTED: sequential role passes |
| Direct peer communication | PARTIALLY_SUPPORTED: separate Agent Teams mechanism | NOT_VERIFIED | NOT_VERIFIED | NOT_SUPPORTED by this adapter |
| External tools | SUPPORTED_NOT_TESTED: host permissions | SUPPORTED_NOT_TESTED: host permissions | PARTIALLY_SUPPORTED: surface/tool availability | PARTIALLY_SUPPORTED: connected tools |
| Project filesystem access | SUPPORTED_NOT_TESTED | SUPPORTED_AND_TESTED: leader read synthetic fixture | PARTIALLY_SUPPORTED: workspace/runtime dependent | PARTIALLY_SUPPORTED: uploaded files or connected environment |
| Persistent context access | SUPPORTED_NOT_TESTED | SUPPORTED_AND_TESTED: shared/local files; child received marker | PARTIALLY_SUPPORTED: files must reach runtime | PARTIALLY_SUPPORTED: manual attachment and refresh |
| Global profiles | SUPPORTED_NOT_TESTED | SUPPORTED_NOT_TESTED | PARTIALLY_SUPPORTED: CLI user profiles | NOT_SUPPORTED |
| Project installation | SUPPORTED_NOT_TESTED | SUPPORTED_NOT_TESTED | SUPPORTED_NOT_TESTED | PARTIALLY_SUPPORTED: local export then manual setup |
| Technical sandbox/approvals | SUPPORTED_NOT_TESTED: configured by host | SUPPORTED_NOT_TESTED: configured by host | PARTIALLY_SUPPORTED: surface dependent | PARTIALLY_SUPPORTED: environment dependent |
| Independent code review | SUPPORTED_NOT_TESTED: separate delegated reviewer | SUPPORTED_AND_TESTED: synthetic static review, supplied role | PARTIALLY_SUPPORTED: requires separate execution | NOT_SUPPORTED by sequential role simulation |
| Native behavior tests | PARTIALLY_SUPPORTED: loading only; auth blocked | SUPPORTED_AND_TESTED: one supplied-role smoke; see limits | NOT_VERIFIED: runtime absent | NOT_VERIFIED: manual import untested |

Conventional Claude Code subagents do not become Agent Teams merely because ten files exist. This framework does not enable experimental Agent Teams. Standard leader-mediated results are the baseline. Copilot CLI, IDE and cloud agents are different surfaces; repository profiles intended for cloud use must be committed through an authorized workflow and present in the cloud revision. A local ignored profile does not reach the cloud.

ChatGPT export files must be manually applied using the actual Project's supported instructions and file attachment interface. The framework neither uploads data nor creates ten independent ChatGPT agents. Ordinary ChatGPT Projects do not consume local `.codex/` or `.claude/` profiles. If a particular ChatGPT Work environment exposes real delegation tools, verify it separately; this adapter makes no such claim.

Actual client versions, evidence and untested dimensions are recorded in the
[1.0.0 validation report](validation.md).

## Local checks and native smoke tests

`python3 scripts/dat.py validate` checks structural consistency, canonical definitions and rendered adapter formats. `python3 -m unittest discover -s tests -v` runs framework tests, including deterministic orchestration contracts and temporary-directory installation/memory cases. These checks can validate local behavior while the native host rows remain untested. The exact executed results belong in the release's delivery evidence.

To promote a native capability, record the product and surface, version, OS, date, relevant configuration, actual invocation and observed evidence. Test discovery/loading, one read-only specialist invocation, a delegated result, context access, denied writes and parallel isolation where supported. Do not record private prompts, credentials or consumer source code in public test evidence. A skipped or unavailable runtime remains explicitly untested.

The CLI uses portable Python 3.11+ and standard-library APIs. OS portability is an implementation objective, not proof of Windows and Linux execution; runs on those systems must be reported separately. Runtime tools may require installation, authentication or permissions not provided by the framework.

Read-only profiles have different technical limits. Claude Code profiles allow only `Read`, `Grep` and `Glob`; Copilot profiles allow `read` and `search`. Codex profiles disable shell, apps, plugins and permission requests, but inherit the host's remaining edit/MCP permissions. A read-only instruction alone is not a complete technical boundary: configure the host sandbox and tool permissions appropriately before independent review.

Default global directories are assumed. Custom host configuration roots such as `CODEX_HOME` or `COPILOT_HOME` are not automatically detected; inspect the rendered paths and the active host configuration before relying on profile discovery.

Codex distinguishes named custom-profile invocation from a native child that
receives a role definition in its assignment. If the current delegation tool has
no custom-profile selector, the leader can read the installed or bundled role and
pass its full instructions plus the task envelope to a real native child. This
fallback must be reported as **native delegated role with supplied definition**;
it does not prove named-profile discovery or apply the profile's feature settings.
For restricted reviewer delegation, use a separate parent review session with
host-enforced read-only permissions and audited MCP/tools. A generic child in a
writable session has only a behavioral no-edit instruction. Verify these behaviors
in the installed runtime before changing the native capability statuses above.
