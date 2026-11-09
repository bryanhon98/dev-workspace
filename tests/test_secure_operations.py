"""Controlled standalone skill installation security regression tests."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


class SecureOperationsTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('secure_operations',
                                                      ROOT / 'scripts/install_selected_skill.py')
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

    def test_existing_skill_is_not_overwritten(self):
        existing = self.skills / 'example'
        existing.mkdir(parents=True)
        (existing / 'SKILL.md').write_text('User data')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            self.mod.install_skill(self.source, self.skills, 'example')
        self.assertEqual((existing / 'SKILL.md').read_text(), 'User data')

    def test_missing_scanner_blocks(self):
        with mock.patch.object(self.mod, '_scanner_executable',
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

if __name__ == '__main__':
    unittest.main()
