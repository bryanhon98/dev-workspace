# My tool brain and Codex setup

This repo helps an agent choose tools for the task, compare them with your installed skills, verify current upstream versions, and remember what worked. It also backs up and restores your Codex setup.

For a substantial task, the [advisor flow](knowledge/BUILD-FLOW.md) uses an interview skill, searches the repo and external sources, proposes a compatible combination for your confirmation, then coordinates the work and tracks evidence. It applies to research, design, media, business, automation and software. You do not need to name the specialists first.

This routing depends on the host loading the repo or global instructions. The repo update alone does not change another device's global rules or install an always-running agent. Simple fixes and explanation questions keep a shorter path.

## Install the advisor core

The advisor core is approved for installation. Its [specific LP3 exception](audits/tool-advisor-1.0.0-20261102/exception.json) covers the reviewed local task-ledger writes at the recorded file hashes. Installation still runs fresh static scans and rejects changed files or findings. Normal host permissions apply.

On the device where you use Codex, clone this repo and run:

```sh
git clone https://github.com/bryanhon98/dev-workspace.git
cd dev-workspace
python3 scripts/setup.py --install-advisor
python3 scripts/setup.py --check-advisor
```

This explicit command selects **tool-advisor**, Matt Pocock's **grilling**, and Vercel's **find-skills**. It installs those skills in `~/.agents/skills`, restores managed Codex instructions, and records the checkout location for access from other projects. It stages complete payloads, runs local static SkillSpector scans, checks exact review hashes and approved historical exceptions, and refuses new findings or locally edited skill copies. Keep the checkout available as the research library.

Python 3.12–3.14, Git and network access are needed for scanner bootstrap; the installer uses an isolated scanner environment with the reviewed source revision and dependency constraints. An existing reviewed scanner can be supplied with `--scanner /path/to/skillspector`. Public-source discovery needs an available web/GitHub tool or a separately reviewed CLI; no unpinned CLI is installed by this command. Plugins, accounts and project-specific specialist runtimes retain their own setup requirements.

Start a new Codex session in your project and say:

> Use tool-advisor. I want to [describe the outcome]. Interview me, find suitable skills and specialists, and show me the combination before starting.

The main assistant uses the interview and discovery skills, presents the plan for your confirmation, then prepares selected capabilities and coordinates workers when its host supports them. It keeps task ownership, dependencies, blockers and verification evidence in the project's ignored `.tool-advisor/` directory. Resume with the same request or inspect the state with:

```sh
python3 /path/to/dev-workspace/scripts/advisor.py --project /path/to/project status
```

`--check-advisor` checks installed files, receipts, source location and managed instructions; a fresh session must still demonstrate that the host loads the skills. The first supported host is Codex. No background model service, universal prompt hook or new account authentication is installed. Isolated development checks are not evidence that your laptop has been configured.

The [bundle manifest](advisor-bundle.json) identifies exact payloads and reviews. [Ledger commands](skills/custom/tool-advisor/references/ledger.md) describe confirmation and task transitions. The full ECC/Agency collections and larger trackers are optional candidates, not core dependencies.

For advice, open the repo and ask, for example:

> I want to analyze reels and produce original videos. Compare my current skills, check the relevant upstream versions, and recommend the smallest useful combination.

Start with the [advisor workflow](knowledge/ADVISOR.md), [task routes](knowledge/ROUTING.md), [reel research index](knowledge/reel-library/index.md) and [import review](knowledge/reel-library/REVIEW.md). All three original research files are preserved with hashes: 1,083 entity records and 475 report entries. They are research leads, not 1,083 verified tools. The existing reviewed GitHub catalog and setup inventory remain separate.

```sh
python3 scripts/knowledge.py search "video transcript frames"
python3 scripts/knowledge.py show graphify
python3 scripts/knowledge.py inspect --root ~/.agents/skills --root ~/.codex/skills
python3 scripts/knowledge.py verify
```

Search retrieves evidence; the agent makes the task-specific comparison after reading relevant installed skills and current source. Inspection is read-only and limited to the machine/paths you run it on. New specialist installation follows the confirmed selection and inspection rules; no automatic removal or background refresh is configured. Dated decisions and feedback are saved under `knowledge/decisions/` for reuse.

## Set up a device

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
python3 scripts/setup.py --install-advisor # Scan/install the three core skills and rules
python3 scripts/setup.py --check-advisor   # Check the advisor installation without writing
```

Python 3 is required. The installer uses CODEX_HOME (normally ~/.codex), preserves unrelated instructions and keeps a local backup. It handles an existing global AGENTS.override.md and refuses to overwrite locally edited managed rules. If you cleared the instruction file, --install-rules restores it. If you only edited/deleted part of the managed section, reconcile it first. Start a new Codex session afterward. --codex-home PATH supports a different profile or isolated testing.

Codex personal instructions are stored in the selected machine's global AGENTS.md. Personalisation also includes other settings such as memory and personality; this repo restores the instruction text, not those account/app settings. [Official explanation](https://learn.chatgpt.com/docs/personalize).

## Current status

The catalog menu and global instruction installer remain available. The explicit advisor option installs its three reviewed core skills under their exact approved exceptions. Installation and file checks passed in an isolated cloud profile; each device still needs its own setup and fresh-session verification. Other component installation and sanitized GitHub logging are performed by Codex following the rules. Some catalog entries still need payload import/review or manual account setup. A sanitized REA MCP template is saved; verify its actual target-device setup before use. Anthropic's creator remains deferred; use Codex's built-in creator when available. An inventory entry is not evidence of installation.

When local Codex loads these global rules and has GitHub write access, it is instructed to publish a record after each verified skill creation, installation, update or removal. Creation records identify drafts separately from installed skills. A failed push must be reported as unsynced, never logged as synced.

Skills from public repositories often need no download login, but some need tools, API keys or private-repo access. Credentials stay on each device. Manual marketplace changes are recorded only after a later sync/verification; this repo is not a background watcher.
