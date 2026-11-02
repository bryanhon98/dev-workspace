# Installable advisor implementation

The user has specified and authorized the product: install this repo as a setup/advisor brain, interview through a skill, discover task-specific capabilities locally and externally, present a combination for confirmation, then coordinate workers and retain task progress. This plan implements that scope; it does not authorize new laptop changes or unrelated skill installations during development.

## Design

The first supported host is Codex. Keep the existing read-only catalog/default setup behavior. Add an explicit `python3 scripts/setup.py --install-advisor` command that selects a small named bundle, runs the reviewed static scanner, installs complete skill payloads and managed global instructions, and records local receipts. `--check-advisor` verifies files and dependencies without writing. Keep the checkout as the research library; record its exact local location in managed instructions. Test installation in an isolated profile, not the user's inaccessible laptop.

The core is a new `tool-advisor` skill plus the already saved, reviewed Matt Pocock `grilling` and Vercel `find-skills` payloads. Preserve their licenses and exact historical exception scope. No full ECC, Agency or third-party tracker is required. Current-source research is separate from adopting new upstream payloads. Read the upstream skills when using their phases; do not claim they executed merely because their names appear in a plan. Available plugin/native invocation or explicit complete-file loading must be recorded honestly.

Task state lives under `.tool-advisor/` in the target project and is ignored by Git. One coordinator writes the ledger; workers report back. Its commands enforce confirmation freshness, role readiness, dependency completion and evidence-required completion. The host performs actual discovery, interviewing, delegation and verification. The CLI does not launch models or authenticate a user's answer, and it cannot prevent an assistant bypassing it. Existing project trackers remain the task source when present; the advisor retains selection/confirmation and links to their task IDs.

Approaches considered: documentation alone lacks executable setup and state; a full orchestration/task platform adds host/runtime requirements and competing controllers; a small installable skill bundle and Python ledger fits the accepted general workflow. A tracker/source comparison is saved separately. No benchmarked superiority is claimed.

## Interfaces and tasks

- [x] Preserve a before-skill response baseline, then write the new skill and run fresh-context response tests with it. Include complete and unclear briefs, confirmation pressure, changed combinations, unavailable skills, general noncoding tasks and non-triggers.
- [x] Create `skills/custom/tool-advisor/SKILL.md` and bounded supporting references. Required phases: read/use grilling, capture brief, use find-skills plus repo/external research, show role/source/version/availability/overlap/cost table, wait for confirmation of that combination, prepare missing selected capabilities, coordinate verified work and save sanitized outcomes.
- [x] Implement the project ledger at `skills/custom/tool-advisor/scripts/ledger.py`, with `scripts/advisor.py` as a repository entrypoint. CLI: `--project PATH init --goal TEXT`; `brief --file JSON`; `propose --file JSON`; `confirm --digest SHA --evidence TEXT`; `ready --role ID --evidence TEXT`; `start --task ID --actor TEXT`; `update --task ID --status blocked|review|done --evidence TEXT`; `status`; `complete`. Test real temporary project state before implementation.
- [x] Brief JSON: `goal`, `deliverables`, `constraints`, `success_criteria`, `open_questions`; optional `assumptions`. Proposal JSON: `roles` (id, job, component, kind, source, revision, availability, reason, alternatives) and `tasks` (id, title, role, depends_on, acceptance). Kinds: skill/agent/tool/manual; availability: ready/needs-install/unverified. Missing scope answers block proposal; task references and dependency DAG must validate. Record explicit confirmation tied to brief+proposal digest; any material change invalidates it. Track actual actors and evidence; dependencies must be done before work starts. Reopening completed work invalidates downstream verification. Never treat the presence of a source file as runtime availability.
- [x] Create `advisor-bundle.json` with exact source payload hashes, versions, license copies, scanner pin and review references. Implement `scripts/install_advisor.py` and meaningful tests. Public functions: `install_bundle(repo_root, skills_root, codex_home, scanner=None) -> dict`; `check_bundle(repo_root, skills_root, codex_home) -> dict` with `ready` and `errors`. Installer stages and scans before activation, rejects symlinks/unmanaged conflicts/local modifications, preserves unchanged copies, and records exact installed hashes and audit results. No bare `npx`, baseline suppression, scanner exclusions or general approval bypass.
- [x] Integrate setup CLI flags, core selection output and managed checkout locator; retain the existing instruction installer and tests. Document Python 3.12+ for scanner bootstrap, network/model requirements and host limitations. An install/check receipt proves files and scanner checks, not a live model invocation.
- [x] Inspect the reviewed scanner bootstrap and install it in an isolated development venv. Run actual static scans on final payloads and compare only exact historical exceptions. New findings block activation and remain concrete review items; they do not stop development, tests or preparing a reviewable bundle.
- [x] Validate fixture installer success/rollback/refusal paths, task state transitions, source archive integrity and all 84 repo tests. Verify real scanner reports and actual source-bundle refusal before target writes. Obtain independent ledger review and fix its findings; primary-agent installer review is recorded separately. Keep project state and temporary profiles out of Git.
- [ ] Activate the actual source bundle in an isolated profile and verify native host discovery. Blocked by the new LP3 finding; successful fixture installs do not establish this result.
- [x] Prepare sanitized source for authorized publication; remote completion is reported only after verifying the push.

## Review focus

Tests must cover missing/partial/malformed scanner reports, new findings despite a success-like risk label, complete-file/hash mismatches, local installation edits, failed bundle activation, moved checkout, stale confirmation after edits, missing role readiness, dependency cycles, evidence-free completion, resuming a partially completed job and simultaneous/stale ledger writers. Existing tool and instruction tests must remain green. Behavior trials measure response choices under supplied capabilities; report that they are not full host E2E benchmarks.

## Authoring checklist

- [x] Define trigger/non-trigger cases and preserve baseline responses before writing the skill.
- [x] Five no-guidance response samples: all begin implementation without combination confirmation.
- [x] Draft discovery metadata and concise phase contracts addressing the baseline omission.
- [x] Read all skill supporting files and implementation code; no hidden executable dependencies.
- [x] Run five fresh-context samples with the skill and edge-case trials; inspect every answer.
- [x] Refine any failed behavior and rerun affected trials.
- [x] Complete static review, exact hashes and licenses; save review and refusal evidence.
- [ ] Obtain specific LP3 approval or a reviewed resolution before creating an actual activation receipt. Publication does not confer approval.

The built-in skill-creator is unavailable in this environment. The repo's creator workflow and available Superpowers writing-skills/TDD guidance are being used directly. The accepted product brief supplies the scope; implementation details above are engineering choices, not new user preferences.

## Final verification state

All 84 unit tests passed, including real temporary ledger transitions and fixture installer rollback/refusal tests. The original research archive hashes and derived coverage match. Actual final static scans cover all payload files; grilling/find-skills retain only their exact historical approved findings. The new advisor has one MEDIUM LP3 finding. Its actual install command refuses before creating target skills, instructions or receipts. See `audits/tool-advisor-1.0.0-20261102/review.json`. No laptop installation or fresh-session native invocation is claimed.
