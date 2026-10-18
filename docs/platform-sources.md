# Official platform sources

Consulted 17–18 October 2026. These sources establish documented formats and
limitations; they do not prove that a particular installed client supports them.
The adapter tests validate rendering and native configuration syntax. Real client
loading and model execution require separate evidence in the compatibility report.

| Platform | Official source | Implementation decision |
| --- | --- | --- |
| Claude Code | [Custom subagents](https://code.claude.com/docs/en/sub-agents) | Markdown with YAML frontmatter in `.claude/agents/` or `~/.claude/agents/`; required `name` and `description`. Read-only roles receive a `Read`, `Grep`, `Glob` allowlist. Models inherit. |
| Claude Code | [Persistent instructions](https://code.claude.com/docs/en/memory) | Project `CLAUDE.md` and user `~/.claude/CLAUDE.md` supply the main conversation's leader instructions. These are behavioral guidance, not command enforcement. |
| Claude Code | [Agent Teams](https://code.claude.com/docs/en/agent-teams) | Agent Teams are experimental and optional. The framework uses ordinary subagents without enabling the experimental feature or generating team runtime state. |
| Codex | [Subagents and custom agent schema](https://learn.chatgpt.com/docs/agent-configuration/subagents) | Standalone `.codex/agents/*.toml` or `~/.codex/agents/*.toml` requires `name`, `description`, `developer_instructions`. No model pin or `config.toml` registration is needed. Capability reductions are partial; parent permissions/provider/MCP remain inherited. |
| Codex | [AGENTS.md discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md) | Project `AGENTS.md` and global `~/.codex/AGENTS.md` hold managed leader instructions. Existing user content is preserved by the installer. |
| GitHub Copilot | [Custom agent configuration](https://docs.github.com/en/copilot/reference/custom-agents-configuration) | YAML-frontmatter `.agent.md` profiles use documented tool aliases. Read-only roles allow `read` and `search`. Prompts exceeding 30,000 characters are rejected. IDE-specific handoffs are not assumed portable. |
| GitHub Copilot CLI | [Create and use custom agents](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/create-custom-agents-for-cli) | Project `.github/agents/`; user `~/.copilot/agents/`. Restart after installation; choose `/agent` or `--agent`. Shared policy is embedded because delegated agents do not inherit repository instructions by default. |
| GitHub Copilot CLI | [Configuration directory](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference) | User instructions use `~/.copilot/copilot-instructions.md`. This global installation targets CLI, not every IDE or GitHub cloud account. |
| GitHub Copilot cloud | [Create cloud custom agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents) | Discovery requires committing profiles and merging them into the default branch. Local generation does not publish them. Cloud task assignment can invoke a Git/PR workflow and needs the appropriate consumer-project authorization. |
| VS Code | [Custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) | Repository `.github/agents/` profiles are usable in supporting releases. CLI, IDE and cloud tool availability and execution controls remain distinct. |
| ChatGPT | [Projects and chats](https://learn.chatgpt.com/docs/projects) | Project instructions and uploaded references provide a manual reusable bundle. ChatGPT Projects do not automatically access a local folder. No automatic global filesystem installation is claimed. |

ChatGPT Work subagents are documented in the same official subagent source linked
above, with account/client availability conditions. The custom TOML discovery
mechanism is documented for local Codex clients. Therefore the ChatGPT export
defaults to labelled sequential role passes and uses actual delegation only when
the current environment exposes it. Sequential passes cannot satisfy an independent
review gate by themselves.

## Enforcement and portability boundaries

The Codex adapter deliberately omits per-agent `sandbox_mode` and `approval_policy`:
the current documented schema says those settings cannot override the parent.
It reduces supported capabilities on read-only profiles and states the remaining
editing/MCP limitation. A read-only parent session with audited integrations is
needed for a stronger boundary. Read-only Claude and Copilot profiles withhold
shell, editing, delegation and MCP tools through allowlists.

Consumer-project approval rules are also stated in every role. Profiles with shell
or external tools are not a universal Git/production command firewall. Existing
host permissions, sandboxing and organizational controls remain authoritative.

Global paths are relative to a user home directory and use documented default
configuration locations. Custom `CODEX_HOME`, `COPILOT_HOME`, provider policies,
managed installations and alternate client-specific configuration roots are not
automatically supported. Review and relocate generated files manually for such a
setup; passing a configuration directory as the installer target would incorrectly
nest another `.codex` or `.copilot` directory inside it.

Canonical definitions remain the single source of truth. The renderer produces
native profiles at install/update time instead of checking in duplicate generated
copies. Its platform-specific reference bundles prevent one platform's uninstall
from deleting another platform's owned files.

## Named profiles and native role delegation

The Codex adapter checks the actual delegation tool schema before assuming a
custom-profile selector exists. Some installed clients may expose real native
delegation without a named-profile argument. In that case, the leader reads the
role's instructions and includes them with the complete task envelope when spawning
a native child. This is an implemented compatibility strategy; its existence does
not establish that a named TOML profile loaded. Native execution, named-profile
selection and technical profile restrictions must be recorded separately.

A generic child does not gain a profile's feature restrictions from its message or
task name. Reviewer fallback requires a read-only parent review session and audited
MCP/tools for technical enforcement. A no-edit message in a writable session is
only behavioral guidance. If real delegation is absent, sequential role passes
remain the fallback and cannot claim independent review.
