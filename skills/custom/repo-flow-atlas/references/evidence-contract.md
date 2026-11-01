# Evidence and manifest contract

The agent traces and explains source; the renderer preserves presentation. Rendering is not semantic analysis or runtime verification.

## Inputs

The manifest is a JSON object containing `title`, `summary`, `scope`, `repositories`, `functions`, `pages` and optional `routes`. Use the bundled fictional manifest as the concrete schema example. Repository roots are resolved relative to the manifest location or can be explicit absolute roots authorized by the user. Every source path within a repository is relative and must resolve inside that root; traversal and escaping symlinks are rejected. Do not include credential, environment, private-key, log or database files.

Each repository has a unique `id`, a `root`, an optional `label`, and optional `package_prefix`. The package prefix is a slash-separated Java package root to omit from displayed locations. Display locations begin with the application/repository id; actual local-file links remain separate and can be disabled with `local_source_links: false`.

Each function has a unique `id`, `repo`, relative `path`, `class` or module label, `method`, one-based `line` and `end_line`. Include the full declaration/body range. Java extraction reads the real signature and statements. A different language needs `signature` and `statements`: each unit has `line`, `end_line`, exact `code`, `kind`, `meaning` and optional nesting `depth`. Non-Java units are checked against their source range after whitespace normalization. Use AST/parser support where available for language-specific boundaries; do not apply Java grouping to another language.

Code categories are `context`, `setup`, `decision` and `action`. They are visual roles, not correctness or security judgments. Preserve validation predicates, error enums, branching conditions, meaningful call arguments and return values. Do not split nested serialization/getter calls out of a parent statement. A multiline call has one gutter label at its first physical source line; its ending line stays metadata. Branch and callback headers can be separate reader units. These lightweight grouping helpers do not resolve overloads, reflection, runtime proxies or dynamic configuration.

## Flow pages and explanation depth

A page has a safe filename `id`, `title`, `summary`, `nodes` and `edges`. Preserve page order. Usually start with an overview and then readable focused views for write, read, async/file or cross-service branches. Do not impose the example's page count on another feature.

Each node has a unique local `id`, a real class/module/table `title`, a `kind`, a short `detail`, and optional nonnegative `col`/`row` coordinates. Kinds: `method`, `decision`, `database`, `config`, `queue`, `boundary`. Function nodes reference a `function_id`; component/resource nodes can instead carry `evidence` (`repo`, `path`, `line`). Layout uses the established grid and avoids routing arrows through boxes. Keep captions short enough for the fixed-size boxes; put deeper content in the inspector.

Every node needs `reader.overview`. A function additionally needs:

- `inputs`: what arrives and which values matter in this flow.
- `steps`: a concrete ordered list of what happens, including the actual routing decisions and enums. Explain the work, not simply “executes business logic.”
- `outcome`: returned output/state change and material failure/retry behavior supported by source.

Optional `actions` records can show exact enum/value call sites (`action`, `line`, optional `code`). Keep any authored code/conditions consistent with source evidence; never replace actual source with invented executable-looking snippets. Mark illustrative pseudocode explicitly when the user provides an incomplete example instead of a repository.

Do not infer persistence because a method has a name like `save`, infer runtime authorization from an annotation, or claim an event publisher based on its topic name. In prose, explain technical concepts as needed: for example, idempotency means avoiding duplicate effects on retry. Keep established identifiers unchanged in local technical output so readers can find the source.

## Relationships

Each edge has `from`, `to`, `kind`, a concise `label`, and a required plain-English `explanation`. The inspector shows real class/method names, never just internal ids. Specify what is passed, the branch/enum/key that selects the route, and whether the next step runs immediately or later. A direct-call arrow must be supported by the caller body; helper/template chains use `control` unless intermediate methods are expanded explicitly.

Kinds: `call`, `rpc`, `dispatch`, `binding`, `control`, `data`, `message`, `async`, `unknown`. A `data` edge describes storage or returned-data relationships, not a function call. End at a marked boundary if a remote dependency or producer implementation is unavailable. Record inferred/unknown edges honestly.

Optional `routes` entries contain `router`, `key` or `condition`, `target` and any evidence note. Extract actual bindings rather than guessing a handler from its name. Do not merge configuration for several deployments into a claimed live state.

## Build and inspection

Invoke the build script with the manifest positional argument and `--output` set to the desired artifact directory. It refuses a nonempty output unless `--overwrite` is explicit. It does not delete unrelated files. The agent must inspect its proposed file reads and output location against the user's instructions before running it.

Review every meaningful branch and conditional gate before handoff. A successfully rendered page proves file/UI validity; it does not prove a complete call graph, production behavior, deployed configuration or policy compliance.

## Portability and sharing

The viewer embeds its data so HTML can open offline. Downloads require the neighboring SVG/Excalidraw files. Local-source links work only where those files exist; omitting those links does not remove the source excerpts. Generated artifacts can contain proprietary source, schemas, identifiers and business logic. Keep them separate from the reusable skill package. Do not publish the user's atlas as part of installing or backing up this skill.
