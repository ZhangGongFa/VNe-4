"""
Main entry point for the upgraded VNe‑4 Streamlit application.

This module defines a single page Streamlit app which loads
corporate financial data for Vietnamese public companies and
displays three interactive sections:

* **Financial** – income statement, balance sheet, cashflow and key
  indicator subtabs for the selected ticker.
* **Sentiment** – simple sentiment analysis using columns in the
  underlying dataset (e.g. ``Sentiment``, ``Sentiment Change`` and
  ``News Shock``).
* **Summary** – a probability of default (PD) summary driven by a
  LightGBM model trained on historic financial data.  This section
  leverages utility functions from the ``analysis_utils`` package to
  clean, engineer and score data.

The report type selector has been redesigned to use a vertical
layout so that the buttons stack top to bottom rather than left to
right.  This avoids layout issues when the Streamlit sidebar is
collapsed and makes the interface more intuitive on narrow screens.
"""

import os
from typing import List

import pandas as pd
import streamlit as st

from utils.io import read_csv_smart
from utils.transforms import build_display_year_column

from tabs import financial, sentiment, summary


def inject_global_css() -> None:
    """Inject a handful of global CSS rules to adjust spacing and
    component appearance.

    Streamlit provides limited theming out of the box.  These rules
    replicate the look and feel of the original VNe‑4 application and
    ensure that the report selector buttons display vertically.
    """
    st.markdown(
        """
<style>
/* Container padding */
.block-container {
    padding-top: 1.0rem;
    padding-bottom: 2.0rem;
    max-width: 1420px;
}
/* Hide the default Streamlit header */
header {visibility: hidden;}
/* Typography */
h1, h2, h3 { font-weight: 700; letter-spacing: 0.2px; }
h1 { font-size: 30px; margin-bottom: 0.25rem; }
.subtitle { font-size: 14px; color: #6b7280; margin-bottom: 1.2rem; }
/* KPI cards */
.kpi-card { border: 1px solid #E5E7EB; border-radius: 12px; padding: 12px 14px; }
.kpi-title { font-size: 12px; color: #6b7280; margin-bottom: 2px; }
.kpi-value { font-size: 18px; font-weight: 700; }
/* Report button container – force vertical layout */
.report-button-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-top: 10px;
}
</style>
""",
        unsafe_allow_html=True,
    )


def load_data() -> pd.DataFrame:
    """Load the main financial dataset.

    The function attempts to locate ``bctc_final.csv`` in the project
    root or in a ``data/`` subdirectory.  It uses ``read_csv_smart``
    from the ``utils.io`` module to handle different encodings and
    optionally searches the repository for similarly named files.  A
    ``display_year`` column is added for consistency across tabs.  If
    the file cannot be found an empty DataFrame is returned and the
    user will be prompted to upload data at runtime.
    """
    try:
        df = read_csv_smart("bctc_final.csv")
    except Exception:
        df = pd.DataFrame()
    if not df.empty:
        df = build_display_year_column(df)
        # Normalize the ticker column name
        if "Ticker" not in df.columns:
            for c in ["ticker", "Mã CP", "MaCP", "Symbol"]:
                if c in df.columns:
                    df = df.rename(columns={c: "Ticker"})
                    break
        if "Ticker" not in df.columns:
            # create a dummy ticker column so the app does not crash
            df["Ticker"] = "SAMPLE"
    return df


def build_ticker_list(df: pd.DataFrame) -> List[str]:
    """Return a sorted list of unique tickers from a dataframe."""
    if df is None or df.empty or "Ticker" not in df.columns:
        return []
    toks = (
        df["Ticker"]
        .astype(str)
        .str.upper()
        .str.strip()
        .replace({"": None})
        .dropna()
        .unique()
        .tolist()
    )
    toks.sort()
    return toks


def safe_get_value(df: pd.DataFrame, col_patterns: List[str], default: str = "—") -> str:
    """Safely retrieve a single numeric value from a dataframe.

    The first column containing one of the supplied patterns (case
    insensitive) is selected.  The latest non‑null value is
    converted to a human friendly string with one decimal place.  If
    no valid value is found the default is returned.
    """
    for pattern in col_patterns:
        matching_cols = [c for c in df.columns if pattern.lower() in c.lower()]
        if matching_cols:
            vals = df[matching_cols[0]].dropna()
            if not vals.empty:
                try:
                    return f"{float(vals.iloc[-1]):,.1f}"
                except Exception:
                    return str(vals.iloc[-1])
    return default


def main() -> None:
    """Run the Streamlit application."""
    st.set_page_config(page_title="Corporate Financial Dashboard", layout="wide")
    inject_global_css()

    # Page header
    st.markdown("<h1>Corporate Financial Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        '<div class="subtitle">AI‑Driven Corporate Default Risk Prediction System</div>',
        unsafe_allow_html=True,
    )

    # Load data
    df = load_data()

    # If no data found, allow the user to upload
    if df.empty:
        st.info("No data file was found. Please upload your CSV (bctc_final.csv)")
        uploaded = st.file_uploader("Upload bctc_final.csv", type=["csv"])
        if uploaded is not None:
            try:
                df = pd.read_csv(uploaded)
                df = build_display_year_column(df)
                if "Ticker" not in df.columns:
                    for c in ["ticker", "Mã CP", "MaCP", "Symbol"]:
                        if c in df.columns:
                            df = df.rename(columns={c: "Ticker"})
                            break
                    if "Ticker" not in df.columns:
                        df["Ticker"] = "SAMPLE"
                # rerun to refresh state after upload
                st.rerun()
            except Exception:
                st.error("Unable to read the uploaded CSV file.")
                st.stop()

    # Sidebar for ticker selection
    with st.sidebar:
        st.header("Ticker Selection")
        all_tickers = build_ticker_list(df)
        # Preselect ticker from URL query parameter if present
        qs = st.query_params
        url_ticker = (qs.get("ticker", "") or "").upper()
        default_index = 0
        if url_ticker and url_ticker in all_tickers:
            default_index = all_tickers.index(url_ticker)
        selected_ticker = st.selectbox(
            "Select ticker",
            options=all_tickers if all_tickers else [],
            index=default_index if all_tickers else None,
            placeholder="Select a ticker...",
        )

    # Report type selector – vertical layout
    st.markdown("---")
    st.header("Report Type")
    # Initialize session state for report selection
    if "report_tab" not in st.session_state:
        st.session_state.report_tab = "Financial"
    st.markdown('<div class="report-button-container">', unsafe_allow_html=True)
    # Define a simple helper to create buttons vertically
    for label in ["Financial", "Sentiment", "Summary"]:
        if st.button(
            f" {label}",
            key=f"btn_{label.lower()}",
            use_container_width=True,
            type="primary" if st.session_state.report_tab == label else "secondary",
        ):
            st.session_state.report_tab = label
    st.markdown("</div>", unsafe_allow_html=True)

    # Display description based on the selected tab
    st.markdown("---")
    descriptions = {
        "Financial": " **Financial Analysis**\n\nView income statements, balance sheets, cash flow statements, and key financial indicators.",
        "Sentiment": " **Sentiment Analysis**\n\nAnalyze news sentiment and market perception related to the selected stock.",
        "Summary": " **Risk Summary**\n\nView comprehensive risk indicators and default probability metrics.",
    }
    st.info(descriptions.get(st.session_state.report_tab, ""))

    # Keep the query parameter in sync with the ticker
    if selected_ticker:
        st.query_params.ticker = selected_ticker

    # Guard if no ticker yet
    if not selected_ticker:
        st.warning("⚠️ Please select a ticker from the sidebar to continue.")
        st.stop()

    # Filter data to the selected ticker and up to the 10 most recent years
    scoped = df[df["Ticker"].astype(str).str.upper() == selected_ticker].copy()
    if "display_year" in scoped.columns:
        recent_years = scoped["display_year"].astype(str).dropna().unique().tolist()
        try:
            recent_years = sorted(recent_years, key=lambda x: (len(x), x))[-10:]
        except Exception:
            recent_years = recent_years[-10:]
        scoped = scoped[scoped["display_year"].astype(str).isin(recent_years)]

    # KPI row using real data
    col1, col2, col3 = st.columns(3)
    with col1:
        net_rev = safe_get_value(scoped, ["net revenue", "revenue", "doanh thu"])
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Net Revenue (Latest)</div><div class="kpi-value">{net_rev}</div></div>',
            unsafe_allow_html=True,
        )
    with col2:
        gross_margin = safe_get_value(scoped, ["gross margin", "gross profit margin"])
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">Gross Margin</div><div class="kpi-value">{gross_margin}</div></div>',
            unsafe_allow_html=True,
        )
    with col3:
        roe = safe_get_value(scoped, ["roe", "return on equity"])
        st.markdown(
            f'<div class="kpi-card"><div class="kpi-title">ROE</div><div class="kpi-value">{roe}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # Render the appropriate tab content
    try:
        if st.session_state.report_tab == "Financial":
            financial.render(scoped)
        elif st.session_state.report_tab == "Sentiment":
            sentiment.render(scoped)
        elif st.session_state.report_tab == "Summary":
            summary.render(scoped)
    except Exception as e:
        st.error(f"Error rendering {st.session_state.report_tab} tab: {str(e)}")
        st.exception(e)


if __name__ == "__main__":
    main()