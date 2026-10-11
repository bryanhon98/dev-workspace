# Personal Codex setup

A private backup of my Codex instructions, skills, plugins and MCP configuration for reuse across laptops.

On a new laptop, install Codex, open this repo and say:

> Set up this laptop using this repo.

Codex follows [setup/SETUP.md](setup/SETUP.md). The working first step is `python3 scripts/setup.py`, which installs the [global rules](global/AGENTS.md) for future sessions on that device. Run `python3 scripts/setup.py --check` to verify them.

The global rules require:
- User-global scope for custom and downloaded skills unless I ask otherwise.
- SkillSpector inspection before skill installation, updates and restoration, plus separate review of supporting code.
- A creator workflow when building/updating skills, using Anthropic's skill-creator or Codex's built-in creator when available: draft, test, improve, inspect, install.
- Verified installation records and sanitized setup changes published back to this GitHub repo.

## Contents

- global/AGENTS.md: complete global policy, with no dependency on project-relative files.
- inventory.json: component sources, versions, scope and honest restore status.
- skills/: reviewed custom/external skill sources and licenses when imported.
- mcp/: sanitized MCP templates when exported.
- audits/: version-specific inspection evidence when imported.
- installations/: per-device verified component history.
- scripts/setup.py and tests/: global rule installer and its regression tests.
- setup/: new-device procedure, creator references and remaining work.

## Current limits

Global rule setup works. Actual skills/audit payloads still need importing from the Mac; the component inventory is not proof of installation or review. Skill/plugin/MCP restoration and GitHub synchronization are currently performed by Codex following the rules, not automatically by the Python command. Account connections require separate login. Manual installs and marketplace auto-updates are not intercepted.

This repo intentionally excludes personal profiles, Java preferences, application projects, credentials and company information.
