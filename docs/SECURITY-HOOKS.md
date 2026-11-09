# SkillSpector: minimal security gate and optional native hooks

This repository uses **NVIDIA SkillSpector** as a scan-before-activation guard for agent skills in **Codex and Claude Code**. The scanner is not an agent, an audit database or a substitute for operating-system permissions. Historical per-skill approval JSON and raw scan archives are not required by the current installer.

## 1. Install the scanner on the actual device

Follow [NVIDIA's official instructions](https://github.com/NVIDIA/SkillSpector). For CLI-only usage with uv:

```powershell
uv tool install git+https://github.com/NVIDIA/skillspector.git
skillspector --version
```

Review the scanner's source and bootstrap trust; this command installs executable third-party software. The repository does **not** execute the command or install SkillSpector on your PC. The scanner version in the CLI is checked when installing skills. The installer does not claim to authenticate the scanner binary's provenance merely by its name.

The primary security boundary is the **controlled installer**, which stages the actual contents and runs `skillspector scan ... --no-llm --format json --fail-on-incomplete --min-coverage 100`. It parses stdout to work on Windows. No persistent scan reports are written.

For the original 17-skill baseline:

```powershell
python scripts/setup.py --plan-advisor
python scripts/setup.py --install-advisor --host codex
python scripts/setup.py --install-advisor --host claude
python scripts/setup.py --check-advisor --host codex
```

For an additional user-selected skill, first download it into a **temporary inactive directory** (for example a subfolder inside a cloned Git repo), then:

```powershell
python scripts/install_selected_skill.py --host claude --name example --source .\incoming\example
```

Replace `example` and the source path with the actual skill name and staged path. The single-skill installer refuses existing destinations and does not overwrite local modifications. For upgrades, reconcile/remove the existing skill separately only after preserving user data and confirming the desired replacement. Do not execute untrusted installation scripts as a staging step.

**Policy:** complete SAFE scans pass; LOW/MEDIUM findings are reported; HIGH/CRITICAL or `DO_NOT_INSTALL` findings, malformed/failed scans, suppressed findings or incomplete coverage block. Static scanners may miss real malware or report false positives. Handle dangerous lower-severity behavior conservatively.

## 2. Optional PreToolUse hooks

On each device with Codex and/or Claude Code, opt in by inspecting the existing settings and running:

```powershell
python scripts/setup_security_hooks.py --host codex --install
python scripts/setup_security_hooks.py --host claude --install
python scripts/setup_security_hooks.py --host codex --check
python scripts/setup_security_hooks.py --host claude --check
```

The setup script merges, rather than replaces, existing `PreToolUse` hook settings at:

- Codex: `~/.codex/hooks.json`
- Claude Code: `~/.claude/settings.json`

It checks existing hooks, refuses malformed configurations, and backs up any pre-existing settings to a `.before-dev-workspace.bak` file on first change. Repeated installs are idempotent. If an existing managed security hook differs, reconcile manually instead of silently overwriting it. These hooks are **not** enabled merely by updating this GitHub repository.

The hook uses the current host's supported synchronous `PreToolUse` event and exit code 2 (stderr reason) to block recognized direct capability installations and writes to active skill/plugin paths. Its scope includes common CLI manager commands and file edits, while ordinary application repository clones remain allowed.

**Known interception limits:** Hooks cannot observe all hosted tools, process APIs, shell obfuscation, external terminals, post-install plugin manager operations, user actions, or arbitrary programs that manipulate the filesystem. Tool event names and hook support can change with host versions. An agent can still use tools not guarded by these matchers; scanner availability or a hook entry alone does not guarantee protection. Do not route risk-sensitive plugin installs through an unverified native manager simply because the hook allows them. Require a staged scan or explicit manual security decision for capabilities outside the controlled installers.

## 3. Verification and rollback

In a fresh session on **each installed host**, inspect registered hooks via the host's interface. Test:

- An ordinary `git clone` to a temporary application directory (should be allowed).
- A direct command `npx skills add ...` or `claude plugin install ...` (should be blocked before execution; use a harmless fake target rather than installing live code).
- A tool write into `~/.agents/skills/...` or `~/.claude/skills/...` (should be blocked).
- A staged benign skill (should scan and install).
- A synthetic high-risk or incomplete scan (should refuse installation).
- A previously modified installed skill (should not be overwritten).

To revert the hook change: remove only the exact managed `skill_security_hook.py` entry from `PreToolUse` in the appropriate settings file, or restore the **verified pre-change** settings backup, preserving later custom changes. No global hooks are removed automatically. For installed skills, existing local file snapshots and receipts under the host's `dev-workspace-advisor` folder remain separate from historical scan logs. Never delete a user-modified skill just to simplify cleanup.

Official documentation: [Codex hooks](https://learn.chatgpt.com/docs/hooks), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [SkillSpector](https://github.com/NVIDIA/SkillSpector).
