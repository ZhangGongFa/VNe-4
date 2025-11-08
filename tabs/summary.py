
import streamlit as st
import pandas as pd

def _pickcol(df, cands):
    lower = {c.lower(): c for c in df.columns}
    for c in cands:
        if c in df.columns: return c
        if c.lower() in lower: return lower[c.lower()]
    return None

def render(fin_df: pd.DataFrame):
    st.header("Summary")
    ycol = _pickcol(fin_df, ["display_year","year"])
    if ycol is None:
        st.info("No year field found."); return
    show = fin_df.drop_duplicates(subset=[ycol]).copy()
    cols = []
    for c in ["Net Revenue","Revenue","Total Assets","Equity","Total Debt","Short-Term Loans","Long-Term Loans"]:
        if c in show.columns: cols.append(c)
    if not cols:
        st.info("Provide core columns to see summary (Revenue, Total Assets, Equity, Debt...)."); return
    st.dataframe(show[[ycol]+cols].set_index(ycol).sort_index(), use_container_width=True)
