import numpy as np 
import cv2

class ViewTransformer(): # class này để biến đổi phối cảnh của các vị trí cầu thủ từ hình ảnh gốc sang hệ tọa độ sân bóng chuẩn hóa
    '''
    logic của class ViewTransformer:
    1. Khởi tạo các tham số cần thiết để thực hiện biến đổi phối cảnh (perspective transformation)
    2. Hàm transform_point: 
    biến đổi một điểm từ hệ tọa độ hình ảnh gốc sang hệ tọa độ sân bóng đã được chuẩn hóa
       - Kiểm tra xem điểm có nằm trong đa giác xác định khu vực sân bóng không
       - Sử dụng cv2.perspectiveTransform để thực hiện biến đổi phối cảnh
    3. Hàm add_transformed_position_to_tracks: thêm vị trí đã được biến đổi vào tracks của các đối tượng
    - Duyệt qua từng đối tượng và khung hình trong tracks
    - Lấy vị trí đã được điều chỉnh (position_adjusted) và biến đổi nó sử dụng hàm transform_point
    - Cập nhật vị trí đã được biến đổi vào tracks dưới khóa 'position_transformed'
    
            
    '''
    def __init__(self):
        # Standard football pitch dimensions (meters)
        court_width = 68  # Width of pitch (goal line to goal line)
        court_length = 105  # Length of pitch (full length)

        self.pixel_vertices = np.array([[110, 1035], 
                               [265, 275], 
                               [910, 260], 
                               [1640, 915]]) # tọa độ pixel của 4 góc sân bóng trong hình ảnh gốc
        
        self.target_vertices = np.array([
            [0,court_width],
            [0, 0], # tọa độ góc trên bên trái của sân bóng trong hệ tọa độ sân bóng chuẩn hóa
            [court_length, 0],
            [court_length, court_width] # tọa độ góc dưới bên phải của sân bóng trong hệ tọa độ sân bóng chuẩn hóa
        ]) # tọa độ tương ứng của 4 góc sân bóng trong hệ tọa độ sân bóng chuẩn hóa

        self.pixel_vertices = self.pixel_vertices.astype(np.float32) # chuyển đổi sang kiểu float32 để sử dụng với OpenCV
        self.target_vertices = self.target_vertices.astype(np.float32) # chuyển đổi sang kiểu float32 để sử dụng với OpenCV

        self.perspective_transformer = cv2.getPerspectiveTransform(self.pixel_vertices, self.target_vertices)

    def transform_point(self,point):
        p = (int(point[0]),int(point[1])) # chuyển đổi điểm sang kiểu int để kiểm tra vị trí trong đa giác
        
        # Note: Removed is_inside check to allow transformation of all players
        # Even if they are outside the defined pitch boundaries in pixel space,
        # we still want to show their approximate positions on the tactical radar
        # is_inside = cv2.pointPolygonTest(self.pixel_vertices,p,False) >= 0
        # if not is_inside:
        #     return None

        reshaped_point = point.reshape(-1,1,2).astype(np.float32) # chuyển đổi điểm sang dạng phù hợp để sử dụng với cv2.perspectiveTransform
        tranform_point = cv2.perspectiveTransform(reshaped_point,self.perspective_transformer) # thực hiện biến đổi phối cảnh 
        # hàm cv2.perspectiveTransform để biến đổi điểm từ hệ tọa độ hình ảnh gốc sang hệ tọa độ sân bóng chuẩn hóa
        return tranform_point.reshape(-1,2)

    def add_transformed_position_to_tracks(self,tracks):
        '''
        logic đoạn này là:
        1. Duyệt qua từng đối tượng và khung hình trong tracks
        2. Lấy vị trí đã được điều chỉnh (position_adjusted) và biến đổi nó sử dụng hàm transform_point
        3. Cập nhật vị trí đã được biến đổi vào tracks dưới khóa 'position_transformed'
        4. Trả về tracks đã được cập nhật
        '''
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info['position_adjusted']
                    position = np.array(position)
                    position_transformed = self.transform_point(position)
                    if position_transformed is not None:
                        position_transformed = position_transformed.squeeze().tolist()
                    tracks[object][frame_num][track_id]['position_transformed'] = position_transformed # thêm vị trí đã được biến đổi vào tracks
                    # ['position_transformed'] là khóa mới để lưu vị trí đã được biến đổi