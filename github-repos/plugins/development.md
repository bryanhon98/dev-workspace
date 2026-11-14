# Development plugins

[Catalog](../README.md) · [Full evidence register](../reviews.json)

Research options, not installation approvals. Use only the selected capability when needed; no blanket activation is recommended.

## [Claudex Loop](https://github.com/chaseai-yt/claudex-loop)

Use selectively when a consequential plan or implementation benefits from another provider reviewing it. Real Python coordination binds approvals to the reviewed plan.

Full loop needs authenticated Claude and Codex CLIs plus Python; both consume quota. Keep native Codex review as the ordinary path. Codex filesystem read-only mode does not remove write-capable MCP tools, so review tool access separately before adoption.

**Cost and license:** MIT; no additional Python runtime packages or separate API key required by the adapter. Both CLI accounts consume their own quota; repeated review rounds increase time and usage.

[Reviewed snapshot](https://github.com/chaseai-yt/claudex-loop/tree/8cf5e2c1771c5151d90c12642391d0ba8fa71b0e) · [Source](https://github.com/chaseai-yt/claudex-loop/blob/8cf5e2c1771c5151d90c12642391d0ba8fa71b0e/README.md) · [Additional evidence](https://github.com/chaseai-yt/claudex-loop/issues/28)

## [Elephant-Goldfish Model (EGM) — google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model)

**Status:** Optional research/trial candidate, **not installed, scanned, approved for activation, or part of the current three-skill core baseline** by this record. Checked 2026-11-09 at [revision `5382b17619be`](https://github.com/google/elephant-goldfish-model/tree/5382b17619be07811a14b2146c7672620b34a791) (main). Apache-2.0; repository says it is **not an officially supported Google product**.

**Role:** Fresh-context independent review of a written software design before implementation. The context-holding Elephant/author creates the specification; Goldfish subagents independently critique it without parent conversation history. Main Tool Advisor remains the overall coordinator and PD/Architect remain design owners.

**Selected subskills:** [`egm-review`](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/skills/egm-review/SKILL.md) for five-stage specification review; [`egm-resolve`](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/skills/egm-resolve/SKILL.md) for author-approved finding resolution; optionally [`egm-drift-report`](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/skills/egm-drift-report/SKILL.md) for design/code drift and [`egm-review-loop`](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/skills/egm-review-loop/SKILL.md) for targeted document reviews. `egm-brainstorm`, `egm-draft` and `egm-bootstrap` are available but not default choices because existing Grilling/Superpowers methods cover requirements and planning.

**Trigger / non-trigger:** Consider for major architecture, cross-service contracts, payments, reliability or security-sensitive designs with a real draft. Skip for minor changes, ordinary well-scoped features and tasks without a design artifact. EGM critiques specifications; it does not replace code review, executable tests, QA or security analysis. Council is a **separate conditional option** for consequential unresolved decisions, not a mandatory simultaneous review.

**Dependencies, limitations and costs:** The [host guide](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/docs/harnesses.md) documents Codex and Claude Code plugin installations and end-to-end fixtures. Reviews require actual fresh-context native subagents and the complete plugin's skill/persona files; if unavailable, EGM stops. Fresh conversations can still inherit user/project instruction files; EGM reports a Codex `AGENTS.md` injection gap in its isolation checks. The plugin can generate review artifacts and approved document edits. Tool/model usage depends on host and reviewer count; no separate vendor subscription is asserted by this catalog. A live trial, exact package scan, target-device compatibility and permission scope remain **unverified**.

[Official README](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/README.md) · [Testing evidence and limitations](https://github.com/google/elephant-goldfish-model/blob/5382b17619be07811a14b2146c7672620b34a791/TESTING.md) · [Selection policy](../../knowledge/BUILD-FLOW.md#conditional-elephant-goldfish-egm-design-review)
