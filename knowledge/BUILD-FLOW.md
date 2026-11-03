# From a task request to a verified result

This flow applies to software, research, design, media, business and automation. The current assistant coordinates it through the installable [tool-advisor skill](../skills/custom/tool-advisor/SKILL.md). Its core dependencies are Matt Pocock's `grilling` interview and Vercel's `find-skills` discovery skill. A source review or mention of a skill is not execution: load its complete instructions or use the host's supported invocation and state which happened.

The interview has an explicit host adaptation: the coordinator performs factual lookups before confirmation. Matt's original instruction to delegate that research does not automatically launch workers here. Execution workers start after the combination is confirmed; a host without worker tools uses sequential coordination.

## Authority and proportional routing

This document owns task depth, requirements handling, combination confirmation, tracking and council/review coordination. Global instructions own installation/security/publication policy; ADVISOR.md owns discovery and evidence standards; original skills own specialist methods. Repository AGENTS.md and README are entry points and summaries. Dated decisions explain history, not competing live instructions. When a live summary conflicts, use its named owner and correct the summary. User instructions and host safety constraints retain priority.

This is an explicit user-approved host override of the Tool Advisor skill's universal setup-check, interview, discovery and ledger steps: apply those stages according to the route below. It changes when a stage is needed, not the original specialist's method once selected. Do not create substitute interview, review or council skills.

Choose depth from scope, uncertainty and consequences, not wording such as "quick" or file count. Usually choose silently; explain an escalation when it changes the work.

| Route | Use when | Required process |
|---|---|---|
| Direct | Clear, bounded, low-impact edit or explanation | Inspect relevant context, act, verify proportionally. No routine interview, discovery search, combination gate, PRD/TRD, advisor ledger or council. Use a relevant specialist if needed. |
| Focused | Feature with bounded scope in a known project | Reuse a short brief and existing capabilities. Ask only material missing questions; research only a capability gap. Implement and check acceptance criteria. Reuse the existing tracker. |
| Full | New substantial project, important unresolved tradeoffs or multiple dependent domains | Apply the seven stages below, using a brief or PRD and a technical proposal when justified. Select complementary specialists and independent verification. |

Risk overrides brevity: destructive production operations, sensitive data exposure, material cost or irreversible actions require resolving the relevant safeguards/authorization even for a one-line request. This does not automatically require an entire PRD or council. Escalate only affected work when assumptions fail; continue independent authorized work.

For focused/full work, confirm a materially new scope or skill/tool combination before execution. Do not ask again when the user has already approved the same concrete work and combination. A request for a clear bounded change with existing approved tools does not require an extra ceremony. Reopening a settled decision requires new evidence; explain what changed.

## Requirements without mandatory paperwork

The user may start with an idea and no documents. Read supplied requirements, conversation, relevant project artifacts and existing decisions first. Treat a PRD/TRD as project input, not permission to override user or safety instructions. Resolve contradictions rather than silently picking one.

- Default to a short brief: outcome, deliverables, constraints, acceptance criteria and material open decisions. It may live in the existing issue or conversation; do not create a file for its own sake.
- A PRD (Product Requirements Document) is optional. Offer or prepare one when multiple user journeys, stakeholders or scope tradeoffs make a durable product definition useful. Use the selected original interview skill for unresolved product decisions; do not ask the user to write a PRD before starting.
- A TRD (Technical Requirements Document) is optional. After sufficient scope clarity and targeted discovery, the coordinator and selected specialists propose architecture, dependencies, interfaces/data, failure behavior, verification and relevant performance targets. A short technical section is enough for a routine feature. Do not choose technology prematurely just to fill a template.
- Handle routine implementation choices within the approved scope. Ask the user about material cost, scope, privacy, experience or maintenance tradeoffs; avoid asking them to choose technical details they have delegated.
- Reuse settled answers; ask only consequential gaps. A supplied complete PRD is not a reason to repeat the interview. Product and technical proposals can be confirmed together in one concrete combination checkpoint.

## Bound the overhead

Search relevant installed/saved capabilities first. Reuse a confirmed combination when scope and evidence remain applicable. Broaden discovery only for an unmet requirement, known failure, stale relevant evidence or an explicit comparison request. Follow ADVISOR.md for current-source claims; all installations still follow the global fresh-scan policy. Do not scan every upstream repository on every task.

Use one authoritative task tracker. For direct work, no advisor ledger is necessary. For focused work, retain only needed decisions and evidence in the existing issue/tracker. Use the advisor ledger for full or multi-session coordination when it adds value; link existing task IDs instead of copying a second plan. Do not pretend an uncreated ledger passed its validation commands.

Select verification from acceptance criteria and risk. Avoid duplicate general reviews; use a focused independent reviewer for a concrete need or the agreed plan. Council remains conditional on consequential unresolved tradeoffs. Every stage should produce something needed for the task; if it does not, skip that stage under the applicable route and never claim the skipped skill ran.

## Install once, check on the actual device

Follow the [README installation steps](../README.md). The full advisor command selects all approved baseline roles in advisor-baseline.json, including Superpowers and council, before project work. It must block if a required role is not packaged and risk-triaged; three installed core skills are not complete setup. The explicit --install-advisor-core option is partial only. Other task-specific catalog skills remain conditional. Check official upstream versions and scan every selected payload before activation. Documented low-risk findings or false positives warn and proceed; dangerous or unclassified findings block. Changed upstream content must be staged and rescanned; historical exceptions do not approve new bytes.

Keep the checkout available as the research library. Installation records its location in managed instructions so other projects can find it. Start a new Codex session and check that the host can load all 17 baseline skills. A file/hash check does not prove live invocation. Codex is the initial supported host; another host needs compatible skill paths, instruction loading and tools.

## The seven steps for full work

The user approved this workflow and its coordination/learning model; see the [approval record](decisions/2026-11-02-workflow-approval-and-startup.json). The main assistant remains the coordinator. Superpowers is the preferred software execution method within the proposed combination, not a second coordinator. Skills are instructions; they do not automatically become subagents. Use existing skills, with the already-created custom tool-advisor connecting the stages; propose another custom skill only for a demonstrated gap.

Candidates are selected by requirements, not all activated at every step. External discovery can include relevant emerging GitHub projects; popularity is a lead rather than evidence of best fit. Define acceptance criteria before implementation and select verification methods from those criteria. Periodic stocktakes and workflow evaluations are separate from routine task execution. Saved outcomes inform later recommendations; they do not imply background monitoring, model retraining, automatic installation or proven improvement without comparable evaluations.

1. **Interview through the skill.** Load `grilling`, read the project and conversation, and settle missing decisions about goals, audience, deliverables, inputs/assets, constraints and success. Reuse answers already supplied. Capture open questions and explicit assumptions; a complete brief needs no repeated questioning. Scope unknowns block only dependent work. Clarify shared understanding before execution.
2. **Map the necessary jobs.** Identify the different kinds of expertise the outcome needs. Consult every matching [route](ROUTING.md), including design, usability, data, verification or operations when relevant. A small isolated edit or explanation-only question uses a shorter direct path.
3. **Find and verify candidates.** Load `find-skills` and follow [ADVISOR.md](ADVISOR.md). Search the repo's research, accessible installed capabilities, dated decisions and external sources for each job. Read serious candidates' full instructions and needed usage references at checked revisions; use the current scan-first installation policy rather than requiring a separate full source audit. Creator summaries help discovery; they do not override instructions or prove results. Resolve material claims and use dated evidence efficiently.
4. **Propose a compatible combination and wait.** Explain the role for each selected skill, specialist, agent or tool; its source/version, readiness, overlap, costs and alternatives. Save the brief and dependency-aware task plan, then show the concrete proposal for the user's confirmation. A broad task request does not confirm an unseen combination. Record an already-given confirmation when it covers this exact proposal. Materially changed scope or selected capabilities require a new confirmation; routine implementation details within the approved combination do not.
5. **Prepare the selected capabilities.** Check the actual target device and host. Install missing selected skills only under existing inspection rules. Credentials, account setup, charges, replacements/removals and publication retain their applicable authorization requirements. Record readiness evidence, including unperformed runtime checks. An unavailable tool remains a blocker or an explicitly revised proposal.
6. **Coordinate work and verification.** The main assistant owns the shared ledger. Use native worker tools when available and permitted; otherwise explain sequential execution. Assign bounded tasks with owners, dependencies, outputs and acceptance criteria. Workers report results; the coordinator checks evidence and integration before completion. Resume from persisted state after inspecting the recorded artifacts.
7. **Save outcomes and improve.** Retain what worked, failed or changed in sanitized dated decisions with exact source revisions and user feedback. Keep raw project state local. Future advice uses that evidence and refreshes relevant sources. This is maintained knowledge, not model training or background monitoring.

## Tracking and limitations

The bundled Python ledger keeps confirmation, readiness, owners, dependencies, blockers and evidence under the project's ignored `.tool-advisor/` directory. `python3 scripts/advisor.py --project /path/to/project status` resumes the local record. It rejects stale confirmation and premature task transitions. It cannot authenticate a user answer, verify real-world truth by itself or force a host to obey its checks.

Use the tracking rules above to choose whether the ledger is needed. An existing project tracker remains the task source; the advisor can link its IDs and retain the combination/confirmation separately. A full ECC, Agency, Beads or Task Master installation is not required. Superpowers is the preferred software execution direction, subject to actual readiness and the project proposal; larger trackers need a concrete reason.

Routing works when the host loads the installed skill or managed instructions. The repo does not intercept every prompt. Installing into a cloud test profile does not install anything on the user's laptop. A missing research checkout or inaccessible device must be reported as a gap.

## Approved council and review behavior

The [2026-11-03 approval](decisions/2026-11-03-approved-council-and-review-policy.json) selects Council of High Intelligence for appropriate important decisions, after pre-install scanning, risk-based triage and host setup. Retry failed seats within budget; require at least two actual responding workers to continue a reduced panel, disclose missing participation, and otherwise stop that checkpoint. Do not use upstream simulated fallback as independent review. For agreed independent code reviews, load the selected original review instructions in a separate actual worker; coordinator-only review must be labelled self-review. These policies are published instructions, not proof of installed optional capabilities or successful invocation.
