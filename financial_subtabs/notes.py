
import streamlit as st
from utils.transforms import build_display_year_column, pivot_long_to_table

NOTE_NAMES = ["NOTE","NOTES","THUYẾT MINH","THUYET MINH"]

def render(fin_df):
    st.subheader("NOTES")
    fin_df = build_display_year_column(fin_df)
    tab = pivot_long_to_table(fin_df, NOTE_NAMES)
    if tab.empty:
        st.info("Notes section not found.")
    else:
        st.dataframe(tab, use_container_width=True)
