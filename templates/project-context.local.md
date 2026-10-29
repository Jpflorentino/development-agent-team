# Private local project context

Legacy archive template for `.ai-team/context.local.md`; new installations use shared `agents/<project>-context.md` memory plus role-specific files in `agents/contexts/`. Keep excluded from Git and review before any upload. Private does not mean a secret store: never save passwords, API keys, tokens, credentials, private keys or unnecessary personal data. Store compact operational recovery facts only. The Team Leader consolidates proposals and verifies them against the current worktree, environment and permissions.

Use the same section keys as shared context so maintenance tooling can inspect both consistently. Keep durable shareable facts in shared context instead of duplicating them here. Empty sections are permitted. Use dated evidence labels (`VERIFIED`, `INFERRED`, `PROPOSED`, `APPROVED`, `IMPLEMENTED`, `TESTED`, `BLOCKED`) honestly.

## PROJECT

<!-- Confirm the project/root identity to prevent recovery into the wrong repository. -->

## TECH_STACK

<!-- Relevant local runtime constraints; no credential values or environment dumps. -->

## ARCHITECTURE

<!-- Only private local operational facts needed to interpret the shared architecture. -->

## COMPONENTS

<!-- Local-only references relevant to recovery; avoid unnecessary personal paths. -->

## CONVENTIONS

<!-- Local workflow constraints, if necessary and not duplicated. -->

## CONSTRAINTS

<!-- Actual unavailable tools, restricted permissions or environment limitations. -->

## DECISIONS

<!-- Relevant local authorization scope and source; no invented approval or duplicate history. -->

## CURRENT_STATE

<!-- Unintegrated local work, observed validation state and interruption recovery facts. No protocol/task files or progress diary. -->

## KNOWN_ISSUES

<!-- Concrete local blockers and dependency state that must be rechecked next session. -->

## REFERENCES

<!-- References needed for recovery; redact sensitive values and minimize private information. -->
