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

def sort_year_labels(labels):
    """
    Sort a list or index of year labels chronologically.
    Handles formats like: '2024', '2024F', '2023', etc.
    """
    return sorted(labels, key=sort_year_label)

def pivot_long_to_table(fin_df: pd.DataFrame, stmt_names):
    """
    Pivot long-format financial data into wide format table.
    
    Parameters:
    -----------
    fin_df : pd.DataFrame
        Input dataframe with long format data
    stmt_names : list
        List of statement names to filter (e.g., ['INCOME_STATEMENT', 'INCOME STATEMENT'])
    
    Returns:
    --------
    pd.DataFrame
        Pivoted table with line items as rows and years as columns
    """
    scol = _pick(fin_df, ["statement","section","Statement","Section"])
    lcol = _pick(fin_df, ["lineitem","line_item","line_item_name","item","account","LineItem","Item"])
    vcol = _pick(fin_df, ["value","amount","Value","Amount"])
    ycol = _pick(fin_df, ["display_year","year_label","year","Year","display_year"])
    
    if not (scol and lcol and vcol and ycol):
        return pd.DataFrame()

    # Filter by statement type
    mask = fin_df[scol].astype(str).str.upper().isin([s.upper() for s in stmt_names])
    sub = fin_df[mask].copy()
    
    if sub.empty: 
        return pd.DataFrame()
    
    # Ensure year column is string
    sub[ycol] = sub[ycol].astype(str)
    
    # Pivot the table
    try:
        tab = sub.pivot_table(index=lcol, columns=ycol, values=vcol, aggfunc="sum")
    except Exception as e:
        return pd.DataFrame()
    
    # Sort columns by year
    tab = tab.reindex(columns=sort_year_labels(tab.columns))
    
    # Clean up index name
    tab.index.name = "Line Item"
    
    return tab

def _pick(df, cands):
    """
    Pick first matching column from candidates list.
    Case-insensitive matching.
    """
    lower = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in df.columns: 
            return c
        if c.lower() in lower: 
            return lower[c.lower()]
    return None
