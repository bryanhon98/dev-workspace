"""Single SkillSpector scan worker and controlled skill/clone operations.

This module owns scanner calls. Hosts intercept operations; installers stage files.
Scanner reports are temporary, while small file digests protect local modifications.
SkillSpector is not a comprehensive general-code malware detector.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import urlparse

def safe_path(value):
    path = Path(os.path.abspath(os.fspath(value)))
    for part in [*reversed(path.parents), path]:
        if part.is_symlink():
            raise ValueError('Refusing symlink path: ' + str(part))
    return path

def file_snapshot(directory):
    directory = safe_path(directory)
    if not directory.is_dir():
        raise ValueError('Missing payload directory: ' + str(directory))
    result = {}
    for item in sorted(directory.rglob('*')):
        safe_path(item)
        if item.is_file():
            result[item.relative_to(directory).as_posix()] = item.read_bytes()
        elif not item.is_dir():
            raise ValueError('Unsupported payload file: ' + str(item))
    return result

def scanner_executable(value):
    candidate = value or shutil.which('skillspector')
    if not candidate:
        raise ValueError('SkillSpector is required: uv tool install git+https://github.com/NVIDIA/skillspector.git')
    # uv tool installs may expose a symlink shim; resolve it for the scanner only.
    # Skill source files still reject symlinks via _path/_files.
    try:
        path = Path(os.path.abspath(os.fspath(candidate))).resolve(strict=True)
    except OSError as exc:
        raise ValueError('SkillSpector executable is missing: ' + str(candidate)) from exc
    if not path.is_file():
        raise ValueError('SkillSpector executable is missing: ' + str(path))
    result = subprocess.run([str(path), '--version'], capture_output=True, text=True, timeout=30)
    if result.returncode or not re.fullmatch(r'SkillSpector v[0-9][^\s]*', result.stdout.strip()):
        raise ValueError('SkillSpector executable/version check failed')
    return {'path': str(path), 'version': result.stdout.strip()}


def scan_skill(stage, scanner, expected_files):
    command = [scanner['path'], 'scan', str(stage), '--no-llm', '--format', 'json',
               '--fail-on-incomplete', '--min-coverage', '100']
    environment = {**os.environ, 'LANGSMITH_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false'}
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=300, env=environment)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError('SkillSpector scan failed: ' + str(exc)) from exc
    if result.returncode not in (0, 1):
        raise ValueError('SkillSpector execution error: ' + result.stderr[-1000:])
    try:
        report = json.loads(result.stdout)
    except (ValueError, TypeError) as exc:
        raise ValueError('SkillSpector did not return valid JSON') from exc
    if not isinstance(report, dict):
        raise ValueError('Malformed SkillSpector report')
    complete = report.get('analysis_completeness')
    metadata = report.get('metadata', {})
    if (not isinstance(complete, dict) or complete.get('is_complete') is not True
            or complete.get('coverage_percent') != 100
            or not isinstance(metadata, dict) or metadata.get('llm_requested') is not False):
        raise ValueError('Incomplete or non-static SkillSpector scan')
    if (report.get('suppressed_count', 0) or report.get('suppressed', [])
            or report.get('execution_successful') is False):
        raise ValueError('Suppressed findings or unsuccessful scan are not allowed')
    present = report.get('components')
    if (not isinstance(present, list) or
            set(x.get('path') for x in present if isinstance(x, dict)) != set(expected_files)):
        raise ValueError('SkillSpector component coverage mismatch')
    issues = report.get('issues')
    risk = report.get('risk_assessment')
    if not isinstance(issues, list) or not isinstance(risk, dict):
        raise ValueError('Missing SkillSpector risk assessment or findings')
    severity = risk.get('severity')
    recommendation = risk.get('recommendation')
    if severity not in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') or (
        recommendation not in ('SAFE', 'CAUTION', 'DO_NOT_INSTALL')
    ):
        raise ValueError('Unknown scanner severity or recommendation')
    if any(not isinstance(x, dict) or x.get('severity') not in
           ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') for x in issues):
        raise ValueError('Malformed individual scan findings')
    blocked = severity in ('MEDIUM', 'HIGH', 'CRITICAL') or recommendation != 'SAFE' or any(
        x['severity'] in ('MEDIUM', 'HIGH', 'CRITICAL') for x in issues)
    if blocked:
        raise ValueError('SkillSpector blocked risky skill: ' + stage.name +
                         ' (' + severity + ', ' + recommendation + ')')
    if result.returncode == 1:
        raise ValueError('SkillSpector scan exited unsuccessfully: ' + stage.name)
    return [{'skill': stage.name, 'severity': x['severity'], 'finding': str(x.get('id', '?'))}
            for x in issues]



def ensure_scanner(value=None):
    """Install from NVIDIA's official GitHub source only if absent.

    A name/version check is not independent binary provenance authentication.
    """
    if value is not None or shutil.which('skillspector'):
        return scanner_executable(value)
    uv = shutil.which('uv')
    if not uv:
        raise ValueError('SkillSpector missing; install uv then rerun setup')
    command = [uv, 'tool', 'install', 'git+https://github.com/NVIDIA/skillspector.git']
    result = subprocess.run(command, capture_output=True, text=True, timeout=300)
    if result.returncode:
        raise ValueError('Official SkillSpector installation failed: ' + result.stderr[-1000:])
    return scanner_executable(None)

def verify_scanner_sample(scanner):
    """Run an actual benign scan, not just a --version check."""
    with tempfile.TemporaryDirectory(prefix='dev-workspace-scanner-check-') as temp:
        sample = Path(temp)
        (sample / 'SKILL.md').write_text(
            '---\nname: benign-example\ndescription: Static security smoke test\n---\n'
            'This sample contains no executable instructions.\n', encoding='utf-8')
        return scan_skill(sample, scanner, file_snapshot(sample))

def _digests(files):
    return {key: hashlib.sha256(value).hexdigest() for key, value in files.items()}

def _write_json_atomic(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix='.secure-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(obj, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def install_skill(source, skills_root, name, scanner=None, update=False):
    """Stage, scan, then install/update exactly the inspected skill bytes."""
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('Invalid skill name')
    source, root = safe_path(source), safe_path(skills_root)
    original = file_snapshot(source)
    if 'SKILL.md' not in original:
        raise ValueError('Skill must contain SKILL.md')
    target = safe_path(root / name)
    state_file = root.parent / 'dev-workspace-security' / 'installed-skills.json'
    state = json.loads(state_file.read_text(encoding='utf-8')) if state_file.exists() else {}
    if not isinstance(state, dict):
        raise ValueError('Invalid installed skills metadata')
    known = state.get(name)
    if update:
        if not target.exists() or not isinstance(known, dict):
            raise ValueError('Update requires a previously controlled installation: ' + name)
        if _digests(file_snapshot(target)) != known.get('files'):
            raise ValueError('Installed skill changed locally; refusing update: ' + name)
    elif target.exists():
        raise ValueError('Skill already exists; refusing unmanaged overwrite: ' + name)
    scanner_info = scanner_executable(scanner)
    root.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.secure-skill-', dir=root.parent) as temp:
        tempdir = Path(temp)
        staged = tempdir / name
        shutil.copytree(source, staged)
        if file_snapshot(staged) != original:
            raise ValueError('Source changed during staging')
        warnings = scan_skill(staged, scanner_info, original)
        if file_snapshot(staged) != original or file_snapshot(source) != original:
            raise ValueError('Skill changed during scan')
        if update and _digests(file_snapshot(target)) != known['files']:
            raise ValueError('Existing skill changed during scan')
        backup = tempdir / 'backup'
        replaced = False
        installed = False
        try:
            if update:
                os.replace(target, backup)
                replaced = True
            root.mkdir(parents=True, exist_ok=True)
            os.replace(staged, target)
            installed = True
            if file_snapshot(target) != original:
                raise ValueError('Installed files differ from scanned files')
            state[name] = {'files': _digests(original)}
            _write_json_atomic(state_file, state)
        except Exception:
            if installed and target.exists():
                shutil.rmtree(target)
            if replaced and backup.exists():
                os.replace(backup, target)
            raise
    return {'installed': True, 'updated': bool(update), 'name': name, 'warnings': warnings}

_GITHUB_URL = re.compile(r'^https://github[.]com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:[.]git)?/?$')

def _report_generic_repository(stage, scanner):
    """Best-effort scan of a non-skill repo: never describe limited coverage as safe."""
    cmd = [scanner['path'], 'scan', str(stage), '--no-llm', '--format', 'json',
           '--fail-on-incomplete', '--min-coverage', '100']
    env = {**os.environ, 'LANGSMITH_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false'}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
        report = json.loads(result.stdout)
    except (ValueError, OSError, subprocess.TimeoutExpired):
        return {'coverage': 'not-applicable', 'note': 'SkillSpector could not assess this non-skill repository'}
    if not isinstance(report, dict):
        return {'coverage': 'not-applicable', 'note': 'No usable SkillSpector result for non-skill repository'}
    risks = report.get('risk_assessment', {})
    issues = report.get('issues', [])
    if (isinstance(risks, dict) and
            (risks.get('severity') in ('MEDIUM', 'HIGH', 'CRITICAL') or
             risks.get('recommendation') in ('CAUTION', 'DO_NOT_INSTALL'))) or (
            isinstance(issues, list) and any(isinstance(x, dict) and
                x.get('severity') in ('MEDIUM', 'HIGH', 'CRITICAL') for x in issues)):
        raise ValueError('SkillSpector identified a risk in cloned repository')
    if result.returncode:
        return {'coverage': 'limited', 'note': 'Non-skill scan did not complete successfully'}
    return {'coverage': 'limited', 'note': 'SkillSpector is not a general repository safety guarantee'}

def clone_repository(url, destination=None, cwd=None, scanner=None):
    """Clone HTTPS GitHub source into staging; inspect before release to destination."""
    if not isinstance(url, str) or not _GITHUB_URL.fullmatch(url):
        raise ValueError('Only HTTPS GitHub repository clone URLs are supported')
    name = url.rstrip('/').rsplit('/', 1)[1].removesuffix('.git')
    base = safe_path(cwd or Path.cwd())
    target = safe_path(base / (destination or name))
    if target.exists():
        raise ValueError('Clone destination already exists: ' + str(target))
    if not base.is_dir() or not target.parent.is_dir():
        raise ValueError('Clone destination parent is missing')
    if not target.is_relative_to(base) or target == base:
        raise ValueError('Clone destination must remain within current workspace')
    scanner_info = scanner_executable(scanner)
    with tempfile.TemporaryDirectory(prefix='.secure-clone-', dir=target.parent) as temp:
        staged = Path(temp) / 'repository'
        environment = {**os.environ, 'GIT_LFS_SKIP_SMUDGE': '1'}
        result = subprocess.run(['git', '-c', 'core.hooksPath=' + os.devnull,
                                 'clone', '--', url, str(staged)],
                                capture_output=True, text=True, timeout=300, env=environment)
        if result.returncode:
            raise ValueError('Git clone failed: ' + result.stderr[-1000:])
        skill_dirs = sorted({p.parent for p in staged.rglob('SKILL.md')
                             if '.git' not in p.relative_to(staged).parts},
                            key=str)
        summary = []
        if skill_dirs:
            for i, folder in enumerate(skill_dirs):
                source_files = file_snapshot(folder)
                with tempfile.TemporaryDirectory(prefix='.secure-inspect-', dir=Path(temp)) as inspect:
                    isolated = Path(inspect) / ('skill-' + str(i))
                    shutil.copytree(folder, isolated)
                    if file_snapshot(isolated) != source_files:
                        raise ValueError('Cloned skill changed during staging')
                    warnings = scan_skill(isolated, scanner_info, source_files)
                    if file_snapshot(isolated) != source_files or file_snapshot(folder) != source_files:
                        raise ValueError('Cloned skill changed during scanning')
                    summary.append({'skill': folder.relative_to(staged).as_posix(), 'warnings': warnings})
        else:
            summary.append(_report_generic_repository(staged, scanner_info))
        if target.exists():
            raise ValueError('Destination created while clone was scanned')
        os.replace(staged, target)
        return {'cloned': True, 'destination': str(target), 'checks': summary,
                'notice': 'SkillSpector scanning does not certify general repository safety'}

def main(argv=None):
    import host_profiles
    p = argparse.ArgumentParser(description=__doc__)
    commands = p.add_subparsers(dest='action', required=True)
    install = commands.add_parser('install', help='Scan and install one staged skill')
    install.add_argument('--source', type=Path, required=True)
    install.add_argument('--name', required=True)
    install.add_argument('--host', choices=host_profiles.host_names(), default='codex')
    install.add_argument('--skills-root', type=Path)
    install.add_argument('--update', action='store_true')
    clone = commands.add_parser('clone', help='Stage and inspect a GitHub clone')
    clone.add_argument('--url', required=True)
    clone.add_argument('--destination')
    clone.add_argument('--cwd', type=Path)
    args = p.parse_args(argv)
    try:
        if args.action == 'install':
            outcome = install_skill(args.source, args.skills_root or
                                    host_profiles.default_skills_root(args.host),
                                    args.name, update=args.update)
        else:
            outcome = clone_repository(args.url, args.destination, args.cwd)
        print(json.dumps(outcome, indent=2))
        return 0
    except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(str(exc), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
