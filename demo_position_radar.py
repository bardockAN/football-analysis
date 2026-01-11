"""
Demo: Player Position Radar Visualization from Real Video
Integrates with main tracking pipeline to generate position radar visualizations
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from analytics.position_radar import PlayerPositionRadar
import numpy as np

def demo_position_radar_from_video(video_path, output_dir='output_videos/position_radar'):
    """
    Demo: Extract player positions from video and create radar visualizations
    
    Args:
        video_path: Path to input video
        output_dir: Output directory for visualizations
    """
    print("="*80)
    print("DEMO: PLAYER POSITION RADAR FROM VIDEO")
    print("="*80)
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"\nInput video: {video_path}")
    print(f"Output directory: {output_dir}")
    
    # Step 1: Read video
    print("\n[1/6] Reading video...")
    video_frames = read_video(video_path)
    print(f"    ✓ Loaded {len(video_frames)} frames")
    
    # Step 2: Initialize tracker
    print("\n[2/6] Initializing tracker...")
    tracker = Tracker('models/best.pt')
    
    # Get tracks for first 500 frames (sample for demo)
    sample_frames = min(500, len(video_frames))
    print(f"    → Processing {sample_frames} frames for demo...")
    
    # Use stub if available to avoid re-tracking
    stub_path = 'stubs/track_stubs.pkl'
    tracks = tracker.get_object_tracks(video_frames[:sample_frames], 
                                       read_from_stub=True,
                                       stub_path=stub_path)
    print("    ✓ Tracking completed")
    
    # Step 3: Assign teams
    print("\n[3/6] Assigning teams...")
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
    
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], 
                                                 track['bbox'], 
                                                 player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]
    
    print("    ✓ Teams assigned")
    
    # Step 3.5: Add positions from bboxes  
    print("\n[3.5/6] Calculating player positions...")
    for object_name in tracks.keys():
        for frame_num, frame_tracks in enumerate(tracks[object_name]):
            for track_id, track_info in frame_tracks.items():
                bbox = track_info['bbox']
                # Position is bottom-center of bbox
                position = [(bbox[0] + bbox[2])/2, bbox[3]]
                track_info['position_adjusted'] = position
    print("    ✓ Positions calculated")
    
    # Step 4: Transform positions to pitch coordinates
    print("\n[4/6] Transforming positions to pitch coordinates...")
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)
    print("    ✓ Position transformation completed")
    
    # Step 5: Create radar visualizations
    print("\n[5/6] Creating position radar visualizations...")
    radar = PlayerPositionRadar(pitch_length=105, pitch_width=68)
    
    frame_nums = list(range(sample_frames))
    results = radar.analyze_from_tracks(tracks, frame_nums, output_dir)
    
    print(f"    ✓ Analyzed {results['team1_positions']} Team 1 positions")
    print(f"    ✓ Analyzed {results['team2_positions']} Team 2 positions")
    
    # Step 6: Create tactical snapshot
    print("\n[6/6] Creating tactical snapshot...")
    
    # Get positions from middle of video
    mid_frame = sample_frames // 2
    team1_positions = []
    team2_positions = []
    
    if mid_frame in tracks['players']:
        for track_id, player_data in tracks['players'][mid_frame].items():
            if 'position_transformed' in player_data:
                x, y = player_data['position_transformed']
                team_id = player_data.get('team', 1)
                
                if team_id == 1:
                    team1_positions.append((x, y))
                else:
                    team2_positions.append((x, y))
        
        # Create tactical snapshot
        fig, ax = radar.create_position_plot(
            team1_positions, team2_positions,
            f"Team 1 ({len(team1_positions)} players)", 
            f"Team 2 ({len(team2_positions)} players)",
            title=f"Tactical Snapshot (Frame {mid_frame})"
        )
        fig.savefig(output_dir / 'tactical_snapshot.png', dpi=300, 
                   bbox_inches='tight', facecolor='#1e3d1e')
        print("    ✓ Saved: tactical_snapshot.png")
    
    # Create summary
    print("\n" + "="*80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"\nGenerated visualizations in: {output_dir}/")
    print("  → team1_heatmap.png - Team 1 position heatmap")
    print("  → team2_heatmap.png - Team 2 position heatmap")
    print("  → combined_positions.png - Combined tactical view")
    print("  → tactical_snapshot.png - Snapshot at mid-video")
    print(f"\nProcessed {sample_frames} frames from video")
    print(f"Total positions analyzed: {results['team1_positions'] + results['team2_positions']}")
    
    return results

def quick_demo():
    """Quick demo with sample data if no video available"""
    print("="*80)
    print("QUICK DEMO: POSITION RADAR (SAMPLE DATA)")
    print("="*80)
    
    output_dir = Path('output_videos/position_radar_quick_demo')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    radar = PlayerPositionRadar()
    
    # Generate sample positions
    print("\nGenerating sample tactical data...")
    
    # Team 1 attacking (4-3-3)
    team1_positions = []
    # Add some randomness around formation positions
    base_positions = [
        (10, 34), # GK
        (25, 10), (25, 24), (25, 44), (25, 58), # Defenders
        (50, 18), (50, 34), (50, 50), # Midfielders
        (75, 15), (75, 34), (75, 53)  # Forwards
    ]
    
    for _ in range(100):  # Multiple samples per position
        for x, y in base_positions:
            # Add noise
            x_noise = np.random.normal(0, 3)
            y_noise = np.random.normal(0, 2)
            team1_positions.append((x + x_noise, y + y_noise))
    
    # Team 2 defending (4-4-2)
    team2_positions = []
    base_positions_2 = [
        (95, 34), # GK
        (80, 10), (80, 24), (80, 44), (80, 58), # Defenders
        (60, 12), (60, 26), (60, 42), (60, 56), # Midfielders
        (40, 24), (40, 44)  # Forwards
    ]
    
    for _ in range(100):
        for x, y in base_positions_2:
            x_noise = np.random.normal(0, 3)
            y_noise = np.random.normal(0, 2)
            team2_positions.append((x + x_noise, y + y_noise))
    
    print("✓ Sample data generated")
    
    # Create visualizations
    print("\nCreating visualizations...")
    
    # Heatmaps
    fig, ax = radar.create_heatmap(team1_positions, 1, 
                                   title="Team 1 Position Heatmap (4-3-3)")
    fig.savefig(output_dir / 'demo_team1_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: demo_team1_heatmap.png")
    
    fig, ax = radar.create_heatmap(team2_positions, 2,
                                   title="Team 2 Position Heatmap (4-4-2)")
    fig.savefig(output_dir / 'demo_team2_heatmap.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: demo_team2_heatmap.png")
    
    # Combined view
    team1_sample = base_positions
    team2_sample = base_positions_2
    
    fig, ax = radar.create_position_plot(team1_sample, team2_sample,
                                        "Team 1 (4-3-3)", "Team 2 (4-4-2)",
                                        title="Tactical Comparison")
    fig.savefig(output_dir / 'demo_tactical_comparison.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: demo_tactical_comparison.png")
    
    print("\n" + "="*80)
    print("QUICK DEMO COMPLETED!")
    print("="*80)
    print(f"\nOutput directory: {output_dir}/")
    print("\nTo run with real video, use:")
    print("  python position_radar_demo_runner.py --video path/to/video.mp4")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Position Radar Demo')
    parser.add_argument('--video', type=str, default=None,
                       help='Path to input video')
    parser.add_argument('--quick', action='store_true',
                       help='Run quick demo with sample data')
    
    args = parser.parse_args()
    
    if args.quick or args.video is None:
        quick_demo()
    else:
        if Path(args.video).exists():
            demo_position_radar_from_video(args.video)
        else:
            print(f"Error: Video not found: {args.video}")
            print("Running quick demo instead...")
            quick_demo()
