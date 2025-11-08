# app.py
# Premium Streamlit App (English-only, no icons)

import os
import pandas as pd
import streamlit as st

# ---- Your internal modules (already in the repo) ----
from utils.io import read_csv_smart
from utils.transforms import build_display_year_column
from tabs import financial, sentiment, summary


# =========================================
# Global page config & CSS
# =========================================
st.set_page_config(page_title="Corporate Financial Dashboard", layout="wide")

def inject_global_css():
    st.markdown(
        """
        <style>
            /* Layout & spacing */
            .block-container {padding-top: 1.0rem; padding-bottom: 2.0rem; max-width: 1420px;}
            header {visibility: hidden;} /* hide default st header */

            /* Typography */
            h1, h2, h3 { font-weight: 700; letter-spacing: 0.2px; }
            h1 { font-size: 30px; margin-bottom: 0.25rem; }
            .subtitle { font-size: 14px; color: #6b7280; margin-bottom: 1.2rem; }

            /* Cards */
            .kpi-card { border: 1px solid #E5E7EB; border-radius: 12px; padding: 12px 14px; }
            .kpi-title { font-size: 12px; color: #6b7280; margin-bottom: 2px; }
            .kpi-value { font-size: 18px; font-weight: 700; }

            /* Tabs look */
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] { height: 36px; background: #F3F4F6; border-radius: 999px; padding: 0 14px; }
            .stTabs [aria-selected="true"] { background: #1F2937 !important; color: #fff !important; }

            /* Sidebar labels */
            [data-testid="stSidebar"] h2, [data-testid="stSidebar"] label { font-weight: 600; }

            /* Dataframe header contrast */
            .stDataFrame thead tr th { background: #f9fafb; }
        </style>
        """,
        unsafe_allow_html=True,
    )

inject_global_css()


# =========================================
# Data loader (resilient)
# =========================================
@st.cache_data(show_spinner=False)
def load_data():
    """
    Try to read ./data/bctc_final.csv (via your util).
    If missing: return empty df; the app will ask for upload.
    """
    try:
        df = read_csv_smart()
    except Exception:
        df = pd.DataFrame()
    if not df.empty:
        df = build_display_year_column(df)
        # Normalize Ticker if necessary
        if "Ticker" not in df.columns:
            for c in ["ticker", "Mã CP", "MaCP", "Symbol"]:
                if c in df.columns:
                    df = df.rename(columns={c: "Ticker"})
                    break
            if "Ticker" not in df.columns:
                df["Ticker"] = "SAMPLE"
    return df


def build_ticker_list(df: pd.DataFrame):
    if df is None or df.empty:
        return []
    if "Ticker" not in df.columns:
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


def filter_options(options, query):
    if not query:
        return options[:300]
    query = query.upper()
    prefix = [x for x in options if x.startswith(query)]
    if prefix:
        return prefix[:300]
    return [x for x in options if query in x][:300]


# =========================================
# App header
# =========================================
st.markdown("<h1>Corporate Financial Dashboard</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">Clean presentation for income statement, balance sheet, cashflow, indicators, and notes.</div>', unsafe_allow_html=True)


# =========================================
# Main
# =========================================
df = load_data()

# If no data found, allow upload so the app never crashes
if df.empty:
    st.info("No data file was found. Please upload your CSV (same schema as your working file).")
    upl = st.file_uploader("Upload bctc_final.csv", type=["csv"])
    if upl is not None:
        df = pd.read_csv(upl)
        df = build_display_year_column(df)
        if "Ticker" not in df.columns:
            for c in ["ticker", "Mã CP", "MaCP", "Symbol"]:
                if c in df.columns:
                    df = df.rename(columns={c: "Ticker"})
                    break
            if "Ticker" not in df.columns:
                df["Ticker"] = "SAMPLE"

# Sidebar (premium style)
with st.sidebar:
    st.header("Ticker")

    # Build the full ticker list from your data
    all_tickers = build_ticker_list(df)  # e.g., ["HPG","VNM","FPT",...]

    # Optional: read ?ticker=HPG from URL to preselect
    qs = st.experimental_get_query_params()
    url_ticker = (qs.get("ticker", [""])[0] or "").upper()

    # Decide default index
    default_index = 0
    if url_ticker and url_ticker in all_tickers:
        default_index = all_tickers.index(url_ticker)

    # Single dropdown (Streamlit selectbox supports type-to-search)
    selected_ticker = st.selectbox(
        "Select ticker",
        options=all_tickers if all_tickers else [],
        index=default_index if all_tickers else None,
        placeholder="Select a ticker...",
    )

    st.markdown("---")
    st.header("Report")
    report_tab = st.radio(
        "Report",
        options=["Financial", "Sentiment", "Summary"],
        index=0,
        label_visibility="collapsed",
    )

# Keep URL in sync
if selected_ticker:
    st.experimental_set_query_params(ticker=selected_ticker)

# Guard if no ticker yet
if not selected_ticker:
    st.stop()

# Scope data to ticker and 10 most recent years (by display_year)
scoped = df[df["Ticker"].astype(str).str.upper() == selected_ticker].copy()
if "display_year" in scoped.columns:
    recent10 = (
        scoped["display_year"].astype(str).dropna().unique().tolist()
    )
    # Sort year labels with your util (already embedded in build_display_year_column)
    try:
        # ensure chronological, then take last 10
        recent10 = sorted(recent10, key=lambda x: (len(x), x))[-10:]
    except Exception:
        recent10 = recent10[-10:]
    scoped = scoped[scoped["display_year"].astype(str).isin(recent10)]

# KPI row (simple, safe even with partial data)
col1, col2, col3 = st.columns(3)
def _fmt(v):
    try:
        return f"{float(v):,.1f}"
    except Exception:
        return "—"

with col1:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Net Revenue (last)</div><div class="kpi-value">—</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="kpi-card"><div class="kpi-title">Gross Margin</div><div class="kpi-value">—</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="kpi-card"><div class="kpi-title">ROE</div><div class="kpi-value">—</div></div>', unsafe_allow_html=True)

# Top-level tabs (English labels only)
tabs = st.tabs(["Income statement", "Balance Sheet", "Cashflow Statement", "Financial Indicator", "Report"])

with tabs[0]:
    try:
        financial.render(scoped)  # your module will open sub-tabs and render income statement etc.
    except Exception as e:
        st.warning(f"Income statement view is not available. Detail: {e}")

with tabs[1]:
    try:
        # financial.render already includes sub-tabs for Balance Sheet; but if you separated, call dedicated renderer.
        # To avoid double work, keep a simple note here:
        st.caption("Open the Financial tab for Balance Sheet sub-tab if you combined them there.")
    except Exception as e:
        st.warning(f"Balance Sheet view is not available. Detail: {e}")

with tabs[2]:
    try:
        st.caption("Open the Financial tab for Cashflow sub-tab if you combined them there.")
    except Exception as e:
        st.warning(f"Cashflow view is not available. Detail: {e}")

with tabs[3]:
    try:
        # If you wrote a dedicated subtab module for indicators, it is called inside financial.render.
        # Here we only provide a placeholder if you want a flat view:
        st.caption("Financial indicators are available in the Financial tab > Financial Indicator.")
    except Exception as e:
        st.warning(f"Financial Indicator view is not available. Detail: {e}")

with tabs[4]:
    try:
        # Notes/report; keep graceful if missing
        if "notes" in scoped.columns and not scoped["notes"].dropna().empty:
            st.subheader("Notes")
            st.dataframe(scoped[["display_year", "notes"]].rename(columns={"display_year": "Year", "notes": "Notes"}), use_container_width=True)
        else:
            st.info("Notes section not found.")
    except Exception as e:
        st.warning(f"Report view is not available. Detail: {e}")
