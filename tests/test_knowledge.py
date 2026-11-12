import hashlib
import importlib.util
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/knowledge.py'


class KnowledgeTests(unittest.TestCase):
    def run_cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_archive_integrity_and_complete_coverage(self):
        result = self.run_cli('verify')
        self.assertEqual(result['entities'], 1083)
        self.assertEqual(result['report_sources'], 475)
        self.assertEqual(result['outcomes'], {'actionable': 407, 'showcase-link-only': 60, 'skipped': 7, 'blocked': 1})
        self.assertEqual(result['original_index_unique_entities'], 181)
        self.assertTrue(result['archive_hashes_match'])

    def test_every_index_link_has_a_readable_detail_target(self):
        library = ROOT / 'knowledge/reel-library'
        links = re.findall(r'\]\(([^)]+)\)', (library / 'index.md').read_text())
        for link in links:
            path, _, anchor = link.partition('#')
            target = library / path
            self.assertTrue(target.is_file(), link)
            self.assertLess(target.stat().st_size, 500_000, link)
            if anchor:
                self.assertIn('## ' + anchor + '\n', target.read_text())

    def test_exact_tool_search_prioritizes_identity_not_mentions(self):
        result = self.run_cli('search', 'graphify', '--limit', '3')
        self.assertEqual(result['results'][0]['id'], 'reel:graphify')
        self.assertEqual(result['results'][0]['evidence_status'], 'unverified-reel-claim')
        self.assertNotIn('recommended', result['results'][0])

    def test_search_includes_existing_reviews_and_inventory(self):
        result = self.run_cli('search', 'watch', '--limit', '100')
        kinds = {r['collection'] for r in result['results']}
        self.assertTrue({'inventory', 'reviews', 'reels'} <= kinds)

    def test_saved_github_markdown_entries_are_searchable(self):
        for query, repo in [('astryx', 'meta/astryx'),
                            ('playwright', 'microsoft/playwright'),
                            ('stageshow', 'benjitaylor/skills'),
                            ('impeccable', 'pbakaus/impeccable'),
                            ('dimensional', 'enesozturk/dimensional-drawing'),
                            ('oil-ui', 'oil-oil/oil-ui'),
                            ('brand identity', 'fatihaydost/brand-identity-skill'),
                            ('awwwards-mcp', 'insane0777/awwwards-mcp'),
                            ('wangp', 'deepbeepmeep/wangp'),
                            ('wan2gp', 'deepbeepmeep/wangp')]:
            with self.subTest(query=query):
                result = self.run_cli('search', query, '--limit', '100')
                matches = [entry for entry in result['results']
                           if entry['id'] == 'saved-github:' + repo]
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]['collection'], 'saved-github')
                self.assertEqual(matches[0]['source'], 'https://github.com/' + repo)
                self.assertIn('not-installed-or-security-approved',
                              matches[0]['evidence_status'])
                self.assertTrue(matches[0]['details'].startswith('github-repos/'))

    def test_saved_github_parser_deduplicates_and_skips_rejected(self):
        spec = importlib.util.spec_from_file_location('knowledge', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            library = Path(tmp)
            (library / 'references').mkdir()
            (library / 'research').mkdir()
            (library / 'references/design.md').write_text(
                '## [Astryx](https://github.com/meta/astryx)\n\n'
                'React design-system components.\n', encoding='utf-8')
            (library / 'research/more.md').write_text(
                '## Design tools\n\n'
                '### [Astryx, alternate case](https://github.com/Meta/astryx)\n\n'
                'Same saved repository, different research note.\n', encoding='utf-8')
            (library / 'not-selected.md').write_text(
                '## [Not selected](https://github.com/example/excluded)\n',
                encoding='utf-8')
            records = module.saved_github_records(library)
            self.assertEqual(len(records), 1)
            entry = records[0]
            self.assertEqual(entry['id'], 'saved-github:meta/astryx')
            self.assertEqual(len(entry['catalog_files']), 2)
            self.assertIn('React design-system', entry['_text'])
            self.assertIn('alternate case', entry['_text'])

    def test_report_only_evidence_is_searchable(self):
        result = self.run_cli('search', 'De9EKndgQoE', '--limit', '100')
        self.assertIn('report:reel_De9EKndgQoE', {r['id'] for r in result['results']})

    def test_saved_decisions_are_retrievable(self):
        spec = importlib.util.spec_from_file_location('knowledge', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / 'decision.json').write_text(json.dumps({
                'id': 'demo', 'task': 'Caption video', 'decision': {'roles': ['transcript']},
                'recorded_at': '2026-11-01T00:00:00Z'}))
            records = module.decision_records(base)
            self.assertEqual(records[0]['id'], 'decision:demo')
            self.assertEqual(records[0]['evidence_status'], 'task-specific-decision; recheck-applicability')

    def test_project_note_without_formal_decision_fields_is_searchable(self):
        spec = importlib.util.spec_from_file_location('knowledge', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / '2026-11-12-scroll-showcase-prototype-trial.json').write_text(
                json.dumps({'date': '2026-11-12',
                            'job': 'Scroll showcase prototype',
                            'status': 'bounded-prototype-verified'}),
                encoding='utf-8')
            entries = module.decision_records(folder)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['id'],
                             'decision:2026-11-12-scroll-showcase-prototype-trial')
            self.assertEqual(entries[0]['name'], 'Scroll showcase prototype')
            self.assertEqual(entries[0]['recorded_at'], '2026-11-12')
            self.assertIn('saved-project-note', entries[0]['evidence_status'])

    def test_show_preserves_full_original_entity_and_source_gaps(self):
        result = self.run_cli('show', 'claude-code')
        raw = json.loads((ROOT / 'knowledge/reel-library/imports/2026-11-01-meta/entities.json').read_text())
        self.assertEqual(result['entity'], next(e for e in raw['entities'] if e['id'] == 'claude-code'))
        self.assertTrue(result['source_list_incomplete'])
        self.assertFalse(result['upstream_verified'])

    def test_inspect_detects_duplicates_and_missing_root_without_modifying(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            data = b'---\nname: demo\ndescription: Test skill\n---\nUse for tests.\n'
            for name in ('a', 'b'):
                (base / name).mkdir()
                (base / name / 'SKILL.md').write_bytes(data)
            result = self.run_cli('inspect', '--root', str(base), '--root', str(base / 'absent'))
            self.assertEqual(len(result['skills']), 2)
            self.assertEqual(len(result['identical_instruction_groups']), 1)
            self.assertEqual(len(result['unavailable_roots']), 1)
            self.assertEqual(result['skills'][0]['instruction_sha256'], hashlib.sha256(data).hexdigest())
            self.assertEqual(len(list(base.rglob('*'))), 4)
            self.assertEqual((base/'a/SKILL.md').read_bytes(), data)

    def test_empty_search_and_unknown_id_fail_clearly(self):
        for args in [('search', '   '), ('show', 'not-a-real-id')]:
            result = subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
