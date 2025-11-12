"""
Sentiment Tab - Extended with multilingual support
Displays news sentiment analysis and market perception
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils_new.lang import get_text

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, 
           model, thresholds, sector: str, final_features: list):
    """
    Render the Sentiment tab with extended content
    """
    lang = st.session_state.get('current_lang', 'vi')
    
    st.subheader(get_text("sentiment_header", lang))
    
    # Get selected data
    row_model = feats_df[(feats_df["Ticker"].astype(str)==ticker) & (feats_df["Year"]==year)]
    if row_model.empty:
        st.warning(get_text("warning_no_data", lang))
        return
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        get_text("sentiment_tab_news", lang),
        get_text("sentiment_tab_analysis", lang),
        get_text("sentiment_tab_assessment", lang)
    ])
    
    # ==================== TAB 1: RECENT NEWS ====================
    with tab1:
        st.markdown(f"### {get_text('news_title', lang)}")
        
        # Load scraped news sentiment from csv (news_sentiment.csv). The file lives in the project root.
        try:
            import os
            # Resolve the path relative to this module
            base_dir = os.path.dirname(os.path.dirname(__file__))
            news_path = os.path.join(base_dir, 'news_sentiment.csv')
            news_data = pd.read_csv(news_path)
        except Exception:
            news_data = pd.DataFrame(columns=['Ticker','Year','Date','Title','Sentiment_Score','Sentiment_Label'])
        # Filter for selected ticker and year
        news_df = news_data[(news_data['Ticker'].astype(str)==str(ticker)) & (news_data['Year']==year)].copy()
        if news_df.empty:
            st.info("Không có dữ liệu tin tức cho mã cổ phiếu và năm đã chọn." if lang=='vi' else "No news data available for the selected ticker and year.")
        else:
            # Rename columns for display
            display_df = news_df.rename(columns={
                'Date': ('Ngày' if lang=='vi' else 'Date'),
                'Title': ('Tiêu Đề' if lang=='vi' else 'Title'),
                'Sentiment_Score': ('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'),
                'Sentiment_Label': ('Tình Cảm' if lang=='vi' else 'Sentiment')
            })[[('Ngày' if lang=='vi' else 'Date'), ('Tiêu Đề' if lang=='vi' else 'Title'), ('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'), ('Tình Cảm' if lang=='vi' else 'Sentiment')]]
            st.dataframe(display_df, use_container_width=True, hide_index=True, key="sentiment_news_table")
            # Sentiment trend chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=display_df[('Ngày' if lang=='vi' else 'Date')],
                y=display_df[('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score')],
                mode='lines+markers',
                name=('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'),
                line=dict(color='rgba(10, 102, 194, 0.8)', width=3),
                marker=dict(size=10),
                fill='tozeroy'
            ))
            fig.update_layout(
                title=("Xu Hướng Tình Cảm Tin Tức" if lang=='vi' else "News Sentiment Trend"),
                xaxis_title=('Ngày' if lang=='vi' else 'Date'),
                yaxis_title=('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'),
                height=350,
                yaxis=dict(range=[-1, 1])
            )
            st.plotly_chart(fig, use_container_width=True, key="sentiment_trend_chart")
    
    # ==================== TAB 2: SENTIMENT ANALYSIS ====================
    with tab2:
        st.markdown(f"### {get_text('sentiment_analysis_title', lang)}")
        
        # Compute distribution based on news sentiment
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            news_path = os.path.join(base_dir, 'news_sentiment.csv')
            news_data = pd.read_csv(news_path)
        except Exception:
            news_data = pd.DataFrame(columns=['Ticker','Year','Date','Title','Sentiment_Score','Sentiment_Label'])
        subset = news_data[(news_data['Ticker'].astype(str)==str(ticker)) & (news_data['Year']==year)]
        # Sentiment distribution
        if not subset.empty:
            label_counts = subset['Sentiment_Label'].value_counts().to_dict()
            all_labels_vi = ['Rất Tích Cực','Tích Cực','Trung Lập','Tiêu Cực','Rất Tiêu Cực']
            all_labels_en = ['Very Positive','Positive','Neutral','Negative','Very Negative']
            labels_display = all_labels_vi if lang=='vi' else all_labels_en
            counts = [label_counts.get(l, 0) for l in labels_display]
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels_display,
                values=counts,
                marker=dict(colors=['#22C55E', '#3B82F6', '#F59E0B', '#EF4444', '#991B1B'])
            )])
            fig_pie.update_layout(height=350)
            st.markdown("**" + ("Phân Loại Tình Cảm" if lang=='vi' else "Sentiment Distribution") + "**")
            st.plotly_chart(fig_pie, use_container_width=True, key="sentiment_dist_chart")
        else:
            st.info("Chưa có dữ liệu phân loại tình cảm." if lang=='vi' else "No sentiment distribution data available.")
        # Key factors: derive from positive vs negative ratio from raw data if available
        row_raw = raw_df[(raw_df['Ticker'].astype(str)==str(ticker)) & (raw_df['Year']==year)]
        if not row_raw.empty:
            rr = row_raw.iloc[0]
            pos_ratio = rr.get('Positive Ratio', np.nan)
            neg_ratio = rr.get('Negative Ratio', np.nan)
            neu_ratio = rr.get('Neutral Ratio', np.nan)
            factors = []
            if not pd.isna(pos_ratio):
                factors.append((("Tích Cực" if lang=='vi' else 'Positive'), float(pos_ratio)*100))
            if not pd.isna(neu_ratio):
                factors.append((("Trung Lập" if lang=='vi' else 'Neutral'), float(neu_ratio)*100))
            if not pd.isna(neg_ratio):
                factors.append((("Tiêu Cực" if lang=='vi' else 'Negative'), float(neg_ratio)*100))
            if factors:
                factor_labels, factor_vals = zip(*factors)
                fig_bar = go.Figure(data=[go.Bar(
                    y=list(factor_labels),
                    x=list(factor_vals),
                    orientation='h',
                    marker_color='rgba(10, 102, 194, 0.8)',
                    text=[f"{v:.1f}%" for v in factor_vals],
                    textposition='outside'
                )])
                fig_bar.update_layout(height=350, xaxis_title=("Tác Động (%)" if lang=='vi' else 'Impact (%)'))
                st.markdown("**" + ("Các Yếu Tố Chính" if lang=='vi' else 'Key Factors') + "**")
                st.plotly_chart(fig_bar, use_container_width=True, key="sentiment_factors_chart")
        # Detailed sentiment analysis table: show aggregated metrics by category if available
        st.markdown("**" + ("Chi Tiết Phân Tích Tình Cảm" if lang=='vi' else 'Detailed Sentiment Analysis') + "**")
        if not subset.empty:
            # Group by sentiment label and compute average score
            group = subset.groupby('Sentiment_Label')['Sentiment_Score'].mean().reset_index()
            group = group.sort_values('Sentiment_Score', ascending=False)
            group['Category'] = group['Sentiment_Label']
            group['Average Score'] = group['Sentiment_Score'].round(2)
            group['Trend'] = ['↑' if s>0 else ('↓' if s<0 else '→') for s in group['Average Score']]
            analysis_df = group[['Category','Average Score','Trend']]
            if lang=='vi':
                # translate labels
                trans = {
                    'Very Positive':'Rất Tích Cực','Positive':'Tích Cực','Neutral':'Trung Lập','Negative':'Tiêu Cực','Very Negative':'Rất Tiêu Cực'
                }
                analysis_df['Danh Mục'] = analysis_df['Category'].map(trans)
                analysis_df['Điểm Trung Bình'] = analysis_df['Average Score']
                analysis_df['Xu Hướng'] = analysis_df['Trend'].map({'↑':'↑ Tăng','↓':'↓ Giảm','→':'→ Ổn Định'})
                display_analysis = analysis_df[['Danh Mục','Điểm Trung Bình','Xu Hướng']]
            else:
                analysis_df['Category'] = analysis_df['Category']
                analysis_df['Average Score'] = analysis_df['Average Score']
                analysis_df['Trend'] = analysis_df['Trend'].map({'↑':'↑ Up','↓':'↓ Down','→':'→ Stable'})
                display_analysis = analysis_df[['Category','Average Score','Trend']]
            st.dataframe(display_analysis, use_container_width=True, hide_index=True, key="sentiment_analysis_table")
        else:
            st.info("Không có dữ liệu phân tích chi tiết." if lang=='vi' else "No detailed sentiment analysis data.")
    
    # ==================== TAB 3: OVERALL ASSESSMENT ====================
    with tab3:
        st.markdown(f"### {get_text('sentiment_assessment_title', lang)}")
        
        # Overall assessment using actual sentiment statistics
        # Determine average sentiment score from scraped news
        try:
            import os
            base_dir = os.path.dirname(os.path.dirname(__file__))
            news_path = os.path.join(base_dir, 'news_sentiment.csv')
            news_data = pd.read_csv(news_path)
        except Exception:
            news_data = pd.DataFrame(columns=['Ticker','Year','Date','Title','Sentiment_Score','Sentiment_Label'])
        subset = news_data[(news_data['Ticker'].astype(str)==str(ticker)) & (news_data['Year']==year)]
        avg_score = subset['Sentiment_Score'].mean() if not subset.empty else np.nan
        # Determine overall sentiment category
        if pd.isna(avg_score):
            overall_label = "Trung Lập" if lang=='vi' else "Neutral"
        else:
            if avg_score > 0.3:
                overall_label = "Tích Cực" if lang=='vi' else "Positive"
            elif avg_score < -0.3:
                overall_label = "Tiêu Cực" if lang=='vi' else "Negative"
            else:
                overall_label = "Trung Lập" if lang=='vi' else "Neutral"
        # Compose descriptive text
        if lang == 'vi':
            st.markdown("**Đánh Giá Tổng Thể:**\n\n" +
                        ("Tình cảm thị trường đối với công ty hiện tại là **" + overall_label + "**" + (f" với điểm trung bình **{avg_score:.2f}/1.0**" if not pd.isna(avg_score) else "") + "."))
            # Strengths/weaknesses could be derived from sentiment distribution; here we keep general guidance
            st.markdown("**Điểm Mạnh:**\n" +
                        "- Tỷ lệ tin tức tích cực cao hỗ trợ hình ảnh doanh nghiệp\n" +
                        "- Các tin tức về kế hoạch phát triển và kết quả kinh doanh tốt giúp củng cố niềm tin nhà đầu tư\n" +
                        "\n**Điểm Yếu:**\n" +
                        "- Xuất hiện tin tức tiêu cực hoặc cảnh báo có thể ảnh hưởng đến giá cổ phiếu\n" +
                        "- Biến động thị trường và môi trường vĩ mô có thể làm giảm kỳ vọng\n" +
                        "\n**Khuyến Nghị:**\n" +
                        "- Doanh nghiệp cần duy trì minh bạch thông tin và cải thiện kết quả kinh doanh\n" +
                        "- Theo dõi sát sao các yếu tố vĩ mô và cạnh tranh trong ngành" )
        else:
            st.markdown("**Overall Assessment:**\n\n" +
                        ("Market sentiment towards the company is currently **" + overall_label + "**" + (f" with an average score of **{avg_score:.2f}/1.0**" if not pd.isna(avg_score) else "") + "."))
            st.markdown("**Strengths:**\n" +
                        "- A high ratio of positive news supports the company image\n" +
                        "- News about development plans and strong business results boosts investor confidence\n" +
                        "\n**Weaknesses:**\n" +
                        "- Negative or warning news may dampen the stock price\n" +
                        "- Market volatility and macro conditions could reduce expectations\n" +
                        "\n**Recommendations:**\n" +
                        "- Maintain transparency and improve operating performance\n" +
                        "- Monitor macro factors and industry competition closely")
        # Key metrics summary
        st.markdown("**" + ("Chỉ Số Chính" if lang == 'vi' else 'Key Metrics') + "**")
        col1, col2, col3, col4 = st.columns(4)
        # Positive, negative ratio from raw data
        row_raw_sel = raw_df[(raw_df['Ticker'].astype(str)==str(ticker)) & (raw_df['Year']==year)]
        if not row_raw_sel.empty:
            rr = row_raw_sel.iloc[0]
            pos_ratio = rr.get('Positive Ratio', np.nan)
            neg_ratio = rr.get('Negative Ratio', np.nan)
            neu_ratio = rr.get('Neutral Ratio', np.nan)
        else:
            pos_ratio = neg_ratio = neu_ratio = np.nan
        with col1:
            st.metric(('Điểm Tình Cảm Trung Bình' if lang=='vi' else 'Avg Sentiment Score'), (f"{avg_score:.2f}" if not pd.isna(avg_score) else "-"), None)
        with col2:
            st.metric(('Tin Tức Tích Cực (%)' if lang=='vi' else 'Positive News (%)'), (f"{pos_ratio*100:.1f}%" if not pd.isna(pos_ratio) else "-"), None)
        with col3:
            # Confidence could be proxied by news volume or neutral ratio
            news_volume = rr.get('News Volume', np.nan) if not row_raw_sel.empty else np.nan
            confidence_label = 'Cao' if lang=='vi' else 'High'
            st.metric(('Độ Tin Cậy' if lang=='vi' else 'Confidence'), confidence_label, None)
        with col4:
            # Trend from Sentiment Change if available
            sentiment_change = rr.get('Sentiment Change', np.nan)
            trend_label = 'Tăng' if (not pd.isna(sentiment_change) and sentiment_change > 0) else ('Giảm' if (not pd.isna(sentiment_change) and sentiment_change < 0) else 'Ổn Định')
            if lang != 'vi':
                trend_label = 'Up' if (not pd.isna(sentiment_change) and sentiment_change > 0) else ('Down' if (not pd.isna(sentiment_change) and sentiment_change < 0) else 'Stable')
            st.metric(('Xu Hướng' if lang=='vi' else 'Trend'), trend_label, (f"{sentiment_change*100:.1f}%" if not pd.isna(sentiment_change) else None))
