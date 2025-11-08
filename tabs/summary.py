
import streamlit as st
import pandas as pd

def _pickcol(df, cands):
    lower = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in df.columns: return c
        if c.lower() in lower: return lower[c.lower()]
    return None

def render(fin_df: pd.DataFrame):
    """
    Render a summary view along with several risk ratios computed from the
    available financial columns. If the necessary columns are missing the
    view falls back to displaying whatever core data is available. The
    following risk indicators are calculated when possible:

    - **Debt to Equity**: total liabilities divided by shareholders’ equity
    - **Debt to Assets**: total liabilities divided by total assets
    - **Current Ratio**: current assets divided by current liabilities
    - **Quick Ratio**: (current assets – inventories) divided by current liabilities

    Users can refer to these ratios to gauge leverage and liquidity risk.
    """
    st.header("Summary & Risk Indicators")
    ycol = _pickcol(fin_df, ["display_year", "year"])
    if ycol is None:
        st.info("No year field found.")
        return
    # Work on a copy to avoid SettingWithCopy warnings
    show = fin_df.copy()
    # Basic columns to display if they exist
    basic_cols = []
    for c in ["Net Revenue", "Revenue", "Revenue (Bn. VND)", "Total Assets", "Equity", "OWNER'S EQUITY(Bn.VND)", "LIABILITIES (Bn. VND)", "CURRENT ASSETS (Bn. VND)", "Current liabilities (Bn. VND)", "Inventories, Net (Bn. VND)", "Net Inventories"]:
        if c in show.columns and c not in basic_cols:
            basic_cols.append(c)
    # Compute risk ratios when the necessary columns are present
    # Debt to Equity
    if "LIABILITIES (Bn. VND)" in show.columns:
        liab = show["LIABILITIES (Bn. VND)"].astype(float)
        # pick an equity column
        equity_col = _pickcol(show, ["OWNER'S EQUITY(Bn.VND)", "Equity", "Total Equity"])
        if equity_col:
            eq = show[equity_col].astype(float)
            show["Debt to Equity"] = liab.div(eq.replace(0, pd.NA))
    # Debt to Assets
    if "LIABILITIES (Bn. VND)" in show.columns and "TOTAL ASSETS (Bn. VND)" in show.columns:
        total_assets = show["TOTAL ASSETS (Bn. VND)"].astype(float)
        show["Debt to Assets"] = show["LIABILITIES (Bn. VND)"].astype(float).div(total_assets.replace(0, pd.NA))
    # Current Ratio
    if "CURRENT ASSETS (Bn. VND)" in show.columns:
        ca = show["CURRENT ASSETS (Bn. VND)"].astype(float)
        if "Current liabilities (Bn. VND)" in show.columns:
            cl = show["Current liabilities (Bn. VND)"].astype(float)
            show["Current Ratio"] = ca.div(cl.replace(0, pd.NA))
            # Quick ratio requires inventories
            inv_col = _pickcol(show, ["Inventories, Net (Bn. VND)", "Net Inventories"])
            if inv_col:
                inv = show[inv_col].astype(float)
                show["Quick Ratio"] = ca.sub(inv).div(cl.replace(0, pd.NA))
    # Keep only one equity column in basic view to avoid duplication
    # Determine which equity column to display
    equity_display = _pickcol(show, ["OWNER'S EQUITY(Bn.VND)", "Equity", "Total Equity"])
    if equity_display and equity_display not in basic_cols:
        basic_cols.append(equity_display)
    # Remove duplicates in basic_cols preserving order
    seen = set()
    basic_cols_unique = []
    for c in basic_cols:
        if c not in seen:
            seen.add(c)
            basic_cols_unique.append(c)
    # Compose final dataframe: year column, basic columns, then risk ratios if any
    final_cols = []
    final_cols.extend(basic_cols_unique)
    # Add risk ratio columns if they exist
    for r in ["Debt to Equity", "Debt to Assets", "Current Ratio", "Quick Ratio"]:
        if r in show.columns:
            final_cols.append(r)
    if not final_cols:
        st.info("Provide more financial columns to compute summary and risk metrics.")
        return
    try:
        out = show[[ycol] + final_cols].drop_duplicates(subset=[ycol]).set_index(ycol).sort_index()
    except Exception:
        out = show[[ycol] + final_cols].set_index(ycol)
    # Format ratio columns as percentage or decimal for readability
    def _format_ratios(val):
        if pd.isna(val):
            return "—"
        try:
            return f"{val:.2f}"
        except Exception:
            return val
    # Apply formatting
    for r in ["Debt to Equity", "Debt to Assets", "Current Ratio", "Quick Ratio"]:
        if r in out.columns:
            out[r] = out[r].apply(_format_ratios)
    st.dataframe(out, use_container_width=True)
