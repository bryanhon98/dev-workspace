# Remaining work for complete restoration

Implemented: self-contained global policy; global rule installer with backups, drift checks and override support; behavior tests; creator workflow; component inventory with explicit pending states.

Still needed:
- Import reviewed skill payloads and exact audit evidence from the Mac; preserve licenses and exceptions. Populate hashes before marking anything restorable.
- Inspect the scanner bootstrap and any requested third-party creator before installation.
- Export sanitized plugin/MCP setup details using supported user/account mechanisms.
- Extend the tested tooling for component restoration and record publishing once exact payload and scanner/report formats are available. Until then Codex performs those steps using the policy.
- Verify a full restore on Laptop B, including a skill inspection, global discovery and a successful GitHub installation record.

Keep this list tied to demonstrated capability. A global instruction rule is not a background synchronization service.
