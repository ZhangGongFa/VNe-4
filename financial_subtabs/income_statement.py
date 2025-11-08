
import streamlit as st
from utils.transforms import build_display_year_column, pivot_long_to_table

IS_NAMES = ["INCOME_STATEMENT","INCOME STATEMENT","P/L","PROFIT_AND_LOSS","PROFIT OR LOSS"]

def render(fin_df):
    st.subheader("INCOME STATEMENT")
    fin_df = build_display_year_column(fin_df)
    tab = pivot_long_to_table(fin_df, IS_NAMES)
    if tab.empty:
        st.info("No recognizable Income Statement found.")
    else:
        st.dataframe(tab, use_container_width=True)
