"""
Tab: Dashboard (Trang tổng quan)

This module renders a high level overview of the market and highlights top
companies by size.  It is intended to give users context before drilling
down into a specific ticker.  The dashboard aggregates data across all
companies and years and surfaces interesting statistics.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from utils_new.lang import get_text

def to_num(x: any) -> float:
    """Convert various numeric strings to float safely."""
    try:
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return np.nan
        if isinstance(x, str):
            # Remove commas and potential unit suffixes
            x = x.replace(",", "").strip()
        return float(x)
    except Exception:
        return np.nan

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame) -> None:
    """Render the dashboard tab.

    Parameters
    ----------
    feats_df: pd.DataFrame
        DataFrame with engineered features (not used here but kept for
        interface consistency).
    raw_df: pd.DataFrame
        Raw financial statement data containing revenue, net profit and
        balance sheet information.
    """
    lang = st.session_state.current_lang

    st.header(get_text('dashboard_title', lang))

    # Compute top companies by total assets for the most recent year
    # Filter to the latest year present in the dataset
    if raw_df.empty:
        st.info(get_text('warning_no_data', lang))
        return
    latest_year = raw_df['Year'].max()
    latest_df = raw_df[raw_df['Year'] == latest_year].copy()
    latest_df['TotalAssets'] = latest_df['TOTAL ASSETS (Bn. VND)'].apply(to_num)
    # Drop rows with missing assets
    latest_df = latest_df.dropna(subset=['TotalAssets'])
    top_n = latest_df.nlargest(5, 'TotalAssets')[['Ticker', 'TotalAssets']]
    # Format numbers
    top_n_display = top_n.copy()
    top_n_display['TotalAssets'] = top_n_display['TotalAssets'].apply(lambda x: f"{x:,.2f} bn VND" if pd.notna(x) else '-')
    st.subheader(get_text('dashboard_top_assets', lang).format(year=int(latest_year)))
    st.dataframe(top_n_display, hide_index=True, use_container_width=True, key='dashboard_top_assets_table')

    # Compute average revenue and net profit across all companies per year
    agg_df = raw_df.copy()
    # Identify revenue column (Net Sales/Revenue)
    if 'Net Sales' in agg_df.columns:
        rev_col = 'Net Sales'
    elif 'Revenue' in agg_df.columns:
        rev_col = 'Revenue'
    else:
        rev_col = 'Revenue (Bn. VND)'
    np_col = 'Net Profit For the Year' if 'Net Profit For the Year' in agg_df.columns else 'Net Profit'
    agg_df['Revenue'] = agg_df[rev_col].apply(to_num)
    agg_df['NetProfit'] = agg_df[np_col].apply(to_num)
    summary = agg_df.groupby('Year')[['Revenue','NetProfit']].mean().reset_index()
    years_str = summary['Year'].astype(str).tolist()
    avg_rev = summary['Revenue'].tolist()
    avg_np = summary['NetProfit'].tolist()
    # Plot trends
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=years_str, y=avg_rev, name=get_text('metric_revenue', lang), mode='lines+markers'))
    fig.add_trace(go.Scatter(x=years_str, y=avg_np, name=get_text('metric_net_profit', lang), mode='lines+markers'))
    fig.update_layout(title=get_text('dashboard_avg_trend', lang), height=350, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
    st.plotly_chart(fig, use_container_width=True, key='dashboard_avg_chart')

    # Provide a brief narrative summarising the market based on latest values
    rev_growth = np.nan
    np_growth = np.nan
    if len(summary) >= 2:
        prev_rev = summary.iloc[-2]['Revenue']
        curr_rev = summary.iloc[-1]['Revenue']
        prev_np = summary.iloc[-2]['NetProfit']
        curr_np = summary.iloc[-1]['NetProfit']
        rev_growth = ((curr_rev - prev_rev) / prev_rev) if prev_rev else np.nan
        np_growth = ((curr_np - prev_np) / prev_np) if prev_np else np.nan
    if lang == 'vi':
        narrative = f"**Tổng quan:** Năm {int(latest_year)}, doanh thu trung bình của các doanh nghiệp đạt {avg_rev[-1]:,.2f} tỷ đồng và lợi nhuận ròng trung bình {avg_np[-1]:,.2f} tỷ đồng."
        if not np.isnan(rev_growth):
            narrative += f" Doanh thu trung bình {'tăng' if rev_growth>=0 else 'giảm'} {abs(rev_growth)*100:.1f}% so với năm trước."
        if not np.isnan(np_growth):
            narrative += f" Lợi nhuận ròng trung bình {'tăng' if np_growth>=0 else 'giảm'} {abs(np_growth)*100:.1f}% so với năm trước."
    else:
        narrative = f"**Overview:** In {int(latest_year)}, the average company revenue was {avg_rev[-1]:,.2f} bn VND and average net profit {avg_np[-1]:,.2f} bn VND."
        if not np.isnan(rev_growth):
            narrative += f" Average revenue {'increased' if rev_growth>=0 else 'decreased'} by {abs(rev_growth)*100:.1f}% from the previous year."
        if not np.isnan(np_growth):
            narrative += f" Average net profit {'increased' if np_growth>=0 else 'decreased'} by {abs(np_growth)*100:.1f}% from the previous year."
    st.markdown(narrative)