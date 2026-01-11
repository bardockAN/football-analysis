import argparse
from utils import read_video, save_video
from trackers import Tracker
import cv2
import numpy as np
from team_assigner import TeamAssigner
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distance_estimator import SpeedAndDistance_Estimator
from player_stats_analyzer import PlayerStatsAnalyzer

# Import các module mới cho case studies và analytics
from case_studies import TeamComparisonAnalyzer, MVPAnalyzer, TacticalAnalyzer
from analytics import DataExporter, DashboardGenerator, ReportGenerator

'''
logic của hàm main:
1. Đọc video từ file
2. Khởi tạo tracker và lấy tracks của các đối tượng trong video
3. Ước lượng chuyển động camera và điều chỉnh vị trí các đối tượng trong tracks
4. Biến đổi góc nhìn từ góc nhìn camera sang góc nhìn từ trên xuống và thêm vị trí đã biến đổi vào tracks
5. Nội suy vị trí bóng trong tracks để ước lượng vị trí bóng ở những khung hình mà bóng không được phát hiện
6. Ước lượng tốc độ và khoảng cách di chuyển của cầu thủ và thêm thông tin này vào tracks
7. Gán đội cho cầu thủ dựa trên màu sắc áo đấu và thêm thông tin này vào tracks
8. Gán cầu thủ có bóng dựa trên khoảng cách từ cầu thủ đến bóng và thêm thông tin này vào tracks
9. Phân tích và thống kê các chỉ số của cầu thủ (số lần chạm bóng, tỉ lệ giữ bóng, quãng đường, tốc độ)
10. Vẽ kết quả đầu ra lên các khung hình video (bao gồm bảng thống kê)
11. Lưu video kết quả và export bảng thống kê ra file

'''
def main():
    # Read Video
    parser = argparse.ArgumentParser(description='Football Analysis AI')
    parser.add_argument('--input', type=str, default='input_videos/08fd33_4.mp4', help='Đường dẫn đến video đầu vào')
    args = parser.parse_args()
    
    video_path = args.input
    
    try:
        video_frames = read_video(video_path)
    except FileNotFoundError as e:
        print(f"\n{e}")
        print(f"\n💡 Hướng dẫn: Vui lòng đặt file video vào thư mục 'input_videos/' hoặc cập nhật đường dẫn trong main.py")
        return
    except ValueError as e:
        print(f"\n{e}")
        return
    except Exception as e:
        print(f"\n❌ Lỗi không xác định khi đọc video: {e}")
        return

    # Initialize Tracker, tracker là đối tượng dùng để theo dõi các đối tượng trong video, tracks là dữ liệu theo dõi các đối tượng
    tracker = Tracker('models/best.pt') 
    tracks = tracker.get_object_tracks(video_frames,
                                       read_from_stub=True,
                                       stub_path='stubs/track_stubs.pkl')
    # Get object positions 
    tracker.add_position_to_tracks(tracks)

    # camera movement estimator
    camera_movement_estimator = CameraMovementEstimator(video_frames[0]) # object này dùng để ước lượng chuyển động camera
    
    # object  camera_movement_per_frame lưu chuyển động camera cho từng khung hình
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames,
                                                                                read_from_stub=True,# tham số này cho biết có đọc từ stub không,stub là dữ liệu đã được tính toán trước để tiết kiệm thời gian
                                                                                stub_path='stubs/camera_movement_stub.pkl') # đường dẫn đến file stub
    camera_movement_estimator.add_adjust_positions_to_tracks(tracks,camera_movement_per_frame) # điều chỉnh vị trí các đối tượng trong tracks dựa trên chuyển động camera


    # View Trasnformer, làm biến đổi góc nhìn từ góc nhìn camera sang góc nhìn từ trên xuống
    view_transformer = ViewTransformer() # khởi tạo đối tượng ViewTransformer
    view_transformer.add_transformed_position_to_tracks(tracks) # thêm vị trí đã biến đổi vào tracks

    # Interpolate Ball Positions, interpolate là nội suy, tức là ước lượng vị trí bóng ở những khung hình mà bóng không được phát hiện
    tracks["ball"] = tracker.interpolate_ball_positions(tracks["ball"]) # nội suy vị trí bóng trong tracks
    # Nội suy là cách ước tính giá trị nằm giữa 2 giá trị đã biết, trong trường hợp này là vị trí bóng trong các khung hình mà bóng không được phát hiện
    
    
    
    # Speed and distance estimator, dựa đoán tốc độ và khoảng cách
    speed_and_distance_estimator = SpeedAndDistance_Estimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    # Assign Player Teams, gán đội cho cầu thủ
    team_assigner = TeamAssigner() 
    team_assigner.assign_team_color(video_frames[0], # sử dụng khung hình đầu tiên để gán màu đội
                                    tracks['players'][0])
    # track['players'] là danh sách các cầu thủ được theo dõi trong từng khung hình
    
    for frame_num, player_track in enumerate(tracks['players']):# với mỗi khung hình và các cầu thủ trong khung hình đó
        for player_id, track in player_track.items():# với mỗi cầu thủ trong khung hình đó
            # player_track.items() trả về cả key và value trong dictionary
            team = team_assigner.get_player_team(video_frames[frame_num],   
                                                 track['bbox'],
                                                 player_id)
            # gọi hàm get_player_team để xác định đội của cầu thủ dựa trên khung hình hiện tại, bounding box và id cầu thủ
            # video_frames[frame_num] là khung hình hiện tại
            # track['bbox'] là bounding box của cầu thủ trong khung hình đó
            # player_id là id của cầu thủ
            
            tracks['players'][frame_num][player_id]['team'] = team  # gán đội cho cầu thủ trong tracks
            #['players'][frame_num][player_id] là cầu thủ cụ thể trong khung hình cụ thể
            #['team'] là thuộc tính đội của cầu thủ đó
            #[player_id] là id của cầu thủ
            #[frame_num] là khung hình hiện tại
            #track['players'][frame_num][player_id]['team'] lưu đội của cầu thủ đó
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]# lưu màu đội của cầu thủ đó

    
    # Assign Ball Aquisition, acquisition là sự chiếm hữu
    player_assigner =PlayerBallAssigner() # khởi tạo đối tượng PlayerBallAssigner để gán cầu thủ có bóng
    team_ball_control= [] # danh sách lưu đội kiểm soát bóng trong từng khung hình
    for frame_num, player_track in enumerate(tracks['players']): # với mỗi khung hình và các cầu thủ trong khung hình đó
        ball_bbox = tracks['ball'][frame_num][1]['bbox'] # lấy bounding box của bóng trong khung hình đó
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_bbox)
        # [1] là vì trong tracks['ball'][frame_num] có thể có nhiều đối tượng, ta lấy đối tượng thứ nhất (bóng)
        # ['bbox'] là bounding box của bóng trong khung hình đó
        
        
        if assigned_player != -1: # nếu có cầu thủ được gán bóng
            tracks['players'][frame_num][assigned_player]['has_ball'] = True # gán cầu thủ có bóng
            team_ball_control.append(tracks['players'][frame_num][assigned_player]['team']) # lưu đội của cầu thủ có bóng
        else:
            # If no player has the ball, keep the last team that had it (or use 0 if first frame)
            team_ball_control.append(team_ball_control[-1] if len(team_ball_control) > 0 else 0) # nếu không có cầu thủ nào có bóng, giữ đội cuối cùng có bóng (hoặc dùng 0 nếu là khung hình đầu tiên)
    team_ball_control= np.array(team_ball_control) # chuyển danh sách thành mảng numpy


    # Phân tích và thống kê các chỉ số cầu thủ
    print("Đang phân tích thống kê cầu thủ...")
    stats_analyzer = PlayerStatsAnalyzer()
    
    # Tính toán stats cho tất cả cầu thủ
    player_stats = stats_analyzer.calculate_player_stats(tracks, team_ball_control)
    
    # Lấy top 5 cầu thủ theo tổng quãng đường (hoặc có thể chọn tiêu chí khác)
    top_5_players = stats_analyzer.get_top_players(n=5, sort_by='total_distance')
    print(f"Top 5 cầu thủ được chọn để thống kê: {top_5_players}")
    
    # Tính lại stats chỉ cho 5 cầu thủ được chọn (để hiển thị rõ ràng hơn)
    selected_stats = stats_analyzer.calculate_player_stats(tracks, team_ball_control, selected_player_ids=top_5_players)
    
    # Tạo bảng thống kê dạng hình ảnh
    stats_table_img = stats_analyzer.create_stats_table_image(width=900, height=400)
    
    # Lưu bảng thống kê ra file ảnh
    cv2.imwrite('output_videos/player_stats_table.png', stats_table_img)
    print("Đã lưu bảng thống kê vào output_videos/player_stats_table.png")
    
    # Export thống kê ra CSV
    stats_analyzer.export_stats_to_csv('output_videos/player_stats.csv')
    print("Đã export thống kê ra output_videos/player_stats.csv")
    
    
    # ============================================================================
    # CASE STUDIES & ADVANCED ANALYTICS
    # ============================================================================
    print("\n" + "="*80)
    print("BẮT ĐẦU PHÂN TÍCH NÂNG CAO VÀ TẠO CASE STUDIES")
    print("="*80 + "\n")
    
    # Case Study 1: Team Comparison Analysis
    print("📊 Case Study 1: Phân tích so sánh hiệu suất 2 đội...")
    team_analyzer = TeamComparisonAnalyzer()
    team_stats = team_analyzer.analyze_teams(tracks, team_ball_control)
    
    # Tạo biểu đồ so sánh đội
    team_comparison_chart = team_analyzer.create_comparison_chart(width=1200, height=800)
    cv2.imwrite('output_videos/case_study_1_team_comparison.png', team_comparison_chart)
    print("✓ Đã lưu: output_videos/case_study_1_team_comparison.png")
    
    # Case Study 2: MVP Analysis
    print("\n🏆 Case Study 2: Phân tích cầu thủ xuất sắc nhất (MVP)...")
    mvp_analyzer = MVPAnalyzer()
    mvp_result = mvp_analyzer.analyze_mvp(selected_stats, tracks)
    
    if mvp_result and mvp_result['mvp']:
        print(f"   MVP: Player {mvp_result['mvp']['player_id']} với MVP Score {mvp_result['mvp']['mvp_score']:.1f}/100")
        
        # Tạo MVP card
        mvp_card = mvp_analyzer.create_mvp_card(width=800, height=1000)
        cv2.imwrite('output_videos/case_study_2_mvp_card.png', mvp_card)
        print("✓ Đã lưu: output_videos/case_study_2_mvp_card.png")
        
        # Tạo top 5 ranking
        top5_ranking = mvp_analyzer.create_top5_ranking(width=1000, height=700)
        cv2.imwrite('output_videos/case_study_2_top5_ranking.png', top5_ranking)
        print("✓ Đã lưu: output_videos/case_study_2_top5_ranking.png")
    
    # Case Study 3: Tactical Analysis
    print("\n⚡ Case Study 3: Phân tích chiến thuật và passing network...")
    tactical_analyzer = TacticalAnalyzer()
    tactical_result = tactical_analyzer.analyze_tactics(tracks, team_ball_control)
    
    # Tạo passing network visualization
    passing_network_viz = tactical_analyzer.create_passing_network_viz(width=1400, height=900)
    cv2.imwrite('output_videos/case_study_3_passing_network.png', passing_network_viz)
    print("✓ Đã lưu: output_videos/case_study_3_passing_network.png")
    
    # Tạo formation visualization
    formation_viz = tactical_analyzer.create_formation_viz(width=1200, height=800)
    cv2.imwrite('output_videos/case_study_3_formations.png', formation_viz)
    print("✓ Đã lưu: output_videos/case_study_3_formations.png")
    
    if tactical_result['formations']:
        for team_id, formation in tactical_result['formations'].items():
            if formation:
                print(f"   Team {team_id}: Đội hình {formation['formation']} ({formation['num_players']} cầu thủ)")
    
    # ============================================================================
    # DATA EXPORT (JSON, CSV)
    # ============================================================================
    print("\n📁 Đang export dữ liệu ra JSON và CSV...")
    data_exporter = DataExporter(output_dir='output_videos/analytics')
    exported_files = data_exporter.export_all_data(
        selected_stats,
        team_analyzer,
        mvp_analyzer,
        tactical_analyzer
    )
    
    # Tạo export summary
    data_exporter.create_export_summary(exported_files)
    
    # ============================================================================
    # DASHBOARD GENERATION
    # ============================================================================
    print("\n📈 Đang tạo dashboard với charts và graphs...")
    dashboard_gen = DashboardGenerator(output_dir='output_videos/analytics')
    
    # Tạo dashboard tổng hợp
    dashboard_path = dashboard_gen.create_full_dashboard(
        selected_stats,
        team_analyzer,
        mvp_analyzer
    )
    
    # Tạo các chart riêng lẻ
    individual_charts = dashboard_gen.create_individual_charts(
        selected_stats,
        team_analyzer,
        mvp_analyzer
    )
    
    # ============================================================================
    # REPORT GENERATION (HTML/PDF)
    # ============================================================================
    print("\n📄 Đang tạo báo cáo HTML...")
    report_gen = ReportGenerator(output_dir='output_videos/analytics')
    
    # Chuẩn bị images paths cho report
    images_paths = {
        'team_comparison': 'output_videos/case_study_1_team_comparison.png',
        'mvp_card': 'output_videos/case_study_2_mvp_card.png',
        'top5_ranking': 'output_videos/case_study_2_top5_ranking.png',
        'passing_network': 'output_videos/case_study_3_passing_network.png',
        'formations': 'output_videos/case_study_3_formations.png',
        'dashboard': dashboard_path
    }
    
    # Tạo HTML report
    html_report_path = report_gen.generate_html_report(
        selected_stats,
        team_analyzer,
        mvp_analyzer,
        tactical_analyzer,
        charts_paths=individual_charts,
        images_paths=images_paths
    )
    
    # Thử tạo PDF report (nếu có weasyprint)
    pdf_report_path = report_gen.generate_pdf_report(html_report_path)
    
    print("\n" + "="*80)
    print("HOÀN TẤT PHÂN TÍCH!")
    print("="*80)
    print(f"\n📊 Case Studies:")
    print(f"   - Team Comparison: output_videos/case_study_1_team_comparison.png")
    print(f"   - MVP Analysis: output_videos/case_study_2_mvp_card.png")
    print(f"   - Tactical Analysis: output_videos/case_study_3_passing_network.png")
    print(f"\n📁 Data Export:")
    print(f"   - Folder: output_videos/analytics/")
    print(f"   - JSON, CSV files với dữ liệu chi tiết")
    print(f"\n📈 Dashboard:")
    print(f"   - Full Dashboard: {dashboard_path}")
    print(f"\n📄 Reports:")
    print(f"   - HTML Report: {html_report_path}")
    if pdf_report_path:
        print(f"   - PDF Report: {pdf_report_path}")
    print("\n" + "="*80 + "\n")


    # Draw output , vẽ kết quả đầu ra
    ## Draw object Tracks
    output_video_frames = tracker.draw_annotations(video_frames, tracks,team_ball_control)

    ## Draw Camera movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames,camera_movement_per_frame)

    ## Draw Speed and Distance
    speed_and_distance_estimator.draw_speed_and_distance(output_video_frames,tracks)
    
    ## Draw Player Stats on frames (vẽ bảng thống kê nhỏ lên góc video)
    print("Đang vẽ thống kê lên video...")
    for frame_num, frame in enumerate(output_video_frames):
        output_video_frames[frame_num] = stats_analyzer.draw_stats_on_frame(
            frame, 
            position=(10, frame.shape[0] - 270),  # Tăng từ 200 lên 270 để hiển thị đủ 5 cầu thủ
            max_players=5
        )

    # Save video
    save_video(output_video_frames, 'output_videos/output_video.avi')

if __name__ == '__main__': # nếu file này được chạy trực tiếp, thì gọi hàm main
    main()
