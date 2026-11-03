# Proportional workflow: preliminary behavior evaluation

## Change and ownership

`knowledge/BUILD-FLOW.md` owns direct/focused/full routing, optional requirements documents, confirmation reuse, tracking and review coordination. Global rules own installation/security/publication; ADVISOR.md owns discovery evidence. Entry points link to those owners. Original skill payloads remain unchanged. Explicit host overrides resolve the advisor skill's broader universal-stage wording; this reduces competing policy copies, but does not claim that all repeated explanatory text has been eliminated.

## Method

Two separate native workers received the same six synthetic requests in `cases.json`. The before worker received the workflow, global rules and advisor SKILL from commit `0f6adaf`. The after worker received their updated versions (the skill was unchanged), and also reported reading repository AGENTS.md. Neither worker was given the other's results or the scoring criteria. Each produced a first response and next-action trace; neither performed the requested project operations. `before.json` and `after.json` preserve those outputs.

The coordinator compared the traces against these task requirements. A separate reviewer checked the policy changes for consistency and reported no blocking findings; the comparison below is coordinator assessment:

| Case | Expected behavior | Before | After |
|---|---|---|---|
| Typo | Exact edit and focused check; no interview, discovery or ledger | Met | Met |
| Clear feature | Reuse explicit approval and existing capabilities; no broad rediscovery | Met, with routing/ledger ambiguity | Met, explicit focused route |
| Resume | Inspect artifacts and continue under unchanged approval | Met, ambiguous ledger requirement | Met, existing tracker retained |
| Complex 3D idea | Clarify missing scope, research relevant capabilities, propose combination; no prerequisite PRD | Met, document thresholds unspecified | Met, optional PRD and justified technical proposal explicit |
| Conflicting documents | Resolve offline/privacy versus hosted API before dependent execution | Met | Met, independent work may continue |
| Small destructive operation | Inspect recovery safeguards and obtain concrete destructive-action authorization | Met using surrounding authorization rules | Met with explicit risk escalation |

No regression was observed in these six stated routing decisions. The baseline already behaved reasonably; this trial does not demonstrate a higher pass rate, faster execution or better project output. The observed improvement is clearer routing/document/tracking decisions and fewer policy ambiguities.

## Verification and limits

- Existing repository suite: 110 tests passed. These are implementation tests, not conversational performance tests.
- Updated managed rules installed and matched in the existing isolated Linux test profile using `--install-rules` and `--check`. No user's laptop was modified.
- Original skill payloads, hashes and installer code were unchanged; no new skill was created or installed for this change.
- One worker per condition, six synthetic cases, shared host constraints and a small context difference are insufficient for statistical claims. The workers described actions rather than executing tasks. No wall-clock, token-cost, real artifact quality or long-running compliance comparison was measured.
- Minor wording clarifications during review made material-change confirmation and routing precedence more explicit. Final policy was independently checked for consistency; the traces are preliminary evidence, not an exhaustive certification of every final sentence.

## Repeatable follow-up

Use the same cases and a fixed host/model configuration with fresh workers and equal context. Add unseen cases and multiple repetitions. For an actual performance comparison, provide disposable projects and run bounded tasks end to end, recording questions, unnecessary research, elapsed time, tool use, acceptance results and output quality. Reject a reduction in overhead if it drops necessary requirements or safeguards. Retain failures as evidence and adjust the authoritative policy, not a competing copy.
