"""Host-specific paths, markers and wording for the personal setup.

Codex and Claude Code share the same installation policy but differ in where
they read instructions from, what those files are called, and how skills are
discovered. Both hosts are supported so the same scripts can set up either one
without changing the Codex behaviour.
"""

import os
from pathlib import Path

# Marker text is host-specific so a managed block is never mistaken for the
# wrong host's instructions.
MARKER_PREFIX = {
    'codex': 'personal-codex-setup',
    'claude': 'personal-claude-setup',
}

# Instruction files are host-specific. Both hosts read a single global file;
# Codex additionally honours AGENTS.override.md before AGENTS.md.
INSTRUCTION_FILES = {
    'codex': ('AGENTS.override.md', 'AGENTS.md'),
    'claude': ('CLAUDE.md',),
}

# Where managed state (receipts, scanner venv, scan reports) lives.
STATE_DIR = {
    'codex': '.codex',
    'claude': '.claude',
}

# Where skills are installed in user-global scope.
SKILLS_DIR = {
    'codex': '.agents/skills',
    'claude': '.claude/skills',
}

# The repo file that becomes the managed global instructions.
RULES_SOURCE = {
    'codex': 'global/AGENTS.md',
    'claude': 'global/CLAUDE.md',
}

# Environment variable that overrides the host home directory.
HOME_ENV = {
    'codex': 'CODEX_HOME',
    'claude': 'CLAUDE_HOME',
}

# Default home directory when the environment variable is unset.
DEFAULT_HOME = {
    'codex': '.codex',
    'claude': '.claude',
}

# Output wording that mentions the host by name.
WORDING = {
    'codex': {
        'session_note': 'Start a new Codex session to load the global rules.',
        'session_note_install': 'Start a new Codex session, then ask to use tool-advisor for your task.',
        'rules_source': 'global/AGENTS.md',
        'skill_creator': "Codex's built-in $skill-creator",
        'skill_creator_claims': "Claude's /skill-creator command is installed in Codex",
        'host_name': 'Codex',
        'instruction_name': 'Codex instructions',
        'catalog_prompt': 'Tell Codex: Which skills do you want — selected names, all eligible skills, or none?',
        'restore_note': 'Continue README.md with Codex for selected skills, manual plugin/MCP setup and GitHub logging.',
        'rules_restored': 'the repo\'s setup rules will be restored into the target device\'s global Codex instructions',
        'rules_installed': 'global/AGENTS.md only into Codex\'s user instructions',
        'restore_only': 'explicitly restores global/AGENTS.md only into Codex\'s user instructions',
        'discovery': 'Official local Codex discovery uses ~/.agents/skills',
        'native_skill_ref': 'superpowers:<name>',
    },
    'claude': {
        'session_note': 'Claude reloads CLAUDE.md at the start of each session, so the new rules apply immediately.',
        'session_note_install': 'Start a new Claude Code session, then ask to use tool-advisor for your task.',
        'rules_source': 'global/CLAUDE.md',
        'skill_creator': "Claude Code's built-in /skill-creator",
        'skill_creator_claims': "Codex's $skill-creator command is installed in Claude Code",
        'host_name': 'Claude Code',
        'instruction_name': 'Claude Code instructions',
        'catalog_prompt': 'Tell Claude: Which skills do you want — selected names, all eligible skills, or none?',
        'restore_note': 'Continue README.md with Claude for selected skills, manual plugin/MCP setup and GitHub logging.',
        'rules_restored': 'the repo\'s setup rules will be restored into the target device\'s global Claude Code instructions',
        'rules_installed': 'global/CLAUDE.md only into Claude Code\'s user instructions',
        'restore_only': 'explicitly restores global/CLAUDE.md only into Claude Code\'s user instructions',
        'discovery': 'Official local Claude Code discovery uses ~/.claude/skills',
        'native_skill_ref': 'superpowers:<name>',
    },
}

HOSTS = ('codex', 'claude')


def host_names():
    return HOSTS


def resolve(host):
    """Validate a host name and return its profile."""
    if host not in HOSTS:
        raise ValueError('Unknown host: ' + str(host) + '. Expected one of: ' + ', '.join(HOSTS))
    return host


def marker_start(host):
    return '<!-- ' + MARKER_PREFIX[resolve(host)] + '-setup:start -->'


def marker_end(host):
    return '<!-- ' + MARKER_PREFIX[resolve(host)] + '-setup:end -->'


def instruction_files(host):
    return INSTRUCTION_FILES[resolve(host)]


def state_dir(host):
    """Return the dot-directory name where managed state lives (e.g., '.codex')."""
    return STATE_DIR[resolve(host)]


def state_subdir(host):
    """Return the subdirectory name for managed receipt/scan state within the host home."""
    # For Codex: state lives in ~/.codex/dev-workspace-advisor
    # For Claude: state could live in ~/.claude/dev-workspace-advisor (or .claude-advisor)
    name = 'dev-workspace-advisor'
    return name


def skills_dir(host):
    return SKILLS_DIR[resolve(host)]


def rules_source(host):
    return RULES_SOURCE[resolve(host)]


def wording(host):
    return WORDING[resolve(host)]


def home_dir(host, home=None):
    """Return the host home directory, honouring an explicit override."""
    resolve(host)
    if home is not None:
        return Path(home)
    return Path(os.environ.get(HOME_ENV[host], str(Path.home() / DEFAULT_HOME[host])))


def default_skills_root(host):
    return Path.home() / skills_dir(host)


def default_home(host):
    return home_dir(host)


def managed_state_path(host):
    """Return the full path where managed state (receipts, scans) lives."""
    return home_dir(host) / state_subdir(host)