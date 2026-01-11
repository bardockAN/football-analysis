# 🚀 QUICK START GUIDE - FOOTBALL ANALYSIS

## Bước 1: Kiểm tra môi trường

```powershell
# Kích hoạt môi trường ảo
cd D:\Footbal_analysis
& .\.venv\Scripts\Activate.ps1

# Di chuyển vào thư mục project
cd football_analysis
```

## Bước 2: Cài đặt thư viện mới (nếu chưa có)

```powershell
pip install seaborn weasyprint pillow
```

**Lưu ý:** Nếu `weasyprint` báo lỗi trên Windows, có thể bỏ qua (PDF generation sẽ không hoạt động nhưng HTML vẫn OK)

## Bước 3: Test các module mới

```powershell
python test_modules.py
```

Bạn sẽ thấy:
```
✓ All imports successful!
✓ TeamComparisonAnalyzer initialized
✓ MVPAnalyzer initialized
✓ TacticalAnalyzer initialized
✓ DataExporter initialized
✓ DashboardGenerator initialized
✓ ReportGenerator initialized

✅ ALL TESTS PASSED!
```

## Bước 4: Chạy phân tích đầy đủ

```powershell
python main.py
```

## Kết quả bạn sẽ nhận được:

### 📊 Case Studies (3 files PNG)
1. **case_study_1_team_comparison.png** - So sánh 2 đội
2. **case_study_2_mvp_card.png** - Thẻ MVP
3. **case_study_3_passing_network.png** - Mạng lưới chuyền bóng

### 📁 Data Export (Folder: analytics/)
- **JSON files**: Dữ liệu chi tiết
- **CSV files**: Dữ liệu dạng bảng
- **comprehensive_analysis.json**: Tất cả dữ liệu

### 📈 Dashboard
- **dashboard_full.png**: Dashboard 9 charts

### 📄 Reports
- **report_TIMESTAMP.html**: Báo cáo HTML đẹp
- **report_TIMESTAMP.pdf**: Báo cáo PDF (nếu có weasyprint)

## Xem kết quả:

```powershell
# Mở thư mục output
explorer output_videos

# Mở thư mục analytics
explorer output_videos\analytics
```

## Tips:

### Nếu muốn chỉ xem case studies nhanh:
Sau khi chạy xong, mở các file PNG trong `output_videos/`

### Nếu muốn xem báo cáo đẹp:
Mở file `output_videos/analytics/report_*.html` trong browser

### Nếu muốn phân tích dữ liệu:
Mở các file CSV trong `output_videos/analytics/` bằng Excel

## Troubleshooting:

### Lỗi import module:
```powershell
# Đảm bảo đang ở đúng thư mục
cd D:\Footbal_analysis\football_analysis
python test_modules.py
```

### Lỗi matplotlib:
```powershell
pip install --upgrade matplotlib seaborn
```

### Lỗi weasyprint (Windows):
Bỏ qua, chỉ cần HTML report là đủ. Hoặc:
1. Download GTK3: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases
2. Cài đặt GTK3
3. `pip install weasyprint`

## Thời gian chạy:

- Video analysis: ~30-60s
- Case studies: ~5-10s
- Dashboard: ~3-5s
- Reports: ~2-3s

**Tổng: ~1-2 phút**

## Kết quả mẫu:

Sau khi chạy xong, bạn sẽ thấy output như:

```
================================================================================
HOÀN TẤT PHÂN TÍCH!
================================================================================

📊 Case Studies:
   - Team Comparison: output_videos/case_study_1_team_comparison.png
   - MVP Analysis: output_videos/case_study_2_mvp_card.png
   - Tactical Analysis: output_videos/case_study_3_passing_network.png

📁 Data Export:
   - Folder: output_videos/analytics/
   - JSON, CSV files với dữ liệu chi tiết

📈 Dashboard:
   - Full Dashboard: output_videos/analytics/dashboard_full.png

📄 Reports:
   - HTML Report: output_videos/analytics/report_20260101_123456.html
   - PDF Report: output_videos/analytics/report_20260101_123456.pdf

================================================================================
```

---

**Chúc bạn phân tích thành công! ⚽🎉**
