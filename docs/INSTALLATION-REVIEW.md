# Scan first, then decide

This is the current installation policy, agreed on 2026-11-16. Global instructions own authorization; this document defines the review format and decision rules. It supersedes older severity-veto descriptions.

## Flow

1. Check the live installation tool's permission requirements first. The desired interaction is one explicit chat approval after the review, followed by installation. If the live tool requires an additional permission step that cannot be satisfied, explain that limitation before asking for installation approval. Do not promise that chat approval alone will complete installation on that host. Staging and scanning may still continue.
2. Stage the selected exact revision outside active skill directories. Never run source-provided scripts to inspect it. Preserve original skill files unless the user explicitly requests edits.
3. Scan every selected inactive payload with static-only NVIDIA SkillSpector. Severity findings and structured incomplete results must not stop remaining independent scans. Retain recoverable scanner errors in the consolidated review. Unsafe paths or changing files stop handling that payload; continue independent safe work.
4. Present the review below. A scan cannot certify absence of malware, and a skill scan does not cover unrelated application source.
5. Automatically approve only a selected payload with a valid, complete static report, 100% coverage, no unresolved gaps, SAFE recommendation, LOW overall severity, and no individual finding above LOW. An AI assessment of a false positive does not change the scanner evidence or qualify a higher-risk report for automatic installation.
6. For every other assessable result, ask a plain question and wait for explicit human acceptance. HIGH/CRITICAL, DO_NOT_INSTALL and structured incomplete results are reviewable concerns, not automatic vetoes. Missing scanner, malformed/unusable reports, unsafe paths and changed bytes are technical failures, not approvable reports. Explain them after finishing independent scans.
7. Revalidate exact files and findings before activation. Changed evidence requires a new review. Rejection or no answer leaves files inactive.
8. Verify the installation and save sanitized source, revision and outcome records. Do not label staged, scanned or approved files installed.

## Human review format

Use these sections in this order. The coordinator writes the contextual assessment; do not invent capabilities from scanner labels. The scanner's original ratings stay visible.

**NAME — installation review**

- Version, official source link and exact revision.
- Purpose, destination/scope, scan coverage and unresolved gaps.
- Scanner overall rating and highest individual severity.
- Current status: staged only / not installed.

**What I found**

| Finding | Severity | Simple explanation | My assessment |
|---|---|---|---|
| Each finding or grouped identical finding with count | Original severity | What the code or instruction actually does | Supported risk judgment, false-positive evidence, or remaining uncertainty |
| Each coverage gap or scan error | Coverage gap / unable to assess | What was not checked and why | How that limits the recommendation |

**Approving this means**

- Explain in short sentences what will be installed and what it can do when used.
- Name actual file, database, account, network, credential, service and dependency access when relevant and evidenced. Distinguish requested capabilities from permissions already enforced by the host; installation is not a new permission grant.
- Describe meaningful side effects and exact scope. Do not imply that the installer automatically sandboxes future skill use.
- State that original skill files remain unchanged unless edits were separately requested.

**My recommendation**

Say approve, reject, or defer, with reasons based on inspected behavior, impact and uncertainty. Evaluate whether each finding matters in this installation. Do not mechanically repeat the scanner verdict, promise zero risk, or call a clean scan proof of safety. Keep the AI assessment separate from the scanner rating.

**Do you want me to install this version, accepting the risks explained above?**

Use a real question, not decorative Approve/Reject text that looks like functioning buttons. For eligible LOW/SAFE results, replace the question with a statement that installation proceeds under the user's standing LOW-risk authorization.

## Host enforcement boundary

An explicit user reply such as "approve", "yes", "y", or "install" after the review authorizes installation of that exact reviewed package. Interpret the reply in context: a quotation, hypothetical example, unrelated yes, or rejection is not approval. Reuse that decision while files, findings and installation scope remain identical. Do not ask the same review question again or require the user to repeat the answer in a terminal. Changed evidence requires a new review.

This conversational authorization does not override a permission requirement imposed by the live host or tool. A review ID, tool description, saved configuration or successful tool call is not evidence that a person approved a required host prompt. Never spoof that prompt, insert an agent-authored approval flag as its substitute, or invoke a reviewed installer on a host known to auto-approve a required human gate. LOW automatic approval also does not override stricter host permissions.

Do not open PowerShell or another terminal as an unsolicited approval fallback. If required host permission is unavailable, retain the chat decision, leave the package inactive, and state the exact unmet requirement once. Offer a terminal fallback only if the user explicitly chooses it. A host-supported route that accepts the actual chat decision would satisfy the intended interaction; the current native installer has not established such a route.

The watermark installation demonstrated missing human-prompt enforcement. The live MCP tools were still advertising the older native-approval contract after the repository update; saved code is not proof that the running server reloaded. Reconnect/restart is needed to load changed tools, but does not by itself prove chat-only approval support. Humanizer's earlier chat approval is retained for its unchanged reviewed package; installation remains unverified.
