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

# Additional CSS to beautify the report selector in the sidebar. This CSS is
# injected separately from the global styling to ensure it is applied on top
# of the base styles. Each radio option becomes a full‑width pill button
# with a dark highlight when selected.
st.markdown(
    """
    <style>
        [data-testid="stSidebar"] .stRadio > div { flex-direction: column; }
        [data-testid="stSidebar"] .stRadio label {
            display: block;
            background: #F3F4F6;
            padding: 10px 14px;
            border-radius: 8px;
            margin-bottom: 6px;
            cursor: pointer;
            font-weight: 600;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background: #E5E7EB;
        }
        [data-testid="stSidebar"] .stRadio label input[type="radio"] {
            display: none;
        }
        [data-testid="stSidebar"] .stRadio label[aria-checked="true"] {
            background: #1F2937;
            color: white;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


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

# ========== KPI row ==========
# Dynamically compute and display a few key indicators based on the most
# recent year for the selected ticker. The helpers below gracefully
# handle missing columns.
def _get_col(row, candidates):
    """Return the first available column value from candidates or None."""
    for c in candidates:
        if c in row and pd.notnull(row[c]):
            return row[c]
    return None

# Determine the most recent record by display_year (string or numeric)
recent_row = None
if not scoped.empty:
    try:
        # Convert display_year to sort properly if it exists
        if "display_year" in scoped.columns:
            tmp = scoped.copy().dropna(subset=["display_year"])
            # sort by length then value to handle FY2017 vs 2017 etc.
            tmp = tmp.sort_values(by="display_year", key=lambda x: x.astype(str).map(lambda v: (len(v), v)))
            recent_row = tmp.iloc[-1]
        else:
            recent_row = scoped.iloc[-1]
    except Exception:
        recent_row = scoped.iloc[-1]

net_rev_val = gross_margin_val = roe_val = None
if recent_row is not None:
    # Net revenue: try a list of possible column names
    net_rev = _get_col(recent_row, ["Net Revenue", "Revenue (Bn. VND)", "Revenue", "Net Sales"])
    gross_profit = _get_col(recent_row, ["Gross Profit"])
    if isinstance(net_rev, (int, float)) and net_rev != 0 and isinstance(gross_profit, (int, float)):
        gross_margin_val = gross_profit / net_rev
    net_profit = _get_col(recent_row, ["Net Profit For the Year", "Profit before tax", "Operating Profit/Loss"])
    equity = _get_col(recent_row, ["OWNER'S EQUITY(Bn.VND)", "Equity", "Total Equity"])
    if isinstance(net_profit, (int, float)) and isinstance(equity, (int, float)) and equity != 0:
        roe_val = net_profit / equity
    net_rev_val = net_rev

# Display KPI cards
col1, col2, col3 = st.columns(3)
def _fmt_val(val, pct=False):
    if val is None or pd.isna(val):
        return "—"
    try:
        if pct:
            return f"{val*100:.1f}%"
        return f"{float(val):,.1f}"
    except Exception:
        return "—"

with col1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Revenue (last)</div><div class="kpi-value">{_fmt_val(net_rev_val)}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Gross Margin</div><div class="kpi-value">{_fmt_val(gross_margin_val, pct=True)}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">ROE</div><div class="kpi-value">{_fmt_val(roe_val, pct=True)}</div></div>', unsafe_allow_html=True)

# ========== Report content ==========
# Based on the selected report type from the sidebar, render the appropriate
# module. Financial view displays the full set of financial statements and
# indicators via its own sub‑tabs. Sentiment and Summary provide compact
# views.
if report_tab == "Financial":
    try:
        financial.render(scoped)
    except Exception as e:
        st.warning(f"Financial view is not available. Detail: {e}")
elif report_tab == "Sentiment":
    try:
        sentiment.render(scoped)
    except Exception as e:
        st.warning(f"Sentiment view is not available. Detail: {e}")
elif report_tab == "Summary":
    try:
        summary.render(scoped)
    except Exception as e:
        st.warning(f"Summary view is not available. Detail: {e}")
