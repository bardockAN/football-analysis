import pickle
import cv2
import numpy as np
import os
import sys 
sys.path.append('../')
from utils import measure_distance,measure_xy_distance

class CameraMovementEstimator(): # lớp để ước lượng chuyển động của camera
    '''
    Lớp này sử dụng thuật toán Lucas-Kanade Optical Flow để ước lượng chuyển động của camera giữa các khung hình trong video.
    Quá trình hoạt động của lớp này bao gồm các bước chính sau:
    1. Khởi tạo các tham số cần thiết cho thuật toán Lucas-Kanade Optical Flow, bao gồm kích thước cửa sổ, mức độ phân cấp và tiêu chí dừng.
    2. Chuyển đổi khung hình đầu tiên sang thang độ xám và xác định các điểm đặc trưng (features) trong khung hình này để theo dõi.
    3. Duyệt qua từng khung hình trong video, chuyển đổi chúng sang thang độ xám và sử dụng thuật toán Lucas-Kanade để tính toán vị trí mới của các điểm đặc trưng trong khung hình hiện tại.
    4. Tính toán khoảng cách di chuyển của các điểm đặc trưng và xác định chuyển động của camera dựa trên điểm có khoảng cách di chuyển lớn nhất.
    5. Cập nhật vị trí của các điểm đặc trưng và khung hình trước để sử dụng trong vòng lặp tiếp theo.
    6. Lưu trữ và trả về danh sách chuyển động của camera cho từng khung hình trong video.
    7. Cung cấp phương thức để vẽ thông tin chuyển động của camera lên các khung hình.
    
    '''
    def __init__(self,frame):
        '''
        logic đoạn này là:
        1. Khởi tạo các tham số cần thiết cho thuật toán Lucas-Kanade Optical Flow, bao gồm kích thước cửa sổ, mức độ phân cấp và tiêu chí dừng.
        2. Tạo mặt nạ để giới hạn khu vực tìm kiếm các điểm đặc trưng, tránh các vùng không mong muốn như biên của khung hình.
        3. Cấu hình các tham số để xác định các điểm đặc trưng trong khung hình đầu tiên.
        4. Chuyển đổi khung hình đầu tiên sang thang độ xám để chuẩn bị cho việc theo dõi các điểm đặc trưng.
        5. Xác định các điểm đặc trưng trong khung hình đầu tiên sử dụng các tham số đã cấu hình.

        '''
        self.minimum_distance = 5

        self.lk_params = dict(
            winSize = (15,15),
            maxLevel = 2,
            criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,0.03)
        ) # tham số cho thuật toán Lucas-Kanade Optical Flow

        # Tạo mặt nạ để giới hạn khu vực tìm kiếm các điểm đặc trưng
        first_frame_grayscale = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        mask_features = np.zeros_like(first_frame_grayscale) #
        mask_features[:,0:20] = 1
        mask_features[:,900:1050] = 1

        self.features = dict(
            maxCorners = 100,
            qualityLevel = 0.3,
            minDistance =3,
            blockSize = 7,
            mask = mask_features
        ) # tạo mặt nạ để tránh các vùng không mong muốn như biên của khung hình

    def add_adjust_positions_to_tracks(self,tracks, camera_movement_per_frame): # hàm để điều chỉnh vị trí các đối tượng trong tracks dựa trên chuyển động camera
        '''
        logic hàm này là:
        1. Duyệt qua từng loại đối tượng trong tracks (ví dụ: cầu thủ, bóng).
        2. Với mỗi khung hình và từng đối tượng trong khung hình đó, lấy vị trí ban đầu của đối tượng.
        3. Lấy chuyển động của camera tại khung hình hiện tại từ danh sách camera_movement_per_frame.
        4. Tính toán vị trí đã được điều chỉnh của đối tượng bằng cách trừ chuyển động của camera khỏi vị trí ban đầu.
        5. Lưu trữ vị trí đã được điều chỉnh vào tracks để sử dụng sau này.
        '''
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info['position'] # vị trí ban đầu của đối tượng
                    camera_movement = camera_movement_per_frame[frame_num] # chuyển động của camera tại khung hình hiện tại
                    position_adjusted = (position[0]-camera_movement[0],position[1]-camera_movement[1]) # vị trí đã được điều chỉnh của đối tượng
                    # (x,y) của vị trí ban đầu trừ đi (x,y) của chuyển động camera
                    tracks[object][frame_num][track_id]['position_adjusted'] = position_adjusted
                    


    def get_camera_movement(self,frames,read_from_stub=False, stub_path=None): # hàm để ước lượng chuyển động camera giữa các khung hình trong video
        '''
        logic đoạn này là:
        1. Kiểm tra nếu có đọc từ stub không, nếu có và file stub tồn tại thì đọc dữ liệu chuyển động camera từ file stub và trả về.
        2. Khởi tạo danh sách camera_movement để lưu chuyển động camera cho từng khung hình, ban đầu tất cả đều là (0,0).
        3. Chuyển đổi khung hình đầu tiên sang thang độ xám và xác định các điểm đặc trưng trong khung hình này để theo dõi.
        4. Duyệt qua từng khung hình trong video, chuyển đổi chúng sang thang độ xám và sử dụng thuật toán Lucas-Kanade để tính toán vị trí mới của các điểm đặc trưng trong khung hình hiện tại.
        5. Tính toán khoảng cách di chuyển của các điểm đặc trưng và xác định chuyển động của camera dựa trên điểm có khoảng cách di chuyển lớn nhất.
        6. Nếu khoảng cách di chuyển lớn hơn ngưỡng minimum_distance, cập nhật chuyển động camera cho khung hình hiện tại và xác định lại các điểm đặc trưng để theo dõi.       
        7. Cập nhật khung hình trước để sử dụng trong vòng lặp tiếp theo.
        8. Lưu trữ dữ liệu chuyển động camera vào file stub nếu đường dẫn stub_path được cung cấp.
        9. Trả về danh sách chuyển động camera cho từng khung hình trong video.
        
        '''
        # Read the stub 
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                return pickle.load(f)

        camera_movement = [[0,0]]*len(frames) # khởi tạo danh sách chuyển động camera cho từng khung hình, ban đầu tất cả đều là (0,0)

        old_gray = cv2.cvtColor(frames[0],cv2.COLOR_BGR2GRAY) # chuyển đổi khung hình đầu tiên sang thang độ xám
        old_features = cv2.goodFeaturesToTrack(old_gray,**self.features) # xác định các điểm đặc trưng trong khung hình đầu tiên để theo dõi

        
        # lặp qua từng khung hình trong video
        '''
        logic phần này lặp qua từng khung hình trong video để ước lượng chuyển động camera giữa các khung hình:
        1. Chuyển đổi khung hình hiện tại sang thang độ xám
        2. Sử dụng thuật toán Lucas-Kanade để tính toán vị trí mới của các điểm đặc trưng trong khung hình hiện tại
        3. Tính toán khoảng cách di chuyển của các điểm đặc trưng và xác định chuyển động của camera dựa trên điểm có khoảng cách di chuyển lớn nhất
        4. Nếu khoảng cách di chuyển lớn hơn ngưỡng minimum_distance, cập nhật chuyển động camera cho khung hình hiện tại và xác định lại các điểm đặc trưng để theo dõi       
        5. Cập nhật khung hình trước để sử dụng trong vòng lặp tiếp theo
        
        '''
        for frame_num in range(1,len(frames)):
            frame_gray = cv2.cvtColor(frames[frame_num],cv2.COLOR_BGR2GRAY) # chuyển đổi khung hình hiện tại sang thang độ xám
            # sử dụng thuật toán Lucas-Kanade để tính toán vị trí mới của các điểm đặc trưng trong khung hình hiện tại
            # calcOpticalFlowPyrLK trả về vị trí mới của các điểm đặc trưng, trạng thái (thành công hay không) và lỗi
            # thuật toán LUcas-Kanade Optical Flow thể hiện ở đâu? thể hiện ở chỗ sử dụng hàm cv2.calcOpticalFlowPyrLK để theo dõi các điểm đặc trưng giữa hai khung hình liên tiếp
            new_features, _,_ = cv2.calcOpticalFlowPyrLK(old_gray,frame_gray,old_features,None,**self.lk_params)

            max_distance = 0
            camera_movement_x, camera_movement_y = 0,0 # khởi tạo chuyển động camera là 0

            for i, (new,old) in enumerate(zip(new_features,old_features)): # duyệt qua từng điểm đặc trưng mới và cũ
                new_features_point = new.ravel() # ravel() để chuyển đổi mảng 2D thành 1D
                old_features_point = old.ravel()

                distance = measure_distance(new_features_point,old_features_point) # tính khoảng cách di chuyển của điểm đặc trưng
                if distance>max_distance: # nếu khoảng cách di chuyển lớn hơn khoảng cách lớn nhất hiện tại
                    max_distance = distance # cập nhật khoảng cách lớn nhất
                    camera_movement_x,camera_movement_y = measure_xy_distance(old_features_point, new_features_point ) # cập nhật chuyển động camera dựa trên điểm có khoảng cách di chuyển lớn nhất
            
            if max_distance > self.minimum_distance: # nếu khoảng cách di chuyển lớn hơn ngưỡng minimum_distance
                 # cập nhật chuyển động camera cho khung hình hiện tại
                camera_movement[frame_num] = [camera_movement_x,camera_movement_y]
                old_features = cv2.goodFeaturesToTrack(frame_gray,**self.features) # xác định lại các điểm đặc trưng để theo dõi

            old_gray = frame_gray.copy() # cập nhật khung hình trước để sử dụng trong vòng lặp tiếp theo
            # frame_gray.copy() để tránh tham chiếu đến cùng một vùng nhớ
        
        # phần mở file stub để lưu chuyển động camera
        if stub_path is not None:
            with open(stub_path,'wb') as f:
                pickle.dump(camera_movement,f)

        return camera_movement
    
    def draw_camera_movement(self,frames, camera_movement_per_frame):
        '''
        logic đoạn này là:
        1. Duyệt qua từng khung hình và chuyển động camera tương ứng trong danh sách camera_movement_per_frame.
        2. Tạo một bản sao của khung hình hiện tại để vẽ thông tin lên đó.
        3. Tạo một lớp phủ (overlay) để vẽ nền cho thông tin chuyển động camera.
        4. Vẽ một hình chữ nhật trắng làm nền cho thông tin chuyển động camera.
        5. Sử dụng cv2.putText để vẽ thông tin chuyển động camera (tọa độ X và Y) lên khung hình tại vị trí đã định.
        6. Lưu trữ khung hình đã được vẽ thông tin vào danh sách output_frames.
        7. Trả về danh sách khung hình đã được vẽ thông tin chuyển động camera.
        '''
        output_frames=[]

        for frame_num, frame in enumerate(frames):
            frame= frame.copy()

            overlay = frame.copy()
            cv2.rectangle(overlay,(0,0),(500,100),(255,255,255),-1)
            # vẽ hình chữ nhật cho camera movement X,Y đúng ko ? 
            
            alpha =0.6 # độ trong suốt của hình chữ nhật
            cv2.addWeighted(overlay,alpha,frame,1-alpha,0,frame) # kết hợp hình chữ nhật với khung hình gốc để tạo hiệu ứng trong suốt

            x_movement, y_movement = camera_movement_per_frame[frame_num] # lấy chuyển động camera tại khung hình hiện tại
            frame = cv2.putText(frame,f"Camera Movement X: {x_movement:.2f}",(10,30), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),3)
            frame = cv2.putText(frame,f"Camera Movement Y: {y_movement:.2f}",(10,60), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,0),3)

            output_frames.append(frame) 

        return output_frames