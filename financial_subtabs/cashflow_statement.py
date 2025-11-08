
import streamlit as st
from utils.transforms import build_display_year_column, pivot_long_to_table

CF_NAMES = ["CASHFLOW_STATEMENT","CASH FLOW STATEMENT","CASHFLOW"]

def render(fin_df):
    st.subheader("CASHFLOW STATEMENT")
    fin_df = build_display_year_column(fin_df)
    tab = pivot_long_to_table(fin_df, CF_NAMES)
    if tab.empty:
        st.info("No recognizable Cashflow Statement found.")
    else:
        st.dataframe(tab, use_container_width=True)
