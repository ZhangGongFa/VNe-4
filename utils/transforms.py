"""
Transformation utilities for the upgraded VNe‑4 application.

This module defines helper functions to normalise year labels,
construct a ``display_year`` column for consistent UI across
components, and pivot long‑format financial statements into wide
format tables.  The implementation mirrors the original repository
while exposing a clean API.
"""

import re
from typing import Iterable, Optional, List

import pandas as pd


def build_display_year_column(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure that a ``display_year`` column exists in ``df``.

    If already present the column is coerced to string.  Otherwise the
    first available column among ``['Year', 'year', 'Năm', 'period']``
    is copied to ``display_year``.  If none are found the new
    column is filled with empty strings.  The original dataframe is
    modified in place and returned.
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


def sort_year_label(label: str) -> tuple:
    """Return a sorting key for year labels.

    Extracts a four digit year from ``label`` (if present) and
    distinguishes forecast years ending with ``F`` or ``f`` by
    prioritising actual years.  If no year is found a high sentinel
    value is used so that such labels sort last.
    """
    s = str(label).strip()
    is_forecast = s.endswith(("F", "f"))
    m = re.search(r"(19|20)\d{2}", s)
    year = int(m.group(0)) if m else 9999
    return (year, 1 if is_forecast else 0, s)


def sort_year_labels(labels: Iterable[str]) -> List[str]:
    """Sort a sequence of year labels chronologically.

    Handles formats like ``2024``, ``2024F``, ``2023``, etc.
    """
    return sorted(labels, key=sort_year_label)


def _pick(df: pd.DataFrame, cands: Iterable[str]) -> Optional[str]:
    """Select the first matching column name from ``df``.

    Performs case‑insensitive matching against a list of candidate
    column names.  Returns ``None`` if no matches are found.
    """
    lower = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in df.columns:
            return c
        if c.lower() in lower:
            return lower[c.lower()]
    return None


def pivot_long_to_table(fin_df: pd.DataFrame, stmt_names: List[str]) -> pd.DataFrame:
    """Pivot long‑format financial data into a wide format table.

    Parameters
    ----------
    fin_df : pd.DataFrame
        Input dataframe with long format data.
    stmt_names : list
        Statement names to filter (e.g., ['INCOME_STATEMENT', 'INCOME STATEMENT']).

    Returns
    -------
    pd.DataFrame
        Pivoted table with line items as rows and years as columns.  If
        required columns are missing an empty DataFrame is returned.
    """
    scol = _pick(fin_df, ["statement", "section", "Statement", "Section"])
    lcol = _pick(fin_df, ["lineitem", "line_item", "line_item_name", "item", "account", "LineItem", "Item"])
    vcol = _pick(fin_df, ["value", "amount", "Value", "Amount"])
    ycol = _pick(fin_df, ["display_year", "year_label", "year", "Year", "display_year"])
    if not (scol and lcol and vcol and ycol):
        return pd.DataFrame()
    # Filter by statement type
    mask = fin_df[scol].astype(str).str.upper().isin([s.upper() for s in stmt_names])
    sub = fin_df[mask].copy()
    if sub.empty:
        return pd.DataFrame()
    # Ensure year column is string for consistent pivot
    sub[ycol] = sub[ycol].astype(str)
    try:
        tab = sub.pivot_table(index=lcol, columns=ycol, values=vcol, aggfunc="sum")
    except Exception:
        return pd.DataFrame()
    # Sort columns by year
    tab = tab.reindex(columns=sort_year_labels(tab.columns))
    tab.index.name = "Line Item"
    return tab