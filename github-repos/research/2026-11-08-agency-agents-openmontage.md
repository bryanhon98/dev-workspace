# Agency Agents and OpenMontage — optional specialists (2026-11-08)

[Catalog](../README.md) · [Routing](../../knowledge/ROUTING.md)

**Status:** source-verified research leads, **not installed, activated, scanned, security-approved, or added to the 17-skill baseline**. Current source snapshots are observations; refresh exact versions and risk gates before use. No candidate code or installer was run in this review.

## [Agency Agents — msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)

- **Classification:** MIT-licensed collection of role/persona instruction files, with an optional distinct [native management app](https://github.com/msitarzewski/agency-agents-app). **Not** a fleet of separately trained AI models, and **not** a substitute for a runtime or coordinator.
- **Current source claim:** README describes 230+ specialists across engineering, security, design, testing, product, marketing, project management and other divisions. Examples include Backend Architect, Frontend Developer, DevOps Automator and Reality Checker. Count may differ from website or change over time; don't infer independent expertise from names.
- **Fit:** For a substantial project with a *specific missing specialist role*, Tool Advisor can inspect a named persona and propose it as a bounded worker/reviewer if the host supports real workers. Examples: specialist design review, release engineering review, narrowly scoped security advice. Keep the user-approved coordinator, Superpowers execution method and independent-review evidence gates.
- **Overlap and prior decision:** This repo previously considered the collection but **excluded bulk installation** in [not-selected.md](../not-selected.md). That remains valid. A persona is a set of instructions, not credentials, a new model, guaranteed expert accuracy, or proof that a separate reviewer ran. Pick **one or a small justified subset** if it improves a real job; don't launch an entire agency for routine Java bugs.
- **Requirements:** Compatible Claude Code/Codex agent loader and selected permissions, isolation for independent workers, user authorization and applicable review/security gates before installing any files. MIT source; normal LLM/tool usage and any third-party services still cost resources.
- **Observed revision:** [`b859c515d813efcfc4755d3471dd9e7686c7706d`](https://github.com/msitarzewski/agency-agents/tree/b859c515d813efcfc4755d3471dd9e7686c7706d), upstream `main` as observed 2026-11-08. README and repository metadata inspected; individual specialist files and scripts not audited.
- **Decision:** **Optional specialist lookup only**. Preserve existing bulk-exclusion. A new named specialist needs exact-source inspection, host compatibility check and user-approved installation.

## [OpenMontage — calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)

- **Classification:** AGPL-3.0 open-source **video production framework/application**. It includes its own pipeline manifests, skill-like director instructions and many tools, but the whole project is **not one drop-in skill**.
- **Current source claim:** 12 production pipelines for topics such as explainers, talking-head edits, documentary montages, cinematic teasers, podcasts and other videos. It coordinates research, script/storyboards, footage or generated assets, audio, subtitles, editing and rendering through an AI coding agent.
- **Fit:** Select when the user's outcome is an **actual finished video** involving multiple production stages. May suit creating website promo clips, product showcases or educational tutorials.
- **Overlap:** [Watch](../tools/documents-and-video.md#watch-claude-video) extracts frames/transcripts and helps understand an *existing* video; [HyperFrames](../skills/video-and-3d.md#hyperframes) and Remotion are composition/rendering engines; OpenMontage orchestrates a **broader production**. Avoid automatically stacking all of them or confusing a rendered video with an interactive 3D website. It may use composition engines within its own workflow.
- **Prerequisites/cost:** Python, Node/Remotion, FFmpeg and project-specific dependencies, plus a working coding-agent runtime and local resources. Has stock-footage and local narration options; premium image/video/audio providers may charge API fees. 'Zero API keys' only covers available free/local media paths, not arbitrary generated cinematic footage. Content licensing for source footage/music needs checking.
- **Limitations:** Many stage instructions/tools increase configuration and security surface; output claims and automatic quality gates are vendor statements, not independent quality benchmarks. Verify realistic Windows setup, selected pipeline dependencies, model/provider cost, file/credential access and genuine final rendered output before broad adoption. AGPL licensing may matter if deploying/adapting the service.
- **Observed revision:** [`d21f5d4eaa08422b09c7091757a05affcbabb35b`](https://github.com/calesthio/OpenMontage/tree/d21f5d4eaa08422b09c7091757a05affcbabb35b), upstream `main` as observed 2026-11-08. Official README and repository metadata inspected; no installation, render or capability benchmark performed.
- **Decision:** **Conditional video-production candidate** only when a project needs end-to-end production, not for every Watch/video-analysis task.

## Workflow placement and boundaries

1. **Agency Agents:** Tool Advisor remains the sole coordinator, identifies a missing role, reviews a specific persona, and uses native independent workers only when present and worthwhile. Never treat role names as separate engines or install the whole collection by default.
2. **OpenMontage:** Tool Advisor selects it for a finished-video deliverable after checking Watch/HyperFrames/Remotion and verifying what type of footage/animation is required; the selected production pipeline controls its internal tools. Get approval for provider charges and asset permissions.
3. **Nontriggers:** Pure Java implementation, one-page frontend fixes, simple video transcription, or ordinary questions do **not** trigger an Agency multi-agent rollout or OpenMontage setup. Catalog inclusion never triggers an installer, downloads or cloud credentials.
