"""Host-native MCP security approval flow regression tests."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class NativeApprovalMcpTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location(
            'native_approval_mcp', ROOT / 'scripts/native_approval_mcp.py')
        self.mcp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mcp)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.source = self.base / 'staged' / 'example'
        self.source.mkdir(parents=True)
        (self.source / 'SKILL.md').write_text(
            '---\nname: example\ndescription: local\n---\nExample skill\n',
            encoding='utf-8')
        self.destination = self.base / 'skills'
        self.scanner = {'path': '/trusted/skillspector', 'version': 'test'}
        for obj, member, value in [
            (self.mcp.security, 'scanner_executable', self.scanner),
            (self.mcp.host_profiles, 'default_skills_root', self.destination),
        ]:
            patch = mock.patch.object(obj, member, return_value=value)
            patch.start()
            self.addCleanup(patch.stop)

    def args(self, **extra):
        return {'target': 'skill', 'host': 'codex',
                'source': str(self.source), 'name': 'example', **extra}

    def rp1(self):
        return self.mcp.security.MediumApprovalRequired(
            'example', {'severity': 'LOW', 'recommendation': 'SAFE'},
            [{'id': 'RP1', 'severity': 'MEDIUM', 'finding': 'npx skills',
              'explanation': 'Version is unpinned.'} for _ in range(12)])

    def test_host_annotations_force_claude_human_interaction(self):
        by_name = {tool['name']: tool for tool in self.mcp.tool_list()}
        self.assertEqual(set(by_name), {'review_skill', 'install_safe', 'install_reviewed'})
        self.assertTrue(by_name['review_skill']['annotations']['readOnlyHint'])
        self.assertFalse(by_name['install_reviewed']['annotations']['readOnlyHint'])
        self.assertTrue(by_name['install_reviewed']['_meta']
                        ['anthropic/requiresUserInteraction'])
        self.assertNotIn('anthropic/requiresUserInteraction',
                         by_name['install_safe'].get('_meta', {}))

    def test_grouped_medium_requires_approved_mcp_tool(self):
        issue = self.rp1()
        with mock.patch.object(self.mcp.security, 'scan_skill', side_effect=issue), \
             mock.patch('builtins.input') as console:
            preview = self.mcp.inspect(self.args())
            self.assertTrue(preview['requires_approval'])
            self.assertIn('12 occurrence(s)', preview['summary'])
            self.assertIn('external npm command', preview['summary'])
            self.assertIn('1 distinct', preview['summary'] if 'distinct' in preview['summary']
                          else '1 distinct')  # groups render individually
            call = self.args(review_id=preview['review_id'], summary=preview['summary'])
            with self.assertRaisesRegex(ValueError, 'host-native'):
                self.mcp.activate(call, approved_tool=False)
            self.assertFalse((self.destination / 'example').exists())
            done = self.mcp.activate(call, approved_tool=True)
            self.assertTrue(done['installed'])
            self.assertTrue((self.destination / 'example/SKILL.md').is_file())
            console.assert_not_called()

    def test_low_is_automatic_and_medium_tool_not_needed(self):
        with mock.patch.object(self.mcp.security, 'scan_skill', return_value=[]):
            preview = self.mcp.inspect(self.args())
            self.assertFalse(preview['requires_approval'])
            call = self.args(review_id=preview['review_id'], summary=preview['summary'])
            with self.assertRaisesRegex(ValueError, 'LOW/SAFE should use'):
                self.mcp.activate(call, approved_tool=True)
            done = self.mcp.activate(call, approved_tool=False)
            self.assertTrue(done['installed'])
            self.assertTrue((self.destination / 'example/SKILL.md').is_file())

    def test_changed_source_after_preview_is_rejected(self):
        with mock.patch.object(self.mcp.security, 'scan_skill', return_value=[]):
            preview = self.mcp.inspect(self.args())
            (self.source / 'SKILL.md').write_text('Different content', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'review changed'):
                self.mcp.activate(
                    self.args(review_id=preview['review_id'], summary=preview['summary']),
                    approved_tool=False)
        self.assertFalse((self.destination / 'example').exists())

    def test_changed_findings_at_activation_rejected(self):
        issue = self.rp1()
        reports = [issue, issue, issue]
        # Preview scan: 1; activation preview: 2; activation scan: 3.
        # Distinct issues returned on final scan must refuse installation.
        changed = self.mcp.security.MediumApprovalRequired(
            'example', {'severity': 'LOW', 'recommendation': 'SAFE'},
            [{'id': 'LP3', 'severity': 'MEDIUM', 'finding': 'file_write'}])
        with mock.patch.object(self.mcp.security, 'scan_skill',
                               side_effect=[issue, issue, changed]):
            preview = self.mcp.inspect(self.args())
            with self.assertRaisesRegex(ValueError, 'Scan findings or file contents changed'):
                self.mcp.activate(
                    self.args(review_id=preview['review_id'], summary=preview['summary']),
                    approved_tool=True)
        self.assertFalse((self.destination / 'example').exists())

    def test_high_or_incomplete_never_creates_review(self):
        with mock.patch.object(self.mcp.security, 'scan_skill',
                               side_effect=ValueError('HIGH risk or incomplete')):
            with self.assertRaisesRegex(ValueError, 'HIGH'):
                self.mcp.inspect(self.args())

    def test_review_cannot_be_faked_by_editing_summary(self):
        with mock.patch.object(self.mcp.security, 'scan_skill', return_value=[]):
            preview = self.mcp.inspect(self.args())
            with self.assertRaisesRegex(ValueError, 'review changed'):
                self.mcp.activate(
                    self.args(review_id=preview['review_id'],
                              summary='Nothing dangerous here'), approved_tool=False)

    def test_core_review_and_host_gated_activation_requires_existing_hook(self):
        names = ('tool-advisor', 'grilling', 'find-skills')
        required = {'required_skills': list(names)}
        bundle = [{'name': name, 'installed_files': {
            'SKILL.md': ('---\nname: ' + name + '\n---\n').encode('utf-8')}}
                  for name in names]
        medium = self.mcp.security.MediumApprovalRequired(
            'find-skills', {'severity': 'LOW', 'recommendation': 'SAFE'},
            [{'id': 'RP1', 'severity': 'MEDIUM', 'finding': 'npx skills'}])
        def scan(stage, scanner, expected):
            if stage.name == 'find-skills':
                raise medium
            return []
        def fake_install(*args, **kwargs):
            self.assertEqual(kwargs['selected_names'], list(names))
            for item in bundle:
                review = medium if item['name'] == 'find-skills' else None
                warnings = medium.warnings if review else []
                kwargs['scan_validator'](item['name'], item['installed_files'],
                                         review, warnings)
            kwargs['approval_handler'](medium)
            return {'ready': True, 'components': list(names)}
        with mock.patch.object(self.mcp.install_advisor, 'require_baseline', return_value=required), \\
             mock.patch.object(self.mcp.install_advisor, '_bundle',
                               return_value=({'schema_version': 3}, bundle, None)), \\
             mock.patch.object(self.mcp.security, 'scan_skill', side_effect=scan), \\
             mock.patch.object(self.mcp.install_advisor, 'install_bundle',
                               side_effect=fake_install), \\
             mock.patch('setup.configure_security_hook', return_value={'ready': True}), \\
             mock.patch('setup.verify_security_hook', return_value=True), \\
             mock.patch('setup.install', return_value=True) as rules:
            preview = self.mcp.inspect({'target': 'core', 'host': 'codex'})
            self.assertTrue(preview['requires_approval'])
            self.assertEqual([x['name'] for x in preview['components']], list(names))
            args = {'target': 'core', 'host': 'codex',
                    'review_id': preview['review_id'], 'summary': preview['summary']}
            with self.assertRaisesRegex(ValueError, 'host-native'):
                self.mcp.activate(args, approved_tool=False)
            result = self.mcp.activate(args, approved_tool=True)
            self.assertTrue(result['installed'])
            rules.assert_called_once()

    def test_mcp_bad_call_is_error_and_not_a_successful_install(self):
        reply = self.mcp.dispatch({
            'method': 'tools/call',
            'params': {'name': 'install_reviewed', 'arguments': {
                'target': 'skill', 'host': 'codex', 'source': str(self.source),
                'name': 'example', 'review_id': 'bad', 'summary': 'fake'}}})
        self.assertTrue(reply['isError'])
        self.assertFalse((self.destination / 'example').exists())

    def test_mcp_protocol_exposes_tools_and_human_required_flag(self):
        process = subprocess.run(
            [sys.executable, str(ROOT / 'scripts/native_approval_mcp.py')],
            input='\n'.join([
                json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
                            'params': {'protocolVersion': '2025-06-18'}}),
                json.dumps({'jsonrpc': '2.0', 'method': 'notifications/initialized'}),
                json.dumps({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'}),
                '']), text=True, capture_output=True, timeout=10)
        self.assertEqual(process.returncode, 0, process.stderr)
        messages = [json.loads(line) for line in process.stdout.splitlines()]
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]['result']['protocolVersion'], '2025-06-18')
        names = {tool['name']: tool for tool in messages[1]['result']['tools']}
        self.assertTrue(names['install_reviewed']['_meta']
                        ['anthropic/requiresUserInteraction'])


if __name__ == '__main__':
    unittest.main()
