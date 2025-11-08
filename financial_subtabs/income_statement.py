"""
Income statement subtab for the Financial section.

This tab pivots long‑format financial statement data into a wide
format income statement table and renders it in a Streamlit data
frame.  It attempts to recognise common names for income statements
in Vietnamese and English.
"""

import streamlit as st

from utils.transforms import build_display_year_column, pivot_long_to_table


# Supported names for income statements (case insensitive)
IS_NAMES = [
    "INCOME_STATEMENT",
    "INCOME STATEMENT",
    "P/L",
    "PROFIT_AND_LOSS",
    "PROFIT OR LOSS",
]


def render(fin_df):
    """Render the income statement tab.

    Parameters
    ----------
    fin_df : pandas.DataFrame
        Filtered dataframe containing rows for the selected ticker.
    """
    st.subheader("INCOME STATEMENT")
    fin_df = build_display_year_column(fin_df)
    tab = pivot_long_to_table(fin_df, IS_NAMES)
    if tab.empty:
        st.info("No recognizable Income Statement found.")
    else:
        st.dataframe(tab, use_container_width=True)