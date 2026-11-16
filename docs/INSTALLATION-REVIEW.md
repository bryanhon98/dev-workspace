# Scan first, then decide

This is the current installation policy, agreed on 2026-11-16. Global instructions own authorization; this document defines the review format and decision rules. It supersedes older severity-veto descriptions.

## Flow

1. Stage the selected exact revision outside active skill directories. Never run source-provided scripts to inspect it. Preserve original skill files unless the user explicitly requests edits.
2. Scan every selected inactive payload with static-only NVIDIA SkillSpector. Severity findings and structured incomplete results must not stop remaining independent scans. Retain recoverable scanner errors in the consolidated review. Unsafe paths or changing files stop handling that payload; continue independent safe work.
3. Present the review below. A scan cannot certify absence of malware, and a skill scan does not cover unrelated application source.
4. Automatically approve only a selected payload with a valid, complete static report, 100% coverage, no unresolved gaps, SAFE recommendation, LOW overall severity, and no individual finding above LOW. An AI assessment of a false positive does not change the scanner evidence or qualify a higher-risk report for automatic installation.
5. For every other assessable result, ask a plain question and wait for explicit human acceptance. HIGH/CRITICAL, DO_NOT_INSTALL and structured incomplete results are reviewable concerns, not automatic vetoes. Missing scanner, malformed/unusable reports, unsafe paths and changed bytes are technical failures, not approvable reports. Explain them after finishing independent scans.
6. Revalidate exact files and findings before activation. Changed evidence requires a new review. Rejection or no answer leaves files inactive.
7. Verify the installation and save sanitized source, revision and outcome records. Do not label staged, scanned or approved files installed.

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

The question is the conversational decision. Existing host-native permission requirements still apply independently. A review ID, tool description, saved configuration or successful tool call is not evidence that a person approved. Never invoke a reviewed installer on a host known to auto-approve it. If native human permission is unavailable, explain the limitation and use the human-operated terminal fallback; do not spoof approval or weaken host policy. LOW automatic approval does not override stricter host permissions.

The watermark installation demonstrated missing human-prompt enforcement. The current session also has an enforced `never` approval policy. Unit tests cannot prove host UI behavior. Humanizer remains staged; this workflow update does not authorize its installation.
