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

    # Display a decorative banner image to create a strong first impression.
    # The image is a futuristic illustration representing AI in finance.
    banner_path = 'assets/dashboard_banner.png'
    try:
        st.image(banner_path, use_column_width=True)
    except Exception:
        # If the image cannot be found (e.g., during development), skip silently.
        pass

    # -------------------------------------------------------------------------
    # Project introduction and market context
    #
    # Before showing any charts, give users some context about what this app is
    # and why it exists.  We emphasise the use of AI for corporate default risk
    # scoring and summarise the scale of Vietnam's stock market.  This section
    # appears at the top of the dashboard so first‑time visitors understand the
    # purpose of the application.  The content is localised based on the
    # current language.
    # Build a card‑style introduction with a soft background.  We remove the
    # reference to EurekA and focus on the AI-driven nature of the project.
    intro_style = "background-color:#F5FAFF;border:1px solid #E0E7FF;"
    intro_style += "padding:16px;border-radius:8px;margin-bottom:16px;"
    if lang == 'vi':
        intro_html = f"""
        <div style='{intro_style}'>
        <h3>🧠 Giới thiệu dự án</h3>
        <p>Ứng dụng này là một <strong>hệ thống đánh giá rủi ro vỡ nợ doanh nghiệp</strong>
        xây dựng trên nền tảng <strong>trí tuệ nhân tạo (AI)</strong>.  Các mô hình
        học máy tiên tiến như <strong>LightGBM</strong>, <strong>XGBoost</strong>,
        <strong>CatBoost</strong> và <strong>AdaBoost</strong> được huấn luyện trên hàng
        nghìn chỉ số tài chính và kết hợp với <strong>phân tích cảm xúc tin tức</strong>
        để dự đoán xác suất vỡ nợ (PD) của từng công ty.  Cách tiếp cận đa yếu tố
        này mang lại góc nhìn toàn diện về sức khỏe doanh nghiệp và hỗ trợ nhà đầu
        tư ra quyết định một cách khoa học.</p>
        <h3>📈 Thị trường chứng khoán Việt Nam</h3>
        <p>Theo dữ liệu năm&nbsp;2025, Việt Nam có <strong>393 công ty niêm yết</strong> với
        <strong>tổng vốn hóa khoảng 220&nbsp;tỷ USD</strong>, tương đương <strong>51,2&nbsp;% GDP</strong>.
        Sàn Giao dịch Chứng khoán TP.&nbsp;HCM (HoSE) khởi đầu năm&nbsp;2000 với chỉ hai
        doanh nghiệp và sáu công ty chứng khoán, nhưng nay đã trở thành trung tâm
        huy động vốn quan trọng cho nền kinh tế.  Tốc độ phát triển nhanh chóng
        và tầm quan trọng ngày càng tăng của thị trường là lý do chúng tôi xây dựng
        công cụ AI này – giúp nhà đầu tư và tổ chức tài chính đánh giá rủi ro một
        cách khách quan.</p>
        </div>
        """
        st.markdown(intro_html, unsafe_allow_html=True)
    else:
        intro_html = f"""
        <div style='{intro_style}'>
        <h3>🧠 Project overview</h3>
        <p>This application is a <strong>corporate default risk scoring system</strong>
        powered by <strong>artificial intelligence</strong>.  Advanced machine‑learning
        models such as <strong>LightGBM</strong>, <strong>XGBoost</strong>, <strong>CatBoost</strong>
        and <strong>AdaBoost</strong> are trained on thousands of financial indicators and
        combined with <strong>news sentiment analysis</strong> to estimate each company's
        probability of default (PD).  This multi‑factor approach provides a
        comprehensive view of corporate health and helps investors make informed
        decisions.</p>
        <h3>📈 Vietnam stock market</h3>
        <p>As of 2025, Vietnam has <strong>393 listed companies</strong> with a combined
        market capitalisation of roughly <strong>USD 220 billion</strong>, equivalent to
        <strong>51.2 % of GDP</strong>.  The Ho Chi Minh City Stock Exchange (HoSE) began
        in 2000 with just two listed companies and six member brokerages, but it
        has since grown into a key funding hub for the economy.  This rapid
        development and the market's growing importance are why we built an AI‑powered
        tool – to provide scientific, objective default‑risk assessment for
        investors and financial institutions.</p>
        </div>
        """
        st.markdown(intro_html, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Key metrics cards
    # Present a few headline numbers to give users a sense of scale.  We
    # calculate the number of unique tickers (companies) from feats_df, the
    # number of AI models used (fixed at 4), and an estimate of the number of
    # financial indicators (columns) leveraged for modelling.  These metrics
    # are displayed in separate columns with Streamlit's metric component.
    try:
        num_companies = feats_df['Ticker'].nunique()
    except Exception:
        num_companies = None
    num_models = 4
    # Estimate number of indicator columns by excluding known non‑numeric fields
    exclude_cols = {'Ticker', 'Year', 'Sector', 'Exchange', 'Ticker Name', 'Company'}
    indicator_cols = [c for c in feats_df.columns if c not in exclude_cols]
    num_indicators = len(indicator_cols)
    col1, col2, col3 = st.columns(3)
    col1.metric(
        label=("Số công ty" if lang == 'vi' else "Companies analysed"),
        value=f"{num_companies}" if num_companies is not None else "–",
        delta=None,
    )
    col2.metric(
        label=("Mô hình AI" if lang == 'vi' else "AI models"),
        value=str(num_models),
        delta=None,
    )
    col3.metric(
        label=("Chỉ số sử dụng" if lang == 'vi' else "Indicators used"),
        value=str(num_indicators),
        delta=None,
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

    # ---------------------------------------------------------------------
    # Top sectors by number of listed companies
    # Many users are curious about which industries dominate the market.  We
    # derive this information from the financial features dataset.  If the
    # sector field is available, count the number of unique tickers per
    # sector, sort descending and display the top five as a bar chart.
    if 'Sector' in feats_df.columns:
        sector_counts = feats_df.groupby('Sector')['Ticker'].nunique().sort_values(ascending=False).head(5)
        sector_labels = sector_counts.index.tolist()
        sector_values = sector_counts.values.tolist()
        fig_sector = go.Figure(go.Bar(x=sector_labels, y=sector_values,
                                      marker_color='#3B82F6'))
        fig_sector.update_layout(
            title=("Top 5 ngành theo số công ty niêm yết" if lang == 'vi' else "Top 5 sectors by number of listed companies"),
            xaxis_title=("Ngành" if lang == 'vi' else "Sector"),
            yaxis_title=("Số lượng công ty" if lang == 'vi' else "Number of companies"),
            height=350,
        )
        st.plotly_chart(fig_sector, use_container_width=True, key='dashboard_sector_bar')

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