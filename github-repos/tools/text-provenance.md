# Text hygiene and provenance research

## guillaumemeyer/watermarks-remover

- Official repository: https://github.com/guillaumemeyer/watermarks-remover
- Observed 2026-11-15 (Asia/Kuala_Lumpur), default-branch revision `5a62be6338d2812372b1da440e55c82922f97d53`.
- Classification: application/service with packaged agent skills and Claude plugin packaging; not solely a standalone skill.
- Purpose claimed upstream: inspect and clean Unicode artifacts and file provenance metadata, with optional text rewriting. Plausible legitimate use: authorized document hygiene and provenance research with required disclosures preserved.
- Components: `remove-ai-marks` is an HTTP-service client; `clean-user-facing-text` targets reader-facing prose. The latter explicitly excludes code-only tasks and undisclosed authorship evasion and preserves code, commands, identifiers and required disclosures.
- Prerequisites: full client needs the separate local HTTP service (Python or container runtime); text-only skill is described as self-contained, with bundled Python inspection helpers. Exact selected payload dependencies and host compatibility require review before installation. Optional rewrite/media backends may have additional dependencies, model costs and licenses.
- Overlap: Humanizer and Instagram `ig-human` overlap prose cleanup; service-backed provenance inspection is a different capability. No guarantee of undetectability or human authorship is established.
- Evidence: read repository README and opening instructions of both SKILL.md files at the revision above. This was identification/cataloging, not a complete payload audit, security scan or runtime evaluation.
- Status: research-only, uninstalled, unexecuted, not security-approved. No inventory/default-baseline change. No project files processed.
- Sources: [README](https://github.com/guillaumemeyer/watermarks-remover/blob/5a62be6338d2812372b1da440e55c82922f97d53/README.md), [text skill](https://github.com/guillaumemeyer/watermarks-remover/blob/5a62be6338d2812372b1da440e55c82922f97d53/skills/clean-user-facing-text/SKILL.md), [service client skill](https://github.com/guillaumemeyer/watermarks-remover/blob/5a62be6338d2812372b1da440e55c82922f97d53/skills/remove-ai-marks/SKILL.md).

### 2026-11-15 Windows installation attempt

- Inspected the same pinned revision above. Downloaded source to an inactive staging directory; no application code, installer, hook or service was executed and no skill was activated.
- NVIDIA SkillSpector 2.12.0 static-only scans: text skill inspected all 10 bundled files but reported unresolved variable-based references; main skill reported 85.7% coverage with command-parser and reference-resolution limitations. A supplementary scan of all 10 verbatim shell examples completed at 100%, retaining MEDIUM HTTP/Docker warnings.
- The separate service scan returned CRITICAL / DO_NOT_INSTALL and 88.5% coverage (46 of 52 components fully inspected). Findings included file-to-network flows, subprocess execution and optional pinned dependency risks; limitations included parsing, obfuscated-text classification, and dependency inspection time/output bounds.
- Some findings appear consistent with documented functionality, but all high/critical findings and coverage gaps were not resolved. These results do not establish malware, nor establish absence of malware. User allowed harmless blockers to be skipped; unresolved security findings were not treated as harmless. Installation remains blocked and unverified.

### 2026-11-16 isolated scanner compatibility test

- Tested official NVIDIA SkillSpector source revision `c81615007d40e86051a302a3cf897f8a05264928` in a separate workspace tool directory; the active scanner was not replaced.
- Rescanned the unchanged `remove-ai-marks` skill through the shared static-only scan implementation. Coverage remained 85.7%, with the same command-boundary parser limit and missing-reference gaps. Findings remained LOW aggregate / CAUTION with MEDIUM individual warnings.
- An upstream upgrade alone did not fix the blocker. Missing references mix illustrative filenames, response-field names, runtime HTTP resources and actual service files outside the skill bundle; blanket suppression is not a valid fix. No scanner patch, clean-scan claim, approval ID or application installation resulted from this experiment.
