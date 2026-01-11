"""
Case Study 1: Team Performance Comparison
Phân tích và so sánh hiệu suất giữa 2 đội bóng
"""

import numpy as np
import cv2
from collections import defaultdict


class TeamComparisonAnalyzer:
    """
    Phân tích so sánh hiệu suất giữa 2 đội
    """
    
    def __init__(self):
        self.team_stats = {}
        self.team_possession_by_zone = {}
        
    def analyze_teams(self, tracks, team_ball_control):
        """
        Phân tích thống kê chi tiết của cả 2 đội
        
        Args:
            tracks: Dictionary chứa tracking data
            team_ball_control: Array chứa thông tin đội kiểm soát bóng
        
        Returns:
            Dictionary chứa thống kê của cả 2 đội
        """
        # Khởi tạo stats cho 2 đội
        self.team_stats = {
            1: self._init_team_stats(1),
            2: self._init_team_stats(2)
        }
        
        total_frames = len(tracks['players'])
        
        # Phân tích từng frame
        for frame_num in range(total_frames):
            player_frame = tracks['players'][frame_num]
            
            for player_id, player_data in player_frame.items():
                team = player_data.get('team')
                if team not in [1, 2]:
                    continue
                
                # Đếm số cầu thủ hoạt động
                self.team_stats[team]['active_players'].add(player_id)
                
                # Tính tổng quãng đường
                if 'distance' in player_data and player_data['distance'] is not None:
                    self.team_stats[team]['total_distance'] += player_data['distance']
                
                # Tính tổng tốc độ
                if 'speed' in player_data and player_data['speed'] is not None:
                    self.team_stats[team]['total_speed'] += player_data['speed']
                    self.team_stats[team]['speed_count'] += 1
                
                # Đếm số lần chạm bóng
                if player_data.get('has_ball', False):
                    # Kiểm tra xem có phải lần chạm mới không
                    if frame_num > 0:
                        prev_frame = tracks['players'][frame_num - 1]
                        if player_id in prev_frame:
                            prev_has_ball = prev_frame[player_id].get('has_ball', False)
                            if not prev_has_ball:
                                self.team_stats[team]['ball_touches'] += 1
                    else:
                        self.team_stats[team]['ball_touches'] += 1
                    
                    self.team_stats[team]['possession_frames'] += 1
            
            # Phân tích kiểm soát bóng
            if frame_num < len(team_ball_control):
                controlling_team = team_ball_control[frame_num]
                if controlling_team in [1, 2]:
                    self.team_stats[controlling_team]['ball_control_frames'] += 1
        
        # Tính toán các chỉ số cuối cùng
        for team in [1, 2]:
            stats = self.team_stats[team]
            
            # Số lượng cầu thủ
            stats['num_players'] = len(stats['active_players'])
            
            # Tốc độ trung bình
            if stats['speed_count'] > 0:
                stats['average_speed'] = stats['total_speed'] / stats['speed_count']
            
            # Tỷ lệ kiểm soát bóng
            if total_frames > 0:
                stats['possession_percentage'] = (stats['ball_control_frames'] / total_frames) * 100
            
            # Quãng đường trung bình mỗi cầu thủ
            if stats['num_players'] > 0:
                stats['avg_distance_per_player'] = stats['total_distance'] / stats['num_players']
        
        return self.team_stats
    
    def _init_team_stats(self, team_id):
        """Khởi tạo cấu trúc thống kê cho đội"""
        return {
            'team_id': team_id,
            'active_players': set(),
            'num_players': 0,
            'ball_touches': 0,
            'possession_frames': 0,
            'ball_control_frames': 0,
            'possession_percentage': 0.0,
            'total_distance': 0.0,
            'avg_distance_per_player': 0.0,
            'total_speed': 0.0,
            'speed_count': 0,
            'average_speed': 0.0,
        }
    
    def create_comparison_chart(self, width=1200, height=800):
        """
        Tạo biểu đồ so sánh giữa 2 đội
        
        Args:
            width: Chiều rộng biểu đồ
            height: Chiều cao biểu đồ
        
        Returns:
            Hình ảnh numpy array của biểu đồ so sánh
        """
        # Tạo canvas trắng
        chart = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        if not self.team_stats:
            return chart
        
        # Màu sắc cho 2 đội
        team1_color = (100, 150, 255)  # Xanh dương
        team2_color = (100, 255, 150)  # Xanh lá
        
        # Tiêu đề
        title = "TEAM PERFORMANCE COMPARISON"
        cv2.putText(chart, title, (width//2 - 300, 60), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 2)
        
        # Vẽ đường phân cách giữa
        cv2.line(chart, (width//2, 100), (width//2, height - 50), (200, 200, 200), 2)
        
        # Thông tin Team 1 (bên trái)
        self._draw_team_info(chart, self.team_stats[1], 50, 120, team1_color, "Team 1")
        
        # Thông tin Team 2 (bên phải)
        self._draw_team_info(chart, self.team_stats[2], width//2 + 50, 120, team2_color, "Team 2")
        
        # Vẽ biểu đồ so sánh dưới cùng
        self._draw_comparison_bars(chart, 50, height - 300, width - 100, 250)
        
        return chart
    
    def _draw_team_info(self, img, stats, x, y, color, team_name):
        """Vẽ thông tin chi tiết của một đội"""
        # Tên đội với màu nền
        cv2.rectangle(img, (x, y - 35), (x + 200, y - 5), color, -1)
        cv2.putText(img, team_name, (x + 10, y - 12), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
        
        y_offset = y + 20
        line_height = 40
        
        # Danh sách các metrics
        metrics = [
            (f"Players: {stats['num_players']}", (0, 0, 0)),
            (f"Ball Touches: {stats['ball_touches']}", (0, 0, 0)),
            (f"Possession: {stats['possession_percentage']:.1f}%", color),
            (f"Total Distance: {stats['total_distance']:.1f} m", (0, 0, 0)),
            (f"Avg Distance/Player: {stats['avg_distance_per_player']:.1f} m", (0, 0, 0)),
            (f"Average Speed: {stats['average_speed']:.2f} km/h", (0, 0, 0)),
        ]
        
        for text, text_color in metrics:
            cv2.putText(img, text, (x, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            y_offset += line_height
    
    def _draw_comparison_bars(self, img, x, y, width, height):
        """Vẽ biểu đồ thanh so sánh các chỉ số"""
        team1_stats = self.team_stats[1]
        team2_stats = self.team_stats[2]
        
        # Tiêu đề
        cv2.putText(img, "Key Metrics Comparison", (x, y - 10), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)
        
        # Các metrics cần so sánh
        metrics = [
            ('Ball Touches', team1_stats['ball_touches'], team2_stats['ball_touches']),
            ('Possession %', team1_stats['possession_percentage'], team2_stats['possession_percentage']),
            ('Total Dist (m)', team1_stats['total_distance'], team2_stats['total_distance']),
            ('Avg Speed', team1_stats['average_speed'], team2_stats['average_speed']),
        ]
        
        bar_height = 35
        bar_spacing = 15
        max_bar_width = (width - 200) // 2
        
        y_pos = y + 30
        
        for label, val1, val2 in metrics:
            # Label
            cv2.putText(img, label, (x, y_pos + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
            
            # Tính độ dài thanh
            max_val = max(val1, val2, 1)  # Tránh chia cho 0
            bar1_width = int((val1 / max_val) * max_bar_width)
            bar2_width = int((val2 / max_val) * max_bar_width)
            
            center_x = x + 200 + max_bar_width
            
            # Team 1 bar (bên trái từ center)
            cv2.rectangle(img, 
                         (center_x - bar1_width, y_pos), 
                         (center_x, y_pos + bar_height),
                         (100, 150, 255), -1)
            cv2.putText(img, f"{val1:.1f}", (center_x - bar1_width - 60, y_pos + 22), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 150, 255), 1)
            
            # Team 2 bar (bên phải từ center)
            cv2.rectangle(img, 
                         (center_x, y_pos), 
                         (center_x + bar2_width, y_pos + bar_height),
                         (100, 255, 150), -1)
            cv2.putText(img, f"{val2:.1f}", (center_x + bar2_width + 10, y_pos + 22), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.45, (100, 255, 150), 1)
            
            # Đường center
            cv2.line(img, (center_x, y_pos), (center_x, y_pos + bar_height), (0, 0, 0), 2)
            
            y_pos += bar_height + bar_spacing
    
    def export_to_dict(self):
        """Export dữ liệu ra dictionary để lưu JSON"""
        export_data = {}
        for team_id, stats in self.team_stats.items():
            export_stats = stats.copy()
            # Chuyển set thành list để serialize JSON
            export_stats['active_players'] = list(stats['active_players'])
            export_data[f'team_{team_id}'] = export_stats
        
        return export_data
