"""
Case Study 2: MVP (Most Valuable Player) Analysis
Phân tích cầu thủ xuất sắc nhất trong trận đấu
"""

import numpy as np
import cv2


class MVPAnalyzer:
    """
    Phân tích và xác định cầu thủ xuất sắc nhất (MVP)
    """
    
    def __init__(self):
        self.mvp_data = None
        self.all_players_ranked = []
        
    def analyze_mvp(self, player_stats, tracks):
        """
        Xác định MVP dựa trên nhiều chỉ số
        
        Args:
            player_stats: Dictionary thống kê cầu thủ từ PlayerStatsAnalyzer
            tracks: Dictionary chứa tracking data
        
        Returns:
            Dictionary chứa thông tin MVP và bảng xếp hạng
        """
        if not player_stats:
            return None
        
        # Tính điểm tổng hợp cho mỗi cầu thủ
        scored_players = []
        
        for player_id, stats in player_stats.items():
            # Tính MVP score (weighted average của các chỉ số)
            mvp_score = self._calculate_mvp_score(stats)
            
            player_info = {
                'player_id': player_id,
                'team': stats['team'],
                'team_color': stats['team_color'],
                'mvp_score': mvp_score,
                'ball_touches': stats['ball_touches'],
                'possession_percentage': stats['possession_percentage'],
                'total_distance': stats['total_distance'],
                'average_speed': stats['average_speed'],
                'frames_tracked': stats['frames_tracked']
            }
            
            scored_players.append(player_info)
        
        # Sắp xếp theo MVP score
        self.all_players_ranked = sorted(scored_players, key=lambda x: x['mvp_score'], reverse=True)
        
        # MVP là người có điểm cao nhất
        if self.all_players_ranked:
            self.mvp_data = self.all_players_ranked[0]
            
            # Thêm thông tin vị trí trong tracks
            self._add_movement_heatmap_data(tracks)
        
        return {
            'mvp': self.mvp_data,
            'top_5': self.all_players_ranked[:5],
            'all_ranked': self.all_players_ranked
        }
    
    def _calculate_mvp_score(self, stats):
        """
        Tính điểm MVP dựa trên các chỉ số
        
        Công thức: 
        - Ball touches: 30%
        - Possession: 25%
        - Distance: 25%
        - Speed: 20%
        """
        # Normalize các chỉ số về scale 0-100
        
        # Ball touches (giả sử max là 10 touches)
        touches_score = min(stats['ball_touches'] / 10.0 * 100, 100)
        
        # Possession (đã là %)
        poss_score = stats['possession_percentage']
        
        # Distance (giả sử max là 30000m cho toàn trận)
        distance_score = min(stats['total_distance'] / 30000.0 * 100, 100)
        
        # Speed (giả sử max là 30 km/h)
        speed_score = min(stats['average_speed'] / 30.0 * 100, 100)
        
        # Tính điểm tổng với trọng số
        mvp_score = (
            touches_score * 0.30 +
            poss_score * 0.25 +
            distance_score * 0.25 +
            speed_score * 0.20
        )
        
        return mvp_score
    
    def _add_movement_heatmap_data(self, tracks):
        """Thêm dữ liệu heatmap di chuyển của MVP"""
        if not self.mvp_data:
            return
        
        mvp_id = self.mvp_data['player_id']
        positions = []
        
        for frame_num, player_frame in enumerate(tracks['players']):
            if mvp_id in player_frame:
                player_data = player_frame[mvp_id]
                if 'position' in player_data:
                    positions.append(player_data['position'])
        
        self.mvp_data['movement_positions'] = positions
    
    def create_mvp_card(self, width=800, height=1000):
        """
        Tạo card thông tin MVP
        
        Args:
            width: Chiều rộng card
            height: Chiều cao card
        
        Returns:
            Hình ảnh numpy array của MVP card
        """
        if not self.mvp_data:
            card = np.ones((height, width, 3), dtype=np.uint8) * 255
            cv2.putText(card, "No MVP data available", (width//4, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            return card
        
        # Tạo gradient background
        card = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Gradient từ đen sang màu đội
        team_color = self.mvp_data['team_color']
        for i in range(height):
            ratio = i / height
            color = (
                int(team_color[2] * ratio),
                int(team_color[1] * ratio),
                int(team_color[0] * ratio)
            )
            cv2.rectangle(card, (0, i), (width, i+1), color, -1)
        
        # Overlay trong suốt
        overlay = card.copy()
        cv2.rectangle(overlay, (50, 50), (width - 50, height - 50), (255, 255, 255), -1)
        card = cv2.addWeighted(overlay, 0.9, card, 0.1, 0)
        
        # Border
        cv2.rectangle(card, (50, 50), (width - 50, height - 50), (0, 0, 0), 3)
        cv2.rectangle(card, (52, 52), (width - 52, height - 52), (255, 215, 0), 2)
        
        # Title
        cv2.putText(card, "MATCH MVP", (width//2 - 150, 120), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 215, 0), 3)
        cv2.putText(card, "MATCH MVP", (width//2 - 150, 120), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 0), 2)
        
        # Player ID với circle background
        player_circle_center = (width // 2, 220)
        cv2.circle(card, player_circle_center, 70, (0, 0, 0), -1)
        cv2.circle(card, player_circle_center, 68, (255, 215, 0), -1)
        
        player_text = f"#{self.mvp_data['player_id']}"
        text_size = cv2.getTextSize(player_text, cv2.FONT_HERSHEY_DUPLEX, 2, 3)[0]
        text_x = player_circle_center[0] - text_size[0] // 2
        text_y = player_circle_center[1] + text_size[1] // 2
        cv2.putText(card, player_text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_DUPLEX, 2, (0, 0, 0), 3)
        
        # MVP Score
        score_text = f"MVP Score: {self.mvp_data['mvp_score']:.1f}/100"
        cv2.putText(card, score_text, (width//2 - 150, 330), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 2)
        
        # Stats section
        y_offset = 400
        line_height = 60
        
        stats_to_show = [
            ("Ball Touches", f"{self.mvp_data['ball_touches']}", (255, 100, 100)),
            ("Possession", f"{self.mvp_data['possession_percentage']:.1f}%", (100, 150, 255)),
            ("Distance Covered", f"{self.mvp_data['total_distance']:.1f} m", (100, 255, 150)),
            ("Average Speed", f"{self.mvp_data['average_speed']:.2f} km/h", (255, 200, 100)),
        ]
        
        for label, value, color in stats_to_show:
            # Background bar
            cv2.rectangle(card, (100, y_offset - 35), (width - 100, y_offset + 15), color, -1)
            cv2.rectangle(card, (100, y_offset - 35), (width - 100, y_offset + 15), (0, 0, 0), 2)
            
            # Label
            cv2.putText(card, label, (120, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Value (right aligned)
            text_size = cv2.getTextSize(value, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
            cv2.putText(card, value, (width - 120 - text_size[0], y_offset), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
            
            y_offset += line_height
        
        # Team indicator
        team_text = f"Team {self.mvp_data['team']}"
        cv2.putText(card, team_text, (width//2 - 80, height - 100), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 0, 0), 2)
        
        # Team color bar
        team_color_bgr = (
            int(team_color[2]),
            int(team_color[1]),
            int(team_color[0])
        )
        cv2.rectangle(card, (width//2 - 100, height - 70), (width//2 + 100, height - 80), 
                     team_color_bgr, -1)
        cv2.rectangle(card, (width//2 - 100, height - 70), (width//2 + 100, height - 80), 
                     (0, 0, 0), 2)
        
        return card
    
    def create_top5_ranking(self, width=1000, height=700):
        """
        Tạo bảng xếp hạng top 5 cầu thủ
        
        Args:
            width: Chiều rộng bảng
            height: Chiều cao bảng
        
        Returns:
            Hình ảnh numpy array của bảng xếp hạng
        """
        if not self.all_players_ranked:
            ranking = np.ones((height, width, 3), dtype=np.uint8) * 255
            cv2.putText(ranking, "No ranking data available", (width//4, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            return ranking
        
        # Background gradient
        ranking = np.ones((height, width, 3), dtype=np.uint8) * 245
        
        # Title
        title = "TOP 5 PLAYERS RANKING"
        cv2.putText(ranking, title, (width//2 - 250, 60), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)
        
        # Header
        header_y = 120
        cv2.rectangle(ranking, (50, header_y - 10), (width - 50, header_y + 35), (50, 50, 50), -1)
        
        headers = ["Rank", "Player", "Team", "MVP Score", "Touches", "Poss%", "Distance"]
        header_x_positions = [70, 180, 280, 380, 520, 640, 760]
        
        for i, header in enumerate(headers):
            cv2.putText(ranking, header, (header_x_positions[i], header_y + 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Player rows
        row_y = header_y + 70
        row_height = 70
        
        top_5 = self.all_players_ranked[:5]
        
        for rank, player in enumerate(top_5, 1):
            # Alternating background
            if rank % 2 == 0:
                cv2.rectangle(ranking, (50, row_y - 25), (width - 50, row_y + 35), 
                             (230, 230, 230), -1)
            
            # Medal/Rank
            rank_color = [(255, 215, 0), (192, 192, 192), (205, 127, 50)][rank - 1] if rank <= 3 else (100, 100, 100)
            cv2.circle(ranking, (90, row_y + 5), 25, rank_color, -1)
            cv2.circle(ranking, (90, row_y + 5), 25, (0, 0, 0), 2)
            cv2.putText(ranking, str(rank), (82 if rank < 10 else 77, row_y + 15), 
                       cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)
            
            # Player ID
            cv2.putText(ranking, str(player['player_id']), (header_x_positions[1], row_y + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Team color
            team_color = player['team_color']
            team_color_bgr = (int(team_color[2]), int(team_color[1]), int(team_color[0]))
            cv2.rectangle(ranking, (header_x_positions[2], row_y - 10), 
                         (header_x_positions[2] + 50, row_y + 20), team_color_bgr, -1)
            cv2.rectangle(ranking, (header_x_positions[2], row_y - 10), 
                         (header_x_positions[2] + 50, row_y + 20), (0, 0, 0), 2)
            
            # MVP Score
            score_color = (0, 180, 0) if player['mvp_score'] >= 50 else (180, 100, 0)
            cv2.putText(ranking, f"{player['mvp_score']:.1f}", (header_x_positions[3], row_y + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, score_color, 2)
            
            # Touches
            cv2.putText(ranking, str(player['ball_touches']), (header_x_positions[4], row_y + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            
            # Possession
            cv2.putText(ranking, f"{player['possession_percentage']:.1f}", (header_x_positions[5], row_y + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            
            # Distance
            cv2.putText(ranking, f"{player['total_distance']:.0f}", (header_x_positions[6], row_y + 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
            
            row_y += row_height
        
        return ranking
    
    def export_to_dict(self):
        """Export dữ liệu ra dictionary"""
        if not self.mvp_data:
            return {}
        
        return {
            'mvp': self.mvp_data,
            'top_5_players': self.all_players_ranked[:5] if len(self.all_players_ranked) >= 5 else self.all_players_ranked,
            'all_players_ranked': self.all_players_ranked
        }
