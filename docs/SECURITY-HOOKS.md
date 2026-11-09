# Security-first SkillSpector workspace

## One command per host

Run from this checkout on the device you want to configure:

```powershell
python scripts/setup.py --host codex --setup-workspace
python scripts/setup.py --host claude --setup-workspace
```

The command installs/verifies NVIDIA SkillSpector (using `uv tool install git+https://github.com/NVIDIA/skillspector.git` if missing), runs a real benign static-scan smoke test, adds a native `PreToolUse` hook **without replacing other hooks**, checks blocking and clone rewrite locally, then stages/scans/installs the complete 17-skill Tool Advisor baseline and finally updates global instructions. Setup fails closed if a required step fails. An existing scanner name/version is not an independently verified software-supply-chain signature.

**Restart each host and verify a live event.** Local self-tests cannot establish that the running Codex/Claude version loaded the hook. Codex settings: `~/.codex/hooks.json`; Claude Code: `~/.claude/settings.json`. Existing settings receive a `.before-dev-workspace.bak` backup on first modification. A conflicting managed hook requires manual reconciliation.

## How the scripts divide responsibilities

- `setup.py`: one setup entry point and hook registration; calls scanner bootstrap and Advisor last.
- `host_profiles.py`: Codex/Claude-specific paths.
- `skill_security_hook.py`: intercepts supported agent tool commands; rewrites simple HTTPS GitHub `git clone` to a controlled operation, blocks unsupported direct skill/plugin installation and edits to active capability directories.
- `secure_operations.py`: **only SkillSpector scan implementation**; stages/verifies files, installs individual managed skills, updates them with rollback, and inspects staged GitHub clones.
- `install_advisor.py`: 17-skill baseline manager, using the scanner from `secure_operations.py`; retains the existing snapshot/rollback system.
- `advisor.py`, `knowledge.py`: unrelated project coordination and knowledge lookup.

No separate `setup_security_hooks.py` or `install_selected_skill.py` is required.

## New skills and updates

Stage files outside live `~/.agents/skills` / `~/.claude/skills` paths **without executing any untrusted setup scripts**. Then use:

```powershell
python scripts/secure_operations.py install --host codex --name example --source .\incoming\example
python scripts/secure_operations.py install --host codex --name example --source .\incoming\example --update
```

The update flag only works for a previously managed, unmodified installation. The worker keeps file hashes (not old scan reports) and rolls back an interrupted update. Direct `npx skills add`, `claude plugin install` or equivalent commands remain **blocked**: a hook cannot automatically inspect arbitrary third-party installer payloads before those installers execute. The agent should use controlled staging for supported skills. Unsupported plugin packaging is not automatically approved.

For skills, the scanner uses `--no-llm --format json --fail-on-incomplete --min-coverage 100`. Require expected file coverage, no suppression, complete results and an allowed SAFE/LOW verdict. CAUTION, MEDIUM/HIGH/CRITICAL, DO_NOT_INSTALL, failed, suppressed, incomplete or changed-file scans block activation. No persistent vulnerability/audit ledger is created.

## GitHub cloning

For a simple supported agent tool call:

```powershell
git clone https://github.com/owner/repo.git destination
```

The hook changes the **tool input**, not the repository itself, into a call to:

```powershell
python scripts/secure_operations.py clone --url https://github.com/owner/repo.git --destination destination
```

The worker clones to a temporary directory, identifies agent skills, invokes SkillSpector for each staged skill, and releases the checkout only when applicable checks pass. If no `SKILL.md` is found, the worker *attempts* a general-repo SkillSpector scan and reports limited/not-applicable coverage. This **does not certify arbitrary source code as harmless**. Complex Git commands, non-GitHub URLs and compound shell syntax are blocked with guidance rather than silently executed. User-run external terminal clones are not intercepted.

## Required live tests and limitations

1. Start a **new** Codex/Claude session and inspect hook registration.
2. Confirm `npx skills add fake-example` is blocked before execution.
3. Confirm a harmless simple HTTPS GitHub clone is redirected to staging.
4. Confirm a benign staged skill installs after a real SkillSpector scan.
5. Confirm CAUTION/MEDIUM, HIGH, scanner crash, incomplete scan and changed files block skill installation.
6. Confirm an existing modified skill remains untouched after attempted update.

Hooks cannot monitor arbitrary subprocesses, external terminals, manual installs, bypassed tools or disabled host hooks; an agent's operating-system permissions/sandbox are an independent protective boundary. SkillSpector is built for agent skills, not comprehensive malware analysis of generic Java/Node/Python repositories. The source repo being updated does **not** install hooks on your laptop until you run setup there.

Official sources: [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Codex hooks](https://learn.chatgpt.com/docs/hooks).
