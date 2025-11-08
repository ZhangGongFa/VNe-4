"""
Finance Tab - Extended with multilingual support
Displays detailed financial statements and indicators
"""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from utils_new.lang import get_text

def render(feats_df: pd.DataFrame, raw_df: pd.DataFrame, ticker: str, year: int, 
           model, thresholds, sector: str, final_features: list):
    """
    Render the Finance tab with extended content
    """
    lang = st.session_state.get('current_lang', 'vi')
    
    st.subheader(get_text("finance_header", lang))
    
    # Get selected data
    row_model = feats_df[(feats_df["Ticker"].astype(str)==ticker) & (feats_df["Year"]==year)]
    if row_model.empty:
        st.warning(get_text("warning_no_data", lang))
        return
    row_model = row_model.iloc[0]
    
    row_raw = raw_df[(raw_df["Ticker"].astype(str)==ticker) & (raw_df["Year"]==year)]
    row_raw = row_raw.iloc[0] if not row_raw.empty else pd.Series(dtype="object")
    
    # Create tabs for different financial statements
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text("finance_tab_income", lang),
        get_text("finance_tab_balance", lang),
        get_text("finance_tab_cashflow", lang),
        get_text("finance_tab_indicators", lang),
        get_text("finance_tab_notes", lang)
    ])
    
    # ==================== TAB 1: INCOME STATEMENT ====================
    with tab1:
        st.markdown(f"### {get_text('income_statement_title', lang)}")
        st.markdown(f"**{get_text('income_year', lang)}:** {year} | **{get_text('income_company', lang)}:** {ticker} | **{get_text('income_sector', lang)}:** {sector}")
        
        # Sample income statement data
        income_data = {
            get_text("stress_table_scenario", lang) if lang == "en" else "Chỉ Tiêu": [
                "Doanh Thu Thuần" if lang == "vi" else "Net Revenue",
                "Chi Phí Hàng Bán" if lang == "vi" else "Cost of Goods Sold",
                "Lợi Nhuận Gộp" if lang == "vi" else "Gross Profit",
                "Chi Phí Bán Hàng" if lang == "vi" else "Selling Expenses",
                "Chi Phí Quản Lý" if lang == "vi" else "Administrative Expenses",
                "Lợi Nhuận Hoạt Động" if lang == "vi" else "Operating Profit",
                "Chi Phí Lãi Vay" if lang == "vi" else "Interest Expenses",
                "Lợi Nhuận Trước Thuế" if lang == "vi" else "Profit Before Tax",
                "Chi Phí Thuế" if lang == "vi" else "Tax Expense",
                "Lợi Nhuận Ròng" if lang == "vi" else "Net Profit"
            ],
            "Giá Trị (Tỷ VND)" if lang == "vi" else "Value (Billion VND)": [
                1050, 630, 420, 105, 84, 231, 21, 210, 42, 168
            ],
            "% Doanh Thu" if lang == "vi" else "% of Revenue": [
                "100.0%", "60.0%", "40.0%", "10.0%", "8.0%", "22.0%", "2.0%", "20.0%", "4.0%", "16.0%"
            ]
        }
        
        income_df = pd.DataFrame(income_data)
        st.dataframe(income_df, use_container_width=True, hide_index=True, key="finance_income_table")
        
        # Income statement chart
        fig = go.Figure(data=[
            go.Bar(name="Doanh Thu" if lang == "vi" else "Revenue", x=["2020", "2021", "2022", "2023", "2024"], y=[850, 920, 950, 1000, 1050]),
            go.Bar(name="Lợi Nhuận Ròng" if lang == "vi" else "Net Profit", x=["2020", "2021", "2022", "2023", "2024"], y=[120, 135, 150, 160, 168])
        ])
        fig.update_layout(
            title="Xu Hướng Doanh Thu & Lợi Nhuận" if lang == "vi" else "Revenue & Net Profit Trend",
            barmode='group',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True, key="finance_income_chart")
    
    # ==================== TAB 2: BALANCE SHEET ====================
    with tab2:
        st.markdown(f"### {get_text('balance_sheet_title', lang)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**" + ("Tài Sản" if lang == "vi" else "Assets") + "**")
            assets_data = {
                "Chỉ Tiêu" if lang == "vi" else "Item": [
                    "Tiền Mặt" if lang == "vi" else "Cash",
                    "Phải Thu Ngắn Hạn" if lang == "vi" else "Short-term Receivables",
                    "Hàng Tồn Kho" if lang == "vi" else "Inventory",
                    "Tài Sản Lưu Động" if lang == "vi" else "Current Assets",
                    "Tài Sản Cố Định" if lang == "vi" else "Fixed Assets",
                    "Tài Sản Vô Hình" if lang == "vi" else "Intangible Assets",
                    "Tổng Tài Sản" if lang == "vi" else "Total Assets"
                ],
                "Giá Trị (Tỷ VND)" if lang == "vi" else "Value (Bn VND)": [
                    210, 315, 210, 840, 840, 105, 1785
                ]
            }
            assets_df = pd.DataFrame(assets_data)
            st.dataframe(assets_df, use_container_width=True, hide_index=True, key="finance_assets_table")
        
        with col2:
            st.markdown("**" + ("Nợ & Vốn Chủ" if lang == "vi" else "Liabilities & Equity") + "**")
            liab_data = {
                "Chỉ Tiêu" if lang == "vi" else "Item": [
                    "Phải Trả Ngắn Hạn" if lang == "vi" else "Short-term Payables",
                    "Vay Ngắn Hạn" if lang == "vi" else "Short-term Borrowings",
                    "Nợ Lưu Động" if lang == "vi" else "Current Liabilities",
                    "Vay Dài Hạn" if lang == "vi" else "Long-term Borrowings",
                    "Tổng Nợ" if lang == "vi" else "Total Liabilities",
                    "Vốn Chủ Sở Hữu" if lang == "vi" else "Equity",
                    "Tổng Nợ & Vốn" if lang == "vi" else "Total Liab. & Equity"
                ],
                "Giá Trị (Tỷ VND)" if lang == "vi" else "Value (Bn VND)": [
                    210, 105, 420, 315, 735, 1050, 1785
                ]
            }
            liab_df = pd.DataFrame(liab_data)
            st.dataframe(liab_df, use_container_width=True, hide_index=True, key="finance_liab_table")
    
    # ==================== TAB 3: CASH FLOW ====================
    with tab3:
        st.markdown(f"### {get_text('cashflow_statement_title', lang)}")
        
        cashflow_data = {
            "Chỉ Tiêu" if lang == "vi" else "Item": [
                "Lợi Nhuận Ròng" if lang == "vi" else "Net Profit",
                "Khấu Hao &摊销" if lang == "vi" else "Depreciation & Amortization",
                "Thay Đổi Vốn Lưu Động" if lang == "vi" else "Change in Working Capital",
                "Lưu Chuyển từ Hoạt Động" if lang == "vi" else "Operating Cash Flow",
                "Chi Đầu Tư Cố Định" if lang == "vi" else "Capital Expenditures",
                "Lưu Chuyển từ Đầu Tư" if lang == "vi" else "Investing Cash Flow",
                "Phát Hành Cổ Phiếu" if lang == "vi" else "Equity Issuance",
                "Trả Nợ Vay" if lang == "vi" else "Debt Repayment",
                "Lưu Chuyển từ Tài Chính" if lang == "vi" else "Financing Cash Flow",
                "Thay Đổi Tiền Mặt" if lang == "vi" else "Net Change in Cash"
            ],
            "Giá Trị (Tỷ VND)" if lang == "vi" else "Value (Bn VND)": [
                168, 42, -21, 189, -84, -84, 0, -63, -63, 42
            ]
        }
        
        cashflow_df = pd.DataFrame(cashflow_data)
        st.dataframe(cashflow_df, use_container_width=True, hide_index=True, key="finance_cashflow_table")
        
        # Waterfall chart for cash flow
        fig = go.Figure(go.Waterfall(
            x=["Operating", "Investing", "Financing", "Net Change"],
            y=[189, -84, -63, 42],
            connector={"line": {"color": "rgba(63, 63, 63, 0.5)"}},
            decreasing={"marker": {"color": "#E24A33"}},
            increasing={"marker": {"color": "#1F77B4"}},
            totals={"marker": {"color": "#22C55E"}}
        ))
        fig.update_layout(
            title="Lưu Chuyển Tiền Tệ" if lang == "vi" else "Cash Flow Waterfall",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True, key="finance_cashflow_chart")
    
    # ==================== TAB 4: FINANCIAL INDICATORS ====================
    with tab4:
        st.markdown(f"### {get_text('financial_indicators_title', lang)}")
        
        indicators_data = {
            "Chỉ Số" if lang == "vi" else "Indicator": [
                "ROA (Return on Assets)",
                "ROE (Return on Equity)",
                "Tỷ Lệ Nợ/Tài Sản",
                "Tỷ Lệ Nợ/Vốn Chủ",
                "Tỷ Lệ Thanh Khoản Hiện Tại",
                "Tỷ Lệ Thanh Khoản Nhanh",
                "Vòng Quay Tài Sản",
                "Biên Lợi Nhuận Ròng",
                "Chu Kỳ Chuyển Đổi Tiền Mặt",
                "Tỷ Lệ Phủ Lãi Vay"
            ],
            "Giá Trị": [
                "16.65%", "36.33%", "54.17%", "1.86", "1.86", "1.43", "0.83", "20.0%", "45 ngày", "11.0x"
            ],
            "Đánh Giá": [
                "Tốt ↑" if lang == "vi" else "Good ↑",
                "Tốt ↑" if lang == "vi" else "Good ↑",
                "Bình Thường →" if lang == "vi" else "Fair →",
                "Bình Thường →" if lang == "vi" else "Fair →",
                "Tốt ↑" if lang == "vi" else "Good ↑",
                "Tốt ↑" if lang == "vi" else "Good ↑",
                "Bình Thường →" if lang == "vi" else "Fair →",
                "Tốt ↑" if lang == "vi" else "Good ↑",
                "Bình Thường →" if lang == "vi" else "Fair →",
                "Tốt ↑" if lang == "vi" else "Good ↑"
            ]
        }
        
        indicators_df = pd.DataFrame(indicators_data)
        st.dataframe(indicators_df, use_container_width=True, hide_index=True, key="finance_indicators_table")
    
    # ==================== TAB 5: NOTES & ASSESSMENT ====================
    with tab5:
        st.markdown(f"### {get_text('notes_assessment_title', lang)}")
        
        if lang == "vi":
            st.markdown("""
            **Tóm Tắt Hoạt Động:**
            - Doanh thu tăng 5% so với năm trước, đạt 1,050 tỷ VND
            - Lợi nhuận ròng tăng 5% lên 168 tỷ VND
            - Lưu chuyển tiền từ hoạt động ổn định ở mức 189 tỷ VND
            
            **Phân Tích Kết Quả:**
            - Biên lợi nhuận ròng 20% cho thấy hiệu quả kinh doanh tốt
            - Tỷ lệ nợ/tài sản 54% ở mức chấp nhận được
            - Tỷ lệ thanh khoản 1.86 đảm bảo khả năng thanh toán ngắn hạn
            
            **Rủi Ro Chính:**
            - Phụ thuộc vào một số khách hàng lớn (chiếm 35% doanh thu)
            - Biến động giá nguyên liệu đầu vào
            - Cạnh tranh tăng từ các đối thủ mới
            
            **Dự Báo:**
            - Doanh thu dự kiến tăng 8-10% trong năm tới
            - Lợi nhuận ròng dự kiến tăng 10-12%
            - Nhu cầu vốn lưu động dự kiến tăng do mở rộng sản xuất
            """)
        else:
            st.markdown("""
            **Business Summary:**
            - Revenue increased 5% YoY to 1,050 billion VND
            - Net profit increased 5% to 168 billion VND
            - Operating cash flow stable at 189 billion VND
            
            **Results Analysis:**
            - Net profit margin of 20% indicates good operational efficiency
            - Debt-to-assets ratio of 54% is at acceptable level
            - Current ratio of 1.86 ensures short-term liquidity
            
            **Key Risks:**
            - Dependency on few major customers (35% of revenue)
            - Volatility in raw material prices
            - Increasing competition from new competitors
            
            **Outlook:**
            - Revenue expected to grow 8-10% next year
            - Net profit expected to grow 10-12%
            - Working capital needs expected to increase due to production expansion
            """)
