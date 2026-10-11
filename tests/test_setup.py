import importlib.util
import pathlib
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

if __name__ == '__main__':
    unittest.main()
