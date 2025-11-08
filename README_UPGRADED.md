# Corporate Default Risk Scoring - Phiên Bản Nâng Cấp

Ứng dụng Streamlit nâng cấp để phân tích rủi ro vỡ nợ của các công ty với ba chức năng chính:

## 🎯 Chức Năng Chính

### 1. 📊 Finance (Phân Tích Tài Chính)
Hiển thị các báo cáo tài chính chi tiết:
- **Báo Cáo Thu Nhập (Income Statement)**: Doanh thu, chi phí, lợi nhuận
- **Bảng Cân Đối Kế Toán (Balance Sheet)**: Tài sản, nợ, vốn chủ sở hữu
- **Báo Cáo Lưu Chuyển Tiền Mặt (Cash Flow)**: Lưu chuyển từ hoạt động, đầu tư, tài chính
- **Chỉ Số Tài Chính (Financial Indicators)**: ROA, ROE, tỷ lệ nợ, thanh khoản, v.v.
- **Ghi Chú & Phân Tích (Notes)**: Tóm tắt hoạt động, phân tích kết quả, rủi ro, dự báo

### 2. 📰 Sentiment (Phân Tích Tình Cảm)
Phân tích tình cảm thị trường và tin tức:
- **Tin Tức Gần Đây**: Danh sách tin tức với điểm tình cảm
- **Phân Tích Tình Cảm**: Tình cảm theo danh mục, các yếu tố chính
- **Đánh Giá Chung**: Đánh giá tổng thể tình hình cổ phiếu, rủi ro, khuyến nghị

### 3. 📈 Summary (Tóm Tắt & Đánh Giá Rủi Ro)
Dashboard tóm tắt với đánh giá rủi ro chi tiết:
- **Dashboard Tóm Tắt**: Các chỉ số chính, xu hướng, so sánh với ngành
- **Đánh Giá Rủi Ro**: Phân loại rủi ro, bản đồ rủi ro, các yếu tố cụ thể, biện pháp giảm thiểu
- **Chi Tiết Mô Hình**: Thông tin mô hình, đặc trưng quan trọng, giải thích dự báo

## 🚀 Cài Đặt & Chạy Ứng Dụng

### Yêu Cầu
- Python 3.8+
- Streamlit
- Pandas, NumPy, Plotly
- LightGBM, scikit-learn, SHAP

### Cài Đặt Thư Viện
```bash
pip install -r requirements.txt
```

### Chạy Ứng Dụng
```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại `http://localhost:8501`

## 📁 Cấu Trúc Dự Án

```
.
├── app.py                    # File chính của ứng dụng
├── requirements.txt          # Danh sách thư viện cần cài đặt
├── bctc_final.csv           # Dữ liệu tài chính
├── models/                  # Thư mục chứa mô hình
│   ├── lgbm_model.pkl       # Mô hình LightGBM
│   ├── threshold.json       # Ngưỡng phân loại
│   └── train_reference.parquet  # Dữ liệu tham chiếu
├── tabs/                    # Các module chức năng chính
│   ├── __init__.py
│   ├── financial.py         # Chức năng Finance
│   ├── sentiment.py         # Chức năng Sentiment
│   └── summary.py           # Chức năng Summary
├── financial_subtabs/       # (Dành cho mở rộng) Các tab con tài chính
├── utils_new/               # Các hàm tiện ích
│   ├── data_cleaning.py
│   ├── feature_engineering.py
│   ├── feature_selection.py
│   ├── model_scoring.py
│   ├── policy.py
│   ├── drift_monitoring.py
│   ├── stress_testing.py
│   └── visualization.py
└── README_UPGRADED.md       # File này
```

## 🎮 Hướng Dẫn Sử Dụng

### 1. Lựa Chọn Ticker & Năm
- Sử dụng sidebar bên trái để chọn mã cổ phiếu (Ticker)
- Chọn năm muốn xem dữ liệu

### 2. Chọn Loại Báo Cáo
Nhấp vào một trong ba nút bấm:
- **📊 Finance**: Xem báo cáo tài chính chi tiết
- **📰 Sentiment**: Xem phân tích tình cảm tin tức
- **📈 Summary**: Xem tóm tắt và đánh giá rủi ro

### 3. Tương Tác Với Biểu Đồ
- Hover chuột để xem chi tiết
- Click vào legend để ẩn/hiện dữ liệu
- Sử dụng toolbar Plotly để zoom, pan, lưu ảnh

## 📊 Dữ Liệu Mẫu

Ứng dụng hiện tại sử dụng **dữ liệu mẫu (sample data)** cho các chức năng Finance, Sentiment, và Summary. 

### Để Cập Nhật Dữ Liệu Thực Tế:

1. **Finance**: Chỉnh sửa dữ liệu trong `tabs/financial.py`:
   - Cập nhật `income_data`, `assets_data`, `liabilities_data`, `cashflow_data`
   - Hoặc lấy dữ liệu từ `raw_df` và `row_raw`

2. **Sentiment**: Chỉnh sửa dữ liệu trong `tabs/sentiment.py`:
   - Cập nhật `news_data` với tin tức thực tế
   - Tích hợp API tin tức (VNExpress, Cafef, v.v.)

3. **Summary**: Chỉnh sửa dữ liệu trong `tabs/summary.py`:
   - Cập nhật các chỉ số rủi ro dựa trên mô hình thực tế
   - Tích hợp kết quả từ mô hình LightGBM

## 🔧 Tùy Chỉnh & Mở Rộng

### Thêm Dữ Liệu Mới
1. Cập nhật `bctc_final.csv` với dữ liệu mới
2. Chạy lại ứng dụng (Streamlit sẽ reload tự động)

### Tùy Chỉnh Giao Diện
- Chỉnh sửa CSS trong phần `inject_global_css()` của `app.py`
- Thay đổi màu sắc, font chữ, layout

### Thêm Chức Năng Mới
1. Tạo file mới trong thư mục `tabs/` (ví dụ: `tabs/new_feature.py`)
2. Thêm hàm `render()` với tham số phù hợp
3. Import trong `app.py` và thêm nút bấm + logic điều hướng

## 📝 Ghi Chú Quan Trọng

- **Dữ Liệu Mẫu**: Tất cả dữ liệu hiện tại là mẫu. Bạn cần cập nhật với dữ liệu thực tế
- **Mô Hình**: Mô hình LightGBM được tải từ `models/lgbm_model.pkl`
- **Ngôn Ngữ**: Ứng dụng sử dụng tiếng Việt
- **Responsive**: Giao diện tối ưu cho desktop và tablet

## 🐛 Khắc Phục Sự Cố

### Lỗi: "ModuleNotFoundError: No module named 'streamlit'"
```bash
pip install streamlit
```

### Lỗi: "FileNotFoundError: bctc_final.csv not found"
- Đảm bảo file `bctc_final.csv` nằm trong thư mục gốc

### Lỗi: "No record for selected Ticker & Year"
- Kiểm tra dữ liệu trong `bctc_final.csv` có chứa Ticker & Year đó không

## 📞 Hỗ Trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra console của Streamlit (terminal nơi chạy `streamlit run app.py`)
2. Xem thông báo lỗi chi tiết
3. Kiểm tra dữ liệu đầu vào

## 📄 Giấy Phép

Dự án này được phát triển cho mục đích phân tích rủi ro tín dụng.

---

**Phiên Bản:** 2.0 (Nâng Cấp)  
**Ngày Cập Nhật:** 2024-11-08
