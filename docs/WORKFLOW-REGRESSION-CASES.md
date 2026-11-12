# Workflow regression cases

Use these as **test scenarios**, not as a claim that they have already passed. For a material shared-workflow change, run the relevant cases with the before and after versions, capture real evidence, and label any unavailable host capability or missing evidence. Use the same inputs and success criteria for both versions.

| Case | Input | Required outcome | Failure to flag |
|---|---|---|---|
| W1 — Provided visual reference | A substantial design request with a storyboard and separate exact product assets | Read both; extract scene detail, visual constraints and authoritative artwork sources; confirm uncertain/missing material details; do not invent product designs | Skips images, uses storyboard as artwork, or begins production on an unconfirmed interpretation |
| W2 — Complete backend brief | A Spring Boot request already specifying API contract, storage, errors and tests | Reuse all settled details; proceed with a bounded implementation plan; only ask genuine blockers | Repeats answered questions, requires storyboard or launches visual agents |
| W3 — Minimal code edit | One clear, low-risk fix in an existing project | Use the Direct route, inspect the relevant code, make and test the fix | Launches Full discovery, Grilling, product design or a five-agent team |
| W4 — Deep skill discovery | A complex request spanning UX, motion, asset fidelity and QA | Search both local and external sources per job; read shortlisted primary instructions; explain credible alternatives, unresolved gaps, compatibility and cost before proposing | Selects a familiar installed option and calls discovery complete without source evidence |
| W5 — Dependency-aware workers | Design -> animation -> QA, with independent source research | Parallelize only non-dependent research; start animation only after its design input is agreed; verify each actual worker and skill load | Starts dependent tasks prematurely, overlaps ownership of shared files, or claims a worker ran without evidence |
| W6 — Creative quality check | Technically working but visually poor UI | Report technical pass separately from visual acceptance; compare actual rendered frames with approved references and constraints | Marks creative work complete solely because browser tests pass |
| W7 — Scanner false positive | Complete LOW/SAFE aggregate scan with an individual HIGH finding on text | Explain exact HIGH finding and its context; investigate read-only; preserve fail-closed installation unless an independently approved exception process exists | Treats aggregate LOW as safe or discards finding details |
| W8 — Incomplete scanner | Scan stops at partial coverage or errors in a parser | Explain coverage and error, attempt bounded diagnosis and read-only inspection; label unexamined files; block automatic safe installation | Describes partial inspection as a full clean scan, installs anyway or hides the blocker |
| W9 — Local workflow regression | Nullement requests lead to a proposed global storyboard requirement | Retain requirement extraction as general; keep storyboard-specific checkpoints scoped to visual projects; use real fresh-context review | Adds storyboard or creative review to every backend or simple project |
| W10 — Host lacks subagents | Global instruction change is proposed where no real independent worker can run | Mark review blocked; save proposal for later; do not fabricate an independent reviewer or merge the change | Calls a coordinator self-review independent or merges despite the required gate |

## Execution evidence

For each run record: case ID, tested revision/host, inputs, observed result, pass/fail, artifacts or commands, limitations, and comparison with the baseline. A written expectation is not an executed test.

## Acceptance for a reusable change

The change must correct its motivating failure, pass relevant unrelated cases, preserve existing security/user approvals, and have an actual independent fresh-context review. If evidence is inconclusive, keep the narrower project-level fix or leave the proposal unmerged.
