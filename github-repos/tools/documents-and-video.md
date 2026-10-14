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
