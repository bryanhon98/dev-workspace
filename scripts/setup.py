#!/usr/bin/env python3
"""Show setup choices; use --install-rules to restore global instructions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

START = '<!-- personal-codex-setup:start -->'
END = '<!-- personal-codex-setup:end -->'
ROOT = Path(__file__).resolve().parents[1]


def block(rules):
    body = rules.strip() + '\n'
    if not rules.strip() or START in rules or END in rules:
        raise ValueError('Rules must be nonempty and must not contain managed markers')
    digest = hashlib.sha256(body.encode()).hexdigest()
    return (START + '\n<!-- content-sha256: ' + digest + ' -->\n' + body + END).encode()


def target_for(home):
    for name in ('AGENTS.override.md', 'AGENTS.md'):
        target = home / name
        if target.is_symlink():
            raise ValueError('Refusing symlink instruction file: ' + str(target))
        if target.exists() and target.read_bytes().strip():
            return target
    return home / 'AGENTS.md'


def managed_span(data):
    start, end = START.encode(), END.encode()
    if start not in data and end not in data:
        return None
    if data.count(start) != 1 or data.count(end) != 1:
        raise ValueError('Malformed or duplicate managed markers; merge manually')
    first, last = data.index(start), data.index(end)
    if last < first:
        raise ValueError('Reversed managed markers; merge manually')
    return first, last + len(end)


def install(home, rules):
    home = Path(home)
    desired = block(rules)
    target = target_for(home)
    before = target.read_bytes() if target.exists() else b''
    span = managed_span(before)
    if span:
        first, last = span
        current = before[first:last]
        if current == desired:
            return False
        match = re.fullmatch(
            re.escape(START.encode()) + rb'\n<!-- content-sha256: ([a-f0-9]{64}) -->\n(.*)' + re.escape(END.encode()),
            current, re.DOTALL)
        if not match or hashlib.sha256(match[2]).hexdigest().encode() != match[1]:
            raise ValueError('Managed rules changed locally; save/reconcile them in the repo first')
        after = before[:first] + desired + before[last:]
    else:
        after = before + (b'\n\n' if before else b'') + desired + b'\n'
    home.mkdir(parents=True, exist_ok=True)
    if before:
        backups = home / 'personal-setup-backups'
        if backups.is_symlink():
            raise ValueError('Refusing symlink backup directory')
        backups.mkdir(exist_ok=True)
        fd, backup = tempfile.mkstemp(prefix=target.name + '.', suffix='.bak', dir=backups)
        with os.fdopen(fd, 'wb') as out:
            out.write(before)
    fd, temporary = tempfile.mkstemp(prefix='.personal-setup-', dir=home)
    try:
        with os.fdopen(fd, 'wb') as out:
            out.write(after)
            out.flush()
            os.fsync(out.fileno())
        if target.is_symlink() or (target.read_bytes() if target.exists() else b'') != before:
            raise ValueError('Instruction file changed during setup; retry after inspecting it')
        os.replace(temporary, target)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    if not check(home, rules):
        raise ValueError('Verification failed; inspect the local backup')
    return True


def check(home, rules):
    target = target_for(Path(home))
    data = target.read_bytes() if target.exists() else b''
    span = managed_span(data)
    return bool(span and data[span[0]:span[1]] == block(rules))


def saved_rules():
    return (ROOT / 'global' / 'AGENTS.md').read_text(encoding='utf-8').strip() + '\n'


def show_catalog():
    catalog = json.loads((ROOT / 'inventory.json').read_text(encoding='utf-8'))
    components = catalog['components']
    for title, kind in [('Prerequisite tools — required before skill installation', 'tool'),
                        ('Skills', 'skill'), ('Manual setup: plugins', 'plugin'),
                        ('Manual setup: MCPs', 'mcp')]:
        print('\n' + title)
        items = [item for item in components if item['kind'] == kind]
        if not items:
            print('  No MCP entries saved.' if kind == 'mcp' else '  No entries saved.')
        for item in items:
            status = 'saved copy; inspect before install' if item.get('restorable') else 'not ready to restore'
            print('  ' + item['name'] + ' — ' + item.get('purpose', '') + ' [' + status + ']')
            print('    Source: ' + str(item.get('source') or 'unconfirmed'))
            print('    Review: ' + item.get('audit_status', 'unknown'))
            print('    Setup/login: ' + item.get('setup_requirements', 'Check requirements before installation.'))
    print('\nTell Codex: Which skills do you want — selected names, all eligible skills, or none?')
    print('Plugins and MCPs are a manual setup checklist. No software or instructions were installed.')
    print('After choosing, Codex can restore global rules with --install-rules and inspect/install selected skills.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--check', action='store_true', help='Verify installed global rules without writing')
    action.add_argument('--install-rules', action='store_true', help='Restore setup rules globally')
    args = parser.parse_args()
    try:
        if not args.check and not args.install_rules:
            show_catalog()
            return 0
        rules = saved_rules()
        if args.check:
            ok = check(args.codex_home, rules)
            print('Global rules match this repo.' if ok else 'Global rules are missing or differ from this repo.')
            return 0 if ok else 1
        changed = install(args.codex_home, rules)
        print(('Installed: ' if changed else 'Already current: ') + str(target_for(args.codex_home)))
        print('Start a new Codex session to load the global rules.')
        print('This command installs instructions only. Continue README.md with Codex for selected skills, manual plugin/MCP setup and GitHub logging.')
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
