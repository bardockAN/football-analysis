# ⚽ Football Analysis System

An advanced computer vision system for football match analysis using YOLOv11, featuring player detection, tracking, team assignment, and tactical visualization.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Detection-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## 📋 Features

- **🎯 Player Detection**: YOLOv11-based detection for players, goalkeepers, referees, and ball
- **📍 Player Tracking**: ByteTrack algorithm for robust multi-object tracking  
- **👕 Team Assignment**: K-means clustering for automatic team color identification
- **⚡ Speed & Distance**: Real-time estimation of player movement metrics
- **📊 Position Radar**: Tactical visualization with mini-pitch overlay
- **🎥 Camera Motion**: Perspective transformation and camera movement estimation
- **📈 Analytics**: Comprehensive player statistics and tactical insights

## 🚀 Quick Start

### Prerequisites

```bash
Python 3.8+
CUDA-capable GPU (recommended)
8GB+ RAM
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/football_analysis.git
cd football-analysis
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download the dataset** (for training)
```bash
# The FutVAR dataset structure should be:
# FutVAR-Football-Players-Detection-Dataset-10/
#   ├── train/
#   ├── valid/
#   ├── test/
#   └── data.yaml
```

Download from: [FutVAR Dataset on Roboflow]([https://universe.roboflow.com/futvar/football-players-detection](https://universe.roboflow.com/ranjit-raut-do9me/futvar-football-players-detection-dataset/dataset/10))

5. **Download pretrained model**
```bash
# Place your trained model weights in models/
# Or download from releases:
# https://github.com/YOUR_USERNAME/football_analysis/releases
```

## 💻 Usage

### 1. Basic Analysis (Detection + Tracking)

```bash
python main.py --input input_videos/your_video.mp4
```

Output:
- `output_videos/output_video.avi` - Annotated video with detections
- `output_videos/player_stats.csv` - Player statistics

### 2. Position Radar Visualization

```bash
python render_position_radar_video.py --input input_videos/your_video.mp4 --frames 500
```

Output:
- `output_videos/position_radar/output_with_radar.avi` - Video with tactical overlay

### 3. Training Your Own Model

```bash
cd training
python download_and_train.py
```

Configuration in `training/download_and_train.py`:
```python
model.train(
    data='../FutVAR-Football-Players-Detection-Dataset-10/data.yaml',
    epochs=100,
    imgsz=640,
    batch=16
)
```

### 4. Model Evaluation

```bash
python evaluate_model.py
```

Output:
- `evaluation_results/model_evaluation_*.json` - Performance metrics
- mAP@0.5, mAP@0.5:0.95, Precision, Recall

### 5. Generate Comparison Charts

```bash
cd evaluation_results
python generate_comparison_charts.py
```

Output: Visualization charts for presentation

## 📁 Project Structure

```
football_analysis/
├── main.py                          # Main analysis pipeline
├── render_position_radar_video.py   # Position radar visualization
├── evaluate_model.py                # Model evaluation
├── yolo_inference.py                # YOLO inference wrapper
│
├── trackers/                        # ByteTrack implementation
├── team_assigner/                   # Team color clustering
├── player_ball_assigner/            # Ball possession logic
├── camera_movement_estimator/       # Camera motion tracking
├── view_transformer/                # Perspective transformation
├── speed_and_distance_estimator/    # Movement metrics
├── player_stats_analyzer/           # Statistics computation
├── analytics/                       # Advanced analytics & reports
│
├── training/                        # Training scripts
│   └── download_and_train.py
│
├── models/                          # Model weights
│   └── best.pt                      # Trained YOLOv11 model
│
├── evaluation_results/              # Evaluation outputs
│   ├── paper_comparison_real.json
│   ├── references_real.bib
│   └── *.png                        # Charts & visualizations
│
├── input_videos/                    # Input video files
├── output_videos/                   # Generated outputs
│
└── requirements.txt                 # Python dependencies
```

## 📊 Model Performance

### YOLOv11 (Custom Trained on FutVAR Dataset)

| Metric | Score |
|--------|-------|
| mAP@0.5 | **48.1%** |
| mAP@0.5:0.95 | 19.6% |
| Precision | 54.0% |
| Recall | 50.4% |

**Dataset**: FutVAR Football Players Detection (4 classes: player, goalkeeper, referee, ball)

## 🎯 Use Cases

1. **Match Analysis**: Automated player tracking and movement analysis
2. **Tactical Insights**: Formation detection and positioning heatmaps
3. **Performance Metrics**: Speed, distance covered, possession statistics
4. **Video Annotation**: Automated highlight generation
5. **Scouting**: Player performance evaluation

## 📝 Citation

If you use this project in your research, please cite:

```bibtex
@software{football_analysis2026,
  author = {Bui Dang Quoc An, Pham Thai Duong, Pham Tien Dat, Tran Le Khanh Duy},
  title = {Football Analysis System with YOLOv11},
  year = {2026},
  url = {https://github.com/YOUR_USERNAME/football_analysis}
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics) - Object detection framework
- [ByteTrack](https://github.com/ifzhang/ByteTrack) - Multi-object tracking
- [FutVAR Dataset](https://universe.roboflow.com/futvar/football-players-detection) - Training dataset


## 📧 Contact

For questions or issues, please open an issue on GitHub.

---

⭐ If you find this project useful, please consider giving it a star!
