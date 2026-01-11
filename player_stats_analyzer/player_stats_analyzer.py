import sys
import cv2
import numpy as np
sys.path.append('../')

class PlayerStatsAnalyzer():
    """
    Lớp để phân tích và thống kê các chỉ số của cầu thủ bao gồm:
    - Số lần chạm bóng (ball touches)
    - Thời gian giữ bóng (possession time)
    - Tỉ lệ giữ bóng (possession percentage)
    - Quãng đường di chuyển (distance covered)
    - Tốc độ trung bình (average speed)
    """
    
    def __init__(self):
        self.player_stats = {}  # Dictionary lưu thống kê của từng cầu thủ
        
    def calculate_player_stats(self, tracks, team_ball_control, selected_player_ids=None):
        """
        Tính toán các chỉ số thống kê cho các cầu thủ
        
        Args:
            tracks: Dictionary chứa dữ liệu tracking của players, ball
            team_ball_control: Array chứa thông tin đội nào kiểm soát bóng ở mỗi frame
            selected_player_ids: List các player_id cần thống kê (nếu None thì thống kê tất cả)
        """
        # Khởi tạo dictionary lưu stats
        self.player_stats = {}
        
        # Lấy tổng số frame
        total_frames = len(tracks['players'])
        
        # Lặp qua từng frame để thu thập dữ liệu
        for frame_num in range(total_frames):
            player_frame = tracks['players'][frame_num]
            
            for player_id, player_data in player_frame.items():
                # Nếu có danh sách player_id được chọn, chỉ xử lý những player đó
                if selected_player_ids is not None and player_id not in selected_player_ids:
                    continue
                
                # Khởi tạo stats cho player nếu chưa có
                if player_id not in self.player_stats:
                    self.player_stats[player_id] = {
                        'player_id': player_id,
                        'team': player_data.get('team', 0),
                        'team_color': player_data.get('team_color', (0, 0, 0)),
                        'ball_touches': 0,  # Số lần chạm bóng
                        'possession_frames': 0,  # Số frame giữ bóng
                        'total_distance': 0,  # Tổng quãng đường (meters)
                        'total_speed': 0,  # Tổng tốc độ để tính trung bình
                        'speed_count': 0,  # Số lần có dữ liệu tốc độ
                        'frames_tracked': 0,  # Số frame được track
                    }
                
                # Đếm số frame được track
                self.player_stats[player_id]['frames_tracked'] += 1
                
                # Kiểm tra player có bóng không
                has_ball = player_data.get('has_ball', False)
                if has_ball:
                    # Kiểm tra xem đây có phải lần đầu chạm bóng không (frame trước không có bóng)
                    if frame_num > 0:
                        prev_frame = tracks['players'][frame_num - 1]
                        if player_id in prev_frame:
                            prev_has_ball = prev_frame[player_id].get('has_ball', False)
                            if not prev_has_ball:  # Chuyển từ không có bóng sang có bóng
                                self.player_stats[player_id]['ball_touches'] += 1
                    else:  # Frame đầu tiên
                        self.player_stats[player_id]['ball_touches'] += 1
                    
                    # Đếm frame giữ bóng
                    self.player_stats[player_id]['possession_frames'] += 1
                
                # Tính quãng đường di chuyển
                if 'distance' in player_data:
                    distance = player_data['distance']
                    if distance is not None:
                        self.player_stats[player_id]['total_distance'] += distance
                
                # Tính tốc độ trung bình
                if 'speed' in player_data:
                    speed = player_data['speed']
                    if speed is not None:
                        self.player_stats[player_id]['total_speed'] += speed
                        self.player_stats[player_id]['speed_count'] += 1
        
        # Tính toán các chỉ số cuối cùng
        for player_id, stats in self.player_stats.items():
            # Tính tỉ lệ giữ bóng (%)
            if stats['frames_tracked'] > 0:
                stats['possession_percentage'] = (stats['possession_frames'] / stats['frames_tracked']) * 100
            else:
                stats['possession_percentage'] = 0
            
            # Tính tốc độ trung bình
            if stats['speed_count'] > 0:
                stats['average_speed'] = stats['total_speed'] / stats['speed_count']
            else:
                stats['average_speed'] = 0
        
        return self.player_stats
    
    def get_top_players(self, n=5, sort_by='total_distance'):
        """
        Lấy top N cầu thủ theo tiêu chí nào đó
        
        Args:
            n: Số lượng cầu thủ cần lấy
            sort_by: Tiêu chí sắp xếp ('total_distance', 'ball_touches', 'possession_percentage', 'average_speed')
        
        Returns:
            List các player_id của top N cầu thủ
        """
        if not self.player_stats:
            return []
        
        # Sắp xếp theo tiêu chí
        sorted_players = sorted(
            self.player_stats.items(),
            key=lambda x: x[1].get(sort_by, 0),
            reverse=True
        )
        
        # Lấy top N
        return [player_id for player_id, _ in sorted_players[:n]]
    
    def create_stats_table_image(self, width=800, height=600):
        """
        Tạo hình ảnh bảng thống kê
        
        Args:
            width: Chiều rộng của bảng
            height: Chiều cao của bảng
        
        Returns:
            Hình ảnh numpy array của bảng thống kê
        """
        # Tạo ảnh trắng
        table_img = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        if not self.player_stats:
            cv2.putText(table_img, "No player stats available", 
                       (width//4, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            return table_img
        
        # Tiêu đề
        title = "PLAYER STATISTICS SUMMARY"
        cv2.putText(table_img, title, (width//4, 40), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
        
        # Header của bảng
        headers = ["ID", "Team", "Touches", "Poss%", "Distance(m)", "Avg Speed(km/h)"]
        col_widths = [80, 100, 120, 120, 160, 220]
        
        y_offset = 80
        x_offset = 20
        
        # Vẽ header
        current_x = x_offset
        for i, header in enumerate(headers):
            cv2.putText(table_img, header, (current_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            current_x += col_widths[i]
        
        # Vẽ đường kẻ ngang dưới header
        cv2.line(table_img, (x_offset, y_offset + 10), 
                (width - x_offset, y_offset + 10), (0, 0, 0), 2)
        
        # Vẽ dữ liệu của từng player
        y_offset += 40
        row_height = 40
        
        for player_id, stats in sorted(self.player_stats.items()):
            current_x = x_offset
            
            # Player ID
            cv2.putText(table_img, str(player_id), (current_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            current_x += col_widths[0]
            
            # Team (vẽ ô màu thể hiện team)
            team = stats['team']
            team_color = stats['team_color']
            # Đổi từ RGB sang BGR cho OpenCV
            team_color_bgr = (int(team_color[2]), int(team_color[1]), int(team_color[0]))
            cv2.rectangle(table_img, 
                         (current_x, y_offset - 15), 
                         (current_x + 40, y_offset + 5),
                         team_color_bgr, -1)
            cv2.rectangle(table_img, 
                         (current_x, y_offset - 15), 
                         (current_x + 40, y_offset + 5),
                         (0, 0, 0), 1)
            current_x += col_widths[1]
            
            # Ball Touches
            cv2.putText(table_img, str(stats['ball_touches']), 
                       (current_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            current_x += col_widths[2]
            
            # Possession %
            poss_text = f"{stats['possession_percentage']:.1f}%"
            cv2.putText(table_img, poss_text, (current_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            current_x += col_widths[3]
            
            # Distance
            dist_text = f"{stats['total_distance']:.1f}"
            cv2.putText(table_img, dist_text, (current_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            current_x += col_widths[4]
            
            # Average Speed
            speed_text = f"{stats['average_speed']:.2f}"
            cv2.putText(table_img, speed_text, (current_x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            y_offset += row_height
            
            # Vẽ đường kẻ ngang
            cv2.line(table_img, (x_offset, y_offset - 20), 
                    (width - x_offset, y_offset - 20), (200, 200, 200), 1)
            
            # Nếu vượt quá chiều cao, dừng lại
            if y_offset > height - 50:
                break
        
        return table_img
    
    def draw_stats_on_frame(self, frame, position=(10, 500), max_players=5):
        """
        Vẽ bảng thống kê chuyên nghiệp lên góc frame
        
        Args:
            frame: Frame video cần vẽ
            position: Vị trí bắt đầu vẽ (x, y)
            max_players: Số lượng player tối đa hiển thị
        
        Returns:
            Frame đã được vẽ thống kê
        """
        if not self.player_stats:
            return frame
        
        x, y = position
        
        # Kích thước bảng
        table_width = 400
        row_height = 36
        header_height = 50
        title_height = 45
        padding = 15
        
        # Tính toán chiều cao tổng
        num_players = min(len(self.player_stats), max_players)
        table_height = title_height + header_height + (num_players * row_height) + padding * 4
        
        # Tạo overlay với gradient background
        overlay = frame.copy()
        
        # Vẽ shadow (hiệu ứng đổ bóng)
        shadow_offset = 4
        cv2.rectangle(overlay, 
                     (x + shadow_offset, y + shadow_offset), 
                     (x + table_width + shadow_offset, y + table_height + shadow_offset),
                     (0, 0, 0), -1)
        
        # Vẽ nền chính với gradient (từ đậm đến nhạt)
        for i in range(table_height):
            alpha = 0.92 - (i / table_height) * 0.15  # Gradient từ 0.92 đến 0.77
            color_val = int(15 + (i / table_height) * 15)  # Gradient màu
            cv2.rectangle(overlay, 
                         (x, y + i), 
                         (x + table_width, y + i + 1),
                         (color_val, color_val, color_val + 5), -1)
        
        # Blend overlay với frame gốc
        frame = cv2.addWeighted(overlay, 0.88, frame, 0.12, 0)
        
        # Vẽ border ngoài với màu accent
        cv2.rectangle(frame, (x, y), (x + table_width, y + table_height),
                     (255, 200, 50), 3)  # Viền vàng cam đẹp mắt
        cv2.rectangle(frame, (x + 2, y + 2), (x + table_width - 2, y + table_height - 2),
                     (200, 200, 200), 1)  # Viền trong màu sáng
        
        # === TIÊU ĐỀ ===
        current_y = y + padding + 22
        title_text = "PLAYER STATS"
        
        # Vẽ text shadow cho tiêu đề
        cv2.putText(frame, title_text, (x + padding + 2, current_y + 2), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 0, 0), 3)
        # Vẽ tiêu đề chính
        cv2.putText(frame, title_text, (x + padding, current_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.75, (255, 255, 255), 2)
        
        # Đường phân cách dưới tiêu đề
        current_y += 12
        cv2.line(frame, (x + padding, current_y), 
                (x + table_width - padding, current_y), 
                (255, 200, 50), 2)
        
        # === HEADER ===
        current_y += 28
        headers = ["ID", "Touches", "Poss%", "Dist(m)", "Speed"]
        col_positions = [x + 15, x + 85, x + 160, x + 230, x + 315]
        
        for i, header in enumerate(headers):
            # Shadow cho header
            cv2.putText(frame, header, (col_positions[i] + 1, current_y + 1), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)
            # Header text
            cv2.putText(frame, header, (col_positions[i], current_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 220, 100), 1)
        
        # Đường kẻ dưới header
        current_y += 8
        cv2.line(frame, (x + padding, current_y), 
                (x + table_width - padding, current_y), 
                (100, 100, 100), 1)
        
        # === DATA ROWS ===
        current_y += 22
        
        # Sắp xếp players theo một tiêu chí (ví dụ: total_distance)
        sorted_players = sorted(
            list(self.player_stats.items())[:max_players],
            key=lambda x: x[1].get('total_distance', 0),
            reverse=True
        )
        
        for idx, (player_id, stats) in enumerate(sorted_players):
            # Vẽ nền xen kẽ cho mỗi row
            if idx % 2 == 0:
                row_overlay = frame.copy()
                cv2.rectangle(row_overlay, 
                             (x + 5, current_y - 18), 
                             (x + table_width - 5, current_y + 8),
                             (40, 40, 45), -1)
                frame = cv2.addWeighted(row_overlay, 0.3, frame, 0.7, 0)
            
            # Team color indicator (hình tròn màu đội)
            team_color = stats.get('team_color', (255, 255, 255))
            team_color_bgr = (int(team_color[2]), int(team_color[1]), int(team_color[0]))
            cv2.circle(frame, (x + 28, current_y - 6), 8, team_color_bgr, -1)
            cv2.circle(frame, (x + 28, current_y - 6), 8, (255, 255, 255), 1)
            
            # Player ID
            id_text = f"{player_id}"
            cv2.putText(frame, id_text, (col_positions[0] + 32, current_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Touches - căn giữa
            touches_text = f"{stats['ball_touches']}"
            text_size = cv2.getTextSize(touches_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
            touches_x = col_positions[1] + 15  # Căn giữa trong khoảng cột
            cv2.putText(frame, touches_text, (touches_x, current_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.48, (200, 255, 200), 1)
            
            # Possession % - căn giữa
            poss_text = f"{stats['possession_percentage']:.1f}"
            text_size = cv2.getTextSize(poss_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
            poss_x = col_positions[2] + 5  # Căn giữa trong khoảng cột
            cv2.putText(frame, poss_text, (poss_x, current_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.48, (150, 220, 255), 1)
            
            # Distance - căn giữa
            dist_text = f"{stats['total_distance']:.1f}"
            text_size = cv2.getTextSize(dist_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
            dist_x = col_positions[3] + 5  # Căn giữa trong khoảng cột
            cv2.putText(frame, dist_text, (dist_x, current_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 200, 150), 1)
            
            # Speed - căn giữa
            speed_text = f"{stats['average_speed']:.1f}"
            text_size = cv2.getTextSize(speed_text, cv2.FONT_HERSHEY_SIMPLEX, 0.48, 1)[0]
            speed_x = col_positions[4] + 5  # Căn giữa trong khoảng cột
            cv2.putText(frame, speed_text, (speed_x, current_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 180, 255), 1)
            
            current_y += row_height
        
        return frame
    
    def export_stats_to_csv(self, output_path='player_stats.csv'):
        """
        Xuất thống kê ra file CSV
        
        Args:
            output_path: Đường dẫn file output
        """
        import csv
        
        if not self.player_stats:
            print("No stats to export")
            return
        
        # Tạo header
        fieldnames = ['player_id', 'team', 'ball_touches', 'possession_frames', 
                     'possession_percentage', 'total_distance', 'average_speed', 
                     'frames_tracked']
        
        # Ghi file CSV
        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for player_id, stats in sorted(self.player_stats.items()):
                row = {
                    'player_id': player_id,
                    'team': stats['team'],
                    'ball_touches': stats['ball_touches'],
                    'possession_frames': stats['possession_frames'],
                    'possession_percentage': f"{stats['possession_percentage']:.2f}",
                    'total_distance': f"{stats['total_distance']:.2f}",
                    'average_speed': f"{stats['average_speed']:.2f}",
                    'frames_tracked': stats['frames_tracked']
                }
                writer.writerow(row)
        
        print(f"Stats exported to {output_path}")
