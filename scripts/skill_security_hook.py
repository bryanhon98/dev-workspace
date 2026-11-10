"""Codex/Claude Code PreToolUse interception for SkillSpector-controlled operations.

For a simple HTTPS GitHub clone, rewrite the command to the staged scanner workflow.
Direct installation managers and unmanaged writes are blocked, not secretly allowed.
Host hooks are best-effort: they cannot enforce operating-system permissions.
"""
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys

INSTALL = [
    re.compile(r'\bclaude\s+plugin\s+install\b', re.I),
    re.compile(r'\bcodex\s+plugin\s+(?:add|install)\b', re.I),
    re.compile(r'\b(?:npx(?:\s+-y)?|bunx|pnpm(?:\s+dlx)?|yarn\s+dlx)\s+'
               r'(?:@[^\s]+/)?skills?\s+(?:add|install|update)\b', re.I),
]
ACTIVE = re.compile(
    r'(?:^|[/\s"\x27])(?:[^\s"\x27]*?/)?'
    r'(?:\.claude/skills|\.claude/plugins|\.agents/skills|\.codex/plugins)'
    r'(?:/|[/\s"\x27]|$)', re.I,
)
MUTATE = re.compile(
    r'\b(?:git\s+(?:clone|pull|checkout|reset)|'
    r'copy-item|move-item|new-item|set-content|add-content|'
    r'cp|mv|install|robocopy|xcopy|mkdir|ln\s+-s)\b', re.I)
CLONE = re.compile(
    r'^git\s+clone\s+(?:--\s+)?'
    r'(https://github[.]com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:[.]git)?/?)'
    r'(?:\s+([A-Za-z0-9_.\\/-]+))?\s*$', re.I)

def _clone_command(url, destination, cwd=None):
    script = str(Path(__file__).resolve().with_name('secure_operations.py'))
    parts = [sys.executable, script, 'clone', '--url', url]
    if destination:
        parts.extend(['--destination', destination])
    if cwd:
        parts.extend(['--cwd', str(cwd)])
    return subprocess.list2cmdline(parts) if os.name == 'nt' else shlex.join(parts)

def decide(payload):
    """Return (block_reason, replacement_command); never return both."""
    if not isinstance(payload, dict):
        return 'Invalid hook input', None
    if payload.get('hook_event_name') != 'PreToolUse':
        return None, None
    tool = str(payload.get('tool_name') or '')
    args = payload.get('tool_input')
    guarded = ('Bash', 'PowerShell', 'Write', 'Edit', 'MultiEdit',
               'NotebookEdit', 'apply_patch')
    if tool in guarded and not isinstance(args, dict):
        return 'Missing tool arguments', None
    if not isinstance(args, dict):
        return None, None
    if tool in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'apply_patch'):
        path = str(args.get('file_path') or args.get('path') or '')
        if ACTIVE.search(path.replace('\\', '/')):
            return 'Direct edits to active skill/plugin directories are blocked', None
    command = args.get('command') or args.get('shell_command') or args.get('cmd') or ''
    if isinstance(command, list):
        command = ' '.join(map(str, command))
    if tool in ('Bash', 'PowerShell') and not command:
        return 'Missing shell command', None
    if isinstance(command, str) and command:
        normalized = command.replace('\\', '/')
        if tool == 'apply_patch' and ACTIVE.search(normalized):
            return 'Direct patching of active skill/plugin directories is blocked', None
        # The MCP server is an installation entrypoint, not a shell command.
        # Host-native permission checks happen only on an MCP tool call.
        # MCP registration itself remains allowed.
        if ('native_approval_mcp' in normalized.lower() and
                not re.search(r'\b(?:codex|claude)\s+mcp\s+add\b', normalized, re.I)):
            return ('The security MCP server must be invoked as an MCP tool, '
                    'not directly from an agent shell command'), None
        if any(p.search(normalized) for p in INSTALL):
            return ('Direct skill/plugin manager install or update blocked; use '
                    'secure_operations.py install --source <staged-dir> --name <skill-name> '
                    '(add --update for an existing controlled skill)'), None
        if ACTIVE.search(normalized) and MUTATE.search(normalized):
            return 'Direct activation in agent skill/plugin directories is blocked', None
        if tool in ('Bash', 'PowerShell') and re.search(r'\bgit\s+clone\b', normalized, re.I):
            match = CLONE.fullmatch(command.strip())
            if match:
                return None, _clone_command(match.group(1), match.group(2), payload.get('cwd'))
            return ('Unsupported or compound git clone command blocked; '
                    'use secure_operations.py clone --url <https-github-url> '
                    '--destination <dir>'), None
        if tool in ('Bash', 'PowerShell') and re.search(r'\bgit\b.*\bclone\b', normalized, re.I):
            return 'Unsupported Git clone syntax blocked; use controlled clone', None
    patch = str(args.get('patch') or '')
    if tool in ('Write', 'Edit', 'MultiEdit', 'apply_patch') and ACTIVE.search(patch.replace('\\', '/')):
        return 'Patching an active skill/plugin directory is blocked', None
    return None, None

def classify(payload):
    """Compatibility helper for tests: return blocking reason or None."""
    return decide(payload)[0]

def main():
    try:
        raw = sys.stdin.read(1048577)
        if len(raw) > 1048576:
            raise ValueError('Oversized security hook input')
        payload = json.loads(raw)
        reason, replacement = decide(payload)
    except (ValueError, TypeError):
        reason, replacement = 'Malformed security-hook JSON input', None
    if reason:
        print(reason, file=sys.stderr)
        return 2
    if replacement:
        original = payload['tool_input']
        edited = {**original, 'command': replacement}
        print(json.dumps({'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'permissionDecision': 'allow',
            'updatedInput': edited,
            'additionalContext': 'Git clone routed through staged SkillSpector inspection'}}))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
