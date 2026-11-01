# Import review — 2026-11-01

The three user-supplied files were copied byte-for-byte into [the dated import](imports/2026-11-01-meta/manifest.json). Original file names, byte sizes and SHA-256 hashes are recorded. The original report is stored as `FULL_REPORT.md`; `index.md` and `entities.json` preserve their original content, including broken relative links and source wording. No claim was silently corrected and no source was dropped.

The review processed all three files: all 475 report rows, all 1,083 JSON entities and every supplied source reference, plus the complete index. Repeated descriptions were grouped to read the 384 distinct `latest_insight` texts, with additional report/snippet material checked separately. This is review of supplied artifacts, not independent viewing of 475 reels, validation of every marketing claim, or source-code review of all mentioned tools.

## Reconciled coverage

- Report: 475 entries — 407 actionable, 60 showcase/link-only, 7 skipped, 1 blocked. These are the compiler's outcome labels. Its claim of 474 reviewed is not our audiovisual coverage.
- JSON: 1,083 unique entity IDs, including concepts, people, outcomes and food entries as well as tools; 384 distinct latest-insight texts shared across records.
- Supplied “Complete” index: only 181 unique entities. The rebuilt index covers all 1,083; 902 remain explicitly uncategorized rather than being assigned guessed classifications.
- 47 entities report more mentions than the supplied `sources` list contains. The JSON has source references to 463 distinct report entries; 12 report entries lack such references. They remain available in the original report and report search; the blocked item is among them. [Coverage JSON](coverage.json) lists all 12 IDs.
- The Markdown report explicitly truncates insights. JSON source snippets and many latest-insight texts also end mid-sentence. Nothing in the three files can reconstruct the missing detail faithfully.
- Original per-entity pages, raw media, captions/transcripts, `source-ledger_18.json`, `checkpoint_18.json` and processing code were not attached. The report's suggested daily-refresh command is not a provided executable. No schedule was installed.

## Meaning of this data

`primary_url` is a reel/post URL, not a verified official tool link. Mention counts are popularity within this collection, not quality evidence. The word “latest” is the export's field name and does not establish recency. Repeated claims do not constitute independent verification. Shared multi-tool summaries must not be attributed wholesale to each entity.

Descriptions cover software workflows, design, animation, video/audio production, marketing, agent orchestration, memory, model routing, backend concepts and unrelated skipped content. Identity ambiguities and comparison routes are captured in [ROUTING.md](../ROUTING.md). Old reviewed recommendations and installation blockers remain intact. No candidate has been installed, promoted to restorable, or certified by this import.

## Verification and future use

`python3 scripts/knowledge.py verify` checks archive hashes, counts, duplicate IDs, index/entity references, entity/report source references and deterministic generated views. `build` regenerates the readable index, full entity detail pages grouped alphabetically and coverage summary. `show ID` returns the complete original entity plus related report rows. Search includes historical inventory/reviews, full entity text and report rows; skipped content is retained but excluded from default discovery results.

Hash verification detects changed bytes; it cannot prove factual correctness. Before proposing a tool, follow the [advisor workflow](../ADVISOR.md): verify identity, read relevant current upstream content, compare the actual installed alternative, and record the task-specific decision and uncertainty.
