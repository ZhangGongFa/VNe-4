"""
Sentiment Analysis Tab
Displays news sentiment and market perception analysis
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta


def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, sector: str):
    """
    Render the Sentiment Analysis tab with news and market perception
    """
    
    st.subheader("📰 Phân Tích Tình Cảm & Tin Tức")
    
    # Create tabs for sentiment analysis
    tab1, tab2, tab3 = st.tabs([
        "Tin Tức Gần Đây",
        "Phân Tích Tình Cảm",
        "Đánh Giá Chung"
    ])
    
    # ==================== TAB 1: RECENT NEWS ====================
    with tab1:
        st.markdown("### Tin Tức Gần Đây (Recent News)")
        st.markdown(f"**Công ty:** {ticker} | **Ngành:** {sector}")
        
        # Sample news data
        news_data = [
            {
                "Ngày": "2024-11-08",
                "Tiêu Đề": "Công ty công bố kết quả quý 3 vượt kỳ vọng",
                "Nguồn": "VNExpress",
                "Tình Cảm": "Tích Cực",
                "Điểm": 0.85
            },
            {
                "Ngày": "2024-11-05",
                "Tiêu Đề": "Ký kết hợp đồng cung cấp với khách hàng lớn",
                "Nguồn": "Cafef",
                "Tình Cảm": "Tích Cực",
                "Điểm": 0.78
            },
            {
                "Ngày": "2024-10-28",
                "Tiêu Đề": "Cảnh báo: Giá nguyên liệu tăng có thể ảnh hưởng lợi nhuận",
                "Nguồn": "Tintuc.vn",
                "Tình Cảm": "Tiêu Cực",
                "Điểm": -0.45
            },
            {
                "Ngày": "2024-10-20",
                "Tiêu Đề": "Công ty được nâng hạng tín dụng bởi Moody's",
                "Nguồn": "Bloomberg",
                "Tình Cảm": "Tích Cực",
                "Điểm": 0.82
            },
            {
                "Ngày": "2024-10-15",
                "Tiêu Đề": "Tuyên bố chia cổ tức bằng tiền mặt 10%",
                "Nguồn": "HOSE",
                "Tình Cảm": "Tích Cực",
                "Điểm": 0.88
            },
            {
                "Ngày": "2024-10-08",
                "Tiêu Đề": "Phát hành cổ phiếu thưởng 1:2",
                "Nguồn": "HNX",
                "Tình Cảm": "Trung Lập",
                "Điểm": 0.15
            },
            {
                "Ngày": "2024-09-30",
                "Tiêu Đề": "Hoàn thành dự án mở rộng nhà máy",
                "Nguồn": "Cafef",
                "Tình Cảm": "Tích Cực",
                "Điểm": 0.75
            },
            {
                "Ngày": "2024-09-20",
                "Tiêu Đề": "Báo cáo bán hàng nửa đầu năm tăng 8.5%",
                "Nguồn": "VNExpress",
                "Tình Cảm": "Tích Cực",
                "Điểm": 0.72
            }
        ]
        
        news_df = pd.DataFrame(news_data)
        
        # Color sentiment
        def color_sentiment(val):
            if val == "Tích Cực":
                return "🟢 Tích Cực"
            elif val == "Tiêu Cực":
                return "🔴 Tiêu Cực"
            else:
                return "🟡 Trung Lập"
        
        news_df["Tình Cảm"] = news_df["Tình Cảm"].apply(color_sentiment)
        
        st.dataframe(news_df, use_container_width=True, hide_index=True)
        
        # News sentiment distribution
        col1, col2 = st.columns(2)
        
        with col1:
            sentiment_counts = {
                "Tích Cực": 5,
                "Tiêu Cực": 1,
                "Trung Lập": 2
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(sentiment_counts.keys()),
                values=list(sentiment_counts.values()),
                marker=dict(colors=["rgba(34, 197, 94, 0.8)", "rgba(239, 68, 68, 0.8)", "rgba(156, 163, 175, 0.8)"])
            )])
            fig.update_layout(
                title="Phân Bố Tình Cảm Tin Tức",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Sentiment trend over time
            dates = pd.to_datetime([d["Ngày"] for d in news_data]).sort_values()
            sentiment_scores = [0.85, 0.78, -0.45, 0.82, 0.88, 0.15, 0.75, 0.72]
            sentiment_scores_sorted = [x for _, x in sorted(zip(dates, sentiment_scores))]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=sorted(dates),
                y=sentiment_scores_sorted,
                mode='lines+markers',
                name='Điểm Tình Cảm',
                line=dict(color='rgba(10, 102, 194, 0.8)', width=2),
                marker=dict(size=6),
                fill='tozeroy'
            ))
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                title="Xu Hướng Tình Cảm Theo Thời Gian",
                xaxis_title="Ngày",
                yaxis_title="Điểm Tình Cảm",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 2: SENTIMENT ANALYSIS ====================
    with tab2:
        st.markdown("### Phân Tích Tình Cảm Chi Tiết (Detailed Sentiment Analysis)")
        st.markdown(f"**Công ty:** {ticker} | **Ngành:** {sector}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Điểm Tình Cảm Trung Bình", "0.58", "+0.12")
        
        with col2:
            st.metric("Tin Tức Tích Cực", "5", "+1")
        
        with col3:
            st.metric("Tin Tức Tiêu Cực", "1", "-1")
        
        st.markdown("---")
        
        # Sentiment by category
        st.markdown("#### Tình Cảm Theo Danh Mục")
        
        sentiment_by_category = {
            "Danh Mục": [
                "Kết Quả Kinh Doanh",
                "Hợp Đồng & Đối Tác",
                "Tài Chính & Nợ",
                "Quản Lý & Nhân Sự",
                "Sản Phẩm & Dịch Vụ",
                "Rủi Ro & Thách Thức"
            ],
            "Điểm Tình Cảm": [0.82, 0.78, 0.65, 0.45, 0.70, -0.35],
            "Số Tin": [3, 2, 2, 1, 2, 1],
            "Đánh Giá": ["Tích Cực", "Tích Cực", "Trung Lập", "Trung Lập", "Tích Cực", "Tiêu Cực"]
        }
        
        category_df = pd.DataFrame(sentiment_by_category)
        st.dataframe(category_df, use_container_width=True, hide_index=True)
        
        # Horizontal bar chart
        fig = go.Figure(data=[
            go.Bar(
                y=sentiment_by_category["Danh Mục"],
                x=sentiment_by_category["Điểm Tình Cảm"],
                orientation='h',
                marker=dict(
                    color=sentiment_by_category["Điểm Tình Cảm"],
                    colorscale='RdYlGn',
                    cmin=-1,
                    cmax=1
                )
            )
        ])
        fig.update_layout(
            title="Tình Cảm Theo Danh Mục",
            xaxis_title="Điểm Tình Cảm",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Sentiment drivers
        st.markdown("#### Những Yếu Tố Chính Ảnh Hưởng Đến Tình Cảm")
        
        drivers = {
            "Yếu Tố": [
                "Tăng Trưởng Doanh Thu",
                "Lợi Nhuận Tăng",
                "Chia Cổ Tức",
                "Nâng Hạng Tín Dụng",
                "Giá Nguyên Liệu Tăng",
                "Cạnh Tranh Tăng"
            ],
            "Tác Động": ["Tích Cực", "Tích Cực", "Tích Cực", "Tích Cực", "Tiêu Cực", "Tiêu Cực"],
            "Mức Độ": ["Cao", "Cao", "Trung Bình", "Trung Bình", "Trung Bình", "Thấp"]
        }
        
        drivers_df = pd.DataFrame(drivers)
        st.dataframe(drivers_df, use_container_width=True, hide_index=True)
    
    # ==================== TAB 3: OVERALL ASSESSMENT ====================
    with tab3:
        st.markdown("### Đánh Giá Chung Tình Hình Cổ Phiếu (Overall Assessment)")
        st.markdown(f"**Công ty:** {ticker} | **Ngành:** {sector} | **Ngày:** {datetime.now().strftime('%d/%m/%Y')}")
        
        # Overall sentiment score
        st.markdown("#### Điểm Đánh Giá Chung")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Tình Cảm Thị Trường", "Tích Cực", "↑")
        
        with col2:
            st.metric("Xu Hướng Tin Tức", "Tích Cực", "↑")
        
        with col3:
            st.metric("Nhận Thức Nhà Đầu Tư", "Tích Cực", "→")
        
        with col4:
            st.metric("Triển Vọng 6 Tháng", "Tích Cực", "↑")
        
        st.markdown("---")
        
        st.markdown("#### Tóm Tắt Đánh Giá")
        
        st.success("""
        **Mẫu Nội Dung - Đánh Giá Chung:**
        
        **Tình Cảm Thị Trường: TÍCH CỰC**
        
        Dựa trên phân tích 8 tin tức gần đây, tình cảm thị trường đối với cổ phiếu {ticker} là **tích cực**.
        
        **Điểm Mạnh:**
        - Kết quả kinh doanh vượt kỳ vọng, doanh thu và lợi nhuận tăng trưởng ổn định
        - Nhận được nâng hạng tín dụng từ các tổ chức quốc tế
        - Tuyên bố chia cổ tức hấp dẫn, thể hiện sự tự tin của quản lý
        - Ký kết các hợp đồng lớn với khách hàng chiến lược
        - Hoàn thành các dự án mở rộng sản xuất
        
        **Điểm Yếu:**
        - Giá nguyên liệu đầu vào có xu hướng tăng, có thể ảnh hưởng đến biên lợi nhuận
        - Cạnh tranh trong ngành tăng lên
        
        **Triển Vọng:**
        Nhà đầu tư có xu hướng tích cực đối với cổ phiếu này. Dự kiến giá cổ phiếu sẽ tiếp tục được hỗ trợ 
        bởi các tin tức tích cực về kinh doanh và các sự kiện công ty trong 6 tháng tới.
        """)
        
        st.markdown("---")
        
        st.markdown("#### Các Rủi Ro Cần Theo Dõi")
        
        st.warning("""
        **Mẫu Nội Dung - Rủi Ro:**
        
        1. **Rủi Ro Kinh Tế Vĩ Mô**
           - Biến động lãi suất có thể ảnh hưởng đến chi phí vay nợ
           - Tình hình kinh tế toàn cầu có thể ảnh hưởng đến nhu cầu sản phẩm
        
        2. **Rủi Ro Ngành**
           - Cạnh tranh tăng từ các đối thủ mới
           - Thay đổi quy định về môi trường và lao động
        
        3. **Rủi Ro Công Ty**
           - Phụ thuộc vào một số khách hàng lớn
           - Rủi Ro tỷ giá từ hoạt động xuất nhập khẩu
        
        4. **Rủi Ro Thị Trường**
           - Biến động giá cổ phiếu có thể tăng nếu có tin tức tiêu cực
        """)
        
        st.markdown("---")
        
        st.markdown("#### Khuyến Nghị Theo Dõi")
        
        st.info("""
        **Mẫu Nội Dung - Khuyến Nghị:**
        
        **Khuyến Nghị:** NẮNG GIỮ / MUA THÊM
        
        **Mục Tiêu Giá:** 85,000 - 95,000 VND (12 tháng)
        
        **Lý Do:**
        - Tăng trưởng kinh doanh ổn định
        - Định giá hợp lý so với đối thủ cạnh tranh
        - Tình cảm thị trường tích cực
        - Cổ tức hấp dẫn
        
        **Điểm Cảnh Báo:**
        - Theo dõi xu hướng giá nguyên liệu
        - Chú ý đến các thay đổi trong danh sách khách hàng lớn
        - Quan sát tình hình cạnh tranh
        """)
