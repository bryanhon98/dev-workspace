"""Regression tests for the version-based, no-checksum skill installer."""
import copy
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/install_advisor.py'
REVISION = 'cf5cac7ba5c756a6e0ebf52dc9763f49422f889f'


class AdvisorInstallTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('installer_under_test', SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        base = pathlib.Path(temp.name)
        self.repo, self.skills, self.home = base / 'repo', base / 'user/skills', base / 'user/codex'
        self.repo.mkdir()
        self.write('constraints.txt', 'example==1.0\n')
        self.write('audits/skillspector-cf5cac7-20261018/review.json',
                   (ROOT / 'audits/skillspector-cf5cac7-20261018/review.json').read_text())
        self.manifest = {
            'schema_version': 2, 'bundle_version': '2.0.0', 'approvals_ref': 'skill-approvals.json',
            'scanner': {'revision': REVISION, 'version': '2.12.0',
                        'source_url': 'https://github.com/NVIDIA/skillspector',
                        'constraints': 'constraints.txt'},
            'components': []}
        self.approvals = {'schema_version': 2, 'skills': []}
        self.add_component('tool-advisor')
        self.write('advisor-baseline.json',
                   {'schema_version': 1, 'required_skills': ['tool-advisor']})
        self.scanner = {'path': str(base / 'scanner'), 'version': '2.12.0',
                        'revision': REVISION, 'source_url': 'https://github.com/NVIDIA/skillspector'}
        self.report_mutation = None
        self.scan_count = 0
        for name, kwargs in [
            ('_prepare_scanner', {'return_value': self.scanner}),
            ('_verify_scanner', {'return_value': self.scanner}),
            ('_verify_upstream', {'return_value': []}),
            ('_run', {'side_effect': self.fake_scan})]:
            patch = mock.patch.object(self.mod, name, **kwargs)
            patch.start()
            self.addCleanup(patch.stop)

    def write(self, relative, value):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, (dict, list)):
            path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
        else:
            path.write_text(value, encoding='utf-8')
        return path

    def save(self):
        self.write('advisor-bundle.json', self.manifest)
        self.write('skill-approvals.json', self.approvals)

    def report(self, name, files, issues=None, complete=True):
        issues = list(issues or [])
        count = len(files)
        covered = count if complete else max(0, count - 1)
        return {
            'skill': {'name': name},
            'execution_successful': True,
            'metadata': {'llm_requested': False, 'skillspector_version': '2.12.0',
                         'meta_analysis_applied': False, 'inference_usage': []},
            'suppressed_count': 0, 'suppressed': [], 'issues': issues,
            'components': [{'path': p} for p in files],
            'analysis_completeness': {
                'execution_successful': True, 'is_complete': complete,
                'status': 'complete' if complete else 'partial',
                'total_components': count, 'scanned_components': covered,
                'fully_inspected_files': covered,
                'partially_inspected_files': count - covered,
                'entirely_uninspected_files': 0,
                'coverage_percent': round(100 * covered / count, 1),
                'ledger_exceptions': [], 'scope_exclusions': [],
                'limitations': [] if complete else ['A file was only partially inspected'],
            }}

    def add_component(self, name):
        self.write('skills/' + name + '/SKILL.md',
                   '---\nname: ' + name + '\n---\nUse the selected skill.\n')
        path = 'audits/' + name
        report = self.report(name, ['SKILL.md'])
        self.write(path + '/scan.json', report)
        self.write(path + '/audit.json', {
            'status': 'triaged-static', 'revision': '1.0.0',
            'scanner': self.manifest['scanner'],
            'report_ref': path + '/scan.json',
            'analysis_completeness': report['analysis_completeness'],
            'findings_decisions': [],
            'coverage_decision': {'disposition': 'complete', 'reason': 'All files inspected.'}})
        item = {'name': name, 'path': 'skills/' + name, 'version': '1.0.0',
                'source': 'https://github.com/example/dev-workspace/tree/main/skills/' + name,
                'extra_files': [], 'audit_ref': path + '/audit.json'}
        self.manifest['components'].append(item)
        self.approvals['skills'].append({
            'name': name, 'version': '1.0.0', 'source': item['source'],
            'approved_at': None, 'approval': 'historical-reviewed',
            'scan': 'historical-triaged', 'audit_ref': item['audit_ref'],
            'upstream_repository': None})
        self.save()
        return item

    def fake_scan(self, args, **kwargs):
        args = list(map(str, args))
        if 'scan' not in args:
            raise AssertionError('Unexpected external command: ' + repr(args))
        self.assertIn('--no-llm', args)
        self.assertIn('--fail-on-incomplete', args)
        self.assertIn('--fail-on-findings', args)
        self.assertEqual(args[args.index('--min-coverage') + 1], '100')
        self.assertEqual(self.mod._environment()['LANGSMITH_TRACING'], 'false')
        source = pathlib.Path(args[args.index('scan') + 1])
        self.assertNotEqual(source.parent, self.skills)
        files = sorted(p.relative_to(source).as_posix()
                       for p in source.rglob('*') if p.is_file())
        report = self.report(source.name, files)
        if self.report_mutation:
            self.report_mutation(report)
        output = pathlib.Path(args[args.index('--output') + 1])
        output.write_text(json.dumps(report), encoding='utf-8')
        self.scan_count += 1
        return subprocess.CompletedProcess(args, 1 if report['issues'] or
                            not report['analysis_completeness']['is_complete'] else 0, '', '')

    def install(self, selected=None):
        return self.mod.install_bundle(self.repo, self.skills, self.home,
                                       selected_names=selected)

    def check(self, selected_host='codex'):
        return self.mod.check_bundle(self.repo, self.skills, self.home, host=selected_host)

    def warning(self, name='tool-advisor'):
        issue = {'id': 'LP3', 'severity': 'MEDIUM', 'finding': 'Explicit tool scope missing',
                 'location': {'file': 'SKILL.md', 'start_line': 1,
                              'end_line': None, 'start_column': None},
                 'match_fingerprint': None}
        path = 'audits/' + name
        report = self.report(name, ['SKILL.md'], [issue])
        self.write(path + '/scan.json', report)
        audit = json.loads((self.repo / path / 'audit.json').read_text())
        audit['analysis_completeness'] = report['analysis_completeness']
        audit['findings_decisions'] = [{
            'signature': list(self.mod._signature(issue)),
            'disposition': 'warn', 'reason': 'Explicitly reviewed warning for exact revision.'}]
        self.write(path + '/audit.json', audit)
        self.report_mutation = lambda r: r.update(issues=[copy.deepcopy(issue)])
        return issue

    def test_real_17_skill_baseline_is_prepared(self):
        plan = self.mod.baseline_plan(ROOT)
        self.assertTrue(plan['payloads_prepared'], plan['audit_error'])
        self.assertEqual(len(plan['required_skills']), 17)
        self.assertEqual(plan['pending_clean_approval'], [])

    def test_plan_is_readonly_and_lists_selected_roles(self):
        plan = self.mod.baseline_plan(self.repo)
        self.assertTrue(plan['payloads_prepared'])
        self.assertEqual(plan['required_skills'], ['tool-advisor'])
        self.assertFalse(self.skills.exists())
        self.assertFalse(self.home.exists())

    def test_missing_required_skill_blocks_full_setup(self):
        self.write('advisor-baseline.json',
                   {'schema_version': 1, 'required_skills': ['tool-advisor', 'council']})
        with self.assertRaisesRegex(ValueError, 'council'):
            self.mod.require_baseline(self.repo)
        self.assertFalse(self.skills.exists())

    def test_missing_or_duplicate_approval_entry_blocks(self):
        for records in ([], self.approvals['skills'] * 2):
            self.write('skill-approvals.json', {'schema_version': 2, 'skills': records})
            with self.assertRaisesRegex(ValueError, 'approval'):
                self.mod._bundle(self.repo)

    def test_unexpected_schema_or_missing_ledger_blocks(self):
        self.approvals['schema_version'] = 99
        self.save()
        with self.assertRaisesRegex(ValueError, 'approval'):
            self.mod._bundle(self.repo)
        (self.repo / 'skill-approvals.json').unlink()
        with self.assertRaisesRegex(ValueError, 'read valid JSON|approval'):
            self.mod._bundle(self.repo)

    def test_install_and_check_with_direct_file_comparison(self):
        result = self.install()
        self.assertTrue(result['ready'])
        self.assertEqual(result['auto_approved_updates'], [])
        self.assertTrue(self.check()['ready'])
        self.assertEqual((self.skills / 'tool-advisor/SKILL.md').read_bytes(),
                         (self.repo / 'skills/tool-advisor/SKILL.md').read_bytes())
        self.assertEqual((self.home / 'dev-workspace-advisor/snapshots/tool-advisor/SKILL.md').read_bytes(),
                         (self.skills / 'tool-advisor/SKILL.md').read_bytes())

    def test_no_file_hashes_in_manifest_approvals_or_receipt(self):
        self.install()
        receipt = json.loads((self.home / 'dev-workspace-advisor/receipt.json').read_text())
        for entry in [self.manifest, self.approvals, receipt]:
            encoded = json.dumps(entry)
            self.assertNotIn('sha256', encoded)
            self.assertNotIn('payload_digest', encoded)
            self.assertNotIn('"hashes"', encoded)
        self.assertEqual(receipt['schema_version'], 2)

    def test_auto_approves_complete_clean_new_revision_and_updates_date(self):
        self.install()
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        source.write_text(source.read_text() + 'New reviewed revision.\n')
        self.manifest['components'][0]['version'] = '1.0.1'
        self.manifest['bundle_version'] = '2.0.1'
        self.save()
        plan = self.mod.baseline_plan(self.repo)
        self.assertEqual(plan['pending_clean_approval'], ['tool-advisor'])
        audit_before = (self.repo / 'audits/tool-advisor/audit.json').read_bytes()
        result = self.install()
        self.assertEqual(result['auto_approved_updates'], ['tool-advisor'])
        record = json.loads((self.repo / 'skill-approvals.json').read_text())['skills'][0]
        self.assertEqual(record['version'], '1.0.1')
        self.assertEqual(record['approval'], 'clean-auto')
        self.assertTrue(record['approved_at'])
        self.assertNotIn('payload_digest', record)
        self.assertEqual(audit_before, (self.repo / 'audits/tool-advisor/audit.json').read_bytes())
        self.assertTrue(self.check()['ready'])

    def test_new_finding_blocks_automatic_approval(self):
        self.manifest['components'][0]['version'] = '1.0.1'
        self.save()
        before = (self.repo / 'skill-approvals.json').read_bytes()
        issue = {'id': 'NEW', 'severity': 'HIGH', 'finding': 'Unsafe instruction',
                 'location': {'file': 'SKILL.md'}, 'match_fingerprint': None}
        self.report_mutation = lambda r: r.update(issues=[issue])
        with self.assertRaisesRegex(ValueError, 'finding'):
            self.install()
        self.assertEqual(before, (self.repo / 'skill-approvals.json').read_bytes())
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_incomplete_new_scan_blocks_automatic_approval(self):
        self.manifest['components'][0]['version'] = '1.0.1'
        self.save()
        def partial(report):
            profile = report['analysis_completeness']
            profile.update(is_complete=False, status='partial', coverage_percent=0,
                           scanned_components=0, fully_inspected_files=0,
                           partially_inspected_files=1,
                           limitations=['SKILL.md only partly read'])
        self.report_mutation = partial
        with self.assertRaisesRegex(ValueError, 'coverage|omissions|scan'):
            self.install()
        self.assertFalse(self.skills.exists() and (self.skills / 'tool-advisor').exists())

    def test_existing_historical_warning_preserved(self):
        self.warning()
        result = self.install()
        self.assertEqual(result['warnings'][0]['kind'], 'finding')
        self.assertTrue(self.check()['ready'])

    def test_new_finding_on_old_approval_blocks(self):
        self.warning()
        self.report_mutation = lambda r: r.update(issues=[{'id': 'DIFFERENT',
            'severity': 'HIGH', 'finding': 'Different risk',
            'location': {'file': 'SKILL.md'}, 'match_fingerprint': None}])
        with self.assertRaisesRegex(ValueError, 'finding'):
            self.install()

    def test_manual_warning_review_matches_exact_revision(self):
        self.warning()
        self.manifest['components'][0]['version'] = '1.0.1'
        audit = json.loads((self.repo / 'audits/tool-advisor/audit.json').read_text())
        audit['revision'] = '1.0.1'
        self.write('audits/tool-advisor/audit.json', audit)
        self.approvals['skills'][0].update(version='1.0.1', approval='manual-reviewed',
                                           scan='triaged', approved_at='2026-11-08T00:00:00+00:00')
        self.save()
        result = self.install()
        self.assertTrue(result['ready'])
        self.assertTrue(result['warnings'])
        self.assertEqual(result['auto_approved_updates'], [])
        self.assertTrue(self.check()['ready'])

    def test_manual_warning_review_wrong_version_blocked(self):
        self.warning()
        self.manifest['components'][0]['version'] = '1.0.1'
        self.approvals['skills'][0].update(version='1.0.1', approval='manual-reviewed', scan='triaged')
        self.save()
        with self.assertRaisesRegex(ValueError, 'revision'):
            self.install()

    def test_reinstall_preserves_unmodified_skill_files(self):
        self.install()
        target = self.skills / 'tool-advisor/SKILL.md'
        before = target.stat().st_mtime_ns
        self.install()
        self.assertEqual(target.stat().st_mtime_ns, before)
        self.assertEqual(self.scan_count, 2)

    def test_changed_installed_skill_never_overwritten(self):
        self.install()
        target = self.skills / 'tool-advisor/SKILL.md'
        target.write_text('Local custom content!')
        self.assertFalse(self.check()['ready'])
        with self.assertRaisesRegex(ValueError, 'modified locally'):
            self.install()
        self.assertEqual(target.read_text(), 'Local custom content!')

    def test_unmanaged_conflict_blocks_install(self):
        target = self.skills / 'tool-advisor/SKILL.md'
        target.parent.mkdir(parents=True)
        target.write_text('Other user-owned skill!')
        with self.assertRaisesRegex(ValueError, 'Unmanaged'):
            self.install()
        self.assertEqual(target.read_text(), 'Other user-owned skill!')

    def test_identical_unmanaged_skill_can_be_adopted(self):
        shutil.copytree(self.repo / 'skills/tool-advisor', self.skills / 'tool-advisor')
        self.assertTrue(self.install()['ready'])
        self.assertTrue(self.check()['ready'])

    def test_legacy_receipt_migrates_when_source_is_unchanged(self):
        self.install()
        receipt = self.home / 'dev-workspace-advisor/receipt.json'
        data = json.loads(receipt.read_text())
        data['schema_version'] = 1
        receipt.write_text(json.dumps(data))
        shutil.rmtree(self.home / 'dev-workspace-advisor/snapshots')
        self.assertTrue(self.install()['ready'])
        self.assertEqual(json.loads(receipt.read_text())['schema_version'], 2)
        self.assertTrue(self.check()['ready'])

    def test_legacy_receipt_changed_version_cannot_overwrite_unknown_files(self):
        self.install()
        receipt = self.home / 'dev-workspace-advisor/receipt.json'
        data = json.loads(receipt.read_text())
        data['schema_version'] = 1
        receipt.write_text(json.dumps(data))
        shutil.rmtree(self.home / 'dev-workspace-advisor/snapshots')
        self.manifest['components'][0]['version'] = '1.0.1'
        self.save()
        with self.assertRaisesRegex(ValueError, 'Legacy installation'):
            self.install()

    def test_receipt_device_name_is_local_only(self):
        with mock.patch.dict(self.mod.os.environ, {'ADVISOR_DEVICE_ALIAS': 'Workstation'}):
            self.install()
        receipt = json.loads((self.home / 'dev-workspace-advisor/receipt.json').read_text())
        self.assertEqual(receipt['device'], 'Workstation')
        self.assertTrue(receipt['installed_at'])
        self.assertNotIn('Workstation', (self.repo / 'skill-approvals.json').read_text())

    def test_fresh_scan_rejects_suppression_or_wrong_coverage(self):
        for field in ('suppressed', 'missing_components'):
            def bad(report):
                if field == 'suppressed':
                    report.update(suppressed_count=1, suppressed=[{'reason': 'hidden'}])
                else:
                    report['components'] = []
            self.report_mutation = bad
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Scan|coverage'):
                self.install()

    def test_missing_receipt_check_does_not_write(self):
        result = self.check()
        self.assertFalse(result['ready'])
        self.assertFalse(self.home.exists())

    def test_changed_scan_report_fails_readonly_check(self):
        self.install()
        receipt = json.loads((self.home / 'dev-workspace-advisor/receipt.json').read_text())
        path = self.home / 'dev-workspace-advisor' / receipt['components'][0]['report']
        report = json.loads(path.read_text())
        report['issues'] = [{'id': 'UNREVIEWED', 'severity': 'HIGH', 'finding': 'Changed',
                             'location': {'file': 'SKILL.md'}, 'match_fingerprint': None}]
        path.write_text(json.dumps(report))
        self.assertFalse(self.check()['ready'])

    def test_selected_partial_core_cannot_claim_full_setup(self):
        self.add_component('grilling')
        self.add_component('find-skills')
        self.add_component('council')
        names = self.mod.require_core_only(self.repo)
        self.assertEqual(set(names), {'tool-advisor', 'grilling', 'find-skills'})
        out = self.install(selected=names)
        self.assertFalse(out['full_bundle_ready'])
        self.assertFalse((self.skills / 'council').exists())

    def test_no_candidate_executes_or_runs_its_script_during_scan(self):
        marker = self.repo / 'executed.flag'
        self.write('skills/tool-advisor/evil.py',
                   'from pathlib import Path\nPath(' + repr(str(marker)) + ').write_text("executed")\n')
        self.manifest['components'][0]['version'] = '1.0.1'
        self.save()
        self.install()
        self.assertFalse(marker.exists())
        self.assertEqual(self.scan_count, 1)

    def test_symlink_source_is_rejected(self):
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        other = self.repo / 'original.md'
        source.replace(other)
        try:
            source.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest('OS does not permit symlink creation')
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.install()

    def test_committed_git_source_required_when_repository_is_git(self):
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'add', 'skills/tool-advisor/SKILL.md'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Unit Test',
                        '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Initial source'],
                       check=True)
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        source.write_text(source.read_text() + 'Uncommitted modification\n')
        with self.assertRaisesRegex(ValueError, 'local edits'):
            self.mod._bundle(self.repo)

    def test_approval_revision_in_source_url_must_match(self):
        item = self.manifest['components'][0]
        item.update(version='a' * 40, upstream_repository='https://github.com/example/project',
                    upstream_ref='HEAD', source='https://github.com/example/project/tree/' + 'b' * 40)
        self.approvals['skills'][0]['upstream_repository'] = item['upstream_repository']
        self.save()
        with self.assertRaisesRegex(ValueError, 'exact upstream revision'):
            self.mod._bundle(self.repo)

    def test_report_warning_batch_scans_all_before_block(self):
        self.add_component('council')
        self.report_mutation = lambda r: r.update(issues=[{
            'id': 'NEW', 'severity': 'HIGH', 'finding': 'New',
            'location': {'file': 'SKILL.md'}, 'match_fingerprint': None}])
        with self.assertRaisesRegex(ValueError, 'scans blocked'):
            self.install()
        self.assertEqual(self.scan_count, 2)
        self.assertFalse(self.skills.exists() and any(self.skills.iterdir()))


if __name__ == '__main__':
    unittest.main()
