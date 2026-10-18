# Installation and maintenance

Run the commands from the framework checkout using Python 3.11 or later. Only the Python standard library is required. On Windows substitute `py -3.11` and a Windows target such as `C:\work\project`. Quote paths containing spaces. The CLI is portable Python; host platform behavior must still be tested on its own operating system.

```sh
python3 scripts/dat.py --help
python3 scripts/dat.py validate
```

The installer supports `install`, `update` and `uninstall` with `--platform`, `--scope`, `--target` and `--dry-run`. Supported platform names are `claude-code`, `codex`, `github-copilot` and `chatgpt`. The target for project scope is the consumer repository; for global scope it is the user's home directory, rather than the platform configuration subdirectory.

## Claude Code

```sh
python3 scripts/dat.py install --platform claude-code --scope project --target /path/to/project --dry-run
python3 scripts/dat.py install --platform claude-code --scope project --target /path/to/project
```

Open the target project in Claude Code, inspect the installed native profiles, and use the host's agent discovery interface to verify that they load. Ask the Team Leader to delegate one read-only inspection to a named specialist and require actual tool evidence. Standard subagents and experimental Agent Teams have different coordination models; installing this framework does not enable Agent Teams or require it. See [official sources](platform-sources.md).

## OpenAI Codex

```sh
python3 scripts/dat.py install --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py install --platform codex --scope project --target /path/to/project
```

Open Codex in the target repository. Trust the project configuration only after inspecting it and use the host's available delegation mechanism to invoke the Team Leader or a specialist. Inspect native TOML definitions and project instructions through `doctor`. Model selection is inherited from the host; model availability is not assumed. Sandboxing and approval settings belong to the host and are not relaxed by installation.

## GitHub Copilot

```sh
python3 scripts/dat.py install --platform github-copilot --scope project --target /path/to/project --dry-run
python3 scripts/dat.py install --platform github-copilot --scope project --target /path/to/project
```

Inspect the custom `.agent.md` profiles and select Team Leader using the agent interface supported by your Copilot product. CLI, IDE and cloud agent capabilities differ. Verify delegation on the actual surface; do not infer it from profile availability. Cloud agents can only discover repository files present in the revision they use. Sharing or committing profiles requires authorization; an ignored local installation is not a cloud installation.

## ChatGPT

```sh
python3 scripts/dat.py install --platform chatgpt --scope project --target /path/to/project
```

This creates a local export, not an authenticated ChatGPT installation. Open a ChatGPT Project, manually add the exported instruction text and attach the specialist/reference files that the target surface supports. Review what is shared before upload. Ask ChatGPT to act as Team Leader and consult each relevant specialist sequentially if native delegation is unavailable. These are role passes in one conversation, not ten independent agents. Independent review must come from a separate reviewer or runtime when required.

Global ChatGPT scope is rejected because no global filesystem installation mechanism has been verified. The project export does not configure every ChatGPT conversation, establish a connection, upload files or create a Custom GPT. Connected tools, file access and executable development capabilities depend on the actual account and surface.

## Global scope

```sh
python3 scripts/dat.py install --platform codex --scope global --target /path/to/home --dry-run
python3 scripts/dat.py install --platform codex --scope global --target /path/to/home
```

Replace the platform as needed. Omit `--target` only when you intend to use the current user's home. Global configuration cannot override product limitations; see the [compatibility matrix](compatibility.md), especially Copilot and ChatGPT surface restrictions. Tests should pass a temporary home target so they cannot modify real user settings.

| Platform | Project files | Global files relative to home |
| --- | --- | --- |
| Claude Code | `.claude/agents/dat-*.md`, `CLAUDE.md` | `.claude/agents/dat-*.md`, `.claude/CLAUDE.md` |
| Codex | `.codex/agents/dat-*.toml`, `AGENTS.md` | `.codex/agents/dat-*.toml`, `.codex/AGENTS.md` |
| GitHub Copilot | `.github/agents/dat-*.agent.md`, `.github/copilot-instructions.md` | `.copilot/agents/dat-*.agent.md`, `.copilot/copilot-instructions.md` (Copilot CLI) |
| ChatGPT | `.ai-team/chatgpt/` manual export | Not supported |

Each supported installation also includes a platform specific canonical reference bundle in `.ai-team/framework/`. Native profile IDs have the prefix `dat-`; for example, `dat-team-leader`.

## Sharing, conflicts and recovery

Installations default to local use with managed ignore rules. `--share-agents` and `--share-context` opt into sharing eligible files; review the diff and authorize any commit separately. Private context remains private. Consumer memory is initialized separately:

```sh
python3 scripts/dat.py memory init --target /path/to/project
```

Inspect `--dry-run` output before any modification. The installer records ownership and original state, preserves unrelated content, and refuses conflicting edits. Resolve a conflict by comparing local edits against the canonical definitions and rerunning after the intended version is chosen; do not delete customizations blindly. A failed operation should leave recoverable originals through the installer's transactional backup/rollback behavior. Do not manually remove ownership metadata until recovery is understood.

After an interrupted write, inspect diagnostics and preview recovery:

```sh
python3 scripts/dat.py doctor --target /path/to/project
python3 scripts/dat.py recover --target /path/to/project --dry-run
python3 scripts/dat.py recover --target /path/to/project
```

If a stale maintenance lock prevents recovery, `recover --unlock` on macOS/Linux verifies that its local owner process has stopped before removing it. Windows automatic unlocking is deliberately unavailable: verify in Task Manager that the process has stopped before manually removing only `.ai-team/.dat/lock`. Never remove an active writer's lock. Recovery refuses to overwrite conflicting subsequent edits. Transaction journals may retain original configuration text locally; keep `.ai-team/.dat/` private and do not upload it as troubleshooting evidence.

## Update and uninstall

```sh
python3 scripts/dat.py update --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py update --platform codex --scope project --target /path/to/project
python3 scripts/dat.py uninstall --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py uninstall --platform codex --scope project --target /path/to/project
```

Update reads the framework version in the current checkout. It does not fetch a newer release from the internet. Obtain the desired reviewed framework revision first. Uninstall removes only managed content and preserves context. Changed managed files are conflicts requiring deliberate resolution, not permission to overwrite them.

Uninstall also retains recovery journals and `.ai-team/.gitignore` privacy rules.
It removes adapter ignore blocks from the root `.gitignore`, while retained local
memory and backups remain ignored. Remove retained data only by deliberate choice.

```sh
python3 scripts/dat.py doctor --target /path/to/project
python3 scripts/dat.py validate
```

`doctor` diagnoses the environment and installation; `validate` checks framework structure and adapters. Neither command proves model behavior, successful native delegation or end-to-end task quality.
