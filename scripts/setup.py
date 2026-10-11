#!/usr/bin/env python3
"""Install this repo's global instructions. Does not install third-party software."""
import argparse
import hashlib
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--codex-home', type=Path, default=Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))))
    parser.add_argument('--check', action='store_true', help='Verify installed global rules without writing')
    args = parser.parse_args()
    try:
        rules = (ROOT / 'global' / 'AGENTS.md').read_text(encoding='utf-8')
        if args.check:
            ok = check(args.codex_home, rules)
            print('Global rules match this repo.' if ok else 'Global rules are missing or differ from this repo.')
            return 0 if ok else 1
        changed = install(args.codex_home, rules)
        print(('Installed: ' if changed else 'Already current: ') + str(target_for(args.codex_home)))
        print('Start a new Codex session to load the global rules.')
        print('This command installs instructions only. Continue setup/SETUP.md for SkillSpector, skills, plugins, MCP and GitHub logging.')
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
