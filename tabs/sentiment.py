
import streamlit as st
import pandas as pd

def render(fin_df: pd.DataFrame):
    st.header("Sentiment")
    cand = [c for c in fin_df.columns if any(k in c.lower() for k in ["sentiment","tone","news","score"])]
    if not cand:
        st.info("No sentiment columns found in CSV.")
        return
    view = fin_df[["display_year"] + cand].drop_duplicates().set_index("display_year").sort_index()
    st.dataframe(view, use_container_width=True)
