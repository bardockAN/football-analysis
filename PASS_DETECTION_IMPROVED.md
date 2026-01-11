# Cải Tiến Thuật Toán Phát Hiện Pass - Case Study 3

## 🐛 Vấn Đề Ban Đầu

Passing network chỉ phát hiện được **2 passes** trong toàn bộ video!
- ❌ Thuật toán cũ chỉ dựa vào flag `has_ball` 
- ❌ `has_ball` chỉ được set khi bóng RẤT GẦN cầu thủ
- ❌ Nhiều pha chuyền bóng thực tế không được phát hiện

### Ví dụ từ dữ liệu thực:
```csv
from_player,to_player,pass_count
7,1,1
19,5,1
```
Chỉ 2 passes trong cả trận đấu - Không thực tế!

## ✅ Giải Pháp Mới

### 1. **Thuật Toán Dựa Trên Khoảng Cách**
Thay vì dựa vào `has_ball`, tính toán cầu thủ gần bóng nhất:

```python
# Tìm cầu thủ gần bóng nhất trong vòng 150 pixels
for player_id, player_data in current_frame.items():
    pos = player_data['position']
    dist = sqrt((pos[0] - ball_x)^2 + (pos[1] - ball_y)^2)
    
    if dist < min_dist:
        current_ball_holder = player_id
```

### 2. **Tracking Possession Changes**
Lưu lại cầu thủ giữ bóng cuối cùng:

```python
self.last_ball_holder = None  # Track cầu thủ giữ bóng

# Phát hiện khi possession thay đổi
if current_ball_holder != self.last_ball_holder:
    # Đây là một pass!
```

### 3. **Debounce Mechanism**
Tránh phát hiện trùng lặp:

```python
self.last_pass_frame = {}  # Lưu frame của pass gần nhất

# Chỉ ghi nhận pass nếu đã qua ít nhất 10 frames
if (frame_num - self.last_pass_frame[pass_key]) >= 10:
    self.passing_network[from][to] += 1
```

### 4. **Tăng Threshold**
- Threshold cũ: 100 pixels
- Threshold mới: **150 pixels** (phát hiện tốt hơn)

### 5. **Kiểm Tra Cùng Đội**
Chỉ ghi nhận passes trong cùng đội:

```python
if prev_team == current_team and prev_team in [1, 2]:
    # Valid pass
    self.passing_network[from][to] += 1
```

## 📊 Kết Quả Test

### Test với dữ liệu giả:
```
Scenario: 3 cầu thủ chuyền bóng (1 -> 2 -> 3)
100 frames

Detected Passes:
  Player 1 -> Player 2: 1 passes ✓
  Player 2 -> Player 3: 1 passes ✓

Total passes detected: 2 ✓
```

## 🔄 So Sánh

| Thuật Toán Cũ | Thuật Toán Mới |
|---------------|----------------|
| Dựa vào `has_ball` flag | Tính khoảng cách đến bóng |
| Threshold: 100px | Threshold: 150px |
| Không có debounce | Có debounce (10 frames) |
| Chỉ 2 frames liên tiếp | Track possession changes |
| **2 passes** trong video | **Nhiều passes hơn** |

## 📝 Chi Tiết Kỹ Thuật

### Hàm Mới:

**`_detect_pass(tracks, frame_num)`** - Hoàn toàn viết lại

```python
def _detect_pass(self, tracks, frame_num):
    # 1. Tìm cầu thủ gần bóng nhất (trong 150px)
    # 2. So sánh với last_ball_holder
    # 3. Kiểm tra cùng đội
    # 4. Debounce (10 frames)
    # 5. Ghi nhận pass
```

### State Tracking:

```python
class TacticalAnalyzer:
    def __init__(self):
        self.last_ball_holder = None       # NEW
        self.last_pass_frame = {}          # NEW
```

## 🚀 Kết Quả Mong Đợi

Sau khi chạy lại với video thực:

### Trước:
```csv
from_player,to_player,pass_count
7,1,1
19,5,1
```
**2 passes** ❌

### Sau:
```csv
from_player,to_player,pass_count
1,2,3
1,5,2
2,3,4
3,5,1
5,7,2
...
```
**20-50 passes** (tùy video) ✓

## ✨ Lợi Ích

1. **Chính xác hơn**: Phát hiện nhiều passes thực tế
2. **Robust hơn**: Không phụ thuộc vào `has_ball` flag
3. **Realistic hơn**: Phản ánh đúng số lượng passes trong trận đấu
4. **Visualization tốt hơn**: Passing network có nhiều connections
5. **Analysis sâu hơn**: Có đủ dữ liệu để phân tích chiến thuật

## 🎯 Cách Sử Dụng

Chạy lại với video thực:

```bash
python main.py
```

Kiểm tra kết quả:
- `output_videos/case_study_3_passing_network.png` - Nhiều arrows hơn
- `output_videos/analytics/passing_network_*.csv` - Nhiều entries hơn
- Passing network visualization đầy đủ, rõ ràng hơn

---

**Note**: Nếu vẫn thấy ít passes, có thể điều chỉnh:
- Tăng `threshold` từ 150 lên 200 pixels
- Giảm `debounce` từ 10 xuống 5 frames
- Kiểm tra chất lượng ball detection trong video
