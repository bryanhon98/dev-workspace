"""Patch input must be classified as a structured edit, not a shell command."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PatchParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('patch_guard', ROOT / 'scripts/skill_security_hook.py')
        cls.guard = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.guard)

    def decision(self, **args):
        return self.guard.decide({'hook_event_name': 'PreToolUse',
                                  'tool_name': 'apply_patch', 'tool_input': args})

    def test_missing_or_malformed_patch_fails_closed(self):
        for patch in ['', 'ordinary text', '*** Begin Patch\n*** End Patch',
                      '*** Begin Patch\n*** Unknown: docs/a.md\n*** End Patch',
                      '*** Begin Patch\n*** Add File: docs/a.md\nnaked content\n*** End Patch',
                      '*** Begin Patch\n*** Move to: docs/a.md\n*** End Patch',
                      '*** Begin Patch\n*** Delete File: docs/a.md\n+unexpected\n*** End Patch']:
            with self.subTest(patch=patch):
                self.assertIsNotNone(self.decision(command=patch)[0])

    def test_ambiguous_payload_fields_fail_closed(self):
        patch = '*** Begin Patch\n*** Add File: docs/a.md\n+hello\n*** End Patch'
        self.assertIsNotNone(self.decision(command=patch, patch=patch)[0])

    def test_add_update_move_and_delete_are_accepted(self):
        patches = [
            '*** Begin Patch\n*** Add File: docs/a.md\n+hello\n*** End Patch',
            '*** Begin Patch\n*** Update File: docs/a.md\n@@\n-old\n+new\n*** End Patch',
            '*** Begin Patch\n*** Update File: docs/a.md\n*** Move to: docs/b.md\n@@\n-old\n+new\n*** End Patch',
            '*** Begin Patch\n*** Delete File: docs/a.md\n*** End Patch',
        ]
        for patch in patches:
            with self.subTest(patch=patch):
                self.assertEqual(self.decision(patch=patch), (None, None))

    def test_content_that_resembles_headers_is_not_a_destination(self):
        patch = ('*** Begin Patch\n*** Add File: docs/example.md\n'
                 '+*** Move to: example displayed in documentation\n*** End Patch')
        self.assertEqual(self.decision(command=patch), (None, None))

    def test_active_path_in_prose_is_allowed_but_real_destination_is_denied(self):
        patch = ('*** Begin Patch\n*** Add File: docs/example.md\n'
                 '+Example: .agents/skills/demo/SKILL.md\n*** End Patch')
        self.assertEqual(self.decision(command=patch), (None, None))
        for target in ('.agents/skills/demo/SKILL.md',
                       'docs/../.agents/skills/demo/SKILL.md',
                       r'C:\Users\example\.agents\skills\demo\SKILL.md'):
            for operation in ('Add File', 'Update File', 'Delete File'):
                body = '\n+hello' if operation == 'Add File' else ''
                patch = f'*** Begin Patch\n*** {operation}: {target}{body}\n*** End Patch'
                self.assertIsNotNone(self.decision(command=patch)[0])
            patch = ('*** Begin Patch\n*** Update File: docs/a.md\n'
                     f'*** Move to: {target}\n@@\n-old\n+new\n*** End Patch')
            self.assertIsNotNone(self.decision(command=patch)[0])


if __name__ == '__main__':
    unittest.main()
