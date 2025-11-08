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
    Render the Finance tab with actual data from bctc_final.csv.

    This implementation replaces sample/static numbers with real financial data for
    the selected ticker and year. It also computes and displays 19 key financial
    ratios and includes multi‑year trend tables/charts to let users see how
    metrics evolve over time.
    """
    lang = st.session_state.get('current_lang', 'vi')

    st.subheader(get_text("finance_header", lang))

    # Retrieve the row for the selected ticker/year from features and raw data
    row_feat = feats_df[(feats_df["Ticker"].astype(str) == str(ticker)) & (feats_df["Year"] == year)]
    row_raw = raw_df[(raw_df["Ticker"].astype(str) == str(ticker)) & (raw_df["Year"] == year)]

    if row_feat.empty or row_raw.empty:
        st.warning(get_text("warning_no_data", lang))
        return

    row_feat = row_feat.iloc[0]
    row_raw = row_raw.iloc[0]

    # Helper to safely convert values to floats
    def to_num(x):
        try:
            if pd.isna(x):
                return 0.0
            if isinstance(x, str):
                return float(str(x).replace(",", ""))
            return float(x)
        except Exception:
            return 0.0

    # Helper to format values nicely
    def fmt_val(x):
        return "-" if (x is None or not np.isfinite(x)) else f"{x:,.2f}"

    # Helper to compute ratio evaluation
    def evaluate_ratio(name: str, value: float):
        if value is None or not np.isfinite(value):
            return "-"
        # Define basic thresholds for good/fair/poor
        thresholds = {
            'Current_Ratio': (1.5, 1.0),
            'Quick_Ratio': (1.0, 0.5),
            'Working_Capital_to_Total_Assets': (0.2, 0.1),
            'Debt_to_Assets': (0.5, 0.7),
            'Debt_to_Equity': (1.0, 2.0),
            'Equity_to_Liabilities': (1.0, 0.5),
            'Long_Term_Debt_to_Assets': (0.3, 0.6),
            'Receivables_Turnover': (5.0, 2.0),
            'Inventory_Turnover': (5.0, 2.0),
            'Asset_Turnover': (1.0, 0.5),
            'ROA': (0.10, 0.0),
            'ROE': (0.15, 0.0),
            'EBIT_to_Assets': (0.10, 0.0),
            'Operating_Income_to_Debt': (0.30, 0.10),
            'Net_Profit_Margin': (0.10, 0.0),
            'Gross_Margin': (0.20, 0.10),
            'Interest_Coverage': (3.0, 1.0),
            'EBITDA_to_Interest': (3.0, 1.0),
            'Total_Debt_to_EBITDA': (3.0, 5.0)
        }
        good, fair = thresholds.get(name, (None, None))
        # For ratios where lower is better (like Total_Debt_to_EBITDA) invert logic
        if name == 'Total_Debt_to_EBITDA':
            if value < good:
                return "Tốt ↑" if lang == 'vi' else "Good ↑"
            elif value < fair:
                return "Bình Thường →" if lang == 'vi' else "Fair →"
            else:
                return "Kém ↓" if lang == 'vi' else "Poor ↓"
        else:
            if value > good:
                return "Tốt ↑" if lang == 'vi' else "Good ↑"
            elif value > fair:
                return "Bình Thường →" if lang == 'vi' else "Fair →"
            else:
                return "Kém ↓" if lang == 'vi' else "Poor ↓"

    # Construct multi‑year slices for trends
    ticker_raw = raw_df[raw_df["Ticker"].astype(str) == str(ticker)].copy()
    ticker_raw = ticker_raw.sort_values("Year")
    ticker_feat = feats_df[feats_df["Ticker"].astype(str) == str(ticker)].copy().sort_values("Year")

    # ================ TAB 1: INCOME STATEMENT ===================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text("finance_tab_income", lang),
        get_text("finance_tab_balance", lang),
        get_text("finance_tab_cashflow", lang),
        get_text("finance_tab_indicators", lang),
        get_text("finance_tab_notes", lang)
    ])

    with tab1:
        st.markdown(f"### {get_text('income_statement_title', lang)}")
        st.markdown(f"**{get_text('income_year', lang)}:** {year} | **{get_text('income_company', lang)}:** {ticker} | **{get_text('income_sector', lang)}:** {sector}")

        # Extract income statement values
        # Determine revenue using available columns (Net Sales preferred, fallback to Revenue (Bn. VND))
        revenue = to_num(row_raw.get('Net Sales', row_raw.get('Revenue', row_raw.get('Revenue (Bn. VND)', np.nan))))
        cogs = to_num(row_raw.get('Cost of Sales'))
        gross_profit = to_num(row_raw.get('Gross Profit'))
        selling_exp = to_num(row_raw.get('Selling Expenses'))
        admin_exp = to_num(row_raw.get('General & Admin Expenses'))
        operating_profit = to_num(row_raw.get('Operating Profit/Loss'))
        interest_exp = to_num(row_raw.get('Interest Expenses', row_raw.get('Interest Expense')))
        profit_before_tax = to_num(row_raw.get('Profit before tax', row_raw.get('Net Profit/Loss before tax')))
        tax_expense = to_num(row_raw.get('Business income tax - current')) + to_num(row_raw.get('Business income tax - deferred'))
        net_profit = to_num(row_raw.get('Net Profit For the Year'))

        income_items_vi = [
            'Doanh Thu Thuần', 'Giá Vốn Hàng Bán', 'Lợi Nhuận Gộp',
            'Chi Phí Bán Hàng', 'Chi Phí Quản Lý', 'Lợi Nhuận Hoạt Động',
            'Chi Phí Lãi Vay', 'Lợi Nhuận Trước Thuế', 'Chi Phí Thuế', 'Lợi Nhuận Ròng'
        ]
        income_items_en = [
            'Net Revenue', 'Cost of Goods Sold', 'Gross Profit',
            'Selling Expenses', 'Administrative Expenses', 'Operating Profit',
            'Interest Expenses', 'Profit Before Tax', 'Tax Expense', 'Net Profit'
        ]
        values = [revenue, cogs, gross_profit, selling_exp, admin_exp,
                  operating_profit, interest_exp, profit_before_tax, tax_expense, net_profit]
        percentages = []
        for v in values:
            if revenue != 0:
                pct = v / revenue
            else:
                pct = 0.0
            percentages.append(f"{pct*100:.1f}%")
        header_key = get_text("stress_table_scenario", lang) if lang == 'en' else "Chỉ Tiêu"
        income_df = pd.DataFrame({
            header_key: income_items_en if lang == 'en' else income_items_vi,
            ("Value (Bn VND)" if lang == 'en' else "Giá Trị (Tỷ VND)"): [fmt_val(v) for v in values],
            ("% of Revenue" if lang == 'en' else "% Doanh Thu"): percentages
        })
        st.dataframe(income_df, use_container_width=True, hide_index=True, key="finance_income_table")

        # Show trend of revenue and net profit across years
        trend_years = ticker_raw['Year'].astype(str).tolist()
        trend_rev = [to_num(v) for v in ticker_raw.get('Net Sales', ticker_raw.get('Revenue', ticker_raw.get('Revenue (Bn. VND)', np.nan)))]
        trend_np = [to_num(v) for v in ticker_raw.get('Net Profit For the Year', ticker_raw.get('Net Profit', np.nan))]
        fig = go.Figure(data=[
            go.Bar(name=get_text('metric_revenue', lang), x=trend_years, y=trend_rev),
            go.Bar(name=get_text('metric_net_profit', lang), x=trend_years, y=trend_np)
        ])
        fig.update_layout(
            title=("Xu Hướng Doanh Thu & Lợi Nhuận" if lang == 'vi' else "Revenue & Net Profit Trend"),
            barmode='group',
            height=350
        )
        st.plotly_chart(fig, use_container_width=True, key="finance_income_chart")

        # Display multi‑year income summary table
        multi_income = pd.DataFrame({
            'Year': ticker_raw['Year'],
            ("Net Revenue" if lang == 'en' else "Doanh Thu"): trend_rev,
            ("Net Profit" if lang == 'en' else "Lợi Nhuận Ròng"): trend_np
        })
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi‑year Data") + "**")
        st.dataframe(multi_income, use_container_width=True, hide_index=True, key="income_multiyear_table")

    # ================ TAB 2: BALANCE SHEET ===================
    with tab2:
        st.markdown(f"### {get_text('balance_sheet_title', lang)}")
        # Assets
        assets_items_vi = ['Tiền Mặt', 'Phải Thu', 'Hàng Tồn Kho', 'Tài Sản Lưu Động', 'Tài Sản Cố Định', 'Đầu Tư Dài Hạn', 'Tổng Tài Sản']
        assets_items_en = ['Cash', 'Accounts Receivable', 'Inventory', 'Current Assets', 'Fixed Assets', 'Long-term Investments', 'Total Assets']
        cash = to_num(row_raw.get('Cash and cash equivalents (Bn. VND)'))
        receivables = to_num(row_raw.get('Accounts receivable (Bn. VND)'))
        inventory = to_num(row_raw.get('Net Inventories', row_raw.get('Inventories, Net (Bn. VND)')))
        current_assets = to_num(row_raw.get('CURRENT ASSETS (Bn. VND)'))
        fixed_assets = to_num(row_raw.get('Fixed assets (Bn. VND)'))
        long_inv = to_num(row_raw.get('Long-term investments (Bn. VND)'))
        total_assets = to_num(row_raw.get('TOTAL ASSETS (Bn. VND)'))
        assets_values = [cash, receivables, inventory, current_assets, fixed_assets, long_inv, total_assets]
        assets_df = pd.DataFrame({
            ('Item' if lang == 'en' else 'Chỉ Tiêu'): assets_items_en if lang == 'en' else assets_items_vi,
            ('Value (Bn VND)' if lang == 'en' else 'Giá Trị (Tỷ VND)'): [fmt_val(v) for v in assets_values]
        })
        # Liabilities and Equity
        liab_items_vi = ['Vay Ngắn Hạn', 'Vay Dài Hạn', 'Nợ Ngắn Hạn', 'Nợ Dài Hạn', 'Tổng Nợ', 'Vốn Chủ Sở Hữu', 'Tổng Nợ & Vốn']
        liab_items_en = ['Short-term Borrowings', 'Long-term Borrowings', 'Current Liabilities', 'Long-term Liabilities', 'Total Liabilities', 'Equity', 'Total Liab. & Equity']
        short_borrow = to_num(row_raw.get('Short-term borrowings (Bn. VND)'))
        long_borrow = to_num(row_raw.get('Long-term borrowings (Bn. VND)'))
        current_liab = to_num(row_raw.get('Current liabilities (Bn. VND)'))
        long_liab = to_num(row_raw.get('Long-term liabilities (Bn. VND)'))
        total_liab = to_num(row_raw.get('LIABILITIES (Bn. VND)'))
        equity = to_num(row_raw.get("OWNER'S EQUITY(Bn.VND)"))
        total_resources = to_num(row_raw.get('TOTAL RESOURCES (Bn. VND)', total_assets))
        liab_values = [short_borrow, long_borrow, current_liab, long_liab, total_liab, equity, total_resources]
        liab_df = pd.DataFrame({
            ('Item' if lang == 'en' else 'Chỉ Tiêu'): liab_items_en if lang == 'en' else liab_items_vi,
            ('Value (Bn VND)' if lang == 'en' else 'Giá Trị (Tỷ VND)'): [fmt_val(v) for v in liab_values]
        })
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**" + ("Assets" if lang == 'en' else "Tài Sản") + "**")
            st.dataframe(assets_df, use_container_width=True, hide_index=True, key="finance_assets_table")
        with col2:
            st.markdown("**" + ("Liabilities & Equity" if lang == 'en' else "Nợ & Vốn Chủ") + "**")
            st.dataframe(liab_df, use_container_width=True, hide_index=True, key="finance_liab_table")
        # Multi‑year summary for balance sheet
        multi_balance = pd.DataFrame({
            'Year': ticker_raw['Year'],
            ('Total Assets' if lang == 'en' else 'Tổng Tài Sản'): [to_num(v) for v in ticker_raw.get('TOTAL ASSETS (Bn. VND)', np.nan)],
            ('Total Liabilities' if lang == 'en' else 'Tổng Nợ'): [to_num(v) for v in ticker_raw.get('LIABILITIES (Bn. VND)', np.nan)],
            ('Equity' if lang == 'en' else 'Vốn Chủ'): [to_num(v) for v in ticker_raw.get("OWNER'S EQUITY(Bn.VND)", np.nan)]
        })
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi‑year Data") + "**")
        st.dataframe(multi_balance, use_container_width=True, hide_index=True, key="balance_multiyear_table")

    # ================ TAB 3: CASH FLOW ===================
    with tab3:
        st.markdown(f"### {get_text('cashflow_statement_title', lang)}")
        # Compute cash flow items
        cf_items_vi = ['Lợi Nhuận Ròng', 'Khấu Hao & Khấu Hao', 'Thay Đổi Vốn Lưu Động', 'Lưu Chuyển từ Hoạt Động', 'Chi Đầu Tư Cố Định', 'Lưu Chuyển từ Đầu Tư', 'Phát Hành Cổ Phiếu', 'Trả Nợ Vay', 'Lưu Chuyển từ Tài Chính', 'Thay Đổi Tiền Mặt']
        cf_items_en = ['Net Profit', 'Depreciation & Amortization', 'Change in Working Capital', 'Operating Cash Flow', 'Capital Expenditures', 'Investing Cash Flow', 'Equity Issuance', 'Debt Repayment', 'Financing Cash Flow', 'Net Change in Cash']
        net_profit_cf = net_profit  # reuse from income statement
        depreciation = to_num(row_raw.get('Depreciation and Amortisation'))
        # Change in working capital: sum of receivables/inventories/payables/prepaid changes if available
        wc_change = (to_num(row_raw.get('Increase/Decrease in receivables')) +
                     to_num(row_raw.get('Increase/Decrease in inventories')) +
                     to_num(row_raw.get('Increase/Decrease in payables')) +
                     to_num(row_raw.get('Increase/Decrease in prepaid expenses')))
        ocf = to_num(row_raw.get('Net cash inflows/outflows from operating activities'))
        capex = to_num(row_raw.get('Purchase of fixed assets'))
        investing_cf = to_num(row_raw.get('Net Cash Flows from Investing Activities'))
        equity_issue = to_num(row_raw.get('Increase in charter captial'))
        debt_repay = to_num(row_raw.get('Repayment of borrowings'))
        financing_cf = to_num(row_raw.get('Cash flows from financial activities'))
        net_change_cash = to_num(row_raw.get('Net increase/decrease in cash and cash equivalents'))
        cf_values = [net_profit_cf, depreciation, wc_change, ocf, capex, investing_cf, equity_issue, debt_repay, financing_cf, net_change_cash]
        cf_df = pd.DataFrame({
            ('Item' if lang == 'en' else 'Chỉ Tiêu'): cf_items_en if lang == 'en' else cf_items_vi,
            ('Value (Bn VND)' if lang == 'en' else 'Giá Trị (Tỷ VND)'): [fmt_val(v) for v in cf_values]
        })
        st.dataframe(cf_df, use_container_width=True, hide_index=True, key="finance_cashflow_table")
        # Waterfall chart
        figcf = go.Figure(go.Waterfall(
            x=["Operating", "Investing", "Financing", "Net Change"],
            y=[ocf, investing_cf, financing_cf, net_change_cash],
            connector={"line": {"color": "rgba(63, 63, 63, 0.5)"}},
            decreasing={"marker": {"color": "#E24A33"}},
            increasing={"marker": {"color": "#1F77B4"}},
            totals={"marker": {"color": "#22C55E"}}
        ))
        figcf.update_layout(
            title=("Lưu Chuyển Tiền Tệ" if lang == 'vi' else 'Cash Flow Waterfall'),
            height=350
        )
        st.plotly_chart(figcf, use_container_width=True, key="finance_cashflow_chart")
        # Multi‑year cash flow summary
        multi_cf = pd.DataFrame({
            'Year': ticker_raw['Year'],
            ('Operating CF' if lang == 'en' else 'Lưu Chuyển Hoạt Động'): [to_num(v) for v in ticker_raw.get('Net cash inflows/outflows from operating activities', np.nan)],
            ('Investing CF' if lang == 'en' else 'Lưu Chuyển Đầu Tư'): [to_num(v) for v in ticker_raw.get('Net Cash Flows from Investing Activities', np.nan)],
            ('Financing CF' if lang == 'en' else 'Lưu Chuyển Tài Chính'): [to_num(v) for v in ticker_raw.get('Cash flows from financial activities', np.nan)],
            ('Net Change Cash' if lang == 'en' else 'Thay Đổi Tiền Mặt'): [to_num(v) for v in ticker_raw.get('Net increase/decrease in cash and cash equivalents', np.nan)]
        })
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi‑year Data") + "**")
        st.dataframe(multi_cf, use_container_width=True, hide_index=True, key="cashflow_multiyear_table")

    # ================ TAB 4: FINANCIAL INDICATORS ===================
    with tab4:
        st.markdown(f"### {get_text('financial_indicators_title', lang)}")
        # List of 19 indicators to display
        ind_list = [
            'Current_Ratio','Quick_Ratio','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity',
            'Equity_to_Liabilities','Long_Term_Debt_to_Assets','Receivables_Turnover','Inventory_Turnover','Asset_Turnover',
            'ROA','ROE','EBIT_to_Assets','Operating_Income_to_Debt','Net_Profit_Margin','Gross_Margin','Interest_Coverage','EBITDA_to_Interest','Total_Debt_to_EBITDA'
        ]
        ind_names_vi = [
            'Tỷ Lệ Thanh Khoản Hiện Tại', 'Tỷ Lệ Thanh Khoản Nhanh', 'Vốn Lưu Động/Tổng Tài Sản', 'Tỷ Lệ Nợ/Tài Sản', 'Tỷ Lệ Nợ/Vốn Chủ',
            'Vốn Chủ/Nợ', 'Nợ Dài Hạn/Tài Sản', 'Vòng Quay Phải Thu', 'Vòng Quay Tồn Kho', 'Vòng Quay Tài Sản',
            'ROA', 'ROE', 'EBIT/Tài Sản', 'Thu Nhập Hoạt Động/Nợ', 'Biên Lợi Nhuận Ròng', 'Biên Lợi Nhuận Gộp', 'Khả Năng Chi Trả Lãi', 'EBITDA/Lãi Vay', 'Tổng Nợ/EBITDA'
        ]
        ind_names_en = [
            'Current Ratio', 'Quick Ratio', 'Working Capital/Total Assets', 'Debt/Assets', 'Debt/Equity',
            'Equity/Liabilities', 'Long-term Debt/Assets', 'Receivables Turnover', 'Inventory Turnover', 'Asset Turnover',
            'ROA', 'ROE', 'EBIT/Assets', 'Operating Income/Debt', 'Net Profit Margin', 'Gross Margin', 'Interest Coverage', 'EBITDA/Interest', 'Total Debt/EBITDA'
        ]
        ind_values = []
        ind_eval = []
        for idx, col in enumerate(ind_list):
            val = row_feat.get(col)
            ind_values.append(val)
            ind_eval.append(evaluate_ratio(col, val))
        # Format values: percentages vs ratios
        display_values = []
        for col, val in zip(ind_list, ind_values):
            if col in ['ROA','ROE','Net_Profit_Margin','Gross_Margin','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets']:
                # show as percentage if between -1 and 1
                display_values.append("-" if val is None or not np.isfinite(val) else f"{val*100:.2f}%")
            else:
                display_values.append("-" if val is None or not np.isfinite(val) else f"{val:,.2f}")
        indicators_df = pd.DataFrame({
            ('Indicator' if lang == 'en' else 'Chỉ Số'): ind_names_en if lang == 'en' else ind_names_vi,
            ('Value' if lang == 'en' else 'Giá Trị'): display_values,
            ('Evaluation' if lang == 'en' else 'Đánh Giá'): ind_eval
        })
        st.dataframe(indicators_df, use_container_width=True, hide_index=True, key="finance_indicators_table")
        # Multi‑year indicators
        multi_ind = ticker_feat[['Year'] + ind_list].copy()
        # Format each indicator for display
        for col in ind_list:
            multi_ind[col] = multi_ind[col].apply(lambda x: np.nan if x is None or (not np.isfinite(x)) else x)
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi‑year Data") + "**")
        st.dataframe(multi_ind, use_container_width=True, hide_index=True, key="indicators_multiyear_table")

    # ================ TAB 5: NOTES & ASSESSMENT ===================
    with tab5:
        st.markdown(f"### {get_text('notes_assessment_title', lang)}")
        # Compute YoY changes for revenue and net profit
        prev_raw = raw_df[(raw_df['Ticker'].astype(str) == str(ticker)) & (raw_df['Year'] == year - 1)]
        if not prev_raw.empty:
            prev_row = prev_raw.iloc[0]
            prev_rev = to_num(prev_row.get('Net Sales', prev_row.get('Revenue', prev_row.get('Revenue (Bn. VND)', np.nan))))
            prev_np = to_num(prev_row.get('Net Profit For the Year', prev_row.get('Net Profit', np.nan)))
            rev_growth = (revenue - prev_rev) / prev_rev if prev_rev != 0 else np.nan
            np_growth = (net_profit - prev_np) / prev_np if prev_np != 0 else np.nan
        else:
            rev_growth = np.nan
            np_growth = np.nan
        # Compose summary sentences
        if lang == 'vi':
            summary_lines = []
            # Revenue change
            if np.isfinite(rev_growth):
                if rev_growth >= 0:
                    summary_lines.append(f"- Doanh thu tăng {rev_growth*100:.1f}% so với năm trước, đạt {fmt_val(revenue)} tỷ VND")
                else:
                    summary_lines.append(f"- Doanh thu giảm {abs(rev_growth)*100:.1f}% so với năm trước, còn {fmt_val(revenue)} tỷ VND")
            # Net profit change
            if np.isfinite(np_growth):
                if np_growth >= 0:
                    summary_lines.append(f"- Lợi nhuận ròng tăng {np_growth*100:.1f}% lên {fmt_val(net_profit)} tỷ VND")
                else:
                    summary_lines.append(f"- Lợi nhuận ròng giảm {abs(np_growth)*100:.1f}% xuống còn {fmt_val(net_profit)} tỷ VND")
            summary_lines.append(f"- Lưu chuyển tiền từ hoạt động là {fmt_val(ocf)} tỷ VND")
            st.markdown("**Tóm Tắt Hoạt Động:**\n" + "\n".join(summary_lines))
            # Basic analysis and risk notes
            st.markdown("**Phân Tích Kết Quả:**\n" +
                        f"- Biên lợi nhuận ròng {display_values[14]} cho thấy hiệu quả kinh doanh.\n" +
                        f"- Tỷ lệ nợ/tài sản {display_values[3]} và nợ/vốn {display_values[4]} phản ánh cơ cấu vốn.\n" +
                        f"- Tỷ lệ thanh khoản hiện tại {display_values[0]} và thanh khoản nhanh {display_values[1]} đánh giá khả năng thanh toán.")
            st.markdown("**Rủi Ro Chính:**\n" +
                        "- Rủi ro thanh khoản khi tỷ lệ thanh khoản thấp\n" +
                        "- Biến động lợi nhuận do chi phí tài chính và thị trường\n" +
                        "- Sức ép cạnh tranh trong ngành và biến động vĩ mô")
            st.markdown("**Dự Báo:**\n" +
                        "- Doanh thu và lợi nhuận dự kiến biến động theo xu hướng ngành\n" +
                        "- Công ty cần tối ưu cấu trúc vốn và kiểm soát chi phí để cải thiện tỷ suất sinh lời\n" +
                        "- Nhu cầu vốn lưu động có thể tăng khi mở rộng sản xuất")
        else:
            summary_lines = []
            if np.isfinite(rev_growth):
                if rev_growth >= 0:
                    summary_lines.append(f"- Revenue increased {rev_growth*100:.1f}% YoY to {fmt_val(revenue)} bn VND")
                else:
                    summary_lines.append(f"- Revenue decreased {abs(rev_growth)*100:.1f}% YoY to {fmt_val(revenue)} bn VND")
            if np.isfinite(np_growth):
                if np_growth >= 0:
                    summary_lines.append(f"- Net profit increased {np_growth*100:.1f}% to {fmt_val(net_profit)} bn VND")
                else:
                    summary_lines.append(f"- Net profit decreased {abs(np_growth)*100:.1f}% to {fmt_val(net_profit)} bn VND")
            summary_lines.append(f"- Operating cash flow was {fmt_val(ocf)} bn VND")
            st.markdown("**Business Summary:**\n" + "\n".join(summary_lines))
            st.markdown("**Results Analysis:**\n" +
                        f"- Net profit margin of {display_values[14]} indicates operational efficiency.\n" +
                        f"- Debt/Assets of {display_values[3]} and Debt/Equity of {display_values[4]} reflect capital structure.\n" +
                        f"- Current and quick ratios of {display_values[0]} and {display_values[1]} assess liquidity.")
            st.markdown("**Key Risks:**\n" +
                        "- Liquidity risk if current ratios are low\n" +
                        "- Earnings volatility due to financial costs and market conditions\n" +
                        "- Competitive pressure in the industry and macroeconomic headwinds")
            st.markdown("**Outlook:**\n" +
                        "- Revenue and profit expected to follow industry trends\n" +
                        "- Company should optimize capital structure and control costs to improve profitability\n" +
                        "- Working capital needs may rise with production expansion")
