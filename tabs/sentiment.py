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
            # Friendly suggestion when no news data is available
            no_data_msg_vi = "Không có dữ liệu tin tức cho mã cổ phiếu và năm đã chọn. Vui lòng thử năm khác hoặc thu thập thêm tin tức."
            no_data_msg_en = "No news data available for the selected ticker and year. Please try another year or collect more news articles."
            st.info(no_data_msg_vi if lang=='vi' else no_data_msg_en)
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
                marker=dict(size=8),
                fill='tozeroy',
                hovertemplate=(
                    ("Ngày: %{x}<br>Điểm: %{y:.2f}" if lang=='vi' else "Date: %{x}<br>Score: %{y:.2f}") + "<extra></extra>"
                )
            ))
            fig.update_layout(
                title=("Xu Hướng Tình Cảm Tin Tức" if lang=='vi' else "News Sentiment Trend"),
                xaxis_title=('Ngày' if lang=='vi' else 'Date'),
                yaxis_title=('Điểm Tình Cảm' if lang=='vi' else 'Sentiment Score'),
                height=350,
                yaxis=dict(range=[-1, 1]),
                xaxis_tickangle=-30
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
            # Normalize sentiment labels to canonical English categories then map to display labels.
            # This ensures that even when the data uses Vietnamese labels, distribution is computed consistently.
            mapping = {
                'Rất Tích Cực': 'Very Positive',
                'Tích Cực': 'Positive',
                'Trung Lập': 'Neutral',
                'Tiêu Cực': 'Negative',
                'Rất Tiêu Cực': 'Very Negative',
                'Very Positive': 'Very Positive',
                'Positive': 'Positive',
                'Neutral': 'Neutral',
                'Negative': 'Negative',
                'Very Negative': 'Very Negative'
            }
            subset_canonical = subset['Sentiment_Label'].map(mapping).fillna(subset['Sentiment_Label'])
            label_counts = subset_canonical.value_counts().to_dict()
            canonical_order = ['Very Positive','Positive','Neutral','Negative','Very Negative']
            counts = [label_counts.get(l, 0) for l in canonical_order]
            total = sum(counts) if sum(counts) > 0 else 1
            labels_display = canonical_order if lang != 'vi' else ['Rất Tích Cực','Tích Cực','Trung Lập','Tiêu Cực','Rất Tiêu Cực']
            # Build pie chart with hover template showing counts and percentages
            fig_pie = go.Figure(data=[go.Pie(
                labels=labels_display,
                values=counts,
                marker=dict(colors=['#22C55E', '#3B82F6', '#F59E0B', '#EF4444', '#991B1B']),
                hovertemplate=(
                    "%{label}: %{value} " + ("bài" if lang=='vi' else "articles") + " (" + "%{percent:.1%}" + ")<extra></extra>"
                )
            )])
            fig_pie.update_layout(height=350)
            st.markdown("**" + ("Phân Loại Tình Cảm" if lang=='vi' else "Sentiment Distribution") + "**")
            st.plotly_chart(fig_pie, use_container_width=True, key="sentiment_dist_chart")
        else:
            # Suggest exploring another year or collecting more news when no distribution data
            no_dist_msg_vi = "Chưa có dữ liệu phân loại tình cảm. Vui lòng thử năm khác hoặc thu thập dữ liệu tin tức."
            no_dist_msg_en = "No sentiment distribution data available. Please try another year or collect more news data."
            st.info(no_dist_msg_vi if lang=='vi' else no_dist_msg_en)
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
                    textposition='outside',
                    hovertemplate="%{y}: %{x:.1f}%<extra></extra>"
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
        # Compose descriptive text with card-style layout for strengths, weaknesses and recommendations
        if lang == 'vi':
            overall_title = "Đánh Giá Tổng Thể"
            strengths_title = "Điểm Mạnh"
            weaknesses_title = "Điểm Yếu"
            recommend_title = "Khuyến Nghị"
            summary_text = f"Tình cảm thị trường đối với công ty hiện tại là **{overall_label}**" + (f" với điểm trung bình **{avg_score:.2f}/1.0**" if not pd.isna(avg_score) else "") + "."
            strengths_bullets = [
                "Tỷ lệ tin tức tích cực cao hỗ trợ hình ảnh doanh nghiệp",
                "Các tin tức về kế hoạch phát triển và kết quả kinh doanh tốt giúp củng cố niềm tin nhà đầu tư"
            ]
            weaknesses_bullets = [
                "Xuất hiện tin tức tiêu cực hoặc cảnh báo có thể ảnh hưởng đến giá cổ phiếu",
                "Biến động thị trường và môi trường vĩ mô có thể làm giảm kỳ vọng"
            ]
            recommendations_bullets = [
                "Doanh nghiệp cần duy trì minh bạch thông tin và cải thiện kết quả kinh doanh",
                "Theo dõi sát sao các yếu tố vĩ mô và cạnh tranh trong ngành"
            ]
        else:
            overall_title = "Overall Assessment"
            strengths_title = "Strengths"
            weaknesses_title = "Weaknesses"
            recommend_title = "Recommendations"
            summary_text = f"Market sentiment towards the company is currently **{overall_label}**" + (f" with an average score of **{avg_score:.2f}/1.0**" if not pd.isna(avg_score) else "") + "."
            strengths_bullets = [
                "A high ratio of positive news supports the company image",
                "News about development plans and strong business results boosts investor confidence"
            ]
            weaknesses_bullets = [
                "Negative or warning news may dampen the stock price",
                "Market volatility and macro conditions could reduce expectations"
            ]
            recommendations_bullets = [
                "Maintain transparency and improve operating performance",
                "Monitor macro factors and industry competition closely"
            ]
        # Display overall summary
        st.markdown(f"**{overall_title}:**\n\n{summary_text}")
        # Draw cards using columns to separate sections
        card_cols = st.columns(3)
        def render_card(col, title, bullets, bg_color, border_color):
            with col:
                bullet_html = ''.join([f"<li>{item}</li>" for item in bullets])
                card_html = f"<div style='background:{bg_color};border:1px solid {border_color};border-radius:8px;padding:12px;margin-bottom:8px;'>" \
                             f"<strong>{title}</strong><ul style='margin-top:4px;margin-bottom:0;padding-left:20px;'>" + bullet_html + "</ul></div>"
                st.markdown(card_html, unsafe_allow_html=True)
        # Define colours for cards (pastel palette)
        if lang == 'vi':
            render_card(card_cols[0], strengths_title, strengths_bullets, '#ECFDF5', '#34D399')
            render_card(card_cols[1], weaknesses_title, weaknesses_bullets, '#FEF2F2', '#F87171')
            render_card(card_cols[2], recommend_title, recommendations_bullets, '#EFF6FF', '#60A5FA')
        else:
            render_card(card_cols[0], strengths_title, strengths_bullets, '#ECFDF5', '#34D399')
            render_card(card_cols[1], weaknesses_title, weaknesses_bullets, '#FEF2F2', '#F87171')
            render_card(card_cols[2], recommend_title, recommendations_bullets, '#EFF6FF', '#60A5FA')
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
            st.metric(
                ('Điểm Tình Cảm Trung Bình' if lang=='vi' else 'Avg Sentiment Score'),
                (f"{avg_score:.2f}" if not pd.isna(avg_score) else "-"),
                None,
                help=(
                    'Điểm trung bình của tất cả tin tức, dao động từ -1 đến 1' if lang=='vi' else 'Average sentiment score of all news articles, ranging from -1 to 1'
                )
            )
        with col2:
            st.metric(
                ('Tin Tức Tích Cực (%)' if lang=='vi' else 'Positive News (%)'),
                (f"{pos_ratio*100:.1f}%" if not pd.isna(pos_ratio) else "-"),
                None,
                help=(
                    'Tỷ lệ phần trăm tin tức tích cực trên tổng số tin tức' if lang=='vi' else 'Percentage of positive news articles relative to total news'
                )
            )
        with col3:
            # Confidence could be proxied by news volume; classify into High/Medium/Low
            news_volume = rr.get('News Volume', np.nan) if not row_raw_sel.empty else np.nan
            if pd.isna(news_volume) or news_volume < 5:
                confidence_label = 'Thấp' if lang=='vi' else 'Low'
            elif news_volume < 15:
                confidence_label = 'Trung Bình' if lang=='vi' else 'Medium'
            else:
                confidence_label = 'Cao' if lang=='vi' else 'High'
            st.metric(
                ('Độ Tin Cậy' if lang=='vi' else 'Confidence'),
                confidence_label,
                None,
                help=(
                    'Độ tin cậy dựa trên khối lượng tin tức: càng nhiều tin tức, điểm càng tin cậy' if lang=='vi' else 'Confidence reflects the news volume: more articles imply a more reliable score'
                )
            )
        with col4:
            # Trend from sentiment change if available
            sentiment_change = rr.get('Sentiment Change', np.nan)
            if lang == 'vi':
                trend_label = 'Tăng' if (not pd.isna(sentiment_change) and sentiment_change > 0) else ('Giảm' if (not pd.isna(sentiment_change) and sentiment_change < 0) else 'Ổn Định')
            else:
                trend_label = 'Up' if (not pd.isna(sentiment_change) and sentiment_change > 0) else ('Down' if (not pd.isna(sentiment_change) and sentiment_change < 0) else 'Stable')
            st.metric(
                ('Xu Hướng' if lang=='vi' else 'Trend'),
                trend_label,
                (f"{sentiment_change*100:.1f}%" if not pd.isna(sentiment_change) else None),
                help=(
                    'Xu hướng cho thấy sự thay đổi điểm tình cảm so với kỳ trước' if lang=='vi' else 'Trend indicates the change in sentiment compared to the previous period'
                )
            )
