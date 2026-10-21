# Worked examples

These are synthetic usage scenarios, not transcripts or claims that models ran. Native IDs have the prefix `dat-`. The Team Leader supplies an in-memory task contract with `TASK_ID`, `OBJECTIVE`, `CONTEXT`, `CONSTRAINTS`, `FILES`, `ACCEPTANCE_CRITERIA`, `PERMISSIONS`, `DEPENDENCIES` and `EXPECTED_OUTPUT`. Specialists return the report fields defined in [orchestration](../docs/orchestration.md). Do not write per-task planning or protocol files in consumer projects.

Every scenario uses real host delegation only when available. Otherwise the leader explicitly labels sequential role passes. A second role pass in the same conversation cannot satisfy an independent review gate.

## 1. New project

> Team Leader: I want to start a project from scratch. My rough idea is a small internal inventory application. Help me clarify the users, essential workflows and MVP scope before proposing how to build it. Ask only important unanswered questions, a few at a time. Use synthetic data and no paid resources.

`NEW_PROJECT`, initial MEDIUM risk subject to the clarified scope. The target can contain only Git metadata and installed team files; no source code or chosen stack is required. The Team Leader uses the brief first and asks focused questions only for material gaps, such as who maintains stock, which stock movements the MVP needs and whether existing systems must be integrated. These are examples of relevant gaps, not mandatory questions if already answered. The user can answer in ordinary language without preparing a delegation envelope.

The leader summarizes the agreed brief and proposed acceptance criteria in the conversation. Software Architect recommends the smallest suitable design using the known constraints, with `FILES: []` when no source exists. Resolve required material choices before scaffolding application code or installing application dependencies; proposals are not approvals. A complete brief with approved technology and implementation scope can proceed without another interview or repeated approvals.

After the relevant decisions are resolved, Backend Developer and Frontend Developer implement agreed boundaries; Database Engineer joins if persistence requires specialist work. QA checks acceptance flows and Code Review Engineer inspects the actual diff. Independent implementation tasks may run concurrently only after contracts and isolated ownership exist. The leader checks actual test output and consolidates approved stack decisions in context. It does not create a consumer planning file or report discovery alone as an implemented application.

## 2. Existing project

> Team Leader: add a reversible UI label change to this existing application. Preserve its framework, style and public contracts.

`EXISTING_PROJECT`, LOW risk, explicit area `frontend`. The leader reads existing instructions and relevant components; Frontend Developer changes the label and performs localized validation. A full architecture audit, database work and all-team review are unnecessary. Report exact files and checks. Update memory only if durable context changed.

## 3. Frontend and backend feature

> Team Leader: add an order search form and an API search endpoint using the existing database schema. Invalid dates must show a helpful error; authorization must match current order access rules.

`FEATURE_DEVELOPMENT`, MEDIUM or HIGH after inspecting access impact. The leader agrees the request/response contract. Frontend Developer owns form files; Backend Developer owns API files. Database Engineer is activated only if query design warrants it, Security Engineer if authorization changes. QA verifies empty, error, loading and success states plus unauthorized requests; Code Review Engineer reads the diff independently when available. Integration and relevant tests precede completion. No new library or schema is assumed necessary.

## 4. Bug fix

> Team Leader: reproduce the crash caused by an empty quantity field, identify its cause and implement the smallest correction.

`BUG_FIX`, risk determined by actual impact. Frontend or Backend Developer is selected from the reproduced failure location. QA provides a focused regression scenario where useful. The leader routes a failing check back to the responsible implementer, requests correction and reruns the relevant test. Repeated unsuccessful corrections trigger reassessment and a concrete blocker report. Do not invent reproduction when the environment cannot execute it.

## 5. Code review

> Team Leader: review the current diff for correctness and regressions. Do not modify code.

`CODE_REVIEW`. Code Review Engineer reads the diff and relevant source, rather than relying on the implementer's summary. Findings include location, evidence, impact, severity and a suggested correction. The leader rejects cosmetic preference lists and unsupported vulnerabilities. Review is read-only; requested fixes require a subsequent authorized implementation scope. In sequential fallback the leader states that the review was not independent.

## 6. Architecture review

> Team Leader: assess whether our module boundary causes the measured build and deployment coupling. Preserve the current stack; propose changes before implementing them.

`ARCHITECTURE_REVIEW`, read-only. Software Architect inspects the actual module structure and available measurements, distinguishing verified problems from inferred risks and optional improvements. The leader compares options with evidence and seeks approval for significant structural changes. No rewrite, framework replacement or new service is silently introduced.

## 7. Security audit

> Team Leader: perform a read-only security review of the authentication flow and dependencies. Do not run intrusive tests or connect new services.

`SECURITY_AUDIT`, HIGH risk assessment context. Security Engineer checks concrete code paths, authorization boundaries, secrets handling and permitted dependency evidence. Backend Developer is consulted only when necessary to explain implementation behavior. The leader reports confirmed findings separately from suspicions, requests authorization for any intrusive operation and never treats an unavailable scanner as a passing scan. Remediation is a separately scoped implementation with independent review where required.

## 8. Database optimization

> Team Leader: investigate the slow order query using a sanitized execution plan. Propose a reversible change without executing production DDL.

`DATABASE_OPTIMIZATION`. Database Engineer inspects query, schema, indexes and execution evidence; Backend Developer joins only if query generation or transaction use changes. QA compares representative behavior and performance in an authorized environment. The leader requires data integrity, compatibility and rollback assessment for migrations. A production index or destructive operation waits for authorization; a proposed improvement is not reported as a measured speedup.

## 9. Deployment

> Team Leader: prepare a staging deployment using the existing delivery workflow. Run the available checks and present a production deployment action for authorization.

`DEPLOYMENT`, risk based on service impact. DevOps Engineer inspects the real pipeline, credentials availability and environment. QA checks staging when authorized; security input is added when exposed configuration warrants it. Production and material paid resources require explicit authorization. The leader verifies test evidence, rollback and operational impact before proceeding, and reports a missing deployment integration as blocked. A generated configuration is not a completed deployment.

## 10. Continue after a new session

> Team Leader: continue the interrupted order search task. Read shared and local context, inspect the worktree, confirm what remains and resume within the existing authorization.

`EXISTING_PROJECT` followed by the resumed task's mode. The leader reads `.ai-team/context.md` and `.ai-team/context.local.md`, verifies stale decisions against actual code and inspects unfinished changes before selecting specialists. It reconciles reports and permissions, retests uncertain results and resumes dependencies. Use `memory show` and `--expected-hash` for consolidated updates; do not overwrite another writer. No prior status or remembered approval substitutes for evidence.

## Deterministic policy example

Run from the framework checkout:

```sh
python3 scripts/dat.py select --mode FEATURE_DEVELOPMENT --risk MEDIUM --areas frontend backend
```

The same deterministic contract is available as Python:

```python
from dat.policy import select

policy = select(
    "FEATURE_DEVELOPMENT", "MEDIUM", areas=("frontend", "backend"),
    delegation=False, parallel=False,
)
assert policy["specialists"] == [
    "frontend-developer", "backend-developer", "qa-engineer", "code-review-engineer"
]
assert policy["execution"]["strategy"] == "sequential_role_simulation"
assert policy["execution"]["review_independence_possible"] is False
```

This helper proposes specialists and gates from explicit inputs. It performs no model invocation, grants no permission and supplies no proof of completed work. `review_independence_possible` describes capability only; it never confirms that a review happened. `quality_gate` fails closed until required gate results and report evidence are supplied; HIGH/CRITICAL also require actual independent review, confirmed separately by the caller after inspecting evidence.
