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

    # -------------------------------------------------------------------------
    # Project introduction and market context
    #
    # Before showing any charts, give users some context about what this app is
    # and why it exists.  We emphasise the use of AI for corporate default risk
    # scoring and summarise the scale of Vietnam's stock market.  This section
    # appears at the top of the dashboard so first‑time visitors understand the
    # purpose of the application.  The content is localised based on the
    # current language.
    if lang == 'vi':
        st.markdown(
            """
            ### 🧠 Giới thiệu dự án
            
            Ứng dụng này là một **hệ thống đánh giá rủi ro vỡ nợ doanh nghiệp**\
            xây dựng trên nền tảng **trí tuệ nhân tạo (AI)**.  Các mô hình học
            máy tiên tiến như **LightGBM**, **XGBoost**, **CatBoost** và
            **AdaBoost** được huấn luyện trên hàng nghìn chỉ số tài chính và
            kết hợp với **phân tích cảm xúc tin tức** để dự đoán xác suất vỡ
            nợ (PD) của từng công ty.  Phương pháp đa yếu tố này được mô tả
            chi tiết trong bài nghiên cứu của nhóm (*EurekA*), mang lại góc
            nhìn toàn diện về sức khỏe doanh nghiệp và hỗ trợ nhà đầu tư ra
            quyết định.
            
            ### 📈 Thị trường chứng khoán Việt Nam
            
            Theo dữ liệu năm 2025, Việt Nam có **393 công ty niêm yết** với
            **tổng vốn hóa khoảng 220&nbsp;tỷ USD**, tương đương **51,2 % GDP**.  Sàn
            Giao dịch Chứng khoán TP.HCM (HoSE) khởi đầu năm 2000 với chỉ hai
            doanh nghiệp và sáu công ty chứng khoán, nhưng nay đã trở thành
            trung tâm huy động vốn quan trọng cho nền kinh tế.  Mức
            độ phát triển nhanh chóng và tầm quan trọng ngày càng tăng của
            thị trường là lý do chúng tôi xây dựng công cụ AI này – giúp
            nhà đầu tư và tổ chức tài chính đánh giá rủi ro một cách khoa
            học và khách quan.
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            ### 🧠 Project overview
            
            This application is a **corporate default risk scoring system**
            powered by **artificial intelligence**.  Advanced machine‑learning
            models such as **LightGBM**, **XGBoost**, **CatBoost** and
            **AdaBoost** are trained on thousands of financial indicators and
            combined with **news sentiment analysis** to estimate each
            company's probability of default (PD).  This multi‑factor approach
            – described in our research paper (*EurekA*) – provides a
            comprehensive view of corporate health and helps investors make
            informed decisions.
            
            ### 📈 Vietnam stock market
            
            As of 2025, Vietnam has **393 listed companies** with a combined
            market capitalisation of roughly **USD 220 billion**, equivalent
            to **51.2 % of GDP**.  The Ho Chi Minh City Stock
            Exchange (HoSE) began in 2000 with just two listed companies and
            six member brokerages, but has grown into a key funding hub for
            the economy.  This rapid development and the
            market's growing importance are why we built an AI‑powered tool
            – to provide scientific, objective default‑risk assessment for
            investors and financial institutions.
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # If there is no raw data, show an info message after introduction
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

    # Add a gauge chart illustrating market capitalisation as a percentage of GDP.
    # We hard‑code the value based on publicly available data: Vietnam's market
    # cap is ~51.2 % of GDP in 2025.  This provides an intuitive visual
    # representation of the market's scale relative to the economy.
    market_share = 51.2
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=market_share,
        number={"suffix": "%"},
        title={"text": ("Vốn hoá thị trường/GDP" if lang == 'vi' else "Market Cap/GDP")},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#10B981"},
            "steps": [
                {"range": [0, 33], "color": "#A7F3D0"},
                {"range": [33, 66], "color": "#FDE68A"},
                {"range": [66, 100], "color": "#FCA5A5"},
            ],
            "threshold": {
                "line": {"color": "#EF4444", "width": 4},
                "thickness": 0.75,
                "value": market_share,
            },
        }
    ))
    fig_gauge.update_layout(height=300)
    st.plotly_chart(fig_gauge, use_container_width=True, key='dashboard_gauge_market_share')

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