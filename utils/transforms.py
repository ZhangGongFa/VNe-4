# utils/transforms.py
import re
import pandas as pd

def build_display_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure a 'display_year' column exists for consistent UI.
    Priority: display_year > Year > year > Năm > period.
    """
    if "display_year" in df.columns:
        df["display_year"] = df["display_year"].astype(str)
        return df

    for c in ["Year", "year", "Năm", "period"]:
        if c in df.columns:
            df["display_year"] = df[c].astype(str)
            break
    else:
        df["display_year"] = ""

    return df

def sort_year_label(label: str):
    """
    Sorting key for year labels:
    - Extract 4-digit year.
    - Real years first, forecast years (suffix 'F'/'f') after.
    - Fallback if no year found.
    """
    s = str(label).strip()
    is_forecast = s.endswith(("F", "f"))
    m = re.search(r"(19|20)\d{2}", s)
    year = int(m.group(0)) if m else 9999
    return (year, 1 if is_forecast else 0, s)

def pivot_long_to_table(fin_df: pd.DataFrame, stmt_names):
    scol = _pick(fin_df, ["statement","section"])
    lcol = _pick(fin_df, ["lineitem","line_item","line_item_name","item","account"])
    vcol = _pick(fin_df, ["value","amount"])
    ycol = _pick(fin_df, ["display_year","year_label","year"])
    if not (scol and lcol and vcol and ycol):
        return pd.DataFrame()

    mask = fin_df[scol].astype(str).str.upper().isin([s.upper() for s in stmt_names])
    sub = fin_df[mask].copy()
    if sub.empty: return pd.DataFrame()
    sub[ycol] = sub[ycol].astype(str)
    tab = sub.pivot_table(index=lcol, columns=ycol, values=vcol, aggfunc="sum")
    tab = tab.reindex(columns=sort_year_labels(tab.columns))
    return tab

def _pick(df, cands):
    lower = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in df.columns: return c
        if c.lower() in lower: return lower[c.lower()]
    return None
