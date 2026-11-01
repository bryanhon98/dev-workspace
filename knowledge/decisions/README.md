# Decision records

Store one JSON object per meaningful task comparison or outcome, named `YYYY-MM-DD-<task>.json`. This directory starts without tool verdicts: the reel import does not prove a better setup. Search it before making new recommendations (`rg -n -i 'topic' knowledge/decisions`); the knowledge search command also includes JSON records here.

Required record fields:

- `id`, `recorded_at` (UTC ISO 8601), `task`, `constraints`, `device_alias` (or `unknown`).
- `candidates`: each has identity, official source URL, skill path, observed/pinned revision, upstream revision, checked time, review depth, fit, overlap, prerequisites, costs and uncertainties. Use `null` for unknowns, never invented versions.
- `decision`: selected roles, keep/add/trial/replace/retire/defer decisions and reasons; explicitly distinguish proposed changes from completed actions.
- `evidence`: source URLs/local audit refs, assertions supported or contradicted, test inputs/criteria/results and unperformed checks. Avoid private payloads or absolute home paths.
- `feedback`: user-reported results, direct observations and inferred preferences labelled separately. Empty if no feedback yet.
- `revisit_when`: concrete triggers (changed task, changed upstream revision, regression, cost change, missing capability).
- `supersedes`: prior record IDs, if any; retain their original files.

For recommendations spanning several capabilities, also include `coverage`: the necessary jobs, candidates actually examined for each, chosen role owner or an explicit gap, and reasons for deferring credible alternatives. Include discovery queries/source scope and unverified areas. This records what was considered; it does not certify exhaustive discovery or turn every considered skill into a recommendation.

A research decision does not change installation status. Record verified installs separately in `installations/` and update inventory/audits under the global rules. Do not record a recommendation as an accepted preference or a successful install.
