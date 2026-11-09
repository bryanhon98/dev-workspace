"""Install one staged skill through the mandatory SkillSpector safety gate.

Designed for optional, task-specific skills outside the curated advisor bundle.
No audit JSON, finding ledger or automatic trust cache is created.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import host_profiles
from install_advisor import _files, _path, _scan, _scanner_executable


def install_one(source, skills_root, name, scanner=None):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('Invalid skill name')
    source = _path(source)
    root = _path(skills_root)
    original = _files(source)
    if 'SKILL.md' not in original:
        raise ValueError('Source must contain SKILL.md')
    target = _path(root / name)
    if target.exists():
        raise ValueError('Skill already exists; manually reconcile or remove it before replacing: ' + name)
    scanner_info = _scanner_executable(scanner)
    root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.skill-stage-', dir=root.parent) as tmp:
        staged = Path(tmp) / name
        shutil.copytree(source, staged)
        if _files(staged) != original:
            raise ValueError('Source changed before scanning')
        warnings = _scan(staged, scanner_info, original)
        if _files(staged) != original or _files(source) != original:
            raise ValueError('Source changed while scanning')
        root.mkdir(parents=True, exist_ok=True)
        # Another process can still write the destination; fail rather than overwrite it.
        if target.exists():
            raise ValueError('Skill appeared during scanning: ' + name)
        os.rename(staged, target)
        try:
            if _files(target) != original:
                raise ValueError('Installed files differ from scanned source')
        except Exception:
            shutil.rmtree(target)
            raise
    return {'installed': True, 'name': name, 'path': str(target),
            'scanner': scanner_info, 'warnings': warnings,
            'note': 'Fresh scan only; no historical scan records stored'}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True, help='Previously staged local skill directory')
    p.add_argument('--name', required=True)
    p.add_argument('--host', choices=host_profiles.host_names(), default='codex')
    p.add_argument('--skills-root', type=Path, default=None)
    p.add_argument('--scanner', type=Path, default=None)
    args = p.parse_args(argv)
    try:
        result = install_one(args.source, args.skills_root or
                             host_profiles.default_skills_root(args.host), args.name, args.scanner)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
