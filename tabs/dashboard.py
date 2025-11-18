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
        <p>Thị trường chứng khoán Việt Nam đã phát triển mạnh mẽ trong hai thập kỷ qua. Dữ liệu về vốn hoá và quy mô thị trường phụ thuộc vào năm và sàn giao dịch bạn đang xem ở bên dưới.</p>
        <p style='font-size:0.85rem'>Để tra cứu định nghĩa các thuật ngữ tài chính, vui lòng chuyển sang tab <strong>Glossary</strong>.</p>
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
        <p>Vietnam's stock market has grown rapidly over the past two decades. The
        capitalisation and scale of the market depend on the year and exchange you
        select below.</p>
        <p style='font-size:0.85rem'>To understand financial terms used across the app, please visit the <strong>Glossary</strong> tab.</p>
        </div>
        """
        st.markdown(intro_html, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Interactive filters
    # Provide high‑level filters allowing users to focus on a specific year,
    # exchange or sector.  The filters update all subsequent charts and
    # statistics.  We wrap the widgets in columns for a compact layout.
    try:
        year_options = sorted(raw_df['Year'].dropna().unique().tolist()) if not raw_df.empty else []
    except Exception:
        year_options = []
    # Default to the latest year if available
    default_year_idx = len(year_options) - 1 if year_options else 0
    exch_options = []
    if 'Exchange' in feats_df.columns:
        exch_options = sorted(feats_df['Exchange'].dropna().unique().tolist())
    elif 'Exchange' in raw_df.columns:
        exch_options = sorted(raw_df['Exchange'].dropna().unique().tolist())
    # Prepend "All" option
    exch_options = ['All'] + exch_options if exch_options else ['All']
    sect_options = []
    if 'Sector' in feats_df.columns:
        sect_options = sorted(feats_df['Sector'].dropna().unique().tolist())
    elif 'Sector' in raw_df.columns:
        sect_options = sorted(raw_df['Sector'].dropna().unique().tolist())
    sect_options = ['All'] + sect_options if sect_options else ['All']
    # Render filter widgets
    filter_container = st.container()
    with filter_container:
        fcol1, fcol2, fcol3 = st.columns(3)
        # Year selector
        if year_options:
            selected_year = fcol1.selectbox(
                "Năm" if lang == 'vi' else "Year",
                options=year_options,
                index=default_year_idx,
                key='dashboard_year_select'
            )
        else:
            selected_year = None
        # Exchange selector
        selected_exchange = fcol2.selectbox(
            "Sàn giao dịch" if lang == 'vi' else "Exchange",
            options=exch_options,
            key='dashboard_exchange_select'
        )
        # Sector selector
        selected_sector = fcol3.selectbox(
            "Ngành" if lang == 'vi' else "Sector",
            options=sect_options,
            key='dashboard_sector_select'
        )

    # Apply filters to the datasets
    feats_filtered = feats_df.copy() if feats_df is not None else pd.DataFrame()
    raw_filtered = raw_df.copy() if raw_df is not None else pd.DataFrame()
    if selected_exchange and selected_exchange != 'All':
        if 'Exchange' in feats_filtered.columns:
            feats_filtered = feats_filtered[feats_filtered['Exchange'] == selected_exchange]
        if 'Exchange' in raw_filtered.columns:
            raw_filtered = raw_filtered[raw_filtered['Exchange'] == selected_exchange]
    if selected_sector and selected_sector != 'All':
        if 'Sector' in feats_filtered.columns:
            feats_filtered = feats_filtered[feats_filtered['Sector'] == selected_sector]
        if 'Sector' in raw_filtered.columns:
            raw_filtered = raw_filtered[raw_filtered['Sector'] == selected_sector]

    # If a specific year is selected, narrow the raw data for certain charts
    if selected_year is not None:
        try:
            year_filtered_df = raw_filtered[raw_filtered['Year'] == selected_year].copy()
        except Exception:
            year_filtered_df = pd.DataFrame()
    else:
        year_filtered_df = raw_filtered.copy()

    # -------------------------------------------------------------------------
    # Key metrics cards
    # Present a few headline numbers to give users a sense of scale.  We
    # calculate the number of unique tickers (companies) from the filtered
    # feature dataframe, the number of AI models used (fixed at 4), and an
    # estimate of the number of financial indicators (columns) leveraged for
    # modelling.  Tooltips explain each metric and expanders provide deeper
    # detail when needed.
    try:
        num_companies = feats_filtered['Ticker'].nunique()
    except Exception:
        num_companies = None
    num_models = 4  # Hard coded as our pipeline currently uses four ML models
    # Estimate number of indicator columns by excluding known non‑numeric fields
    exclude_cols = {'Ticker', 'Year', 'Sector', 'Exchange', 'Ticker Name', 'Company'}
    indicator_cols = [c for c in feats_filtered.columns if c not in exclude_cols]
    num_indicators = len(indicator_cols)
    mcol1, mcol2, mcol3 = st.columns(3)
    mcol1.metric(
        label=("Số công ty" if lang == 'vi' else "Companies analysed"),
        value=f"{num_companies}" if num_companies is not None else "–",
        help=("Số lượng mã chứng khoán hiện có sau khi áp dụng bộ lọc" if lang == 'vi' else "Number of unique tickers after applying filters"),
    )
    mcol2.metric(
        label=("Mô hình AI" if lang == 'vi' else "AI models"),
        value=str(num_models),
        help=("Tổng số mô hình học máy được sử dụng trong hệ thống" if lang == 'vi' else "Total number of machine‑learning models used by the system"),
    )
    mcol3.metric(
        label=("Chỉ số sử dụng" if lang == 'vi' else "Indicators used"),
        value=str(num_indicators),
        help=("Số lượng biến đầu vào được sử dụng cho việc huấn luyện mô hình" if lang == 'vi' else "Number of input features used for model training"),
    )

    # Optional detail: allow the user to inspect lists behind the metrics
    with st.expander("📄 Xem danh sách công ty" if lang == 'vi' else "📄 View company list", expanded=False):
        if num_companies:
            st.write(feats_filtered[['Ticker']].drop_duplicates().reset_index(drop=True))
        else:
            st.info("Không có công ty nào trong phạm vi lọc" if lang == 'vi' else "No companies available under current filters")
    with st.expander("ℹ️ Thông tin chỉ số" if lang == 'vi' else "ℹ️ Indicator info", expanded=False):
        if indicator_cols:
            # Show first 20 indicator names to avoid overwhelming the user
            preview = indicator_cols[:20]
            more = len(indicator_cols) - len(preview)
            st.write(preview)
            if more > 0:
                st.write((f"… và {more} chỉ số khác" if lang == 'vi' else f"… and {more} more indicators"))
        else:
            st.info("Không có chỉ số nào để hiển thị" if lang == 'vi' else "No indicators to display")

    # -------------------------------------------------------------------------
    # How it works / Quy trình đánh giá
    # Provide a concise, icon‑based overview of the AI scoring pipeline.  This
    # section helps users understand the steps involved without overwhelming
    # them with technical detail.  It adapts to the current language.
    how_title_vi = "### 🔧 Quy trình đánh giá"
    how_title_en = "### 🔧 How it works"
    how_items_vi = [
        ("📥", "Thu thập dữ liệu", "Thu thập số liệu tài chính và tin tức liên quan từ nhiều nguồn"),
        ("🧮", "Xử lý & lựa chọn", "Chuẩn hóa, làm sạch và chọn lọc những chỉ số quan trọng"),
        ("🤖", "Huấn luyện mô hình", "Huấn luyện các mô hình học máy LightGBM, XGBoost, CatBoost, AdaBoost"),
        ("💡", "Tính điểm & phân tích", "Tính xác suất vỡ nợ, phân tích cảm xúc và đưa ra cảnh báo"),
    ]
    how_items_en = [
        ("📥", "Data collection", "Gather financial data and related news from multiple sources"),
        ("🧮", "Processing & selection", "Standardise, clean and select the most relevant indicators"),
        ("🤖", "Model training", "Train LightGBM, XGBoost, CatBoost and AdaBoost models"),
        ("💡", "Scoring & insights", "Compute default probabilities, analyse sentiment and provide alerts"),
    ]
    if lang == 'vi':
        st.markdown(how_title_vi)
        items = how_items_vi
    else:
        st.markdown(how_title_en)
        items = how_items_en
    cols = st.columns(len(items))
    for col, (icon, title, desc) in zip(cols, items):
        col.markdown(f"#### {icon} {title}")
        col.markdown(f"<p style='font-size:0.85rem; line-height:1.3;'>{desc}</p>", unsafe_allow_html=True)
    # Encourage users to read more about the process in the glossary
    more_text_vi = "Bạn có thể tìm hiểu chi tiết từng bước trong tab Glossary."
    more_text_en = "You can read more about each step in the Glossary tab."
    st.markdown(more_text_vi if lang == 'vi' else more_text_en)

    # -------------------------------------------------------------------------
    # If there is no raw data after filtering, show an info message and exit
    if raw_filtered.empty:
        st.info(get_text('warning_no_data', lang))
        return

    # -------------------------------------------------------------------------
    # Top companies by selected metric
    # Provide controls to choose the ranking criterion and number of companies
    # displayed.  We aggregate data at the company level for the selected
    # year and then sort accordingly.  When revenue or net profit columns
    # vary in name, we detect the appropriate column names and convert values
    # using the helper to_num().  If the required columns are missing, the
    # table will gracefully degrade.
    with st.container():
        # Determine available columns for revenue and net profit
        rev_col_candidates = ['Net Sales', 'Revenue', 'Revenue (Bn. VND)']
        np_col_candidates = ['Net Profit For the Year', 'Net Profit']
        rev_col = None
        for c in rev_col_candidates:
            if c in raw_filtered.columns:
                rev_col = c
                break
        np_col = None
        for c in np_col_candidates:
            if c in raw_filtered.columns:
                np_col = c
                break
        # Compute aggregated metrics for the selected year
        temp_df = year_filtered_df.copy()
        # Safely convert columns if they exist
        if 'TOTAL ASSETS (Bn. VND)' in temp_df.columns:
            temp_df['TotalAssets'] = temp_df['TOTAL ASSETS (Bn. VND)'].apply(to_num)
        if rev_col is not None:
            temp_df['Revenue'] = temp_df[rev_col].apply(to_num)
        if np_col is not None:
            temp_df['NetProfit'] = temp_df[np_col].apply(to_num)
        # Drop rows with missing key metrics
        metrics = ['TotalAssets', 'Revenue', 'NetProfit']
        # Group by ticker and sum values (for aggregated yearly totals)
        if not temp_df.empty:
            grouped = temp_df.groupby('Ticker')[metrics].sum(numeric_only=True)
            grouped = grouped.reset_index()
        else:
            grouped = pd.DataFrame(columns=['Ticker'] + metrics)
        # User selects sorting metric
        sort_options_vi = {
            'TotalAssets': 'Tổng tài sản',
            'Revenue': 'Doanh thu',
            'NetProfit': 'Lợi nhuận ròng'
        }
        sort_options_en = {
            'TotalAssets': 'Total assets',
            'Revenue': 'Revenue',
            'NetProfit': 'Net profit'
        }
        sort_options = sort_options_vi if lang == 'vi' else sort_options_en
        sort_metric = st.selectbox(
            "Sắp xếp theo" if lang == 'vi' else "Sort by",
            options=list(sort_options.keys()),
            format_func=lambda x: sort_options[x],
            key='dashboard_sort_metric'
        )
        # Number of companies to show
        top_options = [5, 10, 15, 20]
        default_top_idx = 0
        top_n = st.selectbox(
            "Số doanh nghiệp hiển thị" if lang == 'vi' else "Number of companies to show",
            options=top_options,
            index=default_top_idx,
            key='dashboard_top_n_select'
        )
        # Sort and select top n
        if not grouped.empty and sort_metric in grouped.columns:
            grouped_sorted = grouped.sort_values(sort_metric, ascending=False).head(top_n)
            # Format numbers for display
            display_df = grouped_sorted.copy()
            if 'TotalAssets' in display_df.columns:
                display_df['TotalAssets'] = display_df['TotalAssets'].apply(lambda x: f"{x:,.2f} bn VND" if pd.notna(x) else '-')
            if 'Revenue' in display_df.columns:
                display_df['Revenue'] = display_df['Revenue'].apply(lambda x: f"{x:,.2f} bn VND" if pd.notna(x) else '-')
            if 'NetProfit' in display_df.columns:
                display_df['NetProfit'] = display_df['NetProfit'].apply(lambda x: f"{x:,.2f} bn VND" if pd.notna(x) else '-')
            title_txt = ("Top doanh nghiệp theo {} năm {}" if lang == 'vi' else "Top companies by {} in {}")
            sort_label = sort_options[sort_metric]
            st.subheader(title_txt.format(sort_label, selected_year))
            st.dataframe(display_df, hide_index=True, use_container_width=True, key='dashboard_top_companies_table')
        else:
            st.info("Không có dữ liệu để hiển thị danh sách doanh nghiệp" if lang == 'vi' else "No data available for the company ranking")

    # -------------------------------------------------------------------------
    # Revenue and net profit trends across years
    # Allow the user to choose the chart type (line or bar) and whether to
    # display median values and min–max ranges alongside the mean.  We use
    # the filtered raw data so trends reflect the selected exchange and sector.
    trend_container = st.container()
    with trend_container:
        chart_type = st.radio(
            "Kiểu biểu đồ" if lang == 'vi' else "Chart type",
            options=['Line', 'Bar'],
            index=0,
            format_func=lambda x: ("Đường" if x == 'Line' and lang == 'vi' else ("Cột" if x == 'Bar' and lang == 'vi' else x)),
            horizontal=True,
            key='dashboard_chart_type'
        )
        show_median = st.checkbox(
            "Hiển thị trung vị" if lang == 'vi' else "Show median",
            value=False,
            key='dashboard_show_median'
        )
        show_range = st.checkbox(
            "Hiển thị phạm vi (min–max)" if lang == 'vi' else "Show range (min–max)",
            value=False,
            key='dashboard_show_range'
        )
        # Prepare data
        agg_df = raw_filtered.copy()
        # Identify revenue and net profit columns
        rev_col = None
        for c in ['Net Sales', 'Revenue', 'Revenue (Bn. VND)']:
            if c in agg_df.columns:
                rev_col = c
                break
        np_col = None
        for c in ['Net Profit For the Year', 'Net Profit']:
            if c in agg_df.columns:
                np_col = c
                break
        if rev_col is not None:
            agg_df['Revenue'] = agg_df[rev_col].apply(to_num)
        else:
            agg_df['Revenue'] = np.nan
        if np_col is not None:
            agg_df['NetProfit'] = agg_df[np_col].apply(to_num)
        else:
            agg_df['NetProfit'] = np.nan
        # Group by year and compute statistics
        summary_mean = agg_df.groupby('Year')[['Revenue','NetProfit']].mean().reset_index()
        summary_median = agg_df.groupby('Year')[['Revenue','NetProfit']].median().reset_index() if show_median else None
        summary_min = agg_df.groupby('Year')[['Revenue','NetProfit']].min().reset_index() if show_range else None
        summary_max = agg_df.groupby('Year')[['Revenue','NetProfit']].max().reset_index() if show_range else None
        years_list = summary_mean['Year'].astype(str).tolist()
        fig = go.Figure()
        # Choose bar or line mode
        if chart_type == 'Bar':
            fig.add_trace(go.Bar(x=years_list, y=summary_mean['Revenue'], name=get_text('metric_revenue', lang), marker_color='#60A5FA'))
            fig.add_trace(go.Bar(x=years_list, y=summary_mean['NetProfit'], name=get_text('metric_net_profit', lang), marker_color='#FBBF24'))
        else:
            fig.add_trace(go.Scatter(x=years_list, y=summary_mean['Revenue'], name=get_text('metric_revenue', lang), mode='lines+markers', line=dict(color='#60A5FA')))
            fig.add_trace(go.Scatter(x=years_list, y=summary_mean['NetProfit'], name=get_text('metric_net_profit', lang), mode='lines+markers', line=dict(color='#FBBF24')))
        # Add median traces if selected
        if show_median and summary_median is not None:
            if chart_type == 'Bar':
                fig.add_trace(go.Bar(x=years_list, y=summary_median['Revenue'], name=("Trung vị doanh thu" if lang == 'vi' else "Median revenue"), marker_color='#2563EB', opacity=0.5))
                fig.add_trace(go.Bar(x=years_list, y=summary_median['NetProfit'], name=("Trung vị lợi nhuận" if lang == 'vi' else "Median net profit"), marker_color='#D97706', opacity=0.5))
            else:
                fig.add_trace(go.Scatter(x=years_list, y=summary_median['Revenue'], name=("Trung vị doanh thu" if lang == 'vi' else "Median revenue"), mode='lines+markers', line=dict(dash='dash', color='#2563EB')))
                fig.add_trace(go.Scatter(x=years_list, y=summary_median['NetProfit'], name=("Trung vị lợi nhuận" if lang == 'vi' else "Median net profit"), mode='lines+markers', line=dict(dash='dash', color='#D97706')))
        # Add range (min-max) as filled area
        if show_range and summary_min is not None and summary_max is not None:
            # Revenue range shading
            fig.add_trace(go.Scatter(
                x=years_list + years_list[::-1],
                y=summary_max['Revenue'].tolist() + summary_min['Revenue'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(16, 185, 129, 0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=True,
                name=("Doanh thu (min–max)" if lang == 'vi' else "Revenue (min–max)")
            ))
            # Net profit range shading
            fig.add_trace(go.Scatter(
                x=years_list + years_list[::-1],
                y=summary_max['NetProfit'].tolist() + summary_min['NetProfit'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(234, 179, 8, 0.2)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=True,
                name=("Lợi nhuận (min–max)" if lang == 'vi' else "Net profit (min–max)")
            ))
        fig.update_layout(
            title=("Xu hướng doanh thu và lợi nhuận" if lang == 'vi' else "Revenue & net profit trend"),
            height=350,
            barmode='group' if chart_type == 'Bar' else 'overlay',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis_title=("Năm" if lang == 'vi' else "Year"),
            yaxis_title=("Giá trị (bn VND)" if lang == 'vi' else "Value (bn VND)")
        )
        st.plotly_chart(fig, use_container_width=True, key='dashboard_avg_chart')

    # -------------------------------------------------------------------------
    # Market capitalisation gauge (approximation)
    # Estimate the market capitalisation by summing total assets of all companies
    # in the selected year and converting to USD.  Compare this against
    # Vietnam's nominal GDP for that year to compute the market cap/GDP ratio.
    try:
        total_assets = 0.0
        if 'TOTAL ASSETS (Bn. VND)' in year_filtered_df.columns:
            total_assets = year_filtered_df['TOTAL ASSETS (Bn. VND)'].apply(to_num).sum()
        # Convert bn VND to bn USD (approx 1 bn VND ≈ 0.0000435 bn USD)
        total_assets_usd = total_assets * 0.0000435
        # Nominal GDP data in billions of USD (approximate values)
        GDP_USD = {
            2016: 257.096, 2017: 281.354, 2018: 310.106, 2019: 334.365,
            2020: 346.616, 2021: 366.475, 2022: 410.324, 2023: 429.717,
            2024: 450.0, 2025: 470.0
        }
        gdp_usd = GDP_USD.get(int(selected_year), GDP_USD.get(max(GDP_USD.keys()))) if selected_year is not None else GDP_USD.get(max(GDP_USD.keys()))
        market_share = (total_assets_usd / gdp_usd * 100) if gdp_usd else 0.0
    except Exception:
        total_assets = 0.0
        total_assets_usd = 0.0
        gdp_usd = None
        market_share = 0.0
    # Display gauge and supporting metrics
    gauge_title = "Vốn hoá thị trường/GDP" if lang == 'vi' else "Market cap/GDP"
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=market_share,
        number={"suffix": "%"},
        title={"text": gauge_title},
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
    # Show numerical values of total assets and GDP for context
    assets_text = f"Tổng tài sản: {total_assets_usd:,.2f} bn USD" if lang != 'vi' else f"Tổng tài sản: {total_assets:,.2f} tỷ VND (≈ {total_assets_usd:,.2f} tỷ USD)"
    gdp_text = f"GDP: {gdp_usd:,.2f} bn USD" if lang != 'vi' else f"GDP: {gdp_usd:,.2f} tỷ USD"
    st.caption(assets_text)
    st.caption(gdp_text)

    # ---------------------------------------------------------------------
    # Top sectors by number of listed companies
    # Use the filtered features dataframe to compute the number of unique
    # companies per sector.  Allow the user to select how many sectors to
    # display and show both counts and percentage contributions.
    leading_sector = None
    if 'Sector' in feats_filtered.columns and not feats_filtered.empty:
        sector_counts = feats_filtered.groupby('Sector')['Ticker'].nunique().sort_values(ascending=False)
        # User control for number of sectors to display
        sec_options = [5, 10, 15, len(sector_counts)]
        sec_n = st.selectbox(
            "Số ngành hiển thị" if lang == 'vi' else "Number of sectors to show",
            options=sec_options,
            index=0,
            key='dashboard_top_sector_n'
        )
        top_sector_counts = sector_counts.head(sec_n)
        # Compute percentages
        total_companies = sector_counts.sum()
        sector_percent = (top_sector_counts / total_companies * 100).round(2)
        sector_labels = top_sector_counts.index.tolist()
        counts = top_sector_counts.values.tolist()
        percentages = sector_percent.values.tolist()
        # Set leading sector for narrative
        if sector_labels:
            leading_sector = sector_labels[0]
        fig_sector = go.Figure()
        fig_sector.add_trace(go.Bar(x=sector_labels, y=counts, name=("Số công ty" if lang == 'vi' else "Company count"), marker_color='#3B82F6'))
        fig_sector.add_trace(go.Scatter(x=sector_labels, y=percentages, name=("Tỉ lệ (%)" if lang == 'vi' else "Percentage (%)"), yaxis='y2', mode='markers+lines', marker=dict(color='#F97316')))
        fig_sector.update_layout(
            title=("Top ngành theo số công ty niêm yết" if lang == 'vi' else "Top sectors by number of listed companies"),
            xaxis_title=("Ngành" if lang == 'vi' else "Sector"),
            yaxis=dict(title=("Số lượng công ty" if lang == 'vi' else "Number of companies")),
            yaxis2=dict(title="%", overlaying='y', side='right'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            height=350
        )
        st.plotly_chart(fig_sector, use_container_width=True, key='dashboard_sector_bar')
    else:
        st.info("Không có dữ liệu ngành để hiển thị" if lang == 'vi' else "No sector data available to display")

    # -------------------------------------------------------------------------
    # Narrative summary
    # Summarise the latest year's average revenue and profit along with growth rates.
    rev_growth = np.nan
    np_growth = np.nan
    # Use summary_mean from trend section for growth calculation
    # Determine growth relative to previous year if available
    years_sorted = summary_mean['Year'].sort_values().tolist()
    if len(years_sorted) >= 2:
        last_year = years_sorted[-1]
        prev_year = years_sorted[-2]
        last_row = summary_mean[summary_mean['Year'] == last_year]
        prev_row = summary_mean[summary_mean['Year'] == prev_year]
        if not last_row.empty and not prev_row.empty:
            prev_rev = prev_row['Revenue'].values[0]
            curr_rev = last_row['Revenue'].values[0]
            prev_np = prev_row['NetProfit'].values[0]
            curr_np = last_row['NetProfit'].values[0]
            rev_growth = ((curr_rev - prev_rev) / prev_rev) if prev_rev else np.nan
            np_growth = ((curr_np - prev_np) / prev_np) if prev_np else np.nan
    # Compose narrative
    if lang == 'vi':
        narrative = f"**Tổng quan:** Năm {selected_year}, doanh thu trung bình của các doanh nghiệp đạt {summary_mean.iloc[-1]['Revenue']:,.2f} tỷ đồng và lợi nhuận ròng trung bình {summary_mean.iloc[-1]['NetProfit']:,.2f} tỷ đồng."
        if not np.isnan(rev_growth):
            narrative += f" Doanh thu trung bình {'tăng' if rev_growth>=0 else 'giảm'} {abs(rev_growth)*100:.1f}% so với năm trước."
        if not np.isnan(np_growth):
            narrative += f" Lợi nhuận ròng trung bình {'tăng' if np_growth>=0 else 'giảm'} {abs(np_growth)*100:.1f}% so với năm trước."
        # Additional comment comparing sector proportions
        if leading_sector:
            narrative += f" Ngành dẫn đầu về số lượng công ty niêm yết là {leading_sector}."
        narrative += " Bạn có thể nhấp vào các tab khác để xem chi tiết hơn về từng doanh nghiệp hoặc chỉ số tài chính."
    else:
        narrative = f"**Overview:** In {selected_year}, the average company revenue was {summary_mean.iloc[-1]['Revenue']:,.2f} bn VND and average net profit {summary_mean.iloc[-1]['NetProfit']:,.2f} bn VND."
        if not np.isnan(rev_growth):
            narrative += f" Average revenue {'increased' if rev_growth>=0 else 'decreased'} by {abs(rev_growth)*100:.1f}% from the previous year."
        if not np.isnan(np_growth):
            narrative += f" Average net profit {'increased' if np_growth>=0 else 'decreased'} by {abs(np_growth)*100:.1f}% from the previous year."
        if leading_sector:
            narrative += f" The sector with the most listed companies is {leading_sector}."
        narrative += " Explore other tabs for detailed company or financial indicator analysis."
    st.markdown(narrative)