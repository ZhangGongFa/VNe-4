# tabs/financial.py
import streamlit as st
import pandas as pd

from financial_subtabs import (
    income_statement,
    balance_sheet,
    cashflow_statement,
    financial_indicators,
    notes,
)
from utils.ui import inject_global_css

def render(fin_df: pd.DataFrame):
    # Ensure global CSS is applied
    inject_global_css()

    # Top tabs following your visual sample
    tabs = st.tabs([
        "Income statement",
        "Balance Sheet",
        "Cashflow Statement",
        "Financial Indicator",
        "Report",
    ])

    with tabs[0]:
        income_statement.render(fin_df)

    with tabs[1]:
        balance_sheet.render(fin_df)

    with tabs[2]:
        cashflow_statement.render(fin_df)

    with tabs[3]:
        financial_indicators.render(fin_df)  # English only, no icons

    with tabs[4]:
        notes.render(fin_df)
