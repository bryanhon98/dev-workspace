# Personal Codex setup — global rules

Purpose: keep my personal Codex instructions, skills, plugins and MCP setup portable between my laptops using https://github.com/bryanhon98/dev-workspace. This backup is not a developer biography, coding-style guide or project directory. These rules are self-contained and apply across projects when loaded as user instructions.

## Global by default

Install all my custom skills and downloaded skills for user-wide use by default, unless I explicitly request project-only scope. In current Codex, user skills live under ~/.agents/skills/<skill-name>/; inspect existing installations and current client support before choosing a path. Avoid duplicate copies with the same skill name. Use the supported user/account scope for plugins and MCP services when available; report any scope or authentication limitation instead of assuming it works globally. Keep draft skills outside active discovery folders until inspection and testing finish.

## Inspect every skill before activation

This applies to new skills, my own custom skills, updates, restored copies and bundled plugin skills.

1. Resolve the exact source and version and stage the files outside active installation folders. Do not execute candidate scripts or hooks during initial inspection.
2. Run local static-only SkillSpector on every directory containing SKILL.md, including nested skills in a plugin. Keep the scanner version, scan reports, coverage and hashes of the inspected files. Do not send source to an external model without my explicit authorization.
3. Review scripts, hooks, plugin manifests, dependencies, permissions and MCP services separately. SkillSpector checks do not certify arbitrary code or remote services. If a package has no skills, record that the skill scan is not applicable and complete the supporting-code review.
4. A finding, failed or incomplete scan, missing report or unavailable scanner blocks activation. Explain the exact issue. Obtain my approval for a specific exception, never silently suppress findings. A prior recorded exception only applies to the unchanged version, hashes and finding it covers; preserve it as an exception and re-scan on restoration. New findings require new approval.
5. Review the scanner's source before installing or updating the scanner itself. If inspection tools are unavailable, finish independent work and report the blocker; do not claim installation is complete.
6. After inspection, perform appropriate behavior checks in an isolated test location before global activation. Verify the installed files and actual discovery/activation. Do not overwrite local modifications without reconciling them.

## Creating and updating my skills

Whenever I ask to build, create, improve or update a skill, use a skill-creation workflow. Prefer Anthropic's official skill-creator when its reviewed version is installed and compatible: https://github.com/anthropics/skills/tree/main/skills/skill-creator. Check its actual availability; do not pretend a Claude slash command exists in Codex. Codex's built-in $skill-creator is an alternative when available. If neither is callable, use the following workflow directly and disclose that fallback. Installing any third-party creator also requires the inspection above.

- Use the conversation to identify the job, when the skill should and should not trigger, required inputs, expected outputs and success criteria. Ask only for missing essentials.
- Draft a focused SKILL.md with name and description metadata. Make the description explain when to use the skill. Keep the main instructions concise; put optional detail in references and use scripts/assets only where useful.
- Create realistic test prompts, including relevant edge cases and cases that should not trigger. Inspect custom scripts before running them. Check output quality and measurable requirements where appropriate.
- Compare against the previous version when updating, or a baseline without the skill when useful. Review results, improve the draft and rerun affected checks. Do not substitute a security scan for behavior testing or claim unperformed evaluation.
- Complete SkillSpector inspection, install globally, verify the installed copy, then save the source, tests, review summary and exact version in the backup repo. Preserve upstream licenses for copied third-party material.

## Sync verified changes to GitHub

Whenever Codex adds, changes or removes my personal instructions, skills, plugins, tools or MCP setup, update bryanhon98/dev-workspace after verifying the change. This is standing authorization for routine sanitized backup commits; do not repeatedly ask me whether to save them.

Locate a checkout or use the authenticated GitHub connector. Read the current remote version before publishing, preserve unrelated changes and never force-overwrite another laptop's work. Inspect the exact files being published; never upload my whole home directory or raw Codex configuration. If a rule changes, update global/AGENTS.md and apply its managed section to this device too.

Keep inventory.json current with source, exact version, user scope, audit status and restoration method. Keep reviewed custom skill sources and redistributable downloaded skills under skills/, with hashes and audit evidence. Keep sanitized MCP templates under mcp/ and plugin setup details in the inventory. Record successful installs, updates and removals in installations/<device-alias>.jsonl after verification. Use a stable non-sensitive alias for each device. Record timestamp with timezone, action, component, exact version, scope, verification and audit reference. Log rule changes in Git history. GitHub is the primary portable record; the existing installation-log chat is only an optional secondary destination if available.

Confirm the resulting remote commit before saying the backup is synced. If offline or blocked, keep the reviewed local changes and report them as unsynced. Do not claim installation, scanning, logging, restoration or synchronization without evidence.

## Fresh laptop and privacy

On "set up this laptop using this repo", install these global rules first, then follow the repo's setup procedure to inspect and restore the saved components. Explain missing payloads or account login steps. Global availability does not mean every skill is invoked on every request.

Never publish passwords, tokens, private keys, cookies, credential files, personal chat/memory databases, employer code or internal configuration. Connection templates use environment-variable names for secrets; log in separately on each device. The policy guides Codex work; it cannot intercept manual installations or background marketplace updates. On "sync my setup", inspect such changes, review unknown versions and reconcile them before recording them as reviewed backups.
