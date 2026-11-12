# SkillSpector research scans and failure triage

This is a **diagnosis and review procedure**, not an alternate installer. `scripts/secure_operations.py`, `scripts/native_approval_mcp.py` and global security policy remain authoritative for installation. This document does not change any active security gate.

## Two different scan purposes

**Research preview:** SkillSpector accepts a public Git repository URL directly, for example:

```sh
skillspector scan https://github.com/OWNER/REPOSITORY --no-llm --format json
```

SkillSpector retrieves a temporary copy of the remote source to analyze it. "No manual clone" does **not** mean it can analyze code without obtaining its bytes. Confirm the checked commit or immutable tag; a scan of a moving default branch is not an installation authorization.

**Installation review:** Stage the exact selected skill files outside active skill directories. Run the complete local scan, compare the scanner's component paths against the expected file manifest, and verify the same bytes during installation. Do not substitute a prior URL preview for this verification.

The current installer rejects incomplete, suppressed, unknown, HIGH/CRITICAL and `DO_NOT_INSTALL` scans. LOW/SAFE may install under existing rules; MEDIUM requires the existing host-native human approval process. No error-handling change may silently weaken those checks.

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
- **HIGH, full scan:** investigate, show evidence and possible false positives. Do not issue a normal LOW/MEDIUM installation token or silently bypass current hard blocks. A future exception mechanism requires separately designed independent review, per-version audit records, user agreement, and regression/security tests before activation.
- **CRITICAL or confirmed malicious code:** do not use normal installation approval to override the block.
- **Failed/incomplete scan:** manual read-only review may improve understanding, but does not turn missing coverage into a successful complete scan.

If the scanner cannot verify the exact install payload, stop installation. Users can still make informed decisions about next investigative steps; they should not be told that consent proves the payload safe.

## Data and limits

`--no-llm` skips optional content submission to an AI analysis provider. NVIDIA's documentation states that the SC4 supply-chain check still sends dependency names and versions to OSV.dev when reachable. SkillSpector never executes the scanned skill. It is static analysis, **not** a runtime sandbox, malware-free guarantee or general repository audit.

Source: [NVIDIA SkillSpector README](https://github.com/NVIDIA/SkillSpector#basic-usage), including its input, completeness and trust-model descriptions.
