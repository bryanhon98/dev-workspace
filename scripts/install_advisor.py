"""Install the curated advisor bundle after complete local static scans.

This module never invokes installed skills, executes their scripts, or restores
global instructions. setup.py owns instruction setup and the user-facing CLI.
"""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import venv


SCANNER_REVISION = 'cf5cac7ba5c756a6e0ebf52dc9763f49422f889f'
SCANNER_VERSION = '2.12.0'
SCANNER_REVIEW = 'audits/skillspector-cf5cac7-20261018/review.json'
EXCEPTIONS = {
    'grilling': 'matt-pocock-49dd158-20261018-user-approved',
    'find-skills': 'find-skills-13e4063-20261018-user-approved',
}
SHARED_LICENSE = {
    'source': 'skills/external/matt-pocock/LICENSE',
    'destination': 'LICENSE',
    'sha256': '0e7ac423bf2c6e223b7c5b156f8cf72da49d748e56a1641402c31f22ad07dbb5',
}


def _path(value):
    path = Path(os.path.abspath(os.fspath(value)))
    for item in [*reversed(path.parents), path]:
        if item.is_symlink():
            raise ValueError('Refusing symlink path: ' + str(item))
    return path


def _relative(value):
    if not isinstance(value, str) or not value or '\\' in value:
        raise ValueError('Invalid relative path')
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in ('', '.', '..') for p in value.split('/')) or ':' in value:
        raise ValueError('Unsafe relative path: ' + value)
    return value


def _inside(root, relative):
    return _path(root / _relative(relative))


def _json(path):
    try:
        value = json.loads(_path(path).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError('Cannot read valid JSON: ' + str(path)) from exc
    if not isinstance(value, dict):
        raise ValueError('Expected JSON object: ' + str(path))
    return value


def _sha(path):
    return hashlib.sha256(_path(path).read_bytes()).hexdigest()


def _hashes(directory):
    directory = _path(directory)
    if not directory.is_dir():
        raise ValueError('Missing payload directory: ' + str(directory))
    result = {}
    for path in sorted(directory.rglob('*')):
        _path(path)
        if path.is_file():
            result[path.relative_to(directory).as_posix()] = _sha(path)
        elif not path.is_dir():
            raise ValueError('Unsupported payload file: ' + str(path))
    return result


def _hash_map(value):
    if not isinstance(value, dict) or not value:
        raise ValueError('Missing complete payload hashes')
    for name, digest in value.items():
        _relative(name)
        if not isinstance(digest, str) or not re.fullmatch('[a-f0-9]{64}', digest):
            raise ValueError('Invalid payload hash: ' + name)
    return value


def _canonical_url(value):
    return str(value).rstrip('/').removesuffix('.git').lower()


def _signature(issue):
    if not isinstance(issue, dict):
        raise ValueError('Malformed scan finding')
    location = issue.get('location')
    if not isinstance(location, dict):
        raise ValueError('Malformed scan finding location')
    required = ['id', 'severity', 'finding']
    if any(not isinstance(issue.get(k), str) or not issue[k] for k in required):
        raise ValueError('Missing scan finding identity')
    if 'match_fingerprint' not in issue or (issue['match_fingerprint'] is not None
                                           and not isinstance(issue['match_fingerprint'], str)):
        raise ValueError('Malformed scan finding fingerprint')
    filename = _relative(location.get('file'))
    return (issue['id'], issue['severity'], issue['finding'],
            filename, location.get('start_line'), location.get('end_line'),
            location.get('start_column'), issue['match_fingerprint'])


def _audit(root, component, scanner):
    audit = _json(_inside(root, component['audit_ref']))
    expected = component['hashes']
    exception = component.get('exception')
    if exception:
        name = component['name']
        if (not isinstance(exception, dict)
                or EXCEPTIONS.get(name) != exception.get('ref')):
            raise ValueError('Unknown exception approval: ' + name)
        review = _json(_inside(root, exception['review']))
        if (review.get('exception_ref') != exception['ref']
                or review.get('revision') != component['version']):
            raise ValueError('Exception approval or revision mismatch: ' + name)
        approval = review
        if name == 'find-skills' and not review.get('approval'):
            # This exact restore audit retained the original approval for
            # byte-identical content. Do not infer approval from a newer hash.
            if review.get('status') != 'installed-with-existing-approved-exception':
                raise ValueError('Missing retained exception approval: ' + name)
            approval = _json(root / 'audits/find-skills-13e4063-20261018/review.json')
            if approval.get('sha256') != expected:
                raise ValueError('Original exception approval hashes changed: ' + name)
        if not approval.get('approval') or approval.get('exception_ref') != exception['ref']:
            raise ValueError('Missing explicit exception approval: ' + name)
        recorded = review.get('sha256', {})
        if name == 'grilling':
            recorded = {p[len('grilling/'):]: h for p, h in recorded.items() if p.startswith('grilling/')}
        if recorded != expected:
            raise ValueError('Exception payload hashes changed: ' + name)
        report = _json(_inside(root, exception['report']))
        issues = report.get('issues')
        if not isinstance(issues, list) or not issues:
            raise ValueError('Missing historical exception findings: ' + name)
        return sorted(_signature(i) for i in issues)
    if audit.get('status') != 'reviewed-static':
        raise ValueError('Skill audit is not approved for activation: ' + component['name']
                         + ' (status: ' + str(audit.get('status', 'missing'))
                         + '); see ' + component['audit_ref'])
    if audit.get('sha256') != expected:
        raise ValueError('Skill audit payload hashes mismatch: ' + component['name'])
    pin = audit.get('scanner', {})
    if pin.get('revision') != scanner['revision'] or pin.get('version') != scanner['version']:
        raise ValueError('Skill audit scanner pin mismatch: ' + component['name'])
    return []


def _bundle(root):
    manifest = _json(root / 'advisor-bundle.json')
    if manifest.get('schema_version') != 1 or not isinstance(manifest.get('bundle_version'), str):
        raise ValueError('Unknown advisor bundle manifest')
    scanner = manifest.get('scanner', {})
    if (scanner.get('revision') != SCANNER_REVISION or scanner.get('version') != SCANNER_VERSION
            or _canonical_url(scanner.get('source_url')) != 'https://github.com/nvidia/skillspector'):
        raise ValueError('Scanner pin has no supported source review')
    _inside(root, scanner.get('constraints')).read_bytes()
    review = _json(root / SCANNER_REVIEW)
    if (review.get('revision') != scanner['revision'] or review.get('version') != scanner['version']
            or review.get('audit_status') != 'source-reviewed-runtime-verified'):
        raise ValueError('Missing reviewed scanner bootstrap provenance')
    components = manifest.get('components')
    if not isinstance(components, list) or not components:
        raise ValueError('Empty or malformed advisor bundle')
    names = set()
    prepared = []
    for item in components:
        if not isinstance(item, dict):
            raise ValueError('Malformed component')
        name = item.get('name', '')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
            raise ValueError('Invalid or duplicate component name')
        names.add(name)
        hashes = _hash_map(item.get('hashes'))
        source = _inside(root, item.get('path'))
        if _hashes(source) != hashes or 'SKILL.md' not in hashes:
            raise ValueError('Complete source payload hash mismatch: ' + name)
        if not isinstance(item.get('version'), str) or not isinstance(item.get('source'), str):
            raise ValueError('Missing component source/version: ' + name)
        installed = dict(hashes)
        extras = item.get('extra_files', [])
        if not isinstance(extras, list):
            raise ValueError('Malformed extra files: ' + name)
        for extra in extras:
            destination = _relative(extra['destination'])
            if name != 'grilling' or extra != SHARED_LICENSE:
                raise ValueError('Extra files need their own source audit; only the reviewed shared grilling license is supported')
            if destination in installed:
                raise ValueError('Duplicate extra-file destination: ' + destination)
            path = _inside(root, extra['source'])
            if _sha(path) != extra.get('sha256'):
                raise ValueError('Extra-file hash mismatch: ' + destination)
            installed[destination] = extra['sha256']
        prepared.append({**item, 'installed_hashes': installed,
                         'allowed_findings': _audit(root, item, scanner)})
    return manifest, prepared, review


def _read_receipt(path, root, skills, allow_relocation=False):
    if not path.exists():
        return None
    receipt = _json(path)
    if (receipt.get('schema_version') != 1 or not isinstance(receipt.get('source_root'), str)
            or (not allow_relocation and receipt['source_root'] != str(root))
            or receipt.get('skills_root') != str(skills)):
        raise ValueError('Unknown receipt or moved source checkout/skills root')
    components = receipt.get('components')
    if not isinstance(components, list) or not components:
        raise ValueError('Malformed installed receipt')
    names = set()
    for component in components:
        name = component.get('name', '')
        if not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
            raise ValueError('Invalid receipt component')
        names.add(name)
        _hash_map(component.get('hashes'))
        _relative(component.get('report'))
    return receipt


def _preflight_targets(skills, components, receipt):
    old = {c['name']: c for c in receipt['components']} if receipt else {}
    names = {c['name'] for c in components}
    if set(old) - names:
        raise ValueError('Removing a managed component needs an explicit migration')
    snapshots = {}
    for component in components:
        name = component['name']
        target = _path(skills / name)
        if target.exists():
            actual = _hashes(target)
            if name in old and actual != old[name]['hashes']:
                raise ValueError('Installed skill was modified locally: ' + name)
            if name not in old and actual != component['installed_hashes']:
                raise ValueError('Unmanaged skill conflict: ' + name)
            snapshots[name] = actual
        elif name in old:
            raise ValueError('Managed skill is missing; reconcile the local change: ' + name)
        else:
            snapshots[name] = None
    return snapshots


def _environment():
    return {**os.environ, 'LANGSMITH_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false'}


def _run(args, timeout=300):
    try:
        return subprocess.run([str(a) for a in args], text=True, capture_output=True,
                              env=_environment(), timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('Scanner command failed: ' + str(exc)) from exc


def _checked_run(args, timeout=300):
    result = _run(args, timeout)
    if result.returncode:
        raise ValueError('Scanner command failed: ' + result.stderr[-2000:])
    return result


def _scanner_command(executable, *arguments):
    python = Path(executable).parent / ('python.exe' if os.name == 'nt' else 'python')
    # Execute the verified package entrypoint, not an unchecked console wrapper.
    return [python, '-I', '-c', 'from skillspector.cli import app; app()', *arguments]


def _verify_scanner(executable, pin, review):
    executable = _path(executable)
    if not executable.is_file():
        raise ValueError('Scanner executable missing: ' + str(executable))
    python = executable.parent / ('python.exe' if os.name == 'nt' else 'python')
    # A venv's Python commonly is a symlink to the base interpreter. Do not
    # resolve it: doing so loses the venv's distribution metadata context.
    if not python.is_file():
        raise ValueError('Scanner needs a verifiable adjacent venv Python')
    program = (
        'import importlib.metadata as m,json,hashlib; '
        'd=m.distribution("skillspector"); '
        'print(json.dumps({"version":d.version,"direct_url":json.loads(d.read_text("direct_url.json") or "{}"),'
        '"hashes":{"src/skillspector/"+n:hashlib.sha256(d.locate_file("skillspector/"+n).read_bytes()).hexdigest() '
        'for n in ("__init__.py","cli.py")}}))'
    )
    result = _checked_run([python, '-I', '-c', program], 60)
    try:
        metadata = json.loads(result.stdout)
    except ValueError as exc:
        raise ValueError('Malformed scanner provenance') from exc
    direct = metadata.get('direct_url', {})
    if (metadata.get('version') != pin['version']
            or direct.get('vcs_info', {}).get('commit_id') != pin['revision']
            or _canonical_url(direct.get('url')) != _canonical_url(pin['source_url'])):
        raise ValueError('Scanner version/source revision provenance mismatch')
    for filename in ['src/skillspector/__init__.py', 'src/skillspector/cli.py']:
        if metadata.get('hashes', {}).get(filename) != review.get('source_hashes', {}).get(filename):
            raise ValueError('Scanner reviewed source hash mismatch: ' + filename)
    version = _checked_run(_scanner_command(executable, '--version'), 60).stdout
    if version.strip() != 'SkillSpector v' + pin['version']:
        raise ValueError('Scanner CLI version mismatch')
    return {'path': str(executable), 'version': pin['version'], 'revision': pin['revision'],
            'source_url': pin['source_url'], 'hashes': metadata['hashes']}


def _prepare_scanner(root, state, scanner, pin, review):
    if scanner is not None:
        return _verify_scanner(scanner, pin, review)
    environment = _path(state / 'scanner')
    executable = environment / ('Scripts/skillspector.exe' if os.name == 'nt' else 'bin/skillspector')
    if executable.exists():
        return _verify_scanner(executable, pin, review)
    if environment.exists():
        raise ValueError('Incomplete managed scanner environment; inspect before retrying')
    if not (3, 12) <= sys.version_info[:2] < (3, 15):
        raise ValueError('Scanner bootstrap requires Python 3.12, 3.13 or 3.14')
    python = environment / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    package = 'git+' + pin['source_url'].removesuffix('.git') + '.git@' + pin['revision']
    constraints = _inside(root, pin['constraints'])
    uv = shutil.which('uv')
    try:
        if uv:
            _checked_run([uv, 'venv', '--python', sys.executable, environment])
            _checked_run([uv, 'pip', 'install', '--python', python, '--constraint', constraints, package], 900)
            _checked_run([uv, 'pip', 'check', '--python', python])
        else:
            venv.EnvBuilder(with_pip=True).create(environment)
            _checked_run([python, '-m', 'pip', 'install', '--constraint', constraints, package], 900)
            _checked_run([python, '-m', 'pip', 'check'])
        return _verify_scanner(executable, pin, review)
    except Exception:
        # This directory was created by this call; never remove pre-existing
        # environments when they fail verification.
        if environment.exists() and not environment.is_symlink():
            shutil.rmtree(environment)
        raise


def _validate_report(report, component):
    complete = report.get('analysis_completeness', {})
    metadata = report.get('metadata', {})
    if not isinstance(complete, dict) or not isinstance(metadata, dict):
        raise ValueError('Malformed scan completeness or metadata section')
    if (report.get('execution_successful') is not True
            or complete.get('execution_successful') is not True
            or complete.get('is_complete') is not True
            or isinstance(complete.get('coverage_percent'), bool)
            or complete.get('coverage_percent') != 100
            or metadata.get('llm_requested') is not False
            or metadata.get('skillspector_version') != SCANNER_VERSION
            or report.get('suppressed_count') != 0 or report.get('suppressed') != []):
        raise ValueError('Scan is incomplete, suppressed, or not verified static-only: ' + component['name'])
    if any(complete.get(k) not in (0, []) for k in [
            'partially_inspected_files', 'entirely_uninspected_files',
            'ledger_exceptions', 'scope_exclusions', 'limitations']):
        raise ValueError('Scan coverage contains omissions: ' + component['name'])
    files = set(component['installed_hashes'])
    scanned = report.get('components')
    if not isinstance(scanned, list):
        raise ValueError('Scan component coverage missing')
    paths = [_relative(c.get('path')) for c in scanned if isinstance(c, dict)]
    if len(paths) != len(scanned) or len(paths) != len(set(paths)) or set(paths) != files:
        raise ValueError('Scan component coverage does not match complete payload')
    if any(complete.get(k) != len(files) for k in ['total_components', 'scanned_components', 'fully_inspected_files']):
        raise ValueError('Scan component count mismatch')
    issues = report.get('issues')
    if not isinstance(issues, list):
        raise ValueError('Scan findings missing')
    signatures = sorted(_signature(i) for i in issues)
    if signatures != component['allowed_findings']:
        raise ValueError('New or changed scan findings require specific review: ' + component['name'])


def _atomic_json(path, value):
    fd, temporary = tempfile.mkstemp(prefix='.advisor-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        _path(path)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def install_bundle(repo_root, skills_root, codex_home, scanner=None):
    """Stage and scan a complete bundle, then commit files with rollback.

    Raises ValueError/OSError on blocked review, scanner or filesystem failures.
    A ready receipt establishes checked files, not a live model invocation.
    """
    root, skills, home = map(_path, (repo_root, skills_root, codex_home))
    manifest, components, review = _bundle(root)
    state = _path(home / 'dev-workspace-advisor')
    receipt_path = state / 'receipt.json'
    receipt = _read_receipt(receipt_path, root, skills, allow_relocation=True)
    snapshots = _preflight_targets(skills, components, receipt)
    before = receipt_path.read_bytes() if receipt_path.exists() else None
    state.mkdir(parents=True, exist_ok=True)
    lock = _path(state / 'install.lock')
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise ValueError('An advisor installation is already in progress') from exc
    os.close(fd)
    try:
        scanner_meta = _prepare_scanner(root, state, scanner, manifest['scanner'], review)
        skills.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.advisor-stage-', dir=skills.parent) as temporary:
            staging = Path(temporary)
            payloads, backups = staging / 'payloads', staging / 'backups'
            payloads.mkdir()
            backups.mkdir()
            reports = {}
            for component in components:
                name = component['name']
                destination = payloads / name
                shutil.copytree(_inside(root, component['path']), destination)
                for extra in component.get('extra_files', []):
                    target = _inside(destination, extra['destination'])
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(_inside(root, extra['source']), target)
                if _hashes(destination) != component['installed_hashes']:
                    raise ValueError('Staged payload changed: ' + name)
                output = staging / (name + '.json')
                result = _run(_scanner_command(scanner_meta['path'], 'scan', destination, '--no-llm', '--format', 'json',
                               '--output', output, '--fail-on-incomplete', '--min-coverage', '100', '--fail-on-findings'))
                if result.returncode not in (0, 1):
                    raise ValueError('Scanner execution failed for ' + name + ': ' + result.stderr[-1500:])
                report = _json(output)
                _validate_report(report, component)
                if result.returncode != (1 if report['issues'] else 0):
                    raise ValueError('Scanner exit status disagrees with the verified report: ' + name)
                if _hashes(destination) != component['installed_hashes']:
                    raise ValueError('Payload changed during scan: ' + name)
                reports[name] = report
            # Recheck all sources and destinations after the potentially long scans.
            current_manifest, current_components, _ = _bundle(root)
            if current_manifest != manifest or current_components != components:
                raise ValueError('Bundle source changed during installation')
            if _preflight_targets(skills, components, receipt) != snapshots:
                raise ValueError('Installed files changed during installation')
            if (receipt_path.read_bytes() if receipt_path.exists() else None) != before:
                raise ValueError('Installation receipt changed concurrently')
            report_root = _path(state / 'reports' / uuid.uuid4().hex)
            report_root.mkdir(parents=True)
            installed = []
            for component in components:
                name = component['name']
                report_path = report_root / (name + '.json')
                _atomic_json(report_path, reports[name])
                installed.append({'name': name, 'version': component['version'], 'source': component['source'],
                                  'hashes': component['installed_hashes'], 'audit_ref': component['audit_ref'],
                                  'report': report_path.relative_to(state).as_posix(), 'report_sha256': _sha(report_path),
                                  'exception_ref': (component.get('exception') or {}).get('ref')})
            new_receipt = {'schema_version': 1, 'bundle_version': manifest['bundle_version'],
                           'source_root': str(root), 'skills_root': str(skills),
                           'manifest_sha256': _sha(root / 'advisor-bundle.json'),
                           'scanner': scanner_meta, 'components': installed,
                           'verification': 'static scans and complete file hashes; live host invocation untested'}
            changed, moved = [], []
            skills.mkdir(parents=True, exist_ok=True)
            try:
                for component in components:
                    name = component['name']
                    if snapshots[name] == component['installed_hashes']:
                        continue
                    target = _path(skills / name)
                    if target.exists():
                        os.replace(target, backups / name)
                        moved.append(name)
                    os.replace(payloads / name, target)
                    changed.append(name)
                for component in components:
                    if _hashes(skills / component['name']) != component['installed_hashes']:
                        raise ValueError('Installed payload verification failed')
                _atomic_json(receipt_path, new_receipt)
            except Exception:
                for name in reversed(changed):
                    shutil.rmtree(_path(skills / name))
                for name in reversed(moved):
                    os.replace(backups / name, skills / name)
                raise
        return {'ready': True, 'errors': [], 'receipt': str(receipt_path), 'scanner': scanner_meta,
                'components': [c['name'] for c in components], 'live_invocation_verified': False}
    finally:
        lock.unlink(missing_ok=True)


def check_bundle(repo_root, skills_root, codex_home):
    """Read-only validation of current source, receipt, reports and installation."""
    try:
        root, skills, home = map(_path, (repo_root, skills_root, codex_home))
        manifest, components, review = _bundle(root)
        state = _path(home / 'dev-workspace-advisor')
        if (state / 'install.lock').exists():
            raise ValueError('An advisor installation is in progress')
        receipt = _read_receipt(state / 'receipt.json', root, skills)
        if receipt is None:
            raise ValueError('Advisor installation receipt is missing')
        if (receipt.get('manifest_sha256') != _sha(root / 'advisor-bundle.json')
                or receipt.get('bundle_version') != manifest['bundle_version']):
            raise ValueError('Installed bundle differs from the current source manifest')
        recorded = {c['name']: c for c in receipt['components']}
        if set(recorded) != {c['name'] for c in components}:
            raise ValueError('Receipt does not cover the current bundle')
        for component in components:
            item = recorded[component['name']]
            if (item['hashes'] != component['installed_hashes'] or item.get('version') != component['version']
                    or item.get('source') != component['source']):
                raise ValueError('Receipt/source mismatch: ' + component['name'])
            if _hashes(skills / component['name']) != item['hashes']:
                raise ValueError('Installed skill changed or missing: ' + component['name'])
            report_path = _inside(state, item['report'])
            if _sha(report_path) != item.get('report_sha256'):
                raise ValueError('Saved scan report changed')
            _validate_report(_json(report_path), component)
        scanner = receipt.get('scanner', {})
        current = _verify_scanner(scanner.get('path', ''), manifest['scanner'], review)
        if current != scanner:
            raise ValueError('Installed scanner receipt/provenance mismatch')
        return {'ready': True, 'errors': [], 'receipt': str(state / 'receipt.json'),
                'components': list(recorded), 'live_invocation_verified': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {'ready': False, 'errors': [str(exc)], 'live_invocation_verified': False}
