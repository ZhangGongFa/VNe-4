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
            
            /* Report buttons styling */
            .report-button-container {
                display: flex;
                flex-direction: column;
                gap: 10px;
                margin-top: 10px;
            }
            .report-btn {
                width: 100%;
                padding: 12px 16px;
                border: 2px solid #E5E7EB;
                border-radius: 10px;
                background: white;
                cursor: pointer;
                text-align: left;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.2s;
            }
            .report-btn:hover {
                border-color: #0A66C2;
                background: #F0F7FF;
            }
            .report-btn.active {
                border-color: #0A66C2;
                background: #0A66C2;
                color: white;
            }
            .report-btn-title {
                font-size: 15px;
                font-weight: 700;
                margin-bottom: 4px;
            }
            .report-btn-desc {
                font-size: 12px;
                color: #6b7280;
            }
            .report-btn.active .report-btn-desc {
                color: rgba(255,255,255,0.8);
            }
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


# =========================================
# App header
# =========================================
st.markdown("<h1>Corporate Financial Dashboard</h1>", unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-Driven Corporate Default Risk Prediction System</div>', unsafe_allow_html=True)


# =========================================
# Main
# =========================================
df = load_data()

# If no data found, allow upload so the app never crashes
if df.empty:
    st.info("No data file was found. Please upload your CSV (bctc_final.csv)")
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
        st.rerun()

# Sidebar (premium style)
with st.sidebar:
    st.header("Ticker Selection")

    # Build the full ticker list from your data
    all_tickers = build_ticker_list(df)

    # Optional: read ?ticker=HPG from URL to preselect
    qs = st.query_params
    url_ticker = (qs.get("ticker", "") or "").upper()

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
    st.header("Report Type")
    
    # Initialize session state for report selection
    if 'report_tab' not in st.session_state:
        st.session_state.report_tab = "Financial"
    
    # Custom button styling for report selection
    st.markdown('<div class="report-button-container">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Financial", key="btn_financial", use_container_width=True,
                     type="primary" if st.session_state.report_tab == "Financial" else "secondary"):
            st.session_state.report_tab = "Financial"
    
    with col2:
        if st.button("📰 Sentiment", key="btn_sentiment", use_container_width=True,
                     type="primary" if st.session_state.report_tab == "Sentiment" else "secondary"):
            st.session_state.report_tab = "Sentiment"
    
    with col3:
        if st.button("📈 Summary", key="btn_summary", use_container_width=True,
                     type="primary" if st.session_state.report_tab == "Summary" else "secondary"):
            st.session_state.report_tab = "Summary"
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display description based on selection
    st.markdown("---")
    descriptions = {
        "Financial": "📊 **Financial Analysis**\n\nView income statements, balance sheets, cash flow statements, and key financial indicators.",
        "Sentiment": "📰 **Sentiment Analysis**\n\nAnalyze news sentiment and market perception related to the selected stock.",
        "Summary": "📈 **Risk Summary**\n\nView comprehensive risk indicators and default probability metrics."
    }
    st.info(descriptions[st.session_state.report_tab])

# Keep URL in sync
if selected_ticker:
    st.query_params.ticker = selected_ticker

# Guard if no ticker yet
if not selected_ticker:
    st.warning("⚠️ Please select a ticker from the sidebar to continue.")
    st.stop()

# Scope data to ticker and 10 most recent years (by display_year)
scoped = df[df["Ticker"].astype(str).str.upper() == selected_ticker].copy()
if "display_year" in scoped.columns:
    recent10 = (
        scoped["display_year"].astype(str).dropna().unique().tolist()
    )
    # Sort year labels
    try:
        recent10 = sorted(recent10, key=lambda x: (len(x), x))[-10:]
    except Exception:
        recent10 = recent10[-10:]
    scoped = scoped[scoped["display_year"].astype(str).isin(recent10)]

# KPI row with real data
col1, col2, col3 = st.columns(3)

def safe_get_value(df, col_patterns, default="—"):
    """Safely get value from dataframe with multiple possible column names"""
    for pattern in col_patterns:
        matching_cols = [c for c in df.columns if pattern.lower() in c.lower()]
        if matching_cols:
            vals = df[matching_cols[0]].dropna()
            if not vals.empty:
                try:
                    return f"{float(vals.iloc[-1]):,.1f}"
                except:
                    return str(vals.iloc[-1])
    return default

with col1:
    net_rev = safe_get_value(scoped, ["net revenue", "revenue", "doanh thu"])
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Net Revenue (Latest)</div><div class="kpi-value">{net_rev}</div></div>', unsafe_allow_html=True)

with col2:
    gross_margin = safe_get_value(scoped, ["gross margin", "gross profit margin"])
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">Gross Margin</div><div class="kpi-value">{gross_margin}</div></div>', unsafe_allow_html=True)

with col3:
    roe = safe_get_value(scoped, ["roe", "return on equity"])
    st.markdown(f'<div class="kpi-card"><div class="kpi-title">ROE</div><div class="kpi-value">{roe}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Render based on selected report type
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
