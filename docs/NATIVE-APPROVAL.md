# Native skill approval in Codex and Claude Code

## Current scan-first policy (2026-11-16)

Follow [the installation review contract](INSTALLATION-REVIEW.md). Finish independent scans, show version/source and coverage, a findings table, simple "Approving this means" sentences, a reasoned recommendation, and a plain question for results requiring acceptance. Preserve original payloads. LOW automatic approval requires a complete valid static report, 100% coverage, no gaps, SAFE/LOW overall and no higher individual finding.

## Three tools

- **review_skill**: scans inactive payloads and returns exact-file review identity, findings and coverage. It does not install or record approval.
- **install_safe**: automatically installs only eligible LOW/SAFE reports after revalidation.
- **install_reviewed**: revalidates accepted structured concerns, including HIGH/CRITICAL and incomplete reports. It depends on the host to enforce real human permission.

Malformed/unusable reports, unsafe paths and changed bytes cannot be approved. Recoverable errors must not prevent independent scans from completing. Review IDs are integrity fingerprints, not permission records.

**Observed limitation:** the watermark installation returned success without a human prompt. The server dispatches the reviewed tool as approved based on tool routing; it does not independently verify a human click. Saved configuration and unit tests do not prove effective enforcement. Never call this tool on a host known to auto-approve it. Ask the review question, and retain the human-operated terminal fallback when required host permission is unavailable. The current session's enforced approval policy is `never`; this repository update cannot change it. LOW standing authorization never overrides stricter host permissions.

The live hook's manually corrected maintenance guard is preserved. Patch destinations are parsed separately from patch prose. Bounded standalone reads are allowed, but compound shell inspections mentioning the server may still be rejected. Restart/reconnect after changes and test real human denial separately.

## Agent-assisted setup

A request to setup or update the workspace from this repository authorizes the
assistant to register this local MCP and merge the settings below. The user does
not need to copy commands or edit TOML. This exception covers only
`skill_security`; other services retain their existing manual-setup rules.

Inspect first and reuse an already-correct connection. Use the actual checkout
path and an available Python executable. Keep a local backup before edits,
preserve unrelated settings/comments and other servers, and avoid duplicate TOML
headers. Preserve stricter existing per-tool prompts and respect enforced host
policy. Explain the global impact of switching Codex to `on-request`.
Validate the resulting configuration and registration without running the server
script directly from an agent shell. Report configuration separately from live
connection and approval enforcement. Never export raw device configuration.

The assistant still cannot approve the hook or an installation for the user.
After restart/reconnection, verify tool availability and have the user reject a
permission request to confirm that no installation occurs. If the host cannot
enforce human approval, stop the affected installation and use the documented
human-operated terminal fallback.

This is an agent-assisted setup instruction, not a new behavior of
`setup.py --setup-workspace` or the read-only no-argument command. The commands
below remain available for manual setup and are the agent's registration guide.

## Register on each device

First update your repository, ensure SkillSpector and the existing host hook
are installed, and test the hook live. Different devices must configure their
MCP connections separately.

### Codex Desktop or CLI (PowerShell)

```powershell
$server = (Resolve-Path .\scripts\native_approval_mcp.py).Path
codex mcp add skill_security -- python $server
codex mcp list
```

Open your Codex user configuration (normally `$HOME\.codex\config.toml`)
and **merge** these entries with the existing server settings. Do not create
duplicate TOML table headers. The top-level values must appear before
the first table header.

```toml
approval_policy = "on-request"
approvals_reviewer = "user"

[mcp_servers.skill_security]
tool_timeout_sec = 300

[mcp_servers.skill_security.tools.review_skill]
approval_mode = "approve"

[mcp_servers.skill_security.tools.install_safe]
approval_mode = "approve"

[mcp_servers.skill_security.tools.install_reviewed]
approval_mode = "prompt"
```

Retain the existing server `command` and `args` configured by the
`codex mcp add` command. A user-specific `approval_policy = "never"`
or `approvals_reviewer = "auto_review"` is incompatible with requiring a
human to approve. Verify the effective configuration before using this.
In Codex, `approve` means *never prompt*; `prompt` means *ask each time*.
Never enable persistent permission for `install_reviewed`. Restart Codex
and verify a rejected approval does not install anything.

### Claude Code (PowerShell)

```powershell
$server = (Resolve-Path .\scripts\native_approval_mcp.py).Path
claude mcp add --scope user --transport stdio skill_security -- python $server
claude mcp get skill_security
```

The `install_reviewed` MCP tool declares
`_meta["anthropic/requiresUserInteraction"] = true`.
Claude Code documents that this requires a human prompt even in auto or
bypassPermissions modes, and disables "don't ask again". Some Claude
frontends show the full permission dialog in a terminal rather than a
one-tap button. Test the actual version and surface you use.

## Agent conversation workflow

Tell Codex or Claude:

> Scan the skill with the skill_security MCP `review_skill` tool.
> Show me grouped findings and the features. If LOW/SAFE, use
> `install_safe`. For other assessable results, obtain acceptance and call `install_reviewed` with the exact
> review_id and summary. I will approve or reject in the host's native
> permission UI. Never answer permission prompts for me.

To review all three core Advisor skills:
```json
{"target":"core","host":"codex"}
```

For one staged external skill:
```json
{"target":"skill","host":"codex","source":"ABSOLUTE_STAGE_DIR","name":"skill-name","update":false}
```

The agent passes the same target, host, source, name, and update arguments
plus the exact `review_id` and `summary` from `review_skill`. The MCP
installer rescans all content before activation. Core setup also requires
an already-approved host security hook and writes managed global rules;
restart the host after installation.

The initial hook preparation is still:

```powershell
python scripts/setup.py --host codex --setup-workspace
```

Approve the host hook and test a live blocked command before continuing.
Native MCP setup does not itself verify that live hook test.

## Security limitations and fallback

The MCP process itself cannot independently attest that a real Codex or
Claude dialog appeared. **The host must enforce the tool approval.** On
Codex, keep the per-tool approval policy `prompt`, global reviewer `user`,
and an interactive approval policy. On Claude, the require-user-interaction
tool annotation is the native permission mechanism.

An agent with unrestricted local code execution under the same OS account
may bypass a user-space hook or call Python directly. Do not treat this as
an operating-system-enforced sandbox. Keep the host hook and ordinary OS
security boundaries; review any changes to agent permission settings.

If the native host prompt is unavailable, fail closed; do not pass a
model-generated `approved` flag. The existing direct terminal installer
remains available for human-operated `[y/N]` approval.

Sources:
- https://learn.chatgpt.com/docs/extend/mcp
- https://learn.chatgpt.com/docs/config-file/config-reference
- https://code.claude.com/docs/en/mcp
