## Claude Code runtime

Use the native Agent tool and installed dat-* profiles when the host exposes them.
The main conversation acts as Team Leader. `claude --agent dat-team-leader` selects
the native leader profile as the main session. A delegated leader must respect the
host's nesting limit and use sequential role passes if it cannot delegate further.
Use standard subagents; experimental Agent Teams are optional and not required.

Read-only profiles allow only Read, Grep, and Glob, excluding shell, editing, MCP,
and delegation tools. Other profiles inherit the parent's available tools and
permissions. Availability still depends on the installed Claude Code release.
