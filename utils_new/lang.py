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
	    "finance_placeholder_data": {
	        LANG_VI: "Dữ liệu {section} chi tiết sẽ được hiển thị tại đây (Cần tích hợp API dữ liệu).",
	        LANG_EN: "Detailed {section} data will be displayed here (Requires data API integration)."
	    },
	    "finance_section_profitability": {
	        LANG_VI: "Hiệu Quả Sinh Lời",
	        LANG_EN: "Profitability"
	    },
	    "finance_section_leverage": {
	        LANG_VI: "Đòn Bẩy Tài Chính",
	        LANG_EN: "Financial Leverage"
	    },
	    "metric_name": {
	        LANG_VI: "Chỉ Số",
	        LANG_EN: "Metric"
	    },
	    "metric_sector_avg": {
	        LANG_VI: "Trung Bình Ngành",
	        LANG_EN: "Sector Average"
	    },
	    "finance_assess_profit_good": {
	        LANG_VI: "Hiệu quả sinh lời vượt trội",
	        LANG_EN: "Superior profitability"
	    },
	    "finance_assess_profit_bad": {
	        LANG_VI: "Hiệu quả sinh lời kém",
	        LANG_EN: "Poor profitability"
	    },
	    "finance_assess_profit_neutral": {
	        LANG_VI: "Hiệu quả sinh lời ở mức trung bình",
	        LANG_EN: "Average profitability"
	    },
	    "finance_assess_leverage_good": {
	        LANG_VI: "Cấu trúc vốn an toàn",
	        LANG_EN: "Safe capital structure"
	    },
	    "finance_assess_leverage_bad": {
	        LANG_VI: "Rủi ro đòn bẩy cao",
	        LANG_EN: "High leverage risk"
	    },
	    "finance_assess_leverage_neutral": {
	        LANG_VI: "Đòn bẩy ở mức chấp nhận được",
	        LANG_EN: "Acceptable leverage"
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
	    
	    # --- Sentiment Tab - New Keys ---
	    "sentiment_col_date": {
	        LANG_VI: "Ngày",
	        LANG_EN: "Date"
	    },
	    "sentiment_col_source": {
	        LANG_VI: "Nguồn",
	        LANG_EN: "Source"
	    },
	    "sentiment_col_title": {
	        LANG_VI: "Tiêu Đề",
	        LANG_EN: "Title"
	    },
	    "sentiment_col_sentiment": {
	        LANG_VI: "Tình Cảm",
	        LANG_EN: "Sentiment"
	    },
	    "sentiment_chart_trend_name": {
	        LANG_VI: "Điểm Tình Cảm",
	        LANG_EN: "Sentiment Score"
	    },
	    "sentiment_chart_trend_title": {
	        LANG_VI: "Xu Hướng Tình Cảm Tin Tức",
	        LANG_EN: "News Sentiment Trend"
	    },
	    "sentiment_metric_score": {
	        LANG_VI: "Điểm Tình Cảm",
	        LANG_EN: "Sentiment Score"
	    },
	    "sentiment_metric_label": {
	        LANG_VI: "Phân Loại",
	        LANG_EN: "Classification"
	    },
	    "sentiment_label_positive": {
	        LANG_VI: "Tích Cực",
	        LANG_EN: "Positive"
	    },
	    "sentiment_label_neutral": {
	        LANG_VI: "Trung Tính",
	        LANG_EN: "Neutral"
	    },
	    "sentiment_label_negative": {
	        LANG_VI: "Tiêu Cực",
	        LANG_EN: "Negative"
	    },
	    "sentiment_dist_title": {
	        LANG_VI: "Phân Phối Tình Cảm",
	        LANG_EN: "Sentiment Distribution"
	    },
	    "sentiment_factors_title": {
	        LANG_VI: "Các Yếu Tố Tác Động Chính",
	        LANG_EN: "Key Impact Factors"
	    },
	    "sentiment_factor_name": {
	        LANG_VI: "Yếu Tố",
	        LANG_EN: "Factor"
	    },
	    "sentiment_factor_impact": {
	        LANG_VI: "Tác Động (%)",
	        LANG_EN: "Impact (%)"
	    },
	    "sentiment_factor_biz_results": {
	        LANG_VI: "Kết Quả Kinh Doanh",
	        LANG_EN: "Business Results"
	    },
	    "sentiment_factor_product_dev": {
	        LANG_VI: "Phát Triển Sản Phẩm",
	        LANG_EN: "Product Development"
	    },
	    "sentiment_factor_industry": {
	        LANG_VI: "Tình Hình Ngành",
	        LANG_EN: "Industry Situation"
	    },
	    "sentiment_factor_risk_mgmt": {
	        LANG_VI: "Quản Lý Rủi Ro",
	        LANG_EN: "Risk Management"
	    },
	    "sentiment_factor_outlook": {
	        LANG_VI: "Triển Vọng Tương Lai",
	        LANG_EN: "Future Outlook"
	    },
	    "sentiment_analysis_detail_title": {
	        LANG_VI: "Chi Tiết Phân Tích Tình Cảm",
	        LANG_EN: "Detailed Sentiment Analysis"
	    },
	    "sentiment_category_name": {
	        LANG_VI: "Danh Mục",
	        LANG_EN: "Category"
	    },
	    "sentiment_category_avg_score": {
	        LANG_VI: "Điểm Trung Bình",
	        LANG_EN: "Average Score"
	    },
	    "sentiment_category_trend": {
	        LANG_VI: "Xu Hướng",
	        LANG_EN: "Trend"
	    },
	    "sentiment_category_financial": {
	        LANG_VI: "Tài Chính",
	        LANG_EN: "Financial"
	    },
	    "sentiment_category_operations": {
	        LANG_VI: "Hoạt Động",
	        LANG_EN: "Operations"
	    },
	    "sentiment_category_market": {
	        LANG_VI: "Thị Trường",
	        LANG_EN: "Market"
	    },
	    "sentiment_category_management": {
	        LANG_VI: "Quản Lý",
	        LANG_EN: "Management"
	    },
	    "sentiment_category_risk": {
	        LANG_VI: "Rủi Ro",
	        LANG_EN: "Risk"
	    },
	    "sentiment_trend_up": {
	        LANG_VI: "↑ Tăng",
	        LANG_EN: "↑ Up"
	    },
	    "sentiment_trend_stable": {
	        LANG_VI: "→ Ổn Định",
	        LANG_EN: "→ Stable"
	    },
	    "sentiment_trend_down": {
	        LANG_VI: "↓ Giảm",
	        LANG_EN: "↓ Down"
	    },
	    "sentiment_assess_high": {
	        LANG_VI: "Tình cảm thị trường đối với {ticker} hiện tại là **Rất Tích Cực**. Các tin tức và sự kiện gần đây đều hỗ trợ mạnh mẽ cho triển vọng của công ty.",
	        LANG_EN: "Market sentiment towards {ticker} is currently **Very Positive**. Recent news and events strongly support the company's outlook."
	    },
	    "sentiment_assess_medium": {
	        LANG_VI: "Tình cảm thị trường đối với {ticker} hiện tại là **Trung Tính**. Có sự cân bằng giữa các tin tức tích cực và tiêu cực. Cần theo dõi sát sao.",
	        LANG_EN: "Market sentiment towards {ticker} is currently **Neutral**. There is a balance between positive and negative news. Close monitoring is required."
	    },
	    "sentiment_assess_low": {
	        LANG_VI: "Tình cảm thị trường đối với {ticker} hiện tại là **Tiêu Cực**. Các tin tức tiêu cực đang chiếm ưu thế, có thể ảnh hưởng đến giá cổ phiếu và niềm tin nhà đầu tư.",
	        LANG_EN: "Market sentiment towards {ticker} is currently **Negative**. Negative news is dominating, which may affect stock price and investor confidence."
	    },
	    "sentiment_key_metrics_title": {
	        LANG_VI: "Các Chỉ Số Chính",
	        LANG_EN: "Key Metrics"
	    },
	    "sentiment_metric_avg_score": {
	        LANG_VI: "Điểm TB Tình Cảm",
	        LANG_EN: "Avg Sentiment Score"
	    },
	    "sentiment_metric_positive_pct": {
	        LANG_VI: "Tin Tức Tích Cực (%)",
	        LANG_EN: "Positive News (%)"
	    },
	    "sentiment_metric_confidence": {
	        LANG_VI: "Độ Tin Cậy",
	        LANG_EN: "Confidence"
	    },
	    "sentiment_metric_trend": {
	        LANG_VI: "Xu Hướng",
	        LANG_EN: "Trend"
	    },
	    "sentiment_confidence_high": {
	        LANG_VI: "Cao",
	        LANG_EN: "High"
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
	    
	    # --- RCM Assessment ---
	    "summary_section_rcm": {
	        LANG_VI: "E. Đánh Giá Rủi Ro Tổng Thể (RCM)",
	        LANG_EN: "E. Overall Risk Assessment (RCM)"
	    },
	    "rcm_assessment_title": {
	        LANG_VI: "Phân Loại Rủi Ro",
	        LANG_EN: "Risk Classification"
	    },
	    "rcm_low_risk": {
	        LANG_VI: "Rủi Ro Thấp",
	        LANG_EN: "Low Risk"
	    },
	    "rcm_medium_risk": {
	        LANG_VI: "Rủi Ro Trung Bình",
	        LANG_EN: "Medium Risk"
	    },
	    "rcm_high_risk": {
	        LANG_VI: "Rủi Ro Cao",
	        LANG_EN: "High Risk"
	    },
	    "rcm_low_detail": {
	        LANG_VI: "Công ty có PD cơ sở ({pd_final}) và PD tối đa dưới khủng hoảng ({max_pd}) đều ở mức thấp. Rủi ro vỡ nợ được đánh giá là thấp.",
	        LANG_EN: "The company has a low baseline PD ({pd_final}) and a low maximum PD under crisis ({max_pd}). The default risk is assessed as low."
	    },
	    "rcm_medium_detail": {
	        LANG_VI: "PD cơ sở ({pd_final}) ở mức trung bình và PD tối đa dưới khủng hoảng ({max_pd}) cho thấy khả năng chịu đựng ở mức chấp nhận được. Cần theo dõi sát sao.",
	        LANG_EN: "The baseline PD ({pd_final}) is moderate, and the maximum PD under crisis ({max_pd}) indicates acceptable resilience. Close monitoring is required."
	    },
	    "rcm_high_detail": {
	        LANG_VI: "PD cơ sở ({pd_final}) và/hoặc PD tối đa dưới khủng hoảng ({max_pd}) ở mức cao. Rủi ro vỡ nợ đáng kể, cần có biện pháp quản lý rủi ro khẩn cấp.",
	        LANG_EN: "The baseline PD ({pd_final}) and/or maximum PD under crisis ({max_pd}) are high. Significant default risk, urgent risk management measures are needed."
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
