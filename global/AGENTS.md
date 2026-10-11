# Personal Codex setup rules

Backup repository: https://github.com/bryanhon98/dev-workspace. Keep personal instructions, skills, plugins and MCP setup portable across my devices. These rules are copied into my global Codex instructions and apply across projects.

## Setup starts with my choices

When I say "setup my Codex using this repo" (or similar), read the current inventory and show all saved skills, plugins and MCPs with a short purpose, source, readiness and authentication/manual-setup requirements. Distinguish a listed component from a reviewed, restorable copy. Say when a category is empty. Ask which skills I want: specific names, all eligible skills, or none. Wait for my choice; the setup request alone is not a choice to install everything. Previously stated choices remain valid.

Explain that the repo's setup rules will be restored into the target device's global Codex instructions. List plugins and MCPs with installation links and login/setup steps for me to handle manually. Do not automatically install or authenticate those services, even when I select all skills. Verify my completed manual installations before logging them. Report if the chat cannot reach the intended laptop rather than substituting a cloud installation.

Install selected custom and downloaded skills in user-global scope by default (currently ~/.agents/skills/<name>/), unless I explicitly request project-only scope. Check the client's supported paths and reconcile duplicate or locally modified copies. Global availability does not force invocation on every request. List any dependencies or credentials a skill needs; do not assume every skill is self-contained.

## SkillSpector must be ready first

Before installing, updating or restoring any selected skill, verify the actual SkillSpector scanner is installed and can run on the target device. If absent, inspect its pinned source/bootstrap and dependencies, install it first, and verify its version and a local static scan before proceeding. A SkillSpector instruction/skill file alone is not the scanner. Reuse a working reviewed installation; do not reinstall it unnecessarily. This prerequisite also applies to Anthropic's skill-creator and my custom skills. If scanner setup or verification is blocked, stop skill activation and report the blocker. Restore instruction text and prepare manual plugin/MCP checklists independently. Choosing no skills does not require installing the scanner.

## Inspect before installing, updating or restoring skills

- Resolve the exact source/version; stage files outside active skill directories. Do not execute candidate scripts/hooks during initial inspection. This applies to custom skills and every nested SKILL.md in plugins too.
- Run local static-only SkillSpector for each skill. Retain scanner version, coverage, reports and file hashes. Do not send source to an external model without my explicit authorization.
- Separately review scripts, hooks, dependencies, plugin permissions and MCP services. A skill scan does not certify other code/services; record not-applicable coverage honestly.
- Findings, failed/incomplete scans, missing reports or a missing scanner block activation. Explain the issue and obtain approval for that specific exception. Preserve prior exceptions only for the same version, hashes and finding; re-scan restored copies. New findings need new approval. Review the scanner's source/bootstrap before installing/updating the scanner itself.
- After inspection, perform appropriate isolated behavior checks; install only reviewed content, verify hashes and discovery, and preserve modified local copies until reconciled. Never label unperformed checks or incomplete installation successful.

## Creating or improving my skills

Use a creator workflow whenever I ask to build, create, improve or update a skill. Use Codex's built-in $skill-creator when available. Anthropic's official skill-creator is deferred; do not install it unless I ask again. Do not pretend Claude's /skill-creator command is installed in Codex. If neither creator is callable, disclose that and follow this workflow directly; installing a third-party creator requires the checks above.

Establish the job, trigger/non-trigger cases, inputs, outputs and success criteria from context; ask only for missing essentials. Draft concise SKILL.md instructions with name/description metadata and only useful supporting references/scripts/assets. Inspect scripts before executing them. Try realistic prompts and edge cases, compare with the prior version or a baseline when useful, improve and retest affected behavior. Complete SkillSpector review before global activation. Save custom source and tests, exact versions/hashes and review evidence in the backup. Preserve licenses for copied third-party files.

## Save verified changes to GitHub

After Codex adds, changes or removes my personal instructions, skills, plugins, tools or MCP setup, update bryanhon98/dev-workspace. Routine sanitized backup publishing is already authorized. Read the latest remote head, review the exact diff, preserve other devices' edits and never force-overwrite them. Use authenticated Git or the GitHub connector. Do not export the whole home directory or raw configuration.

Keep inventory.json current: source, github_url, version, scope, purpose, audit/readiness status, required tools and manual/auth requirements. Every saved skill must have a real GitHub source link: the original repository/subdirectory for downloaded skills, or its actual location in bryanhon98/dev-workspace for my custom skills. Preserve the upstream link and exact revision when copying a skill into this backup; never invent a source URL. Save reviewed skills under skills/custom/ or skills/external/, inspection summaries under audits/, and sanitized MCP templates under mcp/. Create these folders only when there is real content. After verified component installs/updates/removals, append installations/<device-alias>.jsonl records with timestamp/timezone, device alias, action, component/kind/version/scope, github_url, verification, audit_ref and exception_ref when applicable. After creating a custom skill, save its source and tests and record a created event with its actual draft/tested/reviewed state; a creation event is not an installation. Drafts remain inactive and not restorable until reviewed. Record a separate installed event only after verification. Rule changes are recorded in Git history. GitHub is the primary record; the old installation-log chat is optional.

For rule edits, update the appropriate global source file and apply the managed section on the target device when requested; do not silently restore rules the user intentionally cleared. Start a new session to load changed global instructions. Verify the remote commit before claiming sync; keep local changes and report unsynced status when blocked. Existing instruction text outside the managed section must be preserved.

Never publish credentials, tokens, keys, cookies, personal chat/memory databases, employer code or internal configuration. Use environment-variable names for secrets and separate device logins. Manual installs and marketplace auto-updates are not intercepted: on a sync request, inspect/reconcile unknown versions before marking them reviewed or installed.
