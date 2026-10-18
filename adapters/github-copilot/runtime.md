## GitHub Copilot runtime

Select dat-team-leader as the main agent in a supporting client, then use native
custom-agent delegation when exposed. Copilot CLI supports `/agent` selection and
`copilot --agent dat-team-leader --prompt "YOUR TASK"`. Restart CLI after installing.
Repository profiles live in .github/agents; user profiles in ~/.copilot/agents apply
to CLI. The latter does not install profiles into every IDE or the cloud agent.

Cloud discovery requires the repository profiles to be committed and merged into
the default branch; local installation alone does not publish them. Authorize
the relevant Git/PR workflow before assigning cloud implementation tasks.
IDE/cloud/CLI tools differ. Read-only profiles allow only read and search aliases,
excluding shell, edit, delegation, and MCP tools. Shared instructions are embedded
because CLI subagents do not inherit repository custom instructions by default.
If native delegation is unavailable, state that and use sequential role passes.
