# Complete advisor baseline evidence

This record replaces the earlier preparation-blocked status for the selected 17-skill baseline. Historical audits remain unchanged. See `verification.json` for actual installation/discovery results and their limits.

## Sources and payloads

- Tool Advisor: saved custom 1.0.0, unchanged.
- Matt Pocock skills: `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, complete `skills/productivity/grilling` plus root LICENSE.
- Vercel skills: `7a5e920bead4b1039a6d6df5d7e1163b7b09423a`, complete `skills/find-skills` plus root LICENSE.
- Superpowers: `2ce8aa15d05bd57213e6f746f953aafb7ded7a8b`, the 13 complete skill directories selected in `advisor-baseline.json`, each with root LICENSE. Other plugin features are not baseline dependencies.
- Council of High Intelligence: `14d398f44771be1fc49488ab1b8a348ed76ca172`, Codex instructions, 18 personas and LICENSE. `council/adaptations.json` and `adaptation.patch` record portable asset lookup and the actual-worker requirement. Optional external-provider helpers are not referenced by this selected Codex payload and are not installed.

Official repository HEADs were checked during preparation and again by the installer. `advisor-bundle.json` records the precise sources and every saved file hash. Installation does not execute candidate scripts. Runtime host adaptations are explicit in `global/AGENTS.md`.

## Scan decisions

Every component has its own `scan.json` and `audit.json`. Reports came from SkillSpector 2.12.0 at pinned revision `cf5cac7ba5c756a6e0ebf52dc9763f49422f889f`, static-only with no external model analysis. Published reports replace only the research checkout's absolute location with `<research-checkout>`; findings and completeness are preserved.

Each finding decision is tied to its exact eight-field signature and explains the flagged context. Parser limitations and optional/example references are separately recorded. Some raw reports remain partial; no finding is suppressed, and no entirely uninspected file is accepted. A targeted read to classify a flagged snippet is not a full manual source/security audit.

Fresh installation scans must reproduce the approved findings and coverage profile for the exact bytes. Changes require fresh triage. Established low-risk findings warn and proceed under the user's standing policy; dangerous or unclassified findings block. Accepted documentation examples do not authorize executing their commands outside the actual task's scope.

## Rechecking a newer version

When official HEAD changes, stage the complete selected skill files and required supporting assets outside active skill directories. Scan the entire selected batch, classify changed findings or gaps, update exact hashes and evidence, then run setup again. Never reuse an old decision for changed bytes or label a raw partial report complete. The Python installer detects a newer HEAD; the assistant performs staging and triage rather than silently approving an update.

## Independent code review

A separate worker applied Superpowers' `requesting-code-review/code-reviewer.md` to the installer, setup commands, tests, manifests and audit handling. It independently ran 110 passing tests and verified preparation of all 17 roles. It found no remaining substantive blocker after the scanner count invariant and historical test fixtures were corrected. It did not claim a full upstream security audit, laptop installation, or an end-to-end council session. README accuracy and final installation evidence were checked by the coordinator separately.

## Active approval system update (2026-11-08)

These records are preserved as historical security evidence. The active
installer uses the compact version ledger at `skill-approvals.json` and
matches source/installed file contents directly. Historical scan report
fingerprint fields are no longer installation gates; past findings and
explicit review decisions are still parsed and compared for an unchanged
approved revision. New complete scans without findings auto-approve newer
revisions. Changed findings or incomplete scans require explicit review.
