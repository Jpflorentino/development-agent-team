# Development Agent Team

Development Agent Team is a reusable framework that organizes AI coding assistants into a virtual software engineering team. You describe what you want to build or change to a Team Leader, who clarifies the requirements, involves the specialists needed and coordinates implementation, review and testing.

It supports both a new project that starts with an idea and an existing application that needs development or maintenance. The framework provides eleven role definitions, platform adapters, installation tools and persistent project context. Your chosen AI platform runs the agents using its available tools and permissions; no permanent framework server is required.

Version **1.0.0** · Python **3.11+** · MIT License. [Documentação em português de Portugal](docs/pt-PT/README.md).

## What you can use it for

- **Start a project from scratch:** turn an initial idea into a clarified scope, propose a suitable stack and architecture, then coordinate implementation after the necessary decisions are resolved.
- **Develop an existing application:** implement features, fix bugs and work on frontend, backend or database changes while respecting established conventions.
- **Review and validate work:** coordinate code review, relevant tests, architecture assessments and authorized security analysis, with evidence and stated limitations.
- **Manage project tasks:** the Team Leader reads live pending work and maintains authorized tasks/statuses through an available Notion or other tracker connection. See [task management](docs/task-management.md).
- **Prepare delivery:** organize build, infrastructure and deployment work within the permissions and approvals granted.
- **Continue across sessions:** retain shared project facts and technical context per specialist, updated at meaningful milestones.

The leader selects only useful specialists for each task. Independent work can run in parallel when the host supports it and ownership/isolation are established. When native delegation is unavailable, the workflow uses explicitly labelled sequential role passes; these do not provide independent review.

## How it works

1. **Describe the objective.** Start with a rough idea, a detailed brief, a feature request, a bug or a review task. You do not need to prepare internal agent instructions.
2. **Discuss architecture.** The Team Leader clarifies material gaps, consults Software Architect on undecided architecture/technologies and explains options in your language. Review, revise and approve those choices.
3. **Review tasks and implement.** Based on the approved architecture, the leader proposes tasks per agent, deliverables, dependencies and checks. After execution approval, it coordinates implementation, review and tests. Prior approvals or explicit autonomous authorization are reused within their scope.
4. **Discuss deployment and costs.** When relevant, discuss options and costs with the leader and DevOps. Architecture approval alone does not approve implementation, paid resources or deployment.
5. **Keep context and report.** The leader maintains shared memory; specialists maintain their assigned technical context. It explains actual results and limitations.

You continue the conversation with the Team Leader; it coordinates specialist participation. The Python CLI installs and maintains the team's files. The selected AI platform executes the agents through its available capabilities.

Approval phases are instructions to the host model. The installer does not add a pre-tool execution interceptor, and Codex does not automatically call the Python contract helpers before writing files. Hard prevention of writes before approval requires a host-enforced read-only planning session or an execution gate integrated with the host's tools. Installing these agents alone does not provide that guarantee.

The Team Leader answers you conversationally in your language, with a recommendation or outcome, relevant explanation and focused questions or next steps. Specialist JSON reports are an internal exchange; the leader summarizes their validated contents instead of showing the raw protocol. Structured user-facing output is used when you explicitly ask for it.

Generated main-conversation instructions omit the internal JSON field schemas. Those contracts remain in the canonical reference bundle and delegated profiles, where they are needed for specialist returns.

The plan identifies who was actually consulted, the task assigned, its status, recommendation, rationale and evidence. Roles not needed are identified without activating all roles. Native delegation, sequential role passes and leader proposals are labelled distinctly; installed profiles alone do not prove that an agent received a task. See the [planning and approval protocol](docs/orchestration.md#reviewable-plan-and-approval).

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
| `code-optimization-engineer` | Review existing code for cleanup, simplification and evidenced optimization |

The eleven canonical definitions live in [`agents/`](agents/). Adapters translate those definitions into each platform's format. Instructions cover fourteen modes, from new projects and bug fixes to architecture review, testing, modernization and deployment. Figma is preferred when available and authorized; otherwise the designer produces an implementable alternative and identifies that limitation.

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

After installation, open the target folder in your platform and start a new conversation so the main instructions load. Describe your objective normally: the installed entry point already activates the Team Leader. No activation phrase, mode name or output-format reminder is required. These examples describe product intent, not extra configuration.

### Start a project from scratch

Describe what you want to build in ordinary language. You do not need to choose a framework, design a repository structure or prepare a complete specification first. If you only have an idea, the Team Leader guides discovery with a few focused questions at a time. If your brief already answers them, the leader uses those answers without repeating the interview.

> I want a website for a physiotherapy service at home. People should be able to meet the team, choose a professional and request an appointment. I have not chosen technologies yet. Help me work out the best approach.

The leader should discuss the product and architecture with you, consulting Architect first. After you approve the architecture, it presents the task allocation for execution approval. Deployment and costs can be discussed later with DevOps. You do not need to restate that workflow in your brief.

An empty application folder is expected in this mode. Installation files such as `.codex/`, `.ai-team/`, `AGENTS.md` and Git metadata do not make it an existing application. Missing source files, an unset stack or unfilled context templates are not failures. The leader clarifies the product first, consults the Software Architect when useful, and delegates implementation after the relevant decisions are resolved. It does not activate all roles automatically or create planning files in your project.

### Explain a project already started

> Pause implementation and assess the current project read-only. Explain the stack, architecture and relevant integrations from the actual files. For each specialist, identify the task assigned, participation status, recommendation and evidence where records exist. Distinguish observed code from documented historical decisions and approvals; mark unavailable history unverified. Label any new consultations retrospective. Present the proposed next steps for my approval before further implementation.

### Work on an existing project

On first use, the leader builds the project baseline and technical contexts, reports existing architecture and reviews useful plugins/MCPs for the actual host. It requests authorization for verified missing integrations; none are installed automatically. Later authorized work uses that memory. Describe the feature, bug or review you need, for example:

> Fix the validation error when a customer submits **[describe the problem and how to reproduce it]**. The expected result is **[describe the behavior]**.

The framework responds in the user's language by default. [Documentação em português de Portugal](docs/pt-PT/README.md).

## Safety and context

Within an authorized task, agents may inspect code, make scoped changes, run nondestructive checks and create a development branch. Consumer project commits, pushes, pull requests, significant architectural changes, production deployments, destructive actions and material paid resources require authorization. Host sandbox and approval mechanisms remain authoritative. No planning or progress files are generated in consumer projects.

Shared facts live in `agents/<project>-context.md`; each role also reads its own `agents/contexts/<role>-context.md`. The leader owns shared decisions and coordination; writable specialists own their technical notes, while read-only reviewers propose notes for the leader to save. A first execution in an existing application analyzes and fills these files before application changes, then checks useful host integrations and requests scoped installation consent. Installation only creates pending templates. See [context management](docs/context-management.md) and [first-use onboarding](docs/onboarding.md).

Installed consumer agents, context and metadata are private local files with persistent Git exclusions. Sharing flags are rejected. Already tracked protected files block project installation/update: ignore rules cannot unpublish them, and the installer does not alter Git history or the index. Canonical definitions in this framework repository remain versionable.

## Review existing code for cleanup and optimization

The Code Cleanup & Optimization Engineer reviews code already implemented, even without a current diff. It identifies justified simplifications, duplication/dead-code candidates and performance hypotheses, with locations, tradeoffs, risk and validation requirements. It does not join empty-project setup. Review is read-only; the leader presents useful proposals and routes approved refactors to domain implementers, QA and independent review as needed. Performance gains require measurements. See [the workflow](docs/code-optimization.md).

> Review this existing module for unnecessary complexity and duplication. Propose simpler alternatives while preserving its public behavior.

## Use a task manager

Tell the leader which manager and exact project board/database to use. It verifies the connector, schema and permissions, then reads pending tasks before choosing work. With scoped authorization it can create tasks, edit details/statuses and archive or delete identified tasks. Specialists report progress to the leader; they do not write to the board independently. Existing architecture, execution and provider approvals still apply.

> Use the Notion board **[URL]** for this project. Show pending tasks and blockers. You may create the approved plan tasks and keep their statuses updated during this work.

A generic permission to manage tasks does not authorize deleting arbitrary tasks. No installation connects an account automatically or uploads private agent/context files. See the [provider-neutral workflow and Notion guidance](docs/task-management.md).

## Maintenance and validation

```sh
python3 scripts/dat.py update --platform codex --scope project --target /path/to/project --dry-run
python3 scripts/dat.py update --platform codex --scope project --target /path/to/project
python3 scripts/dat.py uninstall --platform codex --scope project --target /path/to/project
python3 -m unittest discover -s tests -v
```

Install/update preserve unmanaged files and stop on conflicting managed edits. Uninstall retains project memory. Unit tests use temporary targets; contract/simulation tests never stand in for native agent invocation. [Contributing](docs/contributing.md) explains the validation and release process.

For an opt-in check of a normal new-project conversation, run `python3 scripts/native_smoke.py --platform codex --scenario discovery --execute`. This uses the configured account and quota with a fictional brief in a temporary read-only project. It checks that the leader returns a conversational answer with discovery questions, rather than the internal JSON report, and leaves project files unchanged. It does not establish the quality of every recommendation or validate a booking integration.

`python3 scripts/native_memory_smoke.py --execute --timeout 180` tests automatic central-brain maintenance in a temporary synthetic writable project. The user prompt requests only a small code change; the test checks that prior knowledge is retained and the new behavior and refreshed timestamp are recorded without a memory reminder. It uses account quota and never edits the consumer application.

After updating canonical instructions in this checkout, use `update` for each existing project installation and start a new conversation so it can load the updated instructions. Installed copies do not change automatically when this framework's source files change.

`python3 scripts/native_phase_smoke.py --execute --timeout 240` exercises four messages in the same Codex session: a natural brief, an informational architecture question, architecture-only approval and a later deployment/cost discussion. It uses a synthetic project and emits a manual review checklist. Verify Portuguese responses, real Architect/DevOps participation, scoped approvals, proposed tasks and absence of implementation. Automatic checks cover completed responses, conversational format, questions and file hashes only; a read-only sandbox does not prove voluntary enforcement or future behavior.

[`dat/policy.py`](dat/policy.py) supplies deterministic selection and contract/quality-gate helpers for integrations and regression tests. These helpers do not launch models or grant host permissions. Sequential role simulation cannot satisfy an independent-review gate; HIGH/CRITICAL work remains blocked until a genuinely separate review is obtained.

`python3 scripts/native_onboarding_smoke.py --execute --timeout 240` tests first-use analysis in a writable synthetic existing application. It checks that application files remain unchanged and that contexts and evidence are populated; manual transcript review verifies findings and actual participation. No provider installation is exercised.

`python3 scripts/native_task_manager_smoke.py --execute --timeout 240` exercises real Codex tool calls through a temporary local MCP fixture: paginated backlog reads, task creation, status update and targeted trash. This uses account quota but no real Notion workspace.

`python3 scripts/native_optimization_smoke.py --execute --scenario existing --timeout 240` checks a normal cleanup/optimization request against an existing synthetic implementation. Use `--scenario empty` to check missing-code handling. These account-backed tests are read-only and require manual review of attribution, proposals and unmeasured claims.

## Documentation and examples

- [Architecture](docs/architecture.md), [orchestration](docs/orchestration.md), [agent reference](docs/agents.md)
- [Installation](docs/installation.md), [context management](docs/context-management.md), [security](docs/security.md)
- [Compatibility](docs/compatibility.md), [official platform sources](docs/platform-sources.md)
- [Ten worked usage examples](examples/README.md)

Native behavior varies by product surface, version, plan and enabled tools. ChatGPT installation produces a reusable manual export, requiring manual attachment/instructions setup. Runtime smoke tests must verify agent loading, delegation and permissions in each actual host. The compatibility document records these limits without treating generated files as executed integrations.

Contributions are welcome through reviewed changes; see [contributing](docs/contributing.md). Distributed under the [MIT License](LICENSE).
