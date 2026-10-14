# My Codex setup

Open this repo in Codex on the laptop you want to configure and say:

> Setup my Codex using this repo.

Codex should:
1. Show the saved skills, plugins and MCPs, including what needs review, login or manual setup.
2. Ask which skills you want: choose names, all eligible skills, or none. Wait for your choice.
3. Restore your global setup rules, then install/verify SkillSpector first and use it to inspect your chosen skills before installing them globally. "All" never skips a blocked scan.
4. Give you plugin/MCP links and login instructions for manual setup.
5. Verify successful installs and save their records to this GitHub repo.

Additional options: [reviewed GitHub catalog](github-repos/README.md). It records conditional recommendations and omissions; candidates enter the setup inventory only after you choose them and the required review is completed.

## The files you might edit

- inventory.json — the component catalog, GitHub source links, prerequisites and restore status.
- global/AGENTS.md — setup, SkillSpector, skill-creation and GitHub-sync rules.

AGENTS.md guides Codex inside this repo. scripts/setup.py and tests/ implement and test global instruction setup. Skill files, inspection receipts, MCP templates and device logs get their own folders when real content is added.

## Commands

```sh
python3 scripts/setup.py                  # List choices; changes nothing
python3 scripts/setup.py --install-rules  # Restore setup rules only
python3 scripts/setup.py --check          # Check the installed instructions
```

Python 3 is required. The installer uses CODEX_HOME (normally ~/.codex), preserves unrelated instructions and keeps a local backup. It handles an existing global AGENTS.override.md and refuses to overwrite locally edited managed rules. If you cleared the instruction file, --install-rules restores it. If you only edited/deleted part of the managed section, reconcile it first. Start a new Codex session afterward. --codex-home PATH supports a different profile or isolated testing.

Codex personal instructions are stored in the selected machine's global AGENTS.md. Personalisation also includes other settings such as memory and personality; this repo restores the instruction text, not those account/app settings. [Official explanation](https://learn.chatgpt.com/docs/personalize).

## Current status

The catalog menu and global instruction installer work. Component installation and GitHub logging are performed by Codex following the rules; the Python command does not install skills. Existing entries still need payload import/review or manual account setup. No MCP definitions are saved yet. Anthropic's creator is deferred at the user's request; use Codex's built-in creator for now; Ponytail's source is identified and its review decision is recorded in the GitHub catalog. An inventory entry is not evidence of installation.

When local Codex loads these global rules and has GitHub write access, it is instructed to publish a record after each verified skill creation, installation, update or removal. Creation records identify drafts separately from installed skills. A failed push must be reported as unsynced, never logged as synced.

Skills from public repositories often need no download login, but some need tools, API keys or private-repo access. Credentials stay on each device. Manual marketplace changes are recorded only after a later sync/verification; this repo is not a background watcher.
