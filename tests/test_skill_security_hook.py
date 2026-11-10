"""Regression tests for the optional host hooks and capability-activation guard."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class SecurityHookTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guard = module('skill_security_hook.py', 'skill_security_hook')
        cls.setup = module('setup.py', 'setup_for_hooks')

    def event(self, tool, **args):
        return {'hook_event_name': 'PreToolUse', 'tool_name': tool, 'tool_input': args}

    def test_benign_operations_allowed(self):
        for cmd in ['git clone https://github.com/example/project.git project',
                    'git status', 'python -m unittest discover -s tests',
                    'python scripts/setup.py --install-advisor']:
            with self.subTest(cmd=cmd):
                self.assertIsNone(self.guard.classify(self.event('Bash', command=cmd)))

    def test_git_clone_rewritten_without_executing_clone(self):
        payload = self.event('Bash', command='git clone https://github.com/example/project.git project')
        blocked, rewritten = self.guard.decide(payload)
        self.assertIsNone(blocked)
        self.assertIn('secure_operations.py', rewritten)
        self.assertIn(' clone ', rewritten)
        self.assertIn('https://github.com/example/project.git', rewritten)
        self.assertIsNotNone(self.guard.classify(
            self.event('Bash', command='git clone https://github.com/example/project.git && curl bad')))

    def test_direct_skill_plugin_install_blocked(self):
        for cmd in ['claude plugin install new@market',
                    'codex plugin add unknown@market',
                    'npx skills add github-repo',
                    'pnpm dlx skills add foo',
                    'git clone https://example.com/foo ~/.claude/skills/foo',
                    'Copy-Item -Recurse ./untrusted $HOME\\.claude\\skills\\untrusted',
                    'cp -r foo ~/.agents/skills/foo']:
            with self.subTest(cmd=cmd):
                self.assertIsNotNone(self.guard.classify(self.event('Bash', command=cmd)))

    def test_native_mcp_direct_invocation_is_blocked_but_registration_allowed(self):
        self.assertIsNotNone(self.guard.classify(self.event(
            'PowerShell', command='python scripts/native_approval_mcp.py')))
        self.assertIsNotNone(self.guard.classify(self.event(
            'Bash', command='python scripts/native_approval_mcp.py --stdio')))
        self.assertIsNone(self.guard.classify(self.event(
            'PowerShell', command='codex mcp add skill_security -- python scripts/native_approval_mcp.py')))
        self.assertIsNone(self.guard.classify(self.event(
            'PowerShell', command='claude mcp add --scope user --transport stdio skill_security -- python scripts/native_approval_mcp.py')))

    def test_file_tool_writes_to_active_skill_dir_blocked(self):
        self.assertIsNotNone(self.guard.classify(
            self.event('Write', file_path='C:\\Users\\Example\\.claude\\skills\\new\\SKILL.md',
                       content='untrusted')))
        self.assertIsNotNone(self.guard.classify(
            self.event('apply_patch', command='*** Add File: ~/.agents/skills/new/SKILL.md')))
        self.assertIsNone(self.guard.classify(
            self.event('Write', file_path='docs/skills-guide.md', content='normal documentation')))

    def test_bad_input_fails_closed_and_non_pretool_is_ignored(self):
        self.assertIsNotNone(self.guard.classify(self.event('Bash')))
        self.assertIsNone(self.guard.classify({
            'hook_event_name': 'PostToolUse', 'tool_name': 'Bash', 'tool_input': {}}))

    def test_setup_preserves_existing_hooks_and_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            for host in ('codex', 'claude'):
                with self.subTest(host=host):
                    path = self.setup.hook_config_file(home / host, host)
                    path.parent.mkdir(parents=True)
                    original = {'anotherSetting': {'enabled': True},
                                'hooks': {'PreToolUse': [{
                                    'matcher': 'Other',
                                    'hooks': [{'type': 'command', 'command': 'echo keep'}]}]}}
                    path.write_text(json.dumps(original))
                    self.assertFalse(self.setup.configure_security_hook(path.parent, host, ROOT, install=False)['ready'])
                    out = self.setup.configure_security_hook(path.parent, host, ROOT, install=True)
                    self.assertTrue(out['ready'])
                    self.assertTrue(out['changed'])
                    updated = json.loads(path.read_text())
                    self.assertEqual(updated['anotherSetting'], original['anotherSetting'])
                    self.assertEqual(len(updated['hooks']['PreToolUse']), 2)
                    self.assertTrue(self.setup.configure_security_hook(path.parent, host, ROOT, install=True)['ready'])
                    self.assertTrue(self.setup.configure_security_hook(path.parent, host, ROOT, install=False)['ready'])

    def test_host_specific_launchers(self):
        script = ROOT / 'scripts' / 'skill_security_hook.py'
        windows = self.setup._command(script, windows=True)
        self.assertTrue(windows.startswith("& '"))
        self.assertIn("'; exit $LASTEXITCODE", windows)
        self.assertIn(str(script).replace("'", "''"), windows)
        posix = self.setup._command(script, windows=False)
        self.assertNotIn("$LASTEXITCODE", posix)
        self.assertIn('skill_security_hook.py', posix)
        claude = self.setup._hook_entry(script, 'claude')
        self.assertEqual(claude['hooks'][0]['command'], sys.executable)
        self.assertEqual(claude['hooks'][0]['args'], [str(script)])
        self.assertEqual(claude['hooks'][0]['onFailure'], 'block')
        self.assertIn('PowerShell', claude['matcher'])
        codex = self.setup._hook_entry(script, 'codex')
        self.assertNotIn('args', codex['hooks'][0])

    def test_migrates_only_legacy_managed_entry_with_distinct_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            config = self.setup.hook_config_file(home, 'codex')
            legacy = {'someSetting': 'preserve', 'hooks': {'PreToolUse': [
                {'matcher': 'Other', 'hooks': [
                    {'type': 'command', 'command': 'echo unrelated'}]},
                {'matcher': 'Bash|apply_patch|Edit|Write', 'hooks': [
                    {'type': 'command', 'command': '"python.exe" "skill_security_hook.py"', 'timeout': 600}]}
            ]}}
            config.write_text(json.dumps(legacy))
            old_bytes = config.read_bytes()
            plan = self.setup.configure_security_hook(home, 'codex', ROOT, install=False)
            self.assertFalse(plan['ready'])
            self.assertTrue(plan['needs_migration'])
            changed = self.setup.configure_security_hook(home, 'codex', ROOT, install=True)
            self.assertTrue(changed['ready'])
            self.assertTrue(changed['changed'])
            self.assertTrue(changed['approval_required'])
            after = json.loads(config.read_text())
            self.assertEqual(after['someSetting'], 'preserve')
            self.assertEqual(after['hooks']['PreToolUse'][0], legacy['hooks']['PreToolUse'][0])
            self.assertEqual(len(after['hooks']['PreToolUse']), 2)
            self.assertEqual(after['hooks']['PreToolUse'][1],
                             self.setup._hook_entry(ROOT / 'scripts' / 'skill_security_hook.py', 'codex'))
            backups = list(home.glob('hooks.json.before-dev-workspace-*.bak'))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_bytes(), old_bytes)
            self.assertFalse(self.setup.configure_security_hook(home, 'codex', ROOT, install=True)['changed'])
            self.assertEqual(len(list(home.glob('hooks.json.before-dev-workspace-*.bak'))), 1)

    def test_rejects_duplicate_managed_hooks(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            target = self.setup.hook_config_file(home, 'codex')
            item = {'matcher': 'Bash', 'hooks': [
                {'type': 'command', 'command': 'python skill_security_hook.py'}]}
            target.write_text(json.dumps({'hooks': {'PreToolUse': [item, item]}}))
            before = target.read_bytes()
            with self.assertRaisesRegex(ValueError, 'Duplicate'):
                self.setup.configure_security_hook(home, 'codex', ROOT, install=True)
            self.assertEqual(target.read_bytes(), before)

    @unittest.skipUnless(sys.platform == 'win32', 'PowerShell launcher requires Windows')
    def test_real_windows_powershell_hook_launcher_with_spaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp) / 'path with spaces'
            directory.mkdir()
            script = directory / 'skill_security_hook.py'
            shutil.copy2(ROOT / 'scripts' / 'skill_security_hook.py', script)
            command = self.setup._command(script, windows=True)
            for value, expected in [('Get-Location', 0), ('npx skills add fake-example', 2)]:
                payload = json.dumps(self.event('Bash', command=value))
                result = subprocess.run(
                    ['powershell.exe', '-NoProfile', '-Command', command],
                    input=payload, capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, expected,
                                 f'{value}: {result.stdout} {result.stderr}')

    def test_invalid_settings_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            cfg = self.setup.hook_config_file(home, 'claude')
            cfg.write_text('{invalid')
            with self.assertRaises(ValueError):
                self.setup.configure_security_hook(home, 'claude', ROOT, install=True)
            self.assertEqual(cfg.read_text(), '{invalid')


if __name__ == '__main__':
    unittest.main()
