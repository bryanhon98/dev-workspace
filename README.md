# Tool Advisor — my tool and skill knowledge base

Describe what you want to achieve. This repository guides an assistant to understand the task, find suitable skills and tools, compare them with what is already installed, coordinate the work, and remember useful outcomes for next time.

It supports software, design, research, media, business and automation. Its workflow policy is intended for **both Codex and Claude Code**, while the saved setup and installer currently have Codex-specific validation. Claude Code activation and native delegation must be checked in an actual Claude session; a repository file alone does not install or enable an agent. You do not need to know the names of every specialist before asking for help.

## Current status

The mandatory baseline contains **only 3 core skills**: Tool Advisor, Grilling and Vercel Find Skills. The previously listed fourteen Superpowers/Council skills are normal library candidates, not a second baseline tier; their historical source records remain available for discovery and legacy migration. Any selected skill requires a fresh local SkillSpector scan before activation.

| Part | Status |
|---|---|
| Workflow, research library and saved decisions | Available in this repo |
| Three required core skills | Packaged; verified and scanned together at setup |
| Fourteen optional skill sources | Retained in the repository for per-task discovery and selection |
| Default setup command | Installs only the three core skills after its checks pass |
| Security policy | LOW/SAFE automatically; MEDIUM asks you in a terminal with features explained; HIGH/CRITICAL or incomplete scans block |
| Your device | Run setup and verify discovery in a fresh session |

The bundle uses original upstream skills. Council requires actual independent workers; without them, do not claim an independent panel. No separate model-provider account is required for its native-worker route.

Earlier isolated Codex baseline installs were tested, but **this simplified scanner gate and host hooks require fresh device-level verification**. GitHub source changes do not install or activate skills on your laptop.

## How the workflow works

For substantial new projects, the full path is below. Task depth and shortcuts follow [BUILD-FLOW.md](knowledge/BUILD-FLOW.md).

1. **Understand the goal.** Use the interview skill to clarify missing requirements, constraints and success criteria. Reuse information already supplied.
2. **Map the necessary capabilities.** Identify all parts of the job, including design, implementation and verification where relevant.
3. **Find suitable skills and tools.** Search relevant installed capabilities, extracted reels, saved decisions and external sources, including GitHub. Read shortlisted skill instructions and check current versions. Popularity is a discovery signal, not proof of suitability.
4. **Propose a combination.** Explain each role, overlap, readiness, cost and gaps. Confirm the project-specific combination before execution; reuse unchanged approvals.
5. **Do the work.** The main assistant coordinates, using selected skills directly or assigning bounded work to available subagents. Track ownership, dependencies and blockers.
6. **Verify the result.** Check the agreed success criteria using appropriate tests, reviewers, browser interactions or measurements. Report anything unverified.
7. **Save useful outcomes.** Record what worked, failed or changed, then consult that evidence on future tasks.

**Tool Advisor V2 workflow policy (2026-11-07):** The underlying model remains the sole coordinator; Grilling guides substantial unresolved interviews. Strategic capability mapping precedes evidence-based discovery through installed knowledge, reels, Find Skills and targeted external sources. Real available workers receive bounded tasks; their outputs are integrated and independently reviewed when warranted. Council resolves important unresolved trade-offs. The standard baseline changed on 2026-11-10 to three required skills; optional sources remain available, and previously installed device skills are not silently removed.

Small edits and explanation-only questions use a shorter path. The assistant selects the smallest useful combination; it does not run every installed skill for every task.

### How much process is needed?

[BUILD-FLOW.md](knowledge/BUILD-FLOW.md) owns the routing policy. Clear small tasks go directly to action and a focused check. Bounded features reuse a short brief and existing tools. Complex projects get the fuller interview, discovery and coordination flow. Risk can require extra checks even for a small task.

You do not need a PRD to start. A short brief is the default; a fuller product document is optional. The assistant and selected specialists prepare a technical proposal/TRD only when complexity warrants it, after clarifying scope. Existing requirements and approvals are reused. One tracker holds the work; council and independent reviews are selected for a concrete need.

The [initial six-case routing evaluation](audits/advisor-routing-20261103/README.md) found clearer stage choices and no observed routing regression. It was a dry run, not a measured speed or end-to-end quality benchmark.

### Who does what?

| Component | Role |
|---|---|
| Main assistant | Coordinates the goal, plan, workers and final result |
| [Tool Advisor](skills/custom/tool-advisor/SKILL.md) | Custom instructions connecting interview, discovery, selection, tracking and verification |
| [Grilling — Matt Pocock](https://github.com/mattpocock/skills) | Clarifies requirements through questions |
| [Find Skills — Vercel](https://github.com/vercel-labs/skills) | Helps discover relevant skills |
| [Superpowers](https://github.com/obra/superpowers) | Optional software execution, review and verification candidates; compare before selecting |
| [Council of High Intelligence](https://github.com/0xNyk/council-of-high-intelligence) | Optional structured deliberation for important decisions after scope is clear |
| Project specialists | Provide the particular design, technical or domain guidance the task needs |

A **skill is a set of instructions**. A **subagent is a separate AI worker** that can apply those instructions. Loading a skill does not create another worker. Use original selected skills rather than silently replacing them with invented substitutes; disclose host adaptations or unavailable dependencies.

**Native dispatch across Codex and Claude Code:** Tool Advisor selects the skills, accountable agents and task dependencies; the **current session** invokes real agents using whatever native worker tools it supports. Each worker receives the actual skill source/loading instructions and bounded acceptance checks. Do not assume preloading across different agent modes or treat a named skill as executed. When delegation is unavailable, report it and use proportionate sequential work rather than building another dispatcher. See the [host-neutral execution policy](knowledge/BUILD-FLOW.md#host-neutral-skill-to-agent-execution).

For agreed independent reviews, a separate worker applies the selected review instructions. Coordinator-only review must be labelled self-review. Separate workers may still use the same underlying model.

The council is a bounded decision checkpoint, not another overall coordinator. Retry failed participants within a budget; continue with explicitly reported reduced participation only when at least two actual workers respond. Otherwise stop the checkpoint. Imagined responses never count as independent participants. These are the [approved council and reviewer rules](knowledge/decisions/2026-11-03-approved-council-and-review-policy.json).

## Download and setup

[Download ZIP](https://github.com/bryanhon98/dev-workspace/archive/refs/heads/main.zip), or clone the repository:

```sh
git clone https://github.com/bryanhon98/dev-workspace.git
cd dev-workspace
```

For an existing clean Git checkout, update with `git pull --ff-only`. Keep the checkout available: it is the assistant's research library.

Open this folder in Codex **on the device you intend to configure**, then say:

> Setup tool-advisor using this repo. Install the approved baseline up front, reuse my recorded choices, and report any blockers.

That request selects **only Tool Advisor, Grilling and Find Skills**. Superpowers skills and Council are optional research candidates, not automatic installations. Tool Advisor decides when additional capabilities are worth considering and uses Find Skills to compare the saved libraries against external sources before proposing a small task-specific combination.

Inspect the selected baseline without installing anything:

```sh
python3 scripts/setup.py --plan-advisor
```

Install the three-skill core baseline and check its files:

```sh
python3 scripts/setup.py --host codex --setup-workspace
# Approve/restart the host and observe a live blocked-command test
python3 scripts/setup.py --host codex --finish-workspace --acknowledge-live-hook-test
python3 scripts/setup.py --check-advisor
```

When you ask an assistant to setup or update this workspace, it also configures the local `skill_security` MCP and merges its required approval settings automatically. Existing correct settings are reused; other services remain manual. Human hook approval and live denial testing still require you. This is an agent workflow, not automatic MCP registration by the Python setup command.

For **agent-assisted MEDIUM approvals inside Codex/Claude**, see [native MCP approval setup](docs/NATIVE-APPROVAL.md). This uses the host's own permission prompt, not an AI-generated approval string; the existing PowerShell prompt remains the fallback.

The installer stages and scans the **three mandatory core skills** together before activation. If a required component is blocked, it leaves the active core bundle unchanged. `--install-advisor-core` is now a legacy alias of `--install-advisor`; `--check-advisor` checks core readiness, not whether every optional skill is installed. **Previously managed 17-skill devices require explicit safe migration** (below), not silent deletion.

### Existing devices with 17 installed skills

Changing the GitHub baseline **does not uninstall anything from your Windows or Mac**. An existing managed 17-skill receipt must be migrated explicitly; missing or locally modified managed files block retirement instead of being overwritten. From an updated checkout on the actual device:

```powershell
python scripts/setup.py --host codex --retire-optional-advisor-skills
python scripts/setup.py --host codex --setup-workspace
# Approve/restart the host and observe a live blocked-command test
python scripts/setup.py --host codex --finish-workspace --acknowledge-live-hook-test
python scripts/setup.py --host codex --check-advisor
```

Use `--host claude` for the Claude Code profile, separately. Retirement archives the previously managed optional skills and their snapshots under the local Advisor state directory, preserving recovery copies. It does **not** remove unmanaged/independently installed skills, plugins or extra data. To activate a newly selected optional skill later, use the usual controlled staged installation with fresh SkillSpector scanning and your task-specific approval.

Installation uses the target host's global skills directory and a **small local receipt plus file snapshots**, not shared scan/audit records. The preferred security-first setup installs/verifies NVIDIA SkillSpector automatically; the installer checks its CLI, stages and scans all selected skills, preserves unrelated instructions and refuses to overwrite locally modified files. An existing scanner can be specified with `--scanner /path/to/skillspector`. No scanner executable was installed on your device by this repository change.

For a broader device setup, say **“Setup my Codex using this repo”** or **“Setup my Claude using this repo.”** Both use the same security policy. Plugins and MCPs may still require separate user authorization and setup.

## Start or resume a project

After setup and a fresh Codex session, say:

> Use tool-advisor. I want to [describe the outcome]. Clarify the scope and show me the suitable skill combination before starting.

Substantial project requests should enter the flow automatically **when the host loads the managed instructions**. Inside this repo, [AGENTS.md](AGENTS.md) also directs the assistant into the flow. The explicit prompt is a fallback. Merely sharing the GitHub link does not activate it in every app or on another device.

For example:

> I want a realistic 3D website where scrolling flips a book and reveals objects I can inspect. Help me choose the right combination and define how we will test it.

The advisor should account for visual direction, 3D assets, scroll animation, inspection controls, mobile usability and performance—not just select a generic web-development skill.

To resume, ask the assistant to continue from the project record. Its local task ledger lives in the ignored `.tool-advisor/` directory. You can inspect it with:

```sh
python3 /path/to/dev-workspace/scripts/advisor.py --project /path/to/project status
```

An existing project tracker remains the task source. The advisor links relevant tasks and evidence rather than maintaining a competing plan. File checks and saved status do not replace checking actual outputs or demonstrating that the host can load the skills.

## Security-first setup: manual approval, then finish (Codex + Claude Code)

Prepare SkillSpector, configure/migrate the host-specific security hook and test it
locally **without installing core skills**:

```powershell
python scripts/setup.py --host codex --setup-workspace
# Or use --host claude for Claude Code
```

The first stage reports `prepared: true` and `ready: false`. Open the host's
hook review/trust UI (Codex **Review hooks** / Claude Code's supported controls).
Approve the specific local `skill_security_hook.py` entry yourself, restart the
host, and verify that a harmless command works and
`Get-Location # npx skills add fake-example` (Windows) or
`pwd # npx skills add fake-example` (macOS) is **blocked before execution**.
The trailing text is a comment: no npm installation occurs. A hook failure or an
executed probe means you must **not** continue.

After you personally verify the live block:

```powershell
python scripts/setup.py --host codex --finish-workspace --acknowledge-live-hook-test
python scripts/setup.py --host codex --check-advisor
```

The finish step rechecks the scanner and hook config and then scans/installs
the three mandatory core skills and applies global instructions. Its
`--acknowledge-live-hook-test` flag is a **user attestation**, not automatic
host-verification or hook approval. A changed hook may need reapproval.
The shared Python policy stays the same, but launchers differ: PowerShell
on Codex Windows, POSIX shell on Codex macOS, and Claude Code exec-form
command/args on Windows/macOS (requires Claude Code 2.1.295+ for
`onFailure: "block"`). See [security hooks](docs/SECURITY-HOOKS.md)
for host-specific limitations, backups, migration and verification.

One security implementation lives in
[`scripts/secure_operations.py`](scripts/secure_operations.py): staged source
scanning, verdict validation, unchanged-byte verification and controlled
installation. The hook blocks recognized direct skill/plugin installation
commands and routes supported simple GitHub clones through staged inspection.
It is **not** an OS-wide security boundary; external terminals and some agent
execution paths are outside its reach. SkillSpector's static scan is not a
general-purpose malware audit of arbitrary application repositories.


## How the repository learns

The assistant saves sanitized outcomes, failed approaches, corrections and source revisions in [decision records](knowledge/decisions/). Future recommendations consult those records and refresh relevant sources.

This is maintained knowledge—not model retraining, automatic device monitoring or continuous GitHub scanning. Comparable evaluations are needed before claiming that a workflow change improves results. Learning does not automatically remove or replace installed skills.

The three original reel documents are preserved with hashes: **1,083 entity records and 475 report entries**. They contain discovery leads and compiled claims, not 1,083 verified tools. Creator commentary is useful context; repeated claims and star counts are not independent evidence.

## Explore the knowledge base

| Location | Contents |
|---|---|
| [Advisor workflow](knowledge/BUILD-FLOW.md) | Steps from task request to verified result |
| [Advisor rules](knowledge/ADVISOR.md) | Discovery, comparison, selection and evidence practices |
| [Task routes](knowledge/ROUTING.md) | Starting points for different jobs |
| [Reel library](knowledge/reel-library/index.md) | Searchable extracted research |
| [Import review](knowledge/reel-library/REVIEW.md) | Preservation checks and source limitations |
| [Decisions](knowledge/decisions/) | Dated comparisons, approvals and outcomes |
| [GitHub catalog](github-repos/README.md) | Previously considered tools and skill collections |
| [Inventory](inventory.json) | Component sources and recorded readiness |
| [Global instructions](global/AGENTS.md) | Portable setup and operating rules |
| [Required baseline](advisor-baseline.json) | Selected starting workflow skills |
| [Packaged bundle](advisor-bundle.json) | Exact selected versions and source locations |

Useful read-only commands:

```sh
python3 scripts/knowledge.py search "design accessibility"
python3 scripts/knowledge.py show graphify
python3 scripts/knowledge.py inspect --root ~/.agents/skills --root ~/.codex/skills
python3 scripts/knowledge.py verify
python3 scripts/setup.py
python3 scripts/setup.py --plan-advisor
python3 scripts/setup.py --check-advisor
```

`--install-rules` restores only managed instructions; `--check` checks those instructions. Neither installs skills. Start a new session after changing installed instructions. `CODEX_HOME`, `--codex-home` and `--skills-root` support alternate profiles; a cloud test profile is not your laptop.

Verified setup changes and sanitized knowledge are published to this repo when the assistant has access. Raw conversations, private project state, credentials and personal databases are not published. A failed push must be reported as unsynced. No background publishing service is configured.
