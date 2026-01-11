from sklearn.cluster import KMeans

class TeamAssigner: # Lớp để gán đội cho các cầu thủ dựa trên màu sắc áo đấu
    def __init__(self):
        self.team_colors = {}   # dictionary để lưu màu sắc của các đội
        self.player_team_dict = {} # dictionary để lưu đội của từng cầu thủ
    
    def get_clustering_model(self,image): # hàm để lấy mô hình phân cụm K-means từ hình ảnh
        # Reshape the image to 2D array
        image_2d = image.reshape(-1,3) # chuyển đổi hình ảnh thành mảng 2D với mỗi hàng là một pixel và 3 cột là giá trị màu RGB

        # Preform K-means with 2 clusters
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=1) # khởi tạo mô hình K-means với 2 cụm
        kmeans.fit(image_2d) # huấn luyện mô hình K-means trên dữ liệu hình ảnh 2D
        

        return kmeans

    def get_player_color(self,frame,bbox): # hàm để lấy màu sắc của cầu thủ từ khung hình và bounding box
        image = frame[int(bbox[1]):int(bbox[3]),int(bbox[0]):int(bbox[2])] # cắt hình ảnh của cầu thủ từ khung hình dựa trên bounding box
        # bbox = [x_min, y_min, x_max, y_max]
        top_half_image = image[0:int(image.shape[0]/2),:] # lấy nửa trên của hình ảnh cầu thủ
        #dấu : để lấy tất cả các cột, 0 :int(image.shape[0]/2) để lấy từ hàng 0 đến hàng giữa (nửa trên), [0:int(image.shape[0]/2),:], : ở cuối để lấy tất cả các kênh màu
        # image[height, width, channels] 
        
        # Get Clustering model
        kmeans = self.get_clustering_model(top_half_image) # lấy mô hình phân cụm K-means từ nửa trên của hình ảnh cầu thủ
        # lấy mô hình phân cụm từ nửa trên của hình ảnh cầu thủ vì nửa trên thường chứa nhiều thông tin về màu sắc áo đấu hơn nửa dưới
        
        # Get the cluster labels forr each pixel
        labels = kmeans.labels_ # lấy nhãn cụm cho mỗi pixel trong hình ảnh,pixel là một điểm dữ liệu trong không gian màu RGB

        # Reshape the labels to the image shape
        # tại sao phải reshape lại? Vì labels là một mảng 1 chiều chứa nhãn cụm cho mỗi pixel, cần reshape lại để có hình dạng giống với hình ảnh ban đầu để dễ dàng xử lý, hình dạng ban đầu của nửa trên hình ảnh là (height, width)
        clustered_image = labels.reshape(top_half_image.shape[0],top_half_image.shape[1]) # chuyển đổi nhãn cụm trở lại hình dạng ban đầu của nửa trên hình ảnh

        # Get the player cluster
        corner_clusters = [clustered_image[0,0],clustered_image[0,-1],clustered_image[-1,0],clustered_image[-1,-1]] # lấy nhãn cụm của 4 góc của nửa trên hình ảnh
        # clustered_image[-1,-1] là góc dưới bên phải
        non_player_cluster = max(set(corner_clusters),key=corner_clusters.count)
        # xác định cụm không phải cầu thủ dựa trên nhãn xuất hiện nhiều nhất trong 4 góc
        player_cluster = 1 - non_player_cluster # cụm cầu thủ là cụm còn lại
        # 1 là vì chỉ có 2 cụm (0 và 1)
        player_color = kmeans.cluster_centers_[player_cluster] # lấy màu sắc trung tâm của cụm cầu thủ

        return player_color


    def assign_team_color(self,frame, player_detections): # hàm để gán màu sắc đội cho các cầu thủ dựa trên phát hiện cầu thủ
        
        player_colors = []
        for _, player_detection in player_detections.items():
            bbox = player_detection["bbox"] 
            player_color =  self.get_player_color(frame,bbox) 
            player_colors.append(player_color) # lưu màu sắc của cầu thủ vào danh sách
        
        kmeans = KMeans(n_clusters=2, init="k-means++",n_init=10) # khởi tạo mô hình K-means với 2 cụm
        # n_init=10 để chạy K-means 10 lần với các khởi tạo khác nhau và chọn kết quả tốt nhất
        # kmeans++ là phương pháp khởi tạo cụm để cải thiện hiệu suất của K-means
        kmeans.fit(player_colors)

        self.kmeans = kmeans

        self.team_colors[1] = kmeans.cluster_centers_[0] # lưu màu sắc trung tâm của cụm 0 là màu sắc của đội 1
        self.team_colors[2] = kmeans.cluster_centers_[1] # lưu màu sắc trung tâm của cụm 1 là màu sắc của đội 2


    def get_player_team(self,frame,player_bbox,player_id): # hàm để lấy đội của cầu thủ dựa trên bounding box và id cầu thủ
        if player_id in self.player_team_dict: # nếu id cầu thủ đã có trong dictionary thì trả về đội đã gán
            return self.player_team_dict[player_id]

        player_color = self.get_player_color(frame,player_bbox) # lấy màu sắc của cầu thủ từ khung hình và bounding box

        team_id = self.kmeans.predict(player_color.reshape(1,-1))[0] # dự đoán đội của cầu thủ dựa trên màu sắc sử dụng mô hình K-means
        # reshape(1,-1) để chuyển đổi player_color thành mảng 2D với 1 hàng và số cột tương ứng với số đặc trưng (3 đặc trưng cho màu RGB)
        # (1,-1) trong reshape có nghĩa là 1 hàng và số cột tự động xác định dựa trên kích thước ban đầu của mảng
        team_id+=1 # đội 1 và đội 2 tương ứng với cụm 0 và cụm 1 trong K-means, tăng thêm 1 để có đội 1 và đội 2

        if player_id ==91: # nếu id cầu thủ là 91 thì gán đội là 1
            team_id=1

        self.player_team_dict[player_id] = team_id # lưu đội của cầu thủ vào dictionary

        return team_id
