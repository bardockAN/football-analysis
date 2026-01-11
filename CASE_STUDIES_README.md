# Football Analysis - Advanced Case Studies & Analytics

## 🎯 Tổng Quan

Hệ thống phân tích bóng đá tiên tiến với **3 Case Studies chuyên sâu**, **Dashboard visualization**, **Export dữ liệu** và **Báo cáo tự động**.

## ✨ Tính Năng Mới

### 📊 Case Study 1: So Sánh Hiệu Suất 2 Đội
- Phân tích chi tiết thống kê của cả 2 đội
- So sánh: Ball touches, Possession %, Distance, Speed
- Biểu đồ thanh so sánh trực quan
- Export dữ liệu chi tiết

**Output:** `case_study_1_team_comparison.png`

### 🏆 Case Study 2: Phân Tích Cầu Thủ Xuất Sắc Nhất (MVP)
- Tính điểm MVP dựa trên 4 chỉ số:
  - Ball Touches (30%)
  - Possession (25%)
  - Distance (25%)
  - Speed (20%)
- MVP Card với thông tin chi tiết
- Top 5 Players Ranking
- Radar chart performance

**Output:** 
- `case_study_2_mvp_card.png`
- `case_study_2_top5_ranking.png`

### ⚡ Case Study 3: Phân Tích Chiến Thuật & Passing Network
- Phát hiện đội hình (4-4-2, 4-3-3, v.v.)
- Visualize mạng lưới chuyền bóng
- Phân tích vị trí trung bình cầu thủ
- Tactical positioning map

**Output:**
- `case_study_3_passing_network.png`
- `case_study_3_formations.png`

### 📁 Data Export Module
Export dữ liệu ra nhiều định dạng:
- **JSON**: Comprehensive data với metadata
- **CSV**: Dữ liệu dạng bảng dễ phân tích
- **Player Stats**: Chi tiết từng cầu thủ
- **Team Comparison**: So sánh 2 đội
- **Passing Network**: Mạng lưới chuyền bóng
- **MVP Rankings**: Bảng xếp hạng

**Output Folder:** `output_videos/analytics/`

### 📈 Dashboard Visualization
Dashboard tổng hợp với 9 charts:
1. Team Performance Comparison (Bar Chart)
2. Player Distance Covered (Horizontal Bar)
3. Ball Possession Distribution (Pie Chart)
4. Speed Distribution by Team (Histogram)
5. MVP Ranking (Bar Chart)
6. Ball Touches Comparison (Bar Chart)
7. Team Statistics Table
8. Top 5 Players Table
9. MVP Performance Radar Chart

**Output:** `analytics/dashboard_full.png`

### 📄 Automated Reports
Báo cáo tự động với HTML/PDF:
- **HTML Report**: Báo cáo đầy đủ với styling chuyên nghiệp
- **PDF Report**: Export từ HTML (yêu cầu weasyprint)
- Bao gồm tất cả charts, tables và analysis
- Responsive design, in ấn được

**Output:**
- `analytics/report_YYYYMMDD_HHMMSS.html`
- `analytics/report_YYYYMMDD_HHMMSS.pdf` (optional)

## 🚀 Cài Đặt

### 1. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

### 2. (Optional) Cài đặt WeasyPrint cho PDF generation:

**Windows:**
```bash
# Cài GTK3 runtime trước
# Download từ: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases

pip install weasyprint
```

**Linux/Mac:**
```bash
pip install weasyprint
```

## 📝 Cách Sử Dụng

### Chạy phân tích đầy đủ:

```bash
python main.py
```

Chương trình sẽ tự động:
1. ✅ Phân tích video
2. ✅ Tạo 3 case studies
3. ✅ Export dữ liệu (JSON, CSV)
4. ✅ Tạo dashboard
5. ✅ Tạo báo cáo HTML/PDF

### Output Structure:

```
output_videos/
├── output_video.avi                          # Video đã phân tích
├── player_stats.csv                          # Stats cơ bản
├── player_stats_table.png                    # Bảng stats
├── case_study_1_team_comparison.png          # Case Study 1
├── case_study_2_mvp_card.png                 # Case Study 2 - MVP Card
├── case_study_2_top5_ranking.png             # Case Study 2 - Rankings
├── case_study_3_passing_network.png          # Case Study 3 - Passing
├── case_study_3_formations.png               # Case Study 3 - Formations
└── analytics/
    ├── player_stats_TIMESTAMP.json           # Player data (JSON)
    ├── player_stats_TIMESTAMP.csv            # Player data (CSV)
    ├── team_comparison_TIMESTAMP.json        # Team comparison (JSON)
    ├── team_comparison_TIMESTAMP.csv         # Team comparison (CSV)
    ├── mvp_analysis_TIMESTAMP.json           # MVP data (JSON)
    ├── tactical_analysis_TIMESTAMP.json      # Tactical data (JSON)
    ├── passing_network_TIMESTAMP.csv         # Passing network (CSV)
    ├── comprehensive_analysis_TIMESTAMP.json # Tất cả dữ liệu
    ├── export_summary.txt                    # Summary của exports
    ├── dashboard_full.png                    # Dashboard tổng hợp
    ├── chart_team_comparison.png             # Chart riêng lẻ
    ├── chart_player_distances.png            # Chart riêng lẻ
    ├── chart_mvp_ranking.png                 # Chart riêng lẻ
    ├── report_TIMESTAMP.html                 # HTML Report
    └── report_TIMESTAMP.pdf                  # PDF Report (optional)
```

## 🔧 Cấu Trúc Code Mới

```
football_analysis/
├── case_studies/                  # Module Case Studies
│   ├── __init__.py
│   ├── team_comparison.py         # Case Study 1
│   ├── mvp_analysis.py            # Case Study 2
│   └── tactical_analysis.py       # Case Study 3
│
├── analytics/                     # Module Analytics
│   ├── __init__.py
│   ├── data_exporter.py           # Export JSON/CSV
│   ├── dashboard_generator.py     # Matplotlib charts
│   └── report_generator.py        # HTML/PDF reports
│
└── main.py                        # Main script (đã cập nhật)
```

## 📊 API Documentation

### Case Study 1: TeamComparisonAnalyzer

```python
from case_studies import TeamComparisonAnalyzer

analyzer = TeamComparisonAnalyzer()
team_stats = analyzer.analyze_teams(tracks, team_ball_control)

# Tạo biểu đồ so sánh
chart = analyzer.create_comparison_chart(width=1200, height=800)
cv2.imwrite('team_comparison.png', chart)

# Export data
data = analyzer.export_to_dict()
```

### Case Study 2: MVPAnalyzer

```python
from case_studies import MVPAnalyzer

analyzer = MVPAnalyzer()
result = analyzer.analyze_mvp(player_stats, tracks)

print(f"MVP: Player {result['mvp']['player_id']}")
print(f"MVP Score: {result['mvp']['mvp_score']:.1f}/100")

# Tạo MVP card
card = analyzer.create_mvp_card(width=800, height=1000)
cv2.imwrite('mvp_card.png', card)

# Tạo ranking
ranking = analyzer.create_top5_ranking(width=1000, height=700)
cv2.imwrite('top5.png', ranking)
```

### Case Study 3: TacticalAnalyzer

```python
from case_studies import TacticalAnalyzer

analyzer = TacticalAnalyzer()
result = analyzer.analyze_tactics(tracks, team_ball_control)

# Passing network
passing_viz = analyzer.create_passing_network_viz(width=1400, height=900)
cv2.imwrite('passing_network.png', passing_viz)

# Formations
formation_viz = analyzer.create_formation_viz(width=1200, height=800)
cv2.imwrite('formations.png', formation_viz)

print(f"Team 1 Formation: {result['formations'][1]['formation']}")
print(f"Team 2 Formation: {result['formations'][2]['formation']}")
```

### Data Export

```python
from analytics import DataExporter

exporter = DataExporter(output_dir='output_videos/analytics')
exported_files = exporter.export_all_data(
    player_stats,
    team_comparison,
    mvp_analysis,
    tactical_analysis
)

# Tạo summary
exporter.create_export_summary(exported_files)
```

### Dashboard Generation

```python
from analytics import DashboardGenerator

dashboard = DashboardGenerator(output_dir='output_videos/analytics')

# Full dashboard
dashboard_path = dashboard.create_full_dashboard(
    player_stats,
    team_comparison,
    mvp_analysis
)

# Individual charts
charts = dashboard.create_individual_charts(
    player_stats,
    team_comparison,
    mvp_analysis
)
```

### Report Generation

```python
from analytics import ReportGenerator

report = ReportGenerator(output_dir='output_videos/analytics')

# HTML Report
html_path = report.generate_html_report(
    player_stats,
    team_comparison,
    mvp_analysis,
    tactical_analysis,
    charts_paths=charts_dict,
    images_paths=images_dict
)

# PDF Report (optional)
pdf_path = report.generate_pdf_report(html_path)
```

## 🎨 Customization

### Thay đổi màu sắc đội:

Trong `team_assigner/team_assigner.py`, điều chỉnh `team_colors`.

### Thay đổi trọng số MVP:

Trong `case_studies/mvp_analysis.py`, phương thức `_calculate_mvp_score()`:

```python
mvp_score = (
    touches_score * 0.30 +   # Thay đổi weight
    poss_score * 0.25 +
    distance_score * 0.25 +
    speed_score * 0.20
)
```

### Thay đổi style dashboard:

Trong `analytics/dashboard_generator.py`:

```python
plt.style.use('seaborn-v0_8-darkgrid')  # Thay đổi style
```

## 🐛 Troubleshooting

### Lỗi: WeasyPrint not found
```
pip install weasyprint
```
Hoặc bỏ qua PDF generation (chỉ dùng HTML)

### Lỗi: matplotlib backend
```python
import matplotlib
matplotlib.use('Agg')  # Đã được set trong code
```

### Lỗi: No module named 'case_studies'
Đảm bảo chạy từ thư mục gốc:
```bash
cd football_analysis
python main.py
```

## 📈 Performance

- **Video Processing**: ~30-60 giây/100 frames
- **Case Studies**: ~5-10 giây
- **Dashboard Generation**: ~3-5 giây
- **Report Generation**: ~2-3 giây (HTML), ~5-10 giây (PDF)

## 🤝 Contributing

Đóng góp ý tưởng hoặc cải tiến:
1. Fork repository
2. Tạo branch mới
3. Commit changes
4. Push và tạo Pull Request

## 📞 Support

Nếu có vấn đề, tạo issue trên GitHub hoặc liên hệ.

## 📜 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

---

**Made with ❤️ for Football Analytics**
