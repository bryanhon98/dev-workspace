import importlib.util
import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / 'scripts' / 'setup.py'

class GlobalSetupTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('setup_rules', SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = pathlib.Path(self.tmp.name)

    def test_preserves_existing_rules_and_backs_up_exact_bytes(self):
        original = b'# Existing rules\r\nKeep my workflow.\r\n'
        target = self.home / 'AGENTS.md'
        target.write_bytes(original)
        self.mod.install(self.home, '# Setup rules\nUse global skills.\n')
        self.assertTrue(target.read_bytes().startswith(original))
        backups = list((self.home / 'personal-setup-backups').glob('*'))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)

    def test_repeated_install_is_idempotent_and_update_is_scoped(self):
        target = self.home / 'AGENTS.md'
        target.write_text('Unrelated instructions.\n')
        self.mod.install(self.home, 'Version one\n')
        first = target.read_bytes()
        self.assertFalse(self.mod.install(self.home, 'Version one\n'))
        self.assertEqual(first, target.read_bytes())
        self.mod.install(self.home, 'Version two\n')
        self.assertEqual(target.read_text().count(self.mod.START), 1)
        self.assertIn('Unrelated instructions.', target.read_text())
        self.assertNotIn('Version one', target.read_text())

    def test_uses_nonempty_global_override(self):
        (self.home / 'AGENTS.md').write_text('Base.\n')
        override = self.home / 'AGENTS.override.md'
        override.write_text('Override.\n')
        self.mod.install(self.home, 'Global setup.\n')
        self.assertIn('Global setup.', override.read_text())
        self.assertEqual((self.home / 'AGENTS.md').read_text(), 'Base.\n')
        self.assertTrue(self.mod.check(self.home, 'Global setup.\n'))

    def test_refuses_locally_modified_managed_rules(self):
        self.mod.install(self.home, 'Reviewed policy.\n')
        target = self.home / 'AGENTS.md'
        target.write_text(target.read_text().replace('Reviewed policy.', 'Local new rule.'))
        before = target.read_bytes()
        with self.assertRaisesRegex(ValueError, 'changed locally'):
            self.mod.install(self.home, 'Next policy.\n')
        self.assertEqual(target.read_bytes(), before)
        self.assertFalse(self.mod.check(self.home, 'Reviewed policy.\n'))

    def test_refuses_malformed_markers_without_touching_file(self):
        target = self.home / 'AGENTS.md'
        target.write_text('Original\n' + self.mod.START + '\nBroken block')
        before = target.read_bytes()
        with self.assertRaises(ValueError):
            self.mod.install(self.home, 'New rules.\n')
        self.assertEqual(target.read_bytes(), before)

    def test_refuses_symlink_target(self):
        other = self.home / 'other.txt'
        other.write_text('Unrelated\n')
        (self.home / 'AGENTS.md').symlink_to(other)
        with self.assertRaises(ValueError):
            self.mod.install(self.home, 'New rules.\n')
        self.assertEqual(other.read_text(), 'Unrelated\n')

    def test_check_does_not_create_files(self):
        self.assertFalse(self.mod.check(self.home, 'Rules.\n'))
        self.assertEqual(list(self.home.iterdir()), [])

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), '--codex-home', str(self.home), *args], text=True, capture_output=True)

    def test_default_lists_choices_without_installing(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Which skills', result.stdout)
        self.assertIn('Manual setup', result.stdout)
        catalog = json.loads((SCRIPT.parent.parent / 'inventory.json').read_text())
        mcps = [c for c in catalog['components'] if c['kind'] == 'mcp']
        if mcps:
            for component in mcps:
                self.assertIn(component['name'] + ' — ' + component['purpose'], result.stdout)
            self.assertNotIn('No MCP entries saved', result.stdout)
        else:
            self.assertIn('No MCP entries saved', result.stdout)
        self.assertIn('not ready to restore', result.stdout)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_advisor_check_is_readonly_and_reports_missing_installation(self):
        result = self.run_cli('--check-advisor', '--skills-root', str(self.home / 'skills'))
        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report['ready'])
        self.assertTrue(report['errors'])
        self.assertEqual(list(self.home.iterdir()), [])

    def test_advisor_install_rejects_locally_changed_rules_before_activation(self):
        self.mod.install(self.home, 'Existing rule.\n')
        target = self.home / 'AGENTS.md'
        target.write_text(target.read_text().replace('Existing rule.', 'Locally edited.'))
        before = target.read_bytes()
        result = self.run_cli('--install-advisor', '--skills-root', str(self.home / 'skills'))
        self.assertEqual(result.returncode, 1)
        self.assertIn('changed locally', result.stderr)
        self.assertEqual(target.read_bytes(), before)
        self.assertFalse((self.home / 'skills').exists())
        self.assertFalse((self.home / 'dev-workspace-advisor').exists())

    def test_rules_include_checkout_locator_for_other_projects(self):
        result = self.run_cli('--install-rules')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(str(SCRIPT.parent.parent), (self.home / 'AGENTS.md').read_text())

    def test_empty_catalog_explicitly_reports_no_mcps(self):
        (self.home / 'inventory.json').write_text('{"components": []}')
        self.mod.ROOT = self.home
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.mod.show_catalog()
        self.assertIn('No MCP entries saved', output.getvalue())

    def test_explicit_rule_install_excludes_personalisation(self):
        result = self.run_cli('--install-rules')
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.home / 'AGENTS.md').read_text()
        self.assertNotIn('Your communication principles:', text)
        self.assertNotIn('Never use empty praise', text)
        self.assertIn('SkillSpector', text)
        self.assertEqual(self.run_cli('--check').returncode, 0)

    def test_check_catches_changed_setup_rules(self):
        result = self.run_cli('--install-rules')
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.home / 'AGENTS.md'
        target.write_text(target.read_text().replace('## SkillSpector must be ready first', 'Changed locally:'))
        self.assertEqual(self.run_cli('--check').returncode, 1)

    def test_reinstalls_after_user_clears_instruction_file(self):
        self.assertEqual(self.run_cli('--install-rules').returncode, 0)
        target = self.home / 'AGENTS.md'
        target.write_text('')
        self.assertEqual(self.run_cli('--check').returncode, 1)
        self.assertEqual(self.run_cli('--install-rules').returncode, 0)
        self.assertIn('## SkillSpector must be ready first', target.read_text())
        self.assertEqual(self.run_cli('--check').returncode, 0)

if __name__ == '__main__':
    unittest.main()
