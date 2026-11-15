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


class MediumApprovalRequired(ValueError):
    """A complete, static scan needs an explicit one-time local review."""

    def __init__(self, skill, risk, issues):
        self.skill = skill
        self.risk = risk
        self.issues = issues
        self.warnings = [
            {'skill': skill, 'severity': issue['severity'],
             'finding': str(issue.get('id', '?'))} for issue in issues
        ]
        super().__init__(
            'MEDIUM security review required for ' + skill +
            '. Run the install directly in an interactive terminal to approve or reject.')


_MEDIUM_FEATURES = {
    'tool-advisor': (
        'Save project plans and decisions locally.',
        'Track tasks and their progress.',
        'Resume saved workflows.',
        'Update local workflow records when invoked.',
    ),
    'find-skills': (
        'Search for available agent skills and assess relevant candidates.',
        'Compare skill sources and recommend suitable options.',
        'Suggest installing selected skills through the controlled security workflow.',
    ),
}


def _single_line(value, limit=190):
    return re.sub(r'[\x00-\x1f\x7f]+', ' ', str(value)).strip()[:limit]


def _issue_reason(issue):
    """Present a meaningful explanation rather than raw matched command text."""
    issue_id = _single_line(issue.get('id', '?'), 30)
    matched = _single_line(
        issue.get('finding') or issue.get('pattern') or issue.get('matched_text') or '')
    if issue_id == 'LP3':
        capabilities = [
            plain for name, plain in (
                ('file_write', 'modify local files'),
                ('file_read', 'read local files'),
                ('network', 'access the network'),
                ('shell', 'execute shell commands'),
                ('env', 'read environment settings'),
                ('mcp', 'use MCP tools'),
            ) if name in matched
        ]
        if capabilities:
            suffix = 'this capability' if len(capabilities) == 1 else 'these capabilities'
            return ('The skill can ' + ', '.join(capabilities) +
                    ' but has not declared ' + suffix + '.')
        return 'The skill uses capabilities that it has not declared.'
    if issue_id == 'RP1':
        lower = matched.lower()
        if 'npx' in lower:
            return ('References an external npm command without a fixed version; '
                    'running it could fetch changed executable code.')
        if 'uvx' in lower or 'uv tool run' in lower or 'pip' in lower:
            return ('References an external Python tool without a fixed version; '
                    'running it could fetch changed executable code.')
        if 'docker' in lower:
            return ('References a container image without a fixed version; '
                    'running it could use changed executable code.')
        return ('References external software without fixed versions; '
                'running it could fetch changed executable code.')
    explanation = issue.get('explanation')
    return _single_line(explanation or issue.get('finding') or
                        issue.get('pattern') or 'The scanner identified a security concern.')


def _review_groups(issues):
    """Group equivalent reports without losing distinct risks or individual warnings."""
    groups = {}
    for issue in issues:
        issue_id = _single_line(issue.get('id', '?'), 30)
        severity = _single_line(issue.get('severity', '?'), 20)
        reason = _issue_reason(issue)
        key = (issue_id, severity, reason)
        if key not in groups:
            groups[key] = {'id': issue_id, 'severity': severity,
                           'reason': reason, 'count': 0}
        groups[key]['count'] += 1
    return list(groups.values())


def approve_medium(review, trusted_core=False):
    """Ask for each attempt; no approval cache or automatic yes option.

    A TTY is not proof of a human: the user must never delegate the decision
    to an agent, and an agent with OS privileges can still emulate input.
    """
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise ValueError('MEDIUM review requires your interactive terminal. '
                         'Run the installer in PowerShell or Terminal yourself '
                         'and do not delegate the decision to an agent.')

    title = review.skill.replace('-', ' ').title()
    print('\n=== ' + title + ' — Security Review [MEDIUM] ===', flush=True)
    groups = _review_groups(review.issues)
    if groups:
        print('Findings: ' + str(len(review.issues)) + ' occurrence(s) in ' +
              str(len(groups)) + ' distinct group(s).', flush=True)
        for group in groups:
            print('Reason: ' + group['reason'], flush=True)
            print('Finding: ' + group['id'] + ' — ' +
                  str(group['count']) + ' occurrence(s) (technical reference)', flush=True)
    else:
        print('Reason: SkillSpector recommends additional review for this skill.',
              flush=True)
    print('After approval, ' + title + ' can:', flush=True)
    expected_ledger_finding = False
    if len(review.issues) == 1 and str(review.issues[0].get('id')) == 'LP3':
        detail = str(review.issues[0].get('finding') or
                     review.issues[0].get('pattern') or '')
        match = re.search(r'code capabilities were detected:\s*([a-z_, ]+)', detail)
        expected_ledger_finding = bool(
            match and match.group(1).strip().rstrip('.') == 'file_write')
    expected_find_skills_finding = (
        bool(review.issues) and all(
            str(issue.get('id')) == 'RP1' and
            'npx skills' in str(issue.get('finding') or
                                issue.get('pattern') or '').lower()
            for issue in review.issues))
    trusted_features = (
        (review.skill == 'tool-advisor' and expected_ledger_finding) or
        (review.skill == 'find-skills' and expected_find_skills_finding))
    features = (_MEDIUM_FEATURES.get(review.skill)
                if trusted_core and trusted_features else None)
    if features is None:
        reported = ' '.join(_single_line(issue.get('finding') or issue.get('pattern') or '')
                            for issue in review.issues)
        if 'file_write' in reported:
            features = ('Create or update local files when invoked, subject to host permissions.',)
        else:
            features = ('Run its documented features, including the behavior reported above, '
                        'subject to existing host permissions.',)
    for feature in features:
        print('  - ' + feature, flush=True)
    if review.skill == 'find-skills' and expected_find_skills_finding:
        print('Note: Running unpinned npx commands can fetch executable code. '
              'Direct skill installation remains subject to the security hook.',
              flush=True)
    print('Approval does not grant new host permissions or enable background tasks.',
          flush=True)
    try:
        response = input('Approve these capabilities? [y/N]: ').strip().lower()
    except (EOFError, KeyboardInterrupt):
        raise ValueError('MEDIUM approval cancelled; no skill installed') from None
    if response not in ('y', 'yes'):
        raise ValueError('MEDIUM approval rejected; no skill installed')
    return review.warnings


class ScanRejected(ValueError):
    """Completed scanner invocation with findings retained for final review."""
    def __init__(self, reason, report):
        self.report = report
        super().__init__(reason + '\nReview: ' + json.dumps({
            'risk_assessment': report.get('risk_assessment'),
            'issues': report.get('issues'),
            'analysis_completeness': report.get('analysis_completeness'),
        }, ensure_ascii=True))


def scan_skill(stage, scanner, expected_files):
    command = [scanner['path'], 'scan', str(stage), '--no-llm', '--format', 'json',
               '--fail-on-incomplete', '--min-coverage', '100']
    environment = {**os.environ, 'LANGSMITH_TRACING': 'false', 'LANGCHAIN_TRACING_V2': 'false'}
    try:
        # Full static scans may exceed five minutes; validate the completed report below.
        result = subprocess.run(command, capture_output=True, text=True, env=environment)
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
        raise ScanRejected('Incomplete or non-static SkillSpector scan', report)
    if (report.get('suppressed_count', 0) or report.get('suppressed', [])
            or report.get('execution_successful') is False):
        raise ScanRejected('Suppressed findings or unsuccessful scan are not allowed', report)
    present = report.get('components')
    if (not isinstance(present, list) or
            set(x.get('path') for x in present if isinstance(x, dict)) != set(expected_files)):
        raise ScanRejected('SkillSpector component coverage mismatch', report)
    issues = report.get('issues')
    risk = report.get('risk_assessment')
    if not isinstance(issues, list) or not isinstance(risk, dict):
        raise ScanRejected('Missing SkillSpector risk assessment or findings', report)
    severity = risk.get('severity')
    recommendation = risk.get('recommendation')
    if severity not in ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') or (
        recommendation not in ('SAFE', 'CAUTION', 'DO_NOT_INSTALL')
    ):
        raise ScanRejected('Unknown scanner severity or recommendation', report)
    if any(not isinstance(x, dict) or x.get('severity') not in
           ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') for x in issues):
        raise ScanRejected('Malformed individual scan findings', report)
    hard_block = (severity in ('HIGH', 'CRITICAL') or
                  recommendation == 'DO_NOT_INSTALL' or
                  any(x['severity'] in ('HIGH', 'CRITICAL') for x in issues))
    if hard_block:
        raise ScanRejected('SkillSpector blocked high-risk skill: ' + stage.name +
                         ' (' + severity + ', ' + recommendation + ')', report)
    needs_review = (severity == 'MEDIUM' or recommendation == 'CAUTION' or
                    any(x['severity'] == 'MEDIUM' for x in issues))
    if needs_review:
        raise MediumApprovalRequired(stage.name,
                                     {'severity': severity, 'recommendation': recommendation},
                                     issues)
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
    command = [uv, 'tool', 'install',
               'git+https://github.com/NVIDIA/skillspector.git@ea5aeef6b05c593959ad2125c09a528ffa5c55c9']
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

def install_skill(source, skills_root, name, scanner=None, update=False,
                  approval_handler=None, scan_validator=None):
    """Stage, scan, then install/update exactly the inspected skill bytes.

    Native MCP callers supply a trusted per-call validator and an approval
    callback. Public CLI calls continue to require an interactive TTY for
    MEDIUM reports; no CLI bypass flag exists.
    """
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
        review = None
        try:
            warnings = scan_skill(staged, scanner_info, original)
        except MediumApprovalRequired as pending:
            review = pending
            warnings = pending.warnings
        if file_snapshot(staged) != original or file_snapshot(source) != original:
            raise ValueError('Skill changed during scan')
        if update and _digests(file_snapshot(target)) != known['files']:
            raise ValueError('Existing skill changed during scan')
        if scan_validator is not None:
            scan_validator(name, original, review, warnings)
        if review is not None:
            # A host-native tool call invokes the supplied handler only after
            # the host's permission gate. An ordinary CLI prompts locally.
            (approval_handler or approve_medium)(review)
            if file_snapshot(staged) != original or file_snapshot(source) != original:
                raise ValueError('Skill changed during security review')
            if update and _digests(file_snapshot(target)) != known['files']:
                raise ValueError('Existing skill changed during security review')
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
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
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

def _clone_digest(root):
    """Reject symlinks and detect any change in the staged checkout during inspection."""
    digest = hashlib.sha256()
    for item in sorted(root.rglob('*')):
        if item.is_symlink():
            raise ValueError('Cloned repository contains a symlink: ' + str(item))
        if item.is_file():
            rel = item.relative_to(root).as_posix()
            digest.update(rel.encode('utf-8'))
            digest.update(b'\x00')
            with item.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1048576), b''):
                    digest.update(chunk)
        elif not item.is_dir():
            raise ValueError('Unsupported cloned repository file: ' + str(item))
    return digest.digest()

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
        staged_hash = _clone_digest(staged)
        skill_dirs = sorted({p.parent for p in staged.rglob('SKILL.md')
                             if '.git' not in p.relative_to(staged).parts},
                            key=str)
        summary = []
        failures = []
        if skill_dirs:
            for i, folder in enumerate(skill_dirs):
                source_files = file_snapshot(folder)
                with tempfile.TemporaryDirectory(prefix='.secure-inspect-', dir=Path(temp)) as inspect:
                    isolated = Path(inspect) / ('skill-' + str(i))
                    shutil.copytree(folder, isolated)
                    if file_snapshot(isolated) != source_files:
                        raise ValueError('Cloned skill changed during staging')
                    try:
                        warnings = scan_skill(isolated, scanner_info, source_files)
                    except (ValueError, OSError) as exc:
                        # Findings and per-payload failures must not skip later payloads.
                        failures.append({'skill': folder.relative_to(staged).as_posix(),
                                         'error': str(exc),
                                         'issues': getattr(exc, 'issues', [])})
                        warnings = []
                    if file_snapshot(isolated) != source_files or file_snapshot(folder) != source_files:
                        raise ValueError('Cloned skill changed during scanning')
                    summary.append({'skill': folder.relative_to(staged).as_posix(), 'warnings': warnings})
        else:
            summary.append(_report_generic_repository(staged, scanner_info))
        if _clone_digest(staged) != staged_hash:
            raise ValueError('Cloned repository changed during inspection')
        if failures:
            raise ValueError('Scan attempted for all discovered skills; installation/release blocked. '
                             'Consolidated review: ' + json.dumps(
                                 {'checks': summary, 'failures': failures}, ensure_ascii=True))
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
