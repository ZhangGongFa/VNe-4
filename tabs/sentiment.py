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
    Render the Sentiment Analysis tab with enhanced features.
    """
    lang = st.session_state.get('current_lang', 'vi')
    
    st.subheader(get_text("sentiment_header", lang))
    
    # --- Simulated Sentiment Data ---
    # In a real application, this would be fetched from a news/sentiment API
    
    # Calculate average sentiment score from sample data
    news_data_raw = [
        {"date": "2024-11-05", "source": "CafeF", "title": "Công ty công bố kết quả Q3 vượt kỳ vọng", "sentiment": 0.85},
        {"date": "2024-11-03", "source": "VnEconomy", "title": "Ký hợp đồng cung cấp với khách hàng mới", "sentiment": 0.72},
        {"date": "2024-10-28", "source": "Vietstock", "title": "Kế hoạch mở rộng sản xuất được phê duyệt", "sentiment": 0.68},
        {"date": "2024-10-20", "source": "Báo Đầu Tư", "title": "Tăng giá cổ phiếu do kết quả kinh doanh tốt", "sentiment": 0.75},
        {"date": "2024-10-15", "source": "Thanh Niên", "title": "Phát hành cổ phiếu thưởng cho cổ đông", "sentiment": 0.60},
        {"date": "2024-10-10", "source": "Tuổi Trẻ", "title": "Rủi ro cạnh tranh gia tăng trong ngành", "sentiment": 0.30},
        {"date": "2024-10-05", "source": "Lao Động", "title": "Biến động giá nguyên vật liệu đầu vào", "sentiment": 0.45},
    ]
    
    news_df = pd.DataFrame(news_data_raw)
    sentiment_score = news_df["sentiment"].mean()
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        get_text("sentiment_tab_news", lang),
        get_text("sentiment_tab_analysis", lang),
        get_text("sentiment_tab_assessment", lang)
    ])
    
    # ==================== TAB 1: RECENT NEWS ====================
    with tab1:
        st.markdown(f"### {get_text('news_title', lang).replace('[TICKER]', ticker)}")
        
        # Display news in a table format
        news_df["Tình Cảm"] = news_df["sentiment"].apply(lambda x: "Rất Tích Cực" if x > 0.8 else ("Tích Cực" if x > 0.6 else ("Trung Lập" if x > 0.4 else "Tiêu Cực")))
        
        display_df = news_df[["date", "source", "title", "Tình Cảm"]].rename(columns={
            "date": get_text("sentiment_col_date", lang),
            "source": get_text("sentiment_col_source", lang),
            "title": get_text("sentiment_col_title", lang),
            "Tình Cảm": get_text("sentiment_col_sentiment", lang)
        })
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Sentiment trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=news_df["date"],
            y=news_df["sentiment"],
            mode='lines+markers',
            name=get_text("sentiment_chart_trend_name", lang),
            line=dict(color='rgba(10, 102, 194, 0.8)', width=3),
            marker=dict(size=10),
            fill='tozeroy'
        ))
        fig.update_layout(
            title=get_text("sentiment_chart_trend_title", lang),
            xaxis_title=get_text("sentiment_col_date", lang),
            yaxis_title=get_text("sentiment_metric_score", lang),
            height=350,
            yaxis=dict(range=[0, 1])
        )
        st.plotly_chart(fig, use_container_width=True, key="sentiment_trend_chart")
    
    # ==================== TAB 2: SENTIMENT ANALYSIS ====================
    with tab2:
        st.markdown(f"### {get_text('sentiment_analysis_title', lang)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**" + get_text("sentiment_dist_title", lang) + "**")
            sentiment_counts = news_df["Tình Cảm"].value_counts().reset_index()
            sentiment_counts.columns = ["label", "count"]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=sentiment_counts["label"], 
                values=sentiment_counts["count"], 
                hole=.3,
                marker=dict(colors=['#3B82F6', '#22C55E', '#F59E0B', '#EF4444']) # Positive, Very Positive, Neutral, Negative
            )])
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True, key="sentiment_dist_chart")
        
        with col2:
            st.markdown("**" + get_text("sentiment_factors_title", lang) + "**")
            factors_data = {
                get_text("sentiment_factor_name", lang): [
                    get_text("sentiment_factor_biz_results", lang),
                    get_text("sentiment_factor_product_dev", lang),
                    get_text("sentiment_factor_industry", lang),
                    get_text("sentiment_factor_risk_mgmt", lang),
                    get_text("sentiment_factor_outlook", lang)
                ],
                get_text("sentiment_factor_impact", lang): [35, 25, 20, 12, 8]
            }
            
            fig_bar = go.Figure(data=[go.Bar(
                y=factors_data[get_text("sentiment_factor_name", lang)],
                x=factors_data[get_text("sentiment_factor_impact", lang)],
                orientation='h',
                marker_color='rgba(10, 102, 194, 0.8)',
                text=[f"{v}%" for v in factors_data[get_text("sentiment_factor_impact", lang)]],
                textposition='outside'
            )])
            fig_bar.update_layout(
                height=350,
                xaxis_title=get_text("sentiment_factor_impact", lang)
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="sentiment_factors_chart")
        
        # Detailed sentiment analysis table
        st.markdown("**" + get_text("sentiment_analysis_detail_title", lang) + "**")
        analysis_data = {
            get_text("sentiment_category_name", lang): [
                get_text("sentiment_category_financial", lang),
                get_text("sentiment_category_operations", lang),
                get_text("sentiment_category_market", lang),
                get_text("sentiment_category_management", lang),
                get_text("sentiment_category_risk", lang)
            ],
            get_text("sentiment_category_avg_score", lang): [0.78, 0.72, 0.65, 0.70, 0.55],
            get_text("sentiment_category_trend", lang): [
                get_text("sentiment_trend_up", lang),
                get_text("sentiment_trend_stable", lang),
                get_text("sentiment_trend_down", lang),
                get_text("sentiment_trend_up", lang),
                get_text("sentiment_trend_down", lang)
            ]
        }
        analysis_df = pd.DataFrame(analysis_data)
        st.dataframe(analysis_df, use_container_width=True, hide_index=True, key="sentiment_analysis_table")
    
    # ==================== TAB 3: OVERALL ASSESSMENT ====================
    with tab3:
        st.markdown(f"### {get_text('sentiment_assessment_title', lang)}")
        
        # Simple Assessment Logic
        if sentiment_score > 0.7:
            assessment_text = get_text("sentiment_assess_high", lang).format(ticker=ticker)
            color = "green"
        elif sentiment_score > 0.5:
            assessment_text = get_text("sentiment_assess_medium", lang).format(ticker=ticker)
            color = "orange"
        else:
            assessment_text = get_text("sentiment_assess_low", lang).format(ticker=ticker)
            color = "red"
            
        st.markdown(f"""
        <div style="border: 2px solid {color}; border-radius: 10px; padding: 15px; background-color: #F8FAFC;">
            <p style="margin-bottom: 0;">{assessment_text}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Key metrics summary
        st.markdown("**" + get_text("sentiment_key_metrics_title", lang) + "**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(get_text("sentiment_metric_avg_score", lang), f"{sentiment_score:.2f}", "+0.05")
        
        with col2:
            positive_news_pct = news_df[news_df["sentiment"] > 0.6].shape[0] / news_df.shape[0]
            st.metric(get_text("sentiment_metric_positive_pct", lang), f"{positive_news_pct:.0%}", "+5%")
        
        with col3:
            st.metric(get_text("sentiment_metric_confidence", lang), get_text("sentiment_confidence_high", lang), get_text("sentiment_trend_stable", lang))
        
        with col4:
            st.metric(get_text("sentiment_metric_trend", lang), get_text("sentiment_trend_up", lang), "+2.5%")
