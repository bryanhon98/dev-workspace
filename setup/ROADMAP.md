# Completing the personal setup backup

- Import and inspect the prepared codex-setup bundle from the Mac, preserving audit exceptions and upstream licenses.
- Populate skills and plugins inventories with exact sources, versions, review status and restoration method. Include pending items without marking them approved.
- Add sanitized MCP templates and required environment-variable names. Keep actual endpoints and secrets local where private.
- Build and test a setup command that merges user instructions, uses device aliases, verifies skill hashes, handles review blockers and writes installation records.
- Build and test a sync command that compares manual changes, sanitizes exports and publishes against the current remote head without overwriting another device.
- Verify on a fresh temporary home and then a second device. Document separate authentication steps and unsupported account-managed components.

The policy instructs Codex to maintain this backup; these future commands will make the procedure repeatable. There is no background watcher today.
