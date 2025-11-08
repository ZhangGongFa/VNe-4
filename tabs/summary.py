"""
Summary Tab - Integrated with original design and multilingual support
Displays comprehensive financial overview, PD, SHAP, and stress testing
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils_new.lang import get_text

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, 
           model, thresholds, sector: str, final_features: list):
    """
    Render the Summary tab with integrated design from original app.py
    """
    lang = st.session_state.get('current_lang', 'vi')
    
    st.subheader(get_text("summary_header", lang))
    
    # Get selected data
    row_model = feats_df[(feats_df["Ticker"].astype(str)==ticker) & (feats_df["Year"]==year)]
    if row_model.empty:
        st.warning(get_text("warning_no_data", lang))
        return
    row_model = row_model.iloc[0]
    
    row_raw = raw_df[(raw_df["Ticker"].astype(str)==ticker) & (raw_df["Year"]==year)]
    row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype="object")
    
    def safe_get(col_names, default=np.nan):
        """Get value safely from row"""
        for c in col_names:
            if c in row_raw.index:
                try:
                    return float(row_raw[c])
                except:
                    pass
        return default
    
    def fmt_ratio(x):
        """Format as percentage"""
        if (x is None) or (not np.isfinite(x)): return "-"
        return f"{x:.2%}" if -1.5 <= float(x) <= 1.5 else f"{x:,.4f}"
    
    def fmt_money(x):
        """Format as currency"""
        return "-" if (x is None or not np.isfinite(x)) else f"{x:,.2f}"
    
    def safe_div(a, b):
        try:
            return (float(a) / float(b)) if (b not in [0, None, np.nan] and float(b)!=0.0) else np.nan
        except:
            return np.nan
    
    # Extract metrics
    assets = safe_get(["TOTAL ASSETS (Bn. VND)","Total_Assets"])
    equity = safe_get(["OWNER'S EQUITY(Bn.VND)","Equity"])
    curr_liab = safe_get(["Current liabilities (Bn. VND)","Current_Liabilities"], 0.0)
    long_liab = safe_get(["Long-term liabilities (Bn. VND)","Long_Term_Liabilities"], 0.0)
    short_bor = safe_get(["Short-term borrowings (Bn. VND)","Short_Term_Borrowings"], 0.0)
    
    revenue = safe_get(["Net Sales","Revenue"])
    net_profit = safe_get(["Net Profit For the Year","Net_Profit"])
    cash = safe_get(["Cash and cash equivalents (Bn. VND)","Cash"], 0.0)
    receivables = safe_get(["Accounts receivable (Bn. VND)","Receivables"], 0.0)
    current_assets = safe_get(["CURRENT ASSETS (Bn. VND)","Current_Assets"], 0.0)
    
    total_liab = (curr_liab or 0.0) + (long_liab or 0.0)
    debt = (short_bor or 0.0) + (long_liab or 0.0)
    
    roa = safe_div(net_profit, assets)
    roe = safe_div(net_profit, equity)
    dta = safe_div(total_liab, assets)
    dte = safe_div(debt, equity)
    current_ratio = safe_div(current_assets, curr_liab)
    quick_ratio = safe_div((cash or 0.0) + (receivables or 0.0), curr_liab)
    
    # ==================== SECTION A: COMPANY FINANCIAL OVERVIEW ====================
    st.subheader(get_text("summary_section_overview", lang))
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Revenue & Net Profit trend
        hist = raw_df[raw_df["Ticker"].astype(str)==ticker].sort_values("Year")
        if not hist.empty:
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(
                x=hist["Year"], y=hist.get("Net Sales", []), 
                name=get_text("metric_revenue", lang),
                marker_color="rgba(10, 102, 194, 0.8)",
                key="summary_rev_bar"
            ))
            fig_rev.add_trace(go.Scatter(
                x=hist["Year"], y=hist.get("Net Profit For the Year", []),
                name=get_text("metric_net_profit", lang),
                mode="lines+markers",
                yaxis="y2",
                line=dict(color="rgba(34, 197, 94, 0.8)", width=3),
                marker=dict(size=8),
                key="summary_profit_line"
            ))
            fig_rev.update_layout(
                title=get_text("summary_chart_rev_title", lang),
                yaxis=dict(title=get_text("metric_revenue", lang)),
                yaxis2=dict(title=get_text("metric_net_profit", lang), overlaying="y", side="right"),
                hovermode="x unified",
                height=350,
                key="summary_rev_chart"
            )
            st.plotly_chart(fig_rev, use_container_width=True, key="summary_rev_chart_key")
        else:
            st.info(get_text("info_no_historical", lang))
    
    with col2:
        # Capital structure pie chart
        fig_cap = go.Figure(data=[go.Pie(
            labels=[get_text("metric_debt", lang), get_text("metric_equity", lang)],
            values=[debt, equity],
            hole=0.5,
            key="summary_cap_pie"
        )])
        fig_cap.update_layout(
            title=get_text("summary_chart_cap_title", lang),
            height=350,
            key="summary_cap_layout"
        )
        st.plotly_chart(fig_cap, use_container_width=True, key="summary_cap_chart_key")
    
    st.markdown("---")
    
    # Key financial ratios table
    st.markdown(f"### {get_text('summary_key_ratios_title', lang)}")
    key_ratios = pd.DataFrame({
        get_text("stress_table_scenario", lang): ["ROA", "ROE", "Debt/Assets", "Debt/Equity", "Current Ratio", "Quick Ratio"],
        get_text("metric_company", lang) if lang == "en" else "Giá Trị": [fmt_ratio(roa), fmt_ratio(roe), fmt_ratio(dta), fmt_ratio(dte), fmt_ratio(current_ratio), fmt_ratio(quick_ratio)]
    })
    st.dataframe(key_ratios, use_container_width=True, hide_index=True, key="summary_ratios_key")
    
    st.markdown("---")
    
    # ==================== SECTION B: DEFAULT PROBABILITY ====================
    st.subheader(get_text("summary_section_pd", lang))
    
    # Calculate PD from model
    try:
        if hasattr(model, "predict_proba"):
            pd_model = float(model.predict_proba(feats_df[[c for c in final_features if c in feats_df.columns]].iloc[0:1])[:, 1][0])
        else:
            pd_model = float(model.predict(feats_df[[c for c in final_features if c in feats_df.columns]].iloc[0:1])[0])
    except:
        pd_model = 0.25  # Default fallback
    
    # Simple PD adjustment (mẫu)
    pd_final = min(max(pd_model, 0.05), 0.95)
    
    # Policy band classification
    LOW_CUT = 0.20
    MED_CUT = 0.50
    if pd_final < LOW_CUT:
        band = get_text("policy_low", lang)
    elif pd_final < MED_CUT:
        band = get_text("policy_medium", lang)
    else:
        band = get_text("policy_high", lang)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.metric(get_text("metric_pd_final", lang), f"{pd_final:.2%}")
    with col2:
        st.metric(get_text("metric_policy_band", lang), band)
    with col3:
        st.markdown(f"""
        <div style="font-size:12px; color:#6b7280;">
          <span style="display:inline-flex;align-items:center;gap:8px;">
            <span style="display:inline-block;width:14px;height:14px;background:#E8F1FB;border:1px solid #cbd5e1;border-radius:3px;"></span>
            {get_text("policy_low", lang)} &lt; {LOW_CUT:.0%}
            <span style="display:inline-block;width:14px;height:14px;background:#CFE3F7;border:1px solid #cbd5e1;border-radius:3px;margin-left:16px;"></span>
            {get_text("policy_medium", lang)} &lt; {MED_CUT:.0%}
            <span style="display:inline-block;width:14px;height:14px;background:#F9E3E3;border:1px solid #cbd5e1;border-radius:3px;margin-left:16px;"></span>
            {get_text("policy_high", lang)} ≥ {MED_CUT:.0%}
          </span>
        </div>
        """, unsafe_allow_html=True)
    
    # PD Gauge
    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pd_final * 100,
        number={'suffix': "%"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': '#1f77b4'},
            'steps': [
                {'range': [0, LOW_CUT * 100], 'color': '#E8F1FB'},
                {'range': [LOW_CUT * 100, MED_CUT * 100], 'color': '#CFE3F7'},
                {'range': [MED_CUT * 100, 100], 'color': '#F9E3E3'},
            ],
            'threshold': {'line': {'color': 'red', 'width': 3}, 'value': pd_final * 100}
        }
    ))
    gauge.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(gauge, use_container_width=True, key="summary_pd_gauge_key")
    
    st.markdown("---")
    
    # ==================== SECTION C: MODEL EXPLAINABILITY ====================
    st.subheader(get_text("summary_section_shap", lang))
    
    # Sample SHAP values (mẫu)
    shap_features = ["Debt/Assets", "ROA", "Current Ratio", "Debt/Equity", "Revenue Growth"]
    shap_values = [0.15, -0.12, -0.08, 0.10, -0.05]
    
    shap_df = pd.DataFrame({
        get_text("stress_table_scenario", lang): shap_features,
        "SHAP": shap_values
    })
    
    fig_shap = go.Figure()
    colors = ["#E24A33" if v < 0 else "#1F77B4" for v in shap_df["SHAP"]]
    fig_shap.add_trace(go.Bar(
        x=shap_df["SHAP"],
        y=shap_df[get_text("stress_table_scenario", lang)],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.3f}" for v in shap_df["SHAP"]],
        textposition="outside",
        key="summary_shap_bar"
    ))
    fig_shap.update_layout(
        title=get_text("shap_chart_title", lang),
        xaxis=dict(title=get_text("shap_xaxis_title", lang)),
        height=350,
        margin=dict(l=10, r=20, t=40, b=10)
    )
    st.plotly_chart(fig_shap, use_container_width=True, key="summary_shap_chart_key")
    
    st.markdown("---")
    
    # ==================== SECTION D: STRESS TESTING ====================
    st.subheader(get_text("summary_section_stress", lang))
    
    # Sample stress scenarios (mẫu)
    sector_scenarios = {
        "Real Estate": {"Credit Tightening": 0.42, "Property Price Correction": 0.36},
        "Materials": {"Steel Price Collapse": 0.34, "Energy Cost Surge": 0.28},
        "Technology": {"Valuation Reset": 0.24, "Supply Chain Disruptions": 0.20},
        "Other": {"Generic Sector Shock": 0.22}
    }
    
    systemic_scenarios = {
        "Global Financial Crisis": 0.38,
        "Market Liquidity Crisis": 0.34,
        "Interest Rate +300bps": 0.24,
        "Government Tightening": 0.22,
        "Tariffs": 0.18
    }
    
    bucket = sector if sector in sector_scenarios else "Other"
    baseline_pd = pd_final
    
    # Sector scenarios
    sec_names = list(sector_scenarios.get(bucket, sector_scenarios["Other"]).keys())
    abs_pd_sector = [(nm, sector_scenarios[bucket][nm]) for nm in sec_names]
    df_sector = pd.DataFrame(abs_pd_sector, columns=[get_text("stress_table_scenario", lang), "PD"])
    df_sector["Impact_%"] = (df_sector["PD"] - baseline_pd) / max(baseline_pd, 1e-9) * 100.0
    
    # Systemic scenarios
    abs_pd_systemic = [(nm, systemic_scenarios[nm]) for nm in systemic_scenarios.keys()]
    df_sys = pd.DataFrame(abs_pd_systemic, columns=[get_text("stress_table_scenario", lang), "PD"])
    df_sys["Impact_%"] = (df_sys["PD"] - baseline_pd) / max(baseline_pd, 1e-9) * 100.0
    
    st.caption(get_text("stress_caption_baseline", lang).format(sector_raw=sector, bucket=bucket, baseline_pd=f"{baseline_pd:.2%}"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sector = go.Figure()
        fig_sector.add_trace(go.Bar(
            x=df_sector[get_text("stress_table_scenario", lang)],
            y=df_sector["Impact_%"],
            text=[f"{v:+.1f}%" for v in df_sector["Impact_%"]],
            textposition="outside",
            marker_color="rgba(10, 102, 194, 0.8)",
            key="summary_sector_bar"
        ))
        fig_sector.update_layout(
            title=get_text("stress_chart_sector_title", lang).format(bucket=bucket),
            yaxis=dict(title=get_text("stress_yaxis_title", lang)),
            height=340,
            margin=dict(l=10, r=10, t=48, b=80),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_sector, use_container_width=True, key="summary_sector_chart_key")
    
    with col2:
        fig_sys = go.Figure()
        fig_sys.add_trace(go.Bar(
            x=df_sys[get_text("stress_table_scenario", lang)],
            y=df_sys["Impact_%"],
            text=[f"{v:+.1f}%" for v in df_sys["Impact_%"]],
            textposition="outside",
            marker_color="rgba(34, 197, 94, 0.8)",
            key="summary_systemic_bar"
        ))
        fig_sys.update_layout(
            title=get_text("stress_chart_systemic_title", lang),
            yaxis=dict(title=get_text("stress_yaxis_title", lang)),
            height=340,
            margin=dict(l=10, r=10, t=48, b=80),
            xaxis_tickangle=-30
        )
        st.plotly_chart(fig_sys, use_container_width=True, key="summary_systemic_chart_key")
    
    # KPI summary
    k1, k2 = st.columns(2)
    with k1:
        st.metric(get_text("metric_baseline_pd", lang), f"{baseline_pd:.2%}")
    with k2:
        max_pd = max(
            df_sector['PD'].max() if not df_sector.empty else 0.0,
            df_sys['PD'].max() if not df_sys.empty else 0.0
        )
        st.metric(get_text("metric_max_pd", lang), f"{max_pd:.2%}")
    
    # Detailed scenarios table
    with st.expander(get_text("stress_details_expander", lang)):
        out = pd.concat([
            df_sector.assign(Type=get_text("stress_type_sector", lang)),
            df_sys.assign(Type=get_text("stress_type_systemic", lang))
        ], ignore_index=True)
        out = out[[
            "Type",
            get_text("stress_table_scenario", lang),
            "PD",
            "Impact_%"
        ]]
        out["PD"] = out["PD"].map(lambda v: f"{v:.2%}")
        out["Impact_%"] = out["Impact_%"].map(lambda v: f"{v:+.1f}%")
        st.dataframe(out, hide_index=True, use_container_width=True, key="summary_details_table_key")
    
    st.markdown("---")
    
    # ==================== SECTION E: RCM ASSESSMENT ====================
    st.subheader(get_text("summary_section_rcm", lang))
    
    # Placeholder for RCM Assessment
    # In a real application, this would be generated by an LLM or a rule-based system
    # based on PD, SHAP, and Stress Test results.
    
    # Example logic for RCM (Risk Classification Matrix) based on PD and Max PD
    if pd_final < 0.10 and max_pd < 0.20:
        rcm_class = get_text("rcm_low_risk", lang)
        rcm_color = "green"
        rcm_detail = get_text("rcm_low_detail", lang).format(pd_final=f"{pd_final:.2%}", max_pd=f"{max_pd:.2%}")
    elif pd_final < 0.30 and max_pd < 0.40:
        rcm_class = get_text("rcm_medium_risk", lang)
        rcm_color = "orange"
        rcm_detail = get_text("rcm_medium_detail", lang).format(pd_final=f"{pd_final:.2%}", max_pd=f"{max_pd:.2%}")
    else:
        rcm_class = get_text("rcm_high_risk", lang)
        rcm_color = "red"
        rcm_detail = get_text("rcm_high_detail", lang).format(pd_final=f"{pd_final:.2%}", max_pd=f"{max_pd:.2%}")
        
    st.markdown(f"""
    <div style="border: 2px solid {rcm_color}; border-radius: 10px; padding: 15px; background-color: #F8FAFC;">
        <h4 style="color: {rcm_color}; margin-top: 0;">{get_text("rcm_assessment_title", lang)}: {rcm_class}</h4>
        <p style="margin-bottom: 0;">{rcm_detail}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== END OF SUMMARY TAB ====================
