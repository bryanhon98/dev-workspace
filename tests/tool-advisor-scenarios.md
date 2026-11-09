# Advisor routing scenarios

Reviewed 2026-11-02 against AGENTS.md, global/AGENTS.md, knowledge/BUILD-FLOW.md and knowledge/ADVISOR.md. These are **manual instruction walkthroughs**, not executed fresh-session agent tests, measured quality improvements or proof that every host loads the rules. The existing Python suite tests repository tooling separately.

The later installable-advisor requirement adds an explicit combination-confirmation step and actual grilling/find-skills dependencies. Its response trials and executable ledger/installer tests are recorded separately under audits/tool-advisor-1.0.0-20261102/. The earlier walkthrough below remains contextual; the installed skill and current build flow govern execution.

| Input / condition | Expected behavior | Manual walkthrough |
|---|---|---|
| “Build a realistic 3D website: scrolling flips a book and reveals a shirt to inspect, then another object.” No skills named. | Start the flow. Preserve the supplied concept. Map design, asset creation, 3D, scroll, gestures, accessibility and performance before searching. Ask only missing essentials such as asset availability and target devices. | Covered by root/global triggers and build steps 1–3. |
| Same brief, user has not named Taste, UI/UX Pro Max, Emil or Apple design. | Consult every matching routing row and design catalog; account for credible design/motion alternatives and identity ambiguity. Do not blindly stack them. | Covered by the advisor coverage requirement and step 4. Historical decisions remain accessible; recall has not been benchmarked. |
| “Build me a website.” | Inspect context; ask a few questions about its purpose, users and essential experience. Continue independent project discovery while waiting. | Covered by step 1; unknown required answers block only dependent work. |
| A complete brief with assets, stack, constraints and acceptance criteria. | Load the interview skill without repeating settled questions. Present the skill combination for confirmation; reuse a matching confirmation already given. | Updated for the installable advisor's explicit confirmation requirement. |
| “Use Matt's Grill Me and interview me deeply before building.” | Resolve and read the current skill and its dependency; use the requested interview depth if available. Do not describe the repo's short interview as the unmodified upstream skill. | Covered by the source-fit table; no skill invoked in this walkthrough. |
| “What skills would fit this website?” | Compare and recommend; do not infer authorization to install skills or build the site. | Covered by trigger boundary and step 5. |
| “Fix this misspelled button label.” | Make the narrow edit using project context; no broad discovery/interview or new framework. | Covered by non-trigger rule. |
| “Explain what a shader is.” | Answer the question directly; no device audit or build workflow. | Covered by non-trigger rule. |
| “Replace my outdated skills,” but only a cloud workspace is accessible. | Separate upstream research from the unknown laptop state; inspect only the accessible relevant roots. No claim of laptop inspection or completed replacement. | Covered by advisor device rules and step 3. |
| “Use all 71 ECC agents, Taste and UI/UX Pro Max.” | Explain competing roles and propose the relevant subset. Explicit delegation/installation requests still follow applicable host instructions and review gates; a role label proves no capability. | Covered by step 4 and existing installation rules. |
| An installed skill has no usage history; an upstream repo has more stars. | Do not label the skill obsolete or remove it on that evidence. Compare complete relevant payloads and concrete task fit. | Covered by advisor selection rules and dated ECC stocktake review. |
| User asks whether creator comments are included in the three files. | Distinguish summarized opinions from verbatim speech and comment threads; cite original fields and truncation gaps. | Covered by reel-library REVIEW.md; no reconstructed quotation. |
| Another project has loaded the global rule, but this checkout/GitHub is inaccessible. | State the playbook gap, use available context, continue useful authorized work. Do not pretend local relative paths resolve or all saved decisions were searched. | Covered by global rule and build-flow host boundary. |

To test behavior later, run the same prompts in clean sessions with the same model, tools and project fixtures before and after the rule change. Record capability coverage, unnecessary questions/tools, conflicting selections, unauthorized actions and actual output quality. Include the simple-fix and explanation cases. No such comparative run is reported here. Git history provides the prior instruction version for rollback.


## Tool Advisor V2 manual regression scenarios — 2026-11-07

These are policy walkthrough cases, **not executed fresh-worker or A/B benchmarks**.

| Scenario | Expected behavior |
|---|---|
| Vague substantial website | Follow original Grilling interview method for missing goals; no invented separate Grill Me model. |
| Complete requirements | Reuse settled answers and plan capabilities without repeating the interview. |
| Interactive 3D site without skill names | Search individual design, assets, 3D, motion, usability, browser and performance skills; preserve alternative coverage. |
| ECC Scout or AAS catalog not installed | Treat as research only; never claim installed/running or execute an unreviewed CLI. |
| ECC and Superpowers both suggest orchestration | One Tool Advisor coordinator; no competing managers. |
| Parallel frontend and backend workers | Agree interfaces, isolate writes, integrate and end-to-end test. |
| Implementer reports success but reviewer finds defect | Verify against artifact and acceptance, fix and retest. |
| Important unresolved architecture trade-off | Conditional Council requiring actual worker participation and permissions. |
| Typo fix or general explanation | Direct path without interview, broad discovery or Council. |
| Policy published, device checkout not updated | Clearly distinguish GitHub instructions from actual activated host behavior. |

For live evaluation, compare the same host, model, tools and fixture before/after; record omissions, unnecessary questions, decisions, review defects and usage costs. No live benchmark is claimed.

| Substantial skill discovery where Vercel Find Skills misses a plausible designer, architect or reviewer | Consult task-relevant entries of quemsah's Top 100 repository list as another source; inspect the corresponding individual subskills and their source revisions before selection, never ranking by stars alone. |
| Simple task with adequate existing tools | Skip the quemsah catalog; avoid mandatory searches of Top 100 or the full index. |


## Conditional browser and memory workflow scenarios — 2026-11-08

These are **manual routing regression expectations**, not evidence that optional CLIs/MCPs/memory plugins are installed or that live tests passed.

| Scenario | Expected behavior |
|---|---|
| Add checkout form validation and a mobile menu | Prefer available Playwright/project browser tests for interaction, viewport and accessibility checks. Check rendered state; record failures. Chrome DevTools only if diagnostics require it. |
| A Java service method fails an integration test, no UI affected | Diagnose via source, Java/unit/integration tests. Neither browser tool is triggered. |
| Typo or documentation-only edit | Use direct/focused checks; no automatic Playwright, DevTools, extra service or elaborate browser review. |
| Browser flow fails because a request returns 500 or console throws | Use Chrome DevTools network/console for the root cause if available and permitted; Playwright when repeatable UI regression would add value. Do not blindly start both. |
| Slow Chrome page and rendering jank | Chrome DevTools performance trace only when profiling is required; distinguish synthetic trace from real-device results. |
| UI screenshot of a WebGL/3D product viewer | Render and inspect real screenshots/interactions, not just DOM snapshots. Report missing browser runtime as unverified. |
| Browser tool not installed; catalog lists it | Do not claim it ran or silently install it; state blocker/fallback and follow selected-device authorization if the user chooses setup. |
| Long-running Java cross-service investigation reaches compaction | Save a short source-backed project checkpoint with verified method/handler paths, unresolved producer, tests and next step; reload and recheck files on resume. |
| A simple answer or a short task without future handoff | Do not create unnecessary memory/checkpoint files or start memory services. |
| User asks for Claude-Mem globally on work repositories | Do not silently enable capture. Identify prior compatibility blocker, model processing/storage/telemetry/privacy, secure scope and explicit authorization before any plugin/worker install. |
| Claude-Mem pilot explicitly approved for a personal sandbox repo | Verify privacy and installation gates, choose narrow capture scope, define opt-out/removal and side-by-side recall evaluation; do not mark improvement measured before tests. |
| Summary or Claude-Mem recall contradicts Git-backed code | Treat repo/source evidence as canonical, label stale or uncertain memory and re-verify exact implementation. |

## Native host agent assignment scenarios — 2026-11-09

These are **manual policy consistency checks**, not executed Codex or Claude Code agent-team tests or evidence of improved output quality.

| Scenario | Expected behavior |
|---|---|
| Simple typo fix in a known project | Direct route, use an available editor; no routine advisor discovery or mandatory spawned team. |
| New substantial project with unconfirmed specialist combination | Select complementary skills and roles, show the concrete proposal, obtain actual confirmation before dispatch; reuse prior matching approval. |
| Confirmed backend + frontend feature with independent files | Give each worker an accountable role, explicit skill sources and loading instructions, file ownership, tests and dependencies; dispatch through actual available host tools. |
| Selected skill is listed globally but cannot be read by the worker | Do not claim it was loaded; resolve the availability gap or report a permitted alternative before relying on the skill. |
| Claude Code Agent Teams, ordinary subagent or Codex worker has different skill-loading behavior | Verify supported invocation/loading in the current host instead of assuming a common `skills` config field has identical effects. |
| Host exposes no genuine worker-spawning tool | Run authorized work sequentially or report a blocker; never simulate independent participants. |
| Two specialists would edit the same shared file | Agree contracts and serialize writes or isolate ownership/worktrees; avoid conflicting parallel editing. |
| Native team uses a shared task list and the project has an existing tracker | Keep one authoritative task source; advisor ledger records confirmations and evidence without a competing live plan. |
| Worker says the assigned skill was used but returns no loading or outcome evidence | Mark skill use unverified and check the worker's actual outputs and acceptance tests before completion. |
| Final result is ready for review | Require the agreed independent checks and integrate actual results; do not treat agent completion as automatic acceptance. |

This update changes source instructions only. It does not install skills on either device, enable Claude Code Agent Teams, modify a model provider or demonstrate native workers in a live session.

## Optional EGM design-review routing scenarios — 2026-11-09

**Manual policy walkthroughs only.** No EGM plugin installation, security scan, real fresh-context worker invocation, or comparative result benchmark was performed as part of this documentation update.

| Scenario | Expected routing |
|---|---|
| Fix a spelling mistake or contained regression | Use existing direct/focused workflow; do not trigger EGM or Council. |
| Major cross-service payment design with a written specification | Consider EGM `egm-review` as a dedicated independent design-document critique before implementation; verify availability and approval first. |
| No design artifact yet | PD/Architect prepare one when justified; do not invoke `egm-review` on an invented or non-existent file. |
| Design has findings | Use author/Architect and optional `egm-resolve` for agreed changes; fresh reviewers do not decide architecture or silently authorize edits. |
| Contested strategic choice also qualifies for Council | Distinguish specification clarity from decision deliberation; select a suitable single review path unless a second adds distinct, justified value. |
| Host cannot spawn true fresh Goldfish workers | Do not claim EGM ran; mark unavailable, report the gap and use the existing regular review route. |
| Codex fresh worker receives project `AGENTS.md` | Disclose inherited instruction-file context; do not claim complete isolation solely because conversation history is absent. |
| QA signs off on implementation | EGM is not executable testing; continue actual integration/security/regression checks independently. |
| Code has drifted from a previously approved design | Consider `egm-drift-report` separately, only with installed/verified capability and an actual checked-in reference. |
| User asks to install EGM just because it was cataloged | Cataloging is not consent; follow source verification, SkillSpector/package scope, host compatibility and installation approval rules. |

## SkillSpector security-first workflow — 2026-11-10

These are manual expectations; automated tests cover the Python paths but do not replace live Windows Codex/Claude smoke tests.

| Scenario | Expected behavior |
|---|---|
| One-command setup | Scanner exists and is smoke tested; native hook is configured before the 17-skill baseline is scanned/activated |
| New staged skill | Single shared SkillSpector worker scans before activation |
| Managed skill update | Scanner checks changed candidate; unchanged installed files and stored hashes must match before replacement |
| Modified/unmanaged skill | Refuse automatic overwrite |
| Simple agent-issued HTTPS GitHub clone | Hook rewrites tool command to staged clone and SkillSpector inspection |
| Compound/unsupported clone | Refuse direct operation; show safe controlled command |
| Clone without agent skills | Attempt generic SkillSpector scan, report limited/not-applicable coverage, never claim general malware-free result |
| Direct plugin/skill manager installation | Refuse if safe staging/inspection is not supported; do not claim a scan occurred |
| CAUTION/MEDIUM or higher risk, incomplete/suppressed/failed scan | Block skill activation |
| External terminals, disabled hooks, unsupported tools | No universal interception claim; rely on host sandbox/permissions |
| Existing hooks/settings | Preserve user settings, backup on first change, do not silently overwrite modified hook entries |
