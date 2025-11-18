"""
Tab: Glossary / Help

This tab provides explanations of common financial terms and metrics used
throughout the application.  Having a single place for definitions helps
users unfamiliar with finance understand the charts and tables.  The
definitions are intended to be concise and easy to read.
"""

from __future__ import annotations

import streamlit as st

from utils_new.lang import get_text

def render(feats_df=None, raw_df=None) -> None:
    """
    Render the glossary/help tab.

    Parameters
    ----------
    feats_df: pd.DataFrame, optional
        Features dataframe (unused here).
    raw_df: pd.DataFrame, optional
        Raw financial statement data.  When provided, the glossary will
        display an example interactive chart using aggregate metrics.
    """
    lang = st.session_state.current_lang
    st.header(get_text('glossary_title', lang))
    if lang == 'vi':
        st.markdown("""
**Thuật ngữ & chỉ số**

- **Doanh thu (Revenue):** Tổng doanh thu thuần từ bán hàng và cung cấp dịch vụ của doanh nghiệp trong kỳ.
- **Lợi nhuận ròng (Net Profit):** Lợi nhuận sau thuế thu được sau khi trừ đi tất cả chi phí và thuế.
- **Biên lợi nhuận gộp (Gross Margin):** Tỷ lệ giữa lợi nhuận gộp và doanh thu, phản ánh hiệu quả sản xuất/bán hàng.
- **Biên lợi nhuận hoạt động (Operating Margin):** Tỷ lệ giữa lợi nhuận hoạt động và doanh thu, thể hiện hiệu quả quản lý chi phí.
- **Biên lợi nhuận ròng (Net Margin):** Tỷ lệ giữa lợi nhuận ròng và doanh thu, phản ánh lợi nhuận cuối cùng thu được trên mỗi đồng doanh thu.
- **ROA (Return on Assets):** Lợi nhuận sau thuế trên tổng tài sản trung bình, đo lường hiệu quả sử dụng tài sản.
- **ROE (Return on Equity):** Lợi nhuận sau thuế trên vốn chủ sở hữu trung bình, phản ánh khả năng sinh lời trên vốn.
- **Current Ratio:** Tỷ số tài sản ngắn hạn trên nợ ngắn hạn, đánh giá khả năng thanh toán trong ngắn hạn.
- **Debt/Equity:** Tỷ số nợ phải trả trên vốn chủ sở hữu, cho thấy mức độ đòn bẩy tài chính.
        - **CAGR (Compound Annual Growth Rate):** Tốc độ tăng trưởng kép hàng năm, đo lường mức tăng trưởng trung bình qua nhiều năm.
        - **Phân bố (Distribution):** Mô tả cách các giá trị của một biến được phân tán trong một tập dữ liệu. Ví dụ, phân bố doanh thu cho biết bao nhiêu doanh nghiệp có doanh thu nằm trong các khoảng nhất định.

""")
    else:
        st.markdown("""
**Glossary of terms**

- **Revenue:** Total net sales from goods sold and services rendered during the period.
- **Net Profit:** Profit after tax earned once all expenses and taxes are deducted.
- **Gross Margin:** Ratio of gross profit to revenue, reflecting production/sales efficiency.
- **Operating Margin:** Ratio of operating profit to revenue, reflecting cost management efficiency.
- **Net Margin:** Ratio of net profit to revenue, showing final profit per unit of revenue.
- **ROA (Return on Assets):** Net profit over average total assets, measuring asset utilisation effectiveness.
- **ROE (Return on Equity):** Net profit over average shareholders' equity, indicating return on invested capital.
- **Current Ratio:** Current assets divided by current liabilities, gauging short‑term liquidity.
- **Debt/Equity:** Debt divided by shareholders' equity, indicating the degree of financial leverage.
        - **CAGR (Compound Annual Growth Rate):** Average annual growth rate compounded over multiple years.
        - **Distribution:** Describes how the values of a variable are spread in a dataset. For instance, a revenue distribution shows how many firms fall into different revenue ranges.

    """)

    # If raw data provided, show an example interactive chart for illustration
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    if raw_df is not None and not raw_df.empty:
        try:
            # Compute average ROA across all companies per year if available
            # Attempt to read financial indicators similar to finance tab
            fin_ind_df = None
            # Try reading from session state or fallback paths
            if 'fin_ind_df' in st.session_state:
                fin_ind_df = st.session_state['fin_ind_df']
            if fin_ind_df is None or fin_ind_df.empty:
                import os
                candidate_paths = [
                    'financial_indicators.csv',
                    os.path.join('..', 'financial_indicators.csv'),
                    os.path.join(os.getcwd(), 'financial_indicators.csv'),
                    '/home/oai/share/financial_indicators.csv'
                ]
                for pth in candidate_paths:
                    try:
                        if os.path.exists(pth):
                            fin_ind_df = pd.read_csv(pth)
                            break
                    except Exception:
                        continue
            if fin_ind_df is not None and not fin_ind_df.empty:
                # Group by year and compute mean ROA and ROE
                summary = fin_ind_df.groupby('Year')[['ROA','ROE']].mean().reset_index()
                years = summary['Year'].astype(str).tolist()
                roa = summary['ROA'].tolist()
                roe = summary['ROE'].tolist()
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=years, y=roa, name='ROA', mode='lines+markers'))
                fig.add_trace(go.Scatter(x=years, y=roe, name='ROE', mode='lines+markers'))
                fig.update_layout(title=("Ví dụ xu hướng ROA/ROE" if lang=='vi' else "Example ROA/ROE Trend"), height=350, legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))
                st.plotly_chart(fig, use_container_width=True, key='glossary_example_chart')
        except Exception:
            pass