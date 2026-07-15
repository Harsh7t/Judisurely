"""Resolve project root reliably (local + Kaggle)."""

from __future__ import annotations

import os
from pathlib import Path


def find_project_root() -> Path:
    """Find repo root by locating data/legal_kb.json."""
    env_root = os.getenv("NYAY_MITRA_ROOT")
    if env_root:
        root = Path(env_root)
        if (root / "data" / "legal_kb.json").is_file():
            return root.resolve()

    candidates = []
    here = Path(__file__).resolve().parent.parent
    candidates.append(here)
    candidates.append(Path.cwd())

    for base in candidates:
        for path in [base, *base.parents]:
            if (path / "data" / "legal_kb.json").is_file():
                return path.resolve()

    # Fallback: layout relative to this file
    return here.resolve()


PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "data"
