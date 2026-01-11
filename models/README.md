# Model Weights

## Download Pretrained Model

Due to file size limitations, model weights are not included in the repository.

### Option 1: Download from GitHub Releases

1. Go to: `https://github.com/YOUR_USERNAME/football-analysis/releases`
2. Download `best.pt` from the latest release
3. Place it in this directory: `models/best.pt`

### Option 2: Train Your Own Model

```bash
cd training
python download_and_train.py
```

The trained model will be saved automatically to `models/best.pt`

## Model Information

- **Architecture**: YOLOv11
- **Classes**: 4 (player, goalkeeper, referee, ball)
- **Dataset**: FutVAR Football Players Detection
- **Performance**: 
  - mAP@0.5: 48.1%
  - Precision: 54.0%
  - Recall: 50.4%

## File Structure

```
models/
├── best.pt          # Main trained model (download separately)
└── .gitkeep        # Keeps directory in git
```

## Usage

Once you have `best.pt` in this directory, you can run:

```bash
python main.py --input input_videos/your_video.mp4
```

The system will automatically load the model from `models/best.pt`.
