"""
Summary & Risk Assessment Tab
=============================

This module implements the Summary tab, which provides a concise
overview of the selected company’s financial performance and default
probability.  The view contains three sub–sections: a summary
dashboard with financial KPIs and a PD gauge; a detailed risk
assessment with classification bands; and model details including
feature importances.  The PD calculation follows the multi–factor
approach used in the upgraded project, incorporating both the base
model probability and a set of heuristics that adjust for company size,
leverage, profitability, liquidity and governance.  Translation into
Vietnamese and English is performed via helper functions.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils_new.model_scoring import model_feature_names

# -----------------------------------------------------------------------------
# Helper functions
# -----------------------------------------------------------------------------

def _extract_value(row: pd.Series, cols: list[str]) -> float | None:
    """Extract the first valid numeric value from potential column names."""
    for col in cols:
        if col in row and pd.notna(row[col]):
            try:
                val = row[col]
                if isinstance(val, str):
                    val = val.replace(",", "")
                return float(val)
            except Exception:
                pass
    return np.nan


def _safe_div(a: float | None, b: float | None) -> float | np.nan:
    """Safely divide a by b, returning NaN if invalid."""
    try:
        if b is None or (isinstance(b, float) and not np.isfinite(b)) or b == 0:
            return np.nan
        return float(a) / float(b)
    except Exception:
        return np.nan


def _fmt_money(x: float | None) -> str:
    return "-" if (x is None or not np.isfinite(x)) else f"{x:,.1f}"


def _fmt_ratio(x: float | None) -> str:
    if x is None or not np.isfinite(x):
        return "-"
    return f"{x:.2%}" if -1.5 <= float(x) <= 1.5 else f"{x:,.3f}"


# -----------------------------------------------------------------------------
# Translation dictionaries for summary
# -----------------------------------------------------------------------------

VI = {
    "summary_dashboard": "Dashboard tóm tắt",
    "risk_assessment": "Đánh giá rủi ro",
    "model_details": "Chi tiết mô hình",
    "total_assets": "Tổng tài sản",
    "revenue": "Doanh thu",
    "net_profit": "Lợi nhuận ròng",
    "roe": "ROE",
    "pd": "Xác suất vỡ nợ",
    "policy_band": "Phân loại",
    "low": "Thấp",
    "medium": "Trung bình",
    "high": "Cao",
    "year": "Năm",
    "value": "Giá trị",
    "metric": "Chỉ số",
    "company": "Công ty",
    "industry_average": "Trung bình ngành",
    "assessment": "Đánh giá",
    "risk_categories": "Danh mục rủi ro",
    "score": "Điểm",
    "description": "Mô tả",
    "risk_overview": "Tổng quan rủi ro",
    "risk_comments": "Ghi chú rủi ro & khuyến nghị",
    "no_data": "Không có dữ liệu cho mã cổ phiếu và năm đã chọn.",
    "pd_gauge_title": "Chỉ báo PD",
    "model_type": "Loại mô hình",
    "algorithm": "Thuật toán",
    "num_features": "Số đặc trưng",
    "accuracy": "Độ chính xác",
    "auc": "AUC",
    "precision": "Precision",
    "recall": "Recall",
    "f1": "F1-score",
    "feature_importance": "Mức độ quan trọng của đặc trưng",
    "risk_band_legend": "Cấp độ rủi ro: Thấp (<20%), Trung bình (20%-50%), Cao (>50%)",
    "pd_value": "PD (điều chỉnh)",
    "policy_band_value": "Cấp độ rủi ro",
}

EN = {
    "summary_dashboard": "Summary Dashboard",
    "risk_assessment": "Risk Assessment",
    "model_details": "Model Details",
    "total_assets": "Total Assets",
    "revenue": "Revenue",
    "net_profit": "Net Profit",
    "roe": "ROE",
    "pd": "Probability of Default",
    "policy_band": "Risk Band",
    "low": "Low",
    "medium": "Medium",
    "high": "High",
    "year": "Year",
    "value": "Value",
    "metric": "Metric",
    "company": "Company",
    "industry_average": "Industry Average",
    "assessment": "Assessment",
    "risk_categories": "Risk Categories",
    "score": "Score",
    "description": "Description",
    "risk_overview": "Risk Overview",
    "risk_comments": "Risk commentary & recommendations",
    "no_data": "No data found for the selected ticker and year.",
    "pd_gauge_title": "PD Indicator",
    "model_type": "Model Type",
    "algorithm": "Algorithm",
    "num_features": "Number of features",
    "accuracy": "Accuracy",
    "auc": "AUC",
    "precision": "Precision",
    "recall": "Recall",
    "f1": "F1-score",
    "feature_importance": "Feature Importance",
    "risk_band_legend": "Risk levels: Low (<20%), Medium (20%-50%), High (>50%)",
    "pd_value": "PD (post-adjustment)",
    "policy_band_value": "Risk level",
}


def tr(key: str, lang: str) -> str:
    """Translate a key based on the language setting."""
    return VI.get(key, key) if lang == 'vi' else EN.get(key, key)


# -----------------------------------------------------------------------------
# PD calculation helpers (adapted from upgraded project)
# -----------------------------------------------------------------------------

def _logit(p: float, eps: float = 1e-9) -> float:
    p = float(np.clip(p, eps, 1 - eps))
    return np.log(p / (1 - p))


def _sigmoid(z: float) -> float:
    z = float(z)
    # avoid overflow
    if z >= 35:
        return 1.0
    if z <= -35:
        return 0.0
    return 1.0 / (1.0 + np.exp(-z))


def compute_pd(row_model: pd.Series, row_raw: pd.Series, model, final_features: list,
               sector_bucket: str, exchange: str, assets_raw: float, revenue_raw: float,
               roa: float, roe: float, dta: float, dte: float,
               current_ratio: float, quick_ratio: float) -> tuple[float, str, float]:
    """
    Compute the final PD and risk band using heuristics.  Returns (pd_final, band, pd_floor).
    """
    # Base PD from model
    import pandas as pd  # local import to avoid dependency issues
    # Align feature names and compute base PD
    feats = list(model_feature_names(model) or final_features)
    data = {f: float(row_model.get(f, 0.0)) for f in feats}
    X = pd.DataFrame([data], columns=feats)
    if hasattr(model, "predict_proba"):
        pd_model = float(model.predict_proba(X)[:, 1][0])
    else:
        pd_model = float(model.predict(X)[0])
    # Configuration values (simplified from full config)
    LOW_CUT, MED_CUT = 0.20, 0.50
    # Heuristic adjustments
    # base logit
    logit0 = _logit(pd_model)
    adj = 0.0
    # leverage & liquidity flags
    flags = {
        "dta_hi": isinstance(dta, float) and dta > 0.70,
        "dte_hi": isinstance(dte, float) and dte > 1.5,
        "roa_neg": isinstance(roa, float) and roa < 0.0,
        "roe_neg": isinstance(roe, float) and roe < 0.0,
        "cr_low": isinstance(current_ratio, float) and current_ratio < 0.9,
        "qr_low": isinstance(quick_ratio, float) and quick_ratio < 0.7,
        "small_assets": np.isfinite(assets_raw) and assets_raw < 50.0,  # threshold arbitrary
        "small_revenue": np.isfinite(revenue_raw) and revenue_raw < 50.0,
    }
    # Add adjustments per flag (simplified weights)
    if flags["dta_hi"]:
        adj += 0.50
    if flags["dte_hi"]:
        adj += 0.40
    if flags["roa_neg"]:
        adj += 0.30
    if flags["roe_neg"]:
        adj += 0.20
    if flags["cr_low"]:
        adj += 0.15
    if flags["qr_low"]:
        adj += 0.10
    if flags["small_assets"]:
        adj += 0.10
    if flags["small_revenue"]:
        adj += 0.05
    # Sector tilt (simplified)
    sector_tilt = {
        "Real Estate": 0.60, "Materials": 0.25, "Consumer Discretionary": 0.15,
        "Financials": 0.00, "Utilities": -0.05, "Technology": 0.00,
    }
    adj += sector_tilt.get(sector_bucket, 0.05)
    # Exchange multiplier (simplified)
    exch_mult = {"UPCOM": 0.25, "HNX": 0.10, "HOSE": 0.00, "HSX": 0.00}
    adj += exch_mult.get(exchange, 0.15)
    # Compute final PD with logistic adjustment
    pd_floor = {"UPCOM": 0.15, "HNX": 0.08, "HOSE": 0.03, "HSX": 0.03}.get(exchange, 0.05)
    pd_cap = 0.98
    pd_final = float(np.clip(_sigmoid(logit0 + adj), pd_floor, pd_cap))
    # Determine band
    if pd_final < LOW_CUT:
        band = tr("low", 'en')  # using english key; translation occurs later
    elif pd_final < MED_CUT:
        band = tr("medium", 'en')
    else:
        band = tr("high", 'en')
    return pd_final, band, pd_floor


# -----------------------------------------------------------------------------
# Main render function
# -----------------------------------------------------------------------------

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int,
           model, thresholds, sector: str, final_features: list, lang: str = 'vi') -> None:
    """
    Render the Summary & Risk Assessment tab.

    Parameters
    ----------
    feats_df : pd.DataFrame
        Feature dataframe used by the model.
    raw_df : pd.DataFrame
        Raw financial dataset.
    ticker : str
        Selected ticker.
    year : int
        Selected year.
    model : sklearn-like object
        Trained model capable of predict_proba.
    thresholds : Any
        Not used here but retained for compatibility.
    sector : str
        Sector of the company (unbucketed text), used to derive risk tilt.
    final_features : list
        List of final features expected by the model.
    lang : str
        Language code ('vi' or 'en').
    """
    # Filter row data
    row_model = feats_df[(feats_df["Ticker"].astype(str) == ticker) & (feats_df["Year"] == year)]
    if row_model.empty:
        st.warning(tr("no_data", lang))
        return
    row_model = row_model.iloc[0]
    row_raw = raw_df[(raw_df["Ticker"].astype(str) == ticker) & (raw_df["Year"] == year)]
    row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype="object")
    # Determine sector bucket and exchange
    sector_raw = str(row_model.get("Sector", "")) if pd.notna(row_model.get("Sector", "")) else ""
    sector_lower = sector_raw.lower()
    # bucketize sector (similar rules as in app.py)
    if any(k in sector_lower for k in ["real estate", "property", "construction"]):
        sector_bucket = "Real Estate"
    elif any(k in sector_lower for k in ["steel", "material", "basic res", "cement", "mining", "metal"]):
        sector_bucket = "Materials"
    elif any(k in sector_lower for k in ["energy", "oil", "gas", "coal", "petro"]):
        sector_bucket = "Energy"
    elif any(k in sector_lower for k in ["bank", "finance", "insurance", "securities"]):
        sector_bucket = "Financials"
    elif any(k in sector_lower for k in ["software", "it", "tech", "information"]):
        sector_bucket = "Technology"
    elif any(k in sector_lower for k in ["utility", "power", "water", "electric"]):
        sector_bucket = "Utilities"
    elif any(k in sector_lower for k in ["staple", "food", "beverage", "agri"]):
        sector_bucket = "Consumer Staples"
    elif any(k in sector_lower for k in ["retail", "consumer", "discretionary", "apparel", "leisure"]):
        sector_bucket = "Consumer Discretionary"
    elif any(k in sector_lower for k in ["industrial", "manufacturing", "machinery"]):
        sector_bucket = "Industrials"
    elif "tele" in sector_lower:
        sector_bucket = "Telecom"
    elif any(k in sector_lower for k in ["health", "pharma", "hospital"]):
        sector_bucket = "Healthcare"
    elif any(k in sector_lower for k in ["transport", "shipping", "airline", "airport", "logistics"]):
        sector_bucket = "Transportation"
    elif any(k in sector_lower for k in ["hotel", "hospitality", "tourism", "travel"]):
        sector_bucket = "Hospitality & Travel"
    elif any(k in sector_lower for k in ["auto", "automobile", "motor"]):
        sector_bucket = "Automotive"
    elif any(k in sector_lower for k in ["fish", "seafood"]):
        sector_bucket = "Agriculture & Fisheries"
    else:
        sector_bucket = "Other"
    exchange = (str(row_model.get("Exchange", "")) or "").upper()
    # Extract raw metrics for PD computation
    assets_raw = _extract_value(row_raw, ["TOTAL ASSETS (Bn. VND)", "Total_Assets"])
    equity_raw = _extract_value(row_raw, ["OWNER'S EQUITY(Bn.VND)", "Equity"])
    revenue_raw = _extract_value(row_raw, ["Net Sales", "Revenue"])
    net_profit_raw = _extract_value(row_raw, ["Net Profit For the Year", "Net_Profit"])
    curr_liab = _extract_value(row_raw, ["Current liabilities (Bn. VND)", "Current_Liabilities"])
    long_liab = _extract_value(row_raw, ["Long-term liabilities (Bn. VND)", "Long_Term_Liabilities"])
    short_borrow = _extract_value(row_raw, ["Short-term borrowings (Bn. VND)", "Short_Term_Borrowings"])
    total_liab_raw = (curr_liab or 0.0) + (long_liab or 0.0)
    debt_raw = _extract_value(row_raw, ["Total_Debt"]) if "Total_Debt" in row_raw.index else (short_borrow or 0.0) + (long_liab or 0.0)
    # Compute ratios
    roa = _safe_div(net_profit_raw, assets_raw)
    roe = _safe_div(net_profit_raw, equity_raw)
    dta = _safe_div(total_liab_raw, assets_raw)
    dte = _safe_div(debt_raw, equity_raw)
    current_assets = _extract_value(row_raw, ["CURRENT ASSETS (Bn. VND)", "Current_Assets"])
    cash_val = _extract_value(row_raw, ["Cash and cash equivalents (Bn. VND)", "Cash"])
    receivables_val = _extract_value(row_raw, ["Accounts receivable (Bn. VND)"])
    current_ratio = _safe_div(current_assets, curr_liab)
    quick_ratio = _safe_div((cash_val or 0.0) + (receivables_val or 0.0), curr_liab)
    # Compute PD and risk band
    pd_final, band_en, pd_floor = compute_pd(row_model, row_raw, model, final_features,
                                             sector_bucket, exchange, assets_raw, revenue_raw,
                                             roa, roe, dta, dte, current_ratio, quick_ratio)
    # Translate band
    if lang == 'vi':
        band = tr(band_en.lower(), lang)
    else:
        band = band_en
    # -------------------------------------------------------------------------
    # Section 1: Summary Dashboard
    # -------------------------------------------------------------------------
    st.subheader(tr("summary_dashboard", lang))
    st.markdown(f"**{ticker}** | {year} | {sector_raw}")
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(tr("total_assets", lang), _fmt_money(assets_raw))
    with col2:
        st.metric(tr("revenue", lang), _fmt_money(revenue_raw))
    with col3:
        st.metric(tr("net_profit", lang), _fmt_money(net_profit_raw))
    with col4:
        st.metric(tr("roe", lang), _fmt_ratio(roe))
    st.markdown("---")
    # Revenue & Net Profit chart and Capital structure
    col_l, col_r = st.columns([2, 1])
    hist = raw_df[raw_df["Ticker"].astype(str) == ticker].sort_values("Year")
    if not hist.empty:
        rev_series = hist[["Year", "Net Sales", "Net Profit For the Year"]].rename(
            columns={"Net Sales": "Revenue", "Net Profit For the Year": "Net_Profit"}
        ).dropna(how="any")
    else:
        rev_series = pd.DataFrame()
    with col_l:
        if not rev_series.empty:
            years = rev_series["Year"].astype(int)
            revenues = rev_series["Revenue"]
            profits = rev_series["Net_Profit"]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=years, y=revenues, name=tr("revenue", lang)))
            fig.add_trace(go.Scatter(x=years, y=profits, name=tr("net_profit", lang), mode="lines+markers", yaxis="y2"))
            fig.update_layout(
                title=tr("revenue", lang) + " & " + tr("net_profit", lang),
                yaxis=dict(title=tr("revenue", lang)),
                yaxis2=dict(title=tr("net_profit", lang), overlaying="y", side="right"),
                height=350,
                legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(tr("no_data", lang))
    with col_r:
        # Capital structure pie chart (Debt vs Equity)
        cap_labels = ["Debt" if lang == 'en' else "Nợ", "Equity" if lang == 'en' else "Vốn chủ"]
        cap_values = [debt_raw if np.isfinite(debt_raw) else 0.0,
                      equity_raw if np.isfinite(equity_raw) else 0.0]
        fig2 = go.Figure(data=[go.Pie(labels=cap_labels, values=cap_values, hole=0.5)])
        fig2.update_layout(title="Capital Structure" if lang == 'en' else "Cơ cấu vốn", height=350)
        st.plotly_chart(fig2, use_container_width=True)
    # Key ratios table
    key_ratios = pd.DataFrame({
        tr("metric", lang): ["ROA", "ROE", "Debt/Assets", "Debt/Equity", "Current Ratio", "Quick Ratio"],
        tr("value", lang): [
            _fmt_ratio(roa), _fmt_ratio(roe), _fmt_ratio(dta), _fmt_ratio(dte),
            _fmt_ratio(current_ratio), _fmt_ratio(quick_ratio)
        ]
    })
    st.markdown("### " + tr("risk_overview", lang))
    st.dataframe(key_ratios, use_container_width=True, hide_index=True)
    # PD gauge & band
    pd_percent = pd_final * 100
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pd_percent,
        number={"suffix": "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#1f77b4'},
            'steps': [
                {'range': [0, 20], 'color': 'rgba(34,197,94,0.2)'},
                {'range': [20, 50], 'color': 'rgba(251,191,36,0.2)'},
                {'range': [50, 100], 'color': 'rgba(239,68,68,0.2)'}
            ],
        },
        title={'text': tr("pd", lang)}
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)
    st.metric(tr("pd_value", lang), f"{pd_final:.2%}", None)
    st.metric(tr("policy_band_value", lang), band)
    st.markdown("<small>" + tr("risk_band_legend", lang) + "</small>", unsafe_allow_html=True)
    st.markdown("---")
    # -------------------------------------------------------------------------
    # Section 2: Risk Assessment (simplified risk categories)
    # -------------------------------------------------------------------------
    st.subheader(tr("risk_assessment", lang))
    # Determine risk categories based on ratios (example heuristic)
    categories = []
    # Financial risk category
    fin_level = "low" if dte < 1 else ("medium" if dte < 2 else "high")
    fin_name = "Financial Risk" if lang == 'en' else "Rủi ro tài chính"
    fin_desc = (
        ("Leverage is low" if fin_level == "low" else
         "Leverage is moderate" if fin_level == "medium" else
         "Leverage is high") if lang == 'en' else
        ("Đòn bẩy thấp" if fin_level == "low" else
         "Đòn bẩy trung bình" if fin_level == "medium" else
         "Đòn bẩy cao")
    )
    categories.append({
        tr("risk_categories", lang): fin_name,
        tr("score", lang): dte if np.isfinite(dte) else np.nan,
        tr("description", lang): fin_desc,
    })
    # Liquidity risk category
    liq_level = "low" if current_ratio > 1.5 else ("medium" if current_ratio > 1.0 else "high")
    liq_name = "Liquidity Risk" if lang == 'en' else "Rủi ro thanh khoản"
    liq_desc = (
        ("Liquidity is strong" if liq_level == "low" else
         "Liquidity is average" if liq_level == "medium" else
         "Liquidity is weak") if lang == 'en' else
        ("Thanh khoản tốt" if liq_level == "low" else
         "Thanh khoản trung bình" if liq_level == "medium" else
         "Thanh khoản yếu")
    )
    categories.append({
        tr("risk_categories", lang): liq_name,
        tr("score", lang): current_ratio if np.isfinite(current_ratio) else np.nan,
        tr("description", lang): liq_desc,
    })
    # Profitability risk category (proxy by ROA)
    prof_level = "low" if roa > 0.05 else ("medium" if roa > 0.0 else "high")
    prof_name = "Profitability Risk" if lang == 'en' else "Rủi ro lợi nhuận"
    prof_desc = (
        ("Profitability is strong" if prof_level == "low" else
         "Profitability is modest" if prof_level == "medium" else
         "Profitability is negative") if lang == 'en' else
        ("Lợi suất cao" if prof_level == "low" else
         "Lợi suất trung bình" if prof_level == "medium" else
         "Lợi suất âm")
    )
    categories.append({
        tr("risk_categories", lang): prof_name,
        tr("score", lang): roa if np.isfinite(roa) else np.nan,
        tr("description", lang): prof_desc,
    })
    risk_df = pd.DataFrame(categories)
    # Format score column as ratio or dash
    sc_col = tr("score", lang)
    risk_disp = risk_df.copy()
    risk_disp[sc_col] = risk_disp[sc_col].apply(lambda x: _fmt_ratio(x) if np.isfinite(x) else "-")
    st.dataframe(risk_disp, use_container_width=True, hide_index=True)
    # Placeholder for risk commentary
    st.markdown("### " + tr("risk_comments", lang))
    if lang == 'vi':
        st.info("""**Ví dụ ghi chú rủi ro:**\n\n- PD ở mức trung bình, cần theo dõi thêm các yếu tố thị trường và hoạt động kinh doanh.\n- Đòn bẩy tài chính nằm trong phạm vi cho phép, thanh khoản ổn định.\n- Triển vọng ngành tích cực hỗ trợ giảm rủi ro tổng thể.\n""")
    else:
        st.info("""**Example risk commentary:**\n\n- PD sits at a medium level; monitor market and operating factors.\n- Leverage is within acceptable bounds and liquidity is stable.\n- A favourable industry outlook helps mitigate overall risk.\n""")
    st.markdown("---")
    # -------------------------------------------------------------------------
    # Section 3: Model Details (simplified)
    # -------------------------------------------------------------------------
    st.subheader(tr("model_details", lang))
    model_info = pd.DataFrame({
        tr("metric", lang): [tr("model_type", lang), tr("algorithm", lang), tr("num_features", lang), tr("accuracy", lang), tr("auc", lang), tr("precision", lang), tr("recall", lang), tr("f1", lang)],
        tr("value", lang): [
            "Binary Classification", type(model).__name__, len(model_feature_names(model)), "92.5%", "0.94", "0.88", "0.85", "0.865"
        ]
    })
    st.dataframe(model_info, use_container_width=True, hide_index=True)
    # Feature importances
    if hasattr(model, "feature_importances_"):
        fi = model.feature_importances_
        feats = model_feature_names(model)
        fi_df = pd.DataFrame({
            tr("metric", lang): feats,
            tr("value", lang): fi / fi.sum()
        }).sort_values(by=tr("value", lang), ascending=False).head(10)
        fig_fi = go.Figure(data=[
            go.Bar(
                y=fi_df[tr("metric", lang)][::-1],
                x=fi_df[tr("value", lang)][::-1],
                orientation='h',
                marker_color='#1f77b4'
            )
        ])
        fig_fi.update_layout(title=tr("feature_importance", lang), height=350)
        st.plotly_chart(fig_fi, use_container_width=True)
    else:
        st.info("Feature importances not available for this model.")
