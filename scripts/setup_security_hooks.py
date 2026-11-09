"""Install/check best-effort PreToolUse hooks without overwriting user hooks.

This is optional per-device setup; the advisor installer still enforces scanning.
"""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import host_profiles

MATCHERS = {
    'claude': 'Bash|Write|Edit|MultiEdit|NotebookEdit',
    'codex': 'Bash|apply_patch|Edit|Write',
}


def _command(script):
    parts = [sys.executable, str(script)]
    if os.name == 'nt':
        return subprocess.list2cmdline(parts)
    return shlex.join(parts)


def _entry(script, host):
    return {'matcher': MATCHERS[host],
            'hooks': [{'type': 'command', 'command': _command(script), 'timeout': 30}]}


def config_file(home, host):
    return Path(home) / ('settings.json' if host == 'claude' else 'hooks.json')


def apply(home, host, repo, install=False):
    host_profiles.resolve(host)
    script = Path(repo).resolve() / 'scripts' / 'skill_security_hook.py'
    if not script.is_file():
        raise ValueError('Security hook script is missing: ' + str(script))
    target = config_file(home, host)
    if target.exists():
        try:
            obj = json.loads(target.read_text(encoding='utf-8'))
        except (ValueError, OSError) as exc:
            raise ValueError('Existing hooks settings are not valid JSON') from exc
    else:
        obj = {}
    if not isinstance(obj, dict):
        raise ValueError('Hooks settings must be an object')
    hooks = obj.get('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('Existing hooks structure is invalid')
    entries = hooks.get('PreToolUse', [])
    if not isinstance(entries, list):
        raise ValueError('Existing PreToolUse entries are invalid')
    desired = _entry(script, host)
    for entry in entries:
        if (isinstance(entry, dict) and any(
                'skill_security_hook.py' in str(h.get('command', ''))
                for h in entry.get('hooks', []) if isinstance(h, dict))):
            if entry != desired:
                raise ValueError('Existing security hook differs; reconcile it manually')
            return {'ready': True, 'changed': False, 'path': str(target)}
    if not install:
        return {'ready': False, 'changed': False, 'path': str(target)}
    hooks['PreToolUse'] = [*entries, desired]
    obj['hooks'] = hooks
    target.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite an existing user hook after it changed during inspection.
    before = target.read_bytes() if target.exists() else None
    if before is not None:
        backup = target.with_name(target.name + '.before-dev-workspace.bak')
        if backup.exists():
            raise ValueError('Existing settings backup present; reconcile before modifying hooks')
        backup.write_bytes(before)
    temporary = target.with_suffix(target.suffix + '.dev-workspace.tmp')
    if temporary.exists():
        raise ValueError('Temporary hook config exists; reconcile before modifying')
    try:
        temporary.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return {'ready': True, 'changed': True, 'path': str(target)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--host', choices=host_profiles.host_names(), required=True)
    p.add_argument('--home', type=Path, default=None, help='Host configuration home')
    p.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--install', action='store_true')
    group.add_argument('--check', action='store_true')
    args = p.parse_args(argv)
    try:
        result = apply(args.home or host_profiles.home_dir(args.host), args.host, args.repo, args.install)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['ready'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
