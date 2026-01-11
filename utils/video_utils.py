import cv2
import os

def read_video(video_path):
    # Kiểm tra file có tồn tại không
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"❌ Không tìm thấy video tại: {video_path}")
    
    cap = cv2.VideoCapture(video_path) # mở video
    
    # Kiểm tra xem video có mở được không
    if not cap.isOpened():
        raise ValueError(f"❌ Không thể mở video: {video_path}. File có thể bị hỏng hoặc định dạng không được hỗ trợ.")
    
    frames = [] # danh sách lưu trữ các khung hình
    while True: # tạo vòng lặp vô hạn, sẽ break sau khi hết video
        ret, frame = cap.read() # đọc từng khung hình, ret là biến boolean báo hiệu có đọc được khung hình hay không
        # frame là khung hình được đọc
        if not ret: # nếu không đọc được khung hình, tức là đã hết video
            break # thoát khỏi vòng lặp
        frames.append(frame) # thêm khung hình vào danh sách
    
    cap.release() # giải phóng bộ nhớ
    
    # Kiểm tra có đọc được frame nào không
    if len(frames) == 0:
        raise ValueError(f"❌ Không đọc được frame nào từ video: {video_path}")
    
    print(f"✅ Đã đọc thành công {len(frames)} frames từ video: {video_path}")
    return frames # trả về danh sách các khung hình

def save_video(ouput_video_frames,output_video_path): # lưu video từ danh sách các khung hình
    fourcc = cv2.VideoWriter_fourcc(*'XVID') # định dạng video
    # fourcc là mã bốn ký tự xác định codec video
    out = cv2.VideoWriter(output_video_path, fourcc, 24, (ouput_video_frames[0].shape[1], ouput_video_frames[0].shape[0]))
    #tạo đối tượng VideoWriter để ghi video
    # 24 là fps, (width,height) là kích thước khung hình
    for frame in ouput_video_frames:
        out.write(frame)
    out.release() # giải phóng bộ nhớ sau khi ghi xong video
