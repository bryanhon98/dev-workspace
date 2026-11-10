#!/usr/bin/env python3
"""Local stdio MCP interface for native per-call skill installation approvals.

Only the host's permission interface authorizes install_reviewed. This server
never accepts an "approved": true flag, persistent approval record, or a CLI
bypass flag. install_safe cannot activate anything with MEDIUM findings.

The host is responsible for enforcing prompts. Configuring Codex to auto
approve MCP tool calls destroys that guarantee; see docs/NATIVE-APPROVAL.md.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import host_profiles
import secure_operations as security
import install_advisor

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = '2025-06-18'
KNOWN_PROTOCOLS = {'2024-11-05', '2025-03-26', '2025-06-18', '2025-11-25'}


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=True).encode('utf-8')).hexdigest()


def _issues(review, warnings):
    if review is None:
        return [{'id': str(x['finding']), 'severity': x['severity']}
                for x in warnings]
    return [
        {key: issue.get(key) for key in
         ('id', 'severity', 'finding', 'pattern', 'explanation', 'message')
         if issue.get(key) is not None}
        for issue in review.issues
    ]


def _scan_payload(name, files, scanner):
    if 'SKILL.md' not in files:
        raise ValueError('Missing SKILL.md')
    with tempfile.TemporaryDirectory(prefix='native-skill-review-') as tmp:
        staged = Path(tmp) / name
        staged.mkdir()
        for relative, data in files.items():
            destination = staged / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        if security.file_snapshot(staged) != files:
            raise ValueError('Staged skill changed before review')
        review = None
        try:
            warnings = security.scan_skill(staged, scanner, files)
        except security.MediumApprovalRequired as item:
            review = item
            warnings = item.warnings
        if security.file_snapshot(staged) != files:
            raise ValueError('Staged skill changed during review')
    evidence = {'files': security._digests(files),
                'issues': _issues(review, warnings),
                'risk': review.risk if review is not None else
                        {'severity': 'LOW', 'recommendation': 'SAFE'}}
    return evidence, review


def _validated_request(arguments):
    if not isinstance(arguments, dict):
        raise ValueError('Expected tool arguments object')
    kind = arguments.get('target')
    host = arguments.get('host')
    if kind not in ('core', 'skill'):
        raise ValueError('target must be core or skill')
    host_profiles.resolve(host)
    if kind == 'core':
        if arguments.get('source') or arguments.get('name') or arguments.get('update'):
            raise ValueError('Core selection is fixed; do not provide source/name/update')
        return kind, host, None, None, False
    source, name = arguments.get('source'), arguments.get('name')
    if not isinstance(source, str) or not source.strip():
        raise ValueError('Expected staged source directory')
    if not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name):
        raise ValueError('Invalid skill name')
    if type(arguments.get('update', False)) is not bool:
        raise ValueError('update must be boolean')
    return kind, host, security.safe_path(source), name, arguments.get('update', False)


def _feature_lines(name, review, trusted_core):
    issues = review.issues if review else []
    known = False
    if name == 'tool-advisor' and len(issues) == 1:
        first = issues[0]
        known = (str(first.get('id')) == 'LP3' and
                 'file_write' in str(first.get('finding') or first.get('pattern') or ''))
    elif name == 'find-skills' and issues:
        known = all(str(issue.get('id')) == 'RP1' and
                    'npx skills' in str(issue.get('finding') or
                                        issue.get('pattern') or '').lower()
                    for issue in issues)
    if trusted_core and known:
        return list(security._MEDIUM_FEATURES[name])
    return ['Run only the documented features, subject to existing host permissions.']


def _review_text(kind, host, components):
    lines = ['Skill security review (' + host + ', ' + kind + ')']
    for component in components:
        name = component['name']
        evidence = component['evidence']
        issues = evidence['issues']
        lines.append(name + ': ' + ('MEDIUM — approval required'
                                     if component['medium'] else 'LOW/SAFE'))
        if component['medium']:
            for group in component['groups']:
                lines.append('  Reason: ' + group['reason'])
                lines.append('  Finding: ' + group['id'] + ' — ' +
                             str(group['count']) + ' occurrence(s)')
            lines.append('  After approval:')
            for feature in component['features']:
                lines.append('    - ' + feature)
        elif issues:
            lines.append('  ' + str(len(issues)) + ' low-severity observations.')
    lines.append('HIGH/CRITICAL, failed or incomplete scans block installation.')
    lines.append('Approval does not grant additional host permissions.')
    return '\n'.join(lines)


def inspect(arguments):
    """Return ephemeral snapshot identity and plain-language security review."""
    kind, host, source, name, update = _validated_request(arguments)
    scanner = security.scanner_executable(None)
    selected = []
    if kind == 'core':
        core = install_advisor.require_baseline(ROOT)['required_skills']
        _, bundle, _ = install_advisor._bundle(ROOT, core)
        for item in bundle:
            selected.append((item['name'], item['installed_files'], True))
        if [c[0] for c in selected] != core:
            raise ValueError('Missing required core skill')
    else:
        selected.append((name, security.file_snapshot(source), False))
    before = {name: dict(files) for name, files, _ in selected}
    components = []
    for skill, files, trusted in selected:
        evidence, review = _scan_payload(skill, files, scanner)
        components.append({
            'name': skill, 'evidence': evidence, 'medium': review is not None,
            'groups': security._review_groups(review.issues) if review else [],
            'features': _feature_lines(skill, review, trusted),
        })
    # Verify source still matches the inspected payloads.
    if kind == 'core':
        _, refreshed, _ = install_advisor._bundle(ROOT, [x[0] for x in selected])
        for item in refreshed:
            if item['installed_files'] != before[item['name']]:
                raise ValueError('Core source changed during security review')
    elif security.file_snapshot(source) != before[name]:
        raise ValueError('Skill source changed during security review')
    identity = {'target': kind, 'host': host,
                'source': str(source) if source else None, 'name': name,
                'update': update, 'components':
                    [{'name': c['name'], 'evidence': c['evidence']} for c in components]}
    return {
        'review_id': _digest(identity), 'summary': _review_text(kind, host, components),
        'requires_approval': any(c['medium'] for c in components),
        'components': components, 'snapshot': identity,
        'note': 'No stored approval. The installer will scan and verify again at activation.'
    }


def _review_validator(expected):
    by_name = {c['name']: c['evidence'] for c in expected['components']}
    def check(name, files, review, warnings):
        if name not in by_name:
            raise ValueError('Unexpected skill in activation: ' + name)
        actual = {'files': security._digests(files),
                  'issues': _issues(review, warnings),
                  'risk': review.risk if review else
                          {'severity': 'LOW', 'recommendation': 'SAFE'}}
        if actual != by_name[name]:
            raise ValueError('Scan findings or file contents changed since review: ' + name)
    return check


def activate(arguments, approved_tool):
    """Host-gated tool calls only; no caller-supplied 'approved' bool."""
    kind, host, source, name, update = _validated_request(arguments)
    proposed = arguments.get('review_id')
    summary = arguments.get('summary')
    if not isinstance(proposed, str) or not re.fullmatch('[0-9a-f]{64}', proposed):
        raise ValueError('Missing review_id from review_skill')
    if not isinstance(summary, str):
        raise ValueError('Missing exact summary from review_skill')
    current = inspect(arguments)
    if proposed != current['review_id'] or summary != current['summary']:
        raise ValueError('Security review changed. Re-run review_skill and approve the new findings.')
    if current['requires_approval'] != approved_tool:
        if current['requires_approval']:
            raise ValueError('MEDIUM requires host-native install_reviewed permission prompt')
        raise ValueError('LOW/SAFE should use install_safe; no manual approval needed')

    def handle_medium(review):
        if not approved_tool:
            raise ValueError('MEDIUM cannot be installed through install_safe')
        # The host gated the install_reviewed MCP call. Revalidation ensures
        # the approved summary matches exactly what the scanner returned.
        return review.warnings

    validator = _review_validator(current['snapshot'])
    if kind == 'skill':
        outcome = security.install_skill(
            source, host_profiles.default_skills_root(host), name, update=update,
            approval_handler=handle_medium, scan_validator=validator)
    else:
        import setup as workspace
        home = host_profiles.home_dir(host)
        hook = workspace.configure_security_hook(home, host, ROOT, install=False)
        if not hook.get('ready'):
            raise ValueError('Security hook not ready. Complete --setup-workspace and host hook approval first.')
        workspace.verify_security_hook(ROOT)
        core = install_advisor.require_baseline(ROOT)['required_skills']
        outcome = install_advisor.install_bundle(
            ROOT, host_profiles.default_skills_root(host), home,
            selected_names=core, host=host, approval_handler=handle_medium,
            scan_validator=validator)
        workspace.install(home, workspace.saved_rules(host), host)
    return {'installed': True, 'result': outcome,
            'host_permission': ('required by host for install_reviewed'
                                if approved_tool else 'not required; LOW/SAFE'),
            'note': 'Restart the host session to load new or updated global skills.'}


COMMON_FIELDS = {
    'target': {'type': 'string', 'enum': ['skill', 'core'],
               'description': 'core installs only the three required advisor skills'},
    'host': {'type': 'string', 'enum': ['codex', 'claude']},
    'source': {'type': 'string', 'description': 'Absolute staged directory (only for skill)'},
    'name': {'type': 'string', 'description': 'Skill name (only for skill)'},
    'update': {'type': 'boolean', 'description': 'Update a controlled installation (only for skill)'},
}
INSTALL_FIELDS = {**COMMON_FIELDS,
                  'review_id': {'type': 'string', 'description': 'Exact ID returned by review_skill'},
                  'summary': {'type': 'string', 'description': 'Exact user-visible security review from review_skill'}}


def tool_list():
    return [
        {'name': 'review_skill',
         'title': 'Review skill security',
         'description': 'Scan and group findings; show the risk, enabled features, and ephemeral review ID without installing anything.',
         'inputSchema': {'type': 'object', 'properties': COMMON_FIELDS, 'required': ['target', 'host']},
         'annotations': {'readOnlyHint': True}},
        {'name': 'install_safe',
         'title': 'Install reviewed LOW/SAFE skill',
         'description': 'Install only if an identical fresh scan is LOW/SAFE. Reject all MEDIUM or higher findings.',
         'inputSchema': {'type': 'object', 'properties': INSTALL_FIELDS,
                         'required': ['target', 'host', 'review_id', 'summary']},
         'annotations': {'readOnlyHint': False}},
        {'name': 'install_reviewed',
         'title': 'Install MEDIUM skill after human approval',
         'description': 'Always request a real host-native human approval. Read the exact summary before allowing. A matching fresh scan is mandatory.',
         'inputSchema': {'type': 'object', 'properties': INSTALL_FIELDS,
                         'required': ['target', 'host', 'review_id', 'summary']},
         'annotations': {'readOnlyHint': False},
         '_meta': {'anthropic/requiresUserInteraction': True}},
    ]


def _tool_call(params):
    if not isinstance(params, dict):
        raise ValueError('Malformed MCP tool call')
    tool = params.get('name')
    args = params.get('arguments') or {}
    if tool == 'review_skill':
        return inspect(args)
    if tool == 'install_safe':
        return activate(args, approved_tool=False)
    if tool == 'install_reviewed':
        return activate(args, approved_tool=True)
    raise ValueError('Unknown tool: ' + str(tool))


def dispatch(message):
    """Pure MCP JSON-RPC dispatcher. Never print non-protocol text to stdout."""
    method = message.get('method')
    if method == 'initialize':
        params = message.get('params') or {}
        requested = params.get('protocolVersion', PROTOCOL)
        negotiated = requested if requested in KNOWN_PROTOCOLS else PROTOCOL
        return {'protocolVersion': negotiated, 'capabilities': {'tools': {}},
                'serverInfo': {'name': 'dev-workspace-skill-security', 'version': '1.0.0'}}
    if method == 'ping':
        return {}
    if method == 'tools/list':
        return {'tools': tool_list()}
    if method == 'tools/call':
        try:
            payload = _tool_call(message.get('params'))
            return {'content': [{'type': 'text', 'text': json.dumps(payload)}],
                    'isError': False}
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return {'content': [{'type': 'text', 'text': str(exc)}],
                    'isError': True}
    raise ValueError('Unsupported MCP method: ' + str(method))


def serve():
    for raw in sys.stdin.buffer:
        if len(raw) > 1024 * 1024:
            return 1
        try:
            message = json.loads(raw)
            if not isinstance(message, dict):
                raise ValueError('MCP message must be a JSON object')
            if 'id' not in message:  # notifications don't receive responses
                continue
            reply = {'jsonrpc': '2.0', 'id': message['id']}
            try:
                reply['result'] = dispatch(message)
            except (ValueError, TypeError, KeyError) as exc:
                reply['error'] = {'code': -32601, 'message': str(exc)}
        except (ValueError, TypeError, KeyError):
            reply = {'jsonrpc': '2.0', 'id': None,
                     'error': {'code': -32700, 'message': 'Invalid JSON-RPC request'}}
        sys.stdout.write(json.dumps(reply, separators=(',', ':')) + '\n')
        sys.stdout.flush()
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stdio', action='store_true', help='Serve MCP over stdio (default)')
    parser.parse_args()
    raise SystemExit(serve())
