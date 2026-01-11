import sys 
sys.path.append('../')
from utils import get_center_of_bbox, measure_distance

class PlayerBallAssigner(): # lớp để gán bóng cho cầu thủ gần nhất
    def __init__(self):
        self.max_player_ball_distance = 70 # khoảng cách tối đa để gán bóng cho cầu thủ, 70 là
    
    def assign_ball_to_player(self,players,ball_bbox): # hàm để gán bóng cho cầu thủ gần nhất
        ball_position = get_center_of_bbox(ball_bbox) 

        miniumum_distance = 99999 # khởi tạo khoảng cách tối thiểu lớn
        assigned_player=-1 # khởi tạo id cầu thủ được gán bóng là -1 (không có)

        for player_id, player in players.items(): 
            player_bbox = player['bbox'] # lấy bounding box của cầu thủ

            distance_left = measure_distance((player_bbox[0],player_bbox[-1]),ball_position) # tính khoảng cách từ cạnh trái của bounding box cầu thủ đến vị trí bóng
            distance_right = measure_distance((player_bbox[2],player_bbox[-1]),ball_position) # tính khoảng cách từ cạnh phải của bounding box cầu thủ đến vị trí bóng
            distance = min(distance_left,distance_right) # lấy khoảng cách nhỏ hơn trong 2 khoảng cách trên 

            if distance < self.max_player_ball_distance: # nếu khoảng cách nhỏ hơn khoảng cách tối đa để gán bóng
                if distance < miniumum_distance:
                    miniumum_distance = distance
                    assigned_player = player_id

        return assigned_player