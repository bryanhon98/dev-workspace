# Library contract

For substantial collections, maintain readable entries, structured entity records and a media ledger. Reuse an existing user format if it preserves these relationships. Unknown values stay explicitly unknown.

## Entity record

For a pure website showcase, keep its verified website URL. Reliable primary sources that explicitly list tools for that exact project can also supply tool records, labelled researched project credits and linked to the source. Record the documented project-tool relationship separately from each tool's general purpose; exact implementation roles remain unknown unless established. Unrelated creator-profile links and plausible stacks are omitted. When only the URL is verified, keep just the link; when nothing useful is reliably identifiable, record a skipped outcome.

For substantive tool/resource/technique explanations, give each distinct entity a stable local ID independent of its display name. Capture:

- **Identity:** name, kind, aliases, observed identifiers, official URL/repository/page when verified, match confidence per source (confirmed/high-confidence-inferred/unresolved), supporting visual/spoken clues, contradictions and alternative candidates considered. Track primary-source verification separately (verified/pending/conflicting, URL/date). High-confidence inferred matches may appear in the library with a clear label and rationale even without a creator-supplied link. Lower-confidence candidates stay private. A confirmed match or verified tool website does not verify every product claim.
- **Explanation:** purpose, problem solved, mechanism, concrete example, when useful, limitations. Explain unfamiliar terms simply.
- **Use:** demonstrated steps, required software/client, authentication, pricing/access and version when established. Label externally researched steps as researched rather than shown in the reel. Extraction does not imply installation or safety certification.
- **Creator assessments:** creator, source ID, timestamp/locator, positive/negative/mixed stance, specific opinion and evidence status. An absence of criticism is not a positive review.
- **Claims:** statement, source IDs, modality/locator, origin (creator assertion/direct observation/primary-source verification), verification URL/date, status (supported/unverified/conflicting/outdated). Quantified gains need conditions or an explicit unknown.
- **Synthesis provenance:** contributing source IDs, clearest explanation and why it helps, unique details per source, disagreements. Cite supporting sources for factual clauses.
- **Relationships:** workflow components, fork of, renamed from, complements, alternatives; supporting evidence. Similar functionality alone does not establish identity.

A readable entry can use:

> **Name — kind — match confidence — verification status**
> **Use it for:** a specific problem.
> **How it works:** clear mechanism and simple example.
> **What creators say:** attributed benefits and caveats.
> **Practical details:** prerequisites and steps actually established.
> **Limits and uncertainty:** incomplete evidence, conflicts, costs or unknowns.
> **Links:** useful official page/repository and supporting reels with times.

For an inferred association, show: **Match: high confidence, inferred from visuals/speech; creator supplied no link.** List the distinctive matching clues and attach their timestamps or other evidence locators. Link the official source found during research. Explain uncertainty without implying that the creator explicitly named, linked, endorsed or used the tool. Keep the tool's documented capabilities separate from the inferred reel association. A later confirmed source can strengthen the entity record without rewriting the earlier reel's evidence history.

For websites introduced as useful services or explained resources, link the useful page and explain its function even without a GitHub repository. Pure showcases follow the verified-link and documented-project-credits rule above. An uncertain address stays in private research, not the user-facing library. Different tools on one domain can require separate records.

## Media ledger

Each source retains:

- Stable source ID, original URL and normalized aliases, creator, collection, export date.
- Processing state: queued, in progress, partial, reviewed, blocked; last attempt and failure cause where applicable. This state describes completion within the requested scope.
- Review scope: original media or supplied artifacts (evidence-only). Evidence-only extraction may finish within that scope while original-media coverage remains incomplete; expose all missing modalities. A reviewed evidence-only record is not a full audiovisual review.
- Coverage separately for visuals, speech/transcript and export caption, with evidence locators/local artifacts. Record watched interval, frame sampling limits and transcript provenance.
- Entity IDs contributed, unique additions, disagreements and explanation clarity notes.
- Outcome: actionable, showcase-link-only, showcase-with-documented-project-credits, skipped-no-supported-extraction, or undetermined. Record a brief skip reason such as unidentified showcase or insufficient identity evidence. Coverage and outcome are independent: a partial source may contribute a verified link, or be skipped for extraction while missing speech stays explicit.
- Identity research state and unresolved clues, distinguished from download failures.

Promotional captions are context, not substitutes for watched evidence. Screenshot-only review cannot establish that speech contains no additional useful information. A source may be reviewed yet still have an unresolved identity; show the unresolved count separately.

## Resume and update

For hundreds of sources, use one stable local library directory with a readable category index, one detail page per entity, a structured entity database, a source ledger and a checkpoint manifest. Report the absolute library location and link its index. The manifest records file locations and schema version so future sessions reuse the same layout. The readable pages are generated from the same entity records; keep both views synchronized. A new reel about an existing tool adds provenance and improves its existing explanation rather than creating another tool page. Retain per-claim evidence, distinct creator opinions and unresolved conflicts.

The source ledger covers all selected export entries, including queued and skipped items, so progress is countable and resumable. The checkpoint records processing counts, last saved source and next queued source. Raw media and transcripts are evidence assets, separate from the readable index. The library and private export remain local unless the user requests publication; skill-source backup does not include the collection data.

Load the ledger/entity index before the next batch. Match normalized media identifiers to avoid duplicate extraction. Merge only on supported identity; preserve source records, candidate histories and contradictory claims. Preserve stable IDs across renames.

When writing a persistent library, save the ledger and corresponding entity updates together after each reel or small batch. For a no-write pilot, include an inline checkpoint. Preserve files on interruption and report unfinished writes. Duplicate export entries can add collection membership without downloading again. New evidence or a requested check can justify revisiting a partial/reviewed source.

Report selected source count; reviewed/partial/blocked/queued counts within scope; separate evidence-only scope count (which may overlap those states); retained tools/resources with confirmed versus high-confidence inferred associations; showcase links; skipped outcomes; merged duplicate contributions; and the next source. Lower-confidence candidates remain private unless the user asks to inspect them. Do not hide blocked or unresolved cases in a success total.
