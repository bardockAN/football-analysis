# Input Videos

Due to file size limitations, sample videos are not included in this repository.

## How to Add Your Video

1. Place your football match video in this directory
2. Supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`
3. Recommended resolution: 1080p or higher
4. File naming: Use descriptive names (e.g., `match_2024_team1_vs_team2.mp4`)

## Sample Video

You can use any football match video. For testing, try:
- YouTube videos (download with youtube-dl or similar)
- Your own recorded matches
- Public domain football footage

## Usage

```bash
# Run analysis on your video
python main.py --input input_videos/your_video.mp4

# Or with position radar
python render_position_radar_video.py --input input_videos/your_video.mp4
```

## Note

The repository includes one sample video for demonstration purposes. For production use, add your own videos here.
