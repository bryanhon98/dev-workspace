#!/usr/bin/env python3
"""Local evidence retrieval and read-only skill discovery; never installs anything."""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LIBRARY = ROOT / 'knowledge/reel-library'
IMPORT = LIBRARY / 'imports/2026-11-01-meta'


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def entities():
    return read_json(IMPORT / 'entities.json')['entities']


def report_sources():
    rows = []
    for number, line in enumerate((IMPORT / 'FULL_REPORT.md').read_text(encoding='utf-8').splitlines(), 1):
        if re.match(r'^\| \d+ \| reel_', line):
            cells = [c.strip() for c in line.strip('|').split('|')]
            if len(cells) != 6:
                raise ValueError(f'Unexpected report table format at line {number}')
            rows.append(dict(zip(('ordinal', 'source_id', 'outcome', 'entities', 'insight', 'url'), cells),
                             report_line=number))
    return rows


def categories():
    groups = defaultdict(list)
    current = 'Uncategorized in supplied index'
    for line in (IMPORT / 'index.md').read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            current = re.sub(r' \(\d+\)$', '', line[3:])
        match = re.search(r'\.\./entities/([^/)]+)\.md', line)
        if match:
            groups[match[1]].append(current)
    return groups


def stats():
    data = read_json(IMPORT / 'entities.json')
    items, rows, groups = data['entities'], report_sources(), categories()
    ids = {e['id'] for e in items}
    if len(ids) != len(items) or data['total_entities'] != len(items):
        raise ValueError('Duplicate entity IDs or inconsistent total')
    if any(not re.fullmatch(r'[a-z0-9-]+', i) for i in ids):
        raise ValueError('Unsafe entity ID')
    if len({r['source_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate report source IDs')
    if set(groups) - ids:
        raise ValueError('Index refers to unknown entities')
    report_ids = {r['source_id'] for r in rows}
    source_refs = {s['source_id'] for e in items for s in e['sources']}
    unknown = source_refs - report_ids
    if unknown:
        raise ValueError('Entity source not found in report: ' + ', '.join(sorted(unknown)))
    for e in items:
        if e['primary_source_id'] not in report_ids:
            raise ValueError('Unknown primary source: ' + e['id'])
        if not all(isinstance(e[k], str) for k in ('id', 'display_name', 'slug', 'latest_insight', 'outcome')):
            raise ValueError('Invalid entity text fields')
    return {
        'entities': len(items), 'report_sources': len(rows),
        'outcomes': dict(Counter(r['outcome'] for r in rows)),
        'original_index_unique_entities': len(groups),
        'uncategorized_entities': len(ids - set(groups)),
        'entities_with_incomplete_source_lists': sum(e['mention_count'] > len(e['sources']) for e in items),
        'distinct_latest_insights': len({e['latest_insight'] for e in items}),
        'distinct_entity_source_references': len(source_refs),
        'report_sources_without_entity_source_reference': sorted(report_ids - source_refs),
        'upstream_verification': 'not-performed-by-import',
        'original_media_review': 'not-performed-by-import',
    }


def verify():
    for entry in read_json(IMPORT / 'manifest.json')['files']:
        data = (IMPORT / entry['path']).read_bytes()
        if len(data) != entry['bytes'] or hashlib.sha256(data).hexdigest() != entry['sha256']:
            raise ValueError('Archive integrity mismatch: ' + entry['path'])
    result = stats()
    for path, expected in generated().items():
        if not path.exists() or path.read_text(encoding='utf-8') != expected:
            raise ValueError('Derived file missing or stale; run build: ' + str(path.relative_to(ROOT)))
    return dict(result, archive_hashes_match=True, derived_files_match=True)


def generated():
    items, groups = entities(), categories()
    index = ['# Reel research index', '',
             'Generated from all 1,083 supplied entity records. These include tools, concepts, people,',
             'showcases and skipped food content; this is not a list of 1,083 verified tools.',
             'Categories preserve the supplied index; uncategorized entries remain explicit.',
             'Read [coverage and limitations](REVIEW.md) and the [advisor workflow](../ADVISOR.md).', '']
    heading = ['# Supplied entity details', '',
               'Generated without changing source wording. All descriptions below are **unverified reel claims**.',
               '“Latest”, mention counts and outcomes are source labels, not independent verification.',
               'Some descriptions and source lists were already truncated in the supplied export.',
               'Use `python3 scripts/knowledge.py show ID` for the exact JSON and related report rows.', '']
    by_category = defaultdict(list)
    catalogs = {}
    for e in sorted(items, key=lambda x: x['id']):
        catalog = catalogs.setdefault(e['id'][0], list(heading))
        for group in groups.get(e['id'], ['Uncategorized in supplied index']):
            by_category[group].append(e)
        catalog.extend([f"## {e['id']}", '', f"**{html.escape(e['display_name'])}** · Source outcome: {e['outcome']}", '',
                        f"Reported mentions: {e['mention_count']}; supplied source records: {len(e['sources'])}.", '',
                        html.escape(e['latest_insight']), '', f"Primary: {e['primary_source_id']} — {e['primary_url']}", '',
                        'Supplied URLs:', '', *('- ' + u for u in e['all_urls']), '', 'Supplied source snippets:', ''])
        for source in e['sources']:
            catalog.extend([f"- {source['source_id']} ({source['outcome']}) — {source['url']}",
                            '  ' + html.escape(source['insight_snippet'])])
        catalog.append('')
    for group, entries in sorted(by_category.items()):
        index.extend([f'## {group} ({len(entries)})', ''])
        index.extend(f"- [{html.escape(e['display_name'])}](entities/{e['id'][0]}.md#{e['id']}) — `{e['id']}` — {e['outcome']}" for e in entries)
        index.append('')
    output = {LIBRARY / 'index.md': '\n'.join(index),
              LIBRARY / 'coverage.json': json.dumps(stats(), indent=2, ensure_ascii=False) + '\n'}
    output.update({LIBRARY / 'entities' / (letter + '.md'): '\n'.join(line.rstrip() for line in lines)
                   for letter, lines in catalogs.items()})
    return output



def saved_github_records(library_dir):
    """Index linked GitHub project headings across saved category and research notes.

    This is a local, read-only candidate index, not verification of upstream code.
    """
    found = {}
    for path in sorted(library_dir.rglob('*.md')):
        if path.name in {'README.md', 'not-selected.md'} or path.is_symlink():
            continue
        content = path.read_text(encoding='utf-8')
        for section in re.split(r'(?=^#{2,3}\\s)', content, flags=re.MULTILINE):
            heading = section.split('\\n', 1)[0]
            match = re.match(
                r'^#{2,3}\\s+\\[([^\\]]+)\\]\\(https://github\\.com/([\\w.-]+)/([\\w.-]+)(?:/[^)]*)?\\)',
                heading, flags=re.IGNORECASE)
            if not match:
                continue
            name, owner, repo_name = match.groups()
            repo = f'{owner}/{repo_name.removesuffix(".git")}'.lower()
            document = (Path('github-repos') / path.relative_to(library_dir)).as_posix()
            if repo not in found:
                found[repo] = {
                    'id': 'saved-github:' + repo,
                    'name': name,
                    'collection': 'saved-github',
                    'evidence_status': 'saved-library-research; not-installed-or-security-approved',
                    'purpose': section.split('\\n', 1)[-1].strip()[:1200],
                    'source': 'https://github.com/' + repo,
                    'details': document,
                    'catalog_files': [document],
                    '_text': '',
                }
            entry = found[repo]
            if document not in entry['catalog_files']:
                entry['catalog_files'].append(document)
            entry['_text'] += '\\n' + section[:2400]
    return list(found.values())


def decision_records(directory):
    records = []
    for path in sorted(directory.glob('*.json')):
        e = read_json(path)
        records.append({'id': 'decision:' + e['id'], 'name': e['task'], 'collection': 'decisions',
                        'evidence_status': 'task-specific-decision; recheck-applicability',
                        'purpose': e['task'], 'recorded_at': e['recorded_at'],
                        'details': 'knowledge/decisions/' + path.name,
                        '_text': json.dumps(e, ensure_ascii=False)})
    return records


def search(query, limit):
    terms = set(re.findall(r'\w+', query.casefold()))
    if not terms:
        raise ValueError('Provide a nonempty search query')
    records = []
    for e in entities():
        if e['outcome'] == 'skipped':
            continue
        records.append({'id': 'reel:' + e['id'], 'name': e['display_name'], 'collection': 'reels',
                        'evidence_status': 'unverified-reel-claim', 'purpose': e['latest_insight'],
                        'source': e['primary_url'], 'details': f'knowledge/reel-library/entities/{e["id"][0]}.md#{e["id"]}',
                        '_text': json.dumps(e, ensure_ascii=False)})
    for e in read_json(ROOT / 'inventory.json')['components']:
        records.append({'id': 'inventory:' + e['name'], 'name': e['name'], 'collection': 'inventory',
                        'evidence_status': e.get('audit_status', 'unknown'), 'purpose': e.get('purpose', ''),
                        'source': e.get('github_url', e.get('source')), 'details': 'inventory.json',
                        'version': e.get('version'), 'restorable': e.get('restorable', False),
                        '_text': json.dumps(e, ensure_ascii=False)})
    for e in read_json(ROOT / 'github-repos/reviews.json')['repositories']:
        records.append({'id': 'review:' + e['repo'], 'name': e['repo'], 'collection': 'reviews',
                        'evidence_status': 'historical-source-review; refresh-before-recommending',
                        'purpose': e.get('purpose', ''), 'source': 'https://github.com/' + e['repo'],
                        'details': 'github-repos/reviews.json', 'version': e.get('sha'),
                        'prior_decision': e.get('catalog_decision'), '_text': json.dumps(e, ensure_ascii=False)})
    records.extend(saved_github_records(ROOT / 'github-repos'))
    for e in report_sources():
        if e['outcome'] in {'skipped', 'blocked'}:
            continue
        records.append({'id': 'report:' + e['source_id'], 'name': e['source_id'], 'collection': 'report',
                        'evidence_status': 'unverified-reel-claim; truncated-report-insight',
                        'purpose': e['insight'], 'source': e['url'],
                        'details': 'knowledge/reel-library/imports/2026-11-01-meta/FULL_REPORT.md',
                        'report_line': e['report_line'], '_text': json.dumps(e, ensure_ascii=False)})
    records.extend(decision_records(ROOT / 'knowledge/decisions'))
    ranked = []
    for r in records:
        words = set(re.findall(r'\w+', r.pop('_text').casefold()))
        name_words = set(re.findall(r'\w+', r['name'].casefold()))
        matches = terms & words
        if not matches:
            continue
        score = len(matches) + 4 * len(terms & name_words)
        if terms == name_words:
            score += 100
        r['retrieval_score'] = score
        r['matched_terms'] = sorted(matches)
        ranked.append(r)
    ranked.sort(key=lambda r: (-r['retrieval_score'], r['id']))
    return {'query': query, 'notice': 'Lexical discovery only, not a suitability ranking. Read details and verify upstream before recommending.',
            'total_matches': len(ranked), 'results': ranked[:limit]}


def show(entity_id):
    entity_id = entity_id.removeprefix('reel:')
    item = next((e for e in entities() if e['id'] == entity_id), None)
    if item is None:
        raise ValueError('Unknown entity ID: ' + entity_id)
    refs = {s['source_id'] for s in item['sources']} | {item['primary_source_id']}
    return {'entity': item, 'source_list_incomplete': item['mention_count'] > len(item['sources']),
            'upstream_verified': False, 'categories': categories().get(entity_id, []),
            'report_rows': [r for r in report_sources() if r['source_id'] in refs or entity_id in r['entities'].split(',')],
            'notice': 'Report insights are truncated; primary_url points to a reel, not an official tool source.'}


def inspect(roots):
    skills, missing, errors, links = [], [], [], []
    seen = set()
    for value in roots:
        root = Path(value).expanduser().absolute()
        if not root.is_dir():
            missing.append(str(root))
            continue
        def walk_error(error):
            errors.append(str(error))
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=walk_error):
            for name in list(dirs):
                p = Path(directory) / name
                if p.is_symlink():
                    links.append(str(p))
                    dirs.remove(name)
                elif name in {'.git', 'node_modules', '__pycache__', '.venv'}:
                    dirs.remove(name)
            if 'SKILL.md' not in files:
                continue
            path = Path(directory) / 'SKILL.md'
            if path.is_symlink():
                links.append(str(path))
                continue
            if path.resolve() in seen:
                continue
            seen.add(path.resolve())
            try:
                data = path.read_bytes()
                content = data.decode('utf-8')
                header = re.match(r'\A---\s*\n(.*?)\n---(?:\n|$)', content, re.S)
                name = re.search(r'^name:\s*(.+)$', header[1], re.M) if header else None
                skills.append({'path': str(path), 'name': name[1].strip('"\' ') if name else path.parent.name,
                               'instruction_sha256': hashlib.sha256(data).hexdigest(),
                               'metadata_text': header[1] if header else None,
                               'status': 'file-observed; activation/version/dependencies-unverified'})
            except (OSError, UnicodeError) as error:
                errors.append(f'{path}: {error}')
    identical, names = defaultdict(list), defaultdict(list)
    for s in skills:
        identical[s['instruction_sha256']].append(s['path'])
        names[s['name']].append(s['path'])
    return {'observed_at': datetime.now(timezone.utc).isoformat(), 'scope': 'this machine; explicit roots only',
            'skills': sorted(skills, key=lambda s: s['path']), 'unavailable_roots': missing,
            'errors': errors, 'unfollowed_symlinks': links,
            'identical_instruction_groups': [v for v in identical.values() if len(v) > 1],
            'same_name_groups': [v for v in names.values() if len(v) > 1],
            'notice': 'Instructions only. Same text does not prove identical dependencies or redundant capability. Read full skills and supporting files. Symlink targets require an explicit --root. Keep device paths local.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    find = commands.add_parser('search')
    find.add_argument('query')
    find.add_argument('--limit', type=int, default=10)
    detail = commands.add_parser('show')
    detail.add_argument('id')
    local = commands.add_parser('inspect')
    local.add_argument('--root', action='append', required=True)
    commands.add_parser('verify')
    commands.add_parser('build', help='Regenerate readable views; preserves archived originals')
    args = parser.parse_args()
    try:
        if args.command == 'search':
            if args.limit < 1:
                raise ValueError('--limit must be positive')
            result = search(args.query, args.limit)
        elif args.command == 'show':
            result = show(args.id)
        elif args.command == 'inspect':
            result = inspect(args.root)
        elif args.command == 'verify':
            result = verify()
        else:
            # Check originals before writing derived views.
            for f in read_json(IMPORT / 'manifest.json')['files']:
                if hashlib.sha256((IMPORT / f['path']).read_bytes()).hexdigest() != f['sha256']:
                    raise ValueError('Archive hash mismatch: ' + f['path'])
            for path, content in generated().items():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
            result = verify()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
