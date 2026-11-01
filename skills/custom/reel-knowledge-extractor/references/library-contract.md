# Library contract

For substantial collections, maintain readable entries, structured entity records and a media ledger. Reuse an existing user format if it preserves these relationships. Unknown values stay explicitly unknown.

## Entity record

For a pure website showcase, the user-facing entry is only its verified website URL. A private record may retain source ID, verification evidence and the showcase-only classification; the explanation template below does not apply. Do not populate stack/tool records from case studies or add profile-link leads to enrich a showcase. If its URL cannot be reliably identified, omit it from the library and record a skipped outcome in the ledger.

For substantive tool/resource/technique explanations, give each distinct entity a stable local ID independent of its display name. Capture:

- **Identity:** name, kind, aliases, observed identifiers, official URL/repository/page when verified, match confidence (confirmed/likely/unresolved), reasons, and separate primary-source verification (verified/pending/conflicting, URL/date). A confirmed match to a visible coordinate does not verify product claims or official ownership. Keep plausible candidates with evidence for/against them. Canonical identity may remain unknown.
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

For websites introduced as useful services or explained resources, link the useful page and explain its function even without a GitHub repository. Pure showcases follow the link-only exception above. An uncertain address stays in private research, not the user-facing library. Different tools on one domain can require separate records.

## Media ledger

Each source retains:

- Stable source ID, original URL and normalized aliases, creator, collection, export date.
- Processing state: queued, in progress, partial, reviewed, blocked; last attempt and failure cause where applicable. This state describes completion within the requested scope.
- Review scope: original media or supplied artifacts (evidence-only). Evidence-only extraction may finish within that scope while original-media coverage remains incomplete; expose all missing modalities. A reviewed evidence-only record is not a full audiovisual review.
- Coverage separately for visuals, speech/transcript and export caption, with evidence locators/local artifacts. Record watched interval, frame sampling limits and transcript provenance.
- Entity IDs contributed, unique additions, disagreements and explanation clarity notes.
- Outcome: actionable, showcase-link-only, skipped-no-supported-extraction, or undetermined. Record a brief skip reason such as unidentified showcase or insufficient identity evidence. Coverage and outcome are independent: a partial source may contribute a verified link, or be skipped for extraction while missing speech stays explicit.
- Identity research state and unresolved clues, distinguished from download failures.

Promotional captions are context, not substitutes for watched evidence. Screenshot-only review cannot establish that speech contains no additional useful information. A source may be reviewed yet still have an unresolved identity; show the unresolved count separately.

## Resume and update

Load the ledger/entity index before the next batch. Match normalized media identifiers to avoid duplicate extraction. Merge only on supported identity; preserve source records, candidate histories and contradictory claims. Preserve stable IDs across renames.

When writing a persistent library, save the ledger and corresponding entity updates together after each reel or small batch. For a no-write pilot, include an inline checkpoint. Preserve files on interruption and report unfinished writes. Duplicate export entries can add collection membership without downloading again. New evidence or a requested check can justify revisiting a partial/reviewed source.

Report selected source count; reviewed/partial/blocked/queued counts within scope; separate evidence-only scope count (which may overlap those states); retained tools/resources and showcase links; skipped outcomes; merged duplicate contributions; and the next source. Candidate identities remain in private research unless the user asks to inspect them. Do not hide blocked or unresolved cases in a success total.
