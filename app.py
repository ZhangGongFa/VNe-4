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

# ==== Import language configuration ====
from utils_new.lang import LANG_VI, LANG_EN, get_text, T

warnings.filterwarnings("ignore", category=UserWarning)

# Load a mapping of ticker symbols to their full Vietnamese/English company names.
# This optional CSV should live alongside the application code and have columns
# `Ticker`, `CompanyNameVi`, and optionally `CompanyNameEn`. If the file or a
# particular ticker is missing, we fall back to using the ticker symbol as the
# name. Caching is used so the file is read only once per session.
@st.cache_data(show_spinner=False)
def load_company_names(file_path: str | None = None) -> dict:
    """Load a dictionary mapping tickers to company names.

    Parameters
    ----------
    file_path: Optional path to the CSV mapping file. If not provided, the
        function will attempt to load a file named `company_names.csv` located
        in the same directory as this module. The expected CSV schema is::

            Ticker,CompanyNameVi,CompanyNameEn

    Returns
    -------
    dict
        A dictionary keyed by uppercase ticker with values being another
        dictionary containing the Vietnamese ("vi") and English ("en") names. If
        the file does not exist or cannot be read, an empty dictionary is
        returned. Missing fields fall back to the ticker itself.
    """
    # Determine the default path relative to this file when not provided
    if file_path is None:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(this_dir, "company_names.csv")

    names: dict[str, dict[str, str]] = {}
    if not os.path.exists(file_path):
        return names
    try:
        df = pd.read_csv(file_path)
        # Normalize the ticker column to uppercase strings
        if 'Ticker' not in df.columns:
            return names
        for _, row in df.iterrows():
            tkr = str(row['Ticker']).strip().upper()
            vi = str(row.get('CompanyNameVi', '')).strip()
            en = str(row.get('CompanyNameEn', vi)).strip()
            if not tkr:
                continue
            names[tkr] = {"vi": vi if vi else tkr, "en": en if en else tkr}
    except Exception:
        # Ignore errors silently; fallback will be used
        return {}
    return names

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

# ---------- Initialize language session state ----------
if 'current_lang' not in st.session_state:
    st.session_state.current_lang = LANG_VI

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
    # Language selector
    st.markdown("### 🌐 Ngôn Ngữ / Language")
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("🇻🇳 Việt", key="lang_vi", use_container_width=True):
            st.session_state.current_lang = LANG_VI
            st.rerun()
    with lang_col2:
        if st.button("🇬🇧 English", key="lang_en", use_container_width=True):
            st.session_state.current_lang = LANG_EN
            st.rerun()
    
    # Section: select ticker and year
    st.markdown("---")
    st.header(get_text("sidebar_ticker_header", st.session_state.current_lang))

    # Ticker selection
    tickers = sorted(feats_df["Ticker"].astype(str).unique().tolist())
    ticker = st.selectbox(get_text("select_ticker", st.session_state.current_lang), tickers, index=0 if tickers else None, key="sb_ticker")

    # Year selection (default to latest available year for the selected ticker)
    years_avail = sorted(feats_df.loc[feats_df["Ticker"].astype(str)==ticker, "Year"].dropna().astype(int).unique().tolist())
    year_idx = len(years_avail)-1 if years_avail else 0
    year = st.selectbox(get_text("select_year", st.session_state.current_lang), years_avail, index=year_idx, key=f"sb_year_{ticker}")

    # Immediately show a summary profile for the selected company to improve discoverability
    # Compute the summary row from the raw dataset
    row_raw_sm = raw_df[(raw_df["Ticker"].astype(str) == str(ticker)) & (raw_df["Year"] == year)]
    row_raw_sm = row_raw_sm.iloc[0] if not row_raw_sm.empty else None
    if row_raw_sm is not None:
        def _get_raw_info(col_names, default=np.nan):
            for col in col_names:
                if col in row_raw_sm.index and pd.notna(row_raw_sm[col]):
                    x = row_raw_sm[col]
                    try:
                        if isinstance(x, str):
                            x = x.replace(",", "")
                        return float(x)
                    except Exception:
                        continue
            return default
        assets_sm = _get_raw_info(["TOTAL ASSETS (Bn. VND)", "Total_Assets"])
        equity_sm = _get_raw_info(["OWNER'S EQUITY(Bn.VND)", "Equity"])
        curr_liab_sm = _get_raw_info(["Current liabilities (Bn. VND)", "Current_Liabilities"], 0.0)
        long_liab_sm = _get_raw_info(["Long-term liabilities (Bn. VND)", "Long_Term_Liabilities"], 0.0)
        debt_sm = (curr_liab_sm or 0.0) + (long_liab_sm or 0.0)
        if "Total_Debt" in row_raw_sm.index and pd.notna(row_raw_sm.get("Total_Debt")):
            try:
                debt_sm = float(str(row_raw_sm.get("Total_Debt")).replace(",", ""))
            except Exception:
                pass
        ex = (str(row_raw_sm.get("Exchange", "")) or "-").upper()
        sec_raw = str(row_raw_sm.get("Sector", "")).strip()
        sec = sec_raw if sec_raw else "-"
        assets_disp = fmt_money(assets_sm)
        equity_disp = fmt_money(equity_sm)
        debt_disp = fmt_money(debt_sm)
        lang_cur = st.session_state.current_lang
        # Determine logo URL (use uppercase ticker to match Vietstock image endpoint)
        logo_url = f"https://finance.vietstock.vn/image/{ticker.upper()}"
        # Lookup company name from optional CSV mapping. If not found, fallback to ticker.
        names_dict = load_company_names()
        # Default names for Vietnamese and English
        name_vi = ticker.upper()
        name_en = ticker.upper()
        if isinstance(names_dict, dict):
            nm = names_dict.get(str(ticker).upper())
            if nm:
                name_vi = nm.get("vi", name_vi) or name_vi
                name_en = nm.get("en", name_en) or name_en
        # Prepare translated labels for ticker and other fields
        # Vietnamese label for ticker
        ticker_label_vi = "Mã cổ phiếu"
        ticker_label_en = "Ticker"
        # Select the appropriate labels for exchange and sector
        if lang_cur == LANG_VI:
            header_text = get_text('profile_header', lang_cur)
            company_display = name_vi if name_vi else ticker.upper()
            ticker_label = ticker_label_vi
            exchange_label = "Sàn:"
            sector_label = "Ngành:"
        else:
            header_text = get_text('profile_header', lang_cur)
            # Use the English company name if available, otherwise fall back to Vietnamese
            company_display = name_en if name_en else name_vi if name_vi else ticker.upper()
            ticker_label = ticker_label_en
            exchange_label = "Exchange:"
            sector_label = "Sector:"

        # Build the company profile card.  Use a vertical layout to avoid the logo overflowing
        # and ensure the logo does not stretch or distort the card.  The logo is limited in
        # both height and width for consistent sizing across different aspect ratios.
        card_html = f"""
        <div style='background-color:#E8F1FB;border:1px solid #cbd5e1;border-radius:10px;padding:12px;margin-top:6px;'>
          <div style='font-weight:600;font-size:15px;margin-bottom:6px;'>{header_text}</div>
          <div style='font-weight:600;font-size:14px;margin-bottom:4px;'>{company_display}</div>
          <div style='font-size:13px;margin-bottom:6px;'><strong>{ticker_label}:</strong> {ticker.upper()}</div>
          <div style='margin-bottom:8px;'>
            <img src='{logo_url}' alt='logo' style='max-height:50px;max-width:140px;width:auto;height:auto;object-fit:contain;'>
          </div>
          <div style='font-size:13px;'><strong>{exchange_label}</strong> {ex}</div>
          <div style='font-size:13px;'><strong>{sector_label}</strong> {sec}</div>
          <div style='font-size:13px;'><strong>{get_text('metric_total_assets', lang_cur)}:</strong> {assets_disp}</div>
          <div style='font-size:13px;'><strong>{get_text('metric_equity', lang_cur)}:</strong> {equity_disp}</div>
          <div style='font-size:13px;'><strong>{get_text('metric_debt', lang_cur)}:</strong> {debt_disp}</div>
        </div>
        """
        # Render the card
        st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info(get_text("warning_no_data", st.session_state.current_lang))

    st.markdown("---")
    # Section: report type selection
    st.header(get_text("sidebar_report_header", st.session_state.current_lang))

    # Initialize session state for report selection
    if 'report_tab' not in st.session_state:
        st.session_state.report_tab = "Summary"

    # Create vertical buttons for report selection. Each button spans full width to prevent text wrapping.
    if st.button(get_text("btn_finance", st.session_state.current_lang), key="btn_financial", use_container_width=True):
        st.session_state.report_tab = "Finance"
    if st.button(get_text("btn_sentiment", st.session_state.current_lang), key="btn_sentiment", use_container_width=True):
        st.session_state.report_tab = "Sentiment"
    if st.button(get_text("btn_summary", st.session_state.current_lang), key="btn_summary", use_container_width=True):
        st.session_state.report_tab = "Summary"

    st.markdown("---")


# ---------- Get selected data ----------
row_model = feats_df[(feats_df["Ticker"].astype(str)==ticker) & (feats_df["Year"]==year)]
if row_model.empty:
    st.warning(get_text("warning_no_data", st.session_state.current_lang))
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
    # Wrap rendering in a spinner to indicate loading when switching reports or tickers
    spinner_msg = "Đang tải dữ liệu..." if st.session_state.current_lang == LANG_VI else "Loading data..."
    with st.spinner(spinner_msg):
        if st.session_state.report_tab == "Finance":
            financial.render(feats_df, raw_df, ticker, year, model, thresholds, sector_bucket, final_features)
        elif st.session_state.report_tab == "Sentiment":
            sentiment.render(feats_df, raw_df, ticker, year, model, thresholds, sector_bucket, final_features)
        elif st.session_state.report_tab == "Summary":
            summary.render(feats_df, raw_df, ticker, year, model, thresholds, sector_bucket, final_features)
except Exception as e:
    st.error(f"Lỗi khi hiển thị tab {st.session_state.report_tab}: {str(e)}")
    st.exception(e)
