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
