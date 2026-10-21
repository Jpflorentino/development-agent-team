# Development Agent Team

Development Agent Team is a reusable framework that organizes AI coding assistants into a virtual software engineering team. You describe what you want to build or change to a Team Leader, who clarifies the requirements, involves the specialists needed and coordinates implementation, review and testing.

It supports both a new project that starts with an idea and an existing application that needs development or maintenance. The framework provides ten specialist definitions, platform adapters, installation tools and persistent project context. Your chosen AI platform runs the agents using its available tools and permissions; no permanent framework server is required.

Version **1.0.0** · Python **3.11+** · MIT License. [Documentação em português de Portugal](docs/pt-PT/README.md).

## What you can use it for

- **Start a project from scratch:** turn an initial idea into a clarified scope, propose a suitable stack and architecture, then coordinate implementation after the necessary decisions are resolved.
- **Develop an existing application:** implement features, fix bugs and work on frontend, backend or database changes while respecting established conventions.
- **Review and validate work:** coordinate code review, relevant tests, architecture assessments and authorized security analysis, with evidence and stated limitations.
- **Prepare delivery:** organize build, infrastructure and deployment work within the permissions and approvals granted.
- **Continue across sessions:** retain approved decisions, constraints and relevant project state in shared and private local context.

The leader selects only useful specialists for each task. Independent work can run in parallel when the host supports it and ownership/isolation are established. When native delegation is unavailable, the workflow uses explicitly labelled sequential role passes; these do not provide independent review.

## How it works

1. **Describe the objective.** Start with a rough idea, a detailed brief, a feature request, a bug or a review task. You do not need to prepare internal agent instructions.
2. **Clarify and decide.** The Team Leader reads available project information, asks only material unanswered questions and coordinates the necessary product and technical choices. Existing answers, approvals and project conventions are reused.
3. **Implement and verify.** The leader delegates scoped work to the relevant specialists, integrates their results and checks actual changes, review findings and proportionate tests.
4. **Keep context and report.** The leader records durable, nonsecret project context and explains what was implemented, tested, remains proposed or is blocked.

You continue the conversation with the Team Leader; it coordinates specialist participation. The Python CLI installs and maintains the team's files. The selected AI platform executes the agents through its available capabilities.

Adapters are included for **Claude Code, OpenAI Codex, GitHub Copilot and ChatGPT**. Native agent formats are generated where supported; ChatGPT uses a manual Project export. Installing files does not prove native loading or execution. See the [capability matrix](docs/compatibility.md) and [executed validation evidence](docs/validation.md) for tested behavior and limitations.

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

## Get started

You need Python **3.11+** for the installation tools and access to your chosen AI platform to execute the agents. If you do not already have a local checkout:

```sh
git clone https://github.com/Jpflorentino/development-agent-team.git
cd development-agent-team
```

From a local checkout of this repository, preview and install into your chosen project folder. It can be a new, empty folder or an existing application; no application scaffold is required:

```sh
python3 scripts/dat.py validate
python3 scripts/dat.py install --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py install --platform codex --scope project --target /path/to/project
python3 scripts/dat.py memory init --target /path/to/project
python3 scripts/dat.py doctor --target /path/to/project
```

Use `py -3.11` or another Python 3.11+ executable if `python3` is older. The installer runs from this checkout and writes only to the chosen target. See [installation](docs/installation.md) for platform specific steps, global installation, updating, conflicts and removal.

## Run the team

After installation, open the target folder in your platform and start a new conversation. Choose the starting point that matches your project.

### Start a project from scratch

Describe what you want to build in ordinary language. You do not need to choose a framework, design a repository structure or prepare a complete specification first. If you only have an idea, the Team Leader guides discovery with a few focused questions at a time. If your brief already answers them, the leader uses those answers without repeating the interview.

> Act as the Development Agent Team Leader in NEW_PROJECT mode. I want to build **[describe your idea, the problem and intended users, as far as you know them]**. This project has no application code yet. Help me define the essential workflows, MVP scope and constraints. Ask only the important unanswered questions, in small groups, before recommending a stack and architecture. Confirm any material choices that I have not already approved before creating application scaffolding or installing application dependencies. Once those decisions are resolved, coordinate implementation, review and testing with the specialists needed. Do not commit, push or open a pull request without authorization.

For an even earlier starting point, this is enough:

> Act as the Development Agent Team Leader. I want to start a project from scratch, but I only have a rough idea: **[your idea]**. Help me clarify it and ask the essential questions before proposing how to build it.

An empty application folder is expected in this mode. Installation files such as `.codex/`, `.ai-team/`, `AGENTS.md` and Git metadata do not make it an existing application. Missing source files, an unset stack or unfilled context templates are not failures. The leader clarifies the product first, consults the Software Architect when useful, and delegates implementation after the relevant decisions are resolved. It does not activate all ten agents automatically or create planning files in your project.

### Work on an existing project

Describe the feature, bug or review you need, for example:

> Act as the Development Agent Team Leader. Read repository instructions and `.ai-team/context.md`, inspect the relevant code, then fix the reported validation bug. Preserve the existing stack. Use the smallest useful specialist set, verify available delegation tools and report actual tests and limitations. Do not commit, push or open a pull request without authorization.

The framework responds in the user's language by default. [Documentação em português de Portugal](docs/pt-PT/README.md).

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

[`dat/policy.py`](dat/policy.py) supplies deterministic selection and contract/quality-gate helpers for integrations and regression tests. These helpers do not launch models or grant host permissions. Sequential role simulation cannot satisfy an independent-review gate; HIGH/CRITICAL work remains blocked until a genuinely separate review is obtained.

## Documentation and examples

- [Architecture](docs/architecture.md), [orchestration](docs/orchestration.md), [agent reference](docs/agents.md)
- [Installation](docs/installation.md), [context management](docs/context-management.md), [security](docs/security.md)
- [Compatibility](docs/compatibility.md), [official platform sources](docs/platform-sources.md)
- [Ten worked usage examples](examples/README.md)

Native behavior varies by product surface, version, plan and enabled tools. ChatGPT installation produces a reusable manual export, requiring manual attachment/instructions setup. Runtime smoke tests must verify agent loading, delegation and permissions in each actual host. The compatibility document records these limits without treating generated files as executed integrations.

Contributions are welcome through reviewed changes; see [contributing](docs/contributing.md). Distributed under the [MIT License](LICENSE).
