"""
Script để train YOLO model cho football player detection với GPU support
"""

import os
import shutil
import torch
from ultralytics import YOLO
from pathlib import Path

def check_gpu():
    """Kiểm tra GPU có sẵn không"""
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_count = torch.cuda.device_count()
        print(f"✅ GPU được phát hiện: {gpu_name}")
        print(f"✅ Số lượng GPU: {gpu_count}")
        print(f"✅ CUDA version: {torch.version.cuda}")
        return True, 0  # device=0
    else:
        print("⚠️  GPU không được phát hiện, sẽ sử dụng CPU")
        return False, 'cpu'

def train_with_local_dataset(dataset_path=None, model_name="yolov5x.pt", epochs=100, imgsz=640, batch=16):
    """
    Train YOLO model với dataset local
    
    Args:
        dataset_path: Đường dẫn đến thư mục dataset (hoặc None để tự động tìm)
        model_name: Model pretrained (yolov5n, yolov5s, yolov5m, yolov5l, yolov5x)
        epochs: Số epochs
        imgsz: Kích thước ảnh
        batch: Batch size (tăng lên nếu GPU mạnh)
    """
    # Kiểm tra GPU
    has_gpu, device = check_gpu()
    
    # Nếu có GPU, tăng batch size
    if has_gpu:
        batch = max(batch, 16)  # Tối thiểu 16 cho GPU
        print(f"📊 Batch size: {batch}")
    
    # Tìm dataset
    if dataset_path is None:
        # Tìm dataset trong thư mục training hoặc root
        possible_paths = [
            "training/football-players-detection-1",
            "football-players-detection-1",
            "dataset",
            "../dataset"
        ]
        
        for path in possible_paths:
            data_yaml = os.path.join(path, "data.yaml")
            if os.path.exists(data_yaml):
                dataset_path = path
                break
        
        if dataset_path is None:
            print("❌ Không tìm thấy dataset!")
            print("\nVui lòng:")
            print("1. Tải dataset và đặt vào thư mục 'dataset' hoặc 'training'")
            print("2. Hoặc chỉ định đường dẫn dataset_path khi gọi hàm")
            print("\nCấu trúc dataset cần có:")
            print("  dataset/")
            print("    ├── data.yaml")
            print("    ├── train/images")
            print("    ├── train/labels")
            print("    ├── valid/images")
            print("    └── valid/labels")
            return None
    
    # Đường dẫn đến data.yaml
    data_yaml = os.path.join(dataset_path, "data.yaml")
    
    if not os.path.exists(data_yaml):
        print(f"❌ Không tìm thấy data.yaml tại: {data_yaml}")
        return None
    
    # Kiểm tra cấu trúc dataset
    print(f"\n📁 Dataset path: {os.path.abspath(dataset_path)}")
    print(f"📄 Data config: {data_yaml}")
    
    # Load model
    print(f"\n🔄 Đang load model: {model_name}")
    model = YOLO(model_name)
    
    # Training parameters
    print(f"\n🚀 Bắt đầu training...")
    print(f"   Model: {model_name}")
    print(f"   Epochs: {epochs}")
    print(f"   Image size: {imgsz}")
    print(f"   Batch size: {batch}")
    print(f"   Device: {device}")
    
    try:
        # Train model
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            project='runs/detect',
            name='football_training',
            exist_ok=True,
            save=True,
            save_period=10,  # Lưu checkpoint mỗi 10 epochs
            patience=50,  # Early stopping sau 50 epochs không cải thiện
            plots=True,  # Tạo plots
            val=True,  # Validate trong lúc train
            verbose=True,  # Hiển thị chi tiết
        )
        
        print("\n✅ Training hoàn thành!")
        
        # Đường dẫn model tốt nhất
        best_model = "runs/detect/football_training/weights/best.pt"
        last_model = "runs/detect/football_training/weights/last.pt"
        
        if os.path.exists(best_model):
            # Copy model tốt nhất vào thư mục models
            target_dir = "models"
            os.makedirs(target_dir, exist_ok=True)
            target_path = os.path.join(target_dir, "best.pt")
            
            shutil.copy(best_model, target_path)
            print(f"\n📦 Model tốt nhất đã được copy tới: {target_path}")
            print(f"📦 Model cuối cùng tại: {last_model}")
            
            # Hiển thị metrics
            print("\n📊 Training metrics:")
            print(f"   Best model: {best_model}")
            print(f"   Last model: {last_model}")
            
        return results
        
    except Exception as e:
        print(f"\n❌ Lỗi khi training: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def train_with_roboflow(api_key=None, workspace="roboflow-jvuqo", project_name="football-players-detection-3zvbc", 
                        version=1, model_name="yolov5x.pt", epochs=100):
    """
    Train với dataset từ Roboflow (optional)
    """
    try:
        from roboflow import Roboflow
        
        if api_key is None:
            print("❌ Cần API key của Roboflow")
            print("   Lấy tại: https://roboflow.com/settings")
            return None
        
        print("📥 Đang tải dataset từ Roboflow...")
        rf = Roboflow(api_key=api_key)
        project = rf.workspace(workspace).project(project_name)
        version_obj = project.version(version)
        dataset = version_obj.download("yolov5")
        
        print(f"✅ Dataset đã tải tại: {dataset.location}")
        
        # Chuẩn bị cấu trúc dataset
        dataset_location = dataset.location
        if os.path.exists(os.path.join(dataset_location, 'train')):
            nested_path = os.path.join(dataset_location, os.path.basename(dataset_location))
            os.makedirs(nested_path, exist_ok=True)
            
            for folder in ['train', 'test', 'valid']:
                src = os.path.join(dataset_location, folder)
                dst = os.path.join(nested_path, folder)
                if os.path.exists(src) and not os.path.exists(dst):
                    shutil.move(src, dst)
        
        # Train với dataset đã tải
        return train_with_local_dataset(dataset_location, model_name, epochs)
        
    except ImportError:
        print("❌ Cần cài đặt roboflow: pip install roboflow")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("🏈 Football Player Detection - YOLO Training Script")
    print("=" * 60)
    
    # Chọn phương thức train
    print("\nChọn phương thức train:")
    print("1. Train với dataset local (đã có dataset)")
    print("2. Train với dataset từ Roboflow")
    
    choice = input("\nNhập lựa chọn (1 hoặc 2, Enter = 1): ").strip()
    
    if choice == "2":
        # Train với Roboflow
        api_key = input("Nhập Roboflow API key (Enter để bỏ qua): ").strip()
        if not api_key:
            print("⚠️  Bỏ qua Roboflow, chuyển sang dataset local")
            choice = "1"
        else:
            train_with_roboflow(api_key=api_key)
    
    if choice == "1" or choice == "":
        # Train với dataset local
        dataset_path = input("Nhập đường dẫn dataset (Enter để tự động tìm): ").strip()
        if not dataset_path:
            dataset_path = None
        
        # Cấu hình training
        model_name = input("Chọn model (yolov5n/s/m/l/x, Enter = yolov5x): ").strip()
        if not model_name:
            model_name = "yolov5x.pt"
        elif not model_name.endswith(".pt"):
            model_name = f"yolo{model_name}.pt" if not model_name.startswith("yolo") else f"{model_name}.pt"
        
        epochs_input = input("Số epochs (Enter = 100): ").strip()
        epochs = int(epochs_input) if epochs_input.isdigit() else 100
        
        batch_input = input("Batch size (Enter = 16): ").strip()
        batch = int(batch_input) if batch_input.isdigit() else 16
        
        # Bắt đầu train
        train_with_local_dataset(
            dataset_path=dataset_path,
            model_name=model_name,
            epochs=epochs,
            batch=batch
        )
    
    print("\n" + "=" * 60)
    print("✅ Hoàn thành!")
    print("=" * 60)