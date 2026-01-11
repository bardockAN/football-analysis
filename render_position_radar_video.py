"""
Render video with Position Radar overlay
Creates output video with player positions visualized on pitch
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils import read_video, save_video
from trackers import Tracker
from team_assigner import TeamAssigner
from view_transformer import ViewTransformer
import cv2
import numpy as np
from collections import defaultdict

def draw_mini_pitch(frame, team1_positions, team2_positions, pitch_size=(200, 130)):
    """
    Draw mini pitch with player positions in corner of frame
    
    Args:
        frame: Video frame
        team1_positions: List of (x, y) normalized positions for team 1
        team2_positions: List of (x, y) normalized positions for team 2
        pitch_size: (width, height) of mini pitch
    """
    width, height = pitch_size
    
    # Create mini pitch background
    mini_pitch = np.zeros((height, width, 3), dtype=np.uint8)
    mini_pitch[:] = (34, 139, 34)  # Green pitch
    
    # Draw pitch outline
    cv2.rectangle(mini_pitch, (10, 10), (width-10, height-10), (255, 255, 255), 2)
    
    # Draw halfway line
    cv2.line(mini_pitch, (width//2, 10), (width//2, height-10), (255, 255, 255), 1)
    
    # Draw center circle
    cv2.circle(mini_pitch, (width//2, height//2), 15, (255, 255, 255), 1)
    
    # Draw penalty areas
    # Left penalty area
    cv2.rectangle(mini_pitch, (10, 40), (40, 90), (255, 255, 255), 1)
    # Right penalty area  
    cv2.rectangle(mini_pitch, (width-40, 40), (width-10, 90), (255, 255, 255), 1)
    
    # Plot team 1 positions (red)
    for x, y in team1_positions:
        if 0 <= x <= 105 and 0 <= y <= 68:
            # Convert to mini pitch coordinates
            px = int((x / 105) * (width - 20) + 10)
            py = int((y / 68) * (height - 20) + 10)
            cv2.circle(mini_pitch, (px, py), 3, (0, 0, 255), -1)  # Red
            cv2.circle(mini_pitch, (px, py), 4, (255, 255, 255), 1)  # White outline
    
    # Plot team 2 positions (blue)
    for x, y in team2_positions:
        if 0 <= x <= 105 and 0 <= y <= 68:
            px = int((x / 105) * (width - 20) + 10)
            py = int((y / 68) * (height - 20) + 10)
            cv2.circle(mini_pitch, (px, py), 3, (255, 0, 0), -1)  # Blue
            cv2.circle(mini_pitch, (px, py), 4, (255, 255, 255), 1)  # White outline
    
    # Position in top-right corner
    y_offset = 20
    x_offset = frame.shape[1] - width - 20
    
    # Add semi-transparent background
    overlay = frame.copy()
    cv2.rectangle(overlay, (x_offset-5, y_offset-5), 
                 (x_offset+width+5, y_offset+height+5), 
                 (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    
    # Place mini pitch on frame
    frame[y_offset:y_offset+height, x_offset:x_offset+width] = mini_pitch
    
    # Add border
    cv2.rectangle(frame, (x_offset-2, y_offset-2), 
                 (x_offset+width+2, y_offset+height+2), 
                 (255, 255, 255), 2)
    
    # Add labels
    cv2.putText(frame, "Tactical View", 
               (x_offset, y_offset-10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    return frame

def draw_position_trails(frame, position_history, max_trail=30):
    """
    Draw trails showing player movement
    
    Args:
        frame: Video frame
        position_history: Dict of {track_id: [(x, y), ...]}
        max_trail: Maximum trail length
    """
    for track_id, positions in position_history.items():
        if len(positions) < 2:
            continue
        
        # Draw trail with fading effect
        for i in range(len(positions) - 1):
            alpha = (i + 1) / len(positions)
            thickness = max(1, int(2 * alpha))
            
            pt1 = tuple(map(int, positions[i]))
            pt2 = tuple(map(int, positions[i + 1]))
            
            cv2.line(frame, pt1, pt2, (255, 255, 0), thickness)
    
    return frame

def render_position_radar_video(video_path, output_path, max_frames=None):
    """
    Render video with position radar overlay
    
    Args:
        video_path: Input video path
        output_path: Output video path
        max_frames: Maximum frames to process (None for all)
    """
    print("="*80)
    print("RENDERING VIDEO WITH POSITION RADAR")
    print("="*80)
    
    print(f"\nInput: {video_path}")
    print(f"Output: {output_path}")
    
    # Step 1: Read video
    print("\n[1/5] Reading video...")
    video_frames = read_video(video_path)
    
    if max_frames:
        video_frames = video_frames[:max_frames]
    
    print(f"    ✓ Loaded {len(video_frames)} frames")
    
    # Step 2: Track objects
    print("\n[2/5] Tracking players...")
    tracker = Tracker('models/best.pt')
    tracks = tracker.get_object_tracks(video_frames, 
                                       read_from_stub=True,
                                       stub_path='stubs/track_stubs.pkl')
    print("    ✓ Tracking completed")
    
    # Step 3: Assign teams
    print("\n[3/5] Assigning teams...")
    team_assigner = TeamAssigner()
    team_assigner.assign_team_color(video_frames[0], tracks['players'][0])
    
    for frame_num in range(len(video_frames)):
        if frame_num >= len(tracks['players']):
            break
        
        player_track = tracks['players'][frame_num]
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], 
                                                 track['bbox'], 
                                                 player_id)
            tracks['players'][frame_num][player_id]['team'] = team
    
    print("    ✓ Teams assigned")
    
    # Step 4: Calculate positions and transform
    print("\n[4/5] Calculating positions...")
    
    # Add positions from bboxes
    for object_name in tracks.keys():
        for frame_num, frame_tracks in enumerate(tracks[object_name]):
            for track_id, track_info in frame_tracks.items():
                bbox = track_info['bbox']
                position = [(bbox[0] + bbox[2])/2, bbox[3]]
                track_info['position_adjusted'] = position
    
    # Transform to pitch coordinates
    view_transformer = ViewTransformer()
    view_transformer.add_transformed_position_to_tracks(tracks)
    
    print("    ✓ Positions calculated")
    
    # Step 5: Render frames with overlay
    print("\n[5/5] Rendering video with position overlay...")
    
    output_frames = []
    position_history = defaultdict(list)
    
    for frame_num, frame in enumerate(video_frames):
        if frame_num % 50 == 0:
            print(f"    Processing frame {frame_num}/{len(video_frames)}...")
        
        frame_copy = frame.copy()
        
        # Collect positions for this frame
        team1_positions = []
        team2_positions = []
        
        # Debug counters
        total_tracked = 0
        total_transformed = 0
        
        if frame_num < len(tracks['players']):
            total_tracked = len(tracks['players'][frame_num])
            
            for track_id, player_data in tracks['players'][frame_num].items():
                # Draw bbox and team color
                bbox = player_data['bbox']
                team = player_data.get('team', 1)
                
                # Draw bbox
                x1, y1, x2, y2 = map(int, bbox)
                color = (0, 0, 255) if team == 1 else (255, 0, 0)
                cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
                
                # Draw track ID
                cv2.putText(frame_copy, f"ID:{track_id}", 
                           (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # Get transformed position
                if 'position_transformed' in player_data and player_data['position_transformed'] is not None:
                    pos = player_data['position_transformed']
                    total_transformed += 1
                    
                    if team == 1:
                        team1_positions.append(pos)
                    else:
                        team2_positions.append(pos)
                    
                    # Track history for trails
                    position_history[track_id].append(((x1+x2)//2, y2))
                    if len(position_history[track_id]) > 30:
                        position_history[track_id].pop(0)
        
        # Draw position trails (optional)
        # frame_copy = draw_position_trails(frame_copy, position_history)
        
        # Draw mini pitch with positions
        frame_copy = draw_mini_pitch(frame_copy, team1_positions, team2_positions)
        
        # Add frame info with debug stats
        info_text = f"Frame: {frame_num} | Tracked: {total_tracked} | Transformed: {total_transformed} | T1: {len(team1_positions)} T2: {len(team2_positions)}"
        cv2.putText(frame_copy, info_text, 
                   (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        output_frames.append(frame_copy)
    
    print("    ✓ All frames rendered")
    
    # Check frames before saving
    if len(output_frames) == 0:
        print("    ❌ ERROR: No frames to save!")
        return
    
    print(f"    📊 Frame dimensions: {output_frames[0].shape}")
    print(f"    📊 Total frames to save: {len(output_frames)}")
    
    # Save video
    print(f"\n[6/6] Saving video to {output_path}...")
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"    ✓ Output directory: {output_dir}")
    
    try:
        save_video(output_frames, output_path)
        
        # Verify file was created
        if Path(output_path).exists():
            file_size = Path(output_path).stat().st_size / (1024*1024)  # MB
            print(f"    ✓ Video saved successfully! Size: {file_size:.2f} MB")
        else:
            print(f"    ❌ ERROR: Video file was not created at {output_path}")
            return
    except Exception as e:
        print(f"    ❌ ERROR saving video: {e}")
        return
    
    print("\n" + "="*80)
    print("VIDEO RENDERING COMPLETED!")
    print("="*80)
    print(f"\nOutput video: {output_path}")
    print(f"Total frames: {len(output_frames)}")
    print(f"\nYou can now play the video in VLC!")

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Render video with position radar')
    parser.add_argument('--input', type=str, 
                       default='input_videos/08fd33_4.mp4',
                       help='Input video path')
    parser.add_argument('--output', type=str,
                       default='output_videos/position_radar/output_with_radar.avi',
                       help='Output video path')
    parser.add_argument('--frames', type=int, default=500,
                       help='Max frames to process (default: 500 = ~20 seconds at 24fps)')
    
    args = parser.parse_args()
    
    # Create output directory
    Path(args.output).parent.mkdir(exist_ok=True, parents=True)
    
    render_position_radar_video(args.input, args.output, args.frames)
