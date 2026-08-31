#!/usr/bin/env python3
"""Central path configuration for repository-quality tooling.

Code lives in ``CODE_ROOT``. Content normally lives in the same checkout, but
quality tests may point data reads/writes at a synthetic corpus with the
``SECOND_BRAIN_DATA_ROOT`` environment variable.

No-argument default: print the effective paths and whether the selected data
root is a skeleton or a populated corpus.
"""
from __future__ import annotations

import os
from pathlib import Path

CODE_ROOT = Path(__file__).resolve().parent.parent
DATA_ROOT = Path(os.environ.get("SECOND_BRAIN_DATA_ROOT", CODE_ROOT)).expanduser().resolve()
SCRIPTS_DIR = CODE_ROOT / "scripts"
AGENTS_DIR = CODE_ROOT / ".agents"
SKILLS_DIR = AGENTS_DIR / "skills"
SUBAGENTS_DIR = AGENTS_DIR / "agents"
WIKI_ROOT = DATA_ROOT / "wiki"
ESSAYS_DIR = WIKI_ROOT / "essays"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
ENTITIES_DIR = WIKI_ROOT / "entities"
INSIGHTS_DIR = WIKI_ROOT / "insights"
HANDOUTS_DIR = WIKI_ROOT / "handouts"
ASSETS_DIR = WIKI_ROOT / "assets"
SOURCES_DIR = WIKI_ROOT / "sources"
PLAN_DIR = DATA_ROOT / "plan"
RAW_DIR = DATA_ROOT / "raw"
OUTPUT_DIR = DATA_ROOT / "output"
HTML_DIR = OUTPUT_DIR / "html"
PDF_DIR = OUTPUT_DIR / "pdf"
HANDOUT_OUTPUT_DIR = OUTPUT_DIR / "handouts"
STATS_DIR = OUTPUT_DIR / "stats"
GRAPH_DIR = OUTPUT_DIR / "graph"

PAGE_DIRS = (ESSAYS_DIR, CONCEPTS_DIR, ENTITIES_DIR, INSIGHTS_DIR)


def _has_md(directory: Path) -> bool:
    return directory.is_dir() and any(p.name != ".gitkeep" for p in directory.glob("*.md"))


def corpus_has_pages() -> bool:
    return any(_has_md(d) for d in PAGE_DIRS)


def corpus_has_essays() -> bool:
    return _has_md(ESSAYS_DIR)



def relative_display(path: Path) -> Path:
    """Return a stable display path relative to DATA_ROOT or CODE_ROOT.

    Synthetic test corpora may live outside the checkout, so callers must not
    assume every wiki path is underneath CODE_ROOT.
    """
    path = Path(path).resolve()
    for root in (DATA_ROOT, CODE_ROOT):
        try:
            return path.relative_to(root)
        except ValueError:
            pass
    return path

def print_paths() -> None:
    print(f"CODE_ROOT={CODE_ROOT}")
    print(f"DATA_ROOT={DATA_ROOT}")
    print(f"WIKI_ROOT={WIKI_ROOT}")
    print(f"OUTPUT_DIR={OUTPUT_DIR}")
    print(f"mode={'corpus' if corpus_has_pages() else 'skeleton'}")


if __name__ == "__main__":
    print_paths()
