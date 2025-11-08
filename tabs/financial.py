"""
Financial Analysis Tab
Displays financial statements and indicators
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go


def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, sector: str):
    """
    Render the Financial Analysis tab with multiple financial reports
    """
    
    st.subheader("📊 Phân Tích Tài Chính Chi Tiết")
    
    # Create tabs for different financial reports
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Báo Cáo Thu Nhập",
        "Bảng Cân Đối",
        "Lưu Chuyển Tiền",
        "Chỉ Số Tài Chính",
        "Ghi Chú"
    ])
    
    # Get data for selected ticker and year
    row_raw = raw_df[(raw_df["Ticker"].astype(str)==ticker) & (raw_df["Year"]==year)]
    row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype="object")
    
    # ==================== TAB 1: INCOME STATEMENT ====================
    with tab1:
        st.markdown("### Báo Cáo Thu Nhập (Income Statement)")
        st.markdown(f"**Năm:** {year} | **Công ty:** {ticker} | **Ngành:** {sector}")
        
        # Sample Income Statement data
        income_data = {
            "Chỉ Tiêu": [
                "Doanh Thu Thuần",
                "Giá Vốn Hàng Bán",
                "Lợi Nhuận Gộp",
                "Chi Phí Bán Hàng",
                "Chi Phí Quản Lý",
                "Lợi Nhuận Từ Hoạt Động",
                "Doanh Thu Tài Chính",
                "Chi Phí Tài Chính",
                "Lợi Nhuận Trước Thuế",
                "Chi Phí Thuế",
                "Lợi Nhuận Ròng"
            ],
            "Giá Trị (Tỷ VND)": [
                1000.5,  # Revenue
                600.3,   # COGS
                400.2,   # Gross Profit
                80.1,    # Selling Expenses
                60.2,    # Admin Expenses
                260.0,   # Operating Profit
                25.5,    # Financial Revenue
                35.8,    # Financial Expenses
                249.7,   # Profit Before Tax
                49.9,    # Tax Expense
                199.8    # Net Profit
            ],
            "% Doanh Thu": [
                100.0,
                60.0,
                40.0,
                8.0,
                6.0,
                26.0,
                2.6,
                3.6,
                25.0,
                5.0,
                20.0
            ]
        }
        
        income_df = pd.DataFrame(income_data)
        st.dataframe(income_df, use_container_width=True, hide_index=True)
        
        # Visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue breakdown
            fig = go.Figure(data=[
                go.Bar(
                    x=["Doanh Thu Thuần"],
                    y=[1000.5],
                    name="Doanh Thu",
                    marker_color="rgba(10, 102, 194, 0.8)"
                ),
                go.Bar(
                    x=["Doanh Thu Thuần"],
                    y=[600.3],
                    name="Giá Vốn",
                    marker_color="rgba(229, 231, 235, 0.8)"
                ),
                go.Bar(
                    x=["Doanh Thu Thuần"],
                    y=[400.2],
                    name="Lợi Nhuận Gộp",
                    marker_color="rgba(34, 197, 94, 0.8)"
                )
            ])
            fig.update_layout(
                title="Cấu Trúc Doanh Thu",
                barmode="stack",
                height=350,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Profit margin trend
            years = [year-2, year-1, year]
            margins = [18.5, 19.2, 20.0]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=years,
                y=margins,
                mode='lines+markers',
                name='Biên Lợi Nhuận Ròng',
                line=dict(color='rgba(10, 102, 194, 0.8)', width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title="Xu Hướng Biên Lợi Nhuận",
                xaxis_title="Năm",
                yaxis_title="Biên Lợi Nhuận (%)",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 2: BALANCE SHEET ====================
    with tab2:
        st.markdown("### Bảng Cân Đối Kế Toán (Balance Sheet)")
        st.markdown(f"**Năm:** {year} | **Công ty:** {ticker} | **Ngành:** {sector}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### TÀI SẢN (Assets)")
            assets_data = {
                "Chỉ Tiêu": [
                    "Tiền Mặt & Tương Đương",
                    "Khoản Phải Thu",
                    "Hàng Tồn Kho",
                    "Tài Sản Lưu Động Khác",
                    "**Tổng Tài Sản Lưu Động**",
                    "Bất Động Sản, Máy Móc",
                    "Tài Sản Vô Hình",
                    "Tài Sản Dài Hạn Khác",
                    "**Tổng Tài Sản Cố Định**",
                    "**TỔNG TÀI SẢN**"
                ],
                "Giá Trị (Tỷ VND)": [
                    150.0,
                    250.0,
                    180.0,
                    70.0,
                    650.0,
                    400.0,
                    50.0,
                    100.0,
                    550.0,
                    1200.0
                ]
            }
            assets_df = pd.DataFrame(assets_data)
            st.dataframe(assets_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### NGUỒN VỐN (Liabilities & Equity)")
            liabilities_data = {
                "Chỉ Tiêu": [
                    "Khoản Phải Trả Ngắn Hạn",
                    "Vay Nợ Ngắn Hạn",
                    "Doanh Thu Chưa Thực Hiện",
                    "Nợ Dài Hạn Khác",
                    "**Tổng Nợ Ngắn Hạn**",
                    "Vay Nợ Dài Hạn",
                    "Nợ Dài Hạn Khác",
                    "**Tổng Nợ Dài Hạn**",
                    "**TỔNG NỢ**",
                    "Vốn Chủ Sở Hữu",
                    "Lợi Nhuận Giữ Lại",
                    "**TỔNG VỐN CHỦ**",
                    "**TỔNG NGUỒN VỐN**"
                ],
                "Giá Trị (Tỷ VND)": [
                    180.0,
                    120.0,
                    30.0,
                    20.0,
                    350.0,
                    250.0,
                    50.0,
                    300.0,
                    650.0,
                    400.0,
                    150.0,
                    550.0,
                    1200.0
                ]
            }
            liabilities_df = pd.DataFrame(liabilities_data)
            st.dataframe(liabilities_df, use_container_width=True, hide_index=True)
        
        # Asset composition pie chart
        st.markdown("#### Cấu Trúc Tài Sản")
        fig = go.Figure(data=[go.Pie(
            labels=["Tài Sản Lưu Động", "Tài Sản Cố Định"],
            values=[650, 550],
            hole=0.4
        )])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 3: CASH FLOW STATEMENT ====================
    with tab3:
        st.markdown("### Báo Cáo Lưu Chuyển Tiền Mặt (Cash Flow Statement)")
        st.markdown(f"**Năm:** {year} | **Công ty:** {ticker} | **Ngành:** {sector}")
        
        cashflow_data = {
            "Chỉ Tiêu": [
                "Lợi Nhuận Ròng",
                "Khấu Hao &摊销",
                "Thay Đổi Vốn Lưu Động",
                "**Lưu Chuyển Từ Hoạt Động**",
                "",
                "Mua Sắm Tài Sản Cố Định",
                "Bán Tài Sản Cố Định",
                "Đầu Tư Tài Chính",
                "**Lưu Chuyển Từ Đầu Tư**",
                "",
                "Vay Nợ Mới",
                "Trả Nợ",
                "Cổ Tức Trả",
                "**Lưu Chuyển Từ Tài Chính**",
                "",
                "**Thay Đổi Tiền Mặt Ròng**",
                "Tiền Mặt Đầu Kỳ",
                "**Tiền Mặt Cuối Kỳ**"
            ],
            "Giá Trị (Tỷ VND)": [
                199.8,
                80.0,
                -30.0,
                249.8,
                np.nan,
                -120.0,
                20.0,
                -15.0,
                -115.0,
                np.nan,
                100.0,
                -80.0,
                -30.0,
                -10.0,
                np.nan,
                124.8,
                25.2,
                150.0
            ]
        }
        
        cashflow_df = pd.DataFrame(cashflow_data)
        st.dataframe(cashflow_df, use_container_width=True, hide_index=True)
        
        # Cash flow waterfall
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[go.Waterfall(
                x=["Hoạt Động", "Đầu Tư", "Tài Chính", "Thay Đổi Ròng"],
                y=[249.8, -115.0, -10.0, 124.8],
                connector={"line": {"color": "rgba(0,0,0,0)"}},
                increasing={"marker": {"color": "rgba(34, 197, 94, 0.8)"}},
                decreasing={"marker": {"color": "rgba(239, 68, 68, 0.8)"}},
                totals={"marker": {"color": "rgba(10, 102, 194, 0.8)"}}
            )])
            fig.update_layout(
                title="Lưu Chuyển Tiền Mặt",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Cash position trend
            years = [year-2, year-1, year]
            cash_pos = [80.5, 105.0, 150.0]
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=years,
                y=cash_pos,
                name="Tiền Mặt",
                marker_color="rgba(10, 102, 194, 0.8)"
            ))
            fig.update_layout(
                title="Xu Hướng Tiền Mặt",
                xaxis_title="Năm",
                yaxis_title="Tiền Mặt (Tỷ VND)",
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ==================== TAB 4: FINANCIAL INDICATORS ====================
    with tab4:
        st.markdown("### Chỉ Số Tài Chính Chính (Key Financial Indicators)")
        st.markdown(f"**Năm:** {year} | **Công ty:** {ticker} | **Ngành:** {sector}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Chỉ Số Lợi Suất")
            profitability = {
                "Chỉ Tiêu": [
                    "Lợi Suất Tài Sản (ROA)",
                    "Lợi Suất Vốn Chủ (ROE)",
                    "Biên Lợi Nhuận Gộp",
                    "Biên Lợi Nhuận Hoạt Động",
                    "Biên Lợi Nhuận Ròng"
                ],
                "Giá Trị": [
                    "16.65%",
                    "36.33%",
                    "40.00%",
                    "26.00%",
                    "20.00%"
                ],
                "Đánh Giá": [
                    "Tốt",
                    "Rất Tốt",
                    "Tốt",
                    "Tốt",
                    "Tốt"
                ]
            }
            prof_df = pd.DataFrame(profitability)
            st.dataframe(prof_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Chỉ Số Thanh Khoản")
            liquidity = {
                "Chỉ Tiêu": [
                    "Tỷ Lệ Thanh Khoản Hiện Tại",
                    "Tỷ Lệ Thanh Khoản Nhanh",
                    "Tỷ Lệ Tiền Mặt",
                    "Vòng Quay Tài Sản",
                    "Vòng Quay Khoản Phải Thu"
                ],
                "Giá Trị": [
                    "1.86",
                    "1.14",
                    "0.43",
                    "0.83",
                    "91.5 ngày"
                ],
                "Đánh Giá": [
                    "Tốt",
                    "Tốt",
                    "Bình Thường",
                    "Bình Thường",
                    "Bình Thường"
                ]
            }
            liq_df = pd.DataFrame(liquidity)
            st.dataframe(liq_df, use_container_width=True, hide_index=True)
        
        st.markdown("#### Chỉ Số Đòn Bẩy & Solvency")
        col1, col2 = st.columns(2)
        
        with col1:
            leverage = {
                "Chỉ Tiêu": [
                    "Tỷ Lệ Nợ/Tài Sản",
                    "Tỷ Lệ Nợ/Vốn Chủ",
                    "Tỷ Lệ Nợ Ròng/Vốn Chủ",
                    "Lần Bao Phủ Lãi Vay"
                ],
                "Giá Trị": [
                    "54.17%",
                    "1.18",
                    "0.95",
                    "7.25x"
                ],
                "Đánh Giá": [
                    "Bình Thường",
                    "Bình Thường",
                    "Tốt",
                    "Tốt"
                ]
            }
            lev_df = pd.DataFrame(leverage)
            st.dataframe(lev_df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("#### Chỉ Số Tăng Trưởng")
            growth = {
                "Chỉ Tiêu": [
                    "Tăng Trưởng Doanh Thu (YoY)",
                    "Tăng Trưởng Lợi Nhuận (YoY)",
                    "CAGR Doanh Thu (3 năm)",
                    "CAGR Lợi Nhuận (3 năm)"
                ],
                "Giá Trị": [
                    "8.50%",
                    "12.30%",
                    "7.80%",
                    "10.50%"
                ],
                "Đánh Giá": [
                    "Tốt",
                    "Tốt",
                    "Tốt",
                    "Tốt"
                ]
            }
            growth_df = pd.DataFrame(growth)
            st.dataframe(growth_df, use_container_width=True, hide_index=True)
    
    # ==================== TAB 5: NOTES ====================
    with tab5:
        st.markdown("### Ghi Chú & Phân Tích (Notes & Analysis)")
        st.markdown(f"**Năm:** {year} | **Công ty:** {ticker} | **Ngành:** {sector}")
        
        st.markdown("#### 1. Tóm Tắt Hoạt Động Kinh Doanh")
        st.info("""
        **Mẫu Nội Dung:**
        
        Công ty hoạt động trong lĩnh vực [ngành], cung cấp các sản phẩm/dịch vụ chính bao gồm:
        - Sản phẩm A: chiếm 45% doanh thu
        - Sản phẩm B: chiếm 35% doanh thu
        - Dịch vụ C: chiếm 20% doanh thu
        
        Năm {year}, công ty đạt doanh thu 1,000.5 tỷ VND, tăng 8.5% so với năm trước.
        """)
        
        st.markdown("#### 2. Phân Tích Kết Quả Kinh Doanh")
        st.info("""
        **Mẫu Nội Dung:**
        
        **Điểm Mạnh:**
        - Lợi nhuận ròng tăng 12.3% YoY, đạt 199.8 tỷ VND
        - Biên lợi nhuận ròng ở mức 20%, cao hơn trung bình ngành
        - Lưu chuyển tiền từ hoạt động mạnh, đạt 249.8 tỷ VND
        
        **Điểm Yếu:**
        - Tỷ lệ nợ/tài sản ở mức 54.17%, cần theo dõi
        - Vòng quay tài sản còn thấp, cần cải thiện hiệu quả sử dụng tài sản
        """)
        
        st.markdown("#### 3. Các Sự Kiện Quan Trọng")
        st.info("""
        **Mẫu Nội Dung:**
        
        - **Quý 1:** Phát hành cổ phiếu thưởng, tăng vốn điều lệ
        - **Quý 2:** Ký kết hợp đồng lớn với khách hàng chiến l略
        - **Quý 3:** Hoàn thành dự án mở rộng sản xuất
        - **Quý 4:** Tuyên bố chia cổ tức bằng tiền mặt 10%
        """)
        
        st.markdown("#### 4. Rủi Ro & Cảnh Báo")
        st.warning("""
        **Mẫu Nội Dung:**
        
        - **Rủi Ro Thị Trường:** Biến động giá nguyên liệu đầu vào
        - **Rủi Ro Tín Dụng:** Nợ phải thu từ khách hàng lớn
        - **Rủi Ro Tỷ Giá:** Có hoạt động xuất nhập khẩu
        - **Rủi Ro Pháp Lý:** Cần tuân thủ quy định môi trường mới
        """)
        
        st.markdown("#### 5. Dự Báo & Triển Vọng")
        st.success("""
        **Mẫu Nội Dung:**
        
        Năm {year+1} dự kiến:
        - Doanh thu: 1,085 - 1,120 tỷ VND (tăng 8-12%)
        - Lợi nhuận ròng: 225 - 240 tỷ VND (tăng 12-20%)
        - Đầu tư vào R&D: 50 tỷ VND
        - Mục tiêu ROE: 38-40%
        """)
