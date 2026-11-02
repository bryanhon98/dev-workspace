"""Behavior checks for the project-local advisor state machine."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'advisor.py'


class AdvisorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.project = Path(self.tmp.name)
        self.brief = {
            'goal': 'Research and prepare a workshop',
            'deliverables': ['A sourced outline', 'Workshop slides'],
            'constraints': ['Use accessible sources'],
            'success_criteria': ['Every factual claim has a source'],
            'open_questions': [],
        }
        self.proposal = {
            'roles': [{
                'id': 'researcher', 'job': 'Source research',
                'component': 'Research skill', 'kind': 'skill',
                'source': 'https://example.org/research', 'revision': 'v1',
                'availability': 'ready', 'reason': 'Matches the input and output',
                'alternatives': ['Native search with manual source review'],
            }],
            'tasks': [
                {'id': 'research', 'title': 'Research the topic', 'role': 'researcher',
                 'depends_on': [], 'acceptance': ['Citations checked']},
                {'id': 'outline', 'title': 'Prepare the outline', 'role': 'researcher',
                 'depends_on': ['research'], 'acceptance': ['Outline matches sources']},
            ],
        }

    def command(self, *args, ok=True):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), '--project', str(self.project), *args],
            text=True, capture_output=True)
        if ok:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        return result.stderr

    def send(self, command, value, ok=True):
        path = self.project / ('input-' + command + '.json')
        path.write_text(json.dumps(value), encoding='utf-8')
        return self.command(command, '--file', str(path), ok=ok)

    def prepare(self, confirmed=True, ready=True):
        self.command('init', '--goal', self.brief['goal'])
        self.send('brief', self.brief)
        state = self.send('propose', self.proposal)
        if confirmed:
            self.command('confirm', '--digest', state['digest'], '--evidence',
                         'User approved this exact combination in message 4')
        if ready:
            self.command('ready', '--role', 'researcher', '--evidence',
                         'Read full skill; native search and source access verified')

    def finish_task(self, task):
        self.command('start', '--task', task, '--actor', 'worker-1')
        self.command('update', '--task', task, '--status', 'review',
                     '--evidence', 'Deliverable written; report at output/report.md')
        return self.command('update', '--task', task, '--status', 'done',
                            '--evidence', 'Coordinator verified acceptance criteria')

    def state_bytes(self):
        return (self.project / '.tool-advisor' / 'state.json').read_bytes()

    def test_status_does_not_create_state(self):
        self.command('status', ok=False)
        self.assertEqual(list(self.project.iterdir()), [])

    def test_init_and_resume_preserve_goal_and_history(self):
        first = self.command('init', '--goal', 'A specific goal')
        before = self.state_bytes()
        self.assertEqual(first['goal'], 'A specific goal')
        self.assertTrue(first['history'])
        self.assertEqual(self.command('status'), first)
        self.command('init', '--goal', 'Another goal', ok=False)
        self.assertEqual(self.state_bytes(), before)
        self.assertIn('*', (self.project / '.tool-advisor' / '.gitignore').read_text())

    def test_complete_workflow_records_actor_evidence_and_survives_new_process(self):
        self.prepare()
        one = self.finish_task('research')
        self.assertEqual(one['tasks']['research']['actor'], 'worker-1')
        self.assertEqual(one['tasks']['research']['status'], 'done')
        self.assertTrue(one['tasks']['research']['evidence'])
        self.assertIn('research', self.command('status')['tasks'])
        self.finish_task('outline')
        complete = self.command('complete')
        self.assertEqual(complete['phase'], 'complete')
        self.assertTrue(complete['completed_at'])

    def test_proposal_waits_for_complete_interview(self):
        self.command('init', '--goal', self.brief['goal'])
        self.brief['open_questions'] = ['Who is the audience?']
        self.send('brief', self.brief)
        self.assertIn('open questions', self.send('propose', self.proposal, ok=False))

    def test_proposal_requires_brief(self):
        self.command('init', '--goal', self.brief['goal'])
        self.send('propose', self.proposal, ok=False)

    def test_no_start_before_current_confirmation(self):
        self.prepare(confirmed=False, ready=False)
        self.assertIn('confirm', self.command('start', '--task', 'research',
                                            '--actor', 'worker', ok=False).lower())
        self.command('ready', '--role', 'researcher', '--evidence', 'Ready', ok=False)

    def test_declared_ready_is_not_verified_readiness(self):
        self.prepare(ready=False)
        self.assertIn('ready', self.command('start', '--task', 'research',
                                          '--actor', 'worker', ok=False).lower())

    def test_confirmation_rejects_stale_digest_and_blank_evidence(self):
        self.prepare(confirmed=False, ready=False)
        digest = self.command('status')['digest']
        self.command('confirm', '--digest', '0' * 64, '--evidence', 'Yes', ok=False)
        self.command('confirm', '--digest', digest, '--evidence', '  ', ok=False)
        self.command('start', '--task', 'research', '--actor', 'worker', ok=False)

    def test_changed_brief_invalidates_confirmation_and_archives_old_plan(self):
        self.prepare()
        old = self.command('status')
        self.brief['constraints'].append('No paid tools')
        changed = self.send('brief', self.brief)
        self.assertIsNone(changed['confirmation'])
        self.assertIsNone(changed['proposal'])
        self.assertTrue(changed['archives'])
        self.assertEqual(changed['archives'][-1]['digest'], old['digest'])
        self.command('start', '--task', 'research', '--actor', 'worker', ok=False)

    def test_changed_proposal_preserves_completed_work_in_archive(self):
        self.prepare()
        self.finish_task('research')
        old = self.command('status')
        self.proposal['roles'][0]['revision'] = 'v2'
        new = self.send('propose', self.proposal)
        self.assertNotEqual(old['digest'], new['digest'])
        self.assertIsNone(new['confirmation'])
        self.assertEqual(new['archives'][-1]['tasks']['research']['status'], 'done')
        self.assertEqual(new['tasks']['research']['status'], 'pending')
        self.assertGreater(len(new['history']), len(old['history']))
        self.command('confirm', '--digest', old['digest'], '--evidence', 'Old yes', ok=False)

    def test_identical_proposal_does_not_discard_work_or_confirmation(self):
        self.prepare()
        self.finish_task('research')
        before = self.state_bytes()
        self.send('propose', copy.deepcopy(self.proposal))
        self.assertEqual(self.state_bytes(), before)

    def test_material_edits_refused_while_task_running(self):
        self.prepare()
        self.command('start', '--task', 'research', '--actor', 'worker')
        before = self.state_bytes()
        self.proposal['roles'][0]['revision'] = 'v2'
        self.send('propose', self.proposal, ok=False)
        self.brief['goal'] = 'Different goal'
        self.send('brief', self.brief, ok=False)
        self.assertEqual(self.state_bytes(), before)

    def test_dependencies_block_start_until_verified_done(self):
        self.prepare()
        self.command('start', '--task', 'outline', '--actor', 'worker', ok=False)
        self.command('start', '--task', 'research', '--actor', 'worker')
        self.command('update', '--task', 'research', '--status', 'review',
                     '--evidence', 'Output delivered')
        self.command('start', '--task', 'outline', '--actor', 'worker', ok=False)
        self.command('update', '--task', 'research', '--status', 'done',
                     '--evidence', 'Acceptance verified')
        self.command('start', '--task', 'outline', '--actor', 'worker')

    def test_task_cannot_be_claimed_twice(self):
        self.prepare()
        self.command('start', '--task', 'research', '--actor', 'worker-1')
        before = self.state_bytes()
        self.command('start', '--task', 'research', '--actor', 'worker-2', ok=False)
        self.assertEqual(self.state_bytes(), before)

    def test_completion_requires_review_and_nonempty_evidence(self):
        self.prepare()
        self.command('complete', ok=False)
        self.command('update', '--task', 'research', '--status', 'done',
                     '--evidence', 'Guessed', ok=False)
        self.command('start', '--task', 'research', '--actor', 'worker')
        self.command('update', '--task', 'research', '--status', 'done',
                     '--evidence', 'Claimed complete', ok=False)
        self.command('update', '--task', 'research', '--status', 'review',
                     '--evidence', ' ', ok=False)
        self.command('update', '--task', 'research', '--status', 'review',
                     '--evidence', 'Output available')
        self.command('update', '--task', 'research', '--status', 'done',
                     '--evidence', '', ok=False)

    def test_blocked_task_can_resume_with_history(self):
        self.prepare()
        self.command('start', '--task', 'research', '--actor', 'worker-1')
        self.command('update', '--task', 'research', '--status', 'blocked',
                     '--evidence', 'Source server unavailable')
        state = self.command('start', '--task', 'research', '--actor', 'worker-2')
        self.assertEqual(state['tasks']['research']['actor'], 'worker-2')
        self.assertTrue(any(e.get('evidence') == 'Source server unavailable'
                            for e in state['history']))

    def test_reopening_done_invalidates_downstream_verification(self):
        self.prepare()
        self.finish_task('research')
        self.finish_task('outline')
        self.command('complete')
        state = self.command('update', '--task', 'research', '--status', 'blocked',
                             '--evidence', 'Source was retracted')
        self.assertNotEqual(state['phase'], 'complete')
        self.assertIsNone(state['completed_at'])
        self.assertEqual(state['tasks']['outline']['status'], 'blocked')
        self.assertTrue(state['tasks']['outline']['evidence'])
        self.command('complete', ok=False)
        self.command('start', '--task', 'outline', '--actor', 'worker', ok=False)

    def test_unknown_duplicate_and_cyclic_references_are_rejected(self):
        self.command('init', '--goal', self.brief['goal'])
        self.send('brief', self.brief)
        for edit in ['unknown-dep', 'cycle', 'duplicate-task', 'unknown-role', 'duplicate-role']:
            p = copy.deepcopy(self.proposal)
            if edit == 'unknown-dep': p['tasks'][0]['depends_on'] = ['missing']
            elif edit == 'cycle': p['tasks'][0]['depends_on'] = ['outline']
            elif edit == 'duplicate-task': p['tasks'].append(p['tasks'][0])
            elif edit == 'unknown-role': p['tasks'][0]['role'] = 'missing'
            else: p['roles'].append(p['roles'][0])
            with self.subTest(edit=edit): self.send('propose', p, ok=False)

    def test_malformed_briefs_and_proposals_do_not_change_state(self):
        self.prepare()
        before = self.state_bytes()
        for bad in [None, [], {}, {'goal': 'Only a title'}, dict(self.brief, deliverables='text'),
                    dict(self.brief, success_criteria=[]), dict(self.brief, goal='')]:
            with self.subTest(brief=bad): self.send('brief', bad, ok=False)
        for bad in [None, [], {}, dict(self.proposal, tasks=[]),
                    dict(self.proposal, roles='researcher')]:
            with self.subTest(proposal=bad): self.send('propose', bad, ok=False)
        self.assertEqual(self.state_bytes(), before)

    def test_invalid_role_and_task_fields_are_rejected(self):
        self.prepare()
        for key, value in [('id', '../escape'), ('kind', 'plugin'), ('availability', 'maybe'),
                           ('revision', None), ('alternatives', 'other'), ('reason', '')]:
            p = copy.deepcopy(self.proposal)
            p['roles'][0][key] = value
            with self.subTest(role_field=key): self.send('propose', p, ok=False)
        p = copy.deepcopy(self.proposal)
        p['tasks'][0]['acceptance'] = []
        self.send('propose', p, ok=False)

    def test_invalid_json_duplicate_keys_and_corrupt_state_are_refused(self):
        self.prepare()
        path = self.project / 'broken.json'
        for content in ['{broken', '{"goal":"one","goal":"two"}', 'NaN']:
            path.write_text(content)
            self.command('brief', '--file', str(path), ok=False)
        state_path = self.project / '.tool-advisor' / 'state.json'
        state_path.write_text('{}')
        self.command('status', ok=False)
        self.assertEqual(state_path.read_text(), '{}')

    def test_symlink_state_directory_is_refused(self):
        elsewhere = self.project / 'elsewhere'
        elsewhere.mkdir()
        (self.project / '.tool-advisor').symlink_to(elsewhere, target_is_directory=True)
        self.command('init', '--goal', 'Goal', ok=False)
        self.assertEqual(list(elsewhere.iterdir()), [])

    def test_symlink_state_file_and_input_are_refused(self):
        self.prepare()
        input_file = self.project / 'brief-real.json'
        input_file.write_text(json.dumps(self.brief))
        link = self.project / 'brief-link.json'
        link.symlink_to(input_file)
        self.command('brief', '--file', str(link), ok=False)
        state_path = self.project / '.tool-advisor' / 'state.json'
        outside = self.project / 'outside.json'
        state_path.rename(outside)
        before = outside.read_bytes()
        state_path.symlink_to(outside)
        self.command('status', ok=False)
        self.command('ready', '--role', 'researcher', '--evidence', 'Ready', ok=False)
        self.assertEqual(outside.read_bytes(), before)

    def test_existing_lock_prevents_writes_and_is_not_removed(self):
        self.prepare()
        lock = self.project / '.tool-advisor' / '.lock'
        lock.write_text('another coordinator')
        before = self.state_bytes()
        self.assertIn('lock', self.command('start', '--task', 'research',
                                         '--actor', 'worker', ok=False).lower())
        self.assertEqual(lock.read_text(), 'another coordinator')
        self.assertEqual(self.state_bytes(), before)
        self.assertEqual(self.command('status')['phase'], 'confirmed')

    def test_existing_gitignore_cannot_leave_private_state_trackable(self):
        directory = self.project / '.tool-advisor'
        directory.mkdir()
        ignore = directory / '.gitignore'
        ignore.write_text('# Local rules\n!state.json\n')
        before = ignore.read_bytes()
        self.command('init', '--goal', 'Private goal', ok=False)
        self.assertEqual(ignore.read_bytes(), before)
        self.assertFalse((directory / 'state.json').exists())

    @unittest.skipUnless(hasattr(__import__('os'), 'mkfifo'), 'FIFO requires POSIX')
    def test_fifo_input_fails_without_hanging_or_leaving_lock(self):
        import os
        self.prepare()
        fifo = self.project / 'input.fifo'
        os.mkfifo(fifo)
        before = self.state_bytes()
        process = subprocess.Popen([sys.executable, str(SCRIPT), '--project', str(self.project),
                                    'brief', '--file', str(fifo)], text=True,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            self.fail('FIFO input blocked the ledger command')
        self.assertNotEqual(process.returncode, 0, stdout)
        self.assertIn('regular', stderr)
        self.assertFalse((self.project / '.tool-advisor' / '.lock').exists())
        self.assertEqual(self.state_bytes(), before)

    def test_complete_phase_without_selection_is_corrupt(self):
        state = self.command('init', '--goal', 'Goal')
        state.update(phase='complete', completed_at='2026-11-02T00:00:00Z')
        path = self.project / '.tool-advisor' / 'state.json'
        path.write_text(json.dumps(state))
        self.command('status', ok=False)
        self.command('complete', ok=False)

    def test_concurrent_claims_allow_only_one_actor(self):
        self.prepare()
        workers = [subprocess.Popen(
            [sys.executable, str(SCRIPT), '--project', str(self.project), 'start',
             '--task', 'research', '--actor', actor],
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for actor in ('worker-a', 'worker-b')]
        for worker in workers:
            worker.communicate(timeout=5)
        self.assertEqual(sorted(w.returncode for w in workers), [0, 1])
        state = self.command('status')
        self.assertEqual(state['tasks']['research']['status'], 'in_progress')
        claims = [e for e in state['history'] if e['action'] == 'start']
        self.assertEqual(len(claims), 1)

    def test_stale_snapshot_cannot_overwrite_new_state(self):
        self.prepare()
        path = self.project / '.tool-advisor' / 'state.json'
        before = path.read_bytes()
        stale = json.loads(before)
        self.command('start', '--task', 'research', '--actor', 'worker')
        current = path.read_bytes()
        module_path = ROOT / 'skills/custom/tool-advisor/scripts/ledger.py'
        spec = importlib.util.spec_from_file_location('advisor_ledger_test', module_path)
        module = importlib.util.module_from_spec(spec)
        previous = sys.dont_write_bytecode
        try:
            sys.dont_write_bytecode = True
            spec.loader.exec_module(module)
        finally:
            sys.dont_write_bytecode = previous
        with self.assertRaisesRegex(ValueError, 'changed during'):
            module.write_state(path, stale, before)
        self.assertEqual(path.read_bytes(), current)
        self.assertFalse(list(path.parent.glob('.state-*.tmp')))


if __name__ == '__main__':
    unittest.main()
