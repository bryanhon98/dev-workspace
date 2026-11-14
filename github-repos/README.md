# Reviewed GitHub options for my Codex setup

Start here. **Initial October collection: 50 recovered repositories reviewed; 24 conditional options saved; 26 not selected.** Reviewed 14 October 2026 at the linked revisions. This is a curated reference catalog, not a list of installed or security-approved components.

Choose by the job you actually do: AnyDoc for documents, Watch for videos, Emil for UI motion, Corey Haines for marketing, and Obsidian Skills if you use an Obsidian vault. Your selected Taste BrandKit/Image-to-Code children are retained together. Keep broader workflows and extra runtimes optional.

| Category | Saved options |
|---|---|
| [Engineering and security skills](skills/engineering.md) | Matt Pocock — architecture subset; Addy Osmani — performance subset; Anthropic — MCP Builder only; Cloudflare Security Audit; shadcn/improve (optional audit/planning) |
| [Design and motion skills](skills/design.md) | Vercel Agent Skills; UI/UX Pro Max; Taste — BrandKit and Image-to-Code only; Emil Kowalski — motion subset; Extract Design System; Ian Xiaohei Illustrations; Stageshow; Impeccable (restricted); Dimensional Drawing; Oil UI; Brand Identity |
| [Marketing and writing skills](skills/marketing-and-writing.md) | Corey Haines Marketing Skills; Humanizer; Claude SEO; Instagram Agent Skills |
| [Knowledge and image investigation skills](skills/knowledge-and-investigation.md) | Geo-Sleuth; Obsidian Skills |
| [Design references](references/design.md) | Awesome Design MD; Meta Astryx (React design system) |
| [Development plugins](plugins/development.md) | Claudex Loop |
| [Document and video tools](tools/documents-and-video.md) | AnyDoc; Watch (claude-video); rea-video (video breakdown/remake planning) |
| [Local generative-media applications](tools/local-media-generation.md) | WanGP / Wan2GP — optional local AI video, image, audio and 3D runtime (not a skill) |
| [Context and image MCP tools](mcp/context-and-images.md) | Context Mode; PhotoCraft |
| [Design-inspiration MCP tools](mcp/design-inspiration.md) | Awwwards MCP — site reference, motion and optional browser evidence (not a skill) |
| [Model routing software](tools/model-routing.md) | Claude Code Router |
| [Agent orchestration software](tools/agent-orchestration.md) | Paperclip (library only) |
| [Separate assistant runtimes](agents/persistent-assistant.md) | Hermes Agent |

## Later user-saved library additions

**15 November 2026 — Improve, rea-video, Teardown and EGM:** [shadcn/improve](skills/engineering.md#shadcnimprove--codebase-audit-and-executable-plans) and [JuneYaooo/rea-video](tools/documents-and-video.md#rea-video--juneyaooo) were newly saved as *optional research candidates*. [elvarofficial/teardown](skills/user-saved-capabilities.md#elvarofficialteardown) and [Google Elephant-Goldfish Model (EGM)](plugins/development.md#elephant-goldfish-model-egm--googleelephant-goldfish-model) were **already saved**, so no duplicate entries were created. The new sources were checked at pinned revisions; installation dependencies, overlap, and security/permission considerations are in their respective entries. **No skills/tools installed, scanned, activated or added to the three mandatory core skills.**



**13 November 2026 — WanGP:** [WanGP / formerly Wan2GP](tools/local-media-generation.md#wangp-formerly-wan2gp--deepbeepmeep) saved as an optional **local generative-media application**, not a skill or default installation. It supports model-dependent video/image/audio/3D generation with an optional MCP/API interface. Record includes its **custom community license**, GPU/VRAM and setup constraints, source revision and security considerations. The user did not request an installation or host integration; none was performed. The three mandatory Tool Advisor skills, `inventory.json` and device setup remain unchanged.



**10 November 2026 — Instagram product-design Reel:** [five newly verified skill candidates](skills/design.md#stageshow--benji-taylor) (Stageshow, Impeccable, Dimensional Drawing, Oil UI and Brand Identity) and [one MCP research candidate](mcp/design-inspiration.md#awwwards-mcp--insane0777) added to the existing library. **Emil Kowalski's motion subset and the Taste family were already saved**, so no duplicate catalog items or automatic changes to the user's prior Taste child-skill selection were made. Impeccable's documented sandbox/permission-bypass fallback is a **material security blocker for a default install**; the MCP is a separate executable integration and also requires its own approval. No skills or MCP servers were installed, executed, security scanned, enabled or added to the three-skill Tool Advisor baseline.



[Meta Astryx](references/design.md) was saved on 10 November 2026 as an optional React 19+ design-system/component-library reference. It is not an agent skill, has not been installed or security-scanned, and remains outside the setup inventory and baseline.

[Agent Reach, Vercel Agent Desktop, Karpathy Guidelines and Teardown](skills/user-saved-capabilities.md) are saved for task-specific discovery only. Three are new catalog records; Karpathy reuses its existing record. None is installed or added to the default baseline by this selection. The October counts above describe the original collection.

[Awesome Claude Video Skills, Three.js Skills and Hyperframes](skills/video-and-3d.md) are also saved for library discovery only. The unspecified motion-skills collection was skipped; existing Emil motion entries remain.

[juliobsz/skills — awwwards and jury](skills/design.md#juliobsz--awwwards-and-jury) are saved as optional website-building and visual-review candidates, not installed or part of the baseline.

[Paperclip](tools/agent-orchestration.md) was added on 8 November 2026 as an optional agent-orchestration **software** candidate, not a skill. Cataloging it does not install its app or bundled development skills.

[New November 8 GitHub candidates](research/2026-11-08-nine-projects.md): Playwright, Firecrawl, Chrome DevTools MCP, whatsmyagentdoing, Claude-Mem, Hallmark, Last30Days, Graphify, and the already-cataloged Watch. Eight new research references; nothing installed or approved for activation.

[Agency Agents and OpenMontage](research/2026-11-08-agency-agents-openmontage.md) are saved as optional specialist-persona and end-to-end video-production references. Agency's existing **no bulk install** decision remains; neither project is installed or part of the approved baseline.

[Google Elephant-Goldfish Model (EGM)](plugins/development.md#elephant-goldfish-model-egm--googleelephant-goldfish-model) was researched on 9 November 2026 for an **optional fresh-context pre-implementation design review** across Codex and Claude Code. It remains uninstalled, outside the approved default baseline, and conditional on actual native subagents and the normal installation/approval checks.

## What was left out

[See all 26 decisions](not-selected.md). Main reasons: overlapping global behavior (Ponytail/Karpathy/Caveman), extra orchestration frameworks alongside Superpowers and Claudex, duplicate gateways, Claude-specific provisioning, or a narrow job absent from this setup. These are not plagiarism findings. A derivative project can be useful when it adds substantive capability.

## How this connects to setup

- These files save GitHub links and research, not upstream payloads. Parent collections appear once; the notes name selected children.
- **Searchability:** `python3 scripts/knowledge.py search "react design system" --limit 30` indexes entries with linked GitHub repository headings (`##` or `###`) across category and research Markdown files, including saved entries absent from `reviews.json`. Search also covers the Reel library, inventory, prior decisions and historical reviews. Open the returned `details` path and verify upstream before recommending. Catalog entries without a linked section heading may not be returned. An indexed candidate is not installed or approved.
- `inventory.json` remains the actual setup catalog. Research choices are not automatically added to it or installed by selecting all existing inventory skills.
- After you select a new candidate, inspect the exact source and dependencies, run SkillSpector for its skills, verify the target-device installation, then update the inventory and device log. Research does not satisfy that installation gate.
- Plugins/MCPs may need manual installation, credentials or another runtime. No authentication state, session index or private vault belongs in this backup.
- No global communication rules, installed components or existing installation records were changed by this review.

## Evidence and remaining gap

[The evidence register](reviews.json) records every recovered candidate, exact revision, source links, outside reports, reviewer assessment, final selection and review depth. No candidate code was run. Old issue reports were compared with current pinned source; a code change is not proof of a tested fix. Lack of trustworthy independent reviews is recorded rather than filled with promotional claims. Stars were not used as a quality score.

Separate AI reviewers worked by domain, and the lead challenged selection decisions. This used neither hired humans nor a guaranteed mix of model providers; agreement is not a correctness guarantee.

**Coverage is complete for the 50 recovered URLs, not for the entire shared chat.** Its reader truncates long answers at 20,000 characters. The latest list cuts off in section II (plugins), and earlier visible replies recover only part of the later material. The remaining later MCP/software/other sections still need to be supplied. They are pending, not rejected or silently counted as reviewed.

On continuation: compare new URLs against the 50 records, retain your earlier exclusions, review each genuinely new repository, then update these counts and decisions. Do not restart completed reviews unless a source revision or relevant evidence changes.
