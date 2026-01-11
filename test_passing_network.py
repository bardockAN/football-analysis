"""
Test script để kiểm tra passing network filtering
"""

import numpy as np
import cv2
from case_studies.tactical_analysis import TacticalAnalyzer

def test_passing_network_filtering():
    """Test filtering của passing network - chỉ hiển thị top players"""
    
    analyzer = TacticalAnalyzer()
    
    # Tạo dữ liệu giả với NHIỀU cầu thủ (hơn 11 mỗi đội)
    # Giả lập detection lỗi
    
    # Team 1: 15 cầu thủ (11 chính + 4 detection lỗi)
    team1_players = []
    for i in range(1, 12):  # 11 cầu thủ chính
        team1_players.append((i, 150 * i, 100 + i * 50, 100))  # pid, x, y, num_frames
    
    for i in range(12, 16):  # 4 detection lỗi (ít frames)
        team1_players.append((i, 200 + i * 10, 300, 5))
    
    # Team 2: 18 cầu thủ (11 chính + 7 detection lỗi)
    team2_players = []
    for i in range(101, 112):  # 11 cầu thủ chính
        team2_players.append((i, 1000 + (i-100) * 30, 200 + (i-100) * 40, 100))
    
    for i in range(112, 119):  # 7 detection lỗi
        team2_players.append((i, 900, 400 + i * 5, 3))
    
    # Tạo player_positions
    for team_id, players in [(1, team1_players), (2, team2_players)]:
        for pid, x, y, num_frames in players:
            analyzer.player_positions[pid] = {
                'team': team_id,
                'positions': [(x, y)] * num_frames,
                'avg_x': x,
                'avg_y': y
            }
    
    print("Testing Passing Network Filtering...")
    print("=" * 60)
    
    total_players = len(analyzer.player_positions)
    team1_total = sum(1 for p in analyzer.player_positions.values() if p['team'] == 1)
    team2_total = sum(1 for p in analyzer.player_positions.values() if p['team'] == 2)
    
    print(f"\nTotal players detected: {total_players}")
    print(f"  Team 1: {team1_total} players")
    print(f"  Team 2: {team2_total} players")
    
    # Test filtering
    filtered = analyzer._get_top_players_per_team(max_per_team=11)
    
    team1_filtered = sum(1 for p in filtered.values() if p['team'] == 1)
    team2_filtered = sum(1 for p in filtered.values() if p['team'] == 2)
    
    print(f"\nFiltered players (top 11 each team): {len(filtered)}")
    print(f"  Team 1: {team1_filtered} players")
    print(f"  Team 2: {team2_filtered} players")
    
    # Verify filtering worked correctly
    assert len(filtered) <= 22, "❌ Should have max 22 players"
    assert team1_filtered <= 11, "❌ Team 1 should have max 11 players"
    assert team2_filtered <= 11, "❌ Team 2 should have max 11 players"
    
    print("\n" + "=" * 60)
    print("✓ Filtering test passed!")
    
    # Test visualization creation
    print("\nCreating passing network visualization...")
    viz = analyzer.create_passing_network_viz()
    
    if viz is not None:
        print(f"✓ Visualization created: {viz.shape}")
        
        # Save test image
        output_path = "test_passing_network_filtered.png"
        cv2.imwrite(output_path, viz)
        print(f"✓ Saved to: {output_path}")
    else:
        print("❌ Failed to create visualization")
    
    print("\n" + "=" * 60)
    print("All tests completed!")

if __name__ == "__main__":
    test_passing_network_filtering()
