#!/usr/bin/env python3
"""Record advisor scope, confirmed combinations and evidence-backed task progress.

This local ledger does not launch agents, inspect skills or authenticate a user.
The coordinator records actual consent and verification evidence from the host.
"""
import argparse
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile


SCHEMA = 1
MAX_BYTES = 8 * 1024 * 1024
STATUSES = {'pending', 'in_progress', 'blocked', 'review', 'done'}


def now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(label + ' must be nonempty text')
    return value


def strings(value, label, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError(label + ' must be ' + ('a nonempty' if nonempty else 'an') + ' array')
    for item in value:
        text(item, label + ' item')


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,79}', value):
        raise ValueError('Invalid role/task ID')


def validate_brief(brief):
    if not isinstance(brief, dict):
        raise ValueError('Brief must be a JSON object')
    text(brief.get('goal'), 'goal')
    for key in ('deliverables', 'constraints', 'success_criteria', 'open_questions'):
        strings(brief.get(key), key, key in ('deliverables', 'success_criteria'))
    if 'assumptions' in brief:
        strings(brief['assumptions'], 'assumptions')


def validate_proposal(proposal):
    if not isinstance(proposal, dict):
        raise ValueError('Proposal must be a JSON object')
    indexes = {}
    for collection in ('roles', 'tasks'):
        rows = proposal.get(collection)
        if not isinstance(rows, list) or not rows:
            raise ValueError(collection + ' must be a nonempty array')
        index = {}
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError(collection + ' entries must be objects')
            identifier(row.get('id'))
            if row['id'] in index:
                raise ValueError('Duplicate ' + collection + ' ID: ' + row['id'])
            index[row['id']] = row
        indexes[collection] = index
    for role in proposal['roles']:
        for key in ('job', 'component', 'source', 'revision', 'reason'):
            text(role.get(key), key)
        if role.get('kind') not in ('skill', 'agent', 'tool', 'manual'):
            raise ValueError('Invalid role kind')
        if role.get('availability') not in ('ready', 'needs-install', 'unverified'):
            raise ValueError('Invalid role availability')
        strings(role.get('alternatives'), 'alternatives')
    for task in proposal['tasks']:
        text(task.get('title'), 'task title')
        identifier(task.get('role'))
        if task['role'] not in indexes['roles']:
            raise ValueError('Unknown task role: ' + task['role'])
        strings(task.get('acceptance'), 'acceptance', True)
        strings(task.get('depends_on'), 'depends_on')
        if len(set(task['depends_on'])) != len(task['depends_on']):
            raise ValueError('Duplicate dependency')
        for dependency in task['depends_on']:
            if dependency not in indexes['tasks']:
                raise ValueError('Unknown task dependency: ' + dependency)
    # Iterative topological traversal also handles deeply nested plans.
    remaining = {key: set(row['depends_on']) for key, row in indexes['tasks'].items()}
    while remaining:
        ready = {key for key, deps in remaining.items() if not deps}
        if not ready:
            raise ValueError('Task dependencies contain a cycle')
        remaining = {key: deps - ready for key, deps in remaining.items() if key not in ready}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(brief, proposal):
    return hashlib.sha256(canonical({'brief': brief, 'proposal': proposal})).hexdigest()


def safe_path(path):
    path = Path(os.path.abspath(path))
    for part in (*reversed(path.parents), path):
        if part.is_symlink():
            raise ValueError('Refusing symlink path: ' + str(part))
    return path


def read_bytes(path):
    path = safe_path(path)
    if not stat.S_ISREG(path.stat(follow_symlinks=False).st_mode):
        raise ValueError('Expected a regular JSON file')
    # A FIFO can otherwise block open() before fstat() gets a chance to reject it.
    # NONBLOCK also protects the gap between the path check and opening the file.
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0))
    with os.fdopen(fd, 'rb') as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError('Expected a regular JSON file')
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError('JSON file exceeds 8 MiB; archive it explicitly before continuing')
    return data


def decode(data):
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('Duplicate JSON key: ' + key)
            obj[key] = value
        return obj

    def invalid_constant(value):
        raise ValueError('Invalid JSON constant: ' + value)

    return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid_constant)


def read_json(path):
    return decode(read_bytes(path))


def validate_state(state, project):
    if not isinstance(state, dict) or state.get('schema_version') != SCHEMA:
        raise ValueError('Missing or unsupported ledger schema')
    if state.get('project') != str(project):
        raise ValueError('Ledger belongs to a different project path')
    text(state.get('goal'), 'ledger goal')
    if type(state.get('revision')) is not int or state['revision'] < 1:
        raise ValueError('Invalid ledger revision')
    if state.get('phase') not in ('interview', 'proposed', 'confirmed', 'executing', 'complete'):
        raise ValueError('Invalid ledger phase')
    required = {'brief', 'proposal', 'digest', 'confirmation', 'completed_at'}
    if not required <= state.keys():
        raise ValueError('Ledger is missing required fields')
    for field in ('history', 'archives'):
        if not isinstance(state.get(field), list):
            raise ValueError('Invalid ledger ' + field)
    if not isinstance(state.get('roles'), dict) or not isinstance(state.get('tasks'), dict):
        raise ValueError('Invalid role/task state')
    brief, proposal = state.get('brief'), state.get('proposal')
    if brief is not None:
        validate_brief(brief)
    if proposal is None:
        if state.get('digest') is not None or state.get('confirmation') is not None or state['roles'] or state['tasks']:
            raise ValueError('Orphaned selection state')
        if state['phase'] != 'interview' or state['completed_at'] is not None:
            raise ValueError('Ledger phase requires a proposal and verified task state')
        return
    if brief is None or brief['open_questions']:
        raise ValueError('Proposal requires a complete brief')
    validate_proposal(proposal)
    if state.get('digest') != digest(brief, proposal):
        raise ValueError('Brief/proposal changed outside the ledger; confirmation is stale')
    if set(state['roles']) != {r['id'] for r in proposal['roles']} or set(state['tasks']) != {t['id'] for t in proposal['tasks']}:
        raise ValueError('Role/task state does not match the proposal')
    confirmation = state.get('confirmation')
    if state['phase'] == 'interview' or (state['phase'] == 'proposed') != (confirmation is None):
        raise ValueError('Ledger phase and confirmation disagree')
    if confirmation is not None:
        if not isinstance(confirmation, dict) or confirmation.get('digest') != state['digest']:
            raise ValueError('Confirmation does not match the proposal')
        text(confirmation.get('evidence'), 'confirmation evidence')
    for role in state['roles'].values():
        if not isinstance(role, dict) or type(role.get('ready')) is not bool:
            raise ValueError('Invalid role readiness')
        if role['ready']:
            if confirmation is None:
                raise ValueError('Role readiness requires confirmation')
            text(role.get('evidence'), 'role readiness evidence')
    for task in state['tasks'].values():
        if not isinstance(task, dict) or task.get('status') not in STATUSES or not isinstance(task.get('evidence'), list):
            raise ValueError('Invalid task state')
        if task['status'] in ('in_progress', 'review', 'done'):
            text(task.get('actor'), 'task actor')
        if task['status'] == 'done':
            text(task.get('verified_at'), 'verification timestamp')
            if not task['evidence']:
                raise ValueError('Done task lacks evidence')
    if state['phase'] == 'complete':
        text(state['completed_at'], 'completion timestamp')
        if not all(task['status'] == 'done' for task in state['tasks'].values()):
            raise ValueError('Complete ledger has unfinished tasks')
    elif state['completed_at'] is not None:
        raise ValueError('Completion timestamp requires complete phase')


@contextmanager
def locked(directory):
    path = safe_path(directory / '.lock')
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
    except FileExistsError as exc:
        raise ValueError('Ledger is locked by another writer; inspect the lock before retrying') from exc
    identity = os.fstat(fd)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump({'pid': os.getpid(), 'created_at': now()}, stream)
        yield
    finally:
        # Never delete a lock replaced by another process.
        if path.exists() and not path.is_symlink():
            current = path.stat()
            if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                path.unlink()


def write_state(path, state, before):
    encoded = (json.dumps(state, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')
    if len(encoded) > MAX_BYTES:
        raise ValueError('Ledger exceeds 8 MiB; archive it explicitly before continuing')
    safe_path(path)
    fd, name = tempfile.mkstemp(prefix='.state-', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        safe_path(path)
        current = read_bytes(path) if path.exists() else None
        if current != before:
            raise ValueError('Ledger changed during this command; reload before retrying')
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def event(state, action, **values):
    state['history'].append({'at': now(), 'action': action, **values})


def require_confirmed(state):
    if not state.get('proposal') or not state.get('confirmation') or state['confirmation']['digest'] != state['digest']:
        raise ValueError('Confirm the current brief and combination before preparing or starting work')


def archive_selection(state):
    if any(t['status'] == 'in_progress' for t in state['tasks'].values()):
        raise ValueError('Cannot change scope or combination while a task is running; record it blocked first')
    if state['proposal'] is not None:
        fields = ('brief', 'proposal', 'digest', 'confirmation', 'roles', 'tasks', 'phase', 'completed_at')
        state['archives'].append({'archived_at': now(), **{k: deepcopy(state[k]) for k in fields}})
    state.update(proposal=None, digest=None, confirmation=None, roles={}, tasks={}, completed_at=None)


def task_spec(state, task_id):
    identifier(task_id)
    for task in state['proposal']['tasks']:
        if task['id'] == task_id:
            return task
    raise ValueError('Unknown task: ' + task_id)


def dependencies_done(state, spec):
    pending = [dep for dep in spec['depends_on'] if state['tasks'][dep]['status'] != 'done']
    if pending:
        raise ValueError('Task dependencies are not verified done: ' + ', '.join(pending))


def mutate(state, args):
    command = args.command
    if command == 'brief':
        brief = read_json(args.file)
        validate_brief(brief)
        if brief == state['brief']:
            return False
        archive_selection(state)
        state.update(brief=brief, goal=brief['goal'], phase='interview')
        event(state, 'brief')
    elif command == 'propose':
        proposal = read_json(args.file)
        validate_proposal(proposal)
        if state['brief'] is None:
            raise ValueError('Capture the brief before proposing a combination')
        if state['brief']['open_questions']:
            raise ValueError('Resolve the brief open questions before proposing a combination')
        if proposal == state['proposal']:
            return False
        archive_selection(state)
        state.update(proposal=proposal, digest=digest(state['brief'], proposal), phase='proposed')
        state['roles'] = {r['id']: {'ready': False, 'evidence': None, 'verified_at': None} for r in proposal['roles']}
        state['tasks'] = {t['id']: {'status': 'pending', 'actor': None, 'evidence': [], 'verified_at': None}
                          for t in proposal['tasks']}
        event(state, 'propose', digest=state['digest'])
    elif command == 'confirm':
        text(args.evidence, 'confirmation evidence')
        if not state['proposal'] or args.digest != state['digest']:
            raise ValueError('Confirmation digest is stale or no proposal exists')
        if state['confirmation'] is not None:
            return False
        state['confirmation'] = {'digest': args.digest, 'evidence': args.evidence, 'at': now()}
        state['phase'] = 'confirmed'
        event(state, 'confirm', digest=args.digest, evidence=args.evidence)
    else:
        require_confirmed(state)
        if command == 'ready':
            text(args.evidence, 'readiness evidence')
            if args.role not in state['roles']:
                raise ValueError('Unknown role: ' + args.role)
            state['roles'][args.role] = {'ready': True, 'evidence': args.evidence, 'verified_at': now()}
            event(state, 'ready', role=args.role, evidence=args.evidence)
        elif command == 'start':
            text(args.actor, 'actor')
            spec = task_spec(state, args.task)
            task = state['tasks'][args.task]
            if not state['roles'][spec['role']]['ready']:
                raise ValueError('Role is not verified ready: ' + spec['role'])
            if task['status'] not in ('pending', 'blocked'):
                raise ValueError('Task is already claimed, awaiting review or complete')
            dependencies_done(state, spec)
            task.update(status='in_progress', actor=args.actor, verified_at=None)
            state.update(phase='executing', completed_at=None)
            event(state, 'start', task=args.task, actor=args.actor)
        elif command == 'update':
            text(args.evidence, 'task evidence')
            spec = task_spec(state, args.task)
            task = state['tasks'][args.task]
            if args.status == 'review' and task['status'] != 'in_progress':
                raise ValueError('Only an in-progress task can enter review')
            if args.status == 'done':
                if task['status'] != 'review':
                    raise ValueError('Task must enter review before verified completion')
                dependencies_done(state, spec)
            prior = task['status']
            task['evidence'].append({'at': now(), 'status': args.status, 'text': args.evidence})
            task.update(status=args.status, verified_at=now() if args.status == 'done' else None)
            event(state, 'update', task=args.task, status=args.status, evidence=args.evidence)
            state.update(phase='executing', completed_at=None)
            if prior == 'done' and args.status == 'blocked':
                invalid = {args.task}
                while True:
                    descendants = {t['id'] for t in state['proposal']['tasks'] if invalid.intersection(t['depends_on'])}
                    if descendants <= invalid:
                        break
                    invalid.update(descendants)
                for key in sorted(invalid - {args.task}):
                    dependent = state['tasks'][key]
                    if dependent['status'] != 'pending':
                        evidence = 'Reverify after reopened dependency: ' + args.task
                        dependent.update(status='blocked', verified_at=None)
                        dependent['evidence'].append({'at': now(), 'status': 'blocked', 'text': evidence})
                        event(state, 'invalidate', task=key, evidence=evidence)
        elif command == 'complete':
            if not all(t['status'] == 'done' for t in state['tasks'].values()):
                raise ValueError('All tasks must be verified done before completion')
            if state['phase'] == 'complete':
                return False
            state.update(phase='complete', completed_at=now())
            event(state, 'complete')
    return True


def execute(args):
    project = safe_path(args.project)
    if not project.is_dir():
        raise ValueError('Project must be an existing directory')
    directory = safe_path(project / '.tool-advisor')
    path = safe_path(directory / 'state.json')
    if args.command == 'status':
        state = read_json(path)
        validate_state(state, project)
        return state
    if args.command == 'init':
        text(args.goal, 'goal')
        directory.mkdir(mode=0o700, exist_ok=True)
    elif not directory.is_dir():
        raise ValueError('Initialize this project ledger first')
    with locked(directory):
        ignore = safe_path(directory / '.gitignore')
        if ignore.exists() and read_bytes(ignore).strip() != b'*':
            raise ValueError('Existing .tool-advisor/.gitignore differs; preserve and reconcile it before writing private state')
        if args.command != 'init' and not ignore.exists():
            raise ValueError('Missing .tool-advisor/.gitignore; restore its * rule before writing private state')
        before = read_bytes(path) if path.exists() else None
        if args.command == 'init':
            if before is not None:
                raise ValueError('Ledger already exists; use status to resume it')
            if not ignore.exists():
                with ignore.open('x', encoding='utf-8') as stream:
                    stream.write('*\n')
            state = {'schema_version': SCHEMA, 'project': str(project), 'revision': 0,
                     'goal': args.goal, 'phase': 'interview', 'brief': None,
                     'proposal': None, 'digest': None, 'confirmation': None,
                     'roles': {}, 'tasks': {}, 'history': [], 'archives': [],
                     'completed_at': None}
            event(state, 'init', goal=args.goal)
        else:
            if before is None:
                raise ValueError('Initialize this project ledger first')
            state = decode(before)
            validate_state(state, project)
            if not mutate(state, args):
                return state
        state['revision'] += 1
        validate_state(state, project)
        write_state(path, state, before)
        return state


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path.cwd())
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('init').add_argument('--goal', required=True)
    for command in ('brief', 'propose'):
        commands.add_parser(command).add_argument('--file', type=Path, required=True)
    confirm = commands.add_parser('confirm')
    confirm.add_argument('--digest', required=True)
    confirm.add_argument('--evidence', required=True)
    ready = commands.add_parser('ready')
    ready.add_argument('--role', required=True)
    ready.add_argument('--evidence', required=True)
    start = commands.add_parser('start')
    start.add_argument('--task', required=True)
    start.add_argument('--actor', required=True)
    update = commands.add_parser('update')
    update.add_argument('--task', required=True)
    update.add_argument('--status', choices=('blocked', 'review', 'done'), required=True)
    update.add_argument('--evidence', required=True)
    commands.add_parser('status')
    commands.add_parser('complete')
    try:
        print(json.dumps(execute(parser.parse_args(argv)), indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
