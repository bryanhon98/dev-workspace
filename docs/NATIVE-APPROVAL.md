# Native skill approval in Codex and Claude Code

This repository provides a local MCP server at `scripts/native_approval_mcp.py`.
Its host-native permission prompt replaces the Python terminal `[y/N]` prompt
**when the host supports and enforces native MCP tool approvals**.

## Three tools

- **review_skill**: read-only SkillSpector scan; groups security findings and
  returns a temporary review ID plus readable summary.
- **install_safe**: automatically installs LOW/SAFE only. Rejects MEDIUM+.
- **install_reviewed**: requires a host-native permission prompt on every
  installation call; re-scans and verifies the exact same files and findings.

HIGH/CRITICAL, incomplete, suppressed, or failed scans cannot be approved.
No approval history is stored. Review IDs are temporary integrity
fingerprints, not approval records.

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
> `install_safe`. If MEDIUM, call `install_reviewed` with the exact
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
