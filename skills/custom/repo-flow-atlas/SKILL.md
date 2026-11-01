---
name: repo-flow-atlas
description: Use when a user wants to understand an existing repository through a detailed function-to-function flow, execution map, interactive code walkthrough, or evidence-linked atlas, including flows spanning several repositories. Also use for improving an atlas created by this skill. Do not trigger for ordinary feature coding or a new architecture proposal.
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
metadata:
  version: "1.0.0"
---

# Repository Flow Atlas

Reconstruct the requested flow from existing source and render it with the bundled viewer. Keep its established layout and interactions; replace the repository evidence and explanations, not the design.

## Establish the scope

Use the user's repository, feature and starting point (API, topic/event, scheduled job or symbol). Infer these from context when clear; ask only for missing essentials. Default to English unless another language is requested. Read applicable repository instructions before tracing. Additional repositories need user-authorized access; unavailable producer or dependency internals stay explicit boundaries.

## Trace and explain

Read entry points, concrete calls, configuration dispatch, branches, transactions, persistence, failures/retries and outputs relevant to the requested feature. Distinguish direct calls, inherited/template hooks, configured selection, RPC, messages, asynchronous work and relationships through data. Do not turn a file inventory or syntactic call list into a claimed complete execution trace.

For every meaningful function, explain its role in plain English, inputs, concrete processing decisions, result and failure behavior. Say what the class actually does here. Preserve real arguments and enum values. Use short diagram captions and deeper inspector notes. End relationships at unknown boundaries rather than inventing the next function.

Read [the evidence contract](references/evidence-contract.md) when authoring the manifest. It defines the data shape and source/explanation requirements. The bundled [fictional manifest](tests/example-atlas.json) demonstrates it.

## Build with the fixed presentation

Use [the build script](scripts/build_atlas.py) with an authored manifest and an explicit output directory. The script reads only files named in that manifest and never runs project code. It needs Python 3.9 or later; its core has no third-party packages or credentials. Source references use repository-relative paths and explicit line ranges. Java statements are grouped automatically; for other languages supply source-verified units as described in the contract.

Preserve [the visual contract](references/visual-contract.md): sidebar, zoomable diagrams, search, clickable readable connections, explanatory inspector, short application-relative paths, and expandable dark source blocks. One logical statement keeps one first-line label with nested arguments intact. Context/logs are muted, decisions/guards amber, core operations brightest; text labels accompany colors.

Output a standalone HTML atlas, SVG pages, editable Excalidraw pages/combined board, and evidence/build summaries. Keep generated content local by default. Removing file links does not remove embedded source or internal information. Sharing or publishing requires separate explicit authorization and an appropriate content review; creating this atlas does not authorize uploads.

## Verify and deliver

Check evidence, branches and unknowns; validate JSON, SVG and Excalidraw bindings. Run the included [runtime tests](tests/test_runtime.py) when changing helpers. If a browser is available, use [the browser checker](scripts/check_browser.py), which needs Playwright and Chromium already available; do not silently install dependencies. Inspect a representative rendered explanation/code view and report checks actually run. State static-analysis limits and any missing downstream evidence. Give the local atlas link and an example invocation for the next repository.
