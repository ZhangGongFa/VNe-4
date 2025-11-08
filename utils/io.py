# utils/io.py
from __future__ import annotations
import os
from pathlib import Path
import pandas as pd

ENCODINGS = ("utf-8-sig", "utf-8", "latin1")

def _try_read_csv(p: Path) -> pd.DataFrame | None:
    if not p or not p.exists() or not p.is_file():
        return None
    # thử các encoding phổ biến
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
    """
    Tìm và đọc CSV theo thứ tự:
    1) <repo_root>/<filename>
    2) <repo_root>/data/<filename>
    3) <cwd>/<filename>
    4) <cwd>/data/<filename>
    5) glob toàn repo: **/*bctc*final*.csv (không phân biệt hoa thường)
    """
    # Xác định repo_root = thư mục chứa app.py
    here = Path(__file__).resolve()
    repo_root = here.parents[1]  # utils/ -> repo root

    candidates = [
        repo_root / filename,
        repo_root / "data" / filename,
        Path.cwd() / filename,
        Path.cwd() / "data" / filename,
    ]

    # Thử trực tiếp các candidate
    for p in candidates:
        df = _try_read_csv(p)
        if df is not None:
            return df

    # Fallback: glob không phân biệt hoa thường trong repo
    pattern_parts = ["*bctc*", "*final*", "*.csv"]
    glob_hits = []
    for p in repo_root.rglob("*.csv"):
        name_low = p.name.lower()
        if all(part.strip("*").lower() in name_low for part in ["bctc", "final"]):
            glob_hits.append(p)
    # Ưu tiên file nằm trong repo_root/data
    glob_hits.sort(key=lambda x: (0 if "data" in x.parts else 1, len(str(x))))

    for p in glob_hits:
        df = _try_read_csv(p)
        if df is not None:
            return df

    raise FileNotFoundError(f"{filename} not found in repo root or ./data/ (cwd={Path.cwd()})")
