# Execution, tracking and learning

## Readiness and task ownership

Read the confirmed brief, proposal and existing task record before doing work. Resolve missing selected skills and tools using the repo's installation rules and current device inspection. MEDIUM approval applies only to the exact reviewed payload; HIGH/CRITICAL and incomplete scans remain blocked. Record availability evidence after checking actual files, supported invocation and required tools; state unperformed runtime checks explicitly. An instruction file alone cannot make a renderer, browser, account connector or model available.

Record each worker assignment in the existing task record (the ledger only when selected under BUILD-FLOW). When a worker ID is only known after creation, record a unique intended assignment, then update the report with the returned worker ID before relying on its result. The coordinator controls the shared plan; workers return reports and work only within their assigned scope. Use independent workers only for independent tasks with non-overlapping write ownership. Serialize shared-file changes and dependent work. Use the host's limits and permission boundaries.

Every worker brief contains:

1. Task ID, concrete deliverable and relevant scope from the confirmed brief.
2. Required skill/source instructions, known inputs and dependencies already completed.
3. File/output ownership, tools available, permitted actions and boundaries.
4. Acceptance criteria, checks to perform and evidence to return.
5. Stop/report conditions: missing information, changed requirements, unavailable capability or conflicting work.

Avoid creating competing coordinators. A worker does not expand the agreed plan or choose a new skill combination. New roles or material scope changes return to the proposal/confirmation step. The host's ordinary safety and authorization rules continue to apply.

## Native host delegation and skill binding

Tool Advisor decides **which** roles and skills fit the confirmed work; the current Codex or Claude Code session executes available workers through its **actual native tools**. This policy is portable, but supported agent modes, permission scopes and skill-loading behavior must be checked in the active host. Do not invent spawn commands, build a parallel agent runtime, or claim that a host's team feature is enabled just because its documentation exists.

For every task that benefits from delegation:

1. Select **one accountable agent/worker role** and the smallest complementary combination of existing baseline instructions and task-specific skills. Do not spawn every available role or stack competing implementation controllers.
2. Check the worker mechanism, tool permissions, skill availability and dependencies in the **current session/device**. A saved or globally listed skill elsewhere is not proof the worker can access it.
3. Dispatch with the host's supported native agent/subagent/team tool, including the approved task, relevant context, selected skill names and exact installed sources, skill invocation/loading instructions, file ownership, dependencies and evidence to return.
4. Ensure the worker actually **invokes the selected skill or reads its complete installed instructions** via a supported mechanism. A `skills` field or role label must not be assumed to preload instructions across host modes; record whether invocation was native or manual and treat unperformed loading as a gap.
5. Capture the actual worker identity, outcome, files changed and checks performed. Keep worker reports separate from coordinator verification; the coordinator integrates results and independently checks acceptance evidence.

Use concurrent workers only for genuinely independent tasks and isolated/non-overlapping writes. When native delegation is missing, disabled, unauthorized or unsuitable, the coordinator may execute sequentially using available skills; explicitly identify that fallback. A skill or agent definition does not launch a model by itself.

Do not mirror a native team's live task list into an independently maintained second tracker. Preserve the existing project tracker as the source of task truth, and use the advisor ledger for proposal/confirmation and durable references or checkpoints only where the approved routing policy needs it. This paragraph refines tracking ownership; it does not weaken the original confirmation, installation-scan or permission gates.

## Verification and resume

Mark started work as running, blocked work with its reason, and returned work as ready for review. A successful worker message is a claim to check. Inspect its outputs and acceptance evidence; run relevant integration or user-journey checks before marking done. Keep task IDs, actors and evidence paths accurate. Use another reviewer when available and warranted; identify self-review honestly.

If a task fails, record the failure and correct it within its approved scope. An incomplete prerequisite blocks dependent tasks. A changed deliverable reopens affected verification. After interruption, read status, confirmation, completed outputs and remaining dependencies; inspect referenced artifacts before relying on saved completion. A ledger cannot prove that an output still exists or remains correct.

When a project already uses Beads, Task Master or another task system, preserve it as the task source. Store advisor task references and acceptance evidence without creating an independently edited competing plan. The local ledger governs only the advisor's brief/combination confirmation and mirrors the relevant task state at checkpoints.

## Finish and remember

Complete only when agreed tasks and checks are finished. Report the delivered result and material limits, including anything untested. Keep project task state private by default. Add a sanitized dated decision to the research checkout only after reviewing it for private data. Retain task fit, exact source revisions, actual outcomes, failed choices, user corrections and reasons to revisit. Do not copy raw conversations, credentials, private project content or local absolute paths into published knowledge.

This is evidence-driven maintenance performed by the assistant. It does not train a model, automatically watch the device, or establish that a new skill is superior merely because its source changed.
