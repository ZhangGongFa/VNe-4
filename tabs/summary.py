"""Summary tab renderer.

This module implements the Summary tab, which consolidates company
financial overview, default probability scoring and broader default
statistics.  It leverages the ``analysis_utils`` package to load
the LightGBM model, engineer features, compute PD values and
generate distribution plots.  The layout closely follows the
dashboard provided in the PD‑monotonic‑constraints project.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from ..utils.io import read_csv_smart
from ..analysis_utils import (
    clean_and_log_transform,
    preprocess_and_create_features,
    select_features_for_model,
    load_lgbm_model,
    model_feature_names,
    predict_pd,
    explain_shap,
    align_features_to_model,
    load_thresholds,
    thresholds_for_sector,
    classify_pd,
    default_distribution_by_year,
    default_distribution_by_sector,
)


def render(fin_df):
    """Render the Summary tab for the current ticker.

    Parameters
    ----------
    fin_df : pandas.DataFrame
        Filtered dataframe containing rows for the selected ticker.
    """
    if fin_df is None or fin_df.empty:
        st.info("No data available for summary.")
        return

    # Determine absolute paths to data and model within the package
    base_dir = os.path.dirname(os.path.dirname(__file__))  # vne_app
    data_path = os.path.join(base_dir, 'data', 'bctc_final.csv')
    model_path = os.path.join(base_dir, 'models', 'lgbm_model.pkl')
    threshold_path = os.path.join(base_dir, 'models', 'threshold.json')

    # Load and preprocess the full dataset
    try:
        raw_df = pd.read_csv(data_path)
    except Exception:
        # Fallback: attempt to read using utils.io
        try:
            raw_df = read_csv_smart(data_path)
        except Exception:
            st.error("Unable to load the default dataset for summary.")
            return
    # Clean and engineer features
    cleaned_df = clean_and_log_transform(raw_df)
    feats_df = preprocess_and_create_features(cleaned_df)

    # Load model and thresholds
    model = load_lgbm_model(model_path)
    thresholds = load_thresholds(threshold_path)

    # Determine candidate feature list and final features
    candidate_features = [
        'Current_Ratio', 'Quick_Ratio', 'Working_Capital_to_Total_Assets',
        'Debt_to_Assets', 'Debt_to_Equity', 'Equity_to_Liabilities',
        'Long_Term_Debt_to_Assets', 'Receivables_Turnover', 'Inventory_Turnover',
        'Asset_Turnover', 'ROA', 'ROE', 'EBIT_to_Assets',
        'Operating_Income_to_Debt', 'Net_Profit_Margin', 'Gross_Margin',
        'Interest_Coverage', 'EBITDA_to_Interest', 'Total_Debt_to_EBITDA',
        'Net_Debt_to_Equity', 'LowRiskFlag', 'OCF_Deficit_2of3',
        'Revenue_CAGR_3Y', 'PAT_Std_3Y', 'Sector_Default_Rate'
    ]
    model_feats = model_feature_names(model)
    final_features = select_features_for_model(feats_df, candidate_features, model_feats)

    # Identify ticker and available years from feats_df
    current_ticker = fin_df['Ticker'].iloc[0]
    avail_years = feats_df.loc[feats_df['Ticker'] == current_ticker, 'Year'].dropna().astype(int).unique().tolist()
    avail_years.sort()
    if not avail_years:
        st.info("No engineered features available for this ticker.")
        return
    # Year selection
    default_idx = len(avail_years) - 1
    year = st.selectbox("Select Year", options=avail_years, index=default_idx, key=f"summary_year_{current_ticker}")

    # Extract model and raw rows for the selected ticker & year
    row_model = feats_df[(feats_df['Ticker'] == current_ticker) & (feats_df['Year'] == year)]
    if row_model.empty:
        st.warning("No record for the selected ticker & year.")
        return
    row_model = row_model.iloc[0]
    row_raw = raw_df[(raw_df['Ticker'] == current_ticker) & (raw_df['Year'] == year)]
    row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype='object')

    # Extract sector and exchange
    sector_raw = str(row_model.get('Sector', '')) if pd.notna(row_model.get('Sector', '')) else ''
    exchange = str(row_model.get('Exchange', '')).upper() if pd.notna(row_model.get('Exchange', '')) else ''

    # Extract key raw metrics
    def get_raw_val(sr: pd.Series, cols, default=np.nan):
        for c in cols:
            if c in sr.index:
                try:
                    return float(str(sr[c]).replace(',', ''))
                except Exception:
                    try:
                        return float(sr[c])
                    except Exception:
                        return default
        return default

    assets_raw = get_raw_val(row_raw, ["TOTAL ASSETS (Bn. VND)", 'Total_Assets'])
    equity_raw = get_raw_val(row_raw, ["OWNER'S EQUITY(Bn.VND)", 'Equity'])
    current_liab = get_raw_val(row_raw, ['Current liabilities (Bn. VND)', 'Current_Liabilities'], 0.0)
    long_liab = get_raw_val(row_raw, ['Long-term liabilities (Bn. VND)', 'Long_Term_Liabilities'], 0.0)
    short_bor = get_raw_val(row_raw, ['Short-term borrowings (Bn. VND)', 'Short_Term_Borrowings'], 0.0)
    revenue_raw = get_raw_val(row_raw, ['Net Sales', 'Revenue'])
    net_profit_raw = get_raw_val(row_raw, ['Net Profit For the Year', 'Net_Profit'])
    operating_profit_raw = get_raw_val(row_raw, ['Operating Profit/Loss', 'Operating_Profit'])
    interest_exp_raw = get_raw_val(row_raw, ['Interest Expenses', 'Interest_Expenses'], 0.0)
    cash_raw = get_raw_val(row_raw, ['Cash and cash equivalents (Bn. VND)', 'Cash'], 0.0)
    receivables_raw = get_raw_val(row_raw, ['Accounts receivable (Bn. VND)', 'Receivables'], 0.0)
    inventories_raw = get_raw_val(row_raw, ['Net Inventories', 'Inventories'], 0.0)
    current_assets_raw = get_raw_val(row_raw, ['CURRENT ASSETS (Bn. VND)', 'Current_Assets'], 0.0)
    total_liab_raw = (current_liab or 0.0) + (long_liab or 0.0)
    debt_raw = get_raw_val(row_raw, ['Total_Debt']) if 'Total_Debt' in row_raw.index else (short_bor or 0.0) + (long_liab or 0.0)

    # Compute ratio metrics
    def safe_div(a, b):
        try:
            a_f, b_f = float(a or 0.0), float(b or 0.0)
            return a_f / b_f if b_f not in [0, None, np.nan] and b_f != 0.0 else np.nan
        except Exception:
            return np.nan

    roa = safe_div(net_profit_raw, assets_raw)
    roe = safe_div(net_profit_raw, equity_raw)
    dta = safe_div(total_liab_raw, assets_raw)
    dte = safe_div(debt_raw, equity_raw)
    current_ratio = safe_div(current_assets_raw, current_liab)
    quick_ratio = safe_div((cash_raw or 0.0) + (receivables_raw or 0.0), current_liab)

    # Sidebar / header showing company profile & ratios
    st.subheader(f"Default Risk Summary: {current_ticker} — {year}")
    col_prof, col_figs = st.columns([1, 2])
    with col_prof:
        st.markdown(f"**Sector:** {sector_raw or '-'}  \n**Exchange:** {exchange or '-'}")
        st.markdown(
            f"<div class='metric-card'>"
            f"Total Assets: <b>{assets_raw:,.2f}</b><br>"
            f"Equity: <b>{equity_raw:,.2f}</b><br>"
            f"Debt: <b>{debt_raw:,.2f}</b><br>"
            f"Revenue: <b>{revenue_raw:,.2f}</b><br>"
            f"Net Profit: <b>{net_profit_raw:,.2f}</b>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='metric-card'>"
            f"ROA: <b>{roa:.2%}</b><br>"
            f"ROE: <b>{roe:.2%}</b><br>"
            f"Debt/Assets: <b>{dta:.2%}</b><br>"
            f"Debt/Equity: <b>{dte:.2%}</b><br>"
            f"Current Ratio: <b>{current_ratio:.2f}</b><br>"
            f"Quick Ratio: <b>{quick_ratio:.2f}</b>"
            "</div>",
            unsafe_allow_html=True,
        )
    # Company overview charts
    with col_figs:
        # Historical revenue and net profit series for this ticker
        hist = raw_df[raw_df['Ticker'] == current_ticker].sort_values('Year')
        series_df = hist[[
            'Year', 'Net Sales', 'Net Profit For the Year'
        ]].rename(columns={'Net Sales': 'Revenue', 'Net Profit For the Year': 'Net_Profit'}).dropna(how='any')
        if not series_df.empty:
            fig_rev = go.Figure()
            fig_rev.add_trace(go.Bar(x=series_df['Year'], y=series_df['Revenue'], name='Revenue'))
            fig_rev.add_trace(go.Scatter(x=series_df['Year'], y=series_df['Net_Profit'], name='Net Profit', mode='lines+markers', yaxis='y2'))
            fig_rev.update_layout(
                title="Revenue & Net Profit (multi-year)",
                yaxis=dict(title="Revenue"),
                yaxis2=dict(title="Net Profit", overlaying='y', side='right'),
                legend=dict(orientation='h', yanchor='bottom', y=-0.25, xanchor='center', x=0.5),
                height=380
            )
            st.plotly_chart(fig_rev, use_container_width=True)
        else:
            st.info("No historical series for this company.")
        # Capital structure pie chart
        fig_cap = go.Figure(data=[go.Pie(labels=['Total Debt', 'Equity'], values=[debt_raw, equity_raw], hole=0.5)])
        fig_cap.update_layout(title="Capital Structure", height=380)
        st.plotly_chart(fig_cap, use_container_width=True)

    # Compute PD
    X_row = pd.DataFrame([row_model[final_features].values], columns=final_features)
    # Align features to model
    X_row = align_features_to_model(X_row, model)
    pd_value = predict_pd(model, X_row)
    th = thresholds_for_sector(thresholds, sector_raw)
    pd_class = classify_pd(pd_value, th)

    # Display PD and classification
    st.markdown("## Default Probability")
    st.markdown(
        f"Predicted PD: **{pd_value:.2%}**  \nClassification: **{pd_class}** (Low if < {th['low']:.0%}, Medium if < {th['medium']:.0%}, High otherwise)"
    )

    # SHAP explanation
    shap_df = explain_shap(model, X_row, top_n=10)
    if not shap_df.empty:
        st.markdown("### Top Feature Contributions (SHAP)")
        # Convert shap values to bar chart
        shap_fig = go.Figure()
        shap_fig.add_trace(go.Bar(
            x=shap_df['shap'],
            y=shap_df['feature'],
            orientation='h',
            marker=dict(color=np.sign(shap_df['shap']), colorscale='RdBu'),
        ))
        shap_fig.update_layout(
            title="SHAP Feature Contributions",
            xaxis_title="SHAP Value",
            yaxis_title="Feature",
            height=360
        )
        st.plotly_chart(shap_fig, use_container_width=True)

    # Default distribution section
    st.markdown("## Default Distribution Overview")
    pie_fig, bar_year, table_year = default_distribution_by_year(feats_df)
    col_y1, col_y2 = st.columns([2, 1])
    with col_y1:
        st.plotly_chart(bar_year, use_container_width=True)
    with col_y2:
        st.plotly_chart(pie_fig, use_container_width=True)
    st.plotly_chart(table_year, use_container_width=True)

    bar_sector, pie_sector, bar_rate_sector, table_sector = default_distribution_by_sector(feats_df)
    st.markdown("### By Sector")
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        st.plotly_chart(bar_sector, use_container_width=True)
    with col_s2:
        st.plotly_chart(pie_sector, use_container_width=True)
    st.plotly_chart(bar_rate_sector, use_container_width=True)
    st.plotly_chart(table_sector, use_container_width=True)