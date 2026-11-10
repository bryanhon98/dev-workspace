#!/usr/bin/env python3
"""Show setup choices or perform security-first SkillSpector and Advisor setup."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import shlex
import subprocess

# Add scripts directory to path for local imports when run directly
sys.path.insert(0, str(Path(__file__).resolve().parent))

import host_profiles

# Backwards-compatible module constants (Codex markers). Tests reference these
# directly; per-host behaviour comes from the host-aware functions below.
START = host_profiles.marker_start('codex')
END = host_profiles.marker_end('codex')
ROOT = Path(__file__).resolve().parents[1]


def block(rules, host='codex'):
    start, end = host_profiles.marker_start(host), host_profiles.marker_end(host)
    body = rules.strip() + '\n'
    if not rules.strip() or start in rules or end in rules:
        raise ValueError('Rules must be nonempty and must not contain managed markers')
    digest = hashlib.sha256(body.encode()).hexdigest()
    return (start + '\n<!-- content-sha256: ' + digest + ' -->\n' + body + end).encode()


def target_for(home, host='codex'):
    for name in host_profiles.instruction_files(host):
        target = home / name
        if target.is_symlink():
            raise ValueError('Refusing symlink instruction file: ' + str(target))
        if target.exists() and target.read_bytes().strip():
            return target
    return home / host_profiles.instruction_files(host)[-1]


def managed_span(data, host='codex'):
    start, end = host_profiles.marker_start(host).encode(), host_profiles.marker_end(host).encode()
    if start not in data and end not in data:
        return None
    if data.count(start) != 1 or data.count(end) != 1:
        raise ValueError('Malformed or duplicate managed markers; merge manually')
    first, last = data.index(start), data.index(end)
    if last < first:
        raise ValueError('Reversed managed markers; merge manually')
    return first, last + len(end)


def install(home, rules, host='codex'):
    home = Path(home)
    desired = block(rules, host)
    target = target_for(home, host)
    before = target.read_bytes() if target.exists() else b''
    span = managed_span(before, host)
    if span:
        first, last = span
        current = before[first:last]
        if current == desired:
            return False
        match = re.fullmatch(
            re.escape(host_profiles.marker_start(host).encode()) + rb'\n<!-- content-sha256: ([a-f0-9]{64}) -->\n(.*)'
            + re.escape(host_profiles.marker_end(host).encode()),
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


def check(home, rules, host='codex'):
    target = target_for(Path(home), host)
    data = target.read_bytes() if target.exists() else b''
    span = managed_span(data, host)
    return bool(span and data[span[0]:span[1]] == block(rules, host))


def saved_rules(host='codex'):
    rules = (ROOT / host_profiles.rules_source(host)).read_text(encoding='utf-8').strip()
    return rules + '\n\n## Local research checkout\n\n' + (
        'This device installed the rules from "' + str(ROOT) + '". '
        'Use this explicit checkout for the advisor library and scripts when working in other projects. '
        'Keep the checkout available; if moved, reinstall the rules and advisor from its new location.\n')


def show_catalog(host='codex'):
    wording = host_profiles.wording(host)
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
    print('\n' + wording['catalog_prompt'])
    print('Plugins and MCPs are a manual setup checklist. No software or instructions were installed.')
    print('After choosing, ' + wording['host_name'] + ' can restore global rules with --install-rules and inspect/install selected skills.')
    print('Workspace setup: --setup-workspace verifies SkillSpector and registers the security hook. After UI approval and a real blocked-command test, --finish-workspace --acknowledge-live-hook-test scans/installs three core Advisor skills and global rules. Optional skills are chosen per task. --plan-advisor inspects preparation gaps.')


MATCHERS = {
    'claude': 'Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit',
    'codex': 'Bash|apply_patch|Edit|Write',
}


def _command(script, windows=None):
    """Shell-form launcher for Codex; Windows Codex runs it via PowerShell.

    Keep the Python exit status intact so an exit-2 policy denial remains a denial.
    """
    if windows is None:
        windows = os.name == 'nt'
    parts = [sys.executable, str(script)]
    if windows:
        def quote_ps(value):
            return "'" + value.replace("'", "''") + "'"
        return '& ' + ' '.join(quote_ps(part) for part in parts) + '; exit $LASTEXITCODE'
    return shlex.join(parts)


def _hook_entry(script, host):
    if host == 'claude':
        # Claude Code supports exec-form hooks: no Bash/PowerShell path parsing.
        # onFailure=block requires Claude Code >= 2.1.295.
        handler = {'type': 'command', 'command': sys.executable,
                   'args': [str(script)], 'onFailure': 'block', 'timeout': 600}
    else:
        handler = {'type': 'command', 'command': _command(script), 'timeout': 600}
    return {'matcher': MATCHERS[host], 'hooks': [handler]}


def hook_config_file(home, host):
    return Path(home) / ('settings.json' if host == 'claude' else 'hooks.json')


def configure_security_hook(home, host, repo, install=False):
    """Register or migrate only our managed hook; never approve it for the user."""
    host_profiles.resolve(host)
    script = Path(repo).resolve() / 'scripts' / 'skill_security_hook.py'
    if not script.is_file():
        raise ValueError('Security hook script is missing: ' + str(script))
    target = hook_config_file(home, host)
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
    desired = _hook_entry(script, host)

    def is_managed(entry):
        if not isinstance(entry, dict):
            return False
        handlers = entry.get('hooks', [])
        return isinstance(handlers, list) and any(
            isinstance(h, dict) and 'skill_security_hook.py' in
            (str(h.get('command', '')) + ' ' + str(h.get('args', '')))
            for h in handlers)

    matches = [i for i, entry in enumerate(entries) if is_managed(entry)]
    if len(matches) > 1:
        raise ValueError('Duplicate managed security hooks; reconcile manually')
    if matches:
        position = matches[0]
        if not isinstance(entries[position].get('hooks'), list) or len(entries[position]['hooks']) != 1:
            raise ValueError('Managed hook shares entry with other hooks; reconcile manually')
        if entries[position] == desired:
            return {'ready': True, 'changed': False, 'path': str(target)}
    if not install:
        return {'ready': False, 'changed': False, 'path': str(target),
                'needs_migration': bool(matches)}
    updated = list(entries)
    if matches:
        updated[matches[0]] = desired
    else:
        updated.append(desired)
    hooks['PreToolUse'] = updated
    obj['hooks'] = hooks

    target.parent.mkdir(parents=True, exist_ok=True)
    before = target.read_bytes() if target.exists() else None
    if before is not None:
        # Never overwrite existing backups from earlier setup attempts.
        fd, backup = tempfile.mkstemp(
            prefix=target.name + '.before-dev-workspace-', suffix='.bak',
            dir=target.parent)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(before)
    temporary = target.with_suffix(target.suffix + '.dev-workspace.tmp')
    if temporary.exists():
        raise ValueError('Temporary hook config exists; reconcile before modifying')
    try:
        temporary.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')
        # Refuse to overwrite a concurrent settings edit.
        if (target.read_bytes() if target.exists() else None) != before:
            raise ValueError('Hook settings changed during setup; retry after inspection')
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return {'ready': True, 'changed': True, 'path': str(target),
            'approval_required': True}



def verify_security_hook(repo):
    """Test hook blocking and command rewrites locally; live host needs a new session."""
    script = Path(repo) / 'scripts' / 'skill_security_hook.py'
    checks = [
        ({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
          'tool_input': {'command': 'npx skills add unsafe-example'}}, 2),
        ({'hook_event_name': 'PreToolUse', 'tool_name': 'Bash',
          'tool_input': {'command': 'git clone https://github.com/example/repo.git sample'}}, 0),
    ]
    for event, code in checks:
        result = subprocess.run([sys.executable, str(script)], input=json.dumps(event),
                                text=True, capture_output=True, timeout=15)
        if result.returncode != code:
            raise ValueError('Security hook self-test failed: ' + result.stderr[-500:])
        if code == 0:
            try:
                edited = json.loads(result.stdout)['hookSpecificOutput']['updatedInput']['command']
            except (ValueError, KeyError, TypeError) as exc:
                raise ValueError('Security hook did not rewrite Git clone safely') from exc
            if 'secure_operations.py' not in edited or ' clone ' not in edited:
                raise ValueError('Security hook clone rewrite is not controlled')
    return True

def setup_workspace(host, home, skills_root, scanner=None,
                    finish=False, live_hook_test_acknowledged=False):
    """Stage 1: register the hook; Stage 2: user-approved, verified core setup.

    An acknowledged live test is a user attestation, not a programmatic check
    that the host honored a denial. Do not infer host approval from config bytes.
    """
    from secure_operations import ensure_scanner, verify_scanner_sample
    from install_advisor import install_bundle, require_baseline
    core = require_baseline(ROOT)['required_skills']
    if finish and not live_hook_test_acknowledged:
        raise ValueError('Finish requires --acknowledge-live-hook-test after real host blocking verification')
    scanner_info = ensure_scanner(scanner)
    verify_scanner_sample(scanner_info)
    hook = configure_security_hook(home, host, ROOT, install=not finish)
    if not hook['ready']:
        raise ValueError('Security hook missing or outdated; rerun --setup-workspace and approve it')
    verify_security_hook(ROOT)
    if not finish:
        return {'prepared': True, 'ready': False,
                'scanner': scanner_info, 'security_hook': hook,
                'core_skills_installed': False, 'live_host_verified': False,
                'next': 'Approve the hook in the target host UI, restart the host, '
                        'verify a real allow and deny, then run --finish-workspace '
                        '--acknowledge-live-hook-test. No host approval was automated.'}
    result = install_bundle(ROOT, skills_root, home,
                            scanner=Path(scanner_info['path']),
                            selected_names=core, host=host)
    install(home, saved_rules(host), host)
    return {'prepared': True, 'ready': result.get('ready', False),
            'scanner': scanner_info, 'security_hook': hook, 'advisor': result,
            'live_host_test_acknowledged': True,
            'live_host_verified_automatically': False,
            'note': 'User attested to a live host test; this script cannot independently verify UI approval'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='codex', choices=host_profiles.host_names(),
                        help='Target client: codex (default) or claude')
    # --codex-home is kept as a hidden alias for backwards compatibility; new
    # invocations should use --home.
    parser.add_argument('--home', type=Path, default=None)
    parser.add_argument('--codex-home', type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument('--skills-root', type=Path, default=None)
    parser.add_argument('--scanner', type=Path, help='Existing official SkillSpector executable; default discovers it on PATH')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--check', action='store_true', help='Verify installed global rules without writing')
    action.add_argument('--install-rules', action='store_true', help='Restore setup rules globally')
    action.add_argument('--plan-advisor', action='store_true', help='List the three mandatory core skills and optional candidates without writing')
    action.add_argument('--install-advisor-core', action='store_true', help='Legacy alias: install the same three core skills as --install-advisor')
    action.add_argument('--install-advisor', action='store_true', help='Install the three mandatory Advisor core skills only')
    action.add_argument('--check-advisor', action='store_true', help='Check advisor files, receipts and rules without writing')
    action.add_argument('--setup-workspace', action='store_true', help='Prepare SkillSpector and register hook; then approve and live-test in host UI')
    action.add_argument('--finish-workspace', action='store_true', help='After host hook approval and live blocking test, scan/install three core skills and global rules')
    action.add_argument('--retire-optional-advisor-skills', action='store_true',
                        help='Explicitly archive previously managed non-core skills on this device, without deleting or installing anything')
    parser.add_argument('--acknowledge-live-hook-test', action='store_true',
                        help='Explicitly attest that the user approved the hook and verified a live block in the target host')
    args = parser.parse_args()
    host = args.host
    home = args.home or args.codex_home or host_profiles.home_dir(host)
    skills_root = args.skills_root or host_profiles.default_skills_root(host)
    wording = host_profiles.wording(host)
    try:
        if args.scanner and not (args.setup_workspace or args.finish_workspace or args.install_advisor or args.install_advisor_core):
            raise ValueError('--scanner applies only to workspace or advisor installation')
        if args.acknowledge_live_hook_test and not args.finish_workspace:
            raise ValueError('--acknowledge-live-hook-test requires --finish-workspace')
        if args.setup_workspace or args.finish_workspace:
            result = setup_workspace(host, home, skills_root, scanner=args.scanner,
                                     finish=args.finish_workspace,
                                     live_hook_test_acknowledged=args.acknowledge_live_hook_test)
            print(json.dumps(result, indent=2))
            if args.setup_workspace:
                print('Hook prepared. Approve it in ' + wording['host_name'] +
                      ', restart, and verify live blocking before finishing setup.')
                return 0 if result['prepared'] else 1
            return 0 if result['ready'] else 1
        if args.retire_optional_advisor_skills:
            from install_advisor import retire_optional_skills
            result = retire_optional_skills(ROOT, skills_root, home, host=host)
            print(json.dumps(result, indent=2))
            return 0 if result['ready'] else 1
        if args.plan_advisor:
            from install_advisor import baseline_plan
            print(json.dumps(baseline_plan(ROOT), indent=2))
            return 0
        if args.check_advisor or args.install_advisor or args.install_advisor_core:
            from install_advisor import check_bundle, install_bundle, require_baseline, baseline_plan, require_core_only
            rules = saved_rules(host)
            if args.check_advisor:
                result = check_bundle(ROOT, skills_root, home, host=host)
                plan = baseline_plan(ROOT)
                result['baseline'] = plan
                if not result.get('baseline_ready', False):
                    result['ready'] = False
                    result.setdefault('errors', []).append('Installed receipt does not cover the required three core skills.')
                if not plan['payloads_prepared']:
                    result['ready'] = False
                    result.setdefault('errors', []).append('Core baseline payload preparation is incomplete.')
                if not check(home, rules, host):
                    result['ready'] = False
                    result.setdefault('errors', []).append('Managed global instructions are missing or differ from this checkout.')
                print(json.dumps(result, indent=2))
                return 0 if result['ready'] else 1
            # Check existing managed rules for local edits before activating skills.
            target = target_for(home, host)
            before = target.read_bytes() if target.exists() else b''
            span = managed_span(before, host)
            if span:
                current = before[span[0]:span[1]]
                match = re.fullmatch(re.escape(host_profiles.marker_start(host).encode()) + rb'\n<!-- content-sha256: ([a-f0-9]{64}) -->\n(.*)' + re.escape(host_profiles.marker_end(host).encode()), current, re.DOTALL)
                if not match or hashlib.sha256(match[2]).hexdigest().encode() != match[1]:
                    raise ValueError('Managed rules changed locally; reconcile them before advisor installation')
            selected_names = require_baseline(ROOT)['required_skills']
            result = install_bundle(ROOT, skills_root, home, scanner=args.scanner,
                                    selected_names=selected_names, host=host)
            result['setup_scope'] = 'core-baseline'
            result['core_baseline_files_ready'] = result.get('baseline_ready', False)
            try:
                install(home, rules, host)
            except (OSError, ValueError) as exc:
                raise ValueError('Skills were installed, but global rules could not be updated: ' + str(exc)) from exc
            print(json.dumps(result, indent=2))
            print(wording['session_note_install'])
            print('Files and scans verified; live host invocation still needs a fresh-session check.')
            return 0
        if not args.check and not args.install_rules:
            show_catalog(host)
            return 0
        rules = saved_rules(host)
        if args.check:
            ok = check(home, rules, host)
            print('Global rules match this repo.' if ok else 'Global rules are missing or differ from this repo.')
            return 0 if ok else 1
        changed = install(home, rules, host)
        print(('Installed: ' if changed else 'Already current: ') + str(target_for(home, host)))
        print(wording['session_note'])
        print('This command installs instructions only. Continue README.md with ' + wording['host_name'] + ' for selected skills, manual plugin/MCP setup and GitHub logging.')
        return 0
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
