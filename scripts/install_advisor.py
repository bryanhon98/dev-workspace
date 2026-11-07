"""Install the curated advisor bundle after risk-triaged local static scans.

This module never invokes installed skills, executes their scripts, or restores
global instructions. setup.py owns instruction setup and the user-facing CLI.
"""
import hashlib
from datetime import datetime, timezone
import socket
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

# Add scripts directory to path for local imports when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

import host_profiles


SCANNER_REVISION = 'cf5cac7ba5c756a6e0ebf52dc9763f49422f889f'
SCANNER_VERSION = '2.12.0'
SCANNER_REVIEW = 'audits/skillspector-cf5cac7-20261018/review.json'
EXCEPTIONS = {
    'tool-advisor': 'tool-advisor-1.0.0-20261102-LP3-user-approved',
    'grilling': 'matt-pocock-49dd158-20261018-user-approved',
    'find-skills': 'find-skills-13e4063-20261018-user-approved',
}
CORE_NAMES = ('tool-advisor', 'grilling', 'find-skills')
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


def _approval_records(root, manifest):
    """Load the small shared approval ledger. Historical reports stay archived."""
    ref = manifest.get('approvals_ref')
    if ref is None:
        return None  # explicitly legacy bundle (tests/older checkouts)
    if ref != 'skill-approvals.json':
        raise ValueError('Unsupported skill approval record location')
    path = root / ref
    if not path.exists():
        raise ValueError('Required skill approval records are missing')
    data = _json(path)
    if data.get('schema_version') != 1 or not isinstance(data.get('skills'), list):
        raise ValueError('Malformed skill approval record')
    items = data['skills']
    expected = {c['name'] for c in manifest['components']}
    names = [c.get('name') for c in items if isinstance(c, dict)]
    if len(names) != len(items) or len(set(names)) != len(names) or set(names) != expected:
        raise ValueError('Skill approval records do not cover the exact bundle')
    for item in items:
        if (not isinstance(item.get('version'), str) or not item['version']
                or not isinstance(item.get('source'), str)
                or item.get('approval') not in ('historical-reviewed', 'manual-reviewed', 'clean-auto')
                or item.get('scan') not in ('historical-triaged', 'triaged', 'clean')
                or (item['approval'] == 'clean-auto' and item['scan'] != 'clean')
                or (item['approval'] == 'historical-reviewed' and item['scan'] != 'historical-triaged')
                or (item['approval'] == 'manual-reviewed' and item['scan'] != 'triaged')
                or (item.get('upstream_repository') is not None and not isinstance(item['upstream_repository'], str))
                or (item.get('approved_at') is not None and not isinstance(item['approved_at'], str))
                or (item['approval'] == 'clean-auto' and not re.fullmatch(
                    r'[a-f0-9]{64}', item.get('payload_digest', '')))):
            raise ValueError('Invalid skill approval entry: ' + str(item.get('name')))
    return {item['name']: item for item in items}


def _payload_digest(component):
    """Single internal fingerprint; not a second per-file approval manifest."""
    value = json.dumps(component['hashes'], sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(value).hexdigest()


def _approval_for(root, component, scanner, approvals):
    """Old revisions use original triage; changed versions require clean scans."""
    if approvals is None:
        return {**_audit(root, component, scanner), 'pending_clean_approval': False}
    name, entry = component['name'], approvals[component['name']]
    if entry.get('upstream_repository') != component.get('upstream_repository'):
        raise ValueError('Approved upstream repository changed: ' + name)
    if entry['version'] != component['version']:
        upstream = component.get('upstream_repository')
        if upstream:
            expected = upstream.removesuffix('.git') + '/tree/' + component['version']
            if not (component['source'] == expected
                    or component['source'].startswith(expected + '/')):
                raise ValueError('Updated skill source does not match its upstream revision: ' + name)
        elif component['source'] != entry['source']:
            raise ValueError('Custom skill source changed without explicit review: ' + name)
        return {'allowed_findings': [], 'warnings': [], 'pending_clean_approval': True}
    if entry['source'] != component['source']:
        raise ValueError('Approved source changed without version update: ' + name)
    if entry['approval'] == 'clean-auto':
        if entry['payload_digest'] != _payload_digest(component):
            raise ValueError('Approved payload changed without version update: ' + name)
        return {'allowed_findings': [], 'warnings': [], 'pending_clean_approval': False}
    return {**_audit(root, component, scanner), 'pending_clean_approval': False}


def _record_clean_approvals(root, components):
    path = root / 'skill-approvals.json'
    value = _json(path)
    by_name = {x['name']: x for x in value['skills']}
    stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    for component in components:
        item = by_name[component['name']]
        item.update(version=component['version'], source=component['source'],
                    approved_at=stamp, approval='clean-auto', scan='clean',
                    payload_digest=_payload_digest(component))
        item.pop('audit_ref', None)
    _atomic_json(path, value)


def _audit(root, component, scanner):
    audit = _json(_inside(root, component['audit_ref']))
    expected = component['hashes']
    exception = component.get('exception')
    if audit.get('status') == 'triaged-static':
        return _triaged_audit(root, component, scanner, audit)
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
        report_path = _inside(root, exception['report'])
        if name == 'tool-advisor':
            if (audit.get('status') != 'reviewed-with-user-exception'
                    or audit.get('sha256') != expected
                    or audit.get('exception_ref') != exception['ref']):
                raise ValueError('Advisor source review or payload hashes do not match the approval')
            pin = audit.get('scanner', {})
            if pin.get('revision') != scanner['revision'] or pin.get('version') != scanner['version']:
                raise ValueError('Advisor source review scanner pin mismatch')
            if (review.get('report_ref') != exception['report']
                    or review.get('report_sha256') != _sha(report_path)):
                raise ValueError('Approved advisor finding report changed')
        report = _json(report_path)
        issues = report.get('issues')
        if not isinstance(issues, list) or not issues:
            raise ValueError('Missing historical exception findings: ' + name)
        return {'allowed_findings': _signatures(issues), 'warnings': []}
    if audit.get('status') != 'reviewed-static':
        raise ValueError('Skill audit is not approved for activation: ' + component['name']
                         + ' (status: ' + str(audit.get('status', 'missing'))
                         + '); see ' + component['audit_ref'])
    if audit.get('sha256') != expected:
        raise ValueError('Skill audit payload hashes mismatch: ' + component['name'])
    pin = audit.get('scanner', {})
    if pin.get('revision') != scanner['revision'] or pin.get('version') != scanner['version']:
        raise ValueError('Skill audit scanner pin mismatch: ' + component['name'])
    return {'allowed_findings': [], 'warnings': []}


def _signatures(issues):
    return sorted((_signature(issue) for issue in issues), key=repr)


def _decision(value, dispositions):
    if (not isinstance(value, dict) or value.get('disposition') not in dispositions
            or not isinstance(value.get('reason'), str) or not value['reason'].strip()):
        raise ValueError('Missing or unassessed risk triage decision')
    return value


def _triaged_audit(root, component, scanner, audit):
    name = component['name']
    if audit.get('sha256') != component['hashes'] or audit.get('revision') != component['version']:
        raise ValueError('Triaged audit payload hash or revision mismatch: ' + name)
    pin = audit.get('scanner')
    if (not isinstance(pin, dict) or pin.get('revision') != scanner['revision']
            or pin.get('version') != scanner['version']):
        raise ValueError('Triaged audit scanner pin mismatch: ' + name)
    report_path = _inside(root, audit.get('report_ref'))
    if audit.get('report_sha256') != _sha(report_path):
        raise ValueError('Triaged scan report hash mismatch: ' + name)
    report = _json(report_path)
    issues = report.get('issues')
    if not isinstance(issues, list):
        raise ValueError('Triaged scan findings missing: ' + name)
    signatures = _signatures(issues)
    decisions = audit.get('findings_decisions')
    if not isinstance(decisions, list):
        raise ValueError('Missing finding triage decisions: ' + name)
    approved, warnings = [], []
    for entry in decisions:
        entry = _decision(entry, {'warn', 'false-positive'})
        signature = entry.get('signature')
        if not isinstance(signature, list) or len(signature) != 8:
            raise ValueError('Malformed finding triage signature: ' + name)
        approved.append(tuple(signature))
        warnings.append({'component': name, 'kind': 'finding', **entry})
    if sorted(approved, key=repr) != signatures:
        raise ValueError('Every exact finding requires targeted risk triage: ' + name)
    coverage = _decision(audit.get('coverage_decision'), {'warn', 'complete'})
    profile = audit.get('analysis_completeness')
    if not isinstance(profile, dict) or profile != report.get('analysis_completeness'):
        raise ValueError('Triaged coverage does not match the pinned report: ' + name)
    if (coverage['disposition'] == 'complete') != (profile.get('is_complete') is True):
        raise ValueError('Coverage decision misrepresents scan completeness: ' + name)
    if coverage['disposition'] == 'warn':
        warnings.append({'component': name, 'kind': 'coverage', **coverage})
    result = {'allowed_findings': signatures, 'accepted_scan_profile': profile, 'warnings': warnings}
    _validate_report(report, {**component, **result})
    return result


def _bundle(root, selected_names=None):
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
    selection = None
    if selected_names is not None:
        if (not isinstance(selected_names, (list, tuple)) or not selected_names
                or any(not isinstance(n, str) for n in selected_names)
                or len(set(selected_names)) != len(selected_names)):
            raise ValueError('Invalid selected component names')
        selection = set(selected_names)
    approvals = _approval_records(root, manifest)
    names = set()
    prepared = []
    for item in components:
        if not isinstance(item, dict):
            raise ValueError('Malformed component')
        name = item.get('name', '')
        if not isinstance(name, str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
            raise ValueError('Invalid or duplicate component name')
        names.add(name)
        if selection is not None and name not in selection:
            continue
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
        component = {**item, 'installed_hashes': installed}
        prepared.append({**component, **_approval_for(root, component, scanner, approvals)})
    if selection is not None and names & selection != selection:
        raise ValueError('Selected component is missing from bundle')
    return manifest, prepared, review


def baseline_plan(repo_root):
    """Read-only list of selected baseline payloads, not a device readiness claim."""
    root = _path(repo_root)
    baseline = _json(root / 'advisor-baseline.json')
    required = baseline.get('required_skills')
    if (baseline.get('schema_version') != 1 or not isinstance(required, list)
            or not required or any(not isinstance(n, str) or
               not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', n) for n in required)
            or len(required) != len(set(required))):
        raise ValueError('Invalid required advisor baseline skills')
    manifest = _json(root / 'advisor-bundle.json')
    components = manifest.get('components')
    if not isinstance(components, list) or any(not isinstance(c, dict) for c in components):
        raise ValueError('Invalid advisor bundle components')
    names = [c.get('name') for c in components]
    if (any(not isinstance(n, str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', n) for n in names)
            or len(set(names)) != len(names)):
        raise ValueError('Invalid or duplicate advisor bundle component names')
    packaged = set(names)
    missing = [name for name in required if name not in packaged]
    audit_error = None
    pending = []
    try:
        _, staged, _ = _bundle(root)
        pending = [c['name'] for c in staged if c.get('pending_clean_approval')]
    except (ValueError, OSError, KeyError, TypeError) as exc:
        audit_error = str(exc)
    return {'required_skills': required, 'missing_payloads': missing,
            'payloads_prepared': not missing and audit_error is None,
            'pending_clean_approval': pending,
            'audit_error': audit_error, 'device_verified': False,
            'note': 'Setup selects all baseline skills; missing or blocked source preparation prevents full setup. No device or live invocation verified.'}


def require_core_only(repo_root):
    """Select the explicit three-skill core even when the full bundle grows."""
    _bundle(_path(repo_root), selected_names=CORE_NAMES)
    return list(CORE_NAMES)


def require_baseline(repo_root):
    plan = baseline_plan(repo_root)
    if not plan['payloads_prepared']:
        raise ValueError('Full advisor baseline is not ready; prepare scanned and risk-triaged payloads before setup: '
                         + (', '.join(plan['missing_payloads']) or plan['audit_error'])
                         + '. See --plan-advisor and audits/advisor-baseline-20261103/review.json. '
                         + 'A core-only install is available explicitly via --install-advisor-core; it is not full setup.')
    return plan


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
        if not isinstance(component, dict):
            raise ValueError('Malformed installed receipt component')
        name = component.get('name', '')
        if not isinstance(name, str) or not re.fullmatch('[a-z0-9]+(?:-[a-z0-9]+)*', name) or name in names:
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
            or metadata.get('llm_requested') is not False
            or metadata.get('meta_analysis_applied', False) is not False
            or metadata.get('inference_usage', []) != []
            or metadata.get('skillspector_version') != SCANNER_VERSION
            or type(report.get('suppressed_count')) is not int
            or report.get('suppressed_count') != 0 or report.get('suppressed') != []):
        raise ValueError('Scan is incomplete, suppressed, or not verified static-only: ' + component['name'])
    files = set(component['installed_hashes'])
    scanned = report.get('components')
    if not isinstance(scanned, list):
        raise ValueError('Scan component coverage missing')
    paths = [_relative(c.get('path')) for c in scanned if isinstance(c, dict)]
    if len(paths) != len(scanned) or len(paths) != len(set(paths)) or set(paths) != files:
        raise ValueError('Scan component coverage does not match complete payload')
    counts = ['total_components', 'scanned_components', 'fully_inspected_files',
              'partially_inspected_files', 'entirely_uninspected_files']
    if (any(type(complete.get(k)) is not int or complete[k] < 0 for k in counts)
            or complete['total_components'] != len(files)
            or complete['scanned_components'] != complete['fully_inspected_files']
            or complete['entirely_uninspected_files'] != 0
            or complete['fully_inspected_files'] + complete['partially_inspected_files'] != len(files)):
        raise ValueError('Scan component count mismatch or uninspected files')
    # SkillSpector counts only fully inspected files as scanned; partially
    # inspected files remain in total_components and the complete file listing.
    coverage = complete.get('coverage_percent')
    if (type(coverage) not in (int, float) or not 0 <= coverage <= 100
            or type(complete.get('is_complete')) is not bool
            or any(not isinstance(complete.get(k), list) for k in
                   ['ledger_exceptions', 'scope_exclusions', 'limitations'])):
        raise ValueError('Malformed scan coverage')
    if coverage != round(complete['fully_inspected_files'] / len(files) * 100, 1):
        raise ValueError('Scan coverage percentage disagrees with inspected file counts')
    has_omissions = (coverage != 100 or complete['fully_inspected_files'] != len(files)
                     or any(complete[k] for k in ['ledger_exceptions', 'scope_exclusions', 'limitations']))
    if complete['is_complete'] and has_omissions:
        raise ValueError('Scan completeness contradicts coverage omissions')
    profile = component.get('accepted_scan_profile')
    if profile is not None:
        if complete != profile:
            raise ValueError('New or changed scan coverage requires targeted risk triage: ' + component['name'])
    elif not complete['is_complete'] or has_omissions:
        raise ValueError('Scan coverage contains omissions: ' + component['name'])
    issues = report.get('issues')
    if not isinstance(issues, list):
        raise ValueError('Scan findings missing')
    for key in ('findings_before_filtering', 'findings_after_filtering'):
        if key in complete and (type(complete[key]) is not int or complete[key] != len(issues)):
            raise ValueError('Scan finding counts disagree or findings were filtered')
    signatures = _signatures(issues)
    if signatures != component['allowed_findings']:
        raise ValueError('New or changed scan findings require targeted risk triage: ' + component['name'])


def _verify_upstream(components):
    """Check selected official refs once per repository before fresh scans."""
    checked, available = {}, []
    for component in components:
        repository = component.get('upstream_repository')
        ref = component.get('upstream_ref')
        if repository is None and ref is None:
            continue
        if (not isinstance(repository, str) or not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?', repository)
                or ref != 'HEAD'):
            raise ValueError('Unsupported official upstream freshness pin: ' + component['name'])
        key = (repository, ref)
        if key not in checked:
            result = _run(['git', 'ls-remote', repository, ref], timeout=60)
            rows = result.stdout.strip().splitlines()
            if (result.returncode or len(rows) != 1
                    or not re.fullmatch(r'[a-f0-9]{40}\s+HEAD', rows[0])):
                raise ValueError('Cannot verify latest official upstream version: ' + component['name'])
            checked[key] = rows[0].split()[0]
        if checked[key] != component['version']:
            if component.get('pending_clean_approval'):
                raise ValueError('New auto-approved candidate must match upstream HEAD: '
                                 + component['name'] + ' (' + checked[key] + ')')
            available.append({'name': component['name'], 'approved_version': component['version'],
                              'latest_version': checked[key]})
    return available


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


def install_bundle(repo_root, skills_root, home, scanner=None, selected_names=None, host='codex'):
    """Stage and scan a complete bundle, then commit files with rollback.

    Raises ValueError/OSError on blocked review, scanner or filesystem failures.
    A ready receipt establishes checked files, not a live model invocation.
    """
    root, skills, home = map(_path, (repo_root, skills_root, home))
    manifest, components, review = _bundle(root, selected_names)
    state = _path(home / host_profiles.state_subdir(host))
    receipt_path = state / 'receipt.json'
    receipt = _read_receipt(receipt_path, root, skills, allow_relocation=True)
    snapshots = _preflight_targets(skills, components, receipt)
    available_updates = _verify_upstream(components)
    before = receipt_path.read_bytes() if receipt_path.exists() else None
    approvals_path = root / 'skill-approvals.json'
    approvals_before = approvals_path.read_bytes() if approvals_path.exists() else None
    pending_clean = [c for c in components if c.get('pending_clean_approval')]
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
            reports, scan_errors = {}, []
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
                try:
                    result = _run(_scanner_command(scanner_meta['path'], 'scan', destination, '--no-llm', '--format', 'json',
                                   '--output', output, '--fail-on-incomplete', '--min-coverage', '100', '--fail-on-findings'))
                    if result.returncode not in (0, 1):
                        raise ValueError('Scanner execution failed for ' + name + ': ' + result.stderr[-1500:])
                    report = _json(output)
                    _validate_report(report, component)
                    if result.returncode != (1 if report['issues'] or not report['analysis_completeness']['is_complete'] else 0):
                        raise ValueError('Scanner exit status disagrees with the verified report: ' + name)
                    if _hashes(destination) != component['installed_hashes']:
                        raise ValueError('Payload changed during scan: ' + name)
                    reports[name] = report
                except (ValueError, OSError) as exc:
                    scan_errors.append(name + ': ' + str(exc))
            if scan_errors:
                raise ValueError('Selected bundle scans blocked activation: ' + '; '.join(scan_errors))
            # Recheck all sources and destinations after the potentially long scans.
            current_manifest, current_components, _ = _bundle(root, selected_names)
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
                                  'exception_ref': (component.get('exception') or {}).get('ref'),
                                  'warnings': component['warnings'],
                                  'scan_completeness': reports[name]['analysis_completeness']})
            device = os.environ.get('ADVISOR_DEVICE_ALIAS') or socket.gethostname()
            new_receipt = {'schema_version': 1, 'bundle_version': manifest['bundle_version'],
                           'device': str(device)[:128],
                           'installed_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
                           'source_root': str(root), 'skills_root': str(skills),
                           'manifest_sha256': _sha(root / 'advisor-bundle.json'),
                           'scanner': scanner_meta, 'components': installed,
                           'selected_names': list(selected_names) if selected_names is not None else None,
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
                if pending_clean:
                    _record_clean_approvals(root, pending_clean)
            except Exception:
                if before is None:
                    receipt_path.unlink(missing_ok=True)
                elif receipt_path.read_bytes() != before:
                    receipt_path.write_bytes(before)
                if approvals_before is not None and approvals_path.read_bytes() != approvals_before:
                    approvals_path.write_bytes(approvals_before)
                for name in reversed(changed):
                    shutil.rmtree(_path(skills / name))
                for name in reversed(moved):
                    os.replace(backups / name, skills / name)
                raise
        return {'ready': True, 'errors': [], 'receipt': str(receipt_path), 'scanner': scanner_meta,
                'components': [c['name'] for c in components],
                'auto_approved_updates': [c['name'] for c in pending_clean],
                'updates_available': available_updates,
                'approval_records': str(approvals_path) if approvals_before is not None else None,
                'full_bundle_ready': len(components) == len(manifest['components']),
                'warnings': [warning for c in components for warning in c['warnings']],
                'scan_completeness': {name: r['analysis_completeness'] for name, r in reports.items()},
                'live_invocation_verified': False}
    finally:
        lock.unlink(missing_ok=True)


def check_bundle(repo_root, skills_root, home, host='codex'):
    """Read-only validation of current source, receipt, reports and installation."""
    try:
        root, skills, home = map(_path, (repo_root, skills_root, home))
        state = _path(home / host_profiles.state_subdir(host))
        if (state / 'install.lock').exists():
            raise ValueError('An advisor installation is in progress')
        receipt = _read_receipt(state / 'receipt.json', root, skills)
        if receipt is None:
            raise ValueError('Advisor installation receipt is missing')
        manifest, components, review = _bundle(root, receipt.get('selected_names'))
        if (receipt.get('manifest_sha256') != _sha(root / 'advisor-bundle.json')
                or receipt.get('bundle_version') != manifest['bundle_version']):
            raise ValueError('Installed bundle differs from the current source manifest')
        recorded = {c['name']: c for c in receipt['components']}
        if set(recorded) != {c['name'] for c in components}:
            raise ValueError('Receipt does not cover the current bundle')
        scan_completeness = {}
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
            report = _json(report_path)
            _validate_report(report, component)
            scan_completeness[component['name']] = report['analysis_completeness']
            if ('warnings' in item and item['warnings'] != component['warnings']
                    or 'scan_completeness' in item and item['scan_completeness'] != report['analysis_completeness']):
                raise ValueError('Receipt risk triage or coverage mismatch: ' + component['name'])
        scanner = receipt.get('scanner', {})
        current = _verify_scanner(scanner.get('path', ''), manifest['scanner'], review)
        if current != scanner:
            raise ValueError('Installed scanner receipt/provenance mismatch')
        return {'ready': True, 'errors': [], 'receipt': str(state / 'receipt.json'),
                'components': list(recorded),
                'full_bundle_ready': len(components) == len(manifest['components']),
                'warnings': [warning for c in components for warning in c['warnings']],
                'scan_completeness': scan_completeness, 'live_invocation_verified': False}
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {'ready': False, 'errors': [str(exc)], 'live_invocation_verified': False}
