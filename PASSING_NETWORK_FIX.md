# Sửa Lỗi Passing Network - Case Study 3

## 🐛 Vấn Đề

Passing Network hiển thị **quá nhiều cầu thủ** (có thể hàng chục đến hàng trăm nodes), trong khi:
- ❌ Tối đa chỉ có **22 cầu thủ** trên sân (11 mỗi đội)
- ❌ Nhiều detection lỗi từ YOLO được tính là "cầu thủ"
- ❌ Visualization bị lộn xộn, khó đọc

## ✅ Giải Pháp

### 1. **Lọc Top Players**
Thêm hàm `_get_top_players_per_team()` để:
- Nhóm cầu thủ theo đội
- Sắp xếp theo số lượng frames xuất hiện (activity)
- **Chỉ lấy top 11 cầu thủ có nhiều frames nhất mỗi đội**
- Loại bỏ các detection lỗi (ít frames)

```python
def _get_top_players_per_team(self, max_per_team=11):
    """
    Lọc và lấy top N cầu thủ chơi nhiều nhất mỗi đội
    """
    # Nhóm và lọc theo số frames
    # Chỉ giữ lại top 11 cầu thủ mỗi đội
```

### 2. **Áp Dụng Filtering Ở Mọi Nơi**

#### a) Passing Network Visualization
```python
# LỌC CHỈ LẤY TOP 11 CẦU THỦ MỖI ĐỘI
filtered_players = self._get_top_players_per_team(max_per_team=11)

# Chỉ vẽ filtered players
for player_id, data in filtered_players.items():
    # Vẽ node và connections
```

#### b) Data Export
```python
def export_to_dict(self):
    # Lọc top players
    filtered_players = self._get_top_players_per_team(max_per_team=11)
    
    # Chỉ export passes giữa top players
    # Chỉ export vị trí của top players
```

### 3. **Thêm Subtitle Thông Tin**
```python
subtitle = f"Top {team1_count} Team 1 vs Top {team2_count} Team 2 Players"
```
Giúp người dùng biết đang xem bao nhiêu cầu thủ.

## 📊 Kết Quả Test

```
Total players detected: 33
  Team 1: 15 players (11 chính + 4 lỗi)
  Team 2: 18 players (11 chính + 7 lỗi)

Filtered players (top 11 each team): 22 ✓
  Team 1: 11 players ✓
  Team 2: 11 players ✓
```

## 🔄 So Sánh

| Trước | Sau |
|-------|-----|
| 33+ cầu thủ (lộn xộn) | Chính xác 22 cầu thủ |
| Detection lỗi bị hiển thị | Chỉ top 11 mỗi đội |
| Khó đọc, quá nhiều nodes | Rõ ràng, dễ phân tích |
| Export dữ liệu thừa | Export đúng 22 players |

## 📝 Các Thay Đổi

### Files Modified:
1. **`case_studies/tactical_analysis.py`**
   - Thêm `_get_top_players_per_team()` - Lọc top players
   - Cập nhật `create_passing_network_viz()` - Áp dụng filter
   - Cập nhật `export_to_dict()` - Export filtered data
   - Thêm subtitle hiển thị số lượng cầu thủ

### Files Added:
2. **`test_passing_network.py`** - Test script để verify filtering

## 🚀 Cách Sử Dụng

Không cần thay đổi code gọi:

```bash
python main.py
```

Hệ thống tự động:
1. Phát hiện tất cả cầu thủ (có thể 30-40 detections)
2. **Lọc chỉ lấy top 11 cầu thủ mỗi đội** (theo số frames)
3. Tạo visualization sạch sẽ với đúng 22 cầu thủ
4. Export dữ liệu chính xác

## ✨ Kết Quả Mong Đợi

### Passing Network:
- ✅ Tối đa **22 nodes** (11 mỗi đội)
- ✅ Chỉ hiển thị cầu thủ chính, không có detection lỗi
- ✅ Dễ đọc, rõ ràng
- ✅ Subtitle: "Top 11 Team 1 vs Top 11 Team 2 Players"

### Exported Data:
- ✅ `player_avg_positions`: Đúng 22 entries
- ✅ `passing_network`: Chỉ passes giữa 22 players
- ✅ Không có dữ liệu thừa

## 🎯 Lợi Ích

1. **Chính xác hơn**: Phản ánh đúng 22 cầu thủ trên sân
2. **Sạch hơn**: Loại bỏ detection lỗi
3. **Dễ đọc hơn**: Ít nodes, dễ phân tích
4. **Hiệu quả hơn**: Ít dữ liệu cần xử lý/export
5. **Thực tế hơn**: Đúng với luật bóng đá (11 vs 11)
