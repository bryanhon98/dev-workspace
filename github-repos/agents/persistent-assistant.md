# Separate assistant runtimes

[Catalog](../README.md) · [Full evidence register](../reviews.json)

Research options, not installation approvals. Use only the selected capability when needed; no blanket activation is recommended.

## [Hermes Agent](https://github.com/NousResearch/hermes-agent)

Optional separate assistant for persistent messaging and scheduled workflows, when those needs extend beyond your Codex sessions.

Not part of default Codex setup. Its opt-in Codex runtime lacks some native Hermes memory/delegation callbacks, and cron on that runtime is documented as not specifically tested. A second runtime adds its own state, permissions and upkeep.

**Cost and license:** MIT. Model inference, optional tool providers, hosting and messaging infrastructure have separate costs; advertised cheap VPS examples are not an all-inclusive price.

[Reviewed snapshot](https://github.com/NousResearch/hermes-agent/tree/8f817911723e3ec13e7f47fc022fdcc9e2149354) · [Source](https://github.com/NousResearch/hermes-agent/blob/8f817911723e3ec13e7f47fc022fdcc9e2149354/README.md) · [Additional evidence](https://github.com/NousResearch/hermes-agent/issues/41385)
