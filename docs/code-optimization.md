# Existing-code cleanup and optimization

## Purpose and role boundary

`code-optimization-engineer` (Code Cleanup & Optimization Engineer) reviews code that is already implemented. It can inspect a stable module, component, service or workflow without a current diff or Git history. This is separate from `code-review-engineer`, which independently checks consequential defects/regressions in changes and their surrounding code. The optimization role produces a focused improvement proposal; approved changes are implemented by the relevant domain owners.

Use it for cleanup, simpler implementation, duplication, dead-code candidates, redundant state, avoidable work, allocations and demonstrated performance problems. Do not activate it for empty projects, initial stack decisions, scaffolding, every routine change or stylistic preference. Actual source in scope is a prerequisite; missing application code is a coverage blocker. Never create a sample application merely to manufacture review findings.

## Review before changing code

1. The leader identifies the existing paths/flow, desired outcome, known constraints and actual authorization. Read shared memory and the role's technical context, then relevant source, callers, contracts and tests. Initial onboarding remains analysis/context writing only; it can record relevant optimization observations without modifying the application or turning first use into an unrequested whole-repository audit.
2. Assign bounded read-only analysis to the optimization role. Native tools must retain its read-only restrictions. Where independent delegation is unavailable, explicitly label a sequential role pass. Installed profiles or a new context filename do not prove an agent ran.
3. Inspect implementation and real dependencies, including dynamic framework entry points, registries, reflection, exports, plugins, build tooling and generated callers. A text search with no matches is insufficient to prove code is unused. Preserve public contracts, validation/security checks, ordering, errors, data integrity, side effects and business rules.
4. Return a small prioritized set of actionable candidates. Each includes actual source location, current behavior/problem, proposed simpler alternative, concrete benefit, affected consumers/contracts, tradeoffs, risk/effort, prerequisites and required tests or measurements. A shorter expression alone is not a benefit. Explain unsupported deletion claims, missing tests and uncertain behavior instead of assuming safety.
5. Distinguish maintainability cleanup from performance. Algorithmic reasoning may identify avoidable work; actual latency/CPU/memory gains require a representative baseline, workload/data sizes, method, repeatable before/after results and limits. Without those, label a hypothesis and propose the experiment. Never invent benchmark values or percentages. The leader/QA runs authorized tests/profiling in an appropriate environment and returns outputs; the read-only specialist does not gain shell or production access.

The leader explains the findings in the user's language, including a minimal implementation plan and acceptance criteria. Review permission authorizes no edits. An existing scoped instruction to implement specific refactors can cover execution; reuse it rather than asking again. Otherwise present the concrete proposal for approval before application changes. Significant architecture/API/technology changes still involve Architect and their own actual approval.

## Implementation, validation and follow-up

After execution authorization, assign exclusive file ownership to Frontend/Backend/Database or another appropriate implementer. Keep patches focused, preserve the established stack, avoid speculative abstractions, broad formatting, unnecessary dependencies or rewrites. Do not remove tests, compatibility code or safeguards simply to make code shorter. Preserve unrelated user work.

Establish a meaningful behavior baseline before refactoring; add characterization/contract tests where necessary for material uncertainty. Run relevant existing tests and risk-appropriate validation after the change. Performance claims need the actual comparison, not only passing tests. Mark unrun checks and unresolved regressions as limitations/blockers; fewer lines or a successful build alone does not prove improvement.

Revisit original findings to establish what was implemented and verified. Independent Code Review remains separate where the risk gate requires it; the optimization role's recommendations or sequential self-review do not satisfy that gate. Do not say a refactor was delivered when only its review is complete. Report actual before/after behavior, maintenance benefit, measured performance if any, tests and remaining risks.

If an external task manager is configured, the leader may propose or maintain scoped follow-up tasks under its existing grant. An analysis task can be completed when the review is accepted, while proposed implementation remains pending; never mark the implementation done from a completed review. Specialists do not write remote tasks.

## Memory and upgrades

The technical file is `agents/contexts/code-optimization-engineer-context.md`, with BASELINE, CLEANUP_CANDIDATES, PERFORMANCE_EVIDENCE, REFACTOR_PLAN and VALIDATION_GAPS sections. The role reads it plus shared facts; because the role is read-only, it returns notes for the leader to save. Record inspected scope/sources, justified candidates, measured/unmeasured claims, approval references and actual resolution. Keep all context/profile files private and avoid copied source/transcripts/secrets.

Updating a ten-role installation creates the new profile/context and adds a pending role entry to existing schema-1 onboarding metadata. Prior role notes/statuses, integration records and extra metadata are preserved. Pending analysis remains pending; no fake participation or automatic implementation approval is introduced. Unsupported record shapes stop for reconciliation rather than being overwritten. Repeated updates are idempotent.

## Natural requests

- “Revê o código já implementado deste módulo e propõe uma forma mais simples de o manter.” Analysis only; no need to provide a diff.
- “Procura duplicação e trabalho desnecessário neste fluxo, preservando o comportamento.” Bounded existing-code assessment; distinguish findings from performance measurements.
- “Aplica apenas as melhorias 1 e 2 que acabámos de aprovar e verifica regressões.” Authorized domain implementation, validation and risk-appropriate independent review.

The workflow is installed guidance executed by the host; routing helpers do not launch models or enforce every tool permission. Native read-only restrictions and actual authorization remain authoritative.
