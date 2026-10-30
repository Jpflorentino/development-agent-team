# Installation and maintenance

Run the commands from the framework checkout using Python 3.11 or later. Only the Python standard library is required. On Windows substitute `py -3.11` and a Windows target such as `C:\work\project`. Quote paths containing spaces. The CLI is portable Python; host platform behavior must still be tested on its own operating system.

```sh
python3 scripts/dat.py --help
python3 scripts/dat.py validate
```

The installer supports `install`, `update` and `uninstall` with `--platform`, `--scope`, `--target` and `--dry-run`. Supported platform names are `claude-code`, `codex`, `github-copilot` and `chatgpt`. The target for project scope is the consumer repository; for global scope it is the user's home directory, rather than the platform configuration subdirectory.

Project scope also works with a new, empty target folder; application code and a chosen stack are not prerequisites. Installation creates team configuration, not an application scaffold. Open that target folder in the selected platform and start a new conversation. Describe your idea normally; the installed main instructions activate the Team Leader without a role invocation or formatting prompt. See the [natural-language example](../README.md#start-a-project-from-scratch). The leader discusses architecture with Architect, obtains approval, then proposes tasks for execution approval. Deployment/cost decisions are discussed separately when relevant.

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

Inspect the custom `.agent.md` profiles and select Team Leader using the agent interface supported by your Copilot product. CLI, IDE and cloud agent capabilities differ. Verify delegation on the actual surface; do not infer it from profile availability. Cloud agents can only discover repository files present in the revision they use. Installed profiles remain private and excluded from consumer Git publication. A cloud surface needing versioned profiles is incompatible with that private local installation; do not force-add them.

## ChatGPT

```sh
python3 scripts/dat.py install --platform chatgpt --scope project --target /path/to/project
```

This creates a local export, not an authenticated ChatGPT installation. Open a ChatGPT Project, manually add the exported instruction text and attach the specialist/reference files that the target surface supports. Review what is shared before upload. The installed instructions activate Team Leader; describe the objective normally. It consults relevant specialists sequentially if native delegation is unavailable. Attach the shared and relevant role contexts as reviewed snapshots. These are role passes in one conversation, not independent native agents. Independent review must come from a separate reviewer or runtime when required.

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

## Privacy, conflicts and recovery

Consumer profiles and all context/metadata stay private with persistent managed ignore rules. `--share-agents` and `--share-context` are rejected, including prior opt-ins on upgrade. Project install/update and memory initialization stop before private writes if Git already tracks protected artifacts; ignore rules cannot remove indexed or historical remote data. Review any untracking/history remedy separately; the installer does not change the index or rewrite history. The framework source repository may still version its canonical role definitions.

Installation creates the shared `agents/<project>-context.md`, eleven `agents/contexts/<role>-context.md` templates and pending onboarding metadata. Normal context edits are outside adapter ownership hashes and survive updates. Legacy files are preserved. On first execution in an existing application, the leader analyzes sources, writes actual technical context and reports useful host integrations before application implementation. It asks for explicit scoped consent before plugin/MCP installation. See [onboarding](onboarding.md). The optional offline scan detects selected provider configuration filenames and JavaScript dependency prefixes; the agents supplement this limited inventory with actual project analysis. Global profiles leave memory to each project. Explicit initialization is idempotent:

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

Update reads the framework version in the current checkout. It does not fetch a newer release from the internet. Obtain the desired reviewed framework revision first. Uninstall removes only managed adapter content and preserves shared and role contexts, onboarding/path metadata and privacy rules. Changed managed files are conflicts requiring deliberate resolution, not permission to overwrite them.

Uninstall also retains recovery journals and `.ai-team/.gitignore` privacy rules.
It removes adapter ignore blocks from the root `.gitignore`, while retained local
memory and backups remain ignored. Remove retained data only by deliberate choice.

```sh
python3 scripts/dat.py doctor --target /path/to/project
python3 scripts/dat.py validate
```

`doctor` diagnoses the environment and installation; `validate` checks framework structure and adapters. Neither command proves model behavior, successful native delegation or end-to-end task quality.

If the selected target has no managed installation, `doctor` reports a warning rather than presenting that absence as a verified installation. An intact manifest establishes file integrity, not native execution or approval enforcement.


## Optional task manager

The installed bundle includes task-manager instructions; it does not connect Notion or another account. Name the provider and exact project board/database in the host conversation. The leader discovers existing tools/permissions, follows supported installation consent for missing connectors, fetches the schema and records the authorized scope locally. Scoped ongoing task updates reuse that grant. See [task management](task-management.md).
