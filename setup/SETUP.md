# Set up this laptop using this repo

Open the downloaded/cloned repository in Codex and say: "Set up this laptop using this repo."

## 1. Install the global rules

With Python 3 available, run from the repo:

```sh
python3 scripts/setup.py
python3 scripts/setup.py --check
```

The command installs global/AGENTS.md into a managed section of the effective user instruction file under CODEX_HOME (normally ~/.codex). It preserves unrelated instructions, keeps an exact local backup, uses an existing nonempty AGENTS.override.md when applicable, and refuses to overwrite edited managed rules. --codex-home PATH supports explicit profiles and isolated testing. Start a new Codex session to load the result.

If this device has older unmanaged copies of this repo's rules, compare them and remove only the obsolete setup-owned content after a backup. The script intentionally preserves other text instead of guessing ownership.

## 2. Restore the saved components with Codex

- Read inventory.json. Choose/reuse a non-sensitive device alias such as laptop-b.
- Establish authenticated GitHub access and inspect/install SkillSpector if needed. Missing scanner access blocks skill activation, not installation of your own instruction file.
- For each desired component, retrieve the exact saved source/version, inspect it according to global/AGENTS.md, test as appropriate and install in user-global scope by default. Verify hashes and discovery. Never restore an unreviewed version merely because it is listed.
- Custom skill sources belong in skills/custom/ and external redistributable skills in skills/external/. Both install into the supported user skill directory (currently ~/.agents/skills/). Preserve licenses and reconcile duplicate/modified installed copies.
- Reconnect plugins and MCP services through supported user/account settings. Use environment-variable references for secrets and authenticate separately. Do not copy an entire config.toml across devices.
- Append verified component installs/updates/removals to installations/<device-alias>.jsonl. Update inventory and audit summaries, publish the exact sanitized changes and verify the remote commit. Instructions-only setup changes are recorded in Git history.

## What is implemented

Global rule installation and verification are implemented and tested. The rules tell Codex to scan skills, use the creator workflow, install globally and publish installation records. Component restoration and GitHub publishing are agent-led; the Python command does not perform them.

The Mac's earlier prepared skill payloads and audit reports are still unavailable in this checkout. inventory.json records known components as pending import/review or account reconnection, not as a completed backup. The Anthropic creator is a reference awaiting inspection, not an installed skill. Full one-step restoration requires those payloads/reviews and credentials on the new laptop.
