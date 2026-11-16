# SkillSpector research scans and failure triage

This is a **diagnosis and review procedure**, not an alternate installer. `scripts/secure_operations.py`, `scripts/native_approval_mcp.py` and global security policy remain authoritative for installation. This document does not change any active security gate.

## Two different scan purposes

**Research preview:** Use the research-only wrapper for a public GitHub repository:

```sh
python scripts/secure_operations.py research --url https://github.com/OWNER/REPOSITORY
```

The wrapper uses SkillSpector's URL input with static analysis, full-coverage options and a ten-minute process timeout. It does not install or release a checkout. Every result has `install_eligible: false` and `verified_revision: null`: this URL preview cannot establish the exact checked commit or local file manifest. A successful preview exits zero; review-required, incomplete, malformed and failed previews exit one. A MEDIUM/CAUTION preview reports `review-required` without requesting or granting installation approval.

SkillSpector retrieves temporary source bytes internally. "No manual clone" does **not** mean no download. The wrapper accepts only plain HTTPS GitHub repository URLs, without credentials, queries or tree paths. The installed NVIDIA version is v2.12.0 from `ea5aeef6b05c593959ad2125c09a528ffa5c55c9`. Its `InputHandler._github_tree_target` resolves advertised branches/tags, not arbitrary commit-SHA tree URLs; do not describe a branch/tag URL as an exact install pin. The current upstream input handler was also inspected at `3c2c5d7a1ee148d228398070b91d3beaf0d73b11` on 2026-11-12. No scanner update was performed.

Use `--retry` only after identifying a plausible transient execution failure. It permits one additional attempt, with the same options; parsed reports, findings and incomplete coverage are never retried away. The summary preserves each attempt, exit code, error category, stderr byte count and digest. For diagnosis that needs the original error, `--private-diagnostics` includes control-character-stripped error/stdout excerpts capped at 1,000 characters each. These excerpts are explicitly private and unsanitized; inspect and redact them before sharing. Report findings and completeness details can also contain source text or paths, even without this flag.

For an already available local payload, create a read-only inventory:

```sh
python scripts/secure_operations.py inspect --source PATH_TO_STAGED_PAYLOAD
```

This command hashes files without importing or executing source code. It skips Git metadata and stops above 10,000 entries or 100 MiB of file data. It does not clone, install, modify the payload, prove scanner coverage or certify behavior. Read the relevant source files separately to investigate imports, process/network access and parser errors. Keep private paths and source findings out of published reports.

**Installation review:** Stage the exact selected skill files outside active skill directories. Run the complete local scan, compare the scanner's component paths against the expected file manifest, and verify the same bytes during installation. Do not substitute a prior URL preview for this verification.

The current policy is docs/INSTALLATION-REVIEW.md: structured HIGH/CRITICAL, DO_NOT_INSTALL and incomplete results are reviewable. Unusable, suppressed or non-static output remains a technical failure. Complete independent scans before deciding; only fully assessed LOW/SAFE without higher findings or gaps qualifies for automatic installation.

## Triage when a scan fails

1. Record the scanner version, target type, pinned revision, command/options, exit code, stderr summary, completeness percentage, skipped paths, suppression state, and individual findings. Keep raw reports in a trusted local directory; do not expose private paths, tokens or source content in shared logs.
2. Distinguish **scan error**, **incomplete coverage**, **individual finding**, **suspected false positive**, and **verified malicious behavior**. The aggregate risk score alone does not override individual HIGH/CRITICAL findings.
3. If the error is environmental, validate the scanner against a benign sample and investigate the error without executing the target. Attempt only bounded, justified retries; do not retry indefinitely or disable completeness checks just to obtain green output.
4. If a parser cannot inspect a supported file, use read-only source inspection to narrow the unknowns: inventory files, inspect relevant imports, network/process operations, dependency and update scripts. Describe exactly which files and behaviors have been inspected and which have not.
5. Compare a suspected false positive with the original source context. A benign sentence in a Markdown instruction is not equivalent to a shell command. Record the evidence and report a reproducible scanner bug upstream when appropriate.
6. Produce a review summary with **coverage, remaining unknowns, real findings, false-positive hypotheses, install eligibility, and recommended next step**.

## Approval and exception boundaries

- **LOW, full scan:** existing safe-install policy and exact-file revalidation apply.
- **MEDIUM, full scan:** existing explicit human permission and exact-file revalidation apply.
- **HIGH, full scan:** investigate, show all findings and false-positive evidence, recommend approve/reject/defer, and ask a plain question. Do not silently downgrade to LOW automation. Accepted concerns still require exact-file revalidation and applicable host permission.
- **CRITICAL or confirmed malicious code:** finish independent scans, explain the evidence and consequences, and recommend rejection when behavior is harmful. Severity alone is not an automatic veto; applicable host restrictions remain independent.
- **Failed/incomplete scan:** manual read-only review may improve understanding, but does not turn missing coverage into a successful complete scan.

If exact file identity cannot be verified or output is unusable, stop the affected installation. Structured missing coverage is disclosed for review; consent never proves the payload safe.

## Data and limits

`--no-llm` skips optional content submission to an AI analysis provider. NVIDIA's documentation states that the SC4 supply-chain check still sends dependency names and versions to OSV.dev when reachable. SkillSpector never executes the scanned skill. It is static analysis, **not** a runtime sandbox, malware-free guarantee or general repository audit.

Source: [NVIDIA SkillSpector README](https://github.com/NVIDIA/SkillSpector#basic-usage), including its input, completeness and trust-model descriptions.

Verified source: [pinned input handler](https://github.com/NVIDIA/skillspector/blob/ea5aeef6b05c593959ad2125c09a528ffa5c55c9/src/skillspector/input_handler.py) and [current checked input handler](https://github.com/NVIDIA/skillspector/blob/3c2c5d7a1ee148d228398070b91d3beaf0d73b11/src/skillspector/input_handler.py). HIGH/CRITICAL installation diagnostics show triggering findings first, with source file and line from the scanner's `location` object; summaries show at most 20 findings and explicitly count omissions. They do not downgrade or suppress any finding.

## Confirmed hook false positives and current limit

Historical observation before the combined fix: the hook searched complete patch content for active-directory paths and shell text for the security-server module name. A documentation-only test patch to a file under `tests/` was rejected twice, including in an isolated worktree, with `Direct patching of active skill/plugin directories is blocked`. The path appeared only in a regression fixture. Literal reads of the server source were also classified as invocation. These were hook-classification problems, not SkillSpector findings.

The combined implementation preserves the manually corrected shell-maintenance guard from main and imports destination-aware patch parsing from the local PR14 checkout. Patch prose is not treated as an edit destination. Malformed or ambiguous patches remain denied. Direct execution and active-directory mutation guards remain. Compound shell inspection false positives are a known limitation; this change does not claim a general shell parser or verified live UI enforcement.
