"""
Case Study 3: Tactical Analysis & Passing Network
Phân tích chiến thuật và mạng lưới chuyền bóng
"""

import numpy as np
import cv2
from collections import defaultdict
from sklearn.cluster import KMeans


class TacticalAnalyzer:
    """
    Phân tích chiến thuật và passing network
    """
    
    def __init__(self):
        self.passing_network = defaultdict(lambda: defaultdict(int))
        self.player_positions = {}
        self.formation_data = {}
        self.last_pass_frame = {}  # Lưu frame của pass gần nhất để tránh duplicate
        self.last_ball_holder = None  # Lưu cầu thủ giữ bóng trước đó
        
    def analyze_tactics(self, tracks, team_ball_control):
        """
        Phân tích chiến thuật và passing network
        
        Args:
            tracks: Dictionary chứa tracking data
            team_ball_control: Array chứa thông tin đội kiểm soát bóng
        
        Returns:
            Dictionary chứa phân tích chiến thuật
        """
        total_frames = len(tracks['players'])
        
        # Phân tích từng frame
        for frame_num in range(total_frames):
            player_frame = tracks['players'][frame_num]
            
            # Lưu vị trí trung bình của cầu thủ
            for player_id, player_data in player_frame.items():
                team = player_data.get('team')
                if team not in [1, 2]:
                    continue
                
                if player_id not in self.player_positions:
                    self.player_positions[player_id] = {
                        'team': team,
                        'positions': [],
                        'avg_x': 0,
                        'avg_y': 0
                    }
                
                if 'position' in player_data:
                    self.player_positions[player_id]['positions'].append(player_data['position'])
            
            # Phát hiện passing (chuyền bóng)
            if frame_num > 0:
                self._detect_pass(tracks, frame_num)
        
        # Tính vị trí trung bình
        for player_id, data in self.player_positions.items():
            if data['positions']:
                positions = np.array(data['positions'])
                data['avg_x'] = np.mean(positions[:, 0])
                data['avg_y'] = np.mean(positions[:, 1])
        
        # Phân tích đội hình cho từng đội
        self.formation_data[1] = self._detect_formation(1)
        self.formation_data[2] = self._detect_formation(2)
        
        return {
            'passing_network': dict(self.passing_network),
            'formations': self.formation_data,
            'player_positions': self.player_positions
        }
    
    def _detect_pass(self, tracks, frame_num):
        """
        Phát hiện pha chuyền bóng với thuật toán cải tiến
        Sử dụng khoảng cách từ bóng đến cầu thủ thay vì chỉ dựa vào has_ball
        Có debounce để tránh phát hiện trùng lặp
        """
        if frame_num < 1:
            return
        
        current_frame = tracks['players'][frame_num]
        
        # Lấy vị trí bóng
        if frame_num >= len(tracks['ball']) or 1 not in tracks['ball'][frame_num]:
            return
        
        ball_bbox = tracks['ball'][frame_num][1].get('bbox')
        if ball_bbox is None:
            return
        
        # Tính center của bóng
        ball_x = (ball_bbox[0] + ball_bbox[2]) / 2
        ball_y = (ball_bbox[1] + ball_bbox[3]) / 2
        
        # Tìm cầu thủ gần bóng nhất ở frame hiện tại (trong vòng 150 pixels)
        min_dist = 150  # threshold tăng lên để phát hiện tốt hơn
        current_ball_holder = None
        
        for player_id, player_data in current_frame.items():
            if 'position' not in player_data:
                continue
            
            team = player_data.get('team')
            if team not in [1, 2]:
                continue
            
            pos = player_data['position']
            dist = np.sqrt((pos[0] - ball_x)**2 + (pos[1] - ball_y)**2)
            
            if dist < min_dist:
                min_dist = dist
                current_ball_holder = player_id
        
        # Kiểm tra xem có thay đổi possession không
        if current_ball_holder and self.last_ball_holder:
            if current_ball_holder != self.last_ball_holder:
                # Kiểm tra cùng đội
                if current_ball_holder in current_frame:
                    current_team = current_frame[current_ball_holder].get('team')
                    
                    # Tìm team của last_ball_holder từ frame trước
                    for past_frame_num in range(max(0, frame_num - 10), frame_num):
                        if self.last_ball_holder in tracks['players'][past_frame_num]:
                            prev_team = tracks['players'][past_frame_num][self.last_ball_holder].get('team')
                            
                            if prev_team == current_team and prev_team in [1, 2]:
                                # Tạo key cho pass này
                                pass_key = f"{self.last_ball_holder}_{current_ball_holder}"
                                
                                # Kiểm tra debounce (chỉ ghi nhận pass nếu đã qua ít nhất 10 frames)
                                if pass_key not in self.last_pass_frame or (frame_num - self.last_pass_frame[pass_key]) >= 10:
                                    self.passing_network[self.last_ball_holder][current_ball_holder] += 1
                                    self.last_pass_frame[pass_key] = frame_num
                            break
        
        # Cập nhật last_ball_holder
        if current_ball_holder:
            self.last_ball_holder = current_ball_holder
    
    def _get_top_players_per_team(self, max_per_team=11):
        """
        Lọc và lấy top N cầu thủ chơi nhiều nhất mỗi đội
        
        Args:
            max_per_team: Số lượng cầu thủ tối đa mỗi đội (mặc định 11)
        
        Returns:
            Dictionary chứa các cầu thủ đã lọc
        """
        # Nhóm cầu thủ theo đội
        team_players = {1: [], 2: []}
        
        for player_id, data in self.player_positions.items():
            if not data['positions']:
                continue
            
            team = data.get('team')
            if team in [1, 2]:
                team_players[team].append((player_id, len(data['positions']), data))
        
        # Lọc top players cho mỗi đội
        filtered = {}
        
        for team_id in [1, 2]:
            # Sắp xếp theo số frames (chơi nhiều nhất)
            team_players[team_id].sort(key=lambda x: x[1], reverse=True)
            
            # Lấy top max_per_team cầu thủ
            top_players = team_players[team_id][:max_per_team]
            
            for player_id, _, data in top_players:
                filtered[player_id] = data
        
        return filtered
    
    def _detect_formation(self, team_id):
        """
        Phát hiện đội hình dựa trên vị trí trung bình của cầu thủ
        Giới hạn tối đa 11 cầu thủ theo luật bóng đá
        Sử dụng K-means clustering để phát hiện các dòng chính xác
        
        Returns:
            Dictionary chứa thông tin đội hình
        """
        # Lấy cầu thủ của đội
        team_players = {
            pid: data for pid, data in self.player_positions.items()
            if data['team'] == team_id and data['positions']
        }
        
        if not team_players:
            return {'formation': 'Unknown', 'lines': [], 'num_players': 0}
        
        # Giới hạn tối đa 11 cầu thủ (theo luật bóng đá)
        # Lấy 11 cầu thủ có nhiều frames nhất (chơi nhiều nhất)
        player_activity = [
            (pid, len(data['positions']), data) 
            for pid, data in team_players.items()
        ]
        player_activity.sort(key=lambda x: x[1], reverse=True)
        
        # Chỉ lấy tối đa 11 cầu thủ
        top_players = player_activity[:min(11, len(player_activity))]
        team_players = {pid: data for pid, _, data in top_players}
        
        num_players = len(team_players)
        
        if num_players < 4:
            # Quá ít cầu thủ
            return {
                'formation': f'{num_players}-0-0',
                'lines': [[pid for pid, _ in top_players]],
                'num_players': num_players
            }
        
        # Sắp xếp theo vị trí Y (từ thủ môn đến tiền đạo)
        sorted_players = sorted(
            team_players.items(),
            key=lambda x: x[1]['avg_y']
        )
        
        # Tách thủ môn (cầu thủ đầu tiên)
        goalkeeper_id = sorted_players[0][0]
        field_players = sorted_players[1:]  # 10 cầu thủ còn lại
        
        if len(field_players) < 3:
            # Quá ít cầu thủ để phân tích
            return {
                'formation': f'1-{len(field_players)}-0',
                'lines': [[goalkeeper_id], [pid for pid, _ in field_players]],
                'num_players': num_players
            }
        
        # Sử dụng K-means để chia thành 3 dòng: Defenders, Midfielders, Forwards
        y_positions = np.array([data['avg_y'] for _, data in field_players]).reshape(-1, 1)
        
        # Xác định số lượng dòng tối ưu (3 hoặc 4 dòng)
        best_formation = self._find_best_formation_kmeans(field_players, 3)
        
        # Thêm thủ môn vào đầu
        all_lines = [[goalkeeper_id]] + best_formation['lines']
        formation_counts = [1] + best_formation['line_counts']
        
        # Tạo chuỗi formation (bỏ thủ môn, chỉ hiển thị Defenders-Midfielders-Forwards)
        formation_str = '-'.join([str(c) for c in best_formation['line_counts']])
        
        return {
            'formation': formation_str,
            'lines': all_lines,
            'num_players': num_players
        }
    
    def _find_best_formation_kmeans(self, field_players, num_lines=3):
        """
        Tìm đội hình tốt nhất sử dụng K-means clustering
        
        Args:
            field_players: List các cầu thủ (không bao gồm thủ môn)
            num_lines: Số dòng cần chia (mặc định 3: defenders-midfielders-forwards)
        
        Returns:
            Dictionary chứa lines và line_counts
        """
        if len(field_players) < num_lines:
            # Không đủ cầu thủ để chia thành num_lines dòng
            return {
                'lines': [[pid for pid, _ in field_players]],
                'line_counts': [len(field_players)]
            }
        
        # Lấy vị trí Y
        y_positions = np.array([data['avg_y'] for _, data in field_players]).reshape(-1, 1)
        
        # K-means clustering
        kmeans = KMeans(n_clusters=num_lines, random_state=42, n_init=10)
        labels = kmeans.fit_predict(y_positions)
        
        # Nhóm cầu thủ theo cluster
        clusters = [[] for _ in range(num_lines)]
        for idx, (pid, _) in enumerate(field_players):
            cluster_id = labels[idx]
            clusters[cluster_id].append((pid, y_positions[idx][0]))
        
        # Sắp xếp clusters theo vị trí Y trung bình (từ gần thủ môn đến xa)
        cluster_means = [(i, np.mean([y for _, y in cluster])) for i, cluster in enumerate(clusters) if cluster]
        cluster_means.sort(key=lambda x: x[1])
        
        # Tạo lines theo thứ tự từ defenders đến forwards
        lines = []
        line_counts = []
        
        for cluster_idx, _ in cluster_means:
            cluster_players = [pid for pid, _ in clusters[cluster_idx]]
            if cluster_players:
                lines.append(cluster_players)
                line_counts.append(len(cluster_players))
        
        # Kiểm tra và điều chỉnh formation về dạng phổ biến
        line_counts = self._normalize_formation(line_counts, len(field_players))
        
        # Cập nhật lại lines sau khi normalize
        if sum(line_counts) != len(field_players):
            # Nếu normalize thay đổi số lượng, phải tái phân bổ
            lines = self._redistribute_players(field_players, line_counts)
        
        return {
            'lines': lines,
            'line_counts': line_counts
        }
    
    def _normalize_formation(self, line_counts, total_players):
        """
        Chuẩn hóa đội hình về các dạng phổ biến trong bóng đá
        
        Common formations:
        - 4-4-2 (10 players)
        - 4-3-3 (10 players)
        - 3-5-2 (10 players)
        - 4-5-1 (10 players)
        - 3-4-3 (10 players)
        - 5-3-2 (10 players)
        - 5-4-1 (10 players)
        """
        # Các đội hình phổ biến cho 10 cầu thủ (không tính thủ môn)
        common_formations = {
            10: [
                [4, 4, 2],  # 4-4-2 - phổ biến nhất
                [4, 3, 3],  # 4-3-3
                [3, 5, 2],  # 3-5-2
                [4, 5, 1],  # 4-5-1
                [3, 4, 3],  # 3-4-3
                [5, 3, 2],  # 5-3-2
                [5, 4, 1],  # 5-4-1
            ],
            9: [
                [4, 4, 1],
                [4, 3, 2],
                [3, 4, 2],
                [3, 3, 3],
            ],
            8: [
                [4, 3, 1],
                [3, 3, 2],
                [3, 4, 1],
            ],
            7: [
                [3, 3, 1],
                [3, 2, 2],
                [4, 2, 1],
            ]
        }
        
        if total_players not in common_formations:
            return line_counts  # Giữ nguyên nếu không có trong danh sách
        
        # Tìm formation gần nhất với line_counts hiện tại
        possible_formations = common_formations[total_players]
        
        def distance(f1, f2):
            return sum((a - b) ** 2 for a, b in zip(f1, f2))
        
        # Pad line_counts về cùng độ dài nếu cần
        if len(line_counts) < 3:
            line_counts = line_counts + [0] * (3 - len(line_counts))
        elif len(line_counts) > 3:
            # Gộp các dòng thừa vào dòng gần nhất
            line_counts = line_counts[:3]
        
        best_formation = min(possible_formations, key=lambda f: distance(f, line_counts))
        
        return best_formation
    
    def _redistribute_players(self, field_players, target_counts):
        """
        Phân bổ lại cầu thủ theo target_counts
        """
        # Sắp xếp theo Y
        sorted_players = sorted(field_players, key=lambda x: x[1]['avg_y'])
        
        lines = []
        start_idx = 0
        
        for count in target_counts:
            end_idx = start_idx + count
            line_players = [pid for pid, _ in sorted_players[start_idx:end_idx]]
            lines.append(line_players)
            start_idx = end_idx
        
        return lines
    
    def create_passing_network_viz(self, width=1400, height=900):
        """
        Tạo visualization của passing network
        Chỉ hiển thị tối đa 22 cầu thủ (11 mỗi đội)
        
        Args:
            width: Chiều rộng hình ảnh
            height: Chiều cao hình ảnh
        
        Returns:
            Hình ảnh numpy array của passing network
        """
        # Tạo background giống sân bóng
        viz = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Vẽ nền sân xanh
        field_color = (60, 120, 40)
        cv2.rectangle(viz, (50, 50), (width - 50, height - 50), field_color, -1)
        
        # Vẽ đường viền sân
        cv2.rectangle(viz, (50, 50), (width - 50, height - 50), (255, 255, 255), 3)
        
        # Vẽ đường giữa sân
        cv2.line(viz, (width // 2, 50), (width // 2, height - 50), (255, 255, 255), 2)
        cv2.circle(viz, (width // 2, height // 2), 80, (255, 255, 255), 2)
        
        # Title
        cv2.putText(viz, "PASSING NETWORK ANALYSIS", (width//2 - 300, 35), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)
        
        if not self.player_positions:
            cv2.putText(viz, "No data available", (width//2 - 150, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return viz
        
        # LỌC CHỈ LẤY TOP 11 CẦU THỦ MỖI ĐỘI (theo số lượng frames)
        filtered_players = self._get_top_players_per_team(max_per_team=11)
        
        # Đếm số cầu thủ mỗi đội
        team1_count = sum(1 for p in filtered_players.values() if p.get('team') == 1)
        team2_count = sum(1 for p in filtered_players.values() if p.get('team') == 2)
        
        # Subtitle với số lượng cầu thủ
        subtitle = f"Top {team1_count} Team 1 vs Top {team2_count} Team 2 Players"
        cv2.putText(viz, subtitle, (width//2 - 200, 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 100, 100), 2)
        
        if not filtered_players:
            cv2.putText(viz, "No valid players", (width//2 - 150, height//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            return viz
        
        # Scale positions to fit the field (chỉ dùng filtered players)
        all_x = [data['avg_x'] for data in filtered_players.values() if data['positions']]
        all_y = [data['avg_y'] for data in filtered_players.values() if data['positions']]
        
        if not all_x or not all_y:
            return viz
        
        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)
        
        # Map positions to field coordinates
        field_margin = 80
        field_width = width - 2 * field_margin
        field_height = height - 2 * field_margin
        
        player_viz_positions = {}
        
        for player_id, data in filtered_players.items():
            if not data['positions']:
                continue
            
            # Normalize và scale
            if max_x > min_x:
                norm_x = (data['avg_x'] - min_x) / (max_x - min_x)
            else:
                norm_x = 0.5
            
            if max_y > min_y:
                norm_y = (data['avg_y'] - min_y) / (max_y - min_y)
            else:
                norm_y = 0.5
            
            viz_x = int(field_margin + norm_x * field_width)
            viz_y = int(field_margin + norm_y * field_height)
            
            player_viz_positions[player_id] = (viz_x, viz_y)
        
        # Vẽ passing lines (đường chuyền)
        if self.passing_network:
            # Tìm số pass nhiều nhất để scale độ dày đường
            max_passes = max(
                max(passes.values()) if passes else 0
                for passes in self.passing_network.values()
            )
            
            for from_player, passes in self.passing_network.items():
                if from_player not in player_viz_positions:
                    continue
                
                from_pos = player_viz_positions[from_player]
                
                for to_player, pass_count in passes.items():
                    if to_player not in player_viz_positions:
                        continue
                    
                    to_pos = player_viz_positions[to_player]
                    
                    # Độ dày dựa trên số lần pass
                    thickness = int(1 + (pass_count / max(max_passes, 1)) * 8)
                    
                    # Màu dựa trên đội
                    from_team = self.player_positions[from_player]['team']
                    line_color = (150, 200, 255) if from_team == 1 else (150, 255, 200)
                    
                    # Vẽ đường với arrow
                    cv2.arrowedLine(viz, from_pos, to_pos, line_color, thickness, tipLength=0.2)
                    
                    # Vẽ số lần pass
                    mid_x = (from_pos[0] + to_pos[0]) // 2
                    mid_y = (from_pos[1] + to_pos[1]) // 2
                    
                    if pass_count > 1:
                        cv2.circle(viz, (mid_x, mid_y), 15, (255, 255, 255), -1)
                        cv2.circle(viz, (mid_x, mid_y), 15, (0, 0, 0), 2)
                        cv2.putText(viz, str(pass_count), (mid_x - 8, mid_y + 5), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        # Vẽ players (nodes)
        for player_id, pos in player_viz_positions.items():
            team = self.player_positions[player_id]['team']
            
            # Màu dựa trên đội
            if team == 1:
                player_color = (255, 200, 100)
            elif team == 2:
                player_color = (100, 255, 200)
            else:
                player_color = (200, 200, 200)
            
            # Vẽ circle
            cv2.circle(viz, pos, 25, (0, 0, 0), -1)
            cv2.circle(viz, pos, 23, player_color, -1)
            cv2.circle(viz, pos, 23, (0, 0, 0), 2)
            
            # Vẽ player ID
            text = str(player_id)
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            text_x = pos[0] - text_size[0] // 2
            text_y = pos[1] + text_size[1] // 2
            cv2.putText(viz, text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
        # Legend
        legend_x = width - 250
        legend_y = 100
        
        cv2.rectangle(viz, (legend_x - 10, legend_y - 30), 
                     (width - 30, legend_y + 120), (255, 255, 255), -1)
        cv2.rectangle(viz, (legend_x - 10, legend_y - 30), 
                     (width - 30, legend_y + 120), (0, 0, 0), 2)
        
        cv2.putText(viz, "Legend:", (legend_x, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        
        cv2.circle(viz, (legend_x + 10, legend_y + 30), 12, (255, 200, 100), -1)
        cv2.putText(viz, "Team 1", (legend_x + 30, legend_y + 35), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.circle(viz, (legend_x + 10, legend_y + 60), 12, (100, 255, 200), -1)
        cv2.putText(viz, "Team 2", (legend_x + 30, legend_y + 65), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        cv2.arrowedLine(viz, (legend_x + 5, legend_y + 90), (legend_x + 50, legend_y + 90), 
                       (150, 200, 255), 3, tipLength=0.3)
        cv2.putText(viz, "Passes", (legend_x + 60, legend_y + 95), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return viz
    
    def create_formation_viz(self, width=1200, height=800):
        """
        Tạo visualization của đội hình 2 đội
        
        Args:
            width: Chiều rộng
            height: Chiều cao
        
        Returns:
            Hình ảnh numpy array
        """
        viz = np.ones((height, width, 3), dtype=np.uint8) * 255
        
        # Title
        cv2.putText(viz, "TEAM FORMATIONS", (width//2 - 200, 50), 
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 0, 0), 3)
        
        # Draw team 1 formation (left side)
        self._draw_single_formation(viz, 1, 50, 100, (width // 2) - 100, height - 150)
        
        # Draw team 2 formation (right side)
        self._draw_single_formation(viz, 2, (width // 2) + 50, 100, (width // 2) - 100, height - 150)
        
        return viz
    
    def _draw_single_formation(self, img, team_id, x, y, width, height):
        """Vẽ đội hình của một đội"""
        if team_id not in self.formation_data or not self.formation_data[team_id]['lines']:
            cv2.putText(img, f"Team {team_id}: No data", (x + 50, y + height // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
            return
        
        formation = self.formation_data[team_id]
        
        # Background field
        field_color = (60, 120, 40)
        cv2.rectangle(img, (x, y), (x + width, y + height), field_color, -1)
        cv2.rectangle(img, (x, y), (x + width, y + height), (255, 255, 255), 3)
        
        # Team name and formation
        cv2.putText(img, f"Team {team_id}", (x + 10, y + 30), 
                   cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(img, f"Formation: {formation['formation']}", (x + 10, y + 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # Draw players by lines
        lines = formation['lines']
        num_lines = len(lines)
        
        line_spacing = height // (num_lines + 1)
        
        for line_idx, line_players in enumerate(lines):
            line_y = y + line_spacing * (line_idx + 1)
            num_players_in_line = len(line_players)
            
            if num_players_in_line == 0:
                continue
            
            player_spacing = width // (num_players_in_line + 1)
            
            for player_idx, player_id in enumerate(line_players):
                player_x = x + player_spacing * (player_idx + 1)
                
                # Draw player
                player_color = (255, 200, 100) if team_id == 1 else (100, 255, 200)
                
                cv2.circle(img, (player_x, line_y), 20, (0, 0, 0), -1)
                cv2.circle(img, (player_x, line_y), 18, player_color, -1)
                cv2.circle(img, (player_x, line_y), 18, (255, 255, 255), 2)
                
                # Player ID
                text = str(player_id)
                text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)[0]
                text_x = player_x - text_size[0] // 2
                text_y = line_y + text_size[1] // 2
                cv2.putText(img, text, (text_x, text_y), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
    
    def export_to_dict(self):
        """
        Export dữ liệu ra dictionary
        Chỉ export top 11 cầu thủ mỗi đội
        """
        # Lọc top players
        filtered_players = self._get_top_players_per_team(max_per_team=11)
        
        # Chuyển defaultdict về dict thường
        passing_network_dict = {}
        for from_player, passes in self.passing_network.items():
            # Chỉ export passes giữa top players
            if from_player in filtered_players:
                filtered_passes = {
                    to_player: count 
                    for to_player, count in passes.items() 
                    if to_player in filtered_players
                }
                if filtered_passes:
                    passing_network_dict[from_player] = filtered_passes
        
        return {
            'passing_network': passing_network_dict,
            'formations': self.formation_data,
            'player_avg_positions': {
                pid: {
                    'team': data['team'],
                    'avg_x': float(data['avg_x']),
                    'avg_y': float(data['avg_y']),
                    'num_positions': len(data['positions'])
                }
                for pid, data in filtered_players.items()
            }
        }
