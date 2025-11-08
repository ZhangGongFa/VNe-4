"""
I/O utilities for the upgraded VNe‑4 application.

This module provides a ``read_csv_smart`` function which attempts to
load CSV files using several common encodings and searches a few
standard locations.  It mirrors the functionality of the original
repository while exposing a clean API for the rest of the application.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd

# List of encodings to attempt when reading CSV files
ENCODINGS = ("utf-8-sig", "utf-8", "latin1")


def _try_read_csv(p: Path) -> Optional[pd.DataFrame]:
    """Attempt to read a CSV file at ``p`` using common encodings.

    Returns a DataFrame if successful or ``None`` if the file cannot be
    read or has zero columns.
    """
    if not p or not p.exists() or not p.is_file():
        return None
    for enc in ENCODINGS:
        try:
            df = pd.read_csv(p, encoding=enc)
            if df.shape[1] == 0:
                continue
            return df
        except Exception:
            continue
    return None


def read_csv_smart(filename: str = "bctc_final.csv") -> pd.DataFrame:
    """Locate and read a CSV file from several candidate locations.

    The search order is:

    1. The project root.
    2. A ``data`` subdirectory under the project root.
    3. The current working directory.
    4. A ``data`` subdirectory under the current working directory.
    5. Any CSV file in the repository whose name contains
       ``bctc`` and ``final`` (case‑insensitive).

    If no matching file is found a ``FileNotFoundError`` is raised.
    """
    here = Path(__file__).resolve()
    repo_root = here.parents[1]  # utils/ -> repo root
    candidates = [
        repo_root / filename,
        repo_root / "data" / filename,
        Path.cwd() / filename,
        Path.cwd() / "data" / filename,
    ]
    for p in candidates:
        df = _try_read_csv(p)
        if df is not None:
            return df
    # fallback: search for any CSV containing both "bctc" and "final"
    glob_hits = []
    for p in repo_root.rglob("*.csv"):
        name_low = p.name.lower()
        if "bctc" in name_low and "final" in name_low:
            glob_hits.append(p)
    # prioritise files in data folders
    glob_hits.sort(key=lambda x: (0 if "data" in x.parts else 1, len(str(x))))
    for p in glob_hits:
        df = _try_read_csv(p)
        if df is not None:
            return df
    raise FileNotFoundError(f"{filename} not found in repo root or ./data/ (cwd={Path.cwd()})")