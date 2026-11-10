"""Security-first setup orchestration: scanner, hook, then Advisor baseline."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

def load_setup():
    spec = importlib.util.spec_from_file_location('setup_workspace_tests', ROOT / 'scripts/setup.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

class WorkspaceBootstrapTests(unittest.TestCase):
    def test_prepare_registers_hook_without_installing_skills_or_rules(self):
        setup = load_setup()
        events = []
        with tempfile.TemporaryDirectory() as root:
            home, skills = Path(root) / 'profile', Path(root) / 'skills'
            scanner = mock.Mock()
            scanner.ensure_scanner.side_effect = lambda value: (
                events.append('scanner') or {'path': '/scanner', 'version': 'test'})
            scanner.verify_scanner_sample.side_effect = lambda info: events.append('sample')
            advisor = mock.Mock()
            advisor.require_baseline.side_effect = lambda root: (
                events.append('baseline') or {'required_skills': ['tool-advisor', 'grilling', 'find-skills']})
            with mock.patch.dict('sys.modules',
                                 {'secure_operations': scanner, 'install_advisor': advisor}), \
                 mock.patch.object(setup, 'configure_security_hook',
                    side_effect=lambda *args, **kw: events.append('hook') or {'ready': True}) as register, \
                 mock.patch.object(setup, 'verify_security_hook',
                    side_effect=lambda root: events.append('hook-test')), \
                 mock.patch.object(setup, 'install', side_effect=lambda *args: events.append('rules')):
                result = setup.setup_workspace('codex', home, skills)
            self.assertTrue(result['prepared'])
            self.assertFalse(result['ready'])
            self.assertFalse(result['live_host_verified'])
            self.assertFalse(result['core_skills_installed'])
            self.assertEqual(events, ['scanner', 'sample', 'hook', 'hook-test'])
            self.assertTrue(register.call_args.kwargs['install'])
            advisor.install_bundle.assert_not_called()

    def test_finish_requires_user_acknowledgment_and_existing_hook(self):
        setup = load_setup()
        events = []
        with tempfile.TemporaryDirectory() as root:
            home, skills = Path(root) / 'profile', Path(root) / 'skills'
            scanner = mock.Mock()
            scanner.ensure_scanner.side_effect = lambda value: (
                events.append('scanner') or {'path': '/scanner', 'version': 'test'})
            scanner.verify_scanner_sample.side_effect = lambda info: events.append('sample')
            advisor = mock.Mock()
            advisor.require_baseline.side_effect = lambda root: (
                events.append('baseline') or {'required_skills': ['tool-advisor', 'grilling', 'find-skills']})
            advisor.install_bundle.side_effect = lambda *args, **kwargs: (
                events.append('advisor') or {'ready': True})
            with mock.patch.dict('sys.modules',
                                 {'secure_operations': scanner, 'install_advisor': advisor}), \
                 mock.patch.object(setup, 'configure_security_hook',
                    side_effect=lambda *args, **kw: events.append('hook') or {'ready': True}) as register, \
                 mock.patch.object(setup, 'verify_security_hook',
                    side_effect=lambda root: events.append('hook-test')), \
                 mock.patch.object(setup, 'install', side_effect=lambda *args: events.append('rules')):
                with self.assertRaisesRegex(ValueError, 'acknowledge-live-hook-test'):
                    setup.setup_workspace('codex', home, skills, finish=True)
                self.assertEqual(events, [])
                events.clear()
                result = setup.setup_workspace('codex', home, skills, finish=True,
                                               live_hook_test_acknowledged=True)
            self.assertTrue(result['ready'])
            self.assertTrue(result['live_host_test_acknowledged'])
            self.assertFalse(result['live_host_verified_automatically'])
            self.assertEqual(events, ['scanner', 'sample', 'hook', 'hook-test',
                                      'baseline', 'advisor', 'rules'])
            self.assertFalse(register.call_args.kwargs['install'])
            self.assertEqual(advisor.install_bundle.call_args.kwargs['selected_names'],
                             ['tool-advisor', 'grilling', 'find-skills'])


    def test_failed_scanner_never_installs_baseline(self):
        setup = load_setup()
        scanner = mock.Mock()
        scanner.ensure_scanner.side_effect = ValueError('scanner unavailable')
        advisor = mock.Mock()
        advisor.require_baseline.return_value = {'required_skills': ['tool-advisor', 'grilling', 'find-skills']}
        with tempfile.TemporaryDirectory() as root, \
             mock.patch.dict('sys.modules',
                             {'secure_operations': scanner, 'install_advisor': advisor}), \
             mock.patch.object(setup, 'configure_security_hook') as register:
            with self.assertRaisesRegex(ValueError, 'unavailable'):
                setup.setup_workspace('claude', Path(root), Path(root) / 'skills')
            register.assert_not_called()
            advisor.install_bundle.assert_not_called()

if __name__ == '__main__':
    unittest.main()
