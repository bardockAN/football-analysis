import cv2
import sys  # thêm đường dẫn thư mục cha để import module utils
sys.path.append('../')
from utils import measure_distance ,get_foot_position

class SpeedAndDistance_Estimator(): # lớp để ước lượng tốc độ và khoảng cách di chuyển của cầu thủ
    def __init__(self): 
        self.frame_window=5 # số khung hình để tính toán tốc độ và khoảng cách di chuyển
        self.frame_rate=24 # fps của video
    
    def add_speed_and_distance_to_tracks(self,tracks):
        total_distance= {}# dictionary để lưu tổng khoảng cách di chuyển cho từng đối tượng và track_id

        for object, object_tracks in tracks.items(): # duyệt qua từng loại đối tượng trong tracks
            if object == "ball" or object == "referees":
                continue  
            number_of_frames = len(object_tracks) # số khung hình có trong tracks của đối tượng hiện tại
            
            for frame_num in range(0,number_of_frames, self.frame_window): # duyệt qua các khung hình với bước nhảy là frame_window
                last_frame = min(frame_num+self.frame_window,number_of_frames-1 ) # khung hình cuối cùng trong cửa sổ hiện tại
                # min() để đảm bảo không vượt quá số khung hình có trong tracks
                # frame_num+self.frame_window là khung hình tiếp theo sau cửa sổ hiện tại
                # number_of_frames-1 là khung hình cuối cùng trong tracks (vì index bắt đầu từ 0)

                for track_id,_ in object_tracks[frame_num].items(): # duyệt qua từng track_id trong khung hình hiện tại
                    # Tìm vị trí bắt đầu (start_position) - ưu tiên position_transformed
                    start_position = None
                    start_frame_actual = frame_num
                    use_bbox_for_start = False
                    
                    for f in range(frame_num, min(frame_num + self.frame_window, number_of_frames)):
                        if track_id in object_tracks[f]:
                            pos = object_tracks[f][track_id].get('position_transformed')
                            if pos is not None:
                                start_position = pos
                                start_frame_actual = f
                                break
                    
                    # Nếu không có position_transformed, dùng foot position từ bbox
                    if start_position is None and track_id in object_tracks[frame_num]:
                        if 'bbox' in object_tracks[frame_num][track_id]:
                            bbox = object_tracks[frame_num][track_id]['bbox']
                            start_position = get_foot_position(bbox)
                            start_frame_actual = frame_num
                            use_bbox_for_start = True
                    
                    # Tìm vị trí kết thúc (end_position)
                    end_position = None
                    end_frame_actual = last_frame
                    use_bbox_for_end = False
                    
                    for f in range(last_frame, frame_num, -1):
                        if track_id in object_tracks[f]:
                            pos = object_tracks[f][track_id].get('position_transformed')
                            if pos is not None:
                                end_position = pos
                                end_frame_actual = f
                                break
                    
                    # Nếu không có position_transformed, dùng foot position từ bbox
                    if end_position is None:
                        for f in range(last_frame, frame_num, -1):
                            if track_id in object_tracks[f] and 'bbox' in object_tracks[f][track_id]:
                                bbox = object_tracks[f][track_id]['bbox']
                                end_position = get_foot_position(bbox)
                                end_frame_actual = f
                                use_bbox_for_end = True
                                break
                    
                    # Nếu không tìm thấy cả 2 position hoặc 2 position trùng nhau
                    if start_position is None or end_position is None or start_frame_actual >= end_frame_actual:
                        continue
                    
                    # Nếu dùng bbox position, khoảng cách tính bằng pixel cần scale xuống
                    # Giả sử 1 pixel ~ 0.1m (có thể điều chỉnh)
                    distance_covered = measure_distance(start_position, end_position)
                    if use_bbox_for_start or use_bbox_for_end:
                        distance_covered = distance_covered * 0.05  # Scale down vì là pixel position
                    
                    '''
                    logic đoạn này là:
                    1. Lấy vị trí bắt đầu và kết thúc của đối tượng trong cửa sổ khung hình hiện tại
                    2. Tính khoảng cách di chuyển giữa hai vị trí này   
                    3. Tính thời gian đã trôi qua giữa hai khung hình dựa trên frame_rate và số khung hình trong cửa sổ
                    4. Tính tốc độ di chuyển (m/s) và chuyển đổi sang km/h
                    5. Cập nhật tổng khoảng cách di chuyển cho đối tượng và track_id trong dictionary total_distance
                    6. Gán tốc độ và khoảng cách di chuyển cho từng khung hình trong cửa sổ hiện tại   
                    track_id là id của đối tượng được theo dõi (cầu thủ)
                    7. Cập nhật thông tin tốc độ và khoảng cách di chuyển vào tracks để sử dụng sau này
                    '''
                    # Nếu dùng bbox position, khoảng cách tính bằng pixel cần scale xuống
                    # Giả sử 1 pixel ~ 0.1m (có thể điều chỉnh)
                    distance_covered = measure_distance(start_position, end_position)
                    if use_bbox_for_start or use_bbox_for_end:
                        distance_covered = distance_covered * 0.05  # Scale down vì là pixel position
                    
                    time_elapsed = (end_frame_actual - start_frame_actual)/self.frame_rate # tính thời gian đã trôi qua giữa hai khung hình
                    
                    if time_elapsed == 0:  # Tránh chia cho 0
                        continue
                        
                    speed_meteres_per_second = distance_covered/time_elapsed # tính tốc độ di chuyển (m/s)
                    speed_km_per_hour = speed_meteres_per_second*3.6 # chuyển đổi tốc độ sang km/h

                    if object not in total_distance: # khởi tạo dictionary để lưu tổng khoảng cách di chuyển cho đối tượng nếu chưa tồn tại
                        total_distance[object]= {} # khởi tạo dictionary rỗng cho đối tượng 
                    
                    if track_id not in total_distance[object]: # khởi tạo tổng khoảng cách di chuyển cho track_id nếu chưa tồn tại
                        total_distance[object][track_id] = 0 # khởi tạo tổng khoảng cách di chuyển là 0
                    
                    total_distance[object][track_id] += distance_covered # cộng dồn khoảng cách di chuyển vào tổng khoảng cách


                    '''
                    vòng for bên dưới để gán tốc độ và khoảng cách di chuyển cho từng khung hình trong cửa sổ hiện tại
                    '''
                    for frame_num_batch in range(frame_num, last_frame + 1):  # +1 để bao gồm last_frame
                        if track_id not in tracks[object][frame_num_batch]:
                            continue
                        tracks[object][frame_num_batch][track_id]['speed'] = speed_km_per_hour
                        tracks[object][frame_num_batch][track_id]['distance'] = total_distance[object][track_id]
        
        # Sau khi tính toán xong, khởi tạo 0 cho các cầu thủ không có speed/distance
        for object, object_tracks in tracks.items():
            if object == "ball" or object == "referees":
                continue
            for frame_num in range(len(object_tracks)):
                for track_id in object_tracks[frame_num].keys():
                    if 'speed' not in object_tracks[frame_num][track_id]:
                        object_tracks[frame_num][track_id]['speed'] = 0.0
                    if 'distance' not in object_tracks[frame_num][track_id]:
                        object_tracks[frame_num][track_id]['distance'] = 0.0
    
    def draw_speed_and_distance(self,frames,tracks):
        ''''
        Hàm để vẽ tốc độ và khoảng cách di chuyển lên khung hình
        Logic đoạn này là:
        1. Duyệt qua từng khung hình và các đối tượng trong tracks
        2. Bỏ qua đối tượng là bóng và trọng tài
        3. Với mỗi đối tượng và track_id, kiểm tra nếu có thông tin về tốc độ và khoảng cách di chuyển
        4. Lấy bounding box của đối tượng và tính vị trí để vẽ thông tin (dưới chân cầu thủ)
        5. Sử dụng cv2.putText để vẽ tốc độ và khoảng cách di chuyển lên khung hình tại vị trí đã tính toán
        6. Trả về danh sách khung hình đã được vẽ thông tin
        
        '''
        output_frames = []
        for frame_num, frame in enumerate(frames):
            for object, object_tracks in tracks.items():
                if object == "ball" or object == "referees":
                    continue 
                for _, track_info in object_tracks[frame_num].items():
                    # _ là track_id, không sử dụng nên đặt là _
                    # Luôn vẽ speed và distance, ngay cả khi là 0
                    speed = track_info.get('speed', 0.0) # lấy tốc độ từ track_info, mặc định là 0
                    distance = track_info.get('distance', 0.0) # lấy khoảng cách từ track_info, mặc định là 0
                    
                    if 'bbox' not in track_info:
                        continue
                    
                    bbox = track_info['bbox'] 
                    position = get_foot_position(bbox)
                    position = list(position)
                    position[1]+=40 # dịch vị trí y xuống dưới 40 pixel để vẽ thông tin dưới chân cầu thủ

                    position = tuple(map(int,position)) # chuyển vị trí sang kiểu int để vẽ
                    cv2.putText(frame, f"{speed:.2f} km/h",position,cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2)
                    # FONT_HERSHEY_SIMPLEX là font chữ
                    # 0.5 là kích thước chữ
                    # (0,0,0) là màu chữ (đen)
                    # 2 là độ dày chữ
                    cv2.putText(frame, f"{distance:.2f} m",(position[0],position[1]+20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,0),2)
            output_frames.append(frame)
        
        return output_frames