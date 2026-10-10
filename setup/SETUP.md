# Set up this laptop

Open this repository in Codex and say: "Set up this laptop using this repo."

The agent should:
1. Read AGENTS.md, PROFILE.md, preferences/*.md and setup/POLICY.md. Inspect the device's existing Codex configuration before changing it.
2. Ask for a non-sensitive device alias if none is configured. Keep paths, usernames and credentials local.
3. Merge the personal maintenance policy and preferences into the effective Codex user AGENTS.md, preserving unrelated instructions. Store a local backup first. Use a clearly delimited managed section. Verify the resulting file; explain that new chats must load it. Do not blindly replace the whole global file.
4. Check GitHub access and SkillSpector availability. Review any missing tool before installing it. Do not activate third-party skills/plugins before the required inspection.
5. Restore only exact reviewed skill versions from the inventory; re-scan and verify hashes. Report pending and exception-approved components separately. Do not automatically approve recorded findings on a different version.
6. Install/reconnect plugins and MCP services using supported mechanisms. Resolve credentials on this device; never put them in GitHub. Explain unavailable integrations rather than claiming restoration.
7. Record verified successful installs under installations/<device-alias>.jsonl and publish sanitized changes. Confirm the commit and list remaining setup blockers.

## Current status

This repository contains the policy and setup procedure, not a complete automated installer. The tested codex-setup bundle from the other chat is still on the Mac at Documents/Codex/dev-workspace-portable; it has not been imported here. Until that bundle and reviewed inventories are imported, skills/plugins cannot be fully restored from this repo.
