# Development Agent Team

A portable engineering team for Claude Code, OpenAI Codex, GitHub Copilot and ChatGPT. Version **1.0.0**, Python **3.11+**, MIT licensed. The framework uses native agent definitions where available and an explicit sequential fallback elsewhere. No server, account service or permanent process is required.

The Team Leader selects only the specialists needed, delegates scoped work, checks evidence and controls approvals and persistent context. Installing definitions does not prove that a platform loaded or executed agents. See the [capability matrix](docs/compatibility.md) and [executed validation evidence](docs/validation.md) for the distinction.

## Get started

From a local checkout of this repository, preview and install into an existing project:

```sh
python3 scripts/dat.py validate
python3 scripts/dat.py install --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py install --platform codex --scope project --target /path/to/project
python3 scripts/dat.py memory init --target /path/to/project
python3 scripts/dat.py doctor --target /path/to/project
```

Use `py -3.11` or another Python 3.11+ executable if `python3` is older. The installer runs from this checkout and writes only to the chosen target. See [installation](docs/installation.md) for platform specific steps, global installation, updating, conflicts and removal.

Start a conversation in the installed platform with:

> Act as the Development Agent Team Leader. Read repository instructions and `.ai-team/context.md`, inspect the relevant code, then fix the reported validation bug. Preserve the existing stack. Use the smallest useful specialist set, verify available delegation tools and report actual tests and limitations. Do not commit, push or open a pull request without authorization.

The framework responds in the user's language by default. [Documentação em português de Portugal](docs/pt-PT/README.md).

## Team

| Stable agent ID | Responsibility |
| --- | --- |
| `team-leader` | Requirements, delegation, approval, integration and memory |
| `software-architect` | Architectural boundaries and structural decisions |
| `ui-ux-designer` | Flows, accessible design and implementable specifications |
| `frontend-developer` | Interfaces, interaction and API integration |
| `backend-developer` | APIs, services and business rules |
| `database-engineer` | Data integrity, migrations and query performance |
| `qa-engineer` | Acceptance, regression and functional verification |
| `security-engineer` | Evidence based security analysis and safeguards |
| `devops-engineer` | Build, infrastructure, delivery and operations |
| `code-review-engineer` | Independent, read-only review where delegation permits |

The ten canonical definitions live in [`agents/`](agents/). Adapters translate those definitions into each platform's format. Instructions cover thirteen modes, from new projects and bug fixes to architecture review, testing, modernization and deployment. Figma is preferred when available and authorized; otherwise the designer produces an implementable alternative and identifies that limitation.

## How it works

1. The Team Leader reads the actual repository, instructions and compact project context, then sets mode, scope and risk.
2. The leader verifies platform capabilities and delegates only relevant areas. Parallel tasks require agreed contracts, isolation and exclusive file ownership.
3. Specialists return changes, evidence, tests, risks and proposed context updates. The leader integrates and checks proportional quality gates.
4. The leader persists durable, nonsecret context and reports what was implemented, tested or blocked.

Native host delegation executes the agents; the Python CLI is an installer and contract checker. [`dat/policy.py`](dat/policy.py) provides deterministic selection and quality gate helpers for integration and regression testing. It does not invoke a model, launch agents, enforce host permissions or classify arbitrary prose. Sequential role simulation cannot provide independent code review; HIGH/CRITICAL gates remain blocked until a genuinely separate review is obtained.

## Safety and context

Within an authorized task, agents may inspect code, make scoped changes, run nondestructive checks and create a development branch. Consumer project commits, pushes, pull requests, significant architectural changes, production deployments, destructive actions and material paid resources require authorization. Host sandbox and approval mechanisms remain authoritative. No planning or progress files are generated in consumer projects.

Shared technical context belongs in `.ai-team/context.md`; local operational context belongs in `.ai-team/context.local.md`. Neither file may contain secrets. Files remain local unless sharing is explicitly chosen. Memory commands support initialization, additions, compacting and stale context checks; see [context management](docs/context-management.md).

## Maintenance and validation

```sh
python3 scripts/dat.py update --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py update --platform codex --scope project --target /path/to/project
python3 scripts/dat.py uninstall --platform codex --scope project --target /path/to/project
python3 -m unittest discover -s tests -v
```

Install/update preserve unmanaged files and stop on conflicting managed edits. Uninstall retains project memory. Unit tests use temporary targets; contract/simulation tests never stand in for native agent invocation. [Contributing](docs/contributing.md) explains the validation and release process.

## Documentation and examples

- [Architecture](docs/architecture.md), [orchestration](docs/orchestration.md), [agent reference](docs/agents.md)
- [Installation](docs/installation.md), [context management](docs/context-management.md), [security](docs/security.md)
- [Compatibility](docs/compatibility.md), [official platform sources](docs/platform-sources.md)
- [Ten worked usage examples](examples/README.md)

Native behavior varies by product surface, version, plan and enabled tools. ChatGPT installation produces a reusable manual export, requiring manual attachment/instructions setup. Runtime smoke tests must verify agent loading, delegation and permissions in each actual host. The compatibility document records these limits without treating generated files as executed integrations.

Contributions are welcome through reviewed changes; see [contributing](docs/contributing.md). Distributed under the [MIT License](LICENSE).
