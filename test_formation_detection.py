"""
Test script để kiểm tra thuật toán phát hiện đội hình mới
"""

import numpy as np
from case_studies.tactical_analysis import TacticalAnalyzer

def test_formation_detection():
    """Test thuật toán phát hiện đội hình"""
    
    analyzer = TacticalAnalyzer()
    
    # Tạo dữ liệu giả với 11 cầu thủ cho mỗi đội
    # Đội hình 4-4-2: 1 GK, 4 defenders, 4 midfielders, 2 forwards
    
    # Team 1: 4-4-2 formation
    team1_positions = [
        # Goalkeeper
        (1, 100, 400),
        # Defenders (4)
        (2, 200, 300), (3, 200, 400), (4, 200, 500), (5, 200, 600),
        # Midfielders (4)
        (6, 400, 300), (7, 400, 400), (8, 400, 500), (9, 400, 600),
        # Forwards (2)
        (10, 600, 400), (11, 600, 500)
    ]
    
    # Team 2: 4-3-3 formation
    team2_positions = [
        # Goalkeeper
        (101, 800, 400),
        # Defenders (4)
        (102, 700, 300), (103, 700, 400), (104, 700, 500), (105, 700, 600),
        # Midfielders (3)
        (106, 500, 350), (107, 500, 450), (108, 500, 550),
        # Forwards (3)
        (109, 300, 350), (110, 300, 450), (111, 300, 550)
    ]
    
    # Tạo player_positions
    for team_id, positions in [(1, team1_positions), (2, team2_positions)]:
        for pid, x, y in positions:
            analyzer.player_positions[pid] = {
                'team': team_id,
                'positions': [(x, y)] * 100,  # Giả lập 100 frames
                'avg_x': x,
                'avg_y': y
            }
    
    # Test phát hiện đội hình
    print("Testing Formation Detection...")
    print("-" * 50)
    
    for team_id in [1, 2]:
        formation = analyzer._detect_formation(team_id)
        print(f"\nTeam {team_id}:")
        print(f"  Formation: {formation['formation']}")
        print(f"  Number of players: {formation['num_players']}")
        print(f"  Lines: {len(formation['lines'])} lines")
        for i, line in enumerate(formation['lines']):
            print(f"    Line {i+1}: {len(line)} players - {line}")
    
    print("\n" + "=" * 50)
    print("✓ Test completed successfully!")
    
    # Test normalize formation
    print("\nTesting Formation Normalization...")
    print("-" * 50)
    
    test_cases = [
        ([3, 4, 3], 10, "Should normalize to 3-4-3"),
        ([5, 3, 2], 10, "Should normalize to 5-3-2"),
        ([4, 5, 1], 10, "Should normalize to 4-5-1"),
        ([2, 7, 1], 10, "Should normalize to closest common formation"),
    ]
    
    for line_counts, total, description in test_cases:
        result = analyzer._normalize_formation(line_counts, total)
        print(f"\n{description}")
        print(f"  Input:  {'-'.join(map(str, line_counts))} ({sum(line_counts)} players)")
        print(f"  Output: {'-'.join(map(str, result))} ({sum(result)} players)")

if __name__ == "__main__":
    test_formation_detection()
