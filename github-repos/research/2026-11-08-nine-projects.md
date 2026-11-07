# Nine GitHub candidates — saved for discovery only

[Back to GitHub catalog](../README.md) · [Task routing](../../knowledge/ROUTING.md)

Researched 2026-11-08. This is **cataloging, not installation or security approval**. Eight candidates are newly indexed; Watch is an existing reviewed entry linked here to avoid duplication. The reviewed revisions are snapshots, not automatic recommendations for future installations. No new skill payloads, executable scripts, plugins or services were installed or run. The approved 17-skill baseline and `inventory.json` are unchanged. Before installing, recheck the exact upstream version, scanner findings, local prerequisites, licenses and device readiness.

## Browser automation and web data

### [Playwright](https://github.com/microsoft/playwright)

**Classification:** Framework; separate Playwright CLI and MCP integrations.

**Use:** Repeatable browser tests, screenshots, multi-browser end-to-end workflows.

**Existing overlap:** Chrome DevTools for debugging; Playwright CLI already recorded in a 2026-11-02 decision.

**Dependencies/cost:** Node/browser binaries; Apache-2.0; tests/model use local resources.

**Important limitation:** Best when creating regression tests; DOM alone does not verify 3D rendering. Do not assume existing Chrome session is used.

**Observed upstream revision:** [`07c7069c`](https://github.com/microsoft/playwright/tree/07c7069cdbb1f5c7331d3f4d2abd864dcfde745a).

### [Chrome DevTools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp)

**Classification:** MCP/CLI browser-debugging integration, not a skill.

**Use:** Debug live Chrome pages, console errors, network failures, performance traces.

**Existing overlap:** Complement Playwright's multi-browser test suite; avoid redundant always-on browser interfaces.

**Dependencies/cost:** Chrome and Node; Apache-2.0.

**Important limitation:** Active browser content is exposed to your agent. Review documented usage telemetry and authenticated-session risks before connecting.

**Observed upstream revision:** [`0b37364d`](https://github.com/ChromeDevTools/chrome-devtools-mcp/tree/0b37364dc0a88a804c6d73d3335e776adc7f33c4).

### [Firecrawl](https://github.com/firecrawl/firecrawl)

**Classification:** Web-data API/software; official MCP, CLI, and skills are separate integrations.

**Use:** Search, scrape, crawl, parse and extract website content for research or knowledge bases.

**Existing overlap:** Native web research and browser tools; AnyDoc already cataloged as a separate Firecrawl-adjacent document converter.

**Dependencies/cost:** Hosted service generally needs API key and usage-based credits; core self-hosted source AGPL-3.0 with infrastructure requirements.

**Important limitation:** Do not treat Firecrawl as a browser-testing framework or assume unlimited free scraping. Verify privacy and site terms.

**Observed upstream revision:** [`bf6739d9`](https://github.com/firecrawl/firecrawl/tree/bf6739d95caccfd6518d2bf1b5d07fad2b6bd34c).

## Agent monitoring and memory

### [whatsmyagentdoing (myoffice)](https://github.com/Charonyuu/whatsmyagentdoing)

**Classification:** Agent skill plus local monitoring web dashboard.

**Use:** See Claude Code/Codex session activity and user-attention needs across local terminals.

**Existing overlap:** Paperclip orchestrates tasks and schedules; myoffice observes existing local sessions.

**Dependencies/cost:** Node.js 18+; MIT; reads local session logs.

**Important limitation:** Monitoring is not task assignment; keep local dashboard private. Check your actual session paths.

**Observed upstream revision:** [`c69bf2bc`](https://github.com/Charonyuu/whatsmyagentdoing/tree/c69bf2bc98cf96a63d146070e9bbc83b507bf0bf).

### [Claude-Mem](https://github.com/thedotmack/claude-mem)

**Classification:** Persistent agent-memory plugin plus runtime/worker.

**Use:** Retrieve context from prior Claude Code or Codex sessions.

**Existing overlap:** Explicit versioned repo knowledge and Paperclip task history are different from auto-collected session memory.

**Dependencies/cost:** Additional worker/storage/model usage; Apache-2.0; anonymous analytics enabled by default with opt-out documented.

**Important limitation:** Potential access to sensitive code/session content; keep prior unresolved adoption blocker. Cloud sync opt-in per README; no deployment reviewed.

**Observed upstream revision:** [`2d8c08c1`](https://github.com/thedotmack/claude-mem/tree/2d8c08c182af68b20bb7528c7bf989aa871a7d2f).

## Design and current-awareness skills

### [Hallmark](https://github.com/Nutlope/hallmark)

**Classification:** Design skill.

**Use:** Distinct design themes, redesign and audit modes, browser sloplint/visual checks.

**Existing overlap:** Taste, UI/UX Pro Max, Emil, juliobsz; select one primary design director.

**Dependencies/cost:** Node.js 18+; Chrome and Puppeteer Core for render checks; MIT.

**Important limitation:** Use audit-only as a trial before adopting its opinionated redesign approach.

**Observed upstream revision:** [`407fa689`](https://github.com/Nutlope/hallmark/tree/407fa689f4a276f2fd389208d271d0fef08f5058).

### [Last30Days](https://github.com/mvanhorn/last30days-skill)

**Classification:** Research skill with optional external providers.

**Use:** Summarize recent Reddit/X/YouTube and other community discussions around AI trends.

**Existing overlap:** Native web search and weekly GitHub/model rankings; previous skill review was partial.

**Dependencies/cost:** MIT; some public sources work without a key, others need API/login/CLI setups.

**Important limitation:** Popular posts are not verified facts or objective rankings; require dated primary-source checks.

**Observed upstream revision:** [`71dc2a15`](https://github.com/mvanhorn/last30days-skill/tree/71dc2a1529f23dfe7b0d0e3b3e11d4a7e8afd428).

## Video evidence

### [Watch / claude-video](https://github.com/bradautomates/claude-video)

**Classification:** Video-analysis skill — ALREADY CATALOGED.

**Use:** Turn video URL or local file into timestamps, frames and captions/transcript.

**Existing overlap:** Prior library entry under [Document and video tools](../tools/documents-and-video.md); no duplicate entry or installation.

**Dependencies/cost:** MIT; local frame/caption extraction; optional WhisperX/Groq/OpenAI/Gemini resources.

**Important limitation:** Source access and engine selection determine what was actually seen or heard; avoid unintended cloud uploads.

**Observed upstream revision:** [`03ceb42f`](https://github.com/bradautomates/claude-video/tree/03ceb42f7fa2c4439aca01752118044baabffb8f).

## Codebase architecture

### [Graphify](https://github.com/Graphify-Labs/graphify)

**Classification:** Local CLI code graph + agent skill; separate hosted cloud.

**Use:** Graph/code-path queries and call-flow visualizations in Java/Spring and other codebases.

**Existing overlap:** repo-flow-atlas and direct source tracing; use graph for discovery, verify concrete paths against source.

**Dependencies/cost:** Python/uv or pipx; Apache-2.0. Tree-sitter Java parser dependency confirmed; optional semantic model/cloud may charge.

**Important limitation:** Spring proxies/reflection and asynchronous message routing can evade static extraction. EXTRACTED edges differ from INFERRED ones; published token savings unverified.

**Observed upstream revision:** [`16218bfc`](https://github.com/Graphify-Labs/graphify/tree/16218bfc80d4ca2799734d045039f7ed1a5fa9fb).

## Suggested pilot order

1. **Website quality:** Playwright CLI or existing browser tools, plus Chrome DevTools for a real debugging gap. Optionally trial Hallmark's audit mode without adding another default design director.
2. **Java architecture:** Evaluate Graphify on a single representative flow, then compare extracted/inferred edges to source-level findings in ibizmerch/idcommservice.
3. **AI trend research:** Trial Last30Days alongside existing weekly ranking workflow, with primary-source verification.
4. **Only when justified:** Firecrawl for high-volume web extraction, myoffice for parallel local agents, Claude-Mem for a verified persistent-memory gap. Watch is already saved; use that record when video work arises.

**Policy:** Mentions are research-library leads only, not consent to run installers, register hooks, connect external accounts, send code to hosted models, or change the approved advisor baseline. New findings still require user review.
