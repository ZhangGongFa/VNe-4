"""
Language configuration for the Streamlit application.
Contains all text strings in Vietnamese (vi) and English (en).
"""

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
    "metric_roa": {
        LANG_VI: "ROA",
        LANG_EN: "ROA"
    },
    "metric_roe": {
        LANG_VI: "ROE",
        LANG_EN: "ROE"
    },
    "metric_dta": {
        LANG_VI: "Tỷ Lệ Nợ/Tài Sản",
        LANG_EN: "Debt-to-Assets"
    },
    "error_tab_render": {
        LANG_VI: "Lỗi khi hiển thị tab",
        LANG_EN: "Error rendering tab"
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
        LANG_VI: "Ghi Chú",
        LANG_EN: "Notes"
    },
    "income_statement_title": {
        LANG_VI: "Báo Cáo Thu Nhập (Income Statement)",
        LANG_EN: "Income Statement"
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
    
    # --- Summary Tab ---
    "summary_header": {
        LANG_VI: "📈 Tóm Tắt & Đánh Giá Rủi Ro",
        LANG_EN: "📈 Summary & Risk Assessment"
    },
    "summary_tab_dashboard": {
        LANG_VI: "Dashboard Tóm Tắt",
        LANG_EN: "Summary Dashboard"
    },
    "summary_tab_risk": {
        LANG_VI: "Đánh Giá Rủi Ro",
        LANG_EN: "Risk Assessment"
    },
    "summary_tab_model": {
        LANG_VI: "Chi Tiết Mô Hình",
        LANG_EN: "Model Details"
    },
    "summary_dashboard_title": {
        LANG_VI: "Dashboard Tóm Tắt (Summary Dashboard)",
        LANG_EN: "Summary Dashboard"
    },
    "metric_total_assets": {
        LANG_VI: "Tổng Tài Sản",
        LANG_EN: "Total Assets"
    },
    "metric_revenue": {
        LANG_VI: "Doanh Thu",
        LANG_EN: "Revenue"
    },
    "metric_net_profit": {
        LANG_VI: "Lợi Nhuận Ròng",
        LANG_EN: "Net Profit"
    },
    "chart_trend_title": {
        LANG_VI: "Xu Hướng Doanh Thu & Lợi Nhuận",
        LANG_EN: "Revenue & Net Profit Trend"
    },
    "chart_trend_yaxis1": {
        LANG_VI: "Doanh Thu (Tỷ VND)",
        LANG_EN: "Revenue (Billion VND)"
    },
    "chart_trend_yaxis2": {
        LANG_VI: "Lợi Nhuận (Tỷ VND)",
        LANG_EN: "Net Profit (Billion VND)"
    },
    "chart_risk_gauge_title": {
        LANG_VI: "Các Chỉ Báo Rủi Ro Chính",
        LANG_EN: "Key Risk Indicators"
    },
    "gauge_health": {
        LANG_VI: "Sức Khỏe TC",
        LANG_EN: "Financial Health"
    },
    "gauge_credit_risk": {
        LANG_VI: "Rủi Ro TD",
        LANG_EN: "Credit Risk"
    },
    "gauge_pd": {
        LANG_VI: "Xác Suất Vỡ Nợ (PD)",
        LANG_EN: "Default Probability (PD)"
    },
    "ratios_comparison_title": {
        LANG_VI: "So Sánh Chỉ Số Chính",
        LANG_EN: "Key Ratios Comparison"
    },
    "risk_assessment_title": {
        LANG_VI: "Đánh Giá Rủi Ro Chi Tiết (Detailed Risk Assessment)",
        LANG_EN: "Detailed Risk Assessment"
    },
    "risk_score_overall": {
        LANG_VI: "Điểm Rủi Ro Tổng Thể",
        LANG_EN: "Overall Risk Score"
    },
    "risk_pd": {
        LANG_VI: "Xác Suất Vỡ Nợ (PD)",
        LANG_EN: "Default Probability (PD)"
    },
    "risk_credit_rating": {
        LANG_VI: "Hạng Tín Dụng Dự Kiến",
        LANG_EN: "Projected Credit Rating"
    },
    "risk_categories_title": {
        LANG_VI: "Phân Loại Rủi Ro",
        LANG_EN: "Risk Categories"
    },
    "risk_radar_title": {
        LANG_VI: "Bản Đồ Rủi Ro (Risk Radar)",
        LANG_EN: "Risk Radar"
    },
    "risk_factors_title": {
        LANG_VI: "Các Yếu Tố Rủi Ro Cụ Thể",
        LANG_EN: "Specific Risk Factors"
    },
    "risk_high": {
        LANG_VI: "Rủi Ro Cao:",
        LANG_EN: "High Risk Factors:"
    },
    "risk_medium": {
        LANG_VI: "Rủi Ro Trung Bình:",
        LANG_EN: "Medium Risk Factors:"
    },
    "risk_mitigation_title": {
        LANG_VI: "Các Biện Pháp Giảm Thiểu Rủi Ro",
        LANG_EN: "Risk Mitigation Measures"
    },
    "model_details_title": {
        LANG_VI: "Chi Tiết Mô Hình (Model Details)",
        LANG_EN: "Model Details"
    },
    "model_info_title": {
        LANG_VI: "Thông Tin Mô Hình",
        LANG_EN: "Model Information"
    },
    "model_features_title": {
        LANG_VI: "Các Đặc Trưng Quan Trọng Nhất (Top Features)",
        LANG_EN: "Most Important Features (Top Features)"
    },
    "chart_feature_importance_title": {
        LANG_VI: "Tầm Quan Trọng Của Các Đặc Trưng",
        LANG_EN: "Feature Importance"
    },
    "model_prediction_details": {
        LANG_VI: "Chi Tiết Dự Báo",
        LANG_EN: "Prediction Details"
    },
    "model_prediction_confidence": {
        LANG_VI: "Độ Tin Cậy",
        LANG_EN: "Confidence"
    },
    "model_prediction_risk_class": {
        LANG_VI: "Phân Loại Rủi Ro",
        LANG_EN: "Risk Classification"
    },
    "model_prediction_credit_rating": {
        LANG_VI: "Hạng Tín Dụng",
        LANG_EN: "Credit Rating"
    },
    "model_explanation_title": {
        LANG_VI: "Giải Thích Dự Báo (SHAP Values)",
        LANG_EN: "Prediction Explanation (SHAP Values)"
    },
    "model_explanation_push_up": {
        LANG_VI: "Tăng Rủi Ro (Push Up):",
        LANG_EN: "Risk Increasing Factors (Push Up):"
    },
    "model_explanation_push_down": {
        LANG_VI: "Giảm Rủi Ro (Push Down):",
        LANG_EN: "Risk Decreasing Factors (Push Down):"
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
    return get_text(key, get_current_lang())
