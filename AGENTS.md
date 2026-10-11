# Maintain the personal Codex setup

This repo exists only to sync and restore personal instructions, skills, plugins and MCP setup across devices. Read global/AGENTS.md and follow its installation, skill-authoring and GitHub logging rules. It is the canonical self-contained global policy; do not duplicate it in other documents.

For "set up this laptop", follow setup/SETUP.md. For creating or updating a skill, use the creator workflow in global/AGENTS.md and the official sources in setup/SKILL-CREATION.md. Skills are user-global unless the user explicitly asks otherwise.

After verified setup changes, publish sanitized changes to bryanhon98/dev-workspace under the user's standing authorization. Preserve other devices' work and report any unsynced changes. Do not commit secrets, company data, personal profiles, unrelated coding preferences or application projects.

When changing setup tooling, run python3 -m unittest discover -s tests -v and git diff --check. Keep documentation honest about implemented features and missing restore payloads. Never label inventory-only entries as installed, audited or restorable.
