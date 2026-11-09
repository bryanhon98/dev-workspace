"""PreToolUse guard for Codex and Claude Code agent capability activation.

Blocks recognized direct install/write paths. Not a substitute for the
scan-before-install logic in scripts/install_advisor.py; some tools bypass hooks.
"""
import json
import re
import sys

INSTALL = [
    re.compile(r'\bclaude\s+plugin\s+install\b', re.I),
    re.compile(r'\bcodex\s+plugin\s+(?:add|install)\b', re.I),
    re.compile(r'\b(?:npx(?:\s+-y)?|bunx|pnpm(?:\s+dlx)?|yarn\s+dlx)\s+'
               r'(?:@[^\s]+/)?skills?\s+(?:add|install)\b', re.I),
]
ACTIVE = re.compile(
    r'(?:^|[/\s"\x27])(?:[^\s"\x27]*?/)?'
    r'(?:\.claude/skills|\.claude/plugins|\.agents/skills|\.codex/plugins)'
    r'(?:/|[/\s"\x27]|$)', re.I,
)
MUTATE = re.compile(
    r'\b(?:git\s+(?:clone|pull|checkout|reset)|'
    r'copy-item|move-item|new-item|set-content|add-content|'
    r'cp|mv|install|robocopy|xcopy|mkdir|ln\s+-s)\b', re.I
)


def classify(payload):
    """Return a blocking reason or None for recognized native tool actions."""
    if not isinstance(payload, dict):
        return 'Invalid hook input'
    if payload.get('hook_event_name') != 'PreToolUse':
        return None
    tool = str(payload.get('tool_name') or '')
    arg = payload.get('tool_input')
    if not isinstance(arg, dict):
        return ('Missing tool arguments' if tool in ('Bash', 'Write', 'Edit', 'MultiEdit',
                                                  'NotebookEdit', 'apply_patch') else None)
    if tool in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit', 'apply_patch'):
        path = str(arg.get('file_path') or arg.get('path') or '')
        if ACTIVE.search(path.replace('\\', '/')):
            return 'Direct edits to active skill/plugin directories are blocked'
    cmd = arg.get('command') or arg.get('shell_command') or arg.get('cmd') or ''
    if isinstance(cmd, list):
        cmd = ' '.join(map(str, cmd))
    if tool == 'Bash' and not cmd:
        return 'Missing Bash command'
    if isinstance(cmd, str) and cmd:
        normalized = cmd.replace('\\', '/')
        if tool == 'apply_patch' and ACTIVE.search(normalized):
            return 'Direct patching of active skill/plugin files is blocked'
        if any(p.search(normalized) for p in INSTALL):
            return 'Direct skill/plugin manager installation is blocked'
        if ACTIVE.search(normalized) and MUTATE.search(normalized):
            return 'Direct activation inside agent skill/plugin directories is blocked'
    if tool in ('Write', 'Edit', 'MultiEdit', 'apply_patch'):
        patch = str(arg.get('patch') or '')
        if ACTIVE.search(patch.replace('\\', '/')):
            return 'Patch of active agent skill/plugin directory is blocked'
    return None


def main():
    try:
        raw = sys.stdin.read(1048577)
        if len(raw) > 1048576:
            raise ValueError('Oversized security hook input')
        reason = classify(json.loads(raw))
    except (ValueError, TypeError):
        reason = 'Malformed security-hook JSON input'
    if reason:
        print(reason + '. Stage and scan with SkillSpector before activation.', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
