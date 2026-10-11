# Maintain this personal Codex setup

Read global/AGENTS.md for setup/inspection/sync rules; leave global/COMMUNICATION.md inactive unless the user explicitly asks to apply it. Keep this repo focused on syncing those instructions, skills, plugins and MCP setup.

On "setup my Codex using this repo", follow the short flow in README.md: list the catalog first, ask which skills or all eligible skills, then install only the chosen skills after inspection. Plugins/MCPs are a manual setup checklist. Use scripts/setup.py to display the catalog; --install-rules explicitly restores global/AGENTS.md only into Codex's user instructions. No arguments must not modify the device.

Publish verified sanitized setup changes under the user's standing authorization, preserving other devices' work. Do not record unavailable payloads or unchecked installs as ready/successful. Keep explanations short and avoid placeholder documentation. Run python3 -m unittest discover -s tests -v and git diff --check for changes to setup code.
