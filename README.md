# Tool Advisor — my tool and skill knowledge base

Describe what you want to achieve. This repository guides an assistant to understand the task, find suitable skills and tools, compare them with what is already installed, coordinate the work, and remember useful outcomes for next time.

It supports software, design, research, media, business and automation. It also keeps a portable record of your Codex setup. You do not need to know the names of every specialist before asking for help.

## Current status

The complete **17-skill baseline is packaged**: Tool Advisor, Grilling, Find Skills, 13 Superpowers workflow skills and Council of High Intelligence. Installation checks upstream versions, scans the whole selected batch, retains documented warnings and verifies the installed files.

| Part | Status |
|---|---|
| Workflow, research library and saved decisions | Available in this repo |
| All 17 baseline skill payloads | Packaged with exact hashes and scan decisions |
| Full setup command | Installs the baseline together after its checks pass |
| Security policy | Warn and proceed for established low risk; block dangerous or unclassified findings |
| Your device | Run setup and verify discovery in a fresh session |

The bundle uses original upstream skills. Council has [documented host adaptations](audits/advisor-ready-20261103/council/adaptations.json) for portable asset lookup and actual independent workers. No extra model-provider account is required for the native-worker council. A host without worker support can install the files but cannot run independent council deliberation.

**Verified on Linux:** all 17 skills installed and discovered by Codex in a fresh isolated project; all 110 tests passed. No known main setup blocker remained in that test. Full project execution and council deliberation were not exercised.

See the [verification record](audits/advisor-ready-20261103/verification.json) for the tested environment and limits. A download alone does not install or activate skills.

## How the workflow works

For substantial new projects, the full path is below. Task depth and shortcuts follow [BUILD-FLOW.md](knowledge/BUILD-FLOW.md).

1. **Understand the goal.** Use the interview skill to clarify missing requirements, constraints and success criteria. Reuse information already supplied.
2. **Map the necessary capabilities.** Identify all parts of the job, including design, implementation and verification where relevant.
3. **Find suitable skills and tools.** Search relevant installed capabilities, extracted reels, saved decisions and external sources, including GitHub. Read shortlisted skill instructions and check current versions. Popularity is a discovery signal, not proof of suitability.
4. **Propose a combination.** Explain each role, overlap, readiness, cost and gaps. Confirm the project-specific combination before execution; reuse unchanged approvals.
5. **Do the work.** The main assistant coordinates, using selected skills directly or assigning bounded work to available subagents. Track ownership, dependencies and blockers.
6. **Verify the result.** Check the agreed success criteria using appropriate tests, reviewers, browser interactions or measurements. Report anything unverified.
7. **Save useful outcomes.** Record what worked, failed or changed, then consult that evidence on future tasks.

**Tool Advisor V2 workflow policy (2026-11-07):** The underlying model remains the sole coordinator; Grilling guides substantial unresolved interviews. Strategic capability mapping precedes evidence-based discovery through installed knowledge, reels, Find Skills and targeted external sources. Real available workers receive bounded tasks; their outputs are integrated and independently reviewed when warranted. Council resolves important unresolved trade-offs. The verified 17-skill bundle and local installations are unchanged.

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
| [Superpowers](https://github.com/obra/superpowers) | Preferred software execution, review and verification methods |
| [Council of High Intelligence](https://github.com/0xNyk/council-of-high-intelligence) | Optional structured deliberation for important decisions after scope is clear |
| Project specialists | Provide the particular design, technical or domain guidance the task needs |

A **skill is a set of instructions**. A **subagent is a separate AI worker** that can apply those instructions. Loading a skill does not create another worker. Use original selected skills rather than silently replacing them with invented substitutes; disclose host adaptations or unavailable dependencies.

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

That request selects Tool Advisor, Grilling, Find Skills, the Superpowers workflow skills and Council of High Intelligence, plus their required dependencies. It does not select every candidate in the research library. Project-specific specialists remain conditional.

Inspect the selected baseline without installing anything:

```sh
python3 scripts/setup.py --plan-advisor
```

Install the full baseline and check its files:

```sh
python3 scripts/setup.py --install-advisor
python3 scripts/setup.py --check-advisor
```

The installer stages and scans all 17 skills before activation. If a required component is blocked, it leaves the active bundle unchanged. `--install-advisor-core` is available only for an explicitly requested three-skill partial setup; `--check-advisor` reports that as incomplete workflow setup.

Installation uses `~/.agents/skills`, managed Codex instructions and local receipts. It preserves unrelated instructions and refuses to overwrite locally modified managed content. Scanner bootstrap requires Python 3.12–3.14, Git and network access. An existing verified scanner can be supplied with `--scanner /path/to/skillspector`. Plugins, accounts and external model providers retain their own setup requirements; installing instruction files does not configure them automatically.

For a broader device setup, say **“Setup my Codex using this repo.”** That opens the inventory and asks about additional selections while preserving existing approvals. Plugins and MCPs remain a manual setup/login checklist.

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

## Installation policy

The [current user policy](global/AGENTS.md#scan-before-installing-updating-or-restoring-skills) is:

- Check for newer versions at setup/update time. Scan the exact selected version immediately before installation; explain incompatibilities rather than silently choosing an older copy.
- Stage and scan the entire selected batch before deciding what to install, including available supporting files. Do not execute candidate code just to scan it.
- Skip a separate manual source-code/security audit unless requested. Read skill instructions for correct use and inspect flagged context when needed to assess risk.
- **Warn and proceed** for findings reasonably established as low risk or false positives.
- **Block** dangerous behaviour or unresolved gaps that prevent a risk decision. Resolve missing scan inputs where possible; never hide findings or fabricate complete coverage.
- Verify installed files and skill discovery. Report blocked components individually and do not call the workflow ready if a required baseline skill is missing.

These rules replace the earlier blanket “block every finding” policy. Historical audits remain evidence, not automatic approval of changed files. The installer binds warning decisions to exact payload hashes, finding signatures and coverage reports. It rescans during installation; changed findings need fresh triage. Credentials stay on the device; extra provider access or charges are not implied by setup approval.

If upstream HEAD has changed since this bundle was packaged, the command stops with “requires staging and rescan.” Ask the assistant to finish that preparation under the same policy and rerun setup. The Python command checks freshness; it does not autonomously rewrite skills or approve new findings. No repeat selection approval is needed for the unchanged baseline.

Some accepted scans remain marked partial because of parser limits or optional/example references. Their exact limitations and targeted decisions are preserved in the [scan evidence](audits/advisor-ready-20261103/); they are not presented as clean scans or a guarantee of safety.

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
| [Packaged bundle](advisor-bundle.json) | Exact payload hashes and existing installation evidence |

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
