"""
Language configuration for the Streamlit application.
Contains all text strings in Vietnamese (vi) and English (en).
"""

import streamlit as st

LANG_VI = "vi"
LANG_EN = "en"

# Dictionary structure: {key: {vi: "Vietnamese string", en: "English string"}}
TEXTS = {
    # --- Global ---
    "app_title": {
        LANG_VI: "Hệ Thống Đánh Giá Rủi Ro Vỡ Nợ Doanh Nghiệp",
        LANG_EN: "Corporate Default Risk Scoring System"
    },
    "sidebar_ticker_header": {
        LANG_VI: "Lựa chọn Ticker",
        LANG_EN: "Ticker Selection"
    },
    "select_ticker": {
        LANG_VI: "Chọn mã cổ phiếu",
        LANG_EN: "Select ticker"
    },
    "select_year": {
        LANG_VI: "Chọn năm",
        LANG_EN: "Select year"
    },
    "sidebar_report_header": {
        LANG_VI: "Loại Báo Cáo",
        LANG_EN: "Report Type"
    },
    "btn_finance": {
        LANG_VI: "📊 Finance",
        LANG_EN: "📊 Finance"
    },
    "btn_sentiment": {
        LANG_VI: "📰 Sentiment",
        LANG_EN: "📰 Sentiment"
    },
    "btn_summary": {
        LANG_VI: "📈 Summary",
        LANG_EN: "📈 Summary"
    },
    "desc_finance": {
        LANG_VI: "📊 **Phân Tích Tài Chính**\n\nXem báo cáo thu nhập, bảng cân đối kế toán, báo cáo lưu chuyển tiền mặt và các chỉ số tài chính chính.",
        LANG_EN: "📊 **Financial Analysis**\n\nView income statements, balance sheets, cash flow statements, and key financial indicators."
    },
    "desc_sentiment": {
        LANG_VI: "📰 **Phân Tích Tình Cảm**\n\nPhân tích tình cảm tin tức và nhận thức thị trường liên quan đến cổ phiếu đã chọn.",
        LANG_EN: "📰 **Sentiment Analysis**\n\nAnalyze news sentiment and market perception related to the selected stock."
    },
    "desc_summary": {
        LANG_VI: "📈 **Tóm Tắt Rủi Ro**\n\nXem các chỉ số rủi ro toàn diện và số liệu xác suất vỡ nợ.",
        LANG_EN: "📈 **Risk Summary**\n\nView comprehensive risk indicators and default probability metrics."
    },
    "warning_no_data": {
        LANG_VI: "Không có dữ liệu cho Ticker & Năm đã chọn.",
        LANG_EN: "No record for selected Ticker & Year."
    },
    "error_tab_render": {
        LANG_VI: "Lỗi khi hiển thị tab",
        LANG_EN: "Error rendering tab"
    },
    
    # --- Sidebar Metrics (from original app.py) ---
    "profile_header": {
        LANG_VI: "Hồ Sơ Công Ty",
        LANG_EN: "Company Profile"
    },
    "metric_total_assets": {
        LANG_VI: "Tổng Tài Sản",
        LANG_EN: "Total Assets"
    },
    "metric_equity": {
        LANG_VI: "Vốn Chủ Sở Hữu",
        LANG_EN: "Equity"
    },
    "metric_debt": {
        LANG_VI: "Tổng Nợ",
        LANG_EN: "Total Debt"
    },
    "metric_revenue": {
        LANG_VI: "Doanh Thu",
        LANG_EN: "Revenue"
    },
    "metric_net_profit": {
        LANG_VI: "Lợi Nhuận Ròng",
        LANG_EN: "Net Profit"
    },
    "metric_roa": {
        LANG_VI: "ROA",
        LANG_EN: "ROA"
    },
    "metric_roe": {
        LANG_VI: "ROE",
        LANG_EN: "ROE"
    },
    "metric_dta": {
        LANG_VI: "Nợ/Tài Sản",
        LANG_EN: "Debt/Assets"
    },
    "metric_dte": {
        LANG_VI: "Nợ/Vốn Chủ",
        LANG_EN: "Debt/Equity"
    },
    
    # --- Finance Tab ---
    "finance_header": {
        LANG_VI: "📊 Phân Tích Tài Chính Chi Tiết",
        LANG_EN: "📊 Detailed Financial Analysis"
    },
    "finance_tab_income": {
        LANG_VI: "Báo Cáo Thu Nhập",
        LANG_EN: "Income Statement"
    },
    "finance_tab_balance": {
        LANG_VI: "Bảng Cân Đối",
        LANG_EN: "Balance Sheet"
    },
    "finance_tab_cashflow": {
        LANG_VI: "Lưu Chuyển Tiền",
        LANG_EN: "Cash Flow"
    },
    "finance_tab_indicators": {
        LANG_VI: "Chỉ Số Tài Chính",
        LANG_EN: "Financial Indicators"
    },
    "finance_tab_notes": {
        LANG_VI: "Ghi Chú & Đánh Giá",
        LANG_EN: "Notes & Assessment"
    },
    "income_statement_title": {
        LANG_VI: "Báo Cáo Thu Nhập (Income Statement)",
        LANG_EN: "Income Statement"
    },
    "balance_sheet_title": {
        LANG_VI: "Bảng Cân Đối Kế Toán (Balance Sheet)",
        LANG_EN: "Balance Sheet"
    },
    "cashflow_statement_title": {
        LANG_VI: "Báo Cáo Lưu Chuyển Tiền Tệ (Cash Flow Statement)",
        LANG_EN: "Cash Flow Statement"
    },
    "financial_indicators_title": {
        LANG_VI: "Các Chỉ Số Tài Chính Chính",
        LANG_EN: "Key Financial Indicators"
    },
    "notes_assessment_title": {
        LANG_VI: "Ghi Chú và Đánh Giá Tổng Quan",
        LANG_EN: "Notes and Overall Assessment"
    },
    "income_year": {
        LANG_VI: "Năm",
        LANG_EN: "Year"
    },
    "income_company": {
        LANG_VI: "Công ty",
        LANG_EN: "Company"
    },
    "income_sector": {
        LANG_VI: "Ngành",
        LANG_EN: "Sector"
    },
    
    # --- Sentiment Tab ---
    "sentiment_header": {
        LANG_VI: "📰 Phân Tích Tình Cảm & Tin Tức",
        LANG_EN: "📰 Sentiment Analysis & News"
    },
    "sentiment_tab_news": {
        LANG_VI: "Tin Tức Gần Đây",
        LANG_EN: "Recent News"
    },
    "sentiment_tab_analysis": {
        LANG_VI: "Phân Tích Tình Cảm",
        LANG_EN: "Sentiment Analysis"
    },
    "sentiment_tab_assessment": {
        LANG_VI: "Đánh Giá Chung",
        LANG_EN: "Overall Assessment"
    },
    "news_title": {
        LANG_VI: "Tin Tức Liên Quan Đến Mã Cổ Phiếu",
        LANG_EN: "News Related to Stock Ticker"
    },
    "sentiment_analysis_title": {
        LANG_VI: "Phân Tích Tình Cảm Tin Tức",
        LANG_EN: "News Sentiment Analysis"
    },
    "sentiment_assessment_title": {
        LANG_VI: "Đánh Giá Tổng Thể Tình Hình Cổ Phiếu",
        LANG_EN: "Overall Stock Situation Assessment"
    },
    
    # --- Summary Tab (Integrated from original app.py) ---
    "summary_header": {
        LANG_VI: "📈 Tóm Tắt & Đánh Giá Rủi Ro",
        LANG_EN: "📈 Summary & Risk Assessment"
    },
    "summary_section_overview": {
        LANG_VI: "A. Tổng Quan Tài Chính Công Ty",
        LANG_EN: "A. Company Financial Overview"
    },
    "summary_chart_rev_title": {
        LANG_VI: "Xu Hướng Doanh Thu & Lợi Nhuận (Nhiều năm)",
        LANG_EN: "Revenue & Net Profit Trend (Multi-year)"
    },
    "summary_chart_cap_title": {
        LANG_VI: "Cấu Trúc Vốn",
        LANG_EN: "Capital Structure"
    },
    "summary_key_ratios_title": {
        LANG_VI: "Các Chỉ Số Tài Chính Chính",
        LANG_EN: "Key Financial Ratios"
    },
    "summary_section_pd": {
        LANG_VI: "B. Xác Suất Vỡ Nợ (PD) & Ngưỡng Chính Sách",
        LANG_EN: "B. Default Probability (PD) & Policy Band"
    },
    "metric_pd_final": {
        LANG_VI: "PD (đa yếu tố, sau điều chỉnh)",
        LANG_EN: "PD (multi-factor, post-adj.)"
    },
    "metric_policy_band": {
        LANG_VI: "Ngưỡng Chính Sách",
        LANG_EN: "Policy Band"
    },
    "policy_low": {
        LANG_VI: "Thấp",
        LANG_EN: "Low"
    },
    "policy_medium": {
        LANG_VI: "Trung Bình",
        LANG_EN: "Medium"
    },
    "policy_high": {
        LANG_VI: "Cao",
        LANG_EN: "High"
    },
    "policy_floor_cap": {
        LANG_VI: "Ngưỡng Dưới/Trên",
        LANG_EN: "Floor/Cap"
    },
    "policy_exchange": {
        LANG_VI: "Sàn Giao Dịch",
        LANG_EN: "Exchange"
    },
    "summary_section_shap": {
        LANG_VI: "C. Giải Thích Mô Hình (SHAP)",
        LANG_EN: "C. Model Explainability (SHAP)"
    },
    "shap_chart_title": {
        LANG_VI: "Đóng Góp Đặc Trưng Hàng Đầu (SHAP)",
        LANG_EN: "Top Feature Contributions (SHAP)"
    },
    "shap_xaxis_title": {
        LANG_VI: "Giá trị SHAP → PD",
        LANG_EN: "SHAP value → PD"
    },
    "shap_info_not_avail": {
        LANG_VI: "SHAP không khả dụng cho mô hình/đầu vào này.",
        LANG_EN: "SHAP is not available for this model/input."
    },
    "shap_info_unrecog": {
        LANG_VI: "Đầu ra SHAP được phát hiện nhưng các cột không thể nhận dạng.",
        LANG_EN: "SHAP output detected but columns are not recognizable."
    },
    "summary_section_stress": {
        LANG_VI: "D. Kiểm Tra Sức Chịu Đựng — Tác Động Ngành & Hệ Thống",
        LANG_EN: "D. Stress Testing — Sector & Systemic Impacts"
    },
    "stress_caption_baseline": {
        LANG_VI: "Ngành gốc: {sector_raw} → Nhóm: **{bucket}** • PD Cơ sở (sau điều chỉnh): **{baseline_pd}**",
        LANG_EN: "Raw Sector: {sector_raw} → Bucket: **{bucket}** • Baseline PD (post-adj): **{baseline_pd}**"
    },
    "stress_chart_sector_title": {
        LANG_VI: "Tác Động Ngành — ΔPD so với Cơ sở (%) • {bucket}",
        LANG_EN: "Sector Impact — ΔPD vs Baseline (%) • {bucket}"
    },
    "stress_chart_systemic_title": {
        LANG_VI: "Tác Động Hệ Thống — ΔPD so với Cơ sở (%)",
        LANG_EN: "Systemic Impact — ΔPD vs Baseline (%)"
    },
    "stress_yaxis_title": {
        LANG_VI: "Tác Động (%)",
        LANG_EN: "Impact (%)"
    },
    "metric_baseline_pd": {
        LANG_VI: "PD Cơ sở (sau điều chỉnh)",
        LANG_EN: "Baseline PD (post-adj)"
    },
    "metric_max_pd": {
        LANG_VI: "PD Tối đa dưới khủng hoảng",
        LANG_EN: "Max PD under crises"
    },
    "stress_details_expander": {
        LANG_VI: "Chi tiết kịch bản",
        LANG_EN: "Scenario details"
    },
    "stress_type_sector": {
        LANG_VI: "Ngành",
        LANG_EN: "Sector"
    },
    "stress_type_systemic": {
        LANG_VI: "Hệ Thống",
        LANG_EN: "Systemic"
    },
    "stress_table_type": {
        LANG_VI: "Loại",
        LANG_EN: "Type"
    },
    "stress_table_scenario": {
        LANG_VI: "Kịch Bản",
        LANG_EN: "Scenario"
    },
    "stress_table_pd": {
        LANG_VI: "PD",
        LANG_EN: "PD"
    },
    "stress_table_impact": {
        LANG_VI: "Tác Động %",
        LANG_EN: "Impact %"
    },
    "info_no_historical": {
        LANG_VI: "Không có chuỗi dữ liệu lịch sử cho công ty này.",
        LANG_EN: "No historical series for this company."
    },
}

def get_text(key: str, lang: str) -> str:
    """
    Retrieves the localized string for a given key and language.
    Falls back to Vietnamese if the key or language is not found.
    """
    if key not in TEXTS:
        return f"MISSING_KEY: {key}"
    
    if lang == LANG_EN and LANG_EN in TEXTS[key]:
        return TEXTS[key][LANG_EN]
    
    # Default to Vietnamese
    return TEXTS[key][LANG_VI]

def get_current_lang() -> str:
    """
    Retrieves the current language from Streamlit session state.
    Defaults to Vietnamese if not set.
    """
    if 'current_lang' not in st.session_state:
        st.session_state.current_lang = LANG_VI
    return st.session_state.current_lang

def T(key: str) -> str:
    """
    Convenience function to get the translated text based on current session state.
    """
    # Streamlit session state is not available here, so we need to pass the language
    # This function is mainly for use in app.py and tabs where st.session_state is available
    # For now, we'll keep it simple and assume the caller handles the language.
    # The actual implementation in app.py will use get_text(key, st.session_state.current_lang)
    # We will update the tabs to use T(key) and import st.session_state.current_lang
    return get_text(key, get_current_lang())
