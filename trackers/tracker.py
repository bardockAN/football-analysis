from ultralytics import YOLO # đây là thư viện YOLO để thực hiện phát hiện đối tượng
import pickle # thư viện pickle để lưu trữ và tải dữ liệu dạng nhị phân
import os
import numpy as np  
import pandas as pd 
import cv2 # thư viện OpenCV để xử lý ảnh và video
import sys  # thêm thư mục cha vào sys.path để có thể import module từ thư mục cha
sys.path.append('../')
from utils import get_center_of_bbox, get_bbox_width, get_foot_position
from collections import defaultdict

class Tracker: # lớp Tracker để theo dõi các đối tượng trong video
    
    def __init__(self, model_path):
        self.model = YOLO(model_path)
        self.trackers = {}  # Dictionary to store active trackers
        self.next_id = 1    # For assigning unique IDs
        self.max_lost = 30  # Maximum number of frames to keep lost tracks

    def add_position_to_tracks(self,tracks): # hàm này thêm vị trí (position) vào từng track trong tracks
        #tracks là dictionary lưu trữ thông tin về các đối tượng được theo dõi trong từng khung hình
        for object, object_tracks in tracks.items(): # nó sẽ lặp qua từng loại đối tượng: players, referees, ball
            #.items() trả về cả key và value trong dictionary
            for frame_num, track in enumerate(object_tracks): # lặp qua từng khung hình cho từng loại object
                for track_id, track_info in track.items():
                    #track_id là id của đối tượng, track_info là thông tin về bbox
                    #track.items() trả về cả key và value trong dictionary
                    bbox = track_info['bbox'] # Lấy bbox từ track_info
                    if object == 'ball':
                        position= get_center_of_bbox(bbox)# Lấy vị trí trung tâm của bbox cho bóng
                    else:
                        position = get_foot_position(bbox) # Lấy vị trí chân của người chơi và trọng tài
                    tracks[object][frame_num][track_id]['position'] = position # Thêm vị trí vào track

    def interpolate_ball_positions(self,ball_positions): # hàm này nội suy (interpolate) vị trí bóng trong trường hợp bóng không được phát hiện trong một số khung hình
        # nội suy là cách ước tính giá trị nằm giữa 2 giá trị đã biết, trong trường hợp này là vị trí bóng trong các khung hình mà bóng không được phát hiện
        ball_positions = [x.get(1,{}).get('bbox',[]) for x in ball_positions] # Lấy bbox của bóng từ ball_positions
        # x.get(1,{}) lấy thông tin của bóng với track_id là 1, nếu không có thì trả về dictionary rỗng
        # .get('bbox',[]) lấy bbox từ dictionary, nếu không có thì trả về danh sách rỗng
        # dictionary ở đây nó lưu trữ thông tin về các track của bóng trong từng khung hình
        # Tạo DataFrame từ danh sách bbox
        df_ball_positions = pd.DataFrame(ball_positions,columns=['x1','y1','x2','y2'])

        # Interpolate missing values
        df_ball_positions = df_ball_positions.interpolate() # nội suy các giá trị bị thiếu
        df_ball_positions = df_ball_positions.bfill() # điền các giá trị NaN ở đầu bằng giá trị tiếp theo
        # bfill() là hàm trong pandas để điền các giá trị NaN bằng giá trị tiếp theo trong cột

        ball_positions = [{1: {"bbox":x}} for x in df_ball_positions.to_numpy().tolist()]# chuyển DataFrame trở lại danh sách bbox
        # 1: {"bbox":x} tạo dictionary với track_id là 1 và bbox là x
        #tolist() chuyển DataFrame thành danh sách các danh sách
        return ball_positions

    # YOLO Detection
    def detect_frames(self, frames): # hàm này thực hiện phát hiện đối tượng trên từng khung hình trong frames sử dụng mô hình YOLO
        # self là đối tượng của lớp Tracker
        # frames là danh sách các khung hình cần phát hiện đối tượng
        batch_size=20 # kích thước lô để xử lý khung hình , lô ở đây là số lượng khung hình được xử lý cùng một lúc, là số ảnh được đưa vào mô hình để dự đoán trong một lần
        detections = []  # danh sách lưu trữ kết quả phát hiện
        for i in range(0,len(frames),batch_size): # lặp qua các khung hình theo kích thước lô
            
            # Lấy lô khung hình hiện tại
            detections_batch = self.model.predict(frames[i:i+batch_size],conf=0.1)
            # self.model.predict() thực hiện phát hiện đối tượng trên lô khung hình
            # conf=0.1 là ngưỡng độ tin cậy để lọc các phát hiện có độ tin cậy thấp
            # frames[i:i+batch_size] lấy lô khung hình từ i đến i+batch_size
            detections += detections_batch # thêm kết quả phát hiện vào danh sách detections
        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None): # hàm này theo dõi các đối tượng trong frames và trả về tracks, tracks là thông tin về các đối tượng được theo dõi trong từng khung hình
        # frames là danh sách các khung hình cần theo dõi
        # read_from_stub là cờ để đọc tracks từ file stub nếu có
        # file stub là file lưu trữ dữ liệu dạng nhị phân
        # stub_path là đường dẫn đến file stub
        # os.path.exists(stub_path) kiểm tra xem file stub có tồn tại không

        ## đọc dữ liệu từ file stub nếu có
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path,'rb') as f:
                # Đọc tracks từ file stub nếu có
                # rb là chế độ đọc file nhị phân', f là biến file object
                tracks = pickle.load(f) # tải dữ liệu từ file stub
            return tracks

        # chạy YOLO để phát hiện đối tượng trên từng khung hình
        detections = self.detect_frames(frames) # thực hiện phát hiện đối tượng trên từng khung hình

        tracks={
            "players":[],
            "referees":[],
            "ball":[]
        } # khởi tạo tracks rỗng để lưu trữ thông tin về các đối tượng được theo dõi

        for frame_num, detection in enumerate(detections):
            cls_names = detection.names # lấy tên lớp từ kết quả phát hiện, lớp ở đây là các loại đối tượng được phát hiện như player, referee, ball
            cls_names_inv = {v:k for k,v in cls_names.items()} # tạo từ điển đảo ngược để ánh xạ tên lớp sang id lớp

            # Initialize frame dictionaries
            tracks["players"].append({}) # thêm dictionary rỗng cho khung hình hiện tại trong players
            tracks["referees"].append({})
            tracks["ball"].append({})
            
            # Get current frame
            frame = frames[frame_num] 
            
            # Process detections
            '''
            với từng frame thì xử lý toàn bộ detections trong frame đó
            lấy bounding box, độ tin cậy và id lớp từ kết quả phát hiện
            sau đó lặp qua từng phát hiện trong khung hình hiện tại
            nếu độ tin cậy của phát hiện thấp hơn ngưỡng thì bỏ qua
            nếu phát hiện là goalkeeper thì chuyển thành player
            tìm tracker phù hợp hoặc tạo mới, tracker phù hợp là tracker có khoảng cách gần nhất với bounding box hiện tại
            tracker là đối tượng theo dõi vị trí của một đối tượng trong video
            nếu tìm thấy tracker phù hợp thì cập nhật tracker với vị trí mới
            nếu không tìm thấy tracker phù hợp thì tạo mới tracker và thêm vào danh sách trackers
            sau đó thêm thông tin về bounding box vào tracks
            cuối cùng cập nhật bộ đếm mất dấu và vô hiệu hóa các tracker bị mất dấu
            '''
            boxes = detection.boxes.xyxy.cpu().numpy() # lấy bounding box từ kết quả phát hiện
            # .xyxy trả về bounding box dưới dạng (x1, y1, x2, y2)
            #.cpu() chuyển tensor về CPU
            # .numpy() chuyển tensor thành mảng numpy
            confidences = detection.boxes.conf.cpu().numpy() # lấy độ tin cậy từ kết quả phát hiện
            class_ids = detection.boxes.cls.cpu().numpy() # lấy id lớp từ kết quả phát hiện
            
            # Update trackers and process detections
            active_trackers = defaultdict(list)  # theo dõi các tracker hoạt động trong khung hình hiện tại
            # defaultdict(list) tạo dictionary với giá trị mặc định là danh sách rỗng, tạo dictionary để lưu trữ các tracker hoạt động cho từng lớp đối tượng
            
            # xử lý từng phát hiện trong khung hình hiện tại
            for box_idx, (bbox, conf, cls_id) in enumerate(zip(boxes, confidences, class_ids)): # lặp qua từng bounding box, độ tin cậy và id lớp
                # Bỏ qua các phát hiện có độ tin cậy thấp
                if conf < 0.5:  # Skip low confidence detections
                    continue
                    
                # Chuyển đổi goalkeeper thành player
                if cls_names[int(cls_id)] == "goalkeeper":
                    cls_id = cls_names_inv["player"] # lấy id lớp của player từ tên lớp
                
                # Tìm tracker phù hợp hoặc tạo mới, tracker phù hợp là tracker có khoảng cách gần nhất với bounding box hiện tại
                matched_id = None # id của tracker phù hợp
                bbox_center = get_center_of_bbox(bbox) # lấy vị trí trung tâm của bounding box
                
                # Thử tìm tracker phù hợp với các tracker hiện có
                for tracker_id, tracker_info in self.trackers.items():
                    #.items() trả về cả key và value trong dictionary
                    if not tracker_info['active'] or tracker_info['class_id'] != int(cls_id): # bỏ qua các tracker không hoạt động hoặc không cùng lớp
                        continue
                    
                    tracker = tracker_info['tracker'] # lấy tracker từ tracker_info
                    success, track_box = tracker.update(frame) # cập nhật tracker với khung hình hiện tại
                    
                    if success: # 
                        track_center = get_center_of_bbox(track_box)# lấy vị trí trung tâm của bounding box được theo dõi bởi tracker, tracker là đối tượng theo dõi vị trí của một đối tượng trong video
                        dist = np.linalg.norm(np.array(bbox_center) - np.array(track_center)) # tính khoảng cách Euclid giữa vị trí trung tâm của bounding box hiện tại và vị trí trung tâm của bounding box được theo dõi bởi tracker
                        # np.linalg.norm() tính chuẩn Euclid của vector
                        
                        if dist < 50:  # Distance threshold for matching
                            matched_id = tracker_id # gán id của tracker phù hợp
                            # Cập nhật tracker với vị trí mới
                            tracker.init(frame, tuple(bbox.astype(int))) # khởi tạo lại tracker với khung hình hiện tại và bounding box hiện tại
                            # tuple() chuyển mảng numpy thành tuple
                            # .astype(int) chuyển mảng numpy thành kiểu int
                            tracker_info['lost_count'] = 0 # đặt lại bộ đếm mất dấuu tracker
                            break # thoát khỏi vòng lặp sau khi tìm thấy tracker phù hợp
                
                # Create new tracker if no match found
                if matched_id is None:
                    tracker = cv2.TrackerCSRT_create() # tạo tracker mới sử dụng thuật toán CSRT
                    # CSRT (Channel and Spatial Reliability Tracking) là một thuật toán theo dõi đối tượng trong video
                    tracker.init(frame, tuple(bbox.astype(int))) # khởi tạo tracker với khung hình hiện tại và bounding box hiện tại
                    matched_id = self.next_id # gán id mới cho tracker
                    self.next_id += 1 
                    
                    
                    # Thêm tracker mới vào danh sách trackers
                    self.trackers[matched_id] = {
                        'tracker': tracker,
                        'active': True,
                        'class_id': int(cls_id), # id lớp của đối tượng được theo dõi
                        'lost_count': 0 # bộ đếm mất dấu tracker
                    }
                
                # Add to appropriate track list
                if int(cls_id) == cls_names_inv['player']: # nếu đối tượng là player
                    tracks["players"][frame_num][matched_id] = {"bbox": bbox.tolist()} # thêm bounding box vào tracks, tracks là dictionary lưu trữ thông tin về các đối tượng được theo dõi trong từng khung hình
                elif int(cls_id) == cls_names_inv['referee']:
                    tracks["referees"][frame_num][matched_id] = {"bbox": bbox.tolist()}
                elif int(cls_id) == cls_names_inv['ball']:
                    tracks["ball"][frame_num][1] = {"bbox": bbox.tolist()}
                
                active_trackers[int(cls_id)].append(matched_id) # thêm id của tracker vào danh sách tracker hoạt động cho lớp đối tượng hiện tại
            
            # Update lost counts and deactivate lost trackers
            for tracker_id, tracker_info in self.trackers.items():
                if tracker_info['active']: # chỉ cập nhật các tracker đang hoạt động
                    cls_id = tracker_info['class_id'] # lấy id lớp của tracker
                    # tracker_info là thông tin về tracker hiện tại
                    if tracker_id not in active_trackers[cls_id]: # nếu tracker không hoạt động trong khung hình hiện tại
                        tracker_info['lost_count'] += 1 # tăng bộ đếm mất dấu tracker
                        if tracker_info['lost_count'] > self.max_lost: # nếu bộ đếm mất dấu vượt quá ngưỡng cho phép
                            tracker_info['active'] = False # đặt tracker không hoạt động

        if stub_path is not None: # nếu có đường dẫn đến file stub, file stub là file lưu trữ dữ liệu dạng nhị phân
            with open(stub_path,'wb') as f: # lưu tracks vào file stub
                # wb là chế độ ghi file nhị phân, f là biến file object
                pickle.dump(tracks,f) # lưu dữ liệu vào file stub

        return tracks
    
    def draw_ellipse(self,frame,bbox,color,track_id=None):# hàm này vẽ hình ellipse lên khung hình frame dựa trên bounding box bbox và màu color
        y2 = int(bbox[3]) # bbox[3] là tọa độ y dưới cùng của bounding box
        x_center, _ = get_center_of_bbox(bbox) # lấy tọa độ x trung tâm của bounding box
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            center=(x_center,y2),
            axes=(int(width), int(0.35*width)),
            angle=0.0,
            startAngle=-45,
            endAngle=235,
            color = color,
            thickness=2,
            lineType=cv2.LINE_4
        ) # vẽ hình ellipse lên khung hình frame


        # Đây là vẽ hình chữ nhật chứa id của đối tượng
        rectangle_width = 40
        rectangle_height=20
        x1_rect = x_center - rectangle_width//2
        x2_rect = x_center + rectangle_width//2
        y1_rect = (y2- rectangle_height//2) +15
        y2_rect = (y2+ rectangle_height//2) +15

        if track_id is not None:
            cv2.rectangle(frame,
                          (int(x1_rect),int(y1_rect) ),
                          (int(x2_rect),int(y2_rect)),
                          color,
                          cv2.FILLED) # vẽ hình chữ nhật lên khung hình frame, rectangle là hàm vẽ hình chữ nhật trong OpenCV
            
            x1_text = x1_rect+12 # vị trí x để vẽ text, text là id của đối tượng
            if track_id > 99: # nếu id có 3 chữ số
                x1_text -=10 # điều chỉnh vị trí x để vẽ text
            
            cv2.putText(
                frame,
                f"{track_id}",
                (int(x1_text),int(y1_rect+15)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0,0,0),
                2
            )
            # hàm putText để vẽ text lên khung hình frame, FONT_HERSHEY_SIMPLEX là kiểu font chữ trong OpenCV

        return frame

    def draw_traingle(self,frame,bbox,color): # hàm này vẽ hình tam giác lên khung hình frame dựa trên bounding box bbox và màu color
        y= int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([
            [x,y],
            [x-10,y-20],
            [x+10,y-20],
        ])
        cv2.drawContours(frame, [triangle_points],0,color, cv2.FILLED) # vẽ hình tam giác lên khung hình frame
        # drawContours là hàm trong OpenCV để vẽ các đường viền của hình dạng
        # cv2.FILLED là để lấp đầy hình tam giác với màu color
        
        cv2.drawContours(frame, [triangle_points],0,(0,0,0), 2) # vẽ viền cho hình tam giác lên khung hình frame

        return frame # trả về khung hình frame đã được vẽ hình tam giác

    def draw_team_ball_control(self,frame,frame_num,team_ball_control): # hàm này vẽ thông tin về kiểm soát bóng của từng đội lên khung hình frame
        # Draw a semi-transparent rectaggle 
        overlay = frame.copy() # tạo bản sao của khung hình frame để vẽ hình chữ nhật bán trong suốt
        cv2.rectangle(overlay, (1350, 850), (1900,970), (255,255,255), -1 ) # vẽ hình chữ nhật lên bản sao của khung hình frame
        #overlay là bản sao của khung hình frame
        # (1350, 850) là tọa độ góc trên bên trái của hình chữ nhật
        #(1900,970) là tọa độ góc dưới bên phải của hình chữ
        #(255,255,255) là màu trắng
        #-1 là độ dày của hình chữ nhật, -1 nghĩa là hình chữ nhật được lấp đầy
        alpha = 0.4 # độ trong suốt của hình chữ nhật bán trong suốt
        cv2.addWeighted(overlay , alpha, frame, 1 - alpha, 0, frame) # kết hợp bản sao của khung hình frame và khung hình frame gốc để tạo hiệu ứng bán trong suốt
        # addWeighted là hàm trong OpenCV để kết hợp hai hình ảnh với trọng số nhất định
        
        
        team_ball_control_till_frame = team_ball_control[:frame_num+1]  # lấy thông tin kiểm soát bóng của từng đội từ đầu đến khung hình hiện tại
        # Get the number of time each team had ball control
        team_1_num_frames = team_ball_control_till_frame[team_ball_control_till_frame==1].shape[0] # đếm số khung hình mà đội 1 kiểm soát bóng
        team_2_num_frames = team_ball_control_till_frame[team_ball_control_till_frame==2].shape[0] # đếm số khung hình mà đội 2 kiểm soát bóng  
        team_1 = team_1_num_frames/(team_1_num_frames+team_2_num_frames) # tính tỷ lệ kiểm soát bóng của đội 1
        team_2 = team_2_num_frames/(team_1_num_frames+team_2_num_frames) # tính tỷ lệ kiểm soát bóng của đội 2

        cv2.putText(frame, f"Team 1 Ball Control: {team_1*100:.2f}%",(1400,900), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3) # vẽ thông tin kiểm soát bóng của đội 1 lên khung hình frame
        cv2.putText(frame, f"Team 2 Ball Control: {team_2*100:.2f}%",(1400,950), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 3) # vẽ thông tin kiểm soát bóng của đội 2 lên khung hình frame
        #{:.2f} định dạng số thập phân với 2 chữ số sau dấu phẩy
        # FONT_HERSHEY_SIMPLEX là kiểu font chữ trong OpenCV , 1 là kích thước font chữ, (0,0,0) là màu đen, 3 là độ dày của chữ
        return frame

    def draw_annotations(self,video_frames, tracks,team_ball_control):
        # hàm này vẽ các chú thích lên từng khung hình trong video_frames dựa trên thông tin trong tracks và team_ball_control
        output_video_frames= [] # danh sách để lưu trữ các khung hình đã được vẽ chú thích
        for frame_num, frame in enumerate(video_frames): # lặp qua từng khung hình trong video_frames
            frame = frame.copy() # tạo bản sao của khung hình hiện tại để vẽ chú thích

            player_dict = tracks["players"][frame_num] # lấy thông tin về người chơi trong khung hình hiện tại từ tracks
            ball_dict = tracks["ball"][frame_num] # lấy thông tin về quả bóng trong khung hình hiện tại từ tracks
            referee_dict = tracks["referees"][frame_num] # lấy thông tin về trọng tài trong khung hình hiện tại từ tracks

            # Draw Players
            for track_id, player in player_dict.items(): # lặp qua từng người chơi trong khung hình hiện tại
                color = player.get("team_color",(0,0,255)) # lấy màu của đội từ thông tin người chơi, nếu không có thì mặc định là màu đỏ,(0,0,255) là màu đỏ trong không gian màu BGR
                frame = self.draw_ellipse(frame, player["bbox"],color, track_id) # vẽ hình ellipse lên khung hình frame dựa trên bounding box của người chơi và màu của đội,self là đối tượng của lớp Tracker

                if player.get('has_ball',False):# nếu người chơi có bóng
                    frame = self.draw_traingle(frame, player["bbox"],(0,0,255)) # vẽ hình tam giác lên khung hình frame dựa trên bounding box của người chơi và màu đỏ, player["bbox"] là bounding box của người chơi

            # Draw Referee
            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"],(0,255,255))
            
            # Draw ball 
            for track_id, ball in ball_dict.items():
                frame = self.draw_traingle(frame, ball["bbox"],(0,255,0))


            # Draw Team Ball Control
            frame = self.draw_team_ball_control(frame, frame_num, team_ball_control)

            output_video_frames.append(frame)

        return output_video_frames