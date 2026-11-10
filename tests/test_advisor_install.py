"""Tests for the current scan-before-activation installer without audit ledgers."""
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[1]


class AdvisorInstallTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('install_advisor', ROOT / 'scripts/install_advisor.py')
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = pathlib.Path(temp.name)
        self.repo, self.skills, self.home = base / 'repo', base / 'user/skills', base / 'user/codex'
        self.repo.mkdir()
        self.manifest = {'schema_version': 3, 'bundle_version': '3.0.0',
                         'scanner': {'source_url': 'https://github.com/NVIDIA/SkillSpector'},
                         'components': []}
        self.add_component('tool-advisor')
        self.write('advisor-baseline.json', {'schema_version': 1, 'required_skills': ['tool-advisor']})
        self.calls = 0
        for method, return_value in [
            ('_scanner_executable', {'path': '/trusted/skillspector', 'version': 'SkillSpector v2.12.0'}),
            ('_verify_upstream', []),
        ]:
            patch = mock.patch.object(self.mod, method, return_value=return_value)
            patch.start()
            self.addCleanup(patch.stop)
        self.real_scan = self.mod._scan
        patch = mock.patch.object(self.mod, '_scan', side_effect=self.fake_scan)
        patch.start()
        self.addCleanup(patch.stop)

    def write(self, path, value):
        dest = self.repo / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(json.dumps(value, indent=2) if isinstance(value, dict) else value, encoding='utf-8')
        return dest

    def add_component(self, name):
        self.write('skills/' + name + '/SKILL.md', '---\nname: ' + name + '\n---\nSafe example\n')
        self.manifest['components'].append({
            'name': name, 'path': 'skills/' + name, 'version': '1.0.0',
            'source': 'https://github.com/example/dev-workspace/tree/main/skills/' + name,
            'extra_files': []
        })
        self.write('advisor-bundle.json', self.manifest)

    def fake_scan(self, stage, scanner, files):
        self.assertFalse(str(stage).startswith(str(self.skills)))
        self.assertIn('SKILL.md', files)
        self.calls += 1
        return []

    def install(self, selected=None):
        return self.mod.install_bundle(self.repo, self.skills, self.home, selected_names=selected)

    def check(self):
        return self.mod.check_bundle(self.repo, self.skills, self.home)

    def test_real_baseline_has_three_core_and_fourteen_optional_sources(self):
        result = self.mod.baseline_plan(ROOT)
        self.assertTrue(result['payloads_prepared'], result['audit_error'])
        self.assertEqual(result['required_skills'], list(self.mod.CORE_NAMES))
        self.assertEqual(len(result['optional_skills']), 14)
        self.assertFalse(set(result['required_skills']) & set(result['optional_skills']))

    def test_clean_install_check_and_no_scan_history(self):
        result = self.install()
        self.assertTrue(result['ready'])
        self.assertTrue(self.check()['ready'])
        self.assertEqual(result['warnings'], [])
        state = self.home / 'dev-workspace-advisor'
        self.assertFalse((state / 'reports').exists())
        self.assertFalse((self.repo / 'skill-approvals.json').exists())
        receipt = json.loads((state / 'receipt.json').read_text())
        self.assertEqual(receipt['schema_version'], 3)
        self.assertNotIn('report', receipt['components'][0])
        self.assertNotIn('audit_ref', receipt['components'][0])
        self.assertNotIn('scan_records', result)

    def test_reinstall_rescans_but_preserves_unchanged_files(self):
        self.install()
        path = self.skills / 'tool-advisor/SKILL.md'
        before = path.stat().st_mtime_ns
        self.install()
        self.assertEqual(before, path.stat().st_mtime_ns)
        self.assertEqual(self.calls, 2)

    def test_partial_selection_not_full(self):
        self.add_component('grilling')
        self.add_component('find-skills')
        self.add_component('council')
        self.assertEqual(self.mod.require_core_only(self.repo),
                         ['tool-advisor', 'grilling', 'find-skills'])
        out = self.install(selected=list(self.mod.CORE_NAMES))
        self.assertFalse(out['full_bundle_ready'])
        self.assertFalse((self.skills / 'council').exists())

    def test_retire_optional_skills_archives_only_managed_unmodified_entries(self):
        for name in ('grilling', 'find-skills', 'council'):
            self.add_component(name)
        self.write('advisor-baseline.json', {
            'schema_version': 1, 'required_skills': list(self.mod.CORE_NAMES),
            'optional_skills': ['council']})
        self.install()
        result = self.mod.retire_optional_skills(self.repo, self.skills, self.home)
        self.assertEqual(result['archived_skills'], ['council'])
        self.assertFalse((self.skills / 'council').exists())
        self.assertTrue((pathlib.Path(result['archive']) / 'skills/council/SKILL.md').is_file())
        self.assertTrue((pathlib.Path(result['archive']) / 'snapshots/council/SKILL.md').is_file())
        self.assertTrue(self.check()['ready'])
        self.assertTrue(self.check()['baseline_ready'])
        self.assertEqual(set(self.check()['components']), set(self.mod.CORE_NAMES))
        self.assertEqual(self.mod.retire_optional_skills(self.repo, self.skills, self.home)['archived_skills'], [])
        self.assertTrue(self.install(selected=list(self.mod.CORE_NAMES))['baseline_ready'])

    def test_retire_optional_refuses_modified_files_and_preserves_receipt(self):
        for name in ('grilling', 'find-skills', 'council'):
            self.add_component(name)
        self.write('advisor-baseline.json', {
            'schema_version': 1, 'required_skills': list(self.mod.CORE_NAMES),
            'optional_skills': ['council']})
        self.install()
        receipt = self.home / 'dev-workspace-advisor/receipt.json'
        before = receipt.read_bytes()
        (self.skills / 'council/SKILL.md').write_text('My modified instructions')
        with self.assertRaisesRegex(ValueError, 'modified'):
            self.mod.retire_optional_skills(self.repo, self.skills, self.home)
        self.assertEqual(receipt.read_bytes(), before)
        self.assertEqual((self.skills / 'council/SKILL.md').read_text(), 'My modified instructions')

    def test_managed_file_edit_is_protected(self):
        self.install()
        target = self.skills / 'tool-advisor/SKILL.md'
        target.write_text('Changed on this PC!')
        self.assertFalse(self.check()['ready'])
        with self.assertRaisesRegex(ValueError, 'modified locally'):
            self.install()
        self.assertEqual(target.read_text(), 'Changed on this PC!')

    def test_unmanaged_conflict_is_protected(self):
        dest = self.skills / 'tool-advisor/SKILL.md'
        dest.parent.mkdir(parents=True)
        dest.write_text('Different')
        with self.assertRaisesRegex(ValueError, 'Unmanaged'):
            self.install()

    def test_existing_identical_skill_can_be_adopted(self):
        shutil.copytree(self.repo / 'skills/tool-advisor', self.skills / 'tool-advisor')
        self.assertTrue(self.install()['ready'])

    def test_legacy_receipt_is_migrated_without_scanner_history(self):
        self.install()
        receipt = self.home / 'dev-workspace-advisor/receipt.json'
        obj = json.loads(receipt.read_text())
        obj['schema_version'] = 2
        obj['components'][0]['report'] = 'reports/old.json'
        obj['components'][0]['audit_ref'] = 'audits/old/audit.json'
        receipt.write_text(json.dumps(obj))
        self.assertFalse(self.check()['ready'])
        result = self.install()
        self.assertTrue(result['legacy_receipt_migrated'])
        self.assertTrue(self.check()['ready'])

    def test_scan_failure_blocks_all_changes(self):
        self.add_component('council')
        def fail(stage, scanner, files):
            self.calls += 1
            if stage.name == 'council':
                raise ValueError('SkillSpector blocked risky skill')
            return []
        self.mod._scan.side_effect = fail
        with self.assertRaisesRegex(ValueError, 'blocked risky skill'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_scanner_missing_blocks_activation(self):
        self.mod._scanner_executable.side_effect = ValueError('SkillSpector is required')
        with self.assertRaisesRegex(ValueError, 'required'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_locked_install_blocks(self):
        lock = self.home / 'dev-workspace-advisor/install.lock'
        lock.parent.mkdir(parents=True)
        lock.write_text('busy')
        with self.assertRaisesRegex(ValueError, 'already in progress'):
            self.install()

    def test_missing_receipt_check_is_read_only(self):
        self.assertFalse(self.check()['ready'])
        self.assertFalse(self.home.exists())

    def test_source_symlink_is_rejected(self):
        original = self.repo / 'skills/tool-advisor/SKILL.md'
        replacement = self.repo / 'original.md'
        original.replace(replacement)
        try:
            original.symlink_to(replacement)
        except (OSError, NotImplementedError):
            self.skipTest('Symlink creation unavailable')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.install()

    def test_git_source_changes_are_detected(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'add', 'skills'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Test',
                        '-c', 'user.email=test@example.invalid',
                        'commit', '-qm', 'Initial'], check=True)
        item = self.repo / 'skills/tool-advisor/SKILL.md'
        item.write_text(item.read_text() + 'uncommitted')
        with self.assertRaisesRegex(ValueError, 'local edits'):
            self.mod._bundle(self.repo)

    def test_scanner_json_high_medium_and_incomplete(self):
        directory = self.repo / 'skills/tool-advisor'
        base = {'skill': {'name': 'tool-advisor'}, 'execution_successful': True,
                'components': [{'path': 'SKILL.md'}], 'issues': [],
                'metadata': {'llm_requested': False}, 'suppressed_count': 0, 'suppressed': [],
                'analysis_completeness': {'is_complete': True, 'coverage_percent': 100},
                'risk_assessment': {'severity': 'LOW', 'recommendation': 'SAFE'}}
        issue = {'id': 'LP3', 'severity': 'MEDIUM'}
        for report, code, should_block in [
            (base, 0, False),
            ({**base, 'issues': [issue],
              'risk_assessment': {'severity': 'MEDIUM', 'recommendation': 'CAUTION'}}, 0, True),
            ({**base, 'issues': [{'id': 'E2', 'severity': 'HIGH'}],
              'risk_assessment': {'severity': 'HIGH', 'recommendation': 'DO_NOT_INSTALL'}}, 1, True),
            ({**base, 'analysis_completeness': {'is_complete': False, 'coverage_percent': 80}}, 1, True),
            ({**base, 'suppressed_count': 1}, 0, True),
        ]:
            with self.subTest(code=code, blocked=should_block, risk=report['risk_assessment']):
                completed = subprocess.CompletedProcess([], code, json.dumps(report), '')
                with mock.patch.object(self.mod.subprocess, 'run', return_value=completed):
                    if should_block:
                        with self.assertRaises(ValueError):
                            self.real_scan(directory, {'path': '/trusted/scanner'}, ['SKILL.md'])
                    else:
                        warnings = self.real_scan(directory, {'path': '/trusted/scanner'}, ['SKILL.md'])
                        self.assertEqual(len(warnings), len(report['issues']))

    def test_new_revision_requires_fresh_scan(self):
        self.install()
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        source.write_text(source.read_text() + 'New revision\n')
        self.manifest['bundle_version'] = '3.0.1'
        self.manifest['components'][0]['version'] = '1.0.1'
        self.write('advisor-bundle.json', self.manifest)
        self.install()
        self.assertEqual(self.calls, 2)
        self.assertTrue(self.check()['ready'])


if __name__ == '__main__':
    unittest.main()
