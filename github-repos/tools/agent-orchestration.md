# Agent orchestration software

[Catalog](../README.md)

Discovery library only. These are **applications**, not standalone skills or installed/approved components. Compare them with existing Tool Advisor, Superpowers, native agents, project trackers and connected apps before adding a new runtime.

## [Paperclip — paperclipai/paperclip](https://github.com/paperclipai/paperclip)

- **Classification:** Open-source, self-hostable multi-agent orchestration application (Node.js server, React UI). Not a `SKILL.md` specialist, MCP server, or replacement for Claude Code/Codex.
- **Purpose:** Coordinate agents across projects using goals, tasks, ownership, session history, recurring routines, approvals, permissions, and budgets. Supports agents such as Claude Code, Codex, Cursor and OpenClaw via adapters. The system is a management layer; agents still need their own execution environments and model access.
- **When useful:** Several agents/projects operating concurrently or unattended, recurring agent work needing clear ownership, tracked review gates, or spend controls. Start with a narrowly scoped, non-sensitive trial if these requirements become real.
- **When to skip:** A single developer primarily using Tool Advisor + Superpowers + Claude Code/Codex for one coding task at a time. Those already cover skill choice, planning, execution and review. Paperclip adds service maintenance, database/state, agent runtime configuration and permissions.
- **Risks:** More credentials and agent permissions in one service; simultaneous agents can duplicate work or consume model quotas; budget controls are not a substitute for provider-side caps and reviews. Claims about supported adapters may require local validation. Review telemetry defaults and access controls before deployment.
- **Cost/license:** MIT source; self-hosting is possible, but infrastructure and connected AI provider/CLI costs remain separate.
- **Source revision observed:** `4d5265fe7e446226a8e9612d08095626a5d99e4c` on upstream `master`; checked 2026-11-08 (Malaysia time). Refresh before any installation or recommendation.
- **Readiness:** Saved as a research lead only; not installed, not scanned, not executed, not integrated with this repository. Its own `.agents/skills` contains Paperclip-specific development skills; these are not independently selected for the user.

[Source at checked revision](https://github.com/paperclipai/paperclip/tree/4d5265fe7e446226a8e9612d08095626a5d99e4c) · [Official README](https://github.com/paperclipai/paperclip/blob/4d5265fe7e446226a8e9612d08095626a5d99e4c/README.md) · [Bundled Paperclip development skills](https://github.com/paperclipai/paperclip/tree/4d5265fe7e446226a8e9612d08095626a5d99e4c/.agents/skills)

**Library decision (2026-11-08):** Keep as an optional agent-orchestration candidate. Do not add it to the 17-skill Tool Advisor baseline or auto-install it. Reconsider when genuine concurrent multi-project agent coordination is needed.
