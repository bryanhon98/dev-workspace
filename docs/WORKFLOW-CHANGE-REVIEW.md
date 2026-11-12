# Review gate for reusable workflow changes

This policy applies when a failure or user correction in one project suggests changing the reusable `dev-workspace` instructions, scripts, security controls, skill routing, or agent process. It does **not** require a review cycle for ordinary project edits.

## Generalization decision

Record these facts before proposing a shared change:

1. **Observed problem:** The original request, expected result, actual result, and source evidence. Do not infer that one project's complaint proves a universal rule.
2. **Root cause:** Which instruction, implementation, coordination decision or missing verification caused the problem; distinguish confirmed causes from hypotheses.
3. **Smallest appropriate scope:**
   - **Project-specific:** keep it in that project (for example, exact Nullement art or animation requirements).
   - **Domain-specific:** update only the relevant design, backend or security workflow.
   - **Global:** update the shared coordinator or security workflow only if evidence supports reuse across materially different projects.
   - **Unconfirmed:** record the observation but do not change shared behavior yet.
4. **Proposed change:** Show the minimal diff, what it fixes, alternatives, expected cost, and rollback.
5. **Regression evidence:** Reproduce the original failure; evaluate at least one unrelated project type and one simple task that must remain lightweight. Track output quality, correctness, safety, time/tool/token cost when observable, and unexpected new steps. Do not invent test results.

## Fresh-context independent review — required before global adoption

A **different, actual worker in a clean context** must review material global workflow changes before they are merged or activated.

The reviewer receives the original user requirement, source evidence, candidate diff, failing example, comparison against the old behavior, and test results. It must not receive only the proposing agent's favorable summary or be told to agree.

The reviewer must answer:

- Is the root cause supported, and does the change actually address it?
- Would it help more than the originating project? Is a narrower rule better?
- What regressions, permissions, privacy exposure, token/time cost or new complexity could it introduce?
- What tests or counterexamples are missing?

Record the reviewer's identity, source context, objections, and their disposition. A fresh context reduces shared reasoning bias but is not a guarantee of independence; the evidence and tests still matter.

**No real subagent or review capability:** mark the gate `blocked-independent-review`. Keep a proposed change on a review branch/issue; do not claim a simulated persona or the author's own second pass is an independent review. Do not merge or activate the new global policy until the gate has been satisfied.

Review approval is not permission to bypass host security, install an unscanned skill, publish sensitive records or silently change the user's agreed constraints. Keep the user's existing approval requirements.

## Where results belong

- Project-local requirements, raw chat evidence, internal paths and private logs stay in the project, with its existing local ignore/permission controls.
- Sanitize and publish only reusable findings, test case descriptions, checked versions, verified outcomes and decisions into `dev-workspace/knowledge/decisions/`.
- Do not copy proprietary repositories, credentials or private conversations into the shared knowledge base.
- Save the accepted change, review result, test evidence and rollback instructions as one linked decision. Reopen it when later evidence contradicts the conclusion.

See [workflow regression scenarios](WORKFLOW-REGRESSION-CASES.md) for minimum challenge cases.
