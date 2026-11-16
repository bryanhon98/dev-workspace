# Scan first, then decide

This is the current installation policy, agreed on 2026-11-16. Global instructions own authorization; this document defines the review format and decision rules. It supersedes older severity-veto descriptions.

## Flow

1. Check that the live host can request native permission for reviewed installation. The agreed interaction is a full review in chat followed by one concise Codex permission prompt. Do not also ask for a typed chat approval. If the required host permission is unavailable, disclose that before promising installation; independent staging and scanning may continue.
2. Stage the selected exact revision outside active skill directories. Never run source-provided scripts to inspect it. Preserve original skill files unless the user explicitly requests edits.
3. Scan every selected inactive payload with static-only NVIDIA SkillSpector. Severity findings and structured incomplete results must not stop remaining independent scans. Retain recoverable scanner errors in the consolidated review. Unsafe paths or changing files stop handling that payload; continue independent safe work.
4. Present the review below. A scan cannot certify absence of malware, and a skill scan does not cover unrelated application source.
5. Automatically approve only a selected payload with a valid, complete static report, 100% coverage, no unresolved gaps, SAFE recommendation, LOW overall severity, and no individual finding above LOW. An AI assessment of a false positive does not change the scanner evidence or qualify a higher-risk report for automatic installation.
6. For every other assessable result, present the complete chat review first, then request native permission and wait for the user to choose Allow once or Deny. HIGH/CRITICAL, DO_NOT_INSTALL and structured incomplete results are reviewable concerns, not automatic vetoes. Missing scanner, malformed/unusable reports, unsafe paths and changed bytes are technical failures, not approvable reports. Explain them after finishing independent scans.
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

**Review the findings above, then choose Allow once or Deny in the Codex prompt.**

Do not ask for a separate typed chat approval when the native prompt is available. For eligible LOW/SAFE results, state that installation proceeds under the user's standing LOW-risk authorization; stricter host permissions still apply.

## Concise native prompt plan

The chat review carries the complete findings, coverage gaps, capability explanation and contextual recommendation. The native prompt should identify the action without repeating that report:

> Install Humanizer 4.0.0?
> Install the unchanged package described in the review above.

Use the actual package name and version (or exact revision when no version is declared), and identify the scope/destination when needed to distinguish installs. The host supplies the real Allow once / Deny controls. Codex may also display technical tool arguments; do not promise a buttons-only dialog.

A short prompt must remain bound to the exact review identity, files, scanner findings and coverage. Revalidate them before activation. Changed files, findings, scope or coverage require an updated full review and a new native decision. Do not replace the exact summary argument with arbitrary short prose in the existing tool: its current implementation requires the full summary to match. The implementation must first separate concise display text from the full integrity-bound review evidence, with regression checks for changed evidence, rejection and no-answer behavior.

**Status:** full chat review and a real native approval dialog were observed in user-provided screenshots on 2026-11-16. The shorter native summary is an approved plan, not an implemented or verified runtime change. The screenshots do not prove the final installation or denial behavior.

Before shipping the concise summary implementation, verify these cases:

- Full findings and coverage gaps are shown in chat before requesting native permission.
- The display names the actual package/version and matches the review identity; a caller cannot substitute a misleading name or scope.
- Allow once activates only unchanged reviewed files; Deny or an unanswered prompt activates nothing.
- Changed files, findings or coverage reject the old review, even if the short display text is unchanged.
- LOW automation still requires the existing complete LOW/SAFE gate. Shorter text does not change eligibility.
- No third-party skill content, host approval policy or original scanner finding is altered to simplify the prompt.

## Host enforcement boundary

An earlier explicit chat approval remains relevant authorization for the same package; do not ask the chat question again. It never substitutes for a required native permission prompt. With native prompting available, the native decision is the single approval checkpoint after the chat review.

A review ID, saved configuration or successful tool call does not independently prove that the host asked a person. Never spoof a required prompt or use an agent-authored approval flag as a substitute. On hosts that cannot enforce the required human gate, leave the affected package inactive and explain the unmet requirement once. A terminal fallback is opt-in only; never open a shell merely to repeat an approval.

Full access and Custom are host permission modes, not scanner results. The user observed a native prompt after changing modes. Reconnect/restart may be required to load server changes, but saved code is not proof of live behavior. Do not claim every host or future session is verified.
