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
        
        # Sample news data
        news_data = {
            "Ngày" if lang == "vi" else "Date": [
                "2024-11-05", "2024-11-03", "2024-10-28", "2024-10-20", "2024-10-15"
            ],
            "Tiêu Đề" if lang == "vi" else "Title": [
                "Công ty công bố kết quả Q3 vượt kỳ vọng" if lang == "vi" else "Company announces Q3 results beating expectations",
                "Ký hợp đồng cung cấp với khách hàng mới" if lang == "vi" else "Signed supply contract with new customer",
                "Kế hoạch mở rộng sản xuất được phê duyệt" if lang == "vi" else "Production expansion plan approved",
                "Tăng giá cổ phiếu do kết quả kinh doanh tốt" if lang == "vi" else "Stock price increase due to strong business results",
                "Phát hành cổ phiếu thưởng cho cổ đông" if lang == "vi" else "Dividend stock issuance to shareholders"
            ],
            "Điểm Tình Cảm" if lang == "vi" else "Sentiment Score": [
                0.85, 0.72, 0.68, 0.75, 0.60
            ],
            "Tình Cảm" if lang == "vi" else "Sentiment": [
                "Rất Tích Cực" if lang == "vi" else "Very Positive",
                "Tích Cực" if lang == "vi" else "Positive",
                "Tích Cực" if lang == "vi" else "Positive",
                "Tích Cực" if lang == "vi" else "Positive",
                "Trung Lập" if lang == "vi" else "Neutral"
            ]
        }
        
        news_df = pd.DataFrame(news_data)
        st.dataframe(news_df, use_container_width=True, hide_index=True, key="sentiment_news_table")
        
        # Sentiment trend chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=news_df["Ngày" if lang == "vi" else "Date"],
            y=news_df["Điểm Tình Cảm" if lang == "vi" else "Sentiment Score"],
            mode='lines+markers',
            name="Điểm Tình Cảm" if lang == "vi" else "Sentiment Score",
            line=dict(color='rgba(10, 102, 194, 0.8)', width=3),
            marker=dict(size=10),
            fill='tozeroy'
        ))
        fig.update_layout(
            title="Xu Hướng Tình Cảm Tin Tức" if lang == "vi" else "News Sentiment Trend",
            xaxis_title="Ngày" if lang == "vi" else "Date",
            yaxis_title="Điểm Tình Cảm" if lang == "vi" else "Sentiment Score",
            height=350,
            yaxis=dict(range=[0, 1])
        )
        st.plotly_chart(fig, use_container_width=True, key="sentiment_trend_chart")
    
    # ==================== TAB 2: SENTIMENT ANALYSIS ====================
    with tab2:
        st.markdown(f"### {get_text('sentiment_analysis_title', lang)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**" + ("Phân Loại Tình Cảm" if lang == "vi" else "Sentiment Distribution") + "**")
            sentiment_dist = {
                "Tình Cảm" if lang == "vi" else "Sentiment": [
                    "Rất Tích Cực" if lang == "vi" else "Very Positive",
                    "Tích Cực" if lang == "vi" else "Positive",
                    "Trung Lập" if lang == "vi" else "Neutral",
                    "Tiêu Cực" if lang == "vi" else "Negative",
                    "Rất Tiêu Cực" if lang == "vi" else "Very Negative"
                ],
                "Số Lượng" if lang == "vi" else "Count": [12, 28, 15, 8, 2]
            }
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=sentiment_dist["Tình Cảm" if lang == "vi" else "Sentiment"],
                values=sentiment_dist["Số Lượng" if lang == "vi" else "Count"],
                marker=dict(colors=['#22C55E', '#3B82F6', '#F59E0B', '#EF4444', '#991B1B'])
            )])
            fig_pie.update_layout(height=350)
            st.plotly_chart(fig_pie, use_container_width=True, key="sentiment_dist_chart")
        
        with col2:
            st.markdown("**" + ("Các Yếu Tố Chính" if lang == "vi" else "Key Factors") + "**")
            factors_data = {
                "Yếu Tố" if lang == "vi" else "Factor": [
                    "Kết Quả Kinh Doanh" if lang == "vi" else "Business Results",
                    "Phát Triển Sản Phẩm" if lang == "vi" else "Product Development",
                    "Tình Hình Ngành" if lang == "vi" else "Industry Situation",
                    "Quản Lý Rủi Ro" if lang == "vi" else "Risk Management",
                    "Triển Vọng Tương Lai" if lang == "vi" else "Future Outlook"
                ],
                "Tác Động (%)" if lang == "vi" else "Impact (%)": [35, 25, 20, 12, 8]
            }
            
            fig_bar = go.Figure(data=[go.Bar(
                y=factors_data["Yếu Tố" if lang == "vi" else "Factor"],
                x=factors_data["Tác Động (%)" if lang == "vi" else "Impact (%)"],
                orientation='h',
                marker_color='rgba(10, 102, 194, 0.8)',
                text=[f"{v}%" for v in factors_data["Tác Động (%)" if lang == "vi" else "Impact (%)"]],
                textposition='outside'
            )])
            fig_bar.update_layout(
                height=350,
                xaxis_title="Tác Động (%)" if lang == "vi" else "Impact (%)"
            )
            st.plotly_chart(fig_bar, use_container_width=True, key="sentiment_factors_chart")
        
        # Detailed sentiment analysis table
        st.markdown("**" + ("Chi Tiết Phân Tích Tình Cảm" if lang == "vi" else "Detailed Sentiment Analysis") + "**")
        analysis_data = {
            "Danh Mục" if lang == "vi" else "Category": [
                "Tài Chính" if lang == "vi" else "Financial",
                "Hoạt Động" if lang == "vi" else "Operations",
                "Thị Trường" if lang == "vi" else "Market",
                "Quản Lý" if lang == "vi" else "Management",
                "Rủi Ro" if lang == "vi" else "Risk"
            ],
            "Điểm Trung Bình" if lang == "vi" else "Average Score": [0.78, 0.72, 0.65, 0.70, 0.55],
            "Xu Hướng" if lang == "vi" else "Trend": [
                "↑ Tăng" if lang == "vi" else "↑ Up",
                "→ Ổn Định" if lang == "vi" else "→ Stable",
                "↓ Giảm" if lang == "vi" else "↓ Down",
                "↑ Tăng" if lang == "vi" else "↑ Up",
                "↓ Giảm" if lang == "vi" else "↓ Down"
            ]
        }
        analysis_df = pd.DataFrame(analysis_data)
        st.dataframe(analysis_df, use_container_width=True, hide_index=True, key="sentiment_analysis_table")
    
    # ==================== TAB 3: OVERALL ASSESSMENT ====================
    with tab3:
        st.markdown(f"### {get_text('sentiment_assessment_title', lang)}")
        
        if lang == "vi":
            st.markdown("""
            **Đánh Giá Tổng Thể:**
            
            Tình cảm thị trường đối với công ty hiện tại là **Tích Cực** với điểm trung bình **0.70/1.0**.
            
            **Điểm Mạnh:**
            - Kết quả kinh doanh Q3 vượt kỳ vọng, tăng niềm tin nhà đầu tư
            - Ký hợp đồng cung cấp với khách hàng mới mở rộng cơ hội phát triển
            - Kế hoạch mở rộng sản xuất được phê duyệt, cho thấy tầm nhìn dài hạn
            - Chính sách cổ tức tốt duy trì sự hỗ trợ từ cổ đông
            
            **Điểm Yếu:**
            - Một số lo ngại về tình hình ngành trong bối cảnh kinh tế vĩ mô
            - Rủi ro từ biến động giá nguyên liệu đầu vào
            - Cạnh tranh tăng từ các đối thủ mới
            
            **Khuyến Nghị:**
            - Tiếp tục cải thiện kết quả kinh doanh để duy trì niềm tin nhà đầu tư
            - Tăng cường quản lý rủi ro và minh bạch hóa thông tin
            - Phát triển các sản phẩm mới để tăng cạnh tranh
            - Duy trì chính sách cổ tức hấp dẫn
            """)
        else:
            st.markdown("""
            **Overall Assessment:**
            
            Market sentiment towards the company is currently **Positive** with an average score of **0.70/1.0**.
            
            **Strengths:**
            - Q3 business results exceeded expectations, boosting investor confidence
            - Signed supply contract with new customer expands growth opportunities
            - Production expansion plan approved demonstrates long-term vision
            - Good dividend policy maintains shareholder support
            
            **Weaknesses:**
            - Some concerns about industry situation in current macroeconomic context
            - Risk from volatility in raw material prices
            - Increasing competition from new competitors
            
            **Recommendations:**
            - Continue improving business results to maintain investor confidence
            - Strengthen risk management and information transparency
            - Develop new products to increase competitiveness
            - Maintain attractive dividend policy
            """)
        
        # Key metrics summary
        st.markdown("**" + ("Chỉ Số Chính" if lang == "vi" else "Key Metrics") + "**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Điểm Tình Cảm Trung Bình" if lang == "vi" else "Avg Sentiment Score", "0.70", "+0.05")
        
        with col2:
            st.metric("Tin Tức Tích Cực (%)" if lang == "vi" else "Positive News (%)", "80%", "+5%")
        
        with col3:
            st.metric("Độ Tin Cậy" if lang == "vi" else "Confidence", "Cao" if lang == "vi" else "High", "Ổn Định" if lang == "vi" else "Stable")
        
        with col4:
            st.metric("Xu Hướng" if lang == "vi" else "Trend", "Tăng" if lang == "vi" else "Up", "+2.5%")
