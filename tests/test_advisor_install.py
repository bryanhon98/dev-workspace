import copy
import hashlib
import importlib.util
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'install_advisor.py'
REVISION = 'cf5cac7ba5c756a6e0ebf52dc9763f49422f889f'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AdvisorInstallTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'The advisor bundle installer is not implemented')
        spec = importlib.util.spec_from_file_location('advisor_install', SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = pathlib.Path(self.tmp.name)
        self.repo = self.base / 'repo'
        self.repo.mkdir()
        self.skills = self.base / 'user' / 'skills'
        self.codex = self.base / 'user' / 'codex'
        self.scanner = self.base / 'venv' / 'bin' / 'skillspector'
        self.scanner.parent.mkdir(parents=True)
        self.scanner.write_text('scanner fixture')
        (self.scanner.parent / 'python').write_text('python fixture')
        self.review = json.loads((ROOT / 'audits/skillspector-cf5cac7-20261018/review.json').read_text())
        self.write('audits/skillspector-cf5cac7-20261018/review.json', self.review)
        self.write('constraints.txt', 'example==1.0\n')
        self.manifest = {
            'schema_version': 1, 'bundle_version': '1.0.0',
            'scanner': {'revision': REVISION, 'version': '2.12.0',
                        'source_url': 'https://github.com/NVIDIA/skillspector',
                        'constraints': 'constraints.txt'},
            'components': [],
        }
        self.add_component('tool-advisor')
        self.report_mutation = None
        self.scan_exit = None
        self.metadata_mutation = None
        self.scan_count = 0
        self.external = mock.patch.object(self.mod.subprocess, 'run', side_effect=self.fake_run)
        self.external.start()
        self.addCleanup(self.external.stop)

    def write(self, relative, value):
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value) if isinstance(value, (dict, list)) else value)
        return path

    def save_manifest(self):
        self.write('advisor-bundle.json', self.manifest)

    def add_component(self, name):
        path = self.write(f'skills/{name}/SKILL.md', f'---\nname: {name}\n---\nRead the project brief.\n')
        hashes = {'SKILL.md': digest(path)}
        audit = f'audits/{name}.json'
        self.write(audit, {'status': 'reviewed-static', 'sha256': hashes,
                           'scanner': {'revision': REVISION, 'version': '2.12.0'}})
        component = {'name': name, 'path': f'skills/{name}', 'version': '1.0.0',
                     'source': 'https://github.com/example/skills', 'hashes': hashes,
                     'extra_files': [], 'audit_ref': audit, 'exception': None}
        self.manifest['components'].append(component)
        self.save_manifest()
        return component

    def fake_run(self, args, **kwargs):
        args = [str(a) for a in args]
        if '-c' in args and 'distribution(' in args[args.index('-c') + 1]:
            result = {
                'version': '2.12.0',
                'direct_url': {'url': 'https://github.com/NVIDIA/skillspector.git',
                               'vcs_info': {'vcs': 'git', 'commit_id': REVISION}},
                'hashes': {'src/skillspector/__init__.py': self.review['source_hashes']['src/skillspector/__init__.py'],
                           'src/skillspector/cli.py': self.review['source_hashes']['src/skillspector/cli.py']},
            }
            if self.metadata_mutation:
                self.metadata_mutation(result)
            return subprocess.CompletedProcess(args, 0, json.dumps(result), '')
        if '--version' in args:
            return subprocess.CompletedProcess(args, 0, 'SkillSpector v2.12.0\n', '')
        if 'scan' in args:
            self.scan_count += 1
            source = pathlib.Path(args[args.index('scan') + 1])
            self.assertNotEqual(source.parent, self.skills)
            self.assertIn('--no-llm', args)
            self.assertIn('--fail-on-incomplete', args)
            self.assertIn('--fail-on-findings', args)
            self.assertEqual(args[args.index('--min-coverage') + 1], '100')
            self.assertEqual(kwargs['env']['LANGSMITH_TRACING'], 'false')
            self.assertEqual(kwargs['env']['LANGCHAIN_TRACING_V2'], 'false')
            files = [p.relative_to(source).as_posix() for p in source.rglob('*') if p.is_file()]
            report = {
                'skill': {'name': source.name, 'source': str(source)},
                'execution_successful': True,
                'risk_assessment': {'recommendation': 'SAFE'},
                'metadata': {'llm_requested': False, 'skillspector_version': '2.12.0'},
                'issues': [], 'suppressed_count': 0, 'suppressed': [],
                'components': [{'path': p} for p in files],
                'analysis_completeness': {'execution_successful': True, 'is_complete': True,
                    'coverage_percent': 100, 'status': 'complete', 'total_components': len(files),
                    'scanned_components': len(files), 'fully_inspected_files': len(files),
                    'partially_inspected_files': 0, 'entirely_uninspected_files': 0,
                    'ledger_exceptions': [], 'scope_exclusions': [], 'limitations': []},
            }
            if self.report_mutation:
                self.report_mutation(report)
            output = pathlib.Path(args[args.index('--output') + 1])
            output.write_text(json.dumps(report))
            code = self.scan_exit if self.scan_exit is not None else (1 if report['issues'] else 0)
            return subprocess.CompletedProcess(args, code, '', '')
        raise AssertionError('Unexpected external operation: ' + repr(args))

    def install(self):
        return self.mod.install_bundle(self.repo, self.skills, self.codex, scanner=self.scanner)

    def check(self):
        return self.mod.check_bundle(self.repo, self.skills, self.codex)

    def test_stages_all_components_before_install_and_check_is_ready(self):
        self.add_component('task-helper')
        def assert_uninstalled(report):
            self.assertFalse((self.skills / 'tool-advisor').exists())
            self.assertFalse((self.skills / 'task-helper').exists())
        self.report_mutation = assert_uninstalled
        result = self.install()
        self.assertTrue(result['ready'])
        self.assertEqual(self.scan_count, 2)
        self.assertTrue(self.check()['ready'])
        self.assertEqual((self.skills / 'tool-advisor/SKILL.md').read_bytes(),
                         (self.repo / 'skills/tool-advisor/SKILL.md').read_bytes())

    def test_check_missing_install_is_readonly(self):
        self.assertFalse(self.check()['ready'])
        self.assertFalse(self.codex.exists())
        self.assertFalse(self.skills.exists())

    def test_source_hash_mismatch_blocks_before_scanner(self):
        (self.repo / 'skills/tool-advisor/SKILL.md').write_text('Changed')
        with self.assertRaisesRegex(ValueError, 'hash|payload'):
            self.install()
        self.assertEqual(self.scan_count, 0)
        self.assertFalse(self.skills.exists())

    def test_extra_unmanifested_source_file_blocks(self):
        self.write('skills/tool-advisor/hidden.py', 'print("hidden")')
        with self.assertRaisesRegex(ValueError, 'hash|payload'):
            self.install()

    def test_missing_draft_and_mismatched_audits_block(self):
        for value in [None, {'status': 'draft'}, {'status': 'reviewed-static', 'sha256': {}}]:
            with self.subTest(audit=value):
                audit = self.repo / 'audits/tool-advisor.json'
                if value is None:
                    audit.unlink(missing_ok=True)
                else:
                    self.write('audits/tool-advisor.json', value)
                with self.assertRaises((ValueError, OSError)):
                    self.install()
                self.assertFalse(self.skills.exists())

    def test_partial_or_incomplete_scans_block(self):
        for field, value in [('is_complete', False), ('coverage_percent', 99),
                             ('execution_successful', False), ('partially_inspected_files', 1),
                             ('ledger_exceptions', [{'reason': 'skipped'}])]:
            with self.subTest(field=field):
                self.report_mutation = lambda r: r['analysis_completeness'].update({field: value})
                with self.assertRaisesRegex(ValueError, 'scan|coverage|complete'):
                    self.install()
                self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_missing_components_and_llm_or_suppressed_reports_block(self):
        mutations = [lambda r: r.update(components=[]),
                     lambda r: r['metadata'].update(llm_requested=True),
                     lambda r: r.update(suppressed_count=1),
                     lambda r: r.pop('execution_successful')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                self.report_mutation = mutation
                with self.assertRaises(ValueError):
                    self.install()

    def test_safe_recommendation_does_not_hide_new_findings(self):
        self.report_mutation = lambda r: r.update(issues=[{'id': 'NEW', 'severity': 'LOW'}])
        with self.assertRaisesRegex(ValueError, 'finding'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_scanner_failure_blocks_even_with_complete_report(self):
        self.scan_exit = 2
        with self.assertRaisesRegex(ValueError, '(?i)scanner|scan'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_malformed_or_missing_report_blocks(self):
        original = self.mod.subprocess.run
        for text in [None, '{bad json']:
            def bad_run(args, **kwargs):
                result = original(args, **kwargs)
                if 'scan' in args:
                    output = pathlib.Path(args[args.index('--output') + 1])
                    if text is None:
                        output.unlink()
                    else:
                        output.write_text(text)
                return result
            with self.subTest(text=text), mock.patch.object(self.mod.subprocess, 'run', side_effect=bad_run):
                with self.assertRaises((ValueError, OSError)):
                    self.install()

    def test_wrong_scanner_source_commit_blocks(self):
        self.metadata_mutation = lambda r: r['direct_url']['vcs_info'].update(commit_id='0' * 40)
        with self.assertRaisesRegex(ValueError, 'provenance|revision|source'):
            self.install()
        self.assertEqual(self.scan_count, 0)

    def test_wrong_scanner_code_hash_blocks(self):
        self.metadata_mutation = lambda r: r['hashes'].update({'src/skillspector/cli.py': '0' * 64})
        with self.assertRaisesRegex(ValueError, 'hash|source|provenance'):
            self.install()

    def test_preserves_unmanaged_conflicts(self):
        target = self.skills / 'tool-advisor'
        target.mkdir(parents=True)
        (target / 'SKILL.md').write_text('User custom skill')
        with self.assertRaisesRegex(ValueError, 'unmanaged|conflict'):
            self.install()
        self.assertEqual((target / 'SKILL.md').read_text(), 'User custom skill')

    def test_identical_unmanaged_copy_can_be_adopted_without_rewriting(self):
        target = self.skills / 'tool-advisor'
        shutil.copytree(self.repo / 'skills/tool-advisor', target)
        before = (target / 'SKILL.md').stat().st_mtime_ns
        self.install()
        self.assertEqual((target / 'SKILL.md').stat().st_mtime_ns, before)
        self.assertTrue(self.check()['ready'])

    def test_repeated_install_rescans_and_preserves_unchanged_files(self):
        self.install()
        target = self.skills / 'tool-advisor/SKILL.md'
        before = target.stat().st_mtime_ns
        self.install()
        self.assertEqual(self.scan_count, 2)
        self.assertEqual(target.stat().st_mtime_ns, before)

    def test_local_edits_are_never_overwritten(self):
        self.install()
        target = self.skills / 'tool-advisor/SKILL.md'
        target.write_text('My local improvement')
        self.assertFalse(self.check()['ready'])
        with self.assertRaisesRegex(ValueError, 'locally|modified|changed'):
            self.install()
        self.assertEqual(target.read_text(), 'My local improvement')

    def test_receipt_backed_update_is_supported(self):
        self.install()
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        source.write_text(source.read_text() + 'Updated reviewed instructions.\n')
        c = self.manifest['components'][0]
        c['version'] = '1.0.1'
        c['hashes']['SKILL.md'] = digest(source)
        self.manifest['bundle_version'] = '1.0.1'
        self.write(c['audit_ref'], {'status': 'reviewed-static', 'sha256': c['hashes'],
                                   'scanner': {'revision': REVISION, 'version': '2.12.0'}})
        self.save_manifest()
        self.assertFalse(self.check()['ready'])
        self.install()
        self.assertEqual((self.skills / 'tool-advisor/SKILL.md').read_bytes(), source.read_bytes())
        self.assertTrue(self.check()['ready'])

    def test_rollback_restores_previous_bundle_if_activation_fails(self):
        self.install()
        old = (self.skills / 'tool-advisor/SKILL.md').read_bytes()
        receipt = self.codex / 'dev-workspace-advisor/receipt.json'
        previous_receipt = receipt.read_bytes()
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        source.write_text('New reviewed skill')
        c = self.manifest['components'][0]
        c['hashes']['SKILL.md'] = digest(source)
        self.write(c['audit_ref'], {'status': 'reviewed-static', 'sha256': c['hashes'],
                                   'scanner': {'revision': REVISION, 'version': '2.12.0'}})
        self.add_component('task-helper')
        replace = self.mod.os.replace
        def fail_second(src, dst):
            if pathlib.Path(dst) == self.skills / 'task-helper':
                raise OSError('simulated disk error')
            return replace(src, dst)
        with mock.patch.object(self.mod.os, 'replace', side_effect=fail_second):
            with self.assertRaisesRegex((ValueError, OSError), 'simulated disk error'):
                self.install()
        self.assertEqual((self.skills / 'tool-advisor/SKILL.md').read_bytes(), old)
        self.assertEqual(receipt.read_bytes(), previous_receipt)
        self.assertFalse((self.skills / 'task-helper').exists())

    def test_check_detects_moved_checkout_missing_source_and_unknown_receipt(self):
        self.install()
        moved = self.base / 'moved'
        shutil.copytree(self.repo, moved)
        self.assertFalse(self.mod.check_bundle(moved, self.skills, self.codex)['ready'])
        (self.repo / 'skills/tool-advisor/SKILL.md').unlink()
        self.assertFalse(self.check()['ready'])
        receipt = self.codex / 'dev-workspace-advisor/receipt.json'
        receipt.write_text('{"schema_version": 999}')
        self.assertFalse(self.check()['ready'])

    def test_symlink_source_and_target_ancestor_are_refused(self):
        source = self.repo / 'skills/tool-advisor/SKILL.md'
        original = self.base / 'original.md'
        source.replace(original)
        source.symlink_to(original)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.install()
        source.unlink()
        original.replace(source)
        outside = self.base / 'outside'
        outside.mkdir()
        self.skills.parent.mkdir()
        self.skills.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlink'):
            self.install()
        self.assertEqual(list(outside.iterdir()), [])

    def test_parent_traversal_extra_file_destination_is_refused(self):
        license_file = self.write('LICENSE', 'License')
        self.manifest['components'][0]['extra_files'] = [
            {'source': 'LICENSE', 'destination': '../escape', 'sha256': digest(license_file)}]
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'path|destination'):
            self.install()

    def add_grilling(self):
        destination = self.repo / 'skills/grilling'
        shutil.copytree(ROOT / 'skills/external/matt-pocock/grilling', destination)
        review_path = 'audits/matt-pocock-49dd158-20261018/review.json'
        report_path = 'audits/matt-pocock-49dd158-20261018/grilling-scan.json'
        for p in [review_path, report_path]:
            self.write(p, (ROOT / p).read_text())
        hashes = {p.relative_to(destination).as_posix(): digest(p) for p in destination.rglob('*') if p.is_file()}
        self.manifest['components'].append({
            'name': 'grilling', 'path': 'skills/grilling',
            'version': '49dd158d1076134a641b33efb035946536778336',
            'source': 'https://github.com/mattpocock/skills', 'hashes': hashes,
            'extra_files': [], 'audit_ref': review_path,
            'exception': {'ref': 'matt-pocock-49dd158-20261018-user-approved',
                          'review': review_path, 'report': report_path}})
        self.save_manifest()
        issue = json.loads((ROOT / report_path).read_text())['issues'][0]
        self.report_mutation = lambda r: r.update(issues=[copy.deepcopy(issue)]) if r['skill']['name'] == 'grilling' else None
        return issue

    def test_exact_historical_exception_is_retained(self):
        self.add_grilling()
        self.install()
        self.assertTrue(self.check()['ready'])

    def test_new_or_changed_finding_is_not_covered_by_exception(self):
        issue = self.add_grilling()
        issue['severity'] = 'HIGH'
        with self.assertRaisesRegex(ValueError, 'finding|exception'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_unknown_exception_is_rejected(self):
        self.add_grilling()
        self.manifest['components'][-1]['exception']['ref'] = 'arbitrary-approval'
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'exception|approval'):
            self.install()

    def approve_advisor_fixture(self):
        component = self.manifest['components'][0]
        issue = json.loads((ROOT / 'audits/tool-advisor-1.0.0-20261102/scan.json').read_text())['issues'][0]
        exception_ref = 'tool-advisor-1.0.0-20261102-LP3-user-approved'
        report = self.write('audits/advisor-scan.json', {'issues': [issue]})
        approval = {'revision': component['version'], 'exception_ref': exception_ref,
                    'approval': {'response': 'Approve', 'context': 'Fixture approval of this exact LP3 finding'},
                    'sha256': copy.deepcopy(component['hashes']),
                    'report_ref': 'audits/advisor-scan.json', 'report_sha256': digest(report)}
        self.write('audits/advisor-exception.json', approval)
        audit = json.loads((self.repo / component['audit_ref']).read_text())
        audit.update(status='reviewed-with-user-exception', exception_ref=exception_ref)
        self.write(component['audit_ref'], audit)
        component['exception'] = {'ref': exception_ref, 'review': 'audits/advisor-exception.json',
                                  'report': 'audits/advisor-scan.json'}
        self.save_manifest()
        self.report_mutation = lambda r: r.update(issues=[copy.deepcopy(issue)])
        return component, issue

    def test_approved_advisor_exception_installs_only_exact_reviewed_payload(self):
        self.approve_advisor_fixture()
        self.assertTrue(self.install()['ready'])
        self.assertTrue(self.check()['ready'])

    def test_advisor_exception_does_not_cover_changed_payload(self):
        component, _ = self.approve_advisor_fixture()
        source = self.repo / component['path'] / 'SKILL.md'
        source.write_text(source.read_text() + 'Changed instructions.\n')
        component['hashes']['SKILL.md'] = digest(source)
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, 'hash|payload'):
            self.install()
        self.assertFalse(self.skills.exists())

    def test_advisor_exception_does_not_cover_new_findings(self):
        _, issue = self.approve_advisor_fixture()
        extra = {**issue, 'id': 'NEW', 'finding': 'Additional unapproved capability'}
        self.report_mutation = lambda r: r.update(issues=[issue, extra])
        with self.assertRaisesRegex(ValueError, 'finding'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_advisor_approval_binds_the_exact_historical_report(self):
        self.approve_advisor_fixture()
        report = self.repo / 'audits/advisor-scan.json'
        data = json.loads(report.read_text())
        data['issues'][0]['id'] = 'OTHER'
        report.write_text(json.dumps(data))
        self.report_mutation = lambda r: r.update(issues=copy.deepcopy(data['issues']))
        with self.assertRaisesRegex(ValueError, '(?i)report|hash'):
            self.install()
        self.assertEqual(self.scan_count, 0)

    def test_advisor_exception_requires_source_review_and_explicit_approval(self):
        component, _ = self.approve_advisor_fixture()
        for path, field, value in [(component['audit_ref'], 'status', 'draft'),
                                  ('audits/advisor-exception.json', 'approval', None),
                                  ('audits/advisor-exception.json', 'revision', 'future-version')]:
            with self.subTest(field=field):
                original = (self.repo / path).read_text()
                data = json.loads(original)
                data[field] = value
                self.write(path, data)
                with self.assertRaises(ValueError):
                    self.install()
                self.write(path, original)
        self.assertEqual(self.scan_count, 0)

    def test_find_skills_restoration_requires_original_approval_and_identical_hashes(self):
        destination = self.repo / 'skills/find-skills'
        shutil.copytree(ROOT / 'skills/external/find-skills', destination)
        review_path = 'audits/find-skills-a80e4c9-20261023/review.json'
        approval_path = 'audits/find-skills-13e4063-20261018/review.json'
        report_path = 'audits/find-skills-a80e4c9-20261023/scan.json'
        for path in (review_path, approval_path, report_path):
            self.write(path, (ROOT / path).read_text())
        hashes = {p.relative_to(destination).as_posix(): digest(p)
                  for p in destination.rglob('*') if p.is_file()}
        self.manifest['components'].append({
            'name': 'find-skills', 'path': 'skills/find-skills',
            'version': 'a80e4c9d12d607631249d4d7d059f835d4b2f13a',
            'source': 'https://github.com/vercel-labs/skills', 'hashes': hashes,
            'extra_files': [], 'audit_ref': review_path,
            'exception': {'ref': 'find-skills-13e4063-20261018-user-approved',
                          'review': review_path, 'report': report_path}})
        self.save_manifest()
        issues = json.loads((ROOT / report_path).read_text())['issues']
        self.report_mutation = lambda r: r.update(issues=copy.deepcopy(issues)) if r['skill']['name'] == 'find-skills' else None
        self.install()
        self.assertTrue(self.check()['ready'])
        approval = json.loads((self.repo / approval_path).read_text())
        approval['sha256']['SKILL.md'] = '0' * 64
        self.write(approval_path, approval)
        self.assertFalse(self.check()['ready'])
        with self.assertRaisesRegex(ValueError, 'approval|hash'):
            self.install()

    def test_explicit_reinstall_can_relocate_identical_reviewed_checkout(self):
        self.install()
        moved = self.base / 'moved'
        shutil.copytree(self.repo, moved)
        self.assertFalse(self.mod.check_bundle(moved, self.skills, self.codex)['ready'])
        self.mod.install_bundle(moved, self.skills, self.codex, scanner=self.scanner)
        self.assertTrue(self.mod.check_bundle(moved, self.skills, self.codex)['ready'])
        self.assertFalse(self.check()['ready'])

    def test_malformed_report_sections_fail_clearly_without_activation(self):
        for field in ('analysis_completeness', 'metadata'):
            self.report_mutation = lambda r: r.update({field: []})
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'scan|Scan'):
                self.install()
            self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_scanner_failure_exit_without_findings_is_not_accepted(self):
        self.scan_exit = 1
        with self.assertRaisesRegex(ValueError, '(?i)scan'):
            self.install()
        self.assertFalse((self.skills / 'tool-advisor').exists())

    def test_unreviewed_extra_code_is_not_covered_by_source_audit(self):
        helper = self.write('extra.py', 'print("not reviewed with this skill")')
        self.manifest['components'][0]['extra_files'] = [
            {'source': 'extra.py', 'destination': 'scripts/extra.py', 'sha256': digest(helper)}]
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, '(?i)extra|license|audit'):
            self.install()
        self.assertEqual(self.scan_count, 0)

    def test_grilling_shared_license_is_included_and_checked(self):
        self.add_grilling()
        license_path = 'skills/external/matt-pocock/LICENSE'
        license_file = self.write(license_path, (ROOT / license_path).read_text())
        self.manifest['components'][-1]['extra_files'] = [
            {'source': license_path, 'destination': 'LICENSE', 'sha256': digest(license_file)}]
        self.save_manifest()
        self.install()
        self.assertEqual((self.skills / 'grilling/LICENSE').read_bytes(), license_file.read_bytes())
        self.assertTrue(self.check()['ready'])

    def test_verified_package_is_used_instead_of_unverified_console_launcher(self):
        fake = self.fake_run
        def refuse_launcher(args, **kwargs):
            if pathlib.Path(args[0]) == self.scanner:
                raise AssertionError('Unverified console launcher was executed')
            return fake(args, **kwargs)
        with mock.patch.object(self.mod.subprocess, 'run', side_effect=refuse_launcher):
            self.install()
        self.assertTrue(self.check()['ready'])


if __name__ == '__main__':
    unittest.main()
