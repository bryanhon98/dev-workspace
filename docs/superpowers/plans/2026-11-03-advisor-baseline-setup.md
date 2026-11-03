# Advisor baseline setup implementation plan

Goal: “setup tool-advisor” selects all approved baseline roles up front, never reporting a three-skill partial installation as the full workflow.

Architecture: keep the existing hash-pinned installer and its scanner gates. Declare required baseline roles separately from payload readiness so missing or blocked Superpowers/council preparation is visible before activation. Reuse original upstream skills and existing approved exceptions only at matching hashes. Project-specific specialists remain conditional.

User scope: existing core, Superpowers software execution/review/verification capabilities, and Council of High Intelligence. This is the user's explicit correction to the previous core-only setup behavior. Do not infer approval of new scan findings or paid providers.

- [x] Inspect source and scan staged baseline candidates; record exact preparation gaps.
- [x] Add required-role validation and a read-only setup plan; test missing roles and incomplete preparation cannot report ready.
- [x] Update setup intent, documentation and saved approval; preserve original skill payloads.
- [x] Run repository tests and verification; publish verified changes and disclose blockers.

Review focus: core-only receipts, missing required roles, invalid manifests, local modifications and scanner findings must not produce complete setup claims. No new laptop installation is inferred from cloud tests.

Outcome: setup selection, fail-closed preflight, documentation and scans completed. Full baseline payload audit/packaging/installation remain blocked and are NOT marked complete by these checkboxes.

Final review: separate worker baseline_setup_review applied upstream requesting-code-review/code-reviewer.md. Two issues reproduced RED then fixed: core-only scope expansion and hidden audit errors when roles are missing. Minor deferred: malformed unhashable component names can produce a traceback in the read-only plan; activation remains closed. No candidate findings approved.
