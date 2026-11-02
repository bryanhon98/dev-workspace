# ECC agent roster — 2026-11-02

Count: **71** top-level Markdown agent definitions in `agents/` at [b38be6a](https://github.com/affaan-m/ECC/tree/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents). Count excludes skills, commands, translations and integration copies. The recursive Git tree response was complete.

All 71 frontmatters were read. Role summaries below follow the declared descriptions; they are discovery metadata, not proof of competence. Full instruction bodies were read for planner, harness-optimizer, agent-evaluator, e2e-runner, a11y-architect, react-reviewer and performance-optimizer. Other bodies were fetched but not substantively reviewed. No agent was installed, invoked, benchmarked or security-cleared by this review.

These are role instructions and tool/model hints, not 71 separate trained models. Claude model names and tool declarations require host-specific mapping; the roster does not prove 71 agents are discoverable in Codex. Load only roles needed for a concrete job.

## Fit for this user

- For the book/shirt website: consider one planner if needed, React review if React is used, accessibility, browser journey testing, and measured performance work. Existing equivalent skills may already cover these jobs.
- For improving the advisor: harness-optimizer and agent-evaluator provide evaluation ideas. Their self-scores are not independent evidence; harness-optimizer depends on ECC audit/eval tooling and is not a ready-made tool selector.
- Chief-of-staff is a communication-triage role, not a universal skill adviser. Language/domain agents are only relevant when that stack/domain is present.
- Keep Blender/Three.js/GSAP specialists for asset authoring, WebGL and scroll choreography. Generic ECC web roles do not establish those capabilities.
- Broad rules need judgment: performance-optimizer recommends memoization more broadly than react-reviewer, which asks for measured benefit. The a11y brief's SC 2.4.11 reference conflates focus-not-obscured with focus contrast. Browser testing examples also need current API checks. A specialist label is not a correctness guarantee.

## Complete list

### Planning and architecture (5)

| Agent | Declared role | Review depth |
|---|---|---|
| [planner](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/planner.md) | Expert planning specialist for complex features and refactoring. | Full body read |
| [architect](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/architect.md) | Software architecture specialist for system design, scalability, and technical decision-making. | Metadata only |
| [code-architect](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/code-architect.md) | Designs feature architectures by analyzing existing codebase patterns and conventions, then providing implementation blueprints with concrete files, interfaces, data flow, and build order. | Metadata only |
| [code-explorer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/code-explorer.md) | Deeply analyzes existing codebase features by tracing execution paths, mapping architecture layers, and documenting dependencies to inform new development. | Metadata only |
| [spec-miner](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/spec-miner.md) | Extracts behavioral specs from existing codebases for OpenSpec. | Metadata only |

### General review, testing and documentation (12)

| Agent | Declared role | Review depth |
|---|---|---|
| [code-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/code-reviewer.md) | Expert code review specialist. | Metadata only |
| [code-simplifier](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/code-simplifier.md) | Simplifies and refines code for clarity, consistency, and maintainability while preserving behavior. | Metadata only |
| [comment-analyzer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/comment-analyzer.md) | Analyze code comments for accuracy, completeness, maintainability, and comment rot risk. | Metadata only |
| [commit-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/commit-reviewer.md) | Reviews a staged diff and drafts a Conventional Commits-compliant message matching the repository's actual history norms. | Metadata only |
| [doc-updater](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/doc-updater.md) | Documentation and codemap specialist. | Metadata only |
| [docs-lookup](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/docs-lookup.md) | When the user asks how to use a library, framework, or API or needs up-to-date code examples, use Context7 MCP to fetch current documentation and return answers with examples. | Metadata only |
| [pr-test-analyzer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/pr-test-analyzer.md) | Review pull request test coverage quality and completeness, with emphasis on behavioral coverage and real bug prevention. | Metadata only |
| [refactor-cleaner](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/refactor-cleaner.md) | Dead code cleanup and consolidation specialist. | Metadata only |
| [security-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/security-reviewer.md) | Security vulnerability detection and remediation specialist. | Metadata only |
| [silent-failure-hunter](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/silent-failure-hunter.md) | Review code for silent failures, swallowed errors, bad fallbacks, and missing error propagation. | Metadata only |
| [tdd-guide](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/tdd-guide.md) | Test-Driven Development specialist enforcing write-tests-first methodology. | Metadata only |
| [type-design-analyzer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/type-design-analyzer.md) | Analyze type design for encapsulation, invariant expression, usefulness, and enforcement. | Metadata only |

### Website and frontend (9)

| Agent | Declared role | Review depth |
|---|---|---|
| [a11y-architect](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/a11y-architect.md) | Accessibility Architect specializing in WCAG 2.2 compliance for Web and Native platforms. | Full body read |
| [e2e-runner](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/e2e-runner.md) | End-to-end testing specialist using Vercel Agent Browser (preferred) with Playwright fallback. | Full body read |
| [performance-optimizer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/performance-optimizer.md) | Performance analysis and optimization specialist. | Full body read |
| [react-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/react-build-resolver.md) | Diagnose and fix React build failures across Vite, webpack, Next.js, CRA, Parcel, esbuild, and Bun. | Metadata only |
| [react-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/react-reviewer.md) | Expert React/JSX code reviewer specializing in hook correctness, render performance, server/client component boundaries, accessibility, and React-specific security. | Full body read |
| [typescript-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/typescript-reviewer.md) | Expert TypeScript/JavaScript code reviewer specializing in type safety, async correctness, Node/web security, and idiomatic patterns. | Metadata only |
| [vue-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/vue-reviewer.md) | Expert Vue.js code reviewer specializing in Composition API correctness, reactivity pitfalls, component architecture, template security, and Vue-specific performance. | Metadata only |
| [seo-specialist](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/seo-specialist.md) | SEO specialist for technical SEO audits, on-page optimization, structured data, Core Web Vitals, and content/keyword mapping. | Metadata only |
| [marketing-agent](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/marketing-agent.md) | Marketing strategist and copywriter for campaign planning, audience research, positioning, copy creation, and content review. | Metadata only |

### Agent workflows and evaluation (7)

| Agent | Declared role | Review depth |
|---|---|---|
| [agent-evaluator](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/agent-evaluator.md) | Evaluates agent output against 5-axis quality rubric (accuracy, completeness, clarity, actionability, conciseness). | Full body read |
| [conversation-analyzer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/conversation-analyzer.md) | Use this agent when analyzing conversation transcripts to find behaviors worth preventing with hooks. | Metadata only |
| [gan-evaluator](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/gan-evaluator.md) | GAN Harness — Evaluator agent. | Metadata only |
| [gan-generator](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/gan-generator.md) | GAN Harness — Generator agent. | Metadata only |
| [gan-planner](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/gan-planner.md) | GAN Harness — Planner agent. | Metadata only |
| [harness-optimizer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/harness-optimizer.md) | Improve local agent-harness configuration reliability and cost using eval-driven grading (pass@k/pass^k) derived from the eval-harness skill. | Full body read |
| [loop-operator](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/loop-operator.md) | Operate autonomous agent loops, monitor progress, and intervene safely when loops stall. | Metadata only |

### Other domains and operations (13)

| Agent | Declared role | Review depth |
|---|---|---|
| [chief-of-staff](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/chief-of-staff.md) | Personal communication chief of staff that triages email, Slack, LINE, and Messenger. | Metadata only |
| [database-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/database-reviewer.md) | PostgreSQL database specialist for query optimization, schema design, security, and performance. | Metadata only |
| [healthcare-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/healthcare-reviewer.md) | Reviews healthcare application code for clinical safety, CDSS accuracy, PHI compliance, and medical data integrity. | Metadata only |
| [homelab-architect](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/homelab-architect.md) | Designs home and small-lab network plans from hardware inventory, goals, and operator experience level, with safe staged changes and rollback guidance. | Metadata only |
| [mle-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/mle-reviewer.md) | Production machine-learning engineering reviewer for data contracts, feature pipelines, training reproducibility, offline/online evaluation, model serving, monitoring, and rollback. | Metadata only |
| [network-architect](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/network-architect.md) | Designs enterprise or multi-site network architecture from requirements, using existing network skills for focused routing, validation, automation, and troubleshooting detail. | Metadata only |
| [network-config-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/network-config-reviewer.md) | Reviews router and switch configurations for security, correctness, stale references, risky change-window commands, and missing operational guardrails. | Metadata only |
| [network-troubleshooter](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/network-troubleshooter.md) | Diagnoses network connectivity, routing, DNS, interface, and policy symptoms with a read-only OSI-layer workflow and evidence-backed root cause summary. | Metadata only |
| [opensource-forker](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/opensource-forker.md) | Fork any project for open-sourcing. | Metadata only |
| [opensource-packager](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/opensource-packager.md) | Generate complete open-source packaging for a sanitized project. | Metadata only |
| [opensource-sanitizer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/opensource-sanitizer.md) | Verify an open-source fork is fully sanitized before release. | Metadata only |
| [rag-pipeline-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/rag-pipeline-reviewer.md) | Reviews RAG (Retrieval-Augmented Generation) pipelines for retrieval quality, chunking strategy, embedding choices, and evaluation coverage. | Metadata only |
| [bengali-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/bengali-reviewer.md) | Reviews code handling Bengali (Bangla) text for Unicode correctness, proper normalization, script-aware processing, and internationalization best practices. | Metadata only |

### Other build, language and framework specialists (25)

| Agent | Declared role | Review depth |
|---|---|---|
| [build-error-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/build-error-resolver.md) | Build and TypeScript error resolution specialist. | Metadata only |
| [cpp-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/cpp-build-resolver.md) | C++ build, CMake, and compilation error resolution specialist. | Metadata only |
| [cpp-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/cpp-reviewer.md) | Expert C++ code reviewer specializing in memory safety, modern C++ idioms, concurrency, and performance. | Metadata only |
| [csharp-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/csharp-reviewer.md) | Expert C# code reviewer specializing in .NET conventions, async patterns, security, nullable reference types, and performance. | Metadata only |
| [dart-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/dart-build-resolver.md) | Dart/Flutter build, analysis, and dependency error resolution specialist. | Metadata only |
| [django-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/django-build-resolver.md) | Django/Python build, migration, and dependency error resolution specialist. | Metadata only |
| [django-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/django-reviewer.md) | Expert Django code reviewer specializing in ORM correctness, DRF patterns, migration safety, security misconfigurations, and production-grade Django practices. | Metadata only |
| [fastapi-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/fastapi-reviewer.md) | Reviews FastAPI applications for async correctness, dependency injection, Pydantic schemas, security, OpenAPI quality, testing, and production readiness. | Metadata only |
| [flutter-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/flutter-reviewer.md) | Flutter and Dart code reviewer. | Metadata only |
| [fsharp-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/fsharp-reviewer.md) | Expert F# code reviewer specializing in functional idioms, type safety, pattern matching, computation expressions, and performance. | Metadata only |
| [go-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/go-build-resolver.md) | Go build, vet, and compilation error resolution specialist. | Metadata only |
| [go-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/go-reviewer.md) | Expert Go code reviewer specializing in idiomatic Go, concurrency patterns, error handling, and performance. | Metadata only |
| [harmonyos-app-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/harmonyos-app-resolver.md) | HarmonyOS application development expert specializing in ArkTS and ArkUI. | Metadata only |
| [java-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/java-build-resolver.md) | Java/Maven/Gradle build, compilation, and dependency error resolution specialist. | Metadata only |
| [java-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/java-reviewer.md) | Expert Java code reviewer for Spring Boot and Quarkus projects. | Metadata only |
| [kotlin-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/kotlin-build-resolver.md) | Kotlin/Gradle build, compilation, and dependency error resolution specialist. | Metadata only |
| [kotlin-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/kotlin-reviewer.md) | Kotlin and Android/KMP code reviewer. | Metadata only |
| [php-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/php-reviewer.md) | Expert PHP code reviewer specializing in PSR-12 compliance, PHP type system, Eloquent ORM patterns, security, and performance. | Metadata only |
| [python-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/python-reviewer.md) | Expert Python code reviewer specializing in PEP 8 compliance, Pythonic idioms, type hints, security, and performance. | Metadata only |
| [pytorch-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/pytorch-build-resolver.md) | PyTorch runtime, CUDA, and training error resolution specialist. | Metadata only |
| [ruby-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/ruby-reviewer.md) | Expert Ruby and Rails code reviewer specializing in idiomatic Ruby, Active Record query safety, Rails security defaults, and RSpec/Minitest quality. | Metadata only |
| [rust-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/rust-build-resolver.md) | Rust build, compilation, and dependency error resolution specialist. | Metadata only |
| [rust-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/rust-reviewer.md) | Expert Rust code reviewer specializing in ownership, lifetimes, error handling, unsafe usage, and idiomatic patterns. | Metadata only |
| [swift-build-resolver](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/swift-build-resolver.md) | Swift/Xcode build, compilation, and dependency error resolution specialist. | Metadata only |
| [swift-reviewer](https://github.com/affaan-m/ECC/blob/b38be6a7f6350964d59328b52f0624e1d1d552d1/agents/swift-reviewer.md) | Expert Swift code reviewer specializing in protocol-oriented design, value semantics, ARC memory management, Swift Concurrency, and idiomatic patterns. | Metadata only |

Source: ECC, MIT as declared in the reviewed plugin manifest. No third-party executable payload is copied into this repository. See the [dated comparison](../decisions/2026-11-02-matt-ecc-karpathy-build-advisor.json) for evidence and limits.
