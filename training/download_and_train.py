"""
Script để download dataset và train YOLO model cho football detection
"""

import os
import shutil
from roboflow import Roboflow

def download_dataset():
    """Download dataset từ Roboflow"""
    print("=" * 60)
    print("BƯỚC 1: DOWNLOAD DATASET TỪ ROBOFLOW")
    print("=" * 60)
    
    # Khởi tạo Roboflow
    # LƯU Ý: API key này đã bị revoked, bạn cần lấy API key mới từ roboflow.com
    rf = Roboflow(api_key="GQIA6rop9OXhYVo449wA")
    
    print("\n✅ Đang kết nối với Roboflow...")
    project = rf.workspace("roboflow-jvuqo").project("football-players-detection-3zvbc")
    version = project.version(1)
    
    print("✅ Đang download dataset (có thể mất vài phút)...")
    dataset = version.download("yolov5")
    
    print(f"\n✅ Dataset đã được download tại: {dataset.location}")
    
    return dataset

def reorganize_dataset(dataset):
    """Tổ chức lại cấu trúc thư mục dataset"""
    print("\n" + "=" * 60)
    print("BƯỚC 2: TỔ CHỨC LẠI CẤU TRÚC DATASET")
    print("=" * 60)
    
    base_path = 'football-players-detection-1'
    nested_path = os.path.join(base_path, 'football-players-detection-1')
    
    # Tạo thư mục nested nếu chưa có
    os.makedirs(nested_path, exist_ok=True)
    
    # Di chuyển các thư mục
    folders = ['train', 'test', 'valid']
    for folder in folders:
        src = os.path.join(base_path, folder)
        dst = os.path.join(nested_path, folder)
        
        if os.path.exists(src) and not os.path.exists(dst):
            print(f"✅ Di chuyển {folder}/ vào cấu trúc mới...")
            shutil.move(src, dst)
        else:
            print(f"⚠️  {folder}/ đã tồn tại hoặc không cần di chuyển")
    
    print("\n✅ Cấu trúc dataset đã được tổ chức lại!")

def train_model(dataset):
    """Train YOLO model"""
    print("\n" + "=" * 60)
    print("BƯỚC 3: TRAINING MODEL")
    print("=" * 60)
    
    data_yaml = os.path.join(dataset.location, "data.yaml")
    
    print(f"\n📊 Cấu hình training:")
    print(f"   - Model: yolov5x.pt (pretrained)")
    print(f"   - Data config: {data_yaml}")
    print(f"   - Epochs: 100")
    print(f"   - Image size: 640")
    print(f"\n🚀 Bắt đầu training (có thể mất vài giờ)...\n")
    
    # Chạy lệnh train
    command = f'yolo task=detect mode=train model=yolov5x.pt data={data_yaml} epochs=100 imgsz=640'
    
    print(f"Lệnh chạy: {command}\n")
    os.system(command)
    
    print("\n✅ Training hoàn tất!")
    print("📁 Model được lưu tại: runs/detect/train/weights/best.pt")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("FOOTBALL PLAYER DETECTION - DOWNLOAD & TRAIN")
    print("=" * 60)
    
    try:
        # Bước 1: Download dataset
        dataset = download_dataset()
        
        # Bước 2: Tổ chức lại cấu trúc
        reorganize_dataset(dataset)
        
        # Bước 3: Train model
        train_model(dataset)
        
        print("\n" + "=" * 60)
        print("✅ HOÀN THÀNH TẤT CẢ CÁC BƯỚC!")
        print("=" * 60)
        print("\nBước tiếp theo:")
        print("1. Copy model: runs/detect/train/weights/best.pt")
        print("2. Dán vào: models/best.pt")
        print("3. Chạy: python main.py để phân tích video")
        
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        print("\nLƯU Ý:")
        print("- Nếu lỗi API key: Đăng ký tại roboflow.com để lấy API key mới")
        print("- Nếu lỗi module: Chạy 'pip install ultralytics roboflow'")

if __name__ == "__main__":
    main()
