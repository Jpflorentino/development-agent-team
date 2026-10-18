## Codex runtime

Check the actual native subagent tool schema before delegating. When the tool can
select a custom-agent profile, use the installed dat-* name. Never add an unsupported
agent_type/profile argument or assume a name in task_name selects a profile.
If real delegation exists but the tool cannot select a custom profile, read the
installed TOML's developer_instructions or the bundled canonical role definition,
then pass the full role instructions, shared operating contract and task envelope
to a real native child. Include OBJECTIVE, CONTEXT, CONSTRAINTS, FILES,
ACCEPTANCE_CRITERIA, PERMISSIONS, DEPENDENCIES and EXPECTED_OUTPUT, plus supplied
diff/file contents where relevant. Wait for completion and inspect the evidence.
Report this as "native delegated role with supplied definition"; report named
profile loading/invocation as unverified or BLOCKED, according to actual evidence.
The fallback is still real delegated execution, not a loaded custom profile. If no
real delegation tools exist, use labelled sequential role passes and report any
required independent review as BLOCKED.

Standalone TOML profiles require a current local Codex release supporting discovery
in .codex/agents or ~/.codex/agents. No model is pinned; inherit the user's model.

Custom agents inherit parent permissions, provider, and MCP servers. Per-agent
sandbox_mode and approval_policy do not override the parent and are not emitted.
Read-only profiles disable shell, apps, plugins, and permission-request capability;
the prohibition on editing remains an instruction, not a complete filesystem or
MCP read-only boundary. For technically enforced review isolation, launch the
parent review session under the host's read-only permission profile and audit its
MCP tools. Do not describe these profiles alone as a secure read-only sandbox.
Provide the actual diff and relevant file contents in restricted reviewers' task
messages: shell-free filesystem reading is not guaranteed. Request more evidence
through the leader or use a separate read-only parent session when needed.

A generic native child receiving a supplied role definition does not automatically
apply that role's TOML feature restrictions. For reviewer fallback, run a separate
parent review session with the host's read-only permission profile and audited
MCP/tools, then delegate inside that session. In an existing writable session,
the role's no-edit instruction is behavioral only: report enforcement as BLOCKED
and do not claim the child has the installed profile's technical restrictions.
