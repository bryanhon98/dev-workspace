#!/usr/bin/env python3
"""Show setup choices; explicitly install rules or the reviewed advisor bundle."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

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
    print('Advisor setup: --install-advisor selects the full baseline; --plan-advisor shows preparation gaps. --install-advisor-core explicitly installs only the three-skill core.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='codex', choices=host_profiles.host_names(),
                        help='Target client: codex (default) or claude')
    # --codex-home is kept as a hidden alias for backwards compatibility; new
    # invocations should use --home.
    parser.add_argument('--home', type=Path, default=None)
    parser.add_argument('--codex-home', type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument('--skills-root', type=Path, default=None)
    parser.add_argument('--scanner', type=Path, help='Existing reviewed SkillSpector executable for advisor installation')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--check', action='store_true', help='Verify installed global rules without writing')
    action.add_argument('--install-rules', action='store_true', help='Restore setup rules globally')
    action.add_argument('--plan-advisor', action='store_true', help='List all required baseline skills and payload preparation gaps without writing')
    action.add_argument('--install-advisor-core', action='store_true', help='Explicit partial setup: install only tool-advisor, grilling and find-skills')
    action.add_argument('--install-advisor', action='store_true', help='Install the full approved baseline; block partial setup')
    action.add_argument('--check-advisor', action='store_true', help='Check advisor files, receipts and rules without writing')
    action.add_argument('--show-approvals', action='store_true', help='Print shared version approvals without writing')
    args = parser.parse_args()
    host = args.host
    home = args.home or args.codex_home or host_profiles.home_dir(host)
    skills_root = args.skills_root or host_profiles.default_skills_root(host)
    wording = host_profiles.wording(host)
    try:
        if args.scanner and not (args.install_advisor or args.install_advisor_core):
            raise ValueError('--scanner is only used with --install-advisor or --install-advisor-core')
        if args.show_approvals:
            from install_advisor import _json
            print(json.dumps(_json(ROOT / 'skill-approvals.json'), indent=2))
            return 0
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
