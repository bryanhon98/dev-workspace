# Document and video tools

[Catalog](../README.md) · [Full evidence register](../reviews.json)

Research options, not installation approvals. Use only the selected capability when needed; no blanket activation is recommended.

## [AnyDoc](https://github.com/firecrawl/anydoc)

Convert local office documents, spreadsheets, presentations, ebooks and text PDFs to Markdown for reading and analysis.

A concrete local capability, not another prompt. Local conversion has no OCR; scanned or mixed PDFs may need a different path. Optional hosted OCR sends the document outside the device. Markdown does not preserve full layout or recalculate a workbook.

**Cost and license:** MIT; local conversion needs no paid API. Optional Firecrawl Parse OCR has service limits and potentially paid usage; API key raises limits.

[Reviewed snapshot](https://github.com/firecrawl/anydoc/tree/261fc257d17c3eab0f673be31c408fd9fdc2171a) · [Source](https://github.com/firecrawl/anydoc/blob/261fc257d17c3eab0f673be31c408fd9fdc2171a/skills/convert-documents-to-markdown/SKILL.md) · [Additional evidence](https://github.com/firecrawl/anydoc/issues/144)

## [Watch (claude-video)](https://github.com/bradautomates/claude-video)

Produce timestamped video frames and transcripts from a URL or local video so analysis has inspectable evidence.

Actual Codex packaging exists. Choose the engine explicitly: auto can select Gemini and upload video when a key is present. Captionless footage needs speech transcription. Historical deletion/FFmpeg reports have addressing code changes but were not runtime-tested here.

**Cost and license:** MIT. Captions/local frame extraction have no API fee; local WhisperX needs model downloads, disk/RAM. Groq/OpenAI transcription and Gemini usage may incur provider costs.

[Reviewed snapshot](https://github.com/bradautomates/claude-video/tree/03ceb42f7fa2c4439aca01752118044baabffb8f) · [Source](https://github.com/bradautomates/claude-video/blob/03ceb42f7fa2c4439aca01752118044baabffb8f/README.md) · [Additional evidence](https://github.com/bradautomates/claude-video/issues/80)

## [rea-video — JuneYaooo](https://github.com/JuneYaooo/rea-video)

**Library status (2026-11-15):** User-saved **optional video-forensics CLI + Agent Skill**; not installed, executed, SkillSpector-scanned or added to Tool Advisor's three-core baseline. Verified official upstream revision `751596967f58b8949124d291e59bdc40fc04486e` (2026-11-14).

**Distinct capability:** Reverse-engineer an existing video shot by shot to help recreate the *production approach*: cut timing, camera position/movement, lighting, live-action versus AI/3D/code-render indicators, overlays/subtitles, audio layers, asset checklist and possible reconstruction approaches. Generates human-readable reports (HTML/PDF) plus hierarchical `VIDEO.md` for agent use; optional vision-model review and manual/agent verification correct uncertain classification. It **does not generate the new video by itself**. Actual AI shot generation through optional `capsule-cinema` or other tools may cost money.

**Overlap / choose condition:** Saved [Watch / claude-video](documents-and-video.md#watch-claude-video) extracts visual evidence, timestamps and transcripts from footage. rea-video adds more **production-method diagnosis and shot-by-shot recreation plans**, so choose it when the aim is *how to recreate* a reference, not merely *what happened*. Also complements saved [WanGP](local-media-generation.md#wangp-formerly-wan2gp--deepbeepmeep), a **video generation runtime** (not a forensic analyst); avoid invoking both by default if no generation is requested.

**Dependencies / privacy / cost:** Python >=3.10, FFmpeg, Python packages including OpenCV/ONNX Runtime, and optional local OCR/ASR packages; models may download on first use. The documented installation helper can link the skill into Claude/Codex agent folders and modify Python packages; **inspect, scan and approve before execution**. Tools-only mode is advertised as offline and free. Optional hosted vision models (Gemini, Doubao or compatible multimodal endpoint) send clips/frames to provider APIs and may charge; require explicit consent for private/reference footage. Reconstruction through separate tools may invoke paid services. Classification of AI versus live footage is **inference**, affected by platform recompression and vision-model error; don't treat confidence estimates or author-reported evaluation rates as proof. Main CLI and skill are not a substitute for copyright and asset-use review.

**Licensing and status:** Project [Apache-2.0 licence](https://github.com/JuneYaooo/rea-video/blob/751596967f58b8949124d291e59bdc40fc04486e/LICENSE); separately downloaded models/assets may have separate conditions. Skill is documented for Claude Code and Codex but **not automatically connected** merely by saving this link.

**Evidence:** [README and architecture](https://github.com/JuneYaooo/rea-video/blob/751596967f58b8949124d291e59bdc40fc04486e/README.md) · [Agent Skill](https://github.com/JuneYaooo/rea-video/blob/751596967f58b8949124d291e59bdc40fc04486e/skills/rea-video/SKILL.md) · [installation/VLM guide](https://github.com/JuneYaooo/rea-video/blob/751596967f58b8949124d291e59bdc40fc04486e/skills/rea-video/references/setup.md). Source read, not run or benchmarked.

