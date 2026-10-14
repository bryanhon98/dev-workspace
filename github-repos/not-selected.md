# Not selected for this setup

[Catalog](README.md) · [Full evidence register](reviews.json)

These 26 entries were considered and left out of the chosen catalog. Some are useful alternatives or specialized projects; omission is a fit/overlap judgment, not proof of copying or poor quality. No existing inventory entry was removed and nothing was uninstalled.

## Engineering

| Repository | Why it is not selected |
|---|---|
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | Broad writing/review/refactoring trigger; cautions to stop and ask can increase permission-like friction. Inspired by Karpathy observations, not authored or endorsed by Karpathy as established by this review. Search found mostly directories and commentary, not reproducible comparative evidence. |
| [DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail) | Current v5 differs from the externally tested v4.8.4. Mac issue #1043 reports truncated JSON at v4.13; current mode/subagent files still contain immediate exits after finish, but this review did not reproduce or prove the current revision affected. Omission is primarily scope/overlap, not a claim the tool has no benefit. |
| [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | Do not conflate older prose-output benchmarks with current proxy's author-reported 33.2% input reduction. Broader compression correctness, cache effects and compatibility require workload-specific checks. External issues are user reports rather than verified defects in this review. |
| [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) | Session-persistent rules shape every reply, require concrete time estimates and can add repeated next actions/clarifications. Avoid assuming all ADHD readers share the generalized cognitive claims in prompt. Codex hook issue directly affects advertised always-on path; manual skill path is distinct. |
| [cursor/plugins (pstack only)](https://github.com/cursor/plugins) | Overlaps Superpowers heavily, adds many principles/playbooks and host-specific orchestration. Source tells agent to name principles in replies, loads unslop on prose and architecture exploration at function boundaries; conflicts with user's wish to avoid broad behavior. Independent notes are source commentary rather than benchmarks. |
| [Jakeschincariol/replica-skill](https://github.com/Jakeschincariol/replica-skill) | A broad eleven-stage workflow adds overlap and a niche objective rather than improving general Codex work. Weighted self-entered feature parity and image edge scores are not proof of behavioral equivalence. Project is new; external search returned directories/editorials rather than convincing independent usage benchmarks. |

## Design

| Repository | Why it is not selected |
|---|---|
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | A credible alternative design workflow, but overlaps existing Designly/Vercel tools and adds an engine, hooks, downloads and network roll requests. Revisit if those live variations solve a concrete need; not a malware judgment. |
| [kylezantos/design-motion-principles](https://github.com/kylezantos/design-motion-principles) | Substantial duplication with Emil's first-party skills and existing design direction. The author explicitly says the named designers neither authored nor endorsed these interpreted lenses. Absolute rules such as never animating keyboard actions need judgment. Independent user evaluations are insufficient in the collected material. |
| [VoltAgent/awesome-claude-design](https://github.com/VoltAgent/awesome-claude-design) | Strong overlap with the other VoltAgent catalog and existing visual tools. README's one-drop scaffolding claims are promotional, not measured outcomes. Its disclaimer explicitly identifies the references as unofficial and non-endorsed. Independent evaluations and Mac/Codex workflow tests are insufficient. |

## Domain

| Repository | Why it is not selected |
|---|---|
| [nidhinjs/prompt-master](https://github.com/nidhinjs/prompt-master) | A usable prompt workshop, but ordinary Codex planning and the existing skill-creation workflow cover the current need. No demonstrated extra benefit justifies another global prompt framework. |
| [rebelytics/one-skill-to-rule-them-all](https://github.com/rebelytics/one-skill-to-rule-them-all) | Do not infer it silently installs changes: source explicitly stages updates and says nothing is live until the user installs it. Nevertheless, any future candidate it creates or edits must pass the user’s skill-creator plus SkillSpector activation policy; its own staged review cannot replace that gate. Avoid autonomous installation or global first-tool activation. |

## Orchestration

| Repository | Why it is not selected |
|---|---|
| [nyldn/claude-octopus](https://github.com/nyldn/claude-octopus) | Real Codex support and broader provider orchestration, but too much overlapping workflow/runtime for this shortlist. Claudex is the narrower selected cross-provider option. |
| [karpathy/llm-council](https://github.com/karpathy/llm-council) | The author explicitly describes a Saturday experiment and says it will not be supported or improved. Peer ranking is not ground truth, and common model errors can survive synthesis. Its original model defaults, dependency health, privacy, and operational hardening would require separate review before actual use. No evidence here establishes better coding outcomes. |
| [0xNyk/council-of-high-intelligence](https://github.com/0xNyk/council-of-high-intelligence) | Useful optional debate protocol, but native reviewers cover the present need. Failed live seats can become simulated personas; named seats do not prove independent models or corroboration. |
| [ruvnet/ruflo](https://github.com/ruvnet/ruflo) | Its broad runtime footprint duplicates parts of the current harness and adds configuration, permission, and persistence decisions. Claims about swarm performance, learning, federation security, and scale were not independently validated in this review. The omission is a fit/complexity judgment, not a demonstrated defect or claim that the implementation is fake. A scoped benchmark and package-level audit would be needed before recommending adoption. |
| [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents) | Real Codex persona conversion, but no need for a bulk role library alongside existing skills. Personas are instructions, not credentials; revisit a specific missing role. |
| [wshobson/agents](https://github.com/wshobson/agents) | Real native and generated Codex routes with specialist material, but a broad additional collection overlaps the chosen baseline. Revisit one child for a concrete unsupported technology. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | Real Codex hooks/MCP/configuration support, but adopts another large setup framework alongside Superpowers and this repository. Keep it as an evaluated alternative, not an additional baseline. |

## Runtimes

| Repository | Why it is not selected |
|---|---|
| [diegosouzapw/OmniRoute](https://github.com/diegosouzapw/OmniRoute) | A capable alternative gateway, but installing several routers duplicates service and credential management. Claude Code Router is the selected candidate; aggregated free-tier totals are not guaranteed usable quota. |
| [tashfeenahmed/freellmapi](https://github.com/tashfeenahmed/freellmapi) | Useful for free-tier experiments, but duplicates the selected gateway. Aggregated provider allowances and optional paid catalog access do not guarantee reliable free coding capacity. |
| [adewaskar/jarvis](https://github.com/adewaskar/jarvis) | Omit from a focused Codex setup catalog; retain a separate inspiration bookmark only if a voice UI is desired. Source documents a default-deny gate for effectful tools, but switching writes on is a broad authorization change. The read-only label still includes generation calls that can incur costs. No microphone, subscription, or tool execution was tested. |
| [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) | Distinct local classification/MCP capability, but no current typed-decision workload justifies adding model downloads and evaluation duties to a personal Codex setup. Revisit with a labeled target dataset. |
| [ultraworkers/claw-code](https://github.com/ultraworkers/claw-code) | Omit from the practical personal Codex setup catalog. Installing and maintaining a parallel harness adds substantial scope without an established need. Preserve only a research citation if harness internals are relevant. Neither its popularity nor its parity documents establish production suitability; no live runtime, provider connection, or parity test was performed. |

## Tools

| Repository | Why it is not selected |
|---|---|
| [austinmarchese/buildpartner-plugin](https://github.com/austinmarchese/buildpartner-plugin) | Session hooks modify global CLAUDE.md, flush usage events to the service and check updates. PermissionRequest hook auto-allows a regex-matched family of plugin MCP tools. These are meaningful setup changes requiring their own review, especially alongside the user’s explicit scanner/version gate. This omission is about fit and scope, not a malware finding. |
| [chrys/AgentCraft](https://github.com/chrys/AgentCraft) | Pulling a repository or copying SKILL.md is not a SkillSpector scan or dependency audit. Some Antigravity workflows automatically bring sibling skills, broadening a selection. Adopting it would require integrating per-version staged review, scanner results, user-global Codex paths, and installation records. Retain the current focused setup tooling instead. |
| [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Directory membership is not a runtime compatibility or security guarantee; the README explicitly warns that bundled software/MCP contents may change. Individual external source pins and nested payloads need separate inspection under the existing scanner policy. Prefer the user’s native Codex connector/plugin when available; avoid installing a second copy only because it appears here. |

## Earlier exclusions preserved

Your prior exclusions remain excluded: cctop, Secret Redactor, Agent Flow Mod, Context Lens Mod, Oh My Claude, SkillUI, SecuritySweep, Composer, Manifest, Text Observer and Recall. These were not silently reintroduced or counted among the 50 reviewed candidates. Alternative implementations superseded by your chosen parent repositories were not added as duplicates.
