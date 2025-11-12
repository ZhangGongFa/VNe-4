"""
Summary Tab
------------

This module provides the **Summary** view for the upgraded PD scoring
application.  Its purpose is to mirror the look and feel of the original
project’s summary section found in ``PD-monotonic-constraints-main.zip``.
Unlike the financial and sentiment tabs, which are handled elsewhere,
this module focuses solely on presenting a consolidated overview of
company financials, default probability (PD) and model explainability.

The summary is divided into four sections:

1. **Company Financial Overview** – A multi‑year chart of revenue and
   net profit, a capital structure pie chart (debt versus equity) and
   a simple table of key financial ratios.
2. **Default Probability (PD) & Policy Band** – The base PD from the
   model is adjusted for leverage, profitability, liquidity, company
   size, sector tilt and exchange listing.  The final PD and policy
   band are displayed along with a gauge and legend.
3. **Model Explainability (SHAP)** – Top feature contributions are
   visualised if the model exposes SHAP values; otherwise a message
   indicates SHAP is unavailable.
4. **Stress Testing – Sector & Systemic Impacts** – Illustrative PD
   values under preset sector and systemic stress scenarios are shown
   relative to the baseline PD.

The implementation deliberately avoids any dependencies on the
finance/sentiment modules and does not use the language translation
utilities.  All labels are presented in English to match the original
dashboard.  Should you wish to localise the text, you may wrap static
strings in a translation function or import ``get_text`` from
``utils_new.lang`` and adjust accordingly.

"""

from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Import model_feature_names and explain_shap.  We deliberately do not
# import load_train_reference here because some deployments of the
# `utils_new.model_scoring` module do not expose that function.  The
# quantile computation inside `_compute_pd_base` will handle its
# absence gracefully.
from utils_new.model_scoring import model_feature_names, explain_shap
from utils_new.lang import get_text

__all__ = ["render"]


def _bucketize_sector(sector_raw: str) -> str:
    """Coarse mapping of free‑form sector strings into standard buckets.

    Parameters
    ----------
    sector_raw : str
        The raw sector name as contained in the dataset.

    Returns
    -------
    str
        One of a limited set of sectors such as ``"Real Estate"``,
        ``"Materials"``, ``"Technology"``, etc.  If no match is found,
        ``"Other"`` is returned.
    """
    s = (sector_raw or "").lower()
    if any(k in s for k in ["real estate", "property", "construction"]):
        return "Real Estate"
    if any(k in s for k in ["steel", "material", "basic res", "cement", "mining", "metal"]):
        return "Materials"
    if any(k in s for k in ["energy", "oil", "gas", "coal", "petro"]):
        return "Energy"
    if any(k in s for k in ["bank", "finance", "insurance", "securities"]):
        return "Financials"
    if any(k in s for k in ["software", "it", "tech", "information"]):
        return "Technology"
    if any(k in s for k in ["utility", "power", "water", "electric"]):
        return "Utilities"
    if any(k in s for k in ["staple", "food", "beverage", "agri"]):
        return "Consumer Staples"
    if any(k in s for k in ["retail", "consumer", "discretionary", "apparel", "leisure"]):
        return "Consumer Discretionary"
    if any(k in s for k in ["industrial", "manufacturing", "machinery"]):
        return "Industrials"
    if "tele" in s:
        return "Telecom"
    if any(k in s for k in ["health", "pharma", "hospital"]):
        return "Healthcare"
    if any(k in s for k in ["transport", "shipping", "airline", "airport", "logistics"]):
        return "Transportation"
    if any(k in s for k in ["hotel", "hospitality", "tourism", "travel"]):
        return "Hospitality & Travel"
    if any(k in s for k in ["auto", "automobile", "motor"]):
        return "Automotive"
    if any(k in s for k in ["fish", "seafood"]):
        return "Agriculture & Fisheries"
    return "Other"


def _safe_div(a: float | None, b: float | None) -> float:
    """Safely divide two values returning ``np.nan`` if invalid."""
    try:
        if b is None or (isinstance(b, float) and not np.isfinite(b)) or float(b) == 0.0:
            return np.nan
        return float(a) / float(b)
    except Exception:
        return np.nan


def _fmt_ratio(x: float | None) -> str:
    """Format a numeric ratio as a percentage string for display."""
    if x is None or not np.isfinite(x):
        return "-"
    return f"{x:.2%}"


def _fmt_money(x: float | None) -> str:
    """Format a monetary figure with thousands separators."""
    if x is None or not np.isfinite(x):
        return "-"
    return f"{x:,.2f}"


def _extract_first(row: pd.Series, cols: list[str], default: float | None = np.nan) -> float:
    """Extract the first non‑null numeric value from a list of column candidates."""
    for c in cols:
        if c in row and pd.notna(row[c]):
            val = row[c]
            try:
                if isinstance(val, str):
                    val = val.replace(",", "")
                return float(val)
            except Exception:
                continue
    return default


def _get_from_row(row: pd.Series, keys: list[str], default: float | None = np.nan) -> float:
    """Helper to extract a value from a row given several possible column names."""
    for k in keys:
        if k in row.index and pd.notna(row.get(k)):
            try:
                return float(row.get(k))
            except Exception:
                return default
    return default


def _compute_pd_base(row_model: pd.Series, row_raw: pd.Series, model, final_features: list,
                     sector_bucket: str, exchange: str, assets_raw: float, revenue_raw: float,
                     roa: float, roe: float, dta: float, dte: float,
                     current_ratio: float, quick_ratio: float) -> tuple[float, str, float]:
    """Compute adjusted PD, risk band and floor following the original logic.

    This function is largely ported from the original ``app.py``.  It
    obtains a base probability from the model and then applies additive
    adjustments based on leverage, profitability, liquidity, size,
    sector tilt and exchange listing.  Final PD is clipped to a floor
    and cap.  Returns `(pd_final, band_label, pd_floor)` where
    ``band_label`` is one of ``Low``, ``Medium`` or ``High``.
    """
    import pandas as pd  # Local import to avoid circular dependencies

    # Align feature vector for model input
    feats = model_feature_names(model) or final_features
    data = {f: float(row_model.get(f, 0.0)) for f in feats}
    X = pd.DataFrame([data], columns=feats)
    # Base PD from model
    if hasattr(model, "predict_proba"):
        pd_model = float(model.predict_proba(X)[:, 1][0])
    else:
        pd_model = float(model.predict(X)[0])
    # Logit and sigmoid helpers
    def _logit(p: float, eps: float = 1e-9) -> float:
        p = float(np.clip(p, eps, 1 - eps))
        return np.log(p / (1 - p))
    def _sigmoid(z: float) -> float:
        z = float(z)
        if z >= 35:
            return 1.0
        if z <= -35:
            return 0.0
        return 1.0 / (1.0 + np.exp(-z))
    # Fixed policy cutoffs
    LOW_CUT, MED_CUT = 0.20, 0.50
    # Define overrides for specific tickers (copy from original app)
    TICKER_OVERRIDES: dict[str, dict[str, float]] = {
        "HAG": {"logit_boost": 2.20, "severity_boost": 0.50, "pd_floor": 0.45},
        "ROS": {"logit_boost": 1.60, "severity_boost": 0.40, "pd_floor": 0.30},
    }
    # PD configuration (sector and financial adjustments)
    PD_CFG = {
        "exchange_logit_mult": {"UPCOM": 1.10, "HNX": 0.45, "HOSE": 0.00, "HSX": 0.00, "__default__": 0.20},
        "size": {"assets_q40": 0.35, "revenue_q40": 0.20},
        "leverage": {"dta_hi": 0.50, "dte_hi": 0.40, "netde_hi": 0.35},
        "profitability": {"roa_neg": 0.50, "roe_neg": 0.35, "npm_neg": 0.30, "rev_cagr_neg": 0.25},
        "liquidity": {"cr_low": 0.25, "qr_low": 0.20},
        "governance": {"auditor_non_big4": 0.25, "opinion_qualified": 0.70, "filing_delay": 0.25},
        "sector_tilt": {
            "Real Estate": 0.60, "Materials": 0.25, "Consumer Discretionary": 0.15,
            "Financials": 0.00, "Utilities": -0.05, "Technology": 0.00, "__default__": 0.05
        },
        "pd_floor": {"UPCOM": 0.15, "HNX": 0.08, "HOSE": 0.03, "HSX": 0.03, "__default__": 0.05},
        "pd_cap": {"default": 0.98},
    }
    # Helper to extract values from rows (copied from original app)
    def _get(sr: pd.Series, keys: list[str], default_val: float = np.nan) -> float:
        for k in keys:
            if k in sr.index and pd.notna(sr.get(k)):
                try:
                    return float(sr.get(k))
                except Exception:
                    return default_val
        return default_val
    # Additional signals from feature and raw rows
    npm = _get(row_model, ["Net_Profit_Margin", "net_profit_margin"])
    rev_cagr3y = _get(row_model, ["Revenue_CAGR_3Y", "revenue_cagr_3y", "sales_cagr_3y"])
    nde = _get(row_model, ["Net_Debt_to_Equity", "net_debt_to_equity"])
    auditor = str(_get(row_raw, ["Auditor", "Audit_Firm", "Auditor_Name"], "") or "")
    opinion = str(_get(row_raw, ["Audit_Opinion", "Opinion"], "") or "")
    filing_delay = _get(row_raw, ["Filing_Delay_Days", "Filing_Delay"], np.nan)
    # Quantile thresholds from training reference
    # Attempt to compute quantiles from the training reference.  Not all
    # deployments bundle ``load_train_reference`` so we handle missing
    # imports gracefully.  If unavailable, the quantiles remain NaN and
    # the size flags will not trigger.
    try:
        # Import within the function to avoid module load failure at import time.
        from utils_new.model_scoring import load_train_reference  # type: ignore
        ref_df = load_train_reference()
        ref_use = ref_df if isinstance(ref_df, pd.DataFrame) else None
    except Exception:
        ref_use = None
    def _q(col: str, q: float, fallback: float = np.nan) -> float:
        if ref_use is not None and col in ref_use.columns and ref_use[col].notna().any():
            try:
                return float(pd.to_numeric(ref_use[col], errors="coerce").quantile(q))
            except Exception:
                return fallback
        return fallback
    assets_q40 = _q("Total_Assets", 0.40)
    revenue_q40 = _q("Revenue", 0.40)
    # Build risk flags
    flags = {
        "exch_mult": PD_CFG["exchange_logit_mult"].get(exchange, PD_CFG["exchange_logit_mult"]["__default__"]),
        "assets_q40": (np.isfinite(assets_raw) and np.isfinite(assets_q40) and assets_raw < assets_q40),
        "revenue_q40": (np.isfinite(revenue_raw) and np.isfinite(revenue_q40) and revenue_raw < revenue_q40),
        "dta_hi": (isinstance(dta, float) and dta > 0.70),
        "dte_hi": (isinstance(dte, float) and dte > 1.5),
        "netde_hi": (isinstance(nde, float) and nde > 1.0),
        "roa_neg": (isinstance(roa, float) and roa < 0.0),
        "roe_neg": (isinstance(roe, float) and roe < 0.0),
        "npm_neg": (isinstance(npm, float) and npm < 0.0),
        "rev_cagr_neg": (isinstance(rev_cagr3y, float) and rev_cagr3y < 0.0),
        "cr_low": (isinstance(current_ratio, float) and current_ratio < 0.9),
        "qr_low": (isinstance(quick_ratio, float) and quick_ratio < 0.7),
        "auditor_non_big4": (auditor != "" and not any(k in auditor.lower() for k in ["deloitte", "kpmg", "ey", "ernst", "pwc", "pricewaterhouse"])),
        "opinion_qualified": (opinion != "" and any(k in opinion.lower() for k in ["qualified", "adverse", "disclaimer"])),
        "filing_delay": (isinstance(filing_delay, float) and filing_delay >= 20),
    }
    # Risk intensity multiplier
    risk_intensity = 1.0
    for cond, bump in [
        ("dta_hi", 0.25), ("dte_hi", 0.20), ("netde_hi", 0.15),
        ("cr_low", 0.15), ("qr_low", 0.10),
        ("roa_neg", 0.20), ("roe_neg", 0.10), ("npm_neg", 0.10), ("rev_cagr_neg", 0.10),
        ("assets_q40", 0.10), ("revenue_q40", 0.05),
    ]:
        if flags[cond]:
            risk_intensity += bump
    if exchange == "UPCOM":
        risk_intensity += 0.25
    risk_intensity = float(np.clip(risk_intensity, 1.0, 2.5))
    # Base logit and adjustments
    logit0 = _logit(pd_model)
    adj = 0.0
    # Exchange multiplier
    adj += flags["exch_mult"]
    # Sector tilt
    adj += PD_CFG["sector_tilt"].get(sector_bucket, PD_CFG["sector_tilt"]["__default__"])
    # Group adjustments
    for group_cfg, conds in [
        (PD_CFG["size"], ["assets_q40", "revenue_q40"]),
        (PD_CFG["leverage"], ["dta_hi", "dte_hi", "netde_hi"]),
        (PD_CFG["profitability"], ["roa_neg", "roe_neg", "npm_neg", "rev_cagr_neg"]),
        (PD_CFG["liquidity"], ["cr_low", "qr_low"]),
        (PD_CFG["governance"], ["auditor_non_big4", "opinion_qualified", "filing_delay"]),
    ]:
        for c in conds:
            if flags[c]:
                adj += group_cfg[c]
    # Apply per‑ticker overrides if present
    ov = TICKER_OVERRIDES.get(str(row_model.get("Ticker")), {})
    adj += float(ov.get("logit_boost", 0.0))
    risk_intensity += float(ov.get("risk_boost", 0.0))
    adj *= risk_intensity
    # PD floor and cap
    pd_floor = float(ov.get("pd_floor", PD_CFG["pd_floor"].get(exchange, PD_CFG["pd_floor"]["__default__"])))
    pd_cap = PD_CFG["pd_cap"]["default"]
    # Final PD
    pd_final = float(np.clip(_sigmoid(logit0 + adj), pd_floor, pd_cap))
    # Risk band classification
    if pd_final < LOW_CUT:
        band_label = "Low"
    elif pd_final < MED_CUT:
        band_label = "Medium"
    else:
        band_label = "High"
    return pd_final, band_label, pd_floor


def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int,
           model, thresholds, sector: str, final_features: list) -> None:
    """Render the summary tab for the selected ticker and year.

    This function computes financial metrics, default probability, SHAP
    explanations and stress test scenarios, then displays them using
    Streamlit widgets.  It does not modify global state or touch the
    finance and sentiment tabs.

    Parameters
    ----------
    feats_df : pd.DataFrame
        Dataframe of engineered features used for modelling.
    raw_df : pd.DataFrame
        Raw financial dataset containing original values.
    ticker : str
        The selected stock ticker (as string).
    year : int
        The selected fiscal year for detailed metrics.
    model : Any
        Trained classification/regression model implementing ``predict``
        and optionally ``predict_proba``.
    thresholds : Any
        Not used in this tab, kept for API consistency.
    sector : str
        Not used (sector is derived from data) but retained for
        compatibility.
    final_features : list
        Names of features expected by the model.  Used as a fallback
        if ``model_feature_names`` returns ``None``.
    """
    # Filter for selected row in features and raw data
    row_model = feats_df[(feats_df["Ticker"].astype(str) == ticker) & (feats_df["Year"] == year)]
    if row_model.empty:
        st.warning("No record for selected Ticker & Year.")
        return
    row_model = row_model.iloc[0]
    # Determine current language for localisation
    lang = st.session_state.get('current_lang', 'vi')
    row_raw_candidates = raw_df[(raw_df["Ticker"].astype(str) == ticker) & (raw_df["Year"] == year)]
    row_raw = row_raw_candidates.iloc[0] if not row_raw_candidates.empty else pd.Series(dtype="object")
    # Sector and exchange determination
    sector_raw = str(row_model.get("Sector", "")) if pd.notna(row_model.get("Sector", "")) else ""
    sector_bucket = _bucketize_sector(sector_raw)
    exchange = (str(row_model.get("Exchange", "")) or "").upper()
    # Extract raw numeric values for metrics
    assets_raw = _extract_first(row_raw, ["TOTAL ASSETS (Bn. VND)", "Total_Assets"])
    equity_raw = _extract_first(row_raw, ["OWNER'S EQUITY(Bn.VND)", "Equity"])
    curr_liab = _extract_first(row_raw, ["Current liabilities (Bn. VND)", "Current_Liabilities"], 0.0)
    long_liab = _extract_first(row_raw, ["Long-term liabilities (Bn. VND)", "Long_Term_Liabilities"], 0.0)
    short_bor = _extract_first(row_raw, ["Short-term borrowings (Bn. VND)", "Short_Term_Borrowings"], 0.0)
    revenue_raw = _extract_first(row_raw, ["Net Sales", "Revenue"])
    net_profit_raw = _extract_first(row_raw, ["Net Profit For the Year", "Net_Profit"])
    total_liab_raw = (curr_liab or 0.0) + (long_liab or 0.0)
    debt_raw = (
        _extract_first(row_raw, ["Total_Debt"])
        if "Total_Debt" in row_raw.index and pd.notna(row_raw.get("Total_Debt"))
        else (short_bor or 0.0) + (long_liab or 0.0)
    )
    # Additional values for liquidity ratios
    current_assets = _extract_first(row_raw, ["CURRENT ASSETS (Bn. VND)", "Current_Assets"])
    cash_val = _extract_first(row_raw, ["Cash and cash equivalents (Bn. VND)", "Cash"])
    receivables_val = _extract_first(row_raw, ["Accounts receivable (Bn. VND)", "Receivables"])
    # Compute ratios
    roa = _safe_div(net_profit_raw, assets_raw)
    roe = _safe_div(net_profit_raw, equity_raw)
    dta = _safe_div(total_liab_raw, assets_raw)
    dta = min(max(dta, 0.0), 0.999) if pd.notna(dta) else np.nan
    dte = _safe_div(debt_raw, equity_raw)
    dte = min(max(dte, 0.0), 0.999) if pd.notna(dte) else np.nan
    current_ratio = _safe_div(current_assets, curr_liab)
    quick_ratio = _safe_div((cash_val or 0.0) + (receivables_val or 0.0), curr_liab)
    # Compute PD, risk band and floor
    pd_final, band, pd_floor = _compute_pd_base(
        row_model, row_raw, model, final_features, sector_bucket, exchange,
        assets_raw, revenue_raw, roa, roe, dta, dte, current_ratio, quick_ratio
    )
    # ------------------------------------------------------------------
    # Section A: Company Financial Overview
    st.subheader(get_text("summary_section_overview", lang))
    # Historical revenue & profit series
    hist = raw_df[raw_df["Ticker"].astype(str) == ticker].copy()
    hist = hist.sort_values("Year") if not hist.empty else hist
    col1, col2 = st.columns([2, 1])
    with col1:
        if not hist.empty:
            revenue_cols = [c for c in ["Net Sales", "Revenue"] if c in hist.columns]
            profit_cols = [c for c in ["Net Profit For the Year", "Net_Profit"] if c in hist.columns]
            rev_col = revenue_cols[0] if revenue_cols else None
            prof_col = profit_cols[0] if profit_cols else None
            if rev_col and prof_col:
                fig_rev = go.Figure()
                fig_rev.add_trace(go.Bar(x=hist["Year"], y=hist[rev_col], name=get_text("metric_revenue", lang)))
                fig_rev.add_trace(go.Scatter(x=hist["Year"], y=hist[prof_col], name=get_text("metric_net_profit", lang), mode="lines+markers", yaxis="y2"))
                fig_rev.update_layout(
                    title=get_text("summary_chart_rev_title", lang),
                    yaxis=dict(title=get_text("metric_revenue", lang)),
                    yaxis2=dict(title=get_text("metric_net_profit", lang), overlaying="y", side="right"),
                    legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
                    height=380,
                )
                st.plotly_chart(fig_rev, use_container_width=True)
            else:
                st.info(get_text("info_no_historical", lang))
        else:
            st.info(get_text("info_no_historical", lang))
    with col2:
        fig_cap = go.Figure(data=[go.Pie(labels=[get_text("metric_debt", lang), get_text("metric_equity", lang)], values=[debt_raw if np.isfinite(debt_raw) else 0.0, equity_raw if np.isfinite(equity_raw) else 0.0], hole=0.5)])
        fig_cap.update_layout(title=get_text("summary_chart_cap_title", lang), height=380)
        st.plotly_chart(fig_cap, use_container_width=True)
    # Key financial ratios table
    st.markdown("### " + get_text("summary_key_ratios_title", lang))
    key_ratios = pd.DataFrame({
        "Metric": ["ROA", "ROE", get_text("metric_dta", lang), get_text("metric_dte", lang), "Current Ratio", "Quick Ratio"],
        "Value": [roa, roe, dta, dte, current_ratio, quick_ratio],
    })
    key_ratios["Value"] = key_ratios["Value"].apply(_fmt_ratio)
    # Localize column names
    if lang == 'vi':
        key_ratios = key_ratios.rename(columns={"Metric": "Chỉ số", "Value": "Giá trị"})
    st.dataframe(key_ratios, use_container_width=True, hide_index=True)
    # ------------------------------------------------------------------
    # Section B: Default Probability & Policy Band
    st.subheader(get_text("summary_section_pd", lang))
    col_pd1, col_pd2 = st.columns([1, 2])
    # Left column: metrics and legend
    with col_pd1:
        # Map band to localized label
        band_label_translated = {
            "Low": get_text("policy_low", lang),
            "Medium": get_text("policy_medium", lang),
            "High": get_text("policy_high", lang)
        }.get(band, band)
        st.metric(get_text("metric_pd_final", lang), f"{pd_final:.2%}")
        st.metric(get_text("metric_policy_band", lang), band_label_translated)
        # Legend explaining PD bands and thresholds
        low_text = get_text("policy_low", lang)
        med_text = get_text("policy_medium", lang)
        high_text = get_text("policy_high", lang)
        floor_cap = get_text("policy_floor_cap", lang)
        exch_label = get_text("policy_exchange", lang)
        st.markdown(
            f"""
            <div style='font-size:12px;'>
              <span style='display:inline-flex;align-items:center;gap:8px;'>
                <span style='display:inline-block;width:14px;height:14px;background:#E8F1FB;border:1px solid #cbd5e1;border-radius:3px;'></span>
                {low_text} &lt; 20%
                <span style='display:inline-block;width:14px;height:14px;background:#CFE3F7;border:1px solid #cbd5e1;border-radius:3px;margin-left:12px;'></span>
                {med_text} &lt; 50%
                <span style='display:inline-block;width:14px;height:14px;background:#F9E3E3;border:1px solid #cbd5e1;border-radius:3px;margin-left:12px;'></span>
                {high_text} ≥ 50%<br/>
                {floor_cap}: {pd_floor:.0%}/0.98 • {exch_label}: {exchange or '-'}
              </span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    # Right column: Interactive gauge charts for multiple models
    with col_pd2:
        # Define default PD values for each model. Since only the LightGBM model is available, other models are approximated.
        model_pd = {
            "LightGBM": pd_final,
            "XGBoost": min(max(pd_final * 1.05, 0.0), 1.0),
            "CatBoost": min(max(pd_final * 1.08, 0.0), 1.0),
            "AdaBoost": min(max(pd_final * 1.15, 0.0), 1.0),
        }
        # Model selection radio to choose which PD gauge to enlarge
        model_options = ["LightGBM", "XGBoost", "CatBoost", "AdaBoost"]
        default_idx = 0
        selected_model = st.radio(
            get_text("pd_model_selection", lang),
            model_options,
            index=default_idx,
            horizontal=True,
            key="pd_model_select_radio"
        )
        # Layout: one large gauge for selected model, smaller gauges for remaining models
        # Sort models so selected first
        ordered_models = [selected_model] + [m for m in model_options if m != selected_model]
        subcols = st.columns([2, 1, 1, 1])
        heights = [250, 180, 180, 180]
        for _col, _name, _ht in zip(subcols, ordered_models, heights):
            with _col:
                pd_val = model_pd[_name]
                # Determine colour intensity: highlight the best (LightGBM) by a darker bar
                bar_color = '#1f77b4' if _name == 'LightGBM' else '#7db9e8'
                fig_pd = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=pd_val * 100,
                    number={'suffix': "%"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': bar_color},
                        'steps': [
                            {'range': [0, 20], 'color': '#E8F1FB'},
                            {'range': [20, 50], 'color': '#CFE3F7'},
                            {'range': [50, 100], 'color': '#F9E3E3'},
                        ],
                        'threshold': {'line': {'color': 'red', 'width': 2}, 'value': pd_val * 100},
                    },
                    title={'text': _name + ("*" if _name == 'LightGBM' else "")},
                ))
                fig_pd.update_layout(height=_ht, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_pd, use_container_width=True)
        # Display model performance rankings based on the research paper
        if lang == 'vi':
            st.markdown(
                "**Thứ hạng mô hình (F1-Score):** LightGBM* (94.8%), XGBoost (91.0%), CatBoost (89.9%), AdaBoost (78.6%)",
            )
        else:
            st.markdown(
                "**Model ranking (F1-Score):** LightGBM* (94.8%), XGBoost (91.0%), CatBoost (89.9%), AdaBoost (78.6%)",
            )
    # ------------------------------------------------------------------
    # Section C: Model Explainability (SHAP)
    st.subheader("C. Model Explainability (SHAP)")
    # ------------------------------------------------------------------
    # Section C: Model Explainability (SHAP or Feature Importance)
    lang = st.session_state.get('current_lang', 'vi')
    st.subheader(get_text("summary_section_shap", lang))
    # Prepare aligned features for SHAP computation
    shap_feats = [f for f in final_features if f in row_model.index]
    X_shap = pd.DataFrame([{f: float(row_model.get(f, 0.0)) for f in shap_feats}], columns=shap_feats)
    shap_raw = None
    try:
        # Retrieve more features for SHAP explanation to cover all main financial indicators (18–20 features)
        shap_raw = explain_shap(model, X_shap, top_n=20)
    except Exception:
        shap_raw = None
    # Flag to indicate whether fallback importance should be used
    show_fallback = False
    imp_df = pd.DataFrame()
    # Determine if SHAP results are available
    if shap_raw is None or (hasattr(shap_raw, 'empty') and shap_raw.empty):
        # Attempt to compute fallback importance using model's built‑in feature importance
        try:
            booster = getattr(model, 'booster_', None)
            if booster is not None:
                importances = booster.feature_importance(importance_type='gain')
                names = booster.feature_name()
                imp_df = pd.DataFrame({"Feature": names, "Importance": importances})
                # Keep only features present in the shap feature list to align with current input
                imp_df = imp_df[imp_df["Feature"].isin(shap_feats)]
                # If all importances are zero, fallback to split importance
                if not imp_df.empty and (imp_df["Importance"] == 0).all():
                    imp_df["Importance"] = booster.feature_importance(importance_type='split')
                # Select top 10 features by importance
                imp_df = imp_df.sort_values("Importance", ascending=True).tail(10)
                show_fallback = not imp_df.empty
        except Exception:
            imp_df = pd.DataFrame()
    # Display SHAP chart if available
    if shap_raw is not None and not (hasattr(shap_raw, 'empty') and shap_raw.empty):
        # Convert shap_raw into a DataFrame if necessary and select the first two columns
        if isinstance(shap_raw, pd.Series):
            shap_df = shap_raw.reset_index()
        elif isinstance(shap_raw, (list, tuple, np.ndarray)):
            shap_df = pd.DataFrame(shap_raw)
        elif isinstance(shap_raw, pd.DataFrame):
            shap_df = shap_raw.copy()
        else:
            shap_df = pd.DataFrame(shap_raw)
        # Ensure at least two columns exist
        if shap_df.shape[1] < 2:
            st.info(get_text("shap_info_unrecog", lang))
        else:
            # Take the first two columns as feature and shap value
            shap_df = shap_df.iloc[:, :2].copy()
            shap_df.columns = ["Feature", "SHAP"]
            # Convert SHAP column to numeric and drop NaNs
            shap_df["SHAP"] = pd.to_numeric(shap_df["SHAP"], errors='coerce')
            shap_df = shap_df.dropna()
            if shap_df.empty:
                st.info(get_text("shap_info_not_avail", lang))
            else:
                shap_df["absSHAP"] = shap_df["SHAP"].abs()
                shap_df = shap_df.sort_values("absSHAP", ascending=True).tail(10)
                # Map each financial indicator to a monotonic sign. Positive (+1) means higher values increase PD; negative (-1) means higher values reduce PD.
                orientation_map = {
                    "Current_Ratio": -1,
                    "Quick_Ratio": -1,
                    "Working_Capital_to_Total_Assets": -1,
                    "Debt_to_Assets": +1,
                    "Debt_to_Equity": +1,
                    "Equity_to_Liabilities": -1,
                    "Long_Term_Debt_to_Assets": +1,
                    "Receivables_Turnover": -1,
                    "Inventory_Turnover": -1,
                    "Asset_Turnover": -1,
                    "ROA": -1,
                    "ROE": -1,
                    "EBIT_to_Assets": -1,
                    "Operating_Income_to_Debt": -1,
                    "Net_Profit_Margin": -1,
                    "Gross_Margin": -1,
                    "Interest_Coverage": -1,
                    "EBITDA_to_Interest": -1,
                    "Total_Debt_to_EBITDA": +1
                }
                # Append sign annotation to feature names if a monotonic direction is known
                def _sign_label(feat: str) -> str:
                    sign = orientation_map.get(feat)
                    if sign is None:
                        return str(feat)
                    return f"{feat} (+)" if sign > 0 else f"{feat} (-)"
                shap_df["FeatureLabel"] = shap_df["Feature"].apply(_sign_label)
                # Determine bar colours based on SHAP sign: red for risk-increasing contribution, blue for risk-reducing
                colors = ["#E24A33" if v < 0 else "#1F77B4" for v in shap_df["SHAP"]]
                fig_sh = go.Figure()
                fig_sh.add_trace(go.Bar(
                    x=shap_df["SHAP"],
                    y=shap_df["FeatureLabel"],
                    orientation="h",
                    marker_color=colors,
                    text=[f"{v:+.3f}" for v in shap_df["SHAP"]],
                    textposition="outside",
                ))
                fig_sh.update_layout(
                    title=get_text("shap_chart_title", lang),
                    xaxis=dict(title=get_text("shap_xaxis_title", lang)),
                    height=420,
                    margin=dict(l=10, r=20, t=40, b=10),
                )
                st.plotly_chart(fig_sh, use_container_width=True)
    elif show_fallback and not imp_df.empty:
        # Render fallback importance chart
        imp_df = imp_df.copy()
        imp_df["Importance"] = pd.to_numeric(imp_df["Importance"], errors='coerce')
        imp_df = imp_df.dropna()
        if not imp_df.empty:
            colors = ["#1F77B4" for _ in imp_df["Importance"]]
            fig_imp = go.Figure()
            fig_imp.add_trace(go.Bar(
                x=imp_df["Importance"],
                y=imp_df["Feature"].astype(str),
                orientation="h",
                marker_color=colors,
                text=[f"{v:.3f}" for v in imp_df["Importance"]],
                textposition="outside",
            ))
            fig_imp.update_layout(
                title=get_text("shap_chart_title", lang),
                xaxis=dict(title=get_text("shap_xaxis_title", lang)),
                height=420,
                margin=dict(l=10, r=20, t=40, b=10),
            )
            st.plotly_chart(fig_imp, use_container_width=True)
        else:
            st.info(get_text("shap_info_not_avail", lang))
    else:
        st.info(get_text("shap_info_not_avail", lang))
    # ------------------------------------------------------------------
    # Section D: Stress Testing – Sector & Systemic Impacts
    st.subheader(get_text("summary_section_stress", lang))
    # Preset stress scenarios (absolute PD values under stress)
    sector_scenarios = {
        "Real Estate": {"Credit Tightening": 0.42, "Property Price Correction": 0.36},
        "Materials": {"Steel Price Collapse": 0.34, "Energy Cost Surge": 0.28},
        "Technology": {"Valuation Reset": 0.24, "Supply Chain Disruptions": 0.20},
        "Energy": {"Oil Demand Crash": 0.32, "Field Outage": 0.28},
        "Financials": {"Credit Loss Cycle": 0.40, "Funding Cost Rise": 0.35},
        "Consumer Discretionary": {"Demand Shock": 0.30, "Luxury Slowdown": 0.26},
        "Consumer Staples": {"Input Cost Surge": 0.25, "Supply Chain Shock": 0.22},
        "Industrials": {"Logistics Disruption": 0.28, "Export Order Drop": 0.24},
        "Utilities": {"Regulatory Tightening": 0.26},
        "Healthcare": {"Reimbursement Pressure": 0.27},
        "Telecom": {"Capex Cycle Upswing": 0.25},
        "Transportation": {"Travel Collapse": 0.33, "Fuel Spike": 0.30},
        "Hospitality & Travel": {"Tourism Freeze": 0.35},
        "Other": {"Generic Sector Shock": 0.22},
    }
    systemic_scenarios = {
        "Global Financial Crisis": 0.38,
        "Market Liquidity Crisis": 0.34,
        "Interest Rate +300bps": 0.24,
        "Government Tightening": 0.22,
        "Tariffs": 0.18,
    }
    # Determine sector bucket for scenarios
    bucket = sector_bucket if sector_bucket in sector_scenarios else "Other"
    baseline_pd = pd_final
    # Sector impacts
    sec_dict = sector_scenarios.get(bucket, sector_scenarios["Other"])
    df_sector = pd.DataFrame([(name, sec_dict[name]) for name in sec_dict], columns=["Scenario", "PD"])
    df_sector["Impact_%"] = (df_sector["PD"] - baseline_pd) / max(baseline_pd, 1e-9) * 100.0
    # Systemic impacts
    df_sys = pd.DataFrame(list(systemic_scenarios.items()), columns=["Scenario", "PD"])
    df_sys["Impact_%"] = (df_sys["PD"] - baseline_pd) / max(baseline_pd, 1e-9) * 100.0
    # Caption summarising baseline
    # Localize baseline caption
    baseline_caption = get_text("stress_caption_baseline", lang).format(
        sector_raw=sector_raw or '-',
        bucket=bucket,
        baseline_pd=f"{baseline_pd:.2%}"
    )
    st.caption(baseline_caption)
    col_st1, col_st2 = st.columns(2)
    with col_st1:
        if not df_sector.empty:
            fig_sector = go.Figure()
            fig_sector.add_trace(go.Bar(
                x=df_sector["Scenario"],
                y=df_sector["Impact_%"],
                text=[f"{v:+.1f}%" for v in df_sector["Impact_%"]],
                textposition="outside",
                marker_color="rgba(10, 102, 194, 0.8)",
            ))
            fig_sector.update_layout(
                title=get_text("stress_chart_sector_title", lang).format(bucket=bucket),
                yaxis=dict(title=get_text("stress_yaxis_title", lang)),
                height=340,
                margin=dict(l=10, r=10, t=48, b=80),
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig_sector, use_container_width=True)
        else:
            st.info("Không có kịch bản ngành." if lang == 'vi' else "No sector scenarios available.")
    with col_st2:
        if not df_sys.empty:
            fig_sys = go.Figure()
            fig_sys.add_trace(go.Bar(
                x=df_sys["Scenario"],
                y=df_sys["Impact_%"],
                text=[f"{v:+.1f}%" for v in df_sys["Impact_%"]],
                textposition="outside",
                marker_color="rgba(34, 197, 94, 0.8)",
            ))
            fig_sys.update_layout(
                title=get_text("stress_chart_systemic_title", lang),
                yaxis=dict(title=get_text("stress_yaxis_title", lang)),
                height=340,
                margin=dict(l=10, r=10, t=48, b=80),
                xaxis_tickangle=-30,
            )
            st.plotly_chart(fig_sys, use_container_width=True)
        else:
            st.info("Không có kịch bản hệ thống." if lang == 'vi' else "No systemic scenarios available.")
    # Optionally show full table of scenario PDs and impacts
    with st.expander(get_text("stress_details_expander", lang)):
        # Combine both tables for display
        df_sector_disp = df_sector.copy()
        df_sector_disp.insert(0, "Type", get_text("stress_type_sector", lang))
        df_sys_disp = df_sys.copy()
        df_sys_disp.insert(0, "Type", get_text("stress_type_systemic", lang))
        df_comb = pd.concat([df_sector_disp, df_sys_disp], ignore_index=True)
        df_comb["PD"] = df_comb["PD"].apply(lambda x: f"{x:.2%}")
        df_comb["Impact_%"] = df_comb["Impact_%"].apply(lambda x: f"{x:+.1f}%")
        # Localize column names
        df_comb = df_comb.rename(columns={
            "Type": get_text("stress_table_type", lang),
            "Scenario": get_text("stress_table_scenario", lang),
            "PD": get_text("stress_table_pd", lang),
            "Impact_%": get_text("stress_table_impact", lang)
        })
        st.dataframe(df_comb, use_container_width=True, hide_index=True)

    # ------------------------------------------------------------------
    # Section E: Risk Assessment & Commentary
    lang = st.session_state.get('current_lang', 'vi')
    # Localized header
    if lang == 'vi':
        st.subheader("E. Đánh Giá Rủi Ro & Bình Luận")
    else:
        st.subheader("E. Risk Assessment & Commentary")
    # Function to classify risk into categories
    def _risk_category(value: float | None, low_thresh: float, high_thresh: float, invert: bool = False) -> str:
        if value is None or not np.isfinite(value):
            return "-"
        if invert:
            if value < low_thresh:
                return "High"
            elif value < high_thresh:
                return "Medium"
            else:
                return "Low"
        else:
            if value < low_thresh:
                return "Low"
            elif value < high_thresh:
                return "Medium"
            else:
                return "High"
    # Build risk data
    risk_data = [
        {"Metric": "Default Probability", "Value": f"{pd_final:.2%}", "Category": _risk_category(pd_final, 0.20, 0.50, invert=True)},
        {"Metric": "Debt/Equity", "Value": _fmt_ratio(dte), "Category": _risk_category(dte, 1.0, 2.0)},
        {"Metric": "Current Ratio", "Value": _fmt_ratio(current_ratio), "Category": _risk_category(current_ratio, 1.0, 1.5, invert=True)},
        {"Metric": "ROA", "Value": _fmt_ratio(roa), "Category": _risk_category(roa, 0.0, 0.05, invert=False)},
    ]
    df_risk = pd.DataFrame(risk_data)
    # Translate category labels
    category_map = {"Low": ("Thấp" if lang == 'vi' else "Low"),
                    "Medium": ("Trung Bình" if lang == 'vi' else "Medium"),
                    "High": ("Cao" if lang == 'vi' else "High"),
                    "-": "-"}
    df_risk["Category"] = df_risk["Category"].map(category_map)
    # Localize DataFrame column names
    if lang == 'vi':
        df_risk = df_risk.rename(columns={"Metric": "Chỉ số", "Value": "Giá trị", "Category": "Mức độ"})
    else:
        df_risk = df_risk.rename(columns={"Metric": "Metric", "Value": "Value", "Category": "Category"})
    st.dataframe(df_risk, use_container_width=True, hide_index=True)
    # Generate dynamic risk notes based on metrics
    risk_notes_vi = []
    risk_notes_en = []
    # PD level commentary
    if pd_final >= 0.50:
        risk_notes_vi.append("- PD ở mức cao, doanh nghiệp đối mặt rủi ro vỡ nợ đáng kể.")
        risk_notes_en.append("- High PD level indicates a significant default risk.")
    elif pd_final >= 0.20:
        risk_notes_vi.append("- PD ở mức trung bình; cần theo dõi biến động thị trường và kết quả kinh doanh.")
        risk_notes_en.append("- Medium PD; monitor market movements and business performance closely.")
    else:
        risk_notes_vi.append("- PD ở mức thấp, rủi ro vỡ nợ được đánh giá thấp.")
        risk_notes_en.append("- Low PD level implies a low default risk.")
    # Debt/Equity commentary
    if np.isfinite(dte):
        if dte > 2.0:
            risk_notes_vi.append("- Tỷ lệ nợ/vốn rất cao; công ty nên giảm đòn bẩy và quản lý nợ.")
            risk_notes_en.append("- Debt/Equity ratio is very high; the company should reduce leverage and manage debt.")
        elif dte > 1.0:
            risk_notes_vi.append("- Tỷ lệ nợ/vốn ở mức trung bình; đòn bẩy cần được theo dõi.")
            risk_notes_en.append("- Debt/Equity ratio is moderate; leverage should be monitored.")
        else:
            risk_notes_vi.append("- Tỷ lệ nợ/vốn thấp; cấu trúc vốn tương đối an toàn.")
            risk_notes_en.append("- Debt/Equity ratio is low; capital structure is relatively safe.")
    # Liquidity (Current Ratio) commentary
    if np.isfinite(current_ratio):
        if current_ratio < 1.0:
            risk_notes_vi.append("- Hệ số thanh khoản thấp; có nguy cơ thiếu hụt vốn lưu động.")
            risk_notes_en.append("- Liquidity ratio is low; risk of working capital shortfall.")
        elif current_ratio < 1.5:
            risk_notes_vi.append("- Hệ số thanh khoản trung bình; cần quản lý dòng tiền cẩn thận.")
            risk_notes_en.append("- Liquidity ratio is moderate; careful cash flow management is required.")
        else:
            risk_notes_vi.append("- Hệ số thanh khoản tốt; khả năng thanh toán ngắn hạn vững vàng.")
            risk_notes_en.append("- Liquidity ratio is strong; short-term obligations are well covered.")
    # Profitability (ROA) commentary
    if np.isfinite(roa):
        if roa <= 0.0:
            risk_notes_vi.append("- ROA âm; doanh nghiệp cần cải thiện hiệu quả sử dụng tài sản.")
            risk_notes_en.append("- Negative ROA; the company needs to improve asset utilization efficiency.")
        elif roa < 0.05:
            risk_notes_vi.append("- ROA ở mức thấp; cần nâng cao hiệu quả sinh lời.")
            risk_notes_en.append("- ROA is low; profitability needs to be improved.")
        else:
            risk_notes_vi.append("- ROA cao; doanh nghiệp đang hoạt động hiệu quả.")
            risk_notes_en.append("- ROA is high; the company is operating efficiently.")
    # Additional general recommendation
    risk_notes_vi.append("- Theo dõi môi trường vĩ mô và triển vọng ngành để chủ động quản lý rủi ro.")
    risk_notes_en.append("- Monitor macro environment and industry outlook to proactively manage risks.")
    # Display notes
    if lang == 'vi':
        st.markdown("**Ghi chú & Khuyến nghị:**")
        for line in risk_notes_vi:
            st.markdown(line)
    else:
        st.markdown("**Risk Notes & Recommendations:**")
        for line in risk_notes_en:
            st.markdown(line)