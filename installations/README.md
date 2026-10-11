# Per-device component history

Each stable non-sensitive alias has one <device-alias>.jsonl file. Append one JSON object per verified install, update or removal. Required fields: timestamp (ISO 8601 with timezone), device, action, component, kind, version, scope, verification, audit_ref. For an approved exception, include exception_ref. A removal may refer to the previous version's audit. Record unavailable review coverage honestly.

Only write success after checking the actual device. Publish the record and verify its remote commit. Do not include tokens, hostnames, personal paths or company details. Rule changes are tracked in Git history; these logs are for components. No component install has been performed by this repo yet.
