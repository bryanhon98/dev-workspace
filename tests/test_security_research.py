"""Research previews cannot grant installation eligibility."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class ResearchTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('security_research', ROOT / 'scripts/secure_operations.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.report = {
            'metadata': {'llm_requested': False},
            'analysis_completeness': {'is_complete': True, 'coverage_percent': 100},
            'execution_successful': True, 'suppressed_count': 0, 'suppressed': [],
            'components': [{'path': 'SKILL.md'}],
            'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE'}, 'issues': []}

    def result(self, report=None, code=0):
        return subprocess.CompletedProcess([], code, json.dumps(report or self.report), '')

    def test_url_preview_uses_static_scanner_and_never_authorizes_install(self):
        self.assertTrue(callable(getattr(self.mod, 'research_scan', None)), 'research_scan missing')
        def scan(command, **kwargs):
            self.assertEqual(command[1:3], ['scan', 'https://github.com/example/project'])
            self.assertIn('--no-llm', command)
            self.assertIn('--fail-on-incomplete', command)
            self.assertEqual(kwargs['timeout'], 600)
            return self.result()
        with mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner', 'version': 'test'}), mock.patch.object(self.mod.subprocess, 'run', side_effect=scan):
            result = self.mod.research_scan('https://github.com/example/project')
        self.assertFalse(result['install_eligible'])
        self.assertIsNone(result['verified_revision'])
        self.assertEqual(result['status'], 'preview-complete')

    def test_recovery_is_bounded_and_only_for_execution_failure(self):
        self.assertTrue(callable(getattr(self.mod, 'research_scan', None)), 'research_scan missing')
        bad = subprocess.CompletedProcess([], 2, '', 'parser unavailable')
        with mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner'}), mock.patch.object(self.mod.subprocess, 'run', side_effect=[bad, bad]) as run:
            result = self.mod.research_scan('https://github.com/example/project', retry=True)
        self.assertEqual(run.call_count, 2)
        self.assertEqual(result['status'], 'execution-error')
        self.assertFalse(result['install_eligible'])

    def test_high_findings_are_visible_and_not_retried(self):
        self.assertTrue(callable(getattr(self.mod, 'research_scan', None)), 'research_scan missing')
        self.report['issues'] = [{'id': 'X1', 'severity': 'HIGH', 'component': 'SKILL.md', 'finding': 'dangerous instruction'}]
        with mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner'}), mock.patch.object(self.mod.subprocess, 'run', return_value=self.result()) as run:
            result = self.mod.research_scan('https://github.com/example/project', retry=True)
        self.assertEqual(run.call_count, 1)
        self.assertEqual(result['status'], 'review-required')
        self.assertEqual(result['diagnostics']['issues'][0]['id'], 'X1')

    def test_invalid_json_and_incomplete_results_remain_ineligible(self):
        self.assertTrue(callable(getattr(self.mod, 'research_scan', None)), 'research_scan missing')
        self.report['analysis_completeness'] = {'is_complete': False, 'coverage_percent': 60, 'warnings': ['parser failed']}
        cases = [(subprocess.CompletedProcess([], 0, '<html>', ''), 'invalid-json'), (self.result(), 'incomplete')]
        for completed, expected in cases:
            with self.subTest(expected=expected), mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner'}), mock.patch.object(self.mod.subprocess, 'run', return_value=completed):
                result = self.mod.research_scan('https://github.com/example/project')
                self.assertEqual(result['status'], expected)
                self.assertFalse(result['install_eligible'])

    def test_research_rejects_nonrepository_urls_before_scanner(self):
        self.assertTrue(callable(getattr(self.mod, 'research_scan', None)), 'research_scan missing')
        for url in ['http://github.com/a/b', 'https://github.com/a/b?token=secret', 'https://evil.test/a/b', 'https://github.com/a/b/tree/main']:
            with self.subTest(url=url), mock.patch.object(self.mod, 'scanner_executable') as scanner:
                with self.assertRaises(ValueError):
                    self.mod.research_scan(url)
                scanner.assert_not_called()

    def test_local_inspection_is_read_only_and_hashes_exact_bytes(self):
        self.assertTrue(callable(getattr(self.mod, 'inspect_source', None)), 'inspect_source missing')
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)
            (path / 'SKILL.md').write_bytes(b'abc')
            result = self.mod.inspect_source(path)
            self.assertEqual(result['files'][0]['sha256'], 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')
            self.assertFalse(result['install_eligible'])
            self.assertEqual((path / 'SKILL.md').read_bytes(), b'abc')
            self.assertEqual(len(list(path.iterdir())), 1)

    def test_install_high_error_includes_finding_identity_and_location(self):
        self.report['issues'] = [{'id': 'X1', 'severity': 'HIGH', 'location': {'file': 'SKILL.md', 'start_line': 12}, 'finding': 'dangerous instruction'}]
        with mock.patch.object(self.mod.subprocess, 'run', return_value=self.result()):
            with self.assertRaisesRegex(ValueError, 'X1.*SKILL.md:12'):
                self.mod.scan_skill(Path('sample'), {'path': 'scanner'}, {'SKILL.md': b'abc'})

    def test_install_incomplete_diagnostics_show_coverage_and_parser_failure(self):
        self.report['analysis_completeness'] = {'is_complete': False, 'coverage_percent': 60, 'warnings': ['parser failed']}
        with mock.patch.object(self.mod.subprocess, 'run', return_value=self.result()):
            with self.assertRaisesRegex(ValueError, '60.*parser failed'):
                self.mod.scan_skill(Path('sample'), {'path': 'scanner'}, {'SKILL.md': b'abc'})

    def test_incomplete_report_cannot_hide_technical_failure(self):
        self.report['analysis_completeness'] = {'is_complete': False, 'coverage_percent': 60}
        for changed in ({'execution_successful': False}, {'components': None},
                        {'components': [{'path': 'wrong.md'}]},
                        {'components': [{'path': 'SKILL.md'}, {'path': 'SKILL.md'}]},
                        {'components': [{'path': 'SKILL.md'}, None]}):
            with self.subTest(changed=changed), mock.patch.object(
                    self.mod.subprocess, 'run', return_value=self.result({**self.report, **changed})):
                with self.assertRaises(ValueError) as rejected:
                    self.mod.scan_skill(Path('sample'), {'path': 'scanner'}, {'SKILL.md': b'abc'})
                self.assertNotIsInstance(rejected.exception, self.mod.MediumApprovalRequired)
        with mock.patch.object(self.mod.subprocess, 'run', return_value=self.result()):
            with self.assertRaises(self.mod.MediumApprovalRequired):
                self.mod.scan_skill(Path('sample'), {'path': 'scanner'}, {'SKILL.md': b'abc'})

    def test_full_file_coverage_with_gaps_is_not_complete_preview(self):
        for gap in ({'ledger_exceptions': [{'reason_code': 'reference_missing'}]},
                    {'warnings': ['parser limitation']}):
            complete = {**self.report['analysis_completeness'], **gap}
            with self.subTest(gap=gap), mock.patch.object(
                    self.mod, 'scanner_executable', return_value={'path': 'scanner'}), \
                 mock.patch.object(self.mod.subprocess, 'run', return_value=self.result(
                     {**self.report, 'analysis_completeness': complete})):
                result = self.mod.research_scan('https://github.com/example/project')
            self.assertEqual(result['status'], 'incomplete')
            self.assertFalse(result['install_eligible'])

    def test_execution_diagnostics_categorize_error_without_echoing_secret(self):
        bad = subprocess.CompletedProcess([], 2, '', 'Parser failed loading token=private-example')
        with mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner'}), mock.patch.object(self.mod.subprocess, 'run', return_value=bad):
            result = self.mod.research_scan('https://github.com/example/project')
        self.assertEqual(result['diagnostics']['error_category'], 'parser')
        self.assertNotIn('private-example', json.dumps(result))

    def test_private_diagnostics_preserve_bounded_parser_evidence_on_request(self):
        bad = subprocess.CompletedProcess([], 2, '', 'Parser failed: missing tree-sitter module ' + 'x' * 3000)
        with mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner'}), mock.patch.object(self.mod.subprocess, 'run', return_value=bad):
            result = self.mod.research_scan('https://github.com/example/project', private_diagnostics=True)
        detail = result['diagnostics']['private_stderr_excerpt']
        self.assertIn('missing tree-sitter module', detail)
        self.assertLessEqual(len(detail), 1000)
        self.assertIn('private', result['diagnostics']['handling'])

    def test_high_finding_after_many_low_findings_remains_visible(self):
        self.report['issues'] = [{'id': 'L1', 'severity': 'LOW'} for _ in range(25)] + [
            {'id': 'DANGER', 'severity': 'HIGH', 'location': {'file': 'script.py', 'start_line': 7}}]
        with mock.patch.object(self.mod.subprocess, 'run', return_value=self.result()):
            with self.assertRaisesRegex(ValueError, 'DANGER.*script.py:7.*6 finding'):
                self.mod.scan_skill(Path('sample'), {'path': 'scanner'}, {'SKILL.md': b'abc'})

    def test_preview_matrix_never_grants_installation(self):
        cases = [
            ({'risk_assessment': {'severity': 'MEDIUM', 'recommendation': 'CAUTION'}}, 'review-required'),
            ({'risk_assessment': {'severity': 'CRITICAL', 'recommendation': 'DO_NOT_INSTALL'}}, 'review-required'),
            ({'suppressed_count': 1}, 'incomplete'),
            ({'metadata': {'llm_requested': True}}, 'incomplete'),
            ({'execution_successful': False}, 'incomplete'),
            ({'issues': [{'id': 'bad', 'severity': 'UNKNOWN'}]}, 'malformed-report'),
        ]
        for changed, status in cases:
            with self.subTest(status=status), mock.patch.object(self.mod, 'scanner_executable', return_value={'path': 'scanner'}), mock.patch.object(self.mod.subprocess, 'run', return_value=self.result({**self.report, **changed})):
                result = self.mod.research_scan('https://github.com/example/project', retry=True)
            self.assertEqual(result['status'], status)
            self.assertFalse(result['install_eligible'])

    def test_inspection_rejects_oversized_payload_without_modifying_it(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'large.bin'
            with target.open('wb') as stream:
                stream.truncate(100 * 1024 * 1024 + 1)
            with self.assertRaisesRegex(ValueError, '100 MiB'):
                self.mod.inspect_source(Path(temp))
            self.assertEqual(target.stat().st_size, 100 * 1024 * 1024 + 1)


if __name__ == '__main__':
    unittest.main()
