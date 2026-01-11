def get_center_of_bbox(bbox):
    # hàm này nhận vào một bounding box dưới dạng (x1, y1, x2, y2)
    x1,y1,x2,y2 = bbox
    return int((x1+x2)/2),int((y1+y2)/2)

def get_bbox_width(bbox):
    # hàm này nhận vào một bounding box dưới dạng (x1, y1, x2, y2)
    return bbox[2]-bbox[0]

def measure_distance(p1,p2):
    # hàm này đo khoảng cách Euclid giữa hai điểm p1 và p2
    return ((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)**0.5

def measure_xy_distance(p1,p2):
    # hàm này đo khoảng cách theo từng trục x và y giữa hai điểm p1 và p2
    return p1[0]-p2[0],p1[1]-p2[1]

def get_foot_position(bbox):
    # hàm này nhận vào một bounding box dưới dạng (x1, y1, x2, y2) và trả về vị trí chân (foot position)
    x1,y1,x2,y2 = bbox
    return int((x1+x2)/2),int(y2)