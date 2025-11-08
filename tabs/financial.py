"""Financial tab renderer.

This module defines the layout and behaviour of the Financial tab
within the dashboard.  It exposes a single :func:`render` function
which accepts a dataframe scoped to the selected ticker and draws
four subtabs: Income Statement, Balance Sheet, Cashflow Statement
and Financial Indicators.  Each subtab delegates its rendering
logic to the corresponding module in the ``financial_subtabs``
package.
"""

import streamlit as st

from ..financial_subtabs import (
    income_statement,
    balance_sheet,
    cashflow_statement,
    financial_indicators,
)


def render(fin_df):
    """Render the Financial tab for the current ticker.

    Parameters
    ----------
    fin_df : pandas.DataFrame
        Filtered dataframe containing rows for the selected ticker.
    """
    # Create subtabs only if data is present
    if fin_df is None or fin_df.empty:
        st.info("No financial data available for this ticker.")
        return
    tab_names = [
        "Income Statement", "Balance Sheet", "Cashflow Statement", "Financial Indicators"
    ]
    st_tabs = st.tabs(tab_names)
    # Render each subtab using imported modules
    with st_tabs[0]:
        income_statement.render(fin_df)
    with st_tabs[1]:
        balance_sheet.render(fin_df)
    with st_tabs[2]:
        cashflow_statement.render(fin_df)
    with st_tabs[3]:
        financial_indicators.render(fin_df)