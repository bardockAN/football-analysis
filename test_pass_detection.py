"""
Test script để kiểm tra thuật toán phát hiện pass mới
"""

import numpy as np
from case_studies.tactical_analysis import TacticalAnalyzer

def test_pass_detection():
    """Test thuật toán phát hiện pass"""
    
    analyzer = TacticalAnalyzer()
    
    # Tạo dữ liệu giả với các pha chuyền bóng rõ ràng
    # Giả lập 100 frames với bóng di chuyển giữa 3 cầu thủ
    
    tracks = {
        'players': [],
        'ball': []
    }
    
    # Tạo 3 cầu thủ Team 1 và 3 cầu thủ Team 2
    for frame_num in range(100):
        player_frame = {}
        
        # Team 1 players (ID 1, 2, 3)
        player_frame[1] = {
            'team': 1,
            'position': (100, 100)
        }
        player_frame[2] = {
            'team': 1,
            'position': (300, 100)
        }
        player_frame[3] = {
            'team': 1,
            'position': (500, 100)
        }
        
        # Team 2 players (ID 101, 102, 103)
        player_frame[101] = {
            'team': 2,
            'position': (100, 400)
        }
        player_frame[102] = {
            'team': 2,
            'position': (300, 400)
        }
        player_frame[103] = {
            'team': 2,
            'position': (500, 400)
        }
        
        tracks['players'].append(player_frame)
        
        # Tạo ball frame
        ball_frame = {}
        
        # Bóng di chuyển giữa các cầu thủ Team 1
        if frame_num < 20:
            # Ball near player 1
            ball_frame[1] = {'bbox': [90, 90, 110, 110]}
        elif frame_num < 40:
            # Ball moving to player 2
            progress = (frame_num - 20) / 20
            ball_x = 100 + (300 - 100) * progress
            ball_frame[1] = {'bbox': [ball_x - 10, 90, ball_x + 10, 110]}
        elif frame_num < 50:
            # Ball near player 2
            ball_frame[1] = {'bbox': [290, 90, 310, 110]}
        elif frame_num < 70:
            # Ball moving to player 3
            progress = (frame_num - 50) / 20
            ball_x = 300 + (500 - 300) * progress
            ball_frame[1] = {'bbox': [ball_x - 10, 90, ball_x + 10, 110]}
        else:
            # Ball near player 3
            ball_frame[1] = {'bbox': [490, 90, 510, 110]}
        
        tracks['ball'].append(ball_frame)
    
    # Thêm vị trí cho player_positions
    for frame_num in range(100):
        for player_id, player_data in tracks['players'][frame_num].items():
            if player_id not in analyzer.player_positions:
                analyzer.player_positions[player_id] = {
                    'team': player_data['team'],
                    'positions': [],
                    'avg_x': 0,
                    'avg_y': 0
                }
            analyzer.player_positions[player_id]['positions'].append(player_data['position'])
    
    # Test phát hiện passes
    print("Testing Pass Detection...")
    print("=" * 60)
    
    # Chạy detection
    for frame_num in range(1, 100):
        analyzer._detect_pass(tracks, frame_num)
    
    # Kiểm tra kết quả
    print("\nDetected Passes:")
    total_passes = 0
    
    for from_player, passes in analyzer.passing_network.items():
        for to_player, count in passes.items():
            print(f"  Player {from_player} -> Player {to_player}: {count} passes")
            total_passes += count
    
    print(f"\nTotal passes detected: {total_passes}")
    
    # Expected: Ít nhất 2 passes (1->2 và 2->3)
    if total_passes >= 2:
        print("✓ Pass detection working!")
    else:
        print("❌ Too few passes detected!")
    
    print("=" * 60)

if __name__ == "__main__":
    test_pass_detection()
