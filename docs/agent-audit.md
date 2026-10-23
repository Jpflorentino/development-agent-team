# Agent functioning audit — 23 October 2026

Scope: the ten canonical roles, shared policy, native adapter generation, delegation/report helpers, project-context rules, diagnostics and the Codex conversation test. Baseline source revision: `78a826c`, followed by the local fixes described below. Raw account transcripts and consumer source remain outside this repository.

## Findings, in priority order

| Severity | Finding | Evidence / action | Status |
| --- | --- | --- | --- |
| HIGH | Approval of architecture and mandatory delegation are behavioral, without a pre-tool execution interceptor. | Native hosts do not automatically call `dat.policy`. Instructions and helper booleans cannot prevent a broadly permitted write. | Open design limitation; documented explicitly. |
| HIGH | Unresolved `high` findings and malformed severity values could pass the quality helper. | Added known-severity validation and case/whitespace normalization, with blocking and malformed-value regressions. | Fixed locally. |
| MEDIUM | Task context accepted `None`, booleans, numbers and empty data. | Require nonempty text or a nonempty structured object; preserve valid new-project tasks with no source files. | Fixed locally. |
| MEDIUM | The native phase test rejected a valid explanation because it contained no question mark. | Make question-presence validation optional for explanatory/approval phases, while still rejecting internal JSON and failed turns. | Fixed locally. |
| LOW | Diagnostics did not warn when there was no managed installation. | Add an explicit warning; an intact installation remains a file-integrity observation. | Fixed locally. |

## Architecture diagnosis

This repository installs role instructions and provides deterministic helpers. The host model chooses and executes native tools. There is no hidden second model pass or background model service in the Python implementation; account-backed model calls are confined to the explicit native-test scripts. Host internals remain outside this audit.

The main operational gap is therefore at tool execution: architecture/task/deployment approvals can be required by instructions, but the framework does not intercept each tool call. A mutable `APPROVED` memory label or a caller-supplied gate boolean cannot establish trusted user approval by itself. Hard prevention requires host-enforced read-only planning or a separately designed integration that checks trusted approval events before granting execution. Such a runtime change has not been implemented by this audit.

## Role and format checks

All ten definitions and native renderings were reviewed. Team Leader handles user communication and context; Architect advises before task planning; Frontend, Backend and Database have scoped implementation ownership; UI/UX supplies design handoffs; QA owns tests; Security and Code Review return read-only findings; DevOps separates cost analysis from authorized operations. Shared instructions limit analysis-only assignments even for normally writable implementation roles.

Main-conversation instructions omit internal report field schemas; delegated profiles retain the structured contracts. Claims about real child execution, profile loading and independent review remain distinct. Native profile restrictions do not provide complete host isolation by themselves. Installation metadata does not demonstrate execution.

## Verification

- **85 local tests passed** on macOS/Python 3.12.14; structural validation returned no errors.
- The new regressions cover severity normalization/malformed values, task context, missing-installation warnings and valid follow-ups without question marks.
- Initial synthetic Portuguese brief: actual Architect child started and completed; leader proposed architecture in Portuguese and requested approval; no application edits observed.
- Informational follow-up: explanation continued the architecture discussion without treating the question as approval.
- Architecture-only approval: leader produced a proposed per-role task table with deliverables, dependencies and acceptance checks, then asked for execution approval; it did not dispatch implementation.
- Deployment/cost discussion: the resumed leader returned a Portuguese comparison with dated official sources, assumptions and separate authorization boundaries. The DevOps child did not produce an accepted independent result; the leader explicitly labelled the comparison as its own sequential role pass after reporting a quota failure. No independent DevOps completion is claimed.

The original fourth turn was interrupted by an account usage limit. The first two successful turns were preserved and re-assessed after correcting the punctuation heuristic; the same native session continued for the remaining phases. All four user-facing turns completed in the same native session. File hashes remained unchanged and the inspected leader tool trace contained no file-change events; observed shell commands were read-only inspection/help commands. Initial Architecture start/completion events were observed; DevOps had a start event without an accepted completion. A read-only sandbox is a backstop, not proof that a writable host would enforce the same approval boundary.

This audit does not establish live behavior for every implementation specialist, all provider failure modes, the Claude/Copilot/ChatGPT surfaces or future model responses. Existing platform limitations in the compatibility matrix remain applicable.

## Ordered follow-up

1. Keep the host-enforcement limitation explicit. If a hard approval barrier is required, review a concrete host-integration design before implementation.
2. Apply the confirmed validation fixes and keep their regression tests.
3. Retain native dispatch/completion evidence and manually inspect phase semantics; do not promote format/hash checks to a semantic guarantee.
4. Recheck installed copies after source changes. Preserve consumer application files and context; a new conversation is needed to load updated instructions.

The final deployment response completed after account usage became available again. The initial interrupted attempt and raw native traces remain private. Four-phase conversation behavior was observed in this synthetic session; the independent DevOps consultation and unrestricted-write enforcement were not verified.
