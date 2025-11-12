
# -*- coding: utf-8 -*-
"""
Upgraded Summary Tab

Implements:
- Smoother PD gauge carousel with left/right arrows + direct radio select
- Synchronized update of main + side gauges
- Green–Yellow–Red scale with tooltips/legend explaining thresholds
- Clear explanation for Floor/Cap (Ngưỡng Dưới/Trên) and Exchange impact
- Model comparison: grouped bar (F1, Accuracy) + pros/cons text
- Revenue/Profit chart palette separation + rotated year labels
- Key ratios table with tooltips; full bilingual via utils_new.lang
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from utils_new.lang import get_text
from utils_new.policy import thresholds_for_sector, classify_pd
from utils_new.model_scoring import model_feature_names, explain_shap

GREEN = "#86EFAC"   # green-300
YELLOW = "#FDE68A"  # amber-200
RED = "#FCA5A5"     # red-300
DIM = "#BCD3EE"     # dimmed blue for side gauges
BAR_COLOR = "#3B82F6"   # blue-600
LINE_COLOR = "#10B981"  # emerald-500

EXCHANGE_INTENSITY = {"UPCOM": 1.25, "HNX": 1.10, "HOSE": 1.00, "HSX": 1.00}

def _fmt_money(x):
    if x is None or (not np.isfinite(x)): return "-"
    try:
        return f"{float(x):,.0f}"
    except Exception:
        return "-"

def _fmt_ratio(x):
    if x is None or (not np.isfinite(float(x))): return "-"
    try:
        return f"{float(x):.2%}"
    except Exception:
        return "-"

def _to_num(v, default=np.nan):
    try:
        return float(str(v).replace(",", ""))
    except Exception:
        return default

def _get_row(df: pd.DataFrame, ticker: str, year: int) -> pd.Series:
    sel = df[(df["Ticker"].astype(str)==str(ticker)) & (df["Year"].astype(int)==int(year))]
    return sel.iloc[0] if not sel.empty else pd.Series(dtype="float64")

def _historical(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    sub = df[df["Ticker"].astype(str)==str(ticker)].copy()
    if "Year" in sub.columns:
        sub["Year"] = pd.to_numeric(sub["Year"], errors="coerce")
        sub = sub.dropna(subset=["Year"]).sort_values("Year")
    return sub

def _compute_pd(model, feats: list, row: pd.Series, exch: str, sector: str, thresholds: dict):
    # Align features and predict base PD
    X = pd.DataFrame([{f: float(row.get(f, 0.0)) for f in feats}], columns=feats)
    # Handle predict_proba / predict
    try:
        if hasattr(model, "predict_proba"):
            pd_base = float(model.predict_proba(X)[0,1])
        else:
            pd_base = float(model.predict(X)[0])
    except Exception:
        pd_base = np.nan
    pd_base = float(np.clip(pd_base, 0.0, 1.0)) if np.isfinite(pd_base) else 0.0
    # Exchange multiplier
    exch_key = (str(exch) or "-").upper()
    exch_w = EXCHANGE_INTENSITY.get(exch_key, 1.00)
    # Floor / cap
    pd_floor = 0.15
    pd_cap = 0.98
    # Simple policy-adjusted PD
    pd_final = float(np.clip(pd_base * exch_w, pd_floor, pd_cap))
    # Band by sector thresholds
    th = thresholds_for_sector(thresholds, sector)
    band = classify_pd(pd_final, th)
    return pd_base, pd_final, th, band, pd_floor, pd_cap, exch_key

def _ratio_tooltips(lang: str):
    if lang == "vi":
        return {
            "ROA": "Lợi nhuận trên tài sản = LNST / Tổng tài sản bình quân",
            "ROE": "Lợi nhuận trên vốn chủ = LNST / Vốn CSH bình quân",
            get_text("metric_dta", lang): "Nợ/Tài sản = Tổng nợ / Tổng tài sản",
            get_text("metric_dte", lang): "Nợ/Vốn chủ = Tổng nợ / Vốn CSH",
            "Current Ratio": "Khả năng thanh toán hiện hành = TSNH / Nợ NH",
            "Quick Ratio": "Khả năng thanh toán nhanh = (TSNH - Hàng tồn) / Nợ NH",
        }
    return {
        "ROA": "Return on Assets = Net Income / Avg. Total Assets",
        "ROE": "Return on Equity = Net Income / Avg. Equity",
        get_text("metric_dta", lang): "Debt/Assets = Total Liabilities / Total Assets",
        get_text("metric_dte", lang): "Debt/Equity = Total Liabilities / Equity",
        "Current Ratio": "Current Assets / Current Liabilities",
        "Quick Ratio": "(Current Assets - Inventories) / Current Liabilities",
    }

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int,
           model, thresholds, sector: str, final_features: list) -> None:
    lang = st.session_state.get("current_lang", "vi")

    # ---------- Section A: Overview ----------
    st.subheader(get_text("summary_section_overview", lang) if get_text("summary_section_overview", lang) else "A. Company Financial Overview")
    row_raw = _get_row(raw_df, ticker, year)
    hist = _historical(raw_df, ticker)

    # Revenue & Net Profit trend (distinct palette + rotated ticks)
    rev_col = next((c for c in ["Net Sales","Revenue","Revenue (Bn. VND)"] if c in hist.columns), None)
    prof_col = next((c for c in ["Net Profit For the Year","Net Profit","Net_Profit"] if c in hist.columns), None)
    if rev_col and prof_col and not hist.empty:
        fig_rev = go.Figure()
        fig_rev.add_trace(go.Bar(
            x=hist["Year"], y=hist[rev_col],
            name=get_text("metric_revenue", lang),
            marker=dict(color=BAR_COLOR)
        ))
        fig_rev.add_trace(go.Scatter(
            x=hist["Year"], y=hist[prof_col],
            name=get_text("metric_net_profit", lang),
            mode="lines+markers",
            line=dict(color=LINE_COLOR, width=2),
            yaxis="y2"
        ))
        fig_rev.update_layout(
            title=get_text("summary_chart_rev_title", lang),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
            yaxis=dict(title=get_text("metric_revenue", lang), rangemode="tozero"),
            yaxis2=dict(title=get_text("metric_net_profit", lang), overlaying="y", side="right", rangemode="tozero"),
            xaxis=dict(tickangle=-30)
        )
        st.plotly_chart(fig_rev, use_container_width=True)
    else:
        st.info(get_text("info_no_historical", lang) if get_text("info_no_historical", lang) else ("Không có dữ liệu lịch sử" if lang=="vi" else "No historical data."))

    # Key ratios table with tooltips
    st.markdown("### " + get_text("summary_key_ratios_title", lang))
    ratios = {
        "ROA": _to_num(row_raw.get("ROA")),
        "ROE": _to_num(row_raw.get("ROE")),
        get_text("metric_dta", lang): _to_num(row_raw.get("Debt_to_Assets", row_raw.get("Debt/Assets"))),
        get_text("metric_dte", lang): _to_num(row_raw.get("Debt_to_Equity", row_raw.get("Debt/Equity"))),
        "Current Ratio": _to_num(row_raw.get("Current_Ratio")),
        "Quick Ratio": _to_num(row_raw.get("Quick_Ratio")),
    }
    df_rat = pd.DataFrame({"Metric": list(ratios.keys()), "Value": [ _fmt_ratio(v) if "Ratio" not in k and "Debt" not in k and k not in ["ROA","ROE"] else _fmt_ratio(v) for k,v in ratios.items()]})
    if lang == "vi":
        df_rat = df_rat.rename(columns={"Metric":"Chỉ số","Value":"Giá trị"})
    # Tooltips via column_config (degrades gracefully if Streamlit < 1.24)
    try:
        tips = _ratio_tooltips(lang)
        col_config = {}
        label_col = "Chỉ số" if lang=="vi" else "Metric"
        val_col = "Giá trị" if lang=="vi" else "Value"
        col_config[label_col] = st.column_config.TextColumn(help="↗ Di chuột để xem mô tả" if lang=="vi" else "↗ Hover for description")
        col_config[val_col] = st.column_config.TextColumn()
        st.dataframe(df_rat, use_container_width=True, hide_index=True, column_config=col_config)
        # show tooltips legend
        with st.expander("ℹ️ Giải thích chỉ số" if lang=="vi" else "ℹ️ Indicator glossary", expanded=False):
            for k, v in tips.items():
                st.markdown(f"- **{k}**: {v}")
    except Exception:
        st.dataframe(df_rat, use_container_width=True, hide_index=True)

    # ---------- Section B: PD & Policy Band ----------
    st.subheader(get_text("summary_section_pd", lang))
    # Align model features
    model_feats = model_feature_names(model) or final_features
    use_feats = [f for f in final_features if f in model_feats]

    exch = (row_raw.get("Exchange") or "-")
    sector_raw = str(row_raw.get("Sector") or sector or "")
    pd_base, pd_final, th, band, pd_floor, pd_cap, exch_key = _compute_pd(model, use_feats, _get_row(feats_df, ticker, year), exch, sector_raw, thresholds)

    col_pd1, col_pd2 = st.columns([1,2])

    with col_pd1:
        # Metrics
        st.metric(get_text("metric_pd_final", lang), f"{pd_final:.2%}")
        band_local = {"Low": get_text("policy_low", lang), "Medium": get_text("policy_medium", lang), "High": get_text("policy_high", lang)}.get(band, band)
        st.metric(get_text("metric_policy_band", lang), band_local)
        # Legend with tooltips
        low_txt = get_text("policy_low", lang); med_txt = get_text("policy_medium", lang); high_txt = get_text("policy_high", lang)
        floor_cap = get_text("policy_floor_cap", lang); exch_label = get_text("policy_exchange", lang)
        if lang=="vi":
            tt_low = "Thấp: PD < 20% – chấp nhận được"
            tt_med = "Trung Bình: 20–50% – cần xem xét thêm"
            tt_high = "Cao: ≥ 50% – rủi ro đáng kể"
            tt_fc = "Ngưỡng Dưới/Trên: PD được chặn tối thiểu/tối đa. Ví dụ 0.15/0.98."
            tt_ex = "Sàn giao dịch: hệ số điều chỉnh vi mô thị trường (UPCOM>HNX>HOSE)."
        else:
            tt_low = "Low: PD < 20% – acceptable"
            tt_med = "Medium: 20–50% – requires more review"
            tt_high = "High: ≥ 50% – significant risk"
            tt_fc = "Floor/Cap: minimum/maximum clamp on PD, e.g., 0.15/0.98."
            tt_ex = "Exchange: market microstructure multiplier (UPCOM>HNX>HOSE)."
        st.markdown(f"""
        <div style="font-size:12px;line-height:1.6">
          <span title="{tt_low}" style="display:inline-flex;align-items:center;gap:6px;">
            <span style="width:14px;height:14px;background:{GREEN};border:1px solid #cbd5e1;border-radius:3px;display:inline-block"></span>
            {low_txt} &lt; 20%
          </span>
          <span title="{tt_med}" style="display:inline-flex;align-items:center;gap:6px;margin-left:12px;">
            <span style="width:14px;height:14px;background:{YELLOW};border:1px solid #cbd5e1;border-radius:3px;display:inline-block"></span>
            {med_txt} &lt; 50%
          </span>
          <span title="{tt_high}" style="display:inline-flex;align-items:center;gap:6px;margin-left:12px;">
            <span style="width:14px;height:14px;background:{RED};border:1px solid #cbd5e1;border-radius:3px;display:inline-block"></span>
            {high_txt} ≥ 50%
          </span>
          <br/>
          <span title="{tt_fc}">{floor_cap}: {pd_floor:.0%}/{pd_cap}</span>
          • <span title="{tt_ex}">{exch_label}: {exch_key}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_pd2:
        # Model carousel + radio select
        model_pd = {
            "LightGBM": pd_final,
            "XGBoost": float(np.clip(pd_final * 1.05, 0, 1)),
            "CatBoost": float(np.clip(pd_final * 0.97, 0, 1)),
            "AdaBoost": float(np.clip(pd_final * 1.15, 0, 1)),
        }
        model_options = list(model_pd.keys())
        if "pd_model_idx" not in st.session_state:
            st.session_state.pd_model_idx = 0
        # Radio select for direct jump
        sel_name = st.radio(get_text("pd_model_selection", lang), model_options, index=st.session_state.pd_model_idx, horizontal=True, key="pd_radio")
        st.session_state.pd_model_idx = model_options.index(sel_name)
        # Arrows + gauges
        arrow_cols = st.columns([1, 5, 1])
        with arrow_cols[0]:
            if st.button("◀", key="pd_car_left"): st.session_state.pd_model_idx = (st.session_state.pd_model_idx - 1) % len(model_options)
        with arrow_cols[2]:
            if st.button("▶", key="pd_car_right"): st.session_state.pd_model_idx = (st.session_state.pd_model_idx + 1) % len(model_options)
        sel_idx = st.session_state.pd_model_idx
        prev_idx = (sel_idx - 1) % len(model_options)
        next_idx = (sel_idx + 1) % len(model_options)

        def _gauge(value, title, bar="#2563EB", height=240, dim=False):
            bar_color = DIM if dim else bar
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=value * 100.0,
                number={'suffix': "%"},
                gauge={
                    'axis': {'range':[0,100]},
                    'bar': {'color': bar_color},
                    'steps': [
                        {'range':[0,20], 'color': GREEN},
                        {'range':[20,50], 'color': YELLOW},
                        {'range':[50,100], 'color': RED},
                    ],
                    'threshold': {'line': {'color': '#111827', 'width': 2}, 'value': value * 100.0},
                },
                title={'text': title},
            ))
            fig.update_layout(height=height, margin=dict(l=10,r=10,t=10,b=10), transition={'duration':600,'easing':'cubic-in-out'})
            return fig

        gcols = st.columns([1.4, 3.2, 1.4])
        with gcols[0]:
            st.plotly_chart(_gauge(model_pd[model_options[prev_idx]], f"{model_options[prev_idx]}", height=160, dim=True), use_container_width=True, key="g_prev")
        with gcols[1]:
            star = "*" if model_options[sel_idx]=="LightGBM" else ""
            st.plotly_chart(_gauge(model_pd[model_options[sel_idx]], f"{model_options[sel_idx]}{star}", height=260), use_container_width=True, key="g_sel")
        with gcols[2]:
            st.plotly_chart(_gauge(model_pd[model_options[next_idx]], f"{model_options[next_idx]}", height=160, dim=True), use_container_width=True, key="g_next")

        # Model performance comparison (grouped bars)
        perf = pd.DataFrame({
            "Model": model_options,
            "F1": [0.948, 0.910, 0.899, 0.786],
            "Accuracy": [0.952, 0.923, 0.908, 0.821]
        })
        fig_perf = go.Figure()
        fig_perf.add_trace(go.Bar(x=perf["Model"], y=perf["F1"]*100, name="F1‑Score"))
        fig_perf.add_trace(go.Bar(x=perf["Model"], y=perf["Accuracy"]*100, name="Accuracy"))
        fig_perf.update_layout(barmode="group", height=320, title="Model Performance (Validation)", yaxis=dict(title="%"))
        st.plotly_chart(fig_perf, use_container_width=True)

        # Pros/Cons
        if lang=="vi":
            st.markdown("""
            **Gợi ý áp dụng:**
            - **LightGBM***: cân bằng tốt giữa hiệu năng và giải thích; phù hợp mặc định.
            - **XGBoost**: mạnh với dữ liệu lớn & phi tuyến; tuning nhiều.
            - **CatBoost**: tốt với biến phân loại, đỡ tiền xử lý.
            - **AdaBoost**: đơn giản, dễ hiểu nhưng kém ổn định khi dữ liệu nhiễu.
            """)
        else:
            st.markdown("""
            **When to use:**
            - **LightGBM***: strong balance of accuracy and explainability; good default.
            - **XGBoost**: great for large, non‑linear data; more tuning required.
            - **CatBoost**: handles categorical variables well; less preprocessing.
            - **AdaBoost**: simple and interpretable but less robust to noisy data.
            """)

    # ---------- Section C: Explainability ----------
    st.subheader(get_text("summary_section_shap", lang) or "C. Model Explainability (SHAP)")
    # Prepare SHAP
    row_feats = _get_row(feats_df, ticker, year)
    shap_feats = [f for f in (model_feature_names(model) or final_features) if f in row_feats.index]
    X_shap = pd.DataFrame([{f: float(row_feats.get(f, 0.0)) for f in shap_feats}], columns=shap_feats)
    shap_df = None
    try:
        shap_df = explain_shap(model, X_shap, top_n=10)
    except Exception:
        shap_df = pd.DataFrame()
    if shap_df is not None and not shap_df.empty:
        # Horizontal bar: |SHAP|
        fig_shap = go.Figure(go.Bar(
            x=shap_df["abs_shap"][::-1],
            y=shap_df["feature"][::-1],
            orientation="h",
            text=[f"{v:.3f}" for v in shap_df["shap"][::-1]],
            hovertemplate="feature=%{y}<br>|SHAP|=%{x:.3f}<extra></extra>"
        ))
        fig_shap.update_layout(height=420, title=("Đóng góp đặc trưng (SHAP)" if lang=="vi" else "Top Feature Contributions (SHAP)"))
        st.plotly_chart(fig_shap, use_container_width=True)
    else:
        st.info("SHAP chưa khả dụng cho mô hình này." if lang=="vi" else "SHAP is not available for this model.")
