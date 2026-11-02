#!/usr/bin/env python3
"""Repository entrypoint for the installable advisor's project ledger."""
from pathlib import Path
import runpy


if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] /
                      'skills/custom/tool-advisor/scripts/ledger.py'), run_name='__main__')
