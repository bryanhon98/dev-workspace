"""Install the advisor baseline behind a fresh SkillSpector scan, without audit ledgers.

The CLI scans staged source on every install/update. Local receipts and snapshots
protect user edits; neither is a historical vulnerability/approval database.
This module never runs code from an untrusted skill.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import host_profiles

CORE_NAMES = ('tool-advisor', 'grilling', 'find-skills')
SCANNER_SOURCE = 'https://github.com/nvidia/skillspector'
SHARED_LICENSE = {'source': 'skills/external/matt-pocock/LICENSE', 'destination': 'LICENSE'}


from secure_operations import (safe_path as _path, file_snapshot as _files,
                               scanner_executable as _scanner_executable,
                               scan_skill as _scan)

def _relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Invalid relative path')
    p = PurePosixPath(value)
    if p.is_absolute() or ':' in value or any(s in ('', '.', '..') for s in value.split('/')):
        raise ValueError('Unsafe relative path: ' + value)
    return value


def _inside(root, name):
    return _path(root / _relative(name))


def _json(path):
    try:
        obj = json.loads(_path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError('Cannot read valid JSON: ' + str(path)) from exc
    if not isinstance(obj, dict):
        raise ValueError('Expected JSON object: ' + str(path))
    return obj


def _source_clean(root, item):
    if not (root / '.git').exists():
        return
    paths = [_relative(item['path'])] + [_relative(x['source']) for x in item.get('extra_files', [])]
    result = subprocess.run(['git', '-C', str(root), 'status', '--porcelain',
                             '--untracked-files=all', '--', *paths],
                            capture_output=True, text=True, timeout=30)
    if result.returncode or result.stdout.strip():
        raise ValueError('Skill source has local edits or Git could not verify it: ' + item['name'])


def _bundle(root, selected_names=None):
    manifest = _json(root / 'advisor-bundle.json')
    if manifest.get('schema_version') != 3 or not isinstance(manifest.get('bundle_version'), str):
        raise ValueError('Unsupported advisor bundle manifest')
    if str(manifest.get('scanner', {}).get('source_url', '')).rstrip('/').removesuffix('.git').lower() != SCANNER_SOURCE:
        raise ValueError('Expected official NVIDIA SkillSpector source')
    items = manifest.get('components')
    if not isinstance(items, list) or not items:
        raise ValueError('Empty advisor bundle')
    names = [x.get('name') for x in items if isinstance(x, dict)]
    if len(names) != len(items) or len(set(names)) != len(names) or any(
            not isinstance(n, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', n)
            for n in names):
        raise ValueError('Invalid or duplicate skill names')
    if selected_names is not None and (not selected_names or len(selected_names) != len(set(selected_names))
                                       or not set(selected_names).issubset(names)):
        raise ValueError('Invalid selected skill names')
    selected = set(selected_names) if selected_names is not None else set(names)
    components = []
    for item in items:
        if item['name'] not in selected:
            continue
        if not isinstance(item.get('version'), str) or not item['version'] or not isinstance(item.get('source'), str):
            raise ValueError('Missing skill revision or source: ' + item['name'])
        upstream = item.get('upstream_repository')
        if upstream:
            if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', upstream):
                raise ValueError('Unrecognized official upstream URL: ' + item['name'])
            expected = upstream.removesuffix('.git') + '/tree/' + item['version']
            if not (item['source'] == expected or item['source'].startswith(expected + '/')):
                raise ValueError('Skill source must identify its exact upstream revision: ' + item['name'])
        _source_clean(root, item)
        files = _files(_inside(root, item.get('path')))
        if 'SKILL.md' not in files:
            raise ValueError('Missing skill instructions: ' + item['name'])
        extras = item.get('extra_files', [])
        if not isinstance(extras, list):
            raise ValueError('Invalid extras for ' + item['name'])
        for extra in extras:
            if item['name'] != 'grilling' or extra != SHARED_LICENSE:
                raise ValueError('Unapproved supporting file declaration')
            destination = _relative(extra['destination'])
            if destination in files:
                raise ValueError('Duplicate extra file destination: ' + destination)
            files[destination] = _inside(root, extra['source']).read_bytes()
        components.append({**item, 'installed_files': files})
    return manifest, components, None


def baseline_plan(repo_root):
    root = _path(repo_root)
    base = _json(root / 'advisor-baseline.json')
    required = base.get('required_skills')
    if base.get('schema_version') != 1 or not isinstance(required, list) or not required or (
            len(required) != len(set(required)) or any(not isinstance(n, str) for n in required)):
        raise ValueError('Invalid advisor baseline')
    prepared = False
    error = None
    missing = []
    try:
        manifest, components, _ = _bundle(root)
        actual = {c['name'] for c in components}
        missing = [x for x in required if x not in actual]
        prepared = not missing
    except (OSError, ValueError, KeyError, TypeError) as exc:
        error = str(exc)
    return {'required_skills': required, 'missing_payloads': missing,
            'payloads_prepared': prepared, 'pending_clean_approval': [],
            'audit_error': error, 'device_verified': False,
            'note': 'Source payload check only. Every installation still requires a fresh complete local scanner pass.'}


def require_core_only(repo_root):
    _bundle(_path(repo_root), CORE_NAMES)
    return list(CORE_NAMES)


def require_baseline(repo_root):
    result = baseline_plan(repo_root)
    if not result['payloads_prepared']:
        raise ValueError('Full advisor baseline is not ready: ' +
                         (', '.join(result['missing_payloads']) or str(result['audit_error'])))
    return result


def _read_receipt(path, root, skills, allow_relocation=False):
    if not path.exists():
        return None
    receipt = _json(path)
    if receipt.get('schema_version') not in (1, 2, 3) or (
        not allow_relocation and receipt.get('source_root') != str(root)
    ) or receipt.get('skills_root') != str(skills):
        raise ValueError('Unknown receipt or moved source checkout/skills root')
    components = receipt.get('components')
    if not isinstance(components, list) or not components:
        raise ValueError('Malformed installed receipt')
    names = [item.get('name') for item in components if isinstance(item, dict)]
    if len(names) != len(components) or len(set(names)) != len(names):
        raise ValueError('Duplicate or invalid receipt components')
    return receipt


def _preflight_targets(skills, components, receipt, state):
    old = {x['name']: x for x in receipt['components']} if receipt else {}
    if set(old) - {c['name'] for c in components}:
        raise ValueError('Removing managed skills requires separate migration')
    snapshots = {}
    for c in components:
        name = c['name']
        target = _path(skills / name)
        snapshot = _path(state / 'snapshots' / name)
        if target.exists():
            current = _files(target)
            if name in old and snapshot.exists():
                if current != _files(snapshot):
                    raise ValueError('Installed skill modified locally: ' + name)
            elif name in old:
                if (old[name].get('version') != c['version']
                        or old[name].get('source') != c['source']
                        or current != c['installed_files']):
                    raise ValueError('Legacy installation needs manual reconciliation: ' + name)
            elif current != c['installed_files']:
                raise ValueError('Unmanaged skill conflict: ' + name)
            snapshots[name] = current
        elif name in old:
            raise ValueError('Managed skill is missing: ' + name)
        else:
            snapshots[name] = None
        if not target.exists() and snapshot.exists():
            raise ValueError('Orphaned skill snapshot: ' + name)
    return snapshots


def _verify_upstream(components):
    checked, updates = {}, []
    for c in components:
        repo = c.get('upstream_repository')
        if not repo:
            continue
        if c.get('upstream_ref') != 'HEAD':
            raise ValueError('Invalid upstream freshness configuration: ' + c['name'])
        if repo not in checked:
            result = subprocess.run(['git', 'ls-remote', repo, 'HEAD'],
                                    capture_output=True, text=True, timeout=60)
            if result.returncode or not re.fullmatch(r'[a-f0-9]{40}\s+HEAD\s*', result.stdout):
                raise ValueError('Cannot check official upstream HEAD for ' + c['name'])
            checked[repo] = result.stdout.split()[0]
        if checked[repo] != c['version']:
            updates.append({'name': c['name'], 'installed_revision': c['version'],
                            'latest_revision': checked[repo]})
    return updates


def _save_json(path, obj):
    fd, tmp = tempfile.mkstemp(prefix='.advisor-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(obj, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def install_bundle(repo_root, skills_root, home, scanner=None, selected_names=None, host='codex'):
    root, skills, home = map(_path, (repo_root, skills_root, home))
    manifest, components, _ = _bundle(root, selected_names)
    state = _path(home / host_profiles.state_subdir(host))
    receipt_file = state / 'receipt.json'
    old = _read_receipt(receipt_file, root, skills, allow_relocation=True)
    old_receipt_bytes = receipt_file.read_bytes() if receipt_file.exists() else None
    preflight = _preflight_targets(skills, components, old, state)
    state.mkdir(parents=True, exist_ok=True)
    lock = state / 'install.lock'
    try:
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError as exc:
        raise ValueError('An advisor installation is already in progress') from exc
    os.close(fd)
    try:
        scanner_meta = _scanner_executable(scanner)
        updates = _verify_upstream(components)
        skills.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.advisor-stage-', dir=skills.parent) as tmp:
            root_stage = Path(tmp)
            payloads = root_stage / 'payloads'
            backups = root_stage / 'backups'
            saved_backups = root_stage / 'saved-backups'
            for directory in (payloads, backups, saved_backups):
                directory.mkdir()
            warnings = []
            # Scan the complete selected batch before changing any active skill.
            for c in components:
                name = c['name']
                staged = payloads / name
                shutil.copytree(_inside(root, c['path']), staged)
                for extra in c.get('extra_files', []):
                    target = _inside(staged, extra['destination'])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(_inside(root, extra['source']), target)
                if _files(staged) != c['installed_files']:
                    raise ValueError('Staged skill changed before scan: ' + name)
                warnings.extend(_scan(staged, scanner_meta, c['installed_files']))
                if _files(staged) != c['installed_files']:
                    raise ValueError('Staged skill changed during scan: ' + name)
            if _bundle(root, selected_names)[1] != components:
                raise ValueError('Source changed during scan')
            if _preflight_targets(skills, components, old, state) != preflight:
                raise ValueError('Installed files changed during scan')
            if (receipt_file.read_bytes() if receipt_file.exists() else None) != old_receipt_bytes:
                raise ValueError('Receipt changed during scan')
            receipt = {
                'schema_version': 3, 'bundle_version': manifest['bundle_version'],
                'installed_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                'source_root': str(root), 'skills_root': str(skills), 'scanner': scanner_meta,
                'components': [{'name': c['name'], 'version': c['version'],
                                'source': c['source']} for c in components],
                'selected_names': list(selected_names) if selected_names is not None else None,
                'verification': 'fresh static scan and direct file comparison; no historical audit ledger'
            }
            snapshot_dir = state / 'snapshots'
            snapshot_dir.mkdir(parents=True, exist_ok=True)
            changed, moved, snapshots_written, snapshots_moved = [], [], [], []
            try:
                for c in components:
                    name = c['name']
                    if preflight[name] == c['installed_files']:
                        continue
                    destination = _path(skills / name)
                    if destination.exists():
                        os.replace(destination, backups / name)
                        moved.append(name)
                    skills.mkdir(parents=True, exist_ok=True)
                    os.replace(payloads / name, destination)
                    changed.append(name)
                for c in components:
                    if _files(skills / c['name']) != c['installed_files']:
                        raise ValueError('Installed payload differs from scanned bytes')
                for c in components:
                    name = c['name']
                    saved = snapshot_dir / name
                    if saved.exists():
                        os.replace(saved, saved_backups / name)
                        snapshots_moved.append(name)
                    shutil.copytree(skills / name, saved)
                    snapshots_written.append(name)
                _save_json(receipt_file, receipt)
            except Exception:
                if old_receipt_bytes is None:
                    receipt_file.unlink(missing_ok=True)
                else:
                    receipt_file.write_bytes(old_receipt_bytes)
                for name in reversed(snapshots_written):
                    shutil.rmtree(snapshot_dir / name)
                for name in reversed(snapshots_moved):
                    os.replace(saved_backups / name, snapshot_dir / name)
                for name in reversed(changed):
                    shutil.rmtree(skills / name)
                for name in reversed(moved):
                    os.replace(backups / name, skills / name)
                raise
        return {
            'ready': True, 'receipt': str(receipt_file), 'components': [c['name'] for c in components],
            'scanner': scanner_meta, 'warnings': warnings, 'updates_available': updates,
            'full_bundle_ready': len(components) == len(manifest['components']),
            'legacy_receipt_migrated': old is not None and old.get('schema_version') != 3,
            'live_invocation_verified': False
        }
    finally:
        lock.unlink(missing_ok=True)


def check_bundle(repo_root, skills_root, home, host='codex'):
    try:
        root, skills, home = map(_path, (repo_root, skills_root, home))
        state = _path(home / host_profiles.state_subdir(host))
        if (state / 'install.lock').exists():
            raise ValueError('An advisor installation is in progress')
        receipt = _read_receipt(state / 'receipt.json', root, skills)
        if receipt is None or receipt.get('schema_version') != 3:
            raise ValueError('Install again to migrate the legacy receipt or create a new one')
        manifest, components, _ = _bundle(root, receipt.get('selected_names'))
        if receipt.get('bundle_version') != manifest['bundle_version']:
            raise ValueError('Installed bundle differs from manifest')
        indexed = {c['name']: c for c in receipt['components']}
        if set(indexed) != {c['name'] for c in components}:
            raise ValueError('Installed components differ from manifest')
        for c in components:
            if indexed[c['name']].get('version') != c['version'] or indexed[c['name']].get('source') != c['source']:
                raise ValueError('Installed skill revision differs from manifest')
            if (_files(skills / c['name']) != c['installed_files'] or
                    _files(state / 'snapshots' / c['name']) != c['installed_files']):
                raise ValueError('Installed skill differs from saved source: ' + c['name'])
        return {'ready': True, 'errors': [], 'components': list(indexed),
                'full_bundle_ready': len(components) == len(manifest['components']),
                'live_invocation_verified': False}
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {'ready': False, 'errors': [str(exc)], 'live_invocation_verified': False}
