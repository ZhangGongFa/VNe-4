
# -*- coding: utf-8 -*-
"""
Upgraded Sentiment Tab
- Friendly empty state with suggestions
- Hover tooltips for counts/ratios
- Cards for Strengths / Weaknesses / Recommendations
- Full bilingual content
"""
import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils_new.lang import get_text

def _friendly_empty(lang: str):
    if lang=="vi":
        st.info("📰 Chưa có tin tức cho lựa chọn hiện tại.\n\n• Hãy thử **năm khác** hoặc **mã khác**.\n• Bạn cũng có thể cập nhật `news_sentiment.csv` để bổ sung dữ liệu.")
    else:
        st.info("📰 No news data for the current selection.\n\n• Try a **different year** or **ticker**.\n• You may also update `news_sentiment.csv` to add more data.")

def _load_news():
    import os
    base_dir = os.path.dirname(os.path.dirname(__file__))
    news_path = os.path.join(base_dir, 'news_sentiment.csv')
    try:
        return pd.read_csv(news_path)
    except Exception:
        return pd.DataFrame(columns=['Ticker','Year','Date','Title','Sentiment_Score','Sentiment_Label'])

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, 
           model, thresholds, sector: str, final_features: list):

    lang = st.session_state.get("current_lang", "vi")
    st.subheader(get_text("sentiment_header", lang) or "Sentiment Analysis")

    news_data = _load_news()
    subset = news_data[(news_data['Ticker'].astype(str)==str(ticker)) & (news_data['Year']==year)].copy()

    # --- Recent news list & time series
    st.markdown("### " + (get_text("news_title", lang) or ("Tin tức gần đây" if lang=="vi" else "Recent News")))
    if subset.empty:
        _friendly_empty(lang)
    else:
        display_df = subset.rename(columns={
            'Date': ('Ngày' if lang=='vi' else 'Date'),
            'Title': ('Tiêu Đề' if lang=='vi' else 'Title'),
            'Sentiment_Score': ('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'),
            'Sentiment_Label': ('Tình Cảm' if lang=='vi' else 'Sentiment')
        })[[('Ngày' if lang=='vi' else 'Date'), ('Tiêu Đề' if lang=='vi' else 'Title'), ('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'), ('Tình Cảm' if lang=='vi' else 'Sentiment')]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Trend
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=display_df[('Ngày' if lang=='vi' else 'Date')],
            y=display_df[('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score')],
            mode='lines+markers',
            hovertemplate="%{x}<br>Score=%{y:.3f}<extra></extra>"
        ))
        fig_trend.update_layout(height=300, title=("Xu hướng điểm tình cảm" if lang=='vi' else "Sentiment score trend"))
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- Analysis tab (distribution)
    st.markdown("### " + ("Phân Tích Tình Cảm" if lang=='vi' else "Sentiment Analysis"))
    if subset.empty:
        _friendly_empty(lang)
    else:
        mapping = {
            'Rất Tích Cực': 'Very Positive','Tích Cực': 'Positive','Trung Lập': 'Neutral','Tiêu Cực': 'Negative','Rất Tiêu Cực': 'Very Negative',
            'Very Positive': 'Very Positive','Positive': 'Positive','Neutral': 'Neutral','Negative': 'Negative','Very Negative': 'Very Negative'
        }
        subset['Canon'] = subset['Sentiment_Label'].map(mapping).fillna(subset['Sentiment_Label'])
        order = ['Very Positive','Positive','Neutral','Negative','Very Negative']
        counts = subset['Canon'].value_counts().reindex(order).fillna(0).astype(int)
        labels_vi = ['Rất Tích Cực','Tích Cực','Trung Lập','Tiêu Cực','Rất Tiêu Cực']
        labels = labels_vi if lang=='vi' else order
        total = int(counts.sum()) if counts.sum() else 1
        fig_pie = go.Figure(data=[go.Pie(
            labels=labels,
            values=counts.values.tolist(),
            hole=0.35,
            hovertemplate="%{label}: %{value} tin (%{percent})<extra></extra>" if lang=='vi' else "%{label}: %{value} articles (%{percent})<extra></extra>"
        )])
        fig_pie.update_layout(height=350, title=("Phân loại tình cảm" if lang=='vi' else "Sentiment distribution"))
        st.plotly_chart(fig_pie, use_container_width=True)

    # --- Overall evaluation cards
    st.markdown("### " + ("Đánh Giá Chung" if lang=='vi' else "Overall Assessment"))
    avg_score = subset['Sentiment_Score'].mean() if not subset.empty else np.nan
    pos_ratio = (subset['Sentiment_Label'].map(lambda x: 1 if 'Tích Cực' in str(x) or 'Positive' in str(x) else 0).mean()) if not subset.empty else np.nan
    neg_ratio = (subset['Sentiment_Label'].map(lambda x: 1 if 'Tiêu Cực' in str(x) or 'Negative' in str(x) else 0).mean()) if not subset.empty else np.nan
    news_vol = len(subset) if not subset.empty else 0

    conf = "Cao" if lang=='vi' else "High"
    if news_vol < 10: conf = "Trung bình" if lang=='vi' else "Medium"
    if news_vol < 3: conf = "Thấp" if lang=='vi' else "Low"
    trend = "Ổn định" if lang=='vi' else "Stable"
    # If yearly change available in raw_df: use 'Sentiment Change'
    row_raw = raw_df[(raw_df['Ticker'].astype(str)==str(ticker)) & (raw_df['Year']==year)]
    if not row_raw.empty and pd.notna(row_raw.iloc[0].get('Sentiment Change')):
        ch = float(row_raw.iloc[0].get('Sentiment Change'))
        if ch > 0: trend = "Tăng" if lang=='vi' else "Up"
        elif ch < 0: trend = "Giảm" if lang=='vi' else "Down"

    # Cards layout
    st.markdown("""
    <style>
    .card{border:1px solid #e5e7eb;border-radius:10px;padding:14px;background:#fff}
    .card h4{margin:0 0 8px 0}
    </style>
    """, unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='card'><h4>{'Điểm mạnh' if lang=='vi' else 'Strengths'}</h4><ul><li>{'Tỷ lệ tin tích cực cao' if lang=='vi' else 'High share of positive news'}</li><li>{'Tin kết quả kinh doanh hỗ trợ niềm tin' if lang=='vi' else 'Earnings-related coverage supports sentiment'}</li></ul></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='card'><h4>{'Điểm yếu' if lang=='vi' else 'Weaknesses'}</h4><ul><li>{'Một số tin tiêu cực/cảnh báo' if lang=='vi' else 'Some negative/warning coverage'}</li><li>{'Tập trung theo chủ đề dễ đảo chiều' if lang=='vi' else 'Topic concentration can reverse quickly'}</li></ul></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='card'><h4>{'Khuyến nghị' if lang=='vi' else 'Recommendations'}</h4><ul><li>{'Theo dõi thêm 1–2 quý' if lang=='vi' else 'Monitor 1–2 more quarters'}</li><li>{'Kết hợp với chỉ số tài chính' if lang=='vi' else 'Complement with financial ratios'}</li></ul></div>", unsafe_allow_html=True)

    # KPIs row (with explanations)
    k1,k2,k3,k4 = st.columns(4)
    with k1:
        st.metric("Avg. score" if lang!='vi' else "Điểm TB", f"{avg_score:.2f}" if not pd.isna(avg_score) else "-")
    with k2:
        st.metric("Positive %" if lang!='vi' else "Tích cực %", f"{pos_ratio*100:.1f}%" if pos_ratio==pos_ratio else "-")
    with k3:
        st.metric("Confidence" if lang!='vi' else "Độ tin cậy", conf,
            help=("Dựa vào số lượng tin trong năm (N>=10: Cao, 3–9: Trung bình, <3: Thấp)" if lang=='vi' else "Based on yearly news volume (N>=10: High, 3–9: Medium, <3: Low)"))
    with k4:
        st.metric("Trend" if lang!='vi' else "Xu hướng", trend,
            help=("Từ cột 'Sentiment Change' theo năm" if lang=='vi' else "Derived from yearly 'Sentiment Change'"))
