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
    print('Workspace setup: --setup-workspace verifies SkillSpector, configures hooks, then scans/installs the full Advisor baseline. --plan-advisor inspects preparation gaps; --install-advisor-core is partial.')


MATCHERS = {
    'claude': 'Bash|PowerShell|Write|Edit|MultiEdit|NotebookEdit',
    'codex': 'Bash|apply_patch|Edit|Write',
}


def _command(script):
    parts = [sys.executable, str(script)]
    if os.name == 'nt':
        return subprocess.list2cmdline(parts)
    return shlex.join(parts)


def _hook_entry(script, host):
    return {'matcher': MATCHERS[host],
            'hooks': [{'type': 'command', 'command': _command(script), 'timeout': 600}]}


def hook_config_file(home, host):
    return Path(home) / ('settings.json' if host == 'claude' else 'hooks.json')


def configure_security_hook(home, host, repo, install=False):
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

def setup_workspace(host, home, skills_root, scanner=None):
    """Security first, Tool Advisor last; no active skill before a complete scan."""
    from secure_operations import ensure_scanner, verify_scanner_sample
    from install_advisor import install_bundle, require_baseline
    require_baseline(ROOT)
    scanner_info = ensure_scanner(scanner)
    verify_scanner_sample(scanner_info)
    hook = configure_security_hook(home, host, ROOT, install=True)
    if not hook['ready']:
        raise ValueError('Security hook could not be configured')
    verify_security_hook(ROOT)
    result = install_bundle(ROOT, skills_root, home,
                            scanner=Path(scanner_info['path']), host=host)
    install(home, saved_rules(host), host)
    return {'ready': result.get('ready', False), 'scanner': scanner_info,
            'security_hook': hook, 'advisor': result,
            'live_host_verified': False,
            'note': 'Restart the target host and test a real hook event on the device'}


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
    action.add_argument('--plan-advisor', action='store_true', help='List all required baseline skills and payload preparation gaps without writing')
    action.add_argument('--install-advisor-core', action='store_true', help='Explicit partial setup: install only tool-advisor, grilling and find-skills')
    action.add_argument('--install-advisor', action='store_true', help='Install the full approved baseline; block partial setup')
    action.add_argument('--check-advisor', action='store_true', help='Check advisor files, receipts and rules without writing')
    action.add_argument('--setup-workspace', action='store_true', help='Security-first setup of SkillSpector hooks, global rules and the full 17-skill baseline')
    args = parser.parse_args()
    host = args.host
    home = args.home or args.codex_home or host_profiles.home_dir(host)
    skills_root = args.skills_root or host_profiles.default_skills_root(host)
    wording = host_profiles.wording(host)
    try:
        if args.scanner and not (args.setup_workspace or args.install_advisor or args.install_advisor_core):
            raise ValueError('--scanner applies only to workspace or advisor installation')
        if args.setup_workspace:
            result = setup_workspace(host, home, skills_root, scanner=args.scanner)
            print(json.dumps(result, indent=2))
            print('Security configured locally; restart ' + wording['host_name'] +
                  ' and verify live hook behavior before relying on it.')
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
                if not result.get('full_bundle_ready', False):
                    result['ready'] = False
                    result.setdefault('errors', []).append('Installed receipt does not cover the full baseline.')
                if not plan['payloads_prepared']:
                    result['ready'] = False
                    result.setdefault('errors', []).append('Full baseline payload preparation is incomplete.')
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
            selected_names = None
            if args.install_advisor:
                require_baseline(ROOT)
            else:
                selected_names = require_core_only(ROOT)
            result = install_bundle(ROOT, skills_root, home, scanner=args.scanner,
                                    selected_names=selected_names, host=host)
            result['setup_scope'] = 'full-baseline' if args.install_advisor else 'explicit-partial-core'
            result['full_baseline_files_ready'] = bool(args.install_advisor)
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
