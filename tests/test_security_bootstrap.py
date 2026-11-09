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
    def test_setup_orders_scanner_hook_advisor_and_rules(self):
        setup = load_setup()
        events = []
        with tempfile.TemporaryDirectory() as root:
            home, skills = Path(root) / 'profile', Path(root) / 'skills'
            scanner = mock.Mock()
            scanner.ensure_scanner.side_effect = lambda value: (
                events.append('scanner') or {'path': '/scanner', 'version': 'test'})
            scanner.verify_scanner_sample.side_effect = lambda info: events.append('sample')
            advisor = mock.Mock()
            advisor.require_baseline.side_effect = lambda root: events.append('baseline')
            advisor.install_bundle.side_effect = lambda *args, **kwargs: (
                events.append('advisor') or {'ready': True})
            with mock.patch.dict('sys.modules',
                                 {'secure_operations': scanner, 'install_advisor': advisor}), \
                 mock.patch.object(setup, 'configure_security_hook',
                    side_effect=lambda *args, **kw: events.append('hook') or {'ready': True}), \
                 mock.patch.object(setup, 'verify_security_hook',
                    side_effect=lambda root: events.append('hook-test')), \
                 mock.patch.object(setup, 'install', side_effect=lambda *args: events.append('rules')):
                result = setup.setup_workspace('codex', home, skills)
            self.assertTrue(result['ready'])
            self.assertEqual(events, ['baseline', 'scanner', 'sample',
                                      'hook', 'hook-test', 'advisor', 'rules'])
            self.assertFalse(result['live_host_verified'])

    def test_failed_scanner_never_installs_baseline(self):
        setup = load_setup()
        scanner = mock.Mock()
        scanner.ensure_scanner.side_effect = ValueError('scanner unavailable')
        advisor = mock.Mock()
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
