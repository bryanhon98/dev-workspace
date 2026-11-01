# Fixed atlas presentation

Reuse the bundled viewer and graphics helpers. The user wants repeatable presentation, rather than a fresh site design for each repository.

- Dark navy application header; white left navigation; pale blue-gray diagram workspace.
- Sidebar pages in authored order, followed by routing tables, function index and scope/evidence.
- Toolbar: fit-to-width, zoom controls, per-page SVG/Excalidraw downloads and function/business-term search.
- Rectangular nodes on the established grid: 440 by 200 units, 560 horizontal and 320 vertical pitch. Use the bundled orthogonal routing and staggered ports. Avoid diamonds, duplicate ids, floating arrows and overflowing labels.
- Selected node outlined visibly. Click or Enter opens the explanatory inspector; connection names are clickable navigation, not abstract node ids.
- Inspector: readable class/method heading, “What it does,” “What it receives,” signature(s), “Inside this method,” result, application-relative source location, “Where it comes from” and “What happens next,” then code.
- Keep the diagram caption short and the inspector explanation substantive. Do not fill the inspector with generic repetitions of a method name.
- Expanded source blocks use background `#101b2b`. Context/logs use readable muted gray `#91a2ba`; preparation uses `#bdcde0`; conditions/guards use amber `#ffda8a`; core operations use brightest text `#f1f7ff`. Relevant enum values use restrained cyan `#95e5f3`. Every row has a textual category label as well as color.
- Show one first-line number per logical source unit. Preserve complete arguments, nested expressions and enum values. Display the actual method signature so overloaded `execute` calls are distinguishable.
- The inspector fits desktop and narrow screens, has a sticky close control, and wraps long class names, code and paths. Preserve the supplied responsive rules.
- The HTML is self-contained: no CDN, analytics, remote font, external API or account login is required to view it. Browser verification is optional tooling, not a runtime website dependency.

Excalidraw shapes bind to separate text elements; arrows bind to source/target nodes and use explicit orthogonal points. SVG and Excalidraw share the same evidence/geometry. Source-code blocks belong in the HTML reader, not the overview diagram.

Use the browser checker on generated output when Playwright/Chromium are available, then visually inspect the explanation, relationship and code sections. Test source grouping with multiline calls, predicates, enum arguments, comments, strings and callback blocks. Report unavailable checks instead of calling them passed.
