# Security-first SkillSpector workspace

## Two-stage setup: approve the hook manually

On Windows or macOS, run the preparation command for **each host** you want to configure:

```powershell
python scripts/setup.py --host codex --setup-workspace
python scripts/setup.py --host claude --setup-workspace
```

Preparation checks the pinned NVIDIA SkillSpector installation, runs a real benign scan,
writes or migrates the host's `PreToolUse` hook, and runs local Python hook self-tests.
It **does not install the three advisor skills or managed global instructions**.
A successful preparation prints `prepared: true`, `ready: false`, and instructions for
manual approval and live testing. This is intentional; configuration bytes cannot prove
host approval.

1. In Codex, review the hook in the **Review hooks** UI. Approve only the identified
   `skill_security_hook.py` entry; this setup script does not click or bypass approvals.
   For Claude Code, inspect the actual host trust/hook settings and allow the local
   configuration using its supported controls. Never assume both hosts expose identical UI.
2. Restart the host. Run an ordinary harmless command and check that it succeeds.
   Then have the host submit **exactly**
   `Get-Location # npx skills add fake-example` on Windows, or
   `pwd # npx skills add fake-example` on macOS.
   This is a comment-only test; the security hook should deny the tool call *before*
   the shell runs. If the command executes or the hook fails, **do not finish setup**.
3. After personally observing the live denial, explicitly acknowledge the test and
   finish scanning/installing the three core skills and global instructions:

```powershell
python scripts/setup.py --host codex --finish-workspace --acknowledge-live-hook-test
python scripts/setup.py --host codex --check-advisor
```

Replace `codex` with `claude` for Claude Code. The acknowledgment is **user-attested**,
not an automated claim that the host enforced the hook. Finishing re-checks the scanner
and installed hook configuration without rewriting the approved hook; an outdated/missing
hook blocks completion. SkillSpector still scans all core payloads independently.
If the scanner reports a MEDIUM finding, installation pauses for an explicit one-time local terminal decision explaining the reason and features enabled. HIGH/CRITICAL, DO_NOT_INSTALL and incomplete scans still block.

For interactive **Codex / Claude agent sessions**, the optional [native MCP approval workflow](NATIVE-APPROVAL.md) can request host-managed human permission for the MEDIUM install operation after a read-only scan. Do not substitute a chat reply or auto-approved tool call for the host's decision. The terminal flow below remains available for direct PowerShell use.

### MEDIUM findings: one-time feature approval

This is **different** from approving the PreToolUse hook in the Codex UI.
The hook approval allows the hook itself to run; a MEDIUM review decides
whether a **specific scanned skill operation** can be installed or updated.

Run the finish step in your own ordinary PowerShell/Terminal session. If the
scanner produces an LP3 `file_write` MEDIUM finding for the bundled Tool Advisor,
the installer displays a concise review:

```text
Tool Advisor — Security Review [MEDIUM]
Reason: The skill can modify local files but has not declared this capability.
Finding: LP3 (technical reference)
After approval, Tool Advisor can:
  - Save project plans and decisions locally.
  - Track tasks and their progress.
  - Resume saved workflows.
  - Update local workflow records when invoked.
Approve these capabilities? [y/N]:
```

If SkillSpector reports repeated instances of the same issue, the installer
groups them by finding code, severity and the plain-English meaning. Individual
scan findings still remain distinct in the returned warning records:

```text
Find Skills — Security Review [MEDIUM]
Findings: 12 occurrence(s) in 1 distinct group(s).
Reason: References an external npm command without a fixed version;
        running it could fetch changed executable code.
Finding: RP1 — 12 occurrence(s) (technical reference)
After approval, Find Skills can:
  - Search for available agent skills and assess relevant candidates.
  - Compare skill sources and recommend suitable options.
  - Suggest installing selected skills through the controlled security workflow.
Note: Running unpinned npx commands can fetch executable code.
      Direct skill installation remains subject to the security hook.
Approve these capabilities? [y/N]:
```

**Host-native buttons:** the current standalone Python installer cannot create
Approve/Reject buttons inside the Codex Desktop or Claude Code conversation.
Claude Code supports `PreToolUse` `ask` permission decisions, whereas Codex
does not currently support `ask` from a `PreToolUse` hook. A future native-UI
integration would need a separately verified host-specific permission mechanism
(such as a configured approval-gated MCP tool), and its approval would need to
be tied to the actual scan result rather than a model-supplied answer.
Until that integration is verified, the installer remains terminal-only and
fails closed in non-interactive sessions.

Entering `y` or `yes` allows **only this installation attempt** to continue.
Any other input cancels; no changes to active skills are made. No approval
record or reusable approval flag is created. Normal installer snapshots and
file-integrity hashes are retained to protect existing user modifications;
these are not approval signatures or cross-device approval records.

The prompt requires an interactive terminal, but a TTY **cannot authenticate
a human**. Do not ask an AI agent to answer the prompt; the agent could be
capable of emulating terminal input. A high-risk or incomplete scan never
offers this approval. All selected core skills must pass scans before
the first approval prompt appears.

### Portable launchers and migration

- **Codex Windows:** the hook command uses PowerShell's `&` call operator with
  single-quoted absolute Python/script paths and `exit $LASTEXITCODE`. This supports
  spaces in paths and preserves Python's exit 2 denial. Live blocking has been observed
  on Codex 0.166.0; verify other versions separately.
- **Codex macOS:** the hook uses POSIX shell quoting and the Python interpreter
  from the setup environment. The host still requires manual trust and live testing.
- **Claude Code Windows/macOS:** the hook uses Claude's documented exec-form
  `command` + `args` rather than shell-string parsing. The handler uses
  `onFailure: "block"`, requiring Claude Code 2.1.295 or newer. On older versions,
  do not claim fail-closed behavior; update Claude Code and test on the target device.
- The shared `skill_security_hook.py` policy remains unchanged. Each host uses its own
  settings location, matcher and global skill directory.

If the installer detects its own older hook, it replaces only that hook entry and
writes a distinct backup of the prior settings. Unrelated hooks and other settings are
preserved. Duplicate managed hooks, mixed shared entries, malformed JSON, and
concurrent edits are rejected instead of guessed away. Because migration changes the
hook command, the host may show **Modified** and require approval again. The installer
does **not** approve the hook automatically.

Codex user settings: `~/.codex/hooks.json`; Claude Code:
`~/.claude/settings.json`. A GitHub change alone does not update your device.
Local tests can prove scanner behavior and command launching but **cannot**
establish host trust, real interception or coverage of every execution path.

## How the scripts divide responsibilities

- `setup.py`: one setup entry point and hook registration; calls scanner bootstrap and Advisor last.
- `host_profiles.py`: Codex/Claude-specific paths.
- `skill_security_hook.py`: intercepts supported agent tool commands; rewrites simple HTTPS GitHub `git clone` to a controlled operation, blocks unsupported direct skill/plugin installation and edits to active capability directories.
- `secure_operations.py`: **only SkillSpector scan implementation**; stages/verifies files, installs individual managed skills, updates them with rollback, and inspects staged GitHub clones.
- `install_advisor.py`: three-core-skill baseline manager, using the scanner from `secure_operations.py`; retains the existing snapshot/rollback system. It can explicitly archive previously managed optional skills without deleting local copies.
- `advisor.py`, `knowledge.py`: unrelated project coordination and knowledge lookup.

No separate `setup_security_hooks.py` or `install_selected_skill.py` is required.

## Migrating an older 17-skill device

A previous managed installation may still have all 17 skills. The default setup
does **not** silently remove or overwrite them. After checking local changes,
explicitly archive the 14 managed optional skills before finishing core setup:

```powershell
python scripts/setup.py --host codex --retire-optional-advisor-skills
python scripts/setup.py --host codex --setup-workspace
# Review/approve the modified hook and verify live blocking first
python scripts/setup.py --host codex --finish-workspace --acknowledge-live-hook-test
python scripts/setup.py --host codex --check-advisor
```

Use `--host claude` separately if needed. Retirement checks installed files,
retains backups, and leaves unrelated/unmanaged skills alone. Modified/missing
managed files block archival.


## New skills and updates

Stage files outside live `~/.agents/skills` / `~/.claude/skills` paths **without executing any untrusted setup scripts**. Then use:

```powershell
python scripts/secure_operations.py install --host codex --name example --source .\incoming\example
python scripts/secure_operations.py install --host codex --name example --source .\incoming\example --update
```

The update flag only works for a previously managed, unmodified installation. The worker keeps file hashes (not old scan reports) and rolls back an interrupted update. Direct `npx skills add`, `claude plugin install` or equivalent commands remain **blocked**: a hook cannot automatically inspect arbitrary third-party installer payloads before those installers execute. The agent should use controlled staging for supported skills. Unsupported plugin packaging is not automatically approved.

For skills, the scanner uses `--no-llm --format json --fail-on-incomplete --min-coverage 100`. Require expected file coverage, no suppression, complete results and trustworthy risk data. LOW/SAFE without higher individual findings proceeds automatically. MEDIUM findings (or CAUTION recommendations) require an interactive approval on every install/update, without saving that approval. HIGH/CRITICAL, DO_NOT_INSTALL, failed, suppressed, incomplete, or changed-file scans block activation. Scan and compare all selected core skills before any approval prompt or activation. No persistent vulnerability/approval ledger is created.

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

For scanner errors, ambiguous HIGH findings, incomplete coverage and read-only source review, follow the [fail-closed triage procedure](SECURITY-TRIAGE.md). It improves diagnostic evidence; it does **not** authorize an installation bypass or replace the exact-file scan.

## Required live tests and limitations

1. Start a **new** Codex/Claude session and inspect hook registration.
2. Confirm `npx skills add fake-example` is blocked before execution.
3. Confirm a harmless simple HTTPS GitHub clone is redirected to staging.
4. Confirm a benign staged skill installs after a real SkillSpector scan.
5. Confirm CAUTION/MEDIUM requires local terminal consent and rejects by default; HIGH, scanner crash, incomplete scan and changed files block skill installation.
6. Confirm an existing modified skill remains untouched after attempted update.

Hooks cannot monitor arbitrary subprocesses, external terminals, manual installs, bypassed tools or disabled host hooks; an agent's operating-system permissions/sandbox are an independent protective boundary. SkillSpector is built for agent skills, not comprehensive malware analysis of generic Java/Node/Python repositories. The source repo being updated does **not** install hooks on your laptop until you run setup there.

Official sources: [NVIDIA SkillSpector](https://github.com/NVIDIA/SkillSpector), [Claude Code hooks](https://code.claude.com/docs/en/hooks), [Codex hooks](https://learn.chatgpt.com/docs/hooks).
