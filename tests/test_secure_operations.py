"""Controlled standalone skill installation security regression tests."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class SecureOperationsTests(unittest.TestCase):
    def test_only_complete_gap_free_low_report_can_auto_install(self):
        import copy
        import json
        import subprocess
        report = {
            'metadata': {'llm_requested': False},
            'analysis_completeness': {'is_complete': True, 'coverage_percent': 100},
            'components': [{'path': 'SKILL.md'}],
            'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE'},
            'issues': []}
        cases = [
            ({}, None),
            ({'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE',
                                 'max_issue_severity': 'NONE'}}, None),
            ({'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE',
                                 'max_issue_severity': 'NONE'},
              'issues': [{'id': 'X', 'severity': 'LOW'}]}, ValueError),
            ({'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE',
                                 'max_issue_severity': 'UNKNOWN'}}, ValueError),
            ({'issues': [{'id': 'X', 'severity': 'HIGH'}]}, self.mod.MediumApprovalRequired),
            ({'analysis_completeness': {'is_complete': True, 'coverage_percent': 100,
                                       'ledger_exceptions': [{'reason_code': 'reference_missing'}]}},
             self.mod.MediumApprovalRequired),
            ({'analysis_completeness': {'is_complete': False, 'coverage_percent': 60}},
             self.mod.MediumApprovalRequired),
            ({'analysis_completeness': None}, ValueError),
            ({'metadata': []}, ValueError),
            ({'risk_assessment': {'severity': 'UNKNOWN', 'recommendation': 'SAFE'}}, ValueError),
            ({'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE',
                                 'max_issue_severity': 'HIGH'}}, self.mod.MediumApprovalRequired),
            ({'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE',
                                 'max_issue_severity': 'MEDIUM'}}, self.mod.MediumApprovalRequired),
        ]
        for overrides, error in cases:
            with self.subTest(overrides=overrides):
                current = {**copy.deepcopy(report), **overrides}
                result = subprocess.CompletedProcess([], 0, json.dumps(current), '')
                with mock.patch.object(self.mod.subprocess, 'run', return_value=result):
                    if error:
                        with self.assertRaises(error):
                            self.mod.scan_skill(self.source, {'path': 'scanner'}, {'SKILL.md': b'x'})
                    else:
                        self.assertEqual(self.mod.scan_skill(
                            self.source, {'path': 'scanner'}, {'SKILL.md': b'x'}), [])

    def setUp(self):
        spec = importlib.util.spec_from_file_location('secure_operations',
                                                      ROOT / 'scripts/secure_operations.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.source = self.dir / 'downloaded/skill'
        self.source.mkdir(parents=True)
        (self.source / 'SKILL.md').write_text('---\nname: example\n---\nSimple\n')
        self.skills = self.dir / '.agents/skills'
        scanner = mock.patch.object(self.mod, 'scanner_executable',
                                    return_value={'path': '/verified/scanner', 'version': 'test'})
        scanner.start()
        self.addCleanup(scanner.stop)

    def test_install_scanned_staged_files(self):
        captured = []
        def scan(directory, scanner, expected):
            self.assertNotEqual(directory, self.source)
            self.assertEqual((directory / 'SKILL.md').read_bytes(), expected['SKILL.md'])
            self.assertFalse((self.skills / 'example').exists())
            captured.append(directory)
            return []
        with mock.patch.object(self.mod, 'scan_skill', side_effect=scan):
            result = self.mod.install_skill(self.source, self.skills, 'example')
        self.assertTrue(result['installed'])
        self.assertEqual(len(captured), 1)
        self.assertTrue((self.skills / 'example/SKILL.md').exists())
        self.assertFalse((self.skills.parent / 'reports').exists())

    def test_risky_scan_blocks_before_install(self):
        with mock.patch.object(self.mod, 'scan_skill', side_effect=ValueError('HIGH risk')):
            with self.assertRaisesRegex(ValueError, 'HIGH'):
                self.mod.install_skill(self.source, self.skills, 'example')
        self.assertFalse((self.skills / 'example').exists())

    def test_medium_review_reason_features_and_default_reject(self):
        review = self.mod.MediumApprovalRequired('tool-advisor',
            {'severity': 'LOW', 'recommendation': 'SAFE'},
            [{'id': 'LP3', 'severity': 'MEDIUM',
              'finding': 'Skill declares no tool scope but code capabilities were detected: file_write.'}])
        with mock.patch.object(self.mod.sys, 'stdin', mock.Mock(isatty=mock.Mock(return_value=True))), \
             mock.patch.object(self.mod.sys, 'stdout', mock.Mock(isatty=mock.Mock(return_value=True))), \
             mock.patch('builtins.input', return_value='') as choice, \
             mock.patch('builtins.print') as display:
            with self.assertRaisesRegex(ValueError, 'rejected'):
                self.mod.approve_medium(review, trusted_core=True)
        output = '\n'.join(str(call) for call in display.call_args_list)
        self.assertIn('can modify local files', output)
        self.assertIn('Save project plans and decisions', output)
        self.assertIn('Track tasks', output)
        choice.assert_called_once()

    def test_rp1_repeated_findings_grouped_and_explained(self):
        issues = [
            {'id': 'RP1', 'severity': 'MEDIUM', 'finding': 'npx skills',
             'explanation': 'npx commands without a version suffix create rug-pull risk.'}
            for _ in range(12)
        ]
        review = self.mod.MediumApprovalRequired(
            'find-skills', {'severity': 'LOW', 'recommendation': 'SAFE'}, issues)
        self.assertEqual(len(review.warnings), 12)
        with mock.patch.object(self.mod.sys, 'stdin',
                               mock.Mock(isatty=mock.Mock(return_value=True))), \
             mock.patch.object(self.mod.sys, 'stdout',
                               mock.Mock(isatty=mock.Mock(return_value=True))), \
             mock.patch('builtins.input', return_value='n'), \
             mock.patch('builtins.print') as display:
            with self.assertRaisesRegex(ValueError, 'rejected'):
                self.mod.approve_medium(review, trusted_core=True)
        lines = [str(call.args[0]) for call in display.call_args_list
                 if call.args]
        text = '\\n'.join(lines)
        self.assertIn('12 occurrence(s) in 1 distinct group(s)', text)
        self.assertEqual(text.count('Reason:'), 1)
        self.assertEqual(text.count('Finding:'), 1)
        self.assertIn('could fetch changed executable code', text)
        self.assertIn('Search for available agent skills', text)
        self.assertIn('controlled security workflow', text)
        self.assertIn('Direct skill installation remains subject to the security hook', text)
        self.assertNotIn('Reason: npx skills', text)

    def test_different_findings_not_silently_combined(self):
        groups = self.mod._review_groups([
            {'id': 'RP1', 'severity': 'MEDIUM', 'finding': 'npx skills'},
            {'id': 'RP1', 'severity': 'MEDIUM', 'finding': 'uvx tool'},
            {'id': 'LP3', 'severity': 'MEDIUM',
             'finding': 'code capabilities were detected: file_write'}])
        self.assertEqual(len(groups), 3)
        self.assertEqual([x['count'] for x in groups], [1, 1, 1])

    def test_unknown_finding_prefers_explanation_over_short_matched_command(self):
        groups = self.mod._review_groups([{
            'id': 'TEST', 'severity': 'MEDIUM',
            'finding': 'short pattern',
            'explanation': 'This instruction could access remote network services.'}])
        self.assertEqual(groups[0]['reason'],
                         'This instruction could access remote network services.')

    def test_find_skills_unexpected_finding_uses_generic_feature_summary(self):
        review = self.mod.MediumApprovalRequired(
            'find-skills', {'severity': 'MEDIUM', 'recommendation': 'CAUTION'},
            [{'id': 'E2', 'severity': 'MEDIUM', 'finding': 'Unexpected network access'}])
        with mock.patch.object(self.mod.sys, 'stdin',
                               mock.Mock(isatty=mock.Mock(return_value=True))), \
             mock.patch.object(self.mod.sys, 'stdout',
                               mock.Mock(isatty=mock.Mock(return_value=True))), \
             mock.patch('builtins.input', return_value='n'), \
             mock.patch('builtins.print') as display:
            with self.assertRaisesRegex(ValueError, 'rejected'):
                self.mod.approve_medium(review, trusted_core=True)
        text = '\\n'.join(str(c.args[0]) for c in display.call_args_list if c.args)
        self.assertNotIn('Search for available agent skills', text)
        self.assertIn('Unexpected network access', text)

    def test_medium_review_needs_local_terminal(self):
        review = self.mod.MediumApprovalRequired('tool-advisor',
            {'severity': 'LOW', 'recommendation': 'SAFE'},
            [{'id': 'LP3', 'severity': 'MEDIUM'}])
        with mock.patch.object(self.mod.sys, 'stdin', mock.Mock(isatty=mock.Mock(return_value=False))), \
             mock.patch('builtins.input') as prompt:
            with self.assertRaisesRegex(ValueError, 'interactive terminal'):
                self.mod.approve_medium(review)
            prompt.assert_not_called()

    def test_medium_review_can_approve_for_one_install_only(self):
        review = self.mod.MediumApprovalRequired('example',
            {'severity': 'MEDIUM', 'recommendation': 'CAUTION'},
            [{'id': 'LP3', 'severity': 'MEDIUM'}])
        with mock.patch.object(self.mod, 'scan_skill', side_effect=review), \
             mock.patch.object(self.mod, 'approve_medium',
                               return_value=review.warnings) as approve:
            out = self.mod.install_skill(self.source, self.skills, 'example')
        self.assertTrue(out['installed'])
        approve.assert_called_once()
        self.assertFalse((self.skills.parent / 'dev-workspace-security/approvals.json').exists())
        with mock.patch.object(self.mod, 'scan_skill', side_effect=review), \
             mock.patch.object(self.mod, 'approve_medium',
                               side_effect=ValueError('MEDIUM approval rejected')):
            with self.assertRaisesRegex(ValueError, 'rejected'):
                self.mod.install_skill(self.source, self.skills, 'example', update=True)
        self.assertTrue((self.skills / 'example/SKILL.md').is_file())

    def test_medium_reject_does_not_install(self):
        review = self.mod.MediumApprovalRequired('example',
            {'severity': 'LOW', 'recommendation': 'SAFE'},
            [{'id': 'LP3', 'severity': 'MEDIUM'}])
        with mock.patch.object(self.mod, 'scan_skill', side_effect=review), \
             mock.patch.object(self.mod, 'approve_medium',
                               side_effect=ValueError('MEDIUM approval rejected')):
            with self.assertRaisesRegex(ValueError, 'rejected'):
                self.mod.install_skill(self.source, self.skills, 'example')
        self.assertFalse((self.skills / 'example').exists())

    def test_high_requires_review_without_losing_findings(self):
        report = {
            'metadata': {'llm_requested': False},
            'analysis_completeness': {'is_complete': True, 'coverage_percent': 100},
            'execution_successful': True, 'suppressed_count': 0, 'suppressed': [],
            'components': [{'path': 'SKILL.md'}],
            'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE'},
            'issues': [{'id': 'danger', 'severity': 'HIGH'}]}
        completed = __import__('subprocess').CompletedProcess([], 0,
                    __import__('json').dumps(report), '')
        with mock.patch.object(self.mod.subprocess, 'run', return_value=completed):
            with self.assertRaisesRegex(self.mod.MediumApprovalRequired, 'high-risk'):
                self.mod.scan_skill(self.source, {'path': 'scanner'},
                                    {'SKILL.md': (self.source / 'SKILL.md').read_bytes()})

    def test_existing_skill_is_not_overwritten(self):
        existing = self.skills / 'example'
        existing.mkdir(parents=True)
        (existing / 'SKILL.md').write_text('User data')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.mod.install_skill(self.source, self.skills, 'example')
        self.assertEqual((existing / 'SKILL.md').read_text(), 'User data')

    def test_missing_scanner_blocks(self):
        with mock.patch.object(self.mod, 'scanner_executable',
                               side_effect=ValueError('scanner missing')):
            with self.assertRaisesRegex(ValueError, 'scanner missing'):
                self.mod.install_skill(self.source, self.skills, 'example')
        self.assertFalse((self.skills / 'example').exists())

    def test_symlink_in_source_blocks(self):
        external = self.dir / 'external.md'
        external.write_text('outside')
        link = self.source / 'outside.md'
        try:
            link.symlink_to(external)
        except (OSError, NotImplementedError):
            self.skipTest('Symlink not allowed on this host')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.mod.install_skill(self.source, self.skills, 'example')

    def test_invalid_name_blocks(self):
        with self.assertRaisesRegex(ValueError, 'Invalid skill name'):
            self.mod.install_skill(self.source, self.skills, '../example')



    def test_update_requires_existing_unmodified_managed_install(self):
        with mock.patch.object(self.mod, 'scan_skill', return_value=[]):
            self.mod.install_skill(self.source, self.skills, 'example')
            (self.source / 'SKILL.md').write_text('---\nname: example\n---\nnew content\n')
            result = self.mod.install_skill(self.source, self.skills, 'example', update=True)
        self.assertTrue(result['updated'])
        self.assertIn('new content', (self.skills / 'example/SKILL.md').read_text())
        (self.skills / 'example/SKILL.md').write_text('user customization')
        with self.assertRaisesRegex(ValueError, 'changed locally'):
            self.mod.install_skill(self.source, self.skills, 'example', update=True)
        self.assertEqual((self.skills / 'example/SKILL.md').read_text(), 'user customization')

    def test_clone_rejects_outside_destination_and_non_github_source(self):
        with self.assertRaisesRegex(ValueError, 'Only HTTPS GitHub'):
            self.mod.clone_repository('https://example.org/untrusted.git', 'new', self.dir)
        with self.assertRaises(ValueError):
            self.mod.clone_repository('https://github.com/example/demo.git', '../outside', self.dir)

    def test_clone_refuses_active_destinations_even_inside_workspace(self):
        for parent in ('.agents/skills', '.codex/skills', '.claude/plugins'):
            root = self.dir / parent
            root.mkdir(parents=True)
            with self.subTest(parent=parent), mock.patch.object(self.mod.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'active'):
                    self.mod.clone_repository('https://github.com/example/demo', 'new', root)
                run.assert_not_called()

    def test_clone_refuses_config_containers_and_configured_root_ancestors(self):
        for target in ('.agents', '.codex', '.claude'):
            with self.subTest(target=target), mock.patch.object(self.mod.subprocess, 'run') as run:
                with self.assertRaisesRegex(ValueError, 'active'):
                    self.mod.clone_repository('https://github.com/example/demo', target, self.dir)
                run.assert_not_called()
        configured = self.dir / 'custom-container' / 'skills'
        with mock.patch.object(self.mod.host_profiles, 'default_skills_root', return_value=configured), \
             mock.patch.object(self.mod.subprocess, 'run') as run:
            with self.assertRaisesRegex(ValueError, 'active'):
                self.mod.clone_repository('https://github.com/example/demo', 'custom-container', self.dir)
            run.assert_not_called()


    def _mock_clone(self, staged, with_skill=True, symlink=False):
        def git(command, **kwargs):
            destination = Path(command[-1])
            destination.mkdir(parents=True)
            if with_skill:
                skill = destination / 'sample'
                skill.mkdir()
                (skill / 'SKILL.md').write_text('---\nname: sample\n---\nSafe\n')
                if symlink:
                    (skill / 'link').symlink_to(skill / 'SKILL.md')
            else:
                (destination / 'Main.java').write_text('class Main {}')
            return __import__('subprocess').CompletedProcess(command, 0, '', '')
        return git

    def test_clone_stages_scans_and_releases_once(self):
        url = 'https://github.com/example/skill-demo.git'
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=self._mock_clone(None)), \
             mock.patch.object(self.mod, 'scan_skill', return_value=[]) as scan:
            result = self.mod.clone_repository(url, 'checked', self.dir)
        self.assertTrue(result['cloned'])
        self.assertEqual(scan.call_count, 1)
        self.assertTrue((self.dir / 'checked/sample/SKILL.md').is_file())

    def test_clone_scan_failure_retains_inactive_source_and_error(self):
        url = 'https://github.com/example/skill-demo.git'
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=self._mock_clone(None)), \
             mock.patch.object(self.mod, 'scan_skill', side_effect=ValueError('HIGH risk')):
            result = self.mod.clone_repository(url, 'unassessed', self.dir)
        self.assertTrue(result['inactive'])
        self.assertFalse(result['install_eligible'])
        self.assertEqual(result['failures'][0]['error'], 'HIGH risk')
        self.assertTrue((self.dir / 'unassessed/sample/SKILL.md').exists())

    def test_clone_reviews_all_payloads_after_critical_or_incomplete(self):
        def clone(command, **kwargs):
            root = Path(command[-1])
            for name in ('first', 'second', 'third'):
                folder = root / name
                folder.mkdir(parents=True)
                (folder / 'SKILL.md').write_text('---\nname: sample\n---\n')
            return __import__('subprocess').CompletedProcess(command, 0, '', '')
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=clone), \
             mock.patch.object(self.mod, 'scan_skill', side_effect=[
                 ValueError('CRITICAL'), ValueError('Incomplete'), []]) as scan:
            result = self.mod.clone_repository('https://github.com/example/demo', 'review', self.dir)
        self.assertEqual(scan.call_count, 3)
        self.assertIn('CRITICAL', str(result))
        self.assertIn('Incomplete', str(result))
        self.assertIn('third', str(result))
        self.assertTrue(result['inactive'])
        self.assertFalse(result['install_eligible'])
        self.assertTrue((self.dir / 'review').exists())

    def test_clone_changed_during_scan_is_not_released(self):
        def mutate(stage, scanner, expected):
            (stage / 'SKILL.md').write_text('changed')
            raise ValueError('scan failed')
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=self._mock_clone(None)), \
             mock.patch.object(self.mod, 'scan_skill', side_effect=mutate):
            with self.assertRaisesRegex(ValueError, 'changed during scanning'):
                self.mod.clone_repository('https://github.com/example/demo', 'unsafe', self.dir)
        self.assertFalse((self.dir / 'unsafe').exists())

    def test_clone_missing_scanner_retains_unassessed_inactive_files(self):
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=self._mock_clone(None)), \
             mock.patch.object(self.mod, 'scanner_executable', side_effect=ValueError('scanner missing')):
            result = self.mod.clone_repository('https://github.com/example/demo', 'unscanned', self.dir)
        self.assertEqual(result['failures'][0]['status'], 'unassessed')
        self.assertEqual(result['failures'][0]['error'], 'scanner missing')
        self.assertTrue(result['inactive'])
        self.assertFalse(result['install_eligible'])

    def test_clone_target_created_during_scan_is_not_overwritten(self):
        target = self.dir / 'occupied'
        def race(stage, scanner, expected):
            target.mkdir()
            (target / 'mine').write_text('keep')
            return []
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=self._mock_clone(None)), \
             mock.patch.object(self.mod, 'scan_skill', side_effect=race):
            with self.assertRaisesRegex(ValueError, 'Destination created'):
                self.mod.clone_repository('https://github.com/example/demo', 'occupied', self.dir)
        self.assertEqual((target / 'mine').read_text(), 'keep')

    def test_generic_clone_reports_limited_coverage(self):
        url = 'https://github.com/example/java-demo.git'
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=self._mock_clone(None, with_skill=False)), \
             mock.patch.object(self.mod, '_report_generic_repository',
                               return_value={'coverage': 'limited'}) as generic:
            result = self.mod.clone_repository(url, 'java-repo', self.dir)
        generic.assert_called_once()
        self.assertEqual(result['checks'][0]['coverage'], 'limited')
        self.assertTrue((self.dir / 'java-repo/Main.java').is_file())

if __name__ == '__main__':
    unittest.main()
