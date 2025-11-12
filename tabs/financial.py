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

    # ---------- helpers ----------
    def to_num(x):
        try:
            if pd.isna(x):
                return 0.0
            if isinstance(x, str):
                return float(str(x).replace(",", ""))
            return float(x)
        except Exception:
            return 0.0

    def fmt_val(x):
        return "-" if (x is None or not np.isfinite(x)) else f"{x:,.2f}"

    def evaluate_ratio(name: str, value: float):
        if value is None or not np.isfinite(value):
            return "-"
        thr = {
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
        good, fair = thr.get(name, (None, None))
        if name == 'Total_Debt_to_EBITDA':  # lower better
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

    # Construct multi-year slices for trends
    ticker_raw = raw_df[raw_df["Ticker"].astype(str) == str(ticker)].copy().sort_values("Year")
    ticker_feat = feats_df[feats_df["Ticker"].astype(str) == str(ticker)].copy().sort_values("Year")

    # ---------- builders for full tables ----------
    def build_full_income_table():
        income_mapping = [
            {'en': 'Net Revenue', 'vi': 'Doanh Thu Thuần', 'columns': ['Net Sales', 'Revenue']},
            {'en': 'Cost of Goods Sold', 'vi': 'Giá Vốn Hàng Bán', 'columns': ['Cost of Sales']},
            {'en': 'Gross Profit', 'vi': 'Lợi Nhuận Gộp', 'columns': ['Gross Profit']},
            {'en': 'Financial Income', 'vi': 'Doanh Thu Tài Chính', 'columns': ['Financial Income']},
            {'en': 'Financial Expenses', 'vi': 'Chi Phí Tài Chính', 'columns': ['Financial Expenses']},
            {'en': 'Profit from Joint Ventures', 'vi': 'Lợi Nhuận Từ Công Ty Liên Doanh', 'columns': ['Gain/(loss) from joint ventures', 'Net income from associated companies']},
            {'en': 'Selling Expenses', 'vi': 'Chi Phí Bán Hàng', 'columns': ['Selling Expenses']},
            {'en': 'Administrative Expenses', 'vi': 'Chi Phí Quản Lý', 'columns': ['General & Admin Expenses']},
            {'en': 'Operating Profit', 'vi': 'Lợi Nhuận Hoạt Động', 'columns': ['Operating Profit/Loss']},
            {'en': 'Profit Before Tax', 'vi': 'Lợi Nhuận Trước Thuế', 'columns': ['Profit before tax', 'Net Profit/Loss before tax']},
            {'en': 'Tax Expense', 'vi': 'Chi Phí Thuế', 'calc': lambda r: to_num(r.get('Business income tax - current')) + to_num(r.get('Business income tax - deferred'))},
            {'en': 'Net Profit After Tax', 'vi': 'Lợi Nhuận Ròng', 'columns': ['Net Profit For the Year', 'Net Profit']},
        ]
        years = ticker_raw['Year'].tolist()
        rows = []
        for item in income_mapping:
            row_data = {'Chỉ tiêu' if lang == 'vi' else 'Item': item['vi'] if lang == 'vi' else item['en']}
            for yr in years:
                sub = ticker_raw[ticker_raw['Year'] == yr]
                val = None
                if not sub.empty:
                    r = sub.iloc[0]
                    if 'calc' in item:
                        try:
                            val = item['calc'](r)
                        except Exception:
                            val = None
                    else:
                        for col in item['columns']:
                            if col in r.index and pd.notna(r[col]):
                                val = r[col]; break
                row_data[str(yr)] = to_num(val) if val is not None else None
            rows.append(row_data)
        return pd.DataFrame(rows)

    def build_full_balance_table():
        balance_mapping = [
            {'en': 'Cash and Cash Equivalents', 'vi': 'Tiền & Tương Đương Tiền', 'columns': ['Cash and cash equivalents (Bn. VND)']},
            {'en': 'Short-term Investments', 'vi': 'Đầu Tư Ngắn Hạn', 'columns': ['Short-term investments (Bn. VND)']},
            {'en': 'Accounts Receivable', 'vi': 'Phải Thu', 'columns': ['Accounts receivable (Bn. VND)']},
            {'en': 'Net Inventories', 'vi': 'Hàng Tồn Kho', 'columns': ['Net Inventories', 'Inventories, Net (Bn. VND)']},
            {'en': 'Other Current Assets', 'vi': 'Tài Sản Ngắn Hạn Khác', 'columns': ['Other current assets']},
            {'en': 'Current Assets', 'vi': 'Tổng Tài Sản Ngắn Hạn', 'columns': ['CURRENT ASSETS (Bn. VND)']},
            {'en': 'Fixed Assets', 'vi': 'Tài Sản Cố Định', 'columns': ['Fixed assets (Bn. VND)']},
            {'en': 'Long-term Investments', 'vi': 'Đầu Tư Dài Hạn', 'columns': ['Long-term investments (Bn. VND)']},
            {'en': 'Other Non-current Assets', 'vi': 'Tài Sản Dài Hạn Khác', 'columns': ['Other non-current assets']},
            {'en': 'Total Assets', 'vi': 'Tổng Tài Sản', 'columns': ['TOTAL ASSETS (Bn. VND)']},
            {'en': 'Short-term Borrowings', 'vi': 'Vay Ngắn Hạn', 'columns': ['Short-term borrowings (Bn. VND)']},
            {'en': 'Long-term Borrowings', 'vi': 'Vay Dài Hạn', 'columns': ['Long-term borrowings (Bn. VND)']},
            {'en': 'Current Liabilities', 'vi': 'Nợ Ngắn Hạn', 'columns': ['Current liabilities (Bn. VND)']},
            {'en': 'Long-term Liabilities', 'vi': 'Nợ Dài Hạn', 'columns': ['Long-term liabilities (Bn. VND)']},
            {'en': 'Total Liabilities', 'vi': 'Tổng Nợ', 'columns': ['LIABILITIES (Bn. VND)']},
            {'en': 'Owner’s Equity', 'vi': 'Vốn Chủ Sở Hữu', 'columns': ["OWNER'S EQUITY(Bn.VND)"]},
            {'en': 'Capital and Reserves', 'vi': 'Vốn & Quỹ', 'columns': ['Capital and reserves (Bn. VND)']},
            {'en': 'Undistributed Earnings', 'vi': 'LN Chưa Phân Phối', 'columns': ['Undistributed earnings (Bn. VND)']},
            {'en': 'Total Resources', 'vi': 'Tổng Nguồn Vốn', 'columns': ['TOTAL RESOURCES (Bn. VND)']},
        ]
        years = ticker_raw['Year'].tolist()
        rows = []
        for item in balance_mapping:
            row_data = {'Chỉ tiêu' if lang == 'vi' else 'Item': item['vi'] if lang == 'vi' else item['en']}
            for yr in years:
                sub = ticker_raw[ticker_raw['Year'] == yr]
                val = None
                if not sub.empty:
                    r = sub.iloc[0]
                    for col in item['columns']:
                        if col in r.index and pd.notna(r[col]):
                            val = r[col]; break
                row_data[str(yr)] = to_num(val) if val is not None else None
            rows.append(row_data)
        return pd.DataFrame(rows)

    def build_full_cashflow_table():
        cashflow_mapping = [
            {'en': 'Net Profit', 'vi': 'Lợi Nhuận Ròng', 'columns': ['Net Profit For the Year', 'Net Profit']},
            {'en': 'Depreciation & Amortisation', 'vi': 'Khấu Hao & Khấu Hao', 'columns': ['Depreciation and Amortisation']},
            {'en': 'Provision for Credit Losses', 'vi': 'Dự Phòng Tổn Thất', 'columns': ['Provision for credit losses']},
            {'en': 'Unrealized FX Gain/Loss', 'vi': 'Lãi/Lỗ Tỷ Giá Chưa Thực Hiện', 'columns': ['Unrealized foreign exchange gain/loss']},
            {'en': 'Profit/Loss from Disposal of Fixed Assets', 'vi': 'Lãi/Lỗ Từ Thanh Lý TSCĐ', 'columns': ['Profit/Loss from disposal of fixed assets']},
            {'en': 'Profit/Loss from Investing Activities', 'vi': 'Lãi/Lỗ Hoạt Động Đầu Tư', 'columns': ['Profit/Loss from investing activities']},
            {'en': 'Interest Expense', 'vi': 'Chi Phí Lãi Vay', 'columns': ['Interest Expense']},
            {'en': 'Operating Profit Before Changes in Working Capital', 'vi': 'LN Trước Thay Đổi VLĐ', 'columns': ['Operating profit before changes in working capital']},
            {'en': '(Increase)/Decrease in Receivables', 'vi': '(Tăng)/Giảm Phải Thu', 'columns': ['Increase/Decrease in receivables']},
            {'en': '(Increase)/Decrease in Inventories', 'vi': '(Tăng)/Giảm Hàng Tồn Kho', 'columns': ['Increase/Decrease in inventories']},
            {'en': 'Increase/(Decrease) in Payables', 'vi': 'Tăng/(Giảm) Phải Trả', 'columns': ['Increase/Decrease in payables']},
            {'en': '(Increase)/Decrease in Prepaid Expenses', 'vi': '(Tăng)/Giảm Chi Phí Trả Trước', 'columns': ['Increase/Decrease in prepaid expenses']},
            {'en': 'Net Cash Flow from Operating Activities', 'vi': 'LCT Thuần Hoạt Động', 'columns': ['Net cash inflows/outflows from operating activities']},
            {'en': 'Purchase of Fixed Assets', 'vi': 'Chi Mua TSCĐ', 'columns': ['Purchase of fixed assets']},
            {'en': 'Proceeds from Disposal of Fixed Assets', 'vi': 'Thu Thanh Lý TSCĐ', 'columns': ['Proceeds from disposal of fixed assets']},
            {'en': 'Net Cash Flow from Investing Activities', 'vi': 'LCT Thuần Đầu Tư', 'columns': ['Net Cash Flows from Investing Activities']},
            {'en': 'Proceeds from Borrowings', 'vi': 'Thu Từ Vay', 'columns': ['Proceeds from borrowings']},
            {'en': 'Repayment of Borrowings', 'vi': 'Chi Trả Nợ Vay', 'columns': ['Repayment of borrowings']},
            {'en': 'Dividends Paid', 'vi': 'Trả Cổ Tức', 'columns': ['Dividends paid']},
            {'en': 'Cash Flow from Financial Activities', 'vi': 'LCT Tài Chính', 'columns': ['Cash flows from financial activities']},
            {'en': 'Net Increase/(Decrease) in Cash', 'vi': 'Tăng/(Giảm) Tiền', 'columns': ['Net increase/decrease in cash and cash equivalents']},
        ]
        years = ticker_raw['Year'].tolist()
        rows = []
        for item in cashflow_mapping:
            row_data = {'Chỉ tiêu' if lang == 'vi' else 'Item': item['vi'] if lang == 'vi' else item['en']}
            for yr in years:
                sub = ticker_raw[ticker_raw['Year'] == yr]
                val = None
                if not sub.empty:
                    r = sub.iloc[0]
                    for col in item['columns']:
                        if col in r.index and pd.notna(r[col]):
                            val = r[col]; break
                row_data[str(yr)] = to_num(val) if val is not None else None
            rows.append(row_data)
        return pd.DataFrame(rows)

    def build_full_indicator_table():
        ind_list_local = [
            'Current_Ratio','Quick_Ratio','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity',
            'Equity_to_Liabilities','Long_Term_Debt_to_Assets','Receivables_Turnover','Inventory_Turnover','Asset_Turnover',
            'ROA','ROE','EBIT_to_Assets','Operating_Income_to_Debt','Net_Profit_Margin','Gross_Margin','Interest_Coverage','EBITDA_to_Interest','Total_Debt_to_EBITDA'
        ]
        ind_names_vi_local = [
            'Tỷ Lệ Thanh Khoản Hiện Tại', 'Tỷ Lệ Thanh Khoản Nhanh', 'Vốn Lưu Động/Tổng Tài Sản', 'Tỷ Lệ Nợ/Tài Sản', 'Tỷ Lệ Nợ/Vốn Chủ',
            'Vốn Chủ/Nợ', 'Nợ Dài Hạn/Tài Sản', 'Vòng Quay Phải Thu', 'Vòng Quay Tồn Kho', 'Vòng Quay Tài Sản',
            'ROA', 'ROE', 'EBIT/Tài Sản', 'Thu Nhập Hoạt Động/Nợ', 'Biên Lợi Nhuận Ròng', 'Biên Lợi Nhuận Gộp', 'Khả Năng Chi Trả Lãi', 'EBITDA/Lãi Vay', 'Tổng Nợ/EBITDA'
        ]
        ind_names_en_local = [
            'Current Ratio', 'Quick Ratio', 'Working Capital/Total Assets', 'Debt/Assets', 'Debt/Equity',
            'Equity/Liabilities', 'Long-term Debt/Assets', 'Receivables Turnover', 'Inventory Turnover', 'Asset Turnover',
            'ROA', 'ROE', 'EBIT/Assets', 'Operating Income/Debt', 'Net Profit Margin', 'Gross Margin', 'Interest Coverage', 'EBITDA/Interest', 'Total Debt/EBITDA'
        ]
        indicator_map = {code: (vi if lang == 'vi' else en) for code, vi, en in zip(ind_list_local, ind_names_vi_local, ind_names_en_local)}
        years = ticker_feat['Year'].tolist()
        rows = []
        for code in ind_list_local:
            row_data = {'Chỉ số' if lang == 'vi' else 'Indicator': indicator_map.get(code, code)}
            for yr in years:
                sub = ticker_feat[ticker_feat['Year'] == yr]
                val = None
                if not sub.empty:
                    r = sub.iloc[0]; val = r.get(code, None)
                if val is None or not np.isfinite(val):
                    val_fmt = None
                else:
                    if code in ['ROA','ROE','Net_Profit_Margin','Gross_Margin','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets']:
                        val_fmt = val * 100
                    else:
                        val_fmt = val
                row_data[str(yr)] = val_fmt
            rows.append(row_data)
        return pd.DataFrame(rows)

    # =================== TABS ===================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        get_text("finance_tab_income", lang),
        get_text("finance_tab_balance", lang),
        get_text("finance_tab_cashflow", lang),
        get_text("finance_tab_indicators", lang),
        get_text("finance_tab_notes", lang)
    ])

    # ----------------- TAB 1: INCOME -----------------
    with tab1:
        st.markdown(f"### {get_text('income_statement_title', lang)}")
        st.markdown(f"**{get_text('income_year', lang)}:** {year} | **{get_text('income_company', lang)}:** {ticker} | **{get_text('income_sector', lang)}:** {sector}")

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

        income_items_vi = ['Doanh Thu Thuần', 'Giá Vốn Hàng Bán', 'Lợi Nhuận Gộp', 'Chi Phí Bán Hàng', 'Chi Phí Quản Lý', 'Lợi Nhuận Hoạt Động', 'Chi Phí Lãi Vay', 'Lợi Nhuận Trước Thuế', 'Chi Phí Thuế', 'Lợi Nhuận Ròng']
        income_items_en = ['Net Revenue', 'Cost of Goods Sold', 'Gross Profit', 'Selling Expenses', 'Administrative Expenses', 'Operating Profit', 'Interest Expenses', 'Profit Before Tax', 'Tax Expense', 'Net Profit']
        values = [revenue, cogs, gross_profit, selling_exp, admin_exp, operating_profit, interest_exp, profit_before_tax, tax_expense, net_profit]
        percentages = [f"{(v / revenue)*100:.1f}%" if revenue != 0 else "0.0%" for v in values]
        header_key = "Item" if lang == 'en' else "Chỉ Tiêu"
        income_df = pd.DataFrame({
            header_key: income_items_en if lang == 'en' else income_items_vi,
            ("Value (Bn VND)" if lang == 'en' else "Giá Trị (Tỷ VND)"): [fmt_val(v) for v in values],
            ("% of Revenue" if lang == 'en' else "% Doanh Thu"): percentages
        })
        st.dataframe(income_df, use_container_width=True, hide_index=True, key="finance_income_table")

        trend_years = ticker_raw['Year'].astype(str).tolist()
        trend_rev = [to_num(v) for v in ticker_raw.get('Net Sales', ticker_raw.get('Revenue', ticker_raw.get('Revenue (Bn. VND)', np.nan)))]
        trend_np = [to_num(v) for v in ticker_raw.get('Net Profit For the Year', ticker_raw.get('Net Profit', np.nan))]
        multi_income = pd.DataFrame({'Year': ticker_raw['Year'], ("Net Revenue" if lang == 'en' else "Doanh Thu"): trend_rev, ("Net Profit" if lang == 'en' else "Lợi Nhuận Ròng"): trend_np})
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi-year Data") + "**")
        st.dataframe(multi_income, use_container_width=True, hide_index=True, key="income_multiyear_table")

        full_income_table = build_full_income_table()
        st.markdown("**" + ("Báo cáo kết quả kinh doanh chi tiết" if lang == 'vi' else "Detailed Income Statement") + "**")
        display_income = full_income_table.copy()
        for col in display_income.columns[1:]:
            display_income[col] = display_income[col].apply(lambda x: fmt_val(x) if x is not None else '-')
        st.dataframe(display_income, use_container_width=True, hide_index=True, key="income_full_table")

        fig = go.Figure(data=[go.Bar(name=get_text('metric_revenue', lang), x=trend_years, y=trend_rev),
                              go.Bar(name=get_text('metric_net_profit', lang), x=trend_years, y=trend_np)])
        fig.update_layout(title=("Xu Hướng Doanh Thu & Lợi Nhuận" if lang == 'vi' else "Revenue & Net Profit Trend"), barmode='group', height=350)
        st.plotly_chart(fig, use_container_width=True, key="finance_income_chart")

        # Extra comparisons
        cogs_series = ticker_raw['Cost of Sales'] if 'Cost of Sales' in ticker_raw.columns else pd.Series([0]*len(trend_years), index=ticker_raw.index)
        gross_series = ticker_raw['Gross Profit'] if 'Gross Profit' in ticker_raw.columns else pd.Series([0]*len(trend_years), index=ticker_raw.index)
        op_series = ticker_raw['Operating Profit/Loss'] if 'Operating Profit/Loss' in ticker_raw.columns else pd.Series([0]*len(trend_years), index=ticker_raw.index)
        cogs_trend = [to_num(v) for v in cogs_series]
        gross_trend = [to_num(v) for v in gross_series]
        op_trend = [to_num(v) for v in op_series]
        fig_income_extra = go.Figure()
        lbl_rev = 'Doanh Thu' if lang == 'vi' else 'Revenue'
        lbl_cogs = 'Giá Vốn Hàng Bán' if lang == 'vi' else 'Cost of Goods Sold'
        lbl_gross = 'Lợi Nhuận Gộp' if lang == 'vi' else 'Gross Profit'
        lbl_op = 'Lợi Nhuận Hoạt Động' if lang == 'vi' else 'Operating Profit'
        lbl_np = 'Lợi Nhuận Ròng' if lang == 'vi' else 'Net Profit'
        fig_income_extra.add_trace(go.Scatter(name=lbl_rev, x=trend_years, y=trend_rev, mode='lines+markers'))
        fig_income_extra.add_trace(go.Scatter(name=lbl_cogs, x=trend_years, y=cogs_trend, mode='lines+markers'))
        fig_income_extra.add_trace(go.Scatter(name=lbl_gross, x=trend_years, y=gross_trend, mode='lines+markers'))
        fig_income_extra.add_trace(go.Scatter(name=lbl_op, x=trend_years, y=op_trend, mode='lines+markers'))
        fig_income_extra.add_trace(go.Scatter(name=lbl_np, x=trend_years, y=trend_np, mode='lines+markers'))
        fig_income_extra.update_layout(title=("So sánh các chỉ tiêu thu nhập" if lang == 'vi' else "Comparison of Income Statement Metrics"), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_income_extra, use_container_width=True, key="finance_income_chart_extra")

        gross_margin_trend, operating_margin_trend, net_margin_trend = [], [], []
        for _, r in ticker_raw.iterrows():
            rev_val = to_num(r.get('Net Sales', r.get('Revenue', r.get('Revenue (Bn. VND)', np.nan))))
            gp_val = to_num(r.get('Gross Profit')); op_val = to_num(r.get('Operating Profit/Loss'))
            np_val = to_num(r.get('Net Profit For the Year', r.get('Net Profit', np.nan)))
            if rev_val != 0:
                gross_margin_trend.append((gp_val / rev_val) * 100)
                operating_margin_trend.append((op_val / rev_val) * 100)
                net_margin_trend.append((np_val / rev_val) * 100)
            else:
                gross_margin_trend.append(None); operating_margin_trend.append(None); net_margin_trend.append(None)
        lbl_gm = 'Biên LN gộp' if lang == 'vi' else 'Gross Margin'
        lbl_om = 'Biên LN HĐ' if lang == 'vi' else 'Operating Margin'
        lbl_nm = 'Biên LN ròng' if lang == 'vi' else 'Net Margin'
        fig_margin = go.Figure()
        fig_margin.add_trace(go.Scatter(name=lbl_gm, x=trend_years, y=gross_margin_trend, mode='lines+markers'))
        fig_margin.add_trace(go.Scatter(name=lbl_om, x=trend_years, y=operating_margin_trend, mode='lines+markers'))
        fig_margin.add_trace(go.Scatter(name=lbl_nm, x=trend_years, y=net_margin_trend, mode='lines+markers'))
        fig_margin.update_layout(title=("Xu Hướng Biên Lợi Nhuận" if lang == 'vi' else "Profit Margin Trends"), height=350, yaxis=dict(title=('Phần trăm (%)' if lang == 'vi' else 'Percentage (%)')), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_margin, use_container_width=True, key="finance_income_margin_chart")

    # ----------------- TAB 2: BALANCE SHEET -----------------
    with tab2:
        st.markdown(f"### {get_text('balance_sheet_title', lang)}")

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
        assets_df = pd.DataFrame({('Item' if lang == 'en' else 'Chỉ Tiêu'): assets_items_en if lang == 'en' else assets_items_vi, ('Value (Bn VND)' if lang == 'en' else 'Giá Trị (Tỷ VND)'): [fmt_val(v) for v in assets_values]})

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
        liab_df = pd.DataFrame({('Item' if lang == 'en' else 'Chỉ Tiêu'): liab_items_en if lang == 'en' else liab_items_vi, ('Value (Bn VND)' if lang == 'en' else 'Giá Trị (Tỷ VND)'): [fmt_val(v) for v in liab_values]})

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**" + ("Assets" if lang == 'en' else "Tài Sản") + "**")
            st.dataframe(assets_df, use_container_width=True, hide_index=True, key="finance_assets_table")
        with col2:
            st.markdown("**" + ("Liabilities & Equity" if lang == 'en' else "Nợ & Vốn Chủ") + "**")
            st.dataframe(liab_df, use_container_width=True, hide_index=True, key="finance_liab_table")

        multi_balance = pd.DataFrame({
            'Year': ticker_raw['Year'],
            ('Total Assets' if lang == 'en' else 'Tổng Tài Sản'): [to_num(v) for v in ticker_raw.get('TOTAL ASSETS (Bn. VND)', np.nan)],
            ('Total Liabilities' if lang == 'en' else 'Tổng Nợ'): [to_num(v) for v in ticker_raw.get('LIABILITIES (Bn. VND)', np.nan)],
            ('Equity' if lang == 'en' else 'Vốn Chủ'): [to_num(v) for v in ticker_raw.get("OWNER'S EQUITY(Bn.VND)", np.nan)]
        })
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi-year Data") + "**")
        st.dataframe(multi_balance, use_container_width=True, hide_index=True, key="balance_multiyear_table")

        full_balance_table = build_full_balance_table()
        st.markdown("**" + ("Bảng cân đối kế toán chi tiết" if lang == 'vi' else "Detailed Balance Sheet") + "**")
        display_balance = full_balance_table.copy()
        for col in display_balance.columns[1:]:
            display_balance[col] = display_balance[col].apply(lambda x: fmt_val(x) if x is not None else '-')
        st.dataframe(display_balance, use_container_width=True, hide_index=True, key="balance_full_table")

        mb_years = multi_balance['Year'].astype(str).tolist()
        assets_col = 'Tổng Tài Sản' if lang == 'vi' else 'Total Assets'
        liabilities_col = 'Tổng Nợ' if lang == 'vi' else 'Total Liabilities'
        equity_col = 'Vốn Chủ' if lang == 'vi' else 'Equity'
        assets_series = multi_balance[assets_col].tolist()
        liabilities_series = multi_balance[liabilities_col].tolist()
        equity_series = multi_balance[equity_col].tolist()
        figb = go.Figure(data=[go.Bar(name=assets_col, x=mb_years, y=assets_series),
                               go.Bar(name=liabilities_col, x=mb_years, y=liabilities_series),
                               go.Bar(name=equity_col, x=mb_years, y=equity_series)])
        figb.update_layout(title=("Xu Hướng Tài Sản, Nợ & Vốn" if lang == 'vi' else "Assets, Liabilities & Equity Trend"), barmode='group', height=350)
        st.plotly_chart(figb, use_container_width=True, key="finance_balance_chart")

        # Asset composition
        cash_trend = [to_num(v) for v in ticker_raw.get('Cash and cash equivalents (Bn. VND)', pd.Series([0]*len(mb_years)))]
        recv_trend = [to_num(v) for v in ticker_raw.get('Accounts receivable (Bn. VND)', pd.Series([0]*len(mb_years)))]
        if 'Net Inventories' in ticker_raw.columns:
            inv_trend = [to_num(v) for v in ticker_raw['Net Inventories']]
        elif 'Inventories, Net (Bn. VND)' in ticker_raw.columns:
            inv_trend = [to_num(v) for v in ticker_raw['Inventories, Net (Bn. VND)']]
        else:
            inv_trend = [0]*len(mb_years)
        fixed_trend = [to_num(v) for v in ticker_raw.get('Fixed assets (Bn. VND)', pd.Series([0]*len(mb_years)))]
        longinv_trend = [to_num(v) for v in ticker_raw.get('Long-term investments (Bn. VND)', pd.Series([0]*len(mb_years)))]
        lbl_cash = 'Tiền' if lang == 'vi' else 'Cash'
        lbl_recv = 'Phải Thu' if lang == 'vi' else 'Accounts Receivable'
        lbl_inv = 'Tồn Kho' if lang == 'vi' else 'Inventories'
        lbl_fixed = 'TSCĐ' if lang == 'vi' else 'Fixed Assets'
        lbl_longinv = 'Đầu Tư Dài Hạn' if lang == 'vi' else 'Long-term Investments'
        figb_extra = go.Figure()
        figb_extra.add_trace(go.Scatter(name=lbl_cash, x=mb_years, y=cash_trend, mode='lines+markers'))
        figb_extra.add_trace(go.Scatter(name=lbl_recv, x=mb_years, y=recv_trend, mode='lines+markers'))
        figb_extra.add_trace(go.Scatter(name=lbl_inv, x=mb_years, y=inv_trend, mode='lines+markers'))
        figb_extra.add_trace(go.Scatter(name=lbl_fixed, x=mb_years, y=fixed_trend, mode='lines+markers'))
        figb_extra.add_trace(go.Scatter(name=lbl_longinv, x=mb_years, y=longinv_trend, mode='lines+markers'))
        figb_extra.update_layout(title=("Cơ cấu tài sản" if lang == 'vi' else "Asset Composition"), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(figb_extra, use_container_width=True, key="finance_balance_chart_extra")

        # Capital structure ratios
        debt_ratio = [(l/a)*100 if a else None for a, l in zip(assets_series, liabilities_series)]
        equity_ratio = [(e/a)*100 if a else None for a, e in zip(assets_series, equity_series)]
        fig_ratio = go.Figure()
        fig_ratio.add_trace(go.Scatter(name=('Tỷ lệ Nợ/Tài sản' if lang=='vi' else 'Debt/Assets Ratio'), x=mb_years, y=debt_ratio, mode='lines+markers'))
        fig_ratio.add_trace(go.Scatter(name=('Tỷ lệ Vốn Chủ/Tài sản' if lang=='vi' else 'Equity/Assets Ratio'), x=mb_years, y=equity_ratio, mode='lines+markers'))
        fig_ratio.update_layout(title=("Xu Hướng Tỷ Lệ Nguồn Vốn" if lang == 'vi' else "Capital Structure Ratios Trend"), height=350, yaxis=dict(title=('Phần trăm (%)' if lang == 'vi' else 'Percentage (%)')), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_ratio, use_container_width=True, key="finance_balance_ratio_chart")

        # Borrowing trends
        st_borrow_trend = [to_num(v) for v in ticker_raw.get('Short-term borrowings (Bn. VND)', pd.Series([0]*len(mb_years)))]
        lt_borrow_trend = [to_num(v) for v in ticker_raw.get('Long-term borrowings (Bn. VND)', pd.Series([0]*len(mb_years)))]
        fig_borrow = go.Figure()
        fig_borrow.add_trace(go.Scatter(name=('Vay Ngắn Hạn' if lang=='vi' else 'Short-term Borrowings'), x=mb_years, y=st_borrow_trend, mode='lines+markers'))
        fig_borrow.add_trace(go.Scatter(name=('Vay Dài Hạn' if lang=='vi' else 'Long-term Borrowings'), x=mb_years, y=lt_borrow_trend, mode='lines+markers'))
        fig_borrow.update_layout(title=("Xu Hướng Vay Nợ" if lang == 'vi' else "Borrowing Trends"), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_borrow, use_container_width=True, key="finance_balance_borrow_chart")

        # -------- Sunburst: Assets --------
        total_assets_year = to_num(row_raw.get('TOTAL ASSETS (Bn. VND)'))
        current_assets_year = to_num(row_raw.get('CURRENT ASSETS (Bn. VND)'))
        cash_year = to_num(row_raw.get('Cash and cash equivalents (Bn. VND)'))
        receivables_year = to_num(row_raw.get('Accounts receivable (Bn. VND)'))
        inventories_year = to_num(row_raw.get('Net Inventories', row_raw.get('Inventories, Net (Bn. VND)', 0)))
        other_current_year = to_num(row_raw.get('Other current assets'))
        fixed_assets_year = to_num(row_raw.get('Fixed assets (Bn. VND)'))
        long_inv_year = to_num(row_raw.get('Long-term investments (Bn. VND)'))
        other_noncurrent_year = to_num(row_raw.get('Other non-current assets'))
        noncurrent_total = fixed_assets_year + long_inv_year + other_noncurrent_year

        root_asset = 'Tổng Tài Sản' if lang == 'vi' else 'Total Assets'
        current_assets_label = 'Tài sản ngắn hạn' if lang == 'vi' else 'Current Assets'
        noncurrent_assets_label = 'Tài sản dài hạn' if lang == 'vi' else 'Non-current Assets'
        labels_asset = [root_asset, current_assets_label, ('Tiền' if lang == 'vi' else 'Cash'), ('Phải thu' if lang == 'vi' else 'Accounts Receivable'),
                        ('Hàng tồn kho' if lang == 'vi' else 'Inventories'), ('TS ngắn hạn khác' if lang == 'vi' else 'Other Current Assets'),
                        noncurrent_assets_label, ('TSCĐ' if lang == 'vi' else 'Fixed Assets'), ('Đầu tư dài hạn' if lang == 'vi' else 'Long-term Investments'),
                        ('TS dài hạn khác' if lang == 'vi' else 'Other Non-current Assets')]
        parents_asset = ['', root_asset, current_assets_label, current_assets_label, current_assets_label, current_assets_label, root_asset, noncurrent_assets_label, noncurrent_assets_label, noncurrent_assets_label]
        values_asset = [max(total_assets_year,0.0), max(current_assets_year,0.0), max(cash_year,0.0), max(receivables_year,0.0), max(inventories_year,0.0), max(other_current_year,0.0),
                        max(noncurrent_total,0.0), max(fixed_assets_year,0.0), max(long_inv_year,0.0), max(other_noncurrent_year,0.0)]
        fig_sun_asset = go.Figure(go.Sunburst(
            labels=labels_asset,
            parents=parents_asset,
            values=values_asset,
            branchvalues='total'
        ))
        fig_sun_asset.update_layout(
            title=("Cây phân rã tài sản" if lang == 'vi' else "Asset Breakdown"),
            height=450,
            margin=dict(t=40, l=0, r=0, b=0)
        )
        st.plotly_chart(fig_sun_asset, use_container_width=True, key="finance_balance_asset_sunburst")

        # --- Add narrative commentary on asset composition ---
        tot_assets_safe = total_assets_year if total_assets_year and total_assets_year > 0 else 1.0
        curr_assets_share = (current_assets_year / tot_assets_safe) if current_assets_year else 0.0
        noncurr_assets_share = (noncurrent_total / tot_assets_safe) if noncurrent_total else 0.0
        cash_share = (cash_year / tot_assets_safe) if cash_year else 0.0
        receivables_share = (receivables_year / tot_assets_safe) if receivables_year else 0.0
        inventory_share = (inventories_year / tot_assets_safe) if inventories_year else 0.0
        other_current_share = (other_current_year / tot_assets_safe) if other_current_year else 0.0
        fixed_share = (fixed_assets_year / tot_assets_safe) if fixed_assets_year else 0.0
        longinv_share = (long_inv_year / tot_assets_safe) if long_inv_year else 0.0
        other_non_share = (other_noncurrent_year / tot_assets_safe) if other_noncurrent_year else 0.0
        if lang == 'vi':
            narrative_asset = (
                f"**Phân tích tài sản:** Tài sản ngắn hạn chiếm {curr_assets_share*100:.1f}% tổng tài sản, "
                f"bao gồm tiền {cash_share*100:.1f}%, phải thu {receivables_share*100:.1f}%, tồn kho {inventory_share*100:.1f}% "
                f"và tài sản ngắn hạn khác {other_current_share*100:.1f}%. "
                f"Tài sản dài hạn chiếm {noncurr_assets_share*100:.1f}%, trong đó tài sản cố định {fixed_share*100:.1f}%, "
                f"đầu tư dài hạn {longinv_share*100:.1f}% và tài sản dài hạn khác {other_non_share*100:.1f}%."
            )
        else:
            narrative_asset = (
                f"**Asset composition analysis:** Current assets account for {curr_assets_share*100:.1f}% of total assets, "
                f"including cash {cash_share*100:.1f}%, accounts receivable {receivables_share*100:.1f}%, inventories {inventory_share*100:.1f}% "
                f"and other current assets {other_current_share*100:.1f}%. "
                f"Non-current assets comprise {noncurr_assets_share*100:.1f}%, with fixed assets {fixed_share*100:.1f}%, long-term investments {longinv_share*100:.1f}% "
                f"and other non-current assets {other_non_share*100:.1f}%."
            )
        st.markdown(narrative_asset)

        # -------- Sunburst: Liabilities & Equity --------
        total_liabilities_year = to_num(row_raw.get('LIABILITIES (Bn. VND)'))
        total_equity_year = to_num(row_raw.get("OWNER'S EQUITY(Bn.VND)"))
        total_resources_year = to_num(row_raw.get('TOTAL RESOURCES (Bn. VND)'))
        if total_resources_year <= 0:
            total_resources_year = total_liabilities_year + total_equity_year
        current_liabilities_year = to_num(row_raw.get('Current liabilities (Bn. VND)'))
        long_liabilities_year = to_num(row_raw.get('Long-term liabilities (Bn. VND)'))
        other_liabilities_year = max(total_liabilities_year - (current_liabilities_year + long_liabilities_year), 0.0)
        capital_reserves_year = to_num(row_raw.get('Capital and reserves (Bn. VND)'))
        undistributed_earnings_year = to_num(row_raw.get('Undistributed earnings (Bn. VND)'))
        other_equity_year = max(total_equity_year - (capital_reserves_year + undistributed_earnings_year), 0.0)

        if total_resources_year > 0:
            # Build labels and values for liability & equity sunburst
            root_liab = 'Tổng Nợ & Vốn' if lang == 'vi' else 'Total Liabilities & Equity'
            liabilities_label = 'Nợ' if lang == 'vi' else 'Liabilities'
            equity_label = 'Vốn' if lang == 'vi' else 'Equity'
            labels_liab = [root_liab, liabilities_label,
                           ('Nợ ngắn hạn' if lang == 'vi' else 'Current Liabilities'),
                           ('Nợ dài hạn' if lang == 'vi' else 'Long-term Liabilities'),
                           ('Nợ khác' if lang == 'vi' else 'Other Liabilities'),
                           equity_label,
                           ('Vốn & Quỹ' if lang == 'vi' else 'Capital & Reserves'),
                           ('LN chưa phân phối' if lang == 'vi' else 'Undistributed Earnings'),
                           ('Vốn khác' if lang == 'vi' else 'Other Equity')]
            parents_liab = ['', root_liab, liabilities_label, liabilities_label, liabilities_label,
                            root_liab, equity_label, equity_label, equity_label]
            values_liab = [
                max(total_resources_year, 0.0),
                max(total_liabilities_year, 0.0),
                max(current_liabilities_year, 0.0),
                max(long_liabilities_year, 0.0),
                max(other_liabilities_year, 0.0),
                max(total_equity_year, 0.0),
                max(capital_reserves_year, 0.0),
                max(undistributed_earnings_year, 0.0),
                max(other_equity_year, 0.0),
            ]
            # Create sunburst for liabilities and equity
            fig_sun_liab = go.Figure(go.Sunburst(
                labels=labels_liab,
                parents=parents_liab,
                values=values_liab,
                branchvalues='total'
            ))
            fig_sun_liab.update_layout(
                title=("Cây phân rã Nợ & Vốn" if lang == 'vi' else "Liability & Equity Breakdown"),
                height=450,
                margin=dict(t=40, l=0, r=0, b=0)
            )
            st.plotly_chart(fig_sun_liab, use_container_width=True, key="finance_balance_liab_sunburst")

            # --- Add narrative commentary about capital structure ---
            # Compute shares for liabilities and equity relative to total resources
            total_res_safe = total_resources_year if total_resources_year and total_resources_year > 0 else 1.0
            liab_share = (total_liabilities_year / total_res_safe) if total_liabilities_year else 0.0
            eq_share = (total_equity_year / total_res_safe) if total_equity_year else 0.0
            curr_liab_share = (current_liabilities_year / total_res_safe) if current_liabilities_year else 0.0
            long_liab_share = (long_liabilities_year / total_res_safe) if long_liabilities_year else 0.0
            other_liab_share = (other_liabilities_year / total_res_safe) if other_liabilities_year else 0.0
            cap_res_share = (capital_reserves_year / total_res_safe) if capital_reserves_year else 0.0
            undis_share = (undistributed_earnings_year / total_res_safe) if undistributed_earnings_year else 0.0
            other_eq_share = (other_equity_year / total_res_safe) if other_equity_year else 0.0
            # Build commentary text
            if lang == 'vi':
                narrative = (
                    f"**Phân tích nguồn vốn:** Tổng nợ chiếm khoảng {liab_share*100:.1f}% tổng nguồn vốn, "
                    f"trong đó nợ ngắn hạn {curr_liab_share*100:.1f}%, nợ dài hạn {long_liab_share*100:.1f}% và nợ khác {other_liab_share*100:.1f}%. "
                    f"Vốn chủ sở hữu chiếm {eq_share*100:.1f}%, bao gồm {cap_res_share*100:.1f}% vốn & quỹ, {undis_share*100:.1f}% lợi nhuận chưa phân phối "
                    f"và {other_eq_share*100:.1f}% vốn khác."
                )
            else:
                narrative = (
                    f"**Capital structure analysis:** Liabilities account for about {liab_share*100:.1f}% of total capital, "
                    f"with current liabilities at {curr_liab_share*100:.1f}%, long-term liabilities at {long_liab_share*100:.1f}% and other liabilities at {other_liab_share*100:.1f}%. "
                    f"Equity makes up {eq_share*100:.1f}%, comprising {cap_res_share*100:.1f}% capital & reserves, {undis_share*100:.1f}% undistributed earnings and {other_eq_share*100:.1f}% other equity."
                )
            st.markdown(narrative)
        else:
            st.info("Không có dữ liệu để hiển thị cây phân rã nợ & vốn" if lang == 'vi' else "Insufficient data for liability & equity breakdown")

    # ----------------- TAB 3: CASH FLOW -----------------
    with tab3:
        st.markdown(f"### {get_text('cashflow_statement_title', lang)}")
        cf_items_vi = ['Lợi Nhuận Ròng', 'Khấu Hao & Khấu Hao', 'Thay Đổi Vốn Lưu Động', 'Lưu Chuyển từ Hoạt Động', 'Chi Đầu Tư Cố Định', 'Lưu Chuyển từ Đầu Tư', 'Phát Hành Cổ Phiếu', 'Trả Nợ Vay', 'Lưu Chuyển từ Tài Chính', 'Thay Đổi Tiền Mặt']
        cf_items_en = ['Net Profit', 'Depreciation & Amortization', 'Change in Working Capital', 'Operating Cash Flow', 'Capital Expenditures', 'Investing Cash Flow', 'Equity Issuance', 'Debt Repayment', 'Financing Cash Flow', 'Net Change in Cash']
        net_profit_cf = to_num(row_raw.get('Net Profit For the Year', row_raw.get('Net Profit', np.nan)))
        depreciation = to_num(row_raw.get('Depreciation and Amortisation'))
        wc_change = (to_num(row_raw.get('Increase/Decrease in receivables')) + to_num(row_raw.get('Increase/Decrease in inventories')) +
                     to_num(row_raw.get('Increase/Decrease in payables')) + to_num(row_raw.get('Increase/Decrease in prepaid expenses')))
        ocf = to_num(row_raw.get('Net cash inflows/outflows from operating activities'))
        capex = to_num(row_raw.get('Purchase of fixed assets'))
        investing_cf = to_num(row_raw.get('Net Cash Flows from Investing Activities'))
        equity_issue = to_num(row_raw.get('Increase in charter capital', row_raw.get('Increase in charter captial')))
        debt_repay = to_num(row_raw.get('Repayment of borrowings'))
        financing_cf = to_num(row_raw.get('Cash flows from financial activities'))
        net_change_cash = to_num(row_raw.get('Net increase/decrease in cash and cash equivalents'))
        cf_values = [net_profit_cf, depreciation, wc_change, ocf, capex, investing_cf, equity_issue, debt_repay, financing_cf, net_change_cash]
        cf_df = pd.DataFrame({('Item' if lang == 'en' else 'Chỉ Tiêu'): cf_items_en if lang == 'en' else cf_items_vi, ('Value (Bn VND)' if lang == 'en' else 'Giá Trị (Tỷ VND)'): [fmt_val(v) for v in cf_values]})
        st.dataframe(cf_df, use_container_width=True, hide_index=True, key="finance_cashflow_table")

        figcf = go.Figure(go.Waterfall(x=["Operating","Investing","Financing","Net Change"], y=[ocf,investing_cf,financing_cf,net_change_cash],
                                       connector={"line": {"color": "rgba(63,63,63,0.5)"}}, decreasing={"marker": {"color": "#E24A33"}}, increasing={"marker": {"color": "#1F77B4"}}, totals={"marker": {"color": "#22C55E"}}))
        figcf.update_layout(title=("Lưu Chuyển Tiền Tệ" if lang == 'vi' else 'Cash Flow Waterfall'), height=350)
        st.plotly_chart(figcf, use_container_width=True, key="finance_cashflow_chart")

        multi_cf = pd.DataFrame({
            'Year': ticker_raw['Year'],
            ('Operating CF' if lang == 'en' else 'Lưu Chuyển Hoạt Động'): [to_num(v) for v in ticker_raw.get('Net cash inflows/outflows from operating activities', np.nan)],
            ('Investing CF' if lang == 'en' else 'Lưu Chuyển Đầu Tư'): [to_num(v) for v in ticker_raw.get('Net Cash Flows from Investing Activities', np.nan)],
            ('Financing CF' if lang == 'en' else 'Lưu Chuyển Tài Chính'): [to_num(v) for v in ticker_raw.get('Cash flows from financial activities', np.nan)],
            ('Net Change Cash' if lang == 'en' else 'Thay Đổi Tiền Mặt'): [to_num(v) for v in ticker_raw.get('Net increase/decrease in cash and cash equivalents', np.nan)]
        })
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi-year Data") + "**")
        st.dataframe(multi_cf, use_container_width=True, hide_index=True, key="cashflow_multiyear_table")

        full_cf_table = build_full_cashflow_table()
        st.markdown("**" + ("Báo cáo lưu chuyển tiền tệ chi tiết" if lang == 'vi' else "Detailed Cash Flow Statement") + "**")
        display_cf = full_cf_table.copy()
        for col in display_cf.columns[1:]:
            display_cf[col] = display_cf[col].apply(lambda x: fmt_val(x) if x is not None else '-')
        st.dataframe(display_cf, use_container_width=True, hide_index=True, key="cashflow_full_table")

        cf_years = multi_cf['Year'].astype(str).tolist()
        ocf_col = 'Lưu Chuyển Hoạt Động' if lang == 'vi' else 'Operating CF'
        icf_col = 'Lưu Chuyển Đầu Tư' if lang == 'vi' else 'Investing CF'
        fcf_col = 'Lưu Chuyển Tài Chính' if lang == 'vi' else 'Financing CF'
        net_col = 'Thay Đổi Tiền Mặt' if lang == 'vi' else 'Net Change Cash'
        ocf_series = multi_cf[ocf_col].tolist(); icf_series = multi_cf[icf_col].tolist(); fcf_series = multi_cf[fcf_col].tolist(); net_series = multi_cf[net_col].tolist()
        figcf_multi = go.Figure(data=[go.Bar(name=ocf_col, x=cf_years, y=ocf_series), go.Bar(name=icf_col, x=cf_years, y=icf_series), go.Bar(name=fcf_col, x=cf_years, y=fcf_series), go.Bar(name=net_col, x=cf_years, y=net_series)])
        figcf_multi.update_layout(title=("Xu Hướng Lưu Chuyển Tiền" if lang == 'vi' else "Cash Flow Components Trend"), barmode='group', height=350)
        st.plotly_chart(figcf_multi, use_container_width=True, key="finance_cashflow_chart_multi")

        # Net profit vs Operating CF vs FCF
        if 'Net Profit For the Year' in ticker_raw.columns:
            np_trend_full = [to_num(v) for v in ticker_raw['Net Profit For the Year']]
        elif 'Net Profit' in ticker_raw.columns:
            np_trend_full = [to_num(v) for v in ticker_raw['Net Profit']]
        else:
            np_trend_full = [0]*len(cf_years)
        capex_series_full = ticker_raw.get('Purchase of fixed assets', pd.Series([0]*len(cf_years)))
        capex_trend = [to_num(v) for v in capex_series_full]
        fcf_trend = [(ocf_val - capex_val) if (ocf_val is not None and np.isfinite(ocf_val)) else None for ocf_val, capex_val in zip(ocf_series, capex_trend)]
        figcf_compare = go.Figure()
        figcf_compare.add_trace(go.Scatter(name=('Lợi Nhuận Ròng' if lang=='vi' else 'Net Profit'), x=cf_years, y=np_trend_full, mode='lines+markers'))
        figcf_compare.add_trace(go.Scatter(name=('Lưu Chuyển Hoạt Động' if lang=='vi' else 'Operating CF'), x=cf_years, y=ocf_series, mode='lines+markers'))
        figcf_compare.add_trace(go.Scatter(name=('Dòng Tiền Tự Do' if lang=='vi' else 'Free Cash Flow'), x=cf_years, y=fcf_trend, mode='lines+markers'))
        figcf_compare.update_layout(title=("So sánh LN, LCT HĐ & FCF" if lang == 'vi' else "Net Profit, Operating CF & Free Cash Flow"), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(figcf_compare, use_container_width=True, key="finance_cashflow_chart_extra")

    # ----------------- TAB 4: INDICATORS -----------------
    with tab4:
        st.markdown(f"### {get_text('financial_indicators_title', lang)}")
        ind_list = ['Current_Ratio','Quick_Ratio','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets','Receivables_Turnover','Inventory_Turnover','Asset_Turnover','ROA','ROE','EBIT_to_Assets','Operating_Income_to_Debt','Net_Profit_Margin','Gross_Margin','Interest_Coverage','EBITDA_to_Interest','Total_Debt_to_EBITDA']
        ind_names_vi = ['Tỷ Lệ Thanh Khoản Hiện Tại','Tỷ Lệ Thanh Khoản Nhanh','Vốn Lưu Động/Tổng Tài Sản','Tỷ Lệ Nợ/Tài Sản','Tỷ Lệ Nợ/Vốn Chủ','Vốn Chủ/Nợ','Nợ Dài Hạn/Tài Sản','Vòng Quay Phải Thu','Vòng Quay Tồn Kho','Vòng Quay Tài Sản','ROA','ROE','EBIT/Tài Sản','Thu Nhập Hoạt Động/Nợ','Biên Lợi Nhuận Ròng','Biên Lợi Nhuận Gộp','Khả Năng Chi Trả Lãi','EBITDA/Lãi Vay','Tổng Nợ/EBITDA']
        ind_names_en = ['Current Ratio','Quick Ratio','Working Capital/Total Assets','Debt/Assets','Debt/Equity','Equity/Liabilities','Long-term Debt/Assets','Receivables Turnover','Inventory Turnover','Asset Turnover','ROA','ROE','EBIT/Assets','Operating Income/Debt','Net Profit Margin','Gross Margin','Interest Coverage','EBITDA/Interest','Total Debt/EBITDA']
        ind_values, ind_eval = [], []
        for col in ind_list:
            val = row_feat.get(col); ind_values.append(val); ind_eval.append(evaluate_ratio(col, val))

        display_values = []
        for col, val in zip(ind_list, ind_values):
            if col in ['ROA','ROE','Net_Profit_Margin','Gross_Margin','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets']:
                display_values.append("-" if val is None or not np.isfinite(val) else f"{val*100:.2f}%")
            else:
                display_values.append("-" if val is None or not np.isfinite(val) else f"{val:,.2f}")
        indicators_df = pd.DataFrame({('Indicator' if lang == 'en' else 'Chỉ Số'): ind_names_en if lang == 'en' else ind_names_vi, ('Value' if lang == 'en' else 'Giá Trị'): display_values, ('Evaluation' if lang == 'en' else 'Đánh Giá'): ind_eval})
        st.dataframe(indicators_df, use_container_width=True, hide_index=True, key="finance_indicators_table")

        multi_ind = ticker_feat[['Year'] + ind_list].copy()
        for col in ind_list:
            multi_ind[col] = multi_ind[col].apply(lambda x: np.nan if x is None or (not np.isfinite(x)) else x)
        st.markdown("**" + ("Dữ liệu nhiều năm" if lang=='vi' else "Multi-year Data") + "**")
        st.dataframe(multi_ind, use_container_width=True, hide_index=True, key="indicators_multiyear_table")

        full_ind_table = build_full_indicator_table()
        st.markdown("**" + ("Bảng chỉ số tài chính chi tiết" if lang == 'vi' else "Detailed Financial Indicators") + "**")
        display_ind = full_ind_table.copy()
        for col in display_ind.columns[1:]:
            display_ind[col] = display_ind[col].apply(lambda x: fmt_val(x) if x is not None else '-')
        st.dataframe(display_ind, use_container_width=True, hide_index=True, key="indicators_full_table")

        selected_codes = ['Current_Ratio','Debt_to_Equity','ROA','ROE','Net_Profit_Margin']
        indicator_name_map = {code: (ind_names_vi[idx] if lang == 'vi' else ind_names_en[idx]) for idx, code in enumerate(ind_list)}
        years_ind = multi_ind['Year'].astype(str).tolist()
        percent_codes = ['ROA','ROE','Net_Profit_Margin','Gross_Margin','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets']
        fig_ind = go.Figure()
        for code in selected_codes:
            y_vals = []
            for val in multi_ind[code].tolist():
                if val is None or (isinstance(val, float) and not np.isfinite(val)):
                    y_vals.append(None)
                else:
                    y_vals.append(val * 100 if code in percent_codes else val)
            fig_ind.add_trace(go.Scatter(name=indicator_name_map.get(code, code), x=years_ind, y=y_vals, mode='lines+markers'))
        fig_ind.update_layout(title=("Xu Hướng Một Số Chỉ Số Tài Chính" if lang == 'vi' else "Selected Financial Ratios Trend"), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_ind, use_container_width=True, key="finance_indicators_chart")

        eff_codes = ['Asset_Turnover', 'Inventory_Turnover', 'Receivables_Turnover']
        fig_eff = go.Figure()
        for code in eff_codes:
            y_vals_eff = [None if (val is None or (isinstance(val, float) and not np.isfinite(val))) else val for val in multi_ind[code].tolist()]
            fig_eff.add_trace(go.Scatter(name=indicator_name_map.get(code, code), x=years_ind, y=y_vals_eff, mode='lines+markers'))
        fig_eff.update_layout(title=("Xu Hướng Chỉ Số Hiệu Suất" if lang == 'vi' else "Efficiency Ratios Trend"), height=350, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig_eff, use_container_width=True, key="finance_indicators_chart_extra")

        # Overview bar
        numeric_ind_vals, bar_colors, bar_names = [], [], []
        for code, val, eval_str in zip(ind_list, ind_values, ind_eval):
            bar_names.append(indicator_name_map.get(code, code))
            if val is None or not np.isfinite(val):
                numeric_ind_vals.append(0)
            else:
                numeric_ind_vals.append(val*100 if code in ['ROA','ROE','Net_Profit_Margin','Gross_Margin','Working_Capital_to_Total_Assets','Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets'] else val)
            colour = '#d1d5db'
            if eval_str:
                if ('Tốt' in eval_str) or ('Good' in eval_str): colour = '#22c55e'
                elif ('Bình' in eval_str) or ('Fair' in eval_str): colour = '#fbbf24'
                elif ('Kém' in eval_str) or ('Poor' in eval_str): colour = '#ef4444'
            bar_colors.append(colour)
        fig_bar_ind = go.Figure()
        fig_bar_ind.add_trace(go.Bar(x=numeric_ind_vals, y=bar_names, orientation='h', marker_color=bar_colors))
        fig_bar_ind.update_layout(title=("Tổng quan các chỉ số tài chính" if lang == 'vi' else "Financial Ratios Overview"), height=500, xaxis=dict(title=('Giá trị' if lang == 'vi' else 'Value')), yaxis=dict(automargin=True), showlegend=False)
        st.plotly_chart(fig_bar_ind, use_container_width=True, key="finance_indicators_overview_chart")

        # Radar summary
        eval_map_good, eval_map_fair, eval_map_poor = ['Tốt','Good'], ['Bình','Fair'], ['Kém','Poor']
        eval_dict = {code: ind_eval[idx] if idx < len(ind_eval) else None for idx, code in enumerate(ind_list)}
        categories_codes = {
            'Liquidity': ['Current_Ratio','Quick_Ratio','Working_Capital_to_Total_Assets'],
            'Leverage': ['Debt_to_Assets','Debt_to_Equity','Equity_to_Liabilities','Long_Term_Debt_to_Assets','Total_Debt_to_EBITDA'],
            'Profitability': ['ROA','ROE','EBIT_to_Assets','Operating_Income_to_Debt','Net_Profit_Margin','Gross_Margin'],
            'Efficiency': ['Asset_Turnover','Inventory_Turnover','Receivables_Turnover']
        }
        cat_display = {'Liquidity': ('Thanh khoản' if lang=='vi' else 'Liquidity'), 'Leverage': ('Đòn bẩy' if lang=='vi' else 'Leverage'), 'Profitability': ('Sinh lời' if lang=='vi' else 'Profitability'), 'Efficiency': ('Hiệu suất' if lang=='vi' else 'Efficiency')}
        category_scores, category_labels = [], []
        for cat_key, codes in categories_codes.items():
            scores = []
            for code in codes:
                ev = eval_dict.get(code)
                if ev is None or (isinstance(ev, str) and ev.strip() == '-'):
                    scores.append(0.5)
                else:
                    if any(k in ev for k in eval_map_good): scores.append(1.0)
                    elif any(k in ev for k in eval_map_fair): scores.append(0.5)
                    elif any(k in ev for k in eval_map_poor): scores.append(0.0)
                    else: scores.append(0.5)
            category_scores.append(np.mean(scores)*100 if scores else 50.0)
            category_labels.append(cat_display.get(cat_key, cat_key))
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(r=category_scores + [category_scores[0]] if category_scores else [], theta=category_labels + [category_labels[0]] if category_labels else [], fill='toself', name=("Điểm theo nhóm" if lang == 'vi' else "Category Scores")))
        fig_radar.update_layout(title=("Tổng quan theo nhóm chỉ số" if lang == 'vi' else "Category Performance Overview"), polar=dict(radialaxis=dict(range=[0,100], visible=True, tickvals=[0,25,50,75,100], ticktext=['0%','25%','50%','75%','100%']), angularaxis=dict(rotation=90)), height=400, showlegend=False, font=dict(family="Arial", size=14))
        st.plotly_chart(fig_radar, use_container_width=True, key="finance_indicators_radar_chart")

        overall_score = float(np.mean([s for s in category_scores if s is not None])) if category_scores else 50.0
        fig_gauge = go.Figure(go.Indicator(mode="gauge+number", value=overall_score, number={'suffix': '%'}, title={'text': ("Điểm tổng thể" if lang == 'vi' else "Overall Score")}, gauge={'axis': {'range': [0,100]}, 'bar': {'color': '#3b82f6'}, 'steps': [{'range': [0,33], 'color':'#fca5a5'},{'range':[33,66],'color':'#fde68a'},{'range':[66,100],'color':'#86efac'}], 'threshold': {'line': {'color':'#ef4444','width':4}, 'thickness': 0.75, 'value': overall_score}}))
        fig_gauge.update_layout(height=300, margin=dict(t=30,b=10,l=20,r=20), font=dict(family="Arial", size=14))
        st.plotly_chart(fig_gauge, use_container_width=True, key="finance_indicators_gauge_chart")

    # ----------------- TAB 5: NOTES -----------------
    with tab5:
        st.markdown(f"### {get_text('notes_assessment_title', lang)}")
        prev_raw = raw_df[(raw_df['Ticker'].astype(str) == str(ticker)) & (raw_df['Year'] == year - 1)]
        if not prev_raw.empty:
            prev_row = prev_raw.iloc[0]
            prev_rev = to_num(prev_row.get('Net Sales', prev_row.get('Revenue', prev_row.get('Revenue (Bn. VND)', np.nan))))
            prev_np = to_num(prev_row.get('Net Profit For the Year', prev_row.get('Net Profit', np.nan)))
            rev_growth = (revenue - prev_rev) / prev_rev if prev_rev != 0 else np.nan
            np_growth = (net_profit - prev_np) / prev_np if prev_np != 0 else np.nan
        else:
            rev_growth = np.nan; np_growth = np.nan

        if lang == 'vi':
            summary_lines = []
            if np.isfinite(rev_growth):
                summary_lines.append(f"- Doanh thu {'tăng' if rev_growth>=0 else 'giảm'} {abs(rev_growth)*100:.1f}% so với năm trước, đạt {fmt_val(revenue)} tỷ VND")
            if np.isfinite(np_growth):
                summary_lines.append(f"- Lợi nhuận ròng {'tăng' if np_growth>=0 else 'giảm'} {abs(np_growth)*100:.1f}% {'lên' if np_growth>=0 else 'còn'} {fmt_val(net_profit)} tỷ VND")
            summary_lines.append(f"- Lưu chuyển tiền từ hoạt động là {fmt_val(ocf)} tỷ VND")
            st.markdown("**Tóm Tắt Hoạt Động:**\n" + "\n".join(summary_lines))
            st.markdown("**Phân Tích Kết Quả:**\n" + f"- Biên lợi nhuận ròng {display_values[14]} cho thấy hiệu quả kinh doanh.\n" + f"- Tỷ lệ nợ/tài sản {display_values[3]} và nợ/vốn {display_values[4]} phản ánh cơ cấu vốn.\n" + f"- Tỷ lệ thanh khoản hiện tại {display_values[0]} và thanh khoản nhanh {display_values[1]} đánh giá khả năng thanh toán.")
            st.markdown("**Rủi Ro Chính:**\n- Rủi ro thanh khoản khi tỷ lệ thanh khoản thấp\n- Biến động lợi nhuận do chi phí tài chính và thị trường\n- Sức ép cạnh tranh trong ngành và biến động vĩ mô")
            st.markdown("**Dự Báo:**\n- Doanh thu và lợi nhuận dự kiến biến động theo xu hướng ngành\n- Công ty cần tối ưu cấu trúc vốn và kiểm soát chi phí để cải thiện tỷ suất sinh lời\n- Nhu cầu vốn lưu động có thể tăng khi mở rộng sản xuất")
        else:
            summary_lines = []
            if np.isfinite(rev_growth):
                summary_lines.append(f"- Revenue {'increased' if rev_growth>=0 else 'decreased'} {abs(rev_growth)*100:.1f}% YoY to {fmt_val(revenue)} bn VND")
            if np.isfinite(np_growth):
                summary_lines.append(f"- Net profit {'increased' if np_growth>=0 else 'decreased'} {abs(np_growth)*100:.1f}% to {fmt_val(net_profit)} bn VND")
            summary_lines.append(f"- Operating cash flow was {fmt_val(ocf)} bn VND")
            st.markdown("**Business Summary:**\n" + "\n".join(summary_lines))
            st.markdown("**Results Analysis:**\n" + f"- Net profit margin of {display_values[14]} indicates operational efficiency.\n" + f"- Debt/Assets of {display_values[3]} and Debt/Equity of {display_values[4]} reflect capital structure.\n" + f"- Current and quick ratios of {display_values[0]} and {display_values[1]} assess liquidity.")
            st.markdown("**Key Risks:**\n- Liquidity risk if current ratios are low\n- Earnings volatility due to financial costs and market conditions\n- Competitive pressure in the industry and macroeconomic headwinds")
            st.markdown("**Outlook:**\n- Revenue and profit expected to follow industry trends\n- Company should optimize capital structure and control costs to improve profitability\n- Working capital needs may rise with production expansion")
