import os
import json
import warnings
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==== Utils từ dự án gốc ====
from utils_new.data_cleaning import clean_and_log_transform
from utils_new.feature_engineering import preprocess_and_create_features
from utils_new.feature_selection import select_features_for_model
from utils_new.model_scoring import load_lgbm_model, model_feature_names, explain_shap
from utils_new.policy import load_thresholds, thresholds_for_sector, classify_pd

# ==== Import các tab chức năng ====
from tabs import financial, sentiment, summary

warnings.filterwarnings("ignore", category=UserWarning)

# ---------- Page config & styles ----------
st.set_page_config(page_title="Corporate Default Risk Scoring", layout="wide")

def inject_global_css():
    """Inject CSS styling for the application"""
    st.markdown("""
    <style>
    .block-container {padding-top: 0.8rem; padding-bottom: 1.2rem; max-width: 1420px;}
    h1,h2,h3 {font-weight: 650;}
    .small {font-size:12px; color:#6b7280;}
    .metric-card {background:#F8FAFC;border:1px solid #E5E7EB;border-radius:10px;padding:10px 12px;margin-bottom:8px;}
    hr {margin: 0.6rem 0;}
    
    /* Tab navigation styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] { height: 36px; background: #F3F4F6; border-radius: 999px; padding: 0 14px; }
    .stTabs [aria-selected="true"] { background: #1F2937 !important; color: #fff !important; }
    
    /* Report buttons styling */
    .report-button-container {
        display: flex;
        flex-direction: row;
        gap: 10px;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .report-btn {
        flex: 1;
        padding: 12px 16px;
        border: 2px solid #E5E7EB;
        border-radius: 10px;
        background: white;
        cursor: pointer;
        text-align: center;
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
    </style>
    """, unsafe_allow_html=True)

inject_global_css()

# ---------- Small helpers ----------
ID_LABEL_COLS = {"Year","Ticker","Sector","Exchange","Default"}

def read_csv_smart(path: str) -> pd.DataFrame:
    """Read CSV with multiple encoding attempts"""
    for enc in ("utf-8-sig", "utf-8", "latin1"):
        try:
            df = pd.read_csv(path, encoding=enc)
            if df.shape[1] == 0:
                raise ValueError("CSV has no columns (empty or bad delimiter).")
            return df
        except Exception:
            continue
    raise RuntimeError(f"Unable to read {path} with common encodings.")

def to_float(x):
    """Convert value to float safely"""
    try:
        if pd.isna(x): return np.nan
        if isinstance(x, str): x = x.replace(",", "")
        return float(x)
    except Exception:
        return np.nan

def fmt_money(x):
    """Format number as currency"""
    return "-" if (x is None or not np.isfinite(x)) else f"{x:,.2f}"

def fmt_ratio(x):
    """Format number as ratio/percentage"""
    if (x is None) or (not np.isfinite(x)): return "-"
    return f"{x:.2%}" if -1.5 <= float(x) <= 1.5 else f"{x:,.4f}"

def safe_df(X: pd.DataFrame) -> pd.DataFrame:
    """Replace inf values with NaN and fill with 0"""
    return X.replace([np.inf, -np.inf], np.nan).fillna(0.0)

def force_numeric(X: pd.DataFrame) -> pd.DataFrame:
    """Convert all columns to numeric"""
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    return safe_df(X)

def safe_div(a, b):
    """Safe division"""
    try:
        return (float(a) / float(b)) if (b not in [0, None, np.nan] and float(b)!=0.0) else np.nan
    except Exception:
        return np.nan

def bucketize_sector(sector_raw: str) -> str:
    """Categorize sector into standard buckets"""
    s = (sector_raw or "").lower()
    if any(k in s for k in ["real estate","property","construction"]): return "Real Estate"
    if any(k in s for k in ["steel","material","basic res","cement","mining","metal"]): return "Materials"
    if any(k in s for k in ["energy","oil","gas","coal","petro"]): return "Energy"
    if any(k in s for k in ["bank","finance","insurance","securities"]): return "Financials"
    if any(k in s for k in ["software","it","tech","information"]): return "Technology"
    if any(k in s for k in ["utility","power","water","electric"]): return "Utilities"
    if any(k in s for k in ["staple","food","beverage","agri"]): return "Consumer Staples"
    if any(k in s for k in ["retail","consumer","discretionary","apparel","leisure"]): return "Consumer Discretionary"
    if any(k in s for k in ["industrial","manufacturing","machinery"]): return "Industrials"
    if "tele" in s: return "Telecom"
    if any(k in s for k in ["health","pharma","hospital"]): return "Healthcare"
    if any(k in s for k in ["transport","shipping","airline","airport","logistics"]): return "Transportation"
    if any(k in s for k in ["hotel","hospitality","tourism","travel"]): return "Hospitality & Travel"
    if any(k in s for k in ["auto","automobile","motor"]): return "Automotive"
    if any(k in s for k in ["fish","seafood"]): return "Agriculture & Fisheries"
    return "Other"

# Market microstructure risk weight
EXCHANGE_INTENSITY = {"UPCOM": 1.25, "HNX": 1.10, "HOSE": 1.00, "HSX": 1.00}

# ---------- Load data & model ----------
@st.cache_data(show_spinner=False)
def load_raw_and_features():
    """Load and process raw data with features"""
    if not os.path.exists("bctc_final.csv"):
        raise FileNotFoundError("bctc_final.csv not found in repository root.")
    raw = read_csv_smart("bctc_final.csv")
    cleaned = clean_and_log_transform(raw.copy())
    feats = preprocess_and_create_features(cleaned)
    return raw, feats

@st.cache_resource(show_spinner=False)
def load_artifacts():
    """Load model and thresholds"""
    model = load_lgbm_model("models/lgbm_model.pkl")
    thresholds = load_thresholds("models/threshold.json")
    return model, thresholds

# ---------- Header ----------
st.title("Corporate Default Risk Scoring")

# ---------- Data init ----------
try:
    raw_df, feats_df = load_raw_and_features()
except Exception as e:
    st.error(f"Dataset error: {e}")
    st.stop()

try:
    model, thresholds = load_artifacts()
except Exception as e:
    st.error(f"Artifacts error: {e}")
    st.stop()

numeric_cols = [c for c in feats_df.columns if pd.api.types.is_numeric_dtype(feats_df[c])]
candidate_features = [c for c in numeric_cols if c not in ID_LABEL_COLS]
model_feats = model_feature_names(model)
final_features = select_features_for_model(feats_df, candidate_features, model_feats)

# ---------- Sidebar ----------
with st.sidebar:
    # --- Language selection ---
    st.header("Ngôn ngữ / Language")
    # Provide language options. The first entry is Vietnamese, second English.
    lang_option = st.selectbox(
        "Chọn ngôn ngữ / Select language",
        options=["Tiếng Việt", "English"],
        index=0,
        key="sb_language"
    )
    # Map display language to internal code
    lang_code = 'vi' if lang_option == "Tiếng Việt" else 'en'
    # Persist selected language in session state for access across components
    st.session_state['lang'] = lang_code

    st.markdown("---")
    # --- Ticker and year selection ---
    # Display header according to language
    st.header("Lựa chọn Ticker" if lang_code == 'vi' else "Select Ticker")

    tickers = sorted(feats_df["Ticker"].astype(str).unique().tolist())
    ticker_label = "Chọn mã cổ phiếu" if lang_code == 'vi' else "Choose ticker"
    ticker = st.selectbox(ticker_label, tickers, index=0 if tickers else None, key="sb_ticker")

    # Build list of available years for the selected ticker
    years_avail = sorted(
        feats_df.loc[feats_df["Ticker"].astype(str) == ticker, "Year"].dropna().astype(int).unique().tolist()
    )
    year_idx = len(years_avail) - 1 if years_avail else 0
    year_label = "Chọn năm" if lang_code == 'vi' else "Choose year"
    year = st.selectbox(year_label, years_avail, index=year_idx, key=f"sb_year_{ticker}")

    st.markdown("---")
    # --- Report tab selection ---
    report_header = "Loại Báo Cáo" if lang_code == 'vi' else "Report Type"
    st.header(report_header)

    # Initialize session state for report selection if not set
    if 'report_tab' not in st.session_state:
        st.session_state.report_tab = "Summary"

    # Determine button labels based on language
    finance_label   = "📊 Tài chính" if lang_code == 'vi' else "📊 Finance"
    sentiment_label = "📰 Tình cảm" if lang_code == 'vi' else "📰 Sentiment"
    summary_label   = "📈 Tóm tắt" if lang_code == 'vi' else "📈 Summary"

    # Create button columns for report selection
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(finance_label, key="btn_financial", use_container_width=True):
            st.session_state.report_tab = "Finance"

    with col2:
        if st.button(sentiment_label, key="btn_sentiment", use_container_width=True):
            st.session_state.report_tab = "Sentiment"

    with col3:
        if st.button(summary_label, key="btn_summary", use_container_width=True):
            st.session_state.report_tab = "Summary"

    st.markdown("---")

    # Display description based on selected tab and language
    if lang_code == 'vi':
        descriptions = {
            "Finance": "📊 **Phân Tích Tài Chính**\n\nXem báo cáo thu nhập, bảng cân đối kế toán, báo cáo lưu chuyển tiền mặt và các chỉ số tài chính chính.",
            "Sentiment": "📰 **Phân Tích Tình Cảm**\n\nPhân tích tình cảm tin tức và nhận thức thị trường liên quan đến cổ phiếu đã chọn.",
            "Summary": "📈 **Tóm Tắt Rủi Ro**\n\nXem các chỉ số rủi ro toàn diện và số liệu xác suất vỡ nợ."
        }
    else:
        descriptions = {
            "Finance": "📊 **Financial Analysis**\n\nView the income statement, balance sheet, cash flow statement and key financial ratios.",
            "Sentiment": "📰 **Sentiment Analysis**\n\nAnalyze news sentiment and market perception related to the selected stock.",
            "Summary": "📈 **Summary & Risk Overview**\n\nView comprehensive risk metrics and default probability measurements."
        }

    if st.session_state.report_tab in descriptions:
        st.info(descriptions[st.session_state.report_tab])

# ---------- Get selected data ----------
row_model = feats_df[(feats_df["Ticker"].astype(str)==ticker) & (feats_df["Year"]==year)]
if row_model.empty:
    st.warning("Không có dữ liệu cho Ticker & Năm đã chọn.")
    st.stop()
row_model = row_model.iloc[0]

row_raw = raw_df[(raw_df["Ticker"].astype(str)==ticker) & (raw_df["Year"]==year)]
row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype="object")

sector_raw = str(row_model.get("Sector","")) if pd.notna(row_model.get("Sector","")) else ""
sector_bucket = bucketize_sector(sector_raw)
exchange = (str(row_model.get("Exchange","")) or "").upper()

def get_raw(col_names, default=np.nan):
    """Get raw value from row"""
    for c in col_names:
        if c in row_raw.index:
            return to_float(row_raw[c])
    return default

# Extract financial metrics
assets_raw = get_raw(["TOTAL ASSETS (Bn. VND)","Total_Assets"])
equity_raw = get_raw(["OWNER'S EQUITY(Bn.VND)","Equity"])
curr_liab = get_raw(["Current liabilities (Bn. VND)","Current_Liabilities"], 0.0)
long_liab = get_raw(["Long-term liabilities (Bn. VND)","Long_Term_Liabilities"], 0.0)
short_bor = get_raw(["Short-term borrowings (Bn. VND)","Short_Term_Borrowings"], 0.0)

revenue_raw = get_raw(["Net Sales","Revenue"])
net_profit_raw = get_raw(["Net Profit For the Year","Net_Profit"])
oper_profit_raw = get_raw(["Operating Profit/Loss","Operating_Profit"])
interest_exp_raw = get_raw(["Interest Expenses","Interest_Expenses"], 0.0)
cash_raw = get_raw(["Cash and cash equivalents (Bn. VND)","Cash"], 0.0)
receivables_raw = get_raw(["Accounts receivable (Bn. VND)","Receivables"], 0.0)
inventories_raw = get_raw(["Net Inventories","Inventories"], 0.0)
current_assets_raw = get_raw(["CURRENT ASSETS (Bn. VND)","Current_Assets"], 0.0)

total_liab_raw = (curr_liab or 0.0) + (long_liab or 0.0)
interest_bearing_debt = (short_bor or 0.0) + (long_liab or 0.0)
debt_raw = to_float(row_raw.get("Total_Debt")) if ("Total_Debt" in row_raw.index and pd.notna(row_raw.get("Total_Debt"))) else interest_bearing_debt

roa = safe_div(net_profit_raw, assets_raw)
roe = safe_div(net_profit_raw, equity_raw)
dta = safe_div(total_liab_raw, assets_raw); dta = min(max(dta, 0.0), 0.999) if pd.notna(dta) else np.nan
dte = safe_div(debt_raw, equity_raw); dte = min(max(dte, 0.0), 0.999) if pd.notna(dte) else np.nan
current_ratio = safe_div(current_assets_raw, curr_liab)
quick_ratio = safe_div((cash_raw or 0.0) + (receivables_raw or 0.0), curr_liab)

# ---------- Display KPI cards ----------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("ROA", fmt_ratio(roa))

with col2:
    st.metric("ROE", fmt_ratio(roe))

with col3:
    st.metric("Debt-to-Assets", fmt_ratio(dta))

st.markdown("---")

# ---------- Render based on selected report type ----------
try:
    # Pass language code from session state to each tab renderer
    lang_code = st.session_state.get('lang', 'vi')
    if st.session_state.report_tab == "Finance":
        financial.render(feats_df, raw_df, ticker, year, sector_bucket, lang_code)
    elif st.session_state.report_tab == "Sentiment":
        sentiment.render(feats_df, raw_df, ticker, year, sector_bucket, lang_code)
    elif st.session_state.report_tab == "Summary":
        summary.render(feats_df, raw_df, ticker, year, model, thresholds, sector_bucket, final_features, lang_code)
except Exception as e:
    st.error(f"Lỗi khi hiển thị tab {st.session_state.report_tab}: {str(e)}")
    st.exception(e)
