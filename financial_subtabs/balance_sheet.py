"""
Balance sheet subtab for the Financial section.

The balance sheet is divided into assets, liabilities and equity
sections.  Each section is pivoted separately and displayed in its
own table.  Recognises various common Vietnamese and English names.
"""

import streamlit as st

from utils.transforms import pivot_long_to_table


# Statement names for different balance sheet sections
BS_ASSETS = [
    "BALANCE_SHEET (ASSETS)",
    "BALANCE SHEET (ASSETS)",
    "BALANCE_SHEET_ASSETS",
    "ASSETS",
]
BS_LIAB = [
    "BALANCE_SHEET (LIABILITIES)",
    "BALANCE SHEET (LIABILITIES)",
    "BALANCE_SHEET_LIAB",
    "LIABILITIES",
]
BS_EQUITY = [
    "BALANCE_SHEET (EQUITY)",
    "BALANCE SHEET (EQUITY)",
    "BALANCE_SHEET_EQUITY",
    "EQUITY",
]


def render(fin_df):
    """Render the balance sheet tab, split into assets, liabilities and equity."""
    st.subheader("BALANCE SHEET — ASSETS")
    tabA = pivot_long_to_table(fin_df, BS_ASSETS)
    if not tabA.empty:
        st.dataframe(tabA, use_container_width=True)
    else:
        st.info("Assets section not found.")

    st.subheader("BALANCE SHEET — LIABILITIES")
    tabL = pivot_long_to_table(fin_df, BS_LIAB)
    if not tabL.empty:
        st.dataframe(tabL, use_container_width=True)
    else:
        st.info("Liabilities section not found.")

    st.subheader("BALANCE SHEET — EQUITY")
    tabE = pivot_long_to_table(fin_df, BS_EQUITY)
    if not tabE.empty:
        st.dataframe(tabE, use_container_width=True)
    else:
        st.info("Equity section not found.")