"""
Finance Tab - Extended with multilingual support
Displays detailed financial statements and indicators
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils_new.lang import get_text

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, 
           model, thresholds, sector: str, final_features: list):
    """
    Render the Financial Analysis tab with enhanced features.
    """
    lang = st.session_state.get('current_lang', 'vi')
    
    st.subheader(get_text("finance_header", lang))
    
    # --- Data Extraction (Re-using logic from app.py/summary.py for consistency) ---
    # Need to handle case where row_model or row_raw might be empty, though app.py handles it before calling render
    try:
        row_model = feats_df[(feats_df["Ticker"].astype(str)==ticker) & (feats_df["Year"]==year)].iloc[0]
    except IndexError:
        st.warning(get_text("warning_no_data", lang))
        return
        
    row_raw = raw_df[(raw_df["Ticker"].astype(str)==ticker) & (raw_df["Year"]==year)]
    row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype="object")
    
    def safe_get(col_names, default=np.nan):
        """Get value safely from row"""
        for c in col_names:
            if c in row_raw.index:
                try:
                    # Use to_float from app.py if available, otherwise simple float conversion
                    return float(row_raw[c])
                except:
                    pass
        return default
    
    def safe_div(a, b):
        try:
            return (float(a) / float(b)) if (b not in [0, None, np.nan] and float(b)!=0.0) else np.nan
        except:
            return np.nan
            
    def fmt_ratio(x):
        """Format as percentage"""
        if (x is None) or (not np.isfinite(x)): return "-"
        return f"{x:.2%}" if -1.5 <= float(x) <= 1.5 else f"{x:,.4f}"
    
    net_profit = safe_get(["Net Profit For the Year","Net_Profit"])
    assets = safe_get(["TOTAL ASSETS (Bn. VND)","Total_Assets"])
    equity = safe_get(["OWNER'S EQUITY(Bn.VND)","Equity"])
    curr_liab = safe_get(["Current liabilities (Bn. VND)","Current_Liabilities"], 0.0)
    long_liab = safe_get(["Long-term liabilities (Bn. VND)","Long_Term_Liabilities"], 0.0)
    
    total_liab = (curr_liab or 0.0) + (long_liab or 0.0)
    debt = total_liab # Simplified for D/E calculation
    
    roa = safe_div(net_profit, assets)
    roe = safe_div(net_profit, equity)
    dta = safe_div(total_liab, assets)
    dte = safe_div(debt, equity)
    
    # --- Simulated Sector Benchmarks ---
    sector_benchmarks = {
        "Real Estate": {"ROA": 0.03, "ROE": 0.12, "DTA": 0.65, "DTE": 1.80},
        "Materials": {"ROA": 0.05, "ROE": 0.15, "DTA": 0.55, "DTE": 1.20},
        "Technology": {"ROA": 0.08, "ROE": 0.20, "DTA": 0.40, "DTE": 0.80},
        "Financials": {"ROA": 0.02, "ROE": 0.10, "DTA": 0.85, "DTE": 5.00},
        "Consumer Staples": {"ROA": 0.06, "ROE": 0.18, "DTA": 0.35, "DTE": 0.70},
        "Other": {"ROA": 0.04, "ROE": 0.14, "DTA": 0.50, "DTE": 1.00},
    }
    sector_key = sector if sector in sector_benchmarks else "Other"
    benchmark = sector_benchmarks[sector_key]
    
    # --- Tabs for different financial statements ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text("finance_tab_income", lang),
        get_text("finance_tab_balance", lang),
        get_text("finance_tab_cashflow", lang),
        get_text("finance_tab_indicators", lang),
        get_text("finance_tab_notes", lang)
    ])
    
    # ==================== TAB 1: INCOME STATEMENT (Placeholder) ====================
    with tab1:
        st.markdown(f"### {get_text('income_statement_title', lang)}")
        st.info(get_text("finance_placeholder_data", lang).format(section=get_text('income_statement_title', lang)))
        
    # ==================== TAB 2: BALANCE SHEET (Placeholder) ====================
    with tab2:
        st.markdown(f"### {get_text('balance_sheet_title', lang)}")
        st.info(get_text("finance_placeholder_data", lang).format(section=get_text('balance_sheet_title', lang)))
        
    # ==================== TAB 3: CASH FLOW (Placeholder) ====================
    with tab3:
        st.markdown(f"### {get_text('cashflow_statement_title', lang)}")
        st.info(get_text("finance_placeholder_data", lang).format(section=get_text('cashflow_statement_title', lang)))
        
    # ==================== TAB 4: FINANCIAL INDICATORS (Enhanced) ====================
    with tab4:
        st.markdown(f"### {get_text('financial_indicators_title', lang)}")
        
        st.markdown(f"#### {get_text('finance_section_profitability', lang)}")
        profit_data = pd.DataFrame({
            get_text("metric_name", lang): ["ROA", "ROE"],
            get_text("metric_company", lang): [fmt_ratio(roa), fmt_ratio(roe)],
            get_text("metric_sector_avg", lang): [fmt_ratio(benchmark["ROA"]), fmt_ratio(benchmark["ROE"])]
        })
        st.dataframe(profit_data, hide_index=True, use_container_width=True)
        
        st.markdown(f"#### {get_text('finance_section_leverage', lang)}")
        leverage_data = pd.DataFrame({
            get_text("metric_name", lang): ["Debt/Assets (DTA)", "Debt/Equity (DTE)"],
            get_text("metric_company", lang): [fmt_ratio(dta), fmt_ratio(dte)],
            get_text("metric_sector_avg", lang): [fmt_ratio(benchmark["DTA"]), fmt_ratio(benchmark["DTE"])]
        })
        st.dataframe(leverage_data, hide_index=True, use_container_width=True)
        
    # ==================== TAB 5: NOTES & ASSESSMENT (Enhanced) ====================
    with tab5:
        st.markdown(f"### {get_text('notes_assessment_title', lang)}")
        
        # Simple Assessment Logic
        assessment = []
        
        # Profitability
        if roa > benchmark["ROA"] and roe > benchmark["ROE"]:
            assessment.append(f"✅ **{get_text('finance_assess_profit_good', lang)}** ({fmt_ratio(roa)} ROA so với {fmt_ratio(benchmark['ROA'])} ngành).")
        elif roa < 0 or roe < 0:
            assessment.append(f"❌ **{get_text('finance_assess_profit_bad', lang)}** (ROA/ROE âm, cần xem xét nguyên nhân).")
        else:
            assessment.append(f"⚠️ **{get_text('finance_assess_profit_neutral', lang)}** (ROA {fmt_ratio(roa)} so với {fmt_ratio(benchmark['ROA'])} ngành).")
            
        # Leverage
        if dte < benchmark["DTE"] * 0.8:
            assessment.append(f"✅ **{get_text('finance_assess_leverage_good', lang)}** (Tỷ lệ Nợ/Vốn {fmt_ratio(dte)} thấp hơn đáng kể so với mức trung bình ngành {fmt_ratio(benchmark['DTE'])}).")
        elif dte > benchmark["DTE"] * 1.2:
            assessment.append(f"❌ **{get_text('finance_assess_leverage_bad', lang)}** (Tỷ lệ Nợ/Vốn {fmt_ratio(dte)} cao hơn mức trung bình ngành {fmt_ratio(benchmark['DTE'])}).")
        else:
            assessment.append(f"⚠️ **{get_text('finance_assess_leverage_neutral', lang)}** (Tỷ lệ Nợ/Vốn {fmt_ratio(dte)} ở mức tương đương ngành).")
            
        st.markdown("\n\n".join(assessment))
