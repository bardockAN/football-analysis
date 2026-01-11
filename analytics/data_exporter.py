"""
Data Export Module
Module để export dữ liệu ra JSON và CSV với nhiều metrics chi tiết
"""

import json
import csv
import os
import numpy as np
from datetime import datetime


class DataExporter:
    """
    Class để export dữ liệu phân tích ra nhiều định dạng
    """
    
    def __init__(self, output_dir='output_videos/analytics'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    @staticmethod
    def convert_numpy_types(obj):
        """Convert numpy types to Python native types for JSON serialization"""
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            # Convert both keys and values - keys must also be Python native types
            return {
                (int(key) if isinstance(key, np.integer) else str(key) if not isinstance(key, (str, int, float, bool, type(None))) else key): 
                DataExporter.convert_numpy_types(value) 
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [DataExporter.convert_numpy_types(item) for item in obj]
        elif isinstance(obj, set):
            return [DataExporter.convert_numpy_types(item) for item in obj]
        return obj
        
    def export_all_data(self, player_stats, team_comparison, mvp_analysis, tactical_analysis):
        """
        Export tất cả dữ liệu ra JSON và CSV
        
        Args:
            player_stats: Thống kê cầu thủ
            team_comparison: Dữ liệu so sánh đội
            mvp_analysis: Dữ liệu phân tích MVP
            tactical_analysis: Dữ liệu phân tích chiến thuật
        
        Returns:
            Dictionary chứa đường dẫn các file đã export
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        exported_files = {}
        
        # Export player stats
        exported_files['player_stats_json'] = self.export_player_stats_json(player_stats, timestamp)
        exported_files['player_stats_csv'] = self.export_player_stats_csv(player_stats, timestamp)
        
        # Export team comparison
        exported_files['team_comparison_json'] = self.export_team_comparison_json(team_comparison, timestamp)
        exported_files['team_comparison_csv'] = self.export_team_comparison_csv(team_comparison, timestamp)
        
        # Export MVP analysis
        exported_files['mvp_analysis_json'] = self.export_mvp_analysis_json(mvp_analysis, timestamp)
        
        # Export tactical analysis
        exported_files['tactical_analysis_json'] = self.export_tactical_analysis_json(tactical_analysis, timestamp)
        exported_files['passing_network_csv'] = self.export_passing_network_csv(tactical_analysis, timestamp)
        
        # Export comprehensive JSON
        exported_files['comprehensive_json'] = self.export_comprehensive_json(
            player_stats, team_comparison, mvp_analysis, tactical_analysis, timestamp
        )
        
        return exported_files
    
    def export_player_stats_json(self, player_stats, timestamp):
        """Export player stats ra JSON"""
        filename = f"{self.output_dir}/player_stats_{timestamp}.json"
        
        # Chuẩn bị dữ liệu
        export_data = {
            'timestamp': timestamp,
            'analysis_type': 'player_statistics',
            'players': {}
        }
        
        for player_id, stats in player_stats.items():
            # Convert numpy types
            export_data['players'][str(int(player_id))] = {
                'player_id': int(player_id),
                'team': int(stats['team']),
                'ball_touches': int(stats['ball_touches']),
                'possession_frames': int(stats['possession_frames']),
                'possession_percentage': round(float(stats['possession_percentage']), 2),
                'total_distance_meters': round(float(stats['total_distance']), 2),
                'average_speed_kmh': round(float(stats['average_speed']), 2),
                'frames_tracked': int(stats['frames_tracked'])
            }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_player_stats_csv(self, player_stats, timestamp):
        """Export player stats ra CSV"""
        filename = f"{self.output_dir}/player_stats_{timestamp}.csv"
        
        fieldnames = [
            'player_id', 'team', 'ball_touches', 'possession_frames',
            'possession_percentage', 'total_distance_meters', 
            'average_speed_kmh', 'frames_tracked'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for player_id, stats in sorted(player_stats.items()):
                writer.writerow({
                    'player_id': int(player_id),
                    'team': int(stats['team']),
                    'ball_touches': int(stats['ball_touches']),
                    'possession_frames': int(stats['possession_frames']),
                    'possession_percentage': round(float(stats['possession_percentage']), 2),
                    'total_distance_meters': round(float(stats['total_distance']), 2),
                    'average_speed_kmh': round(float(stats['average_speed']), 2),
                    'frames_tracked': int(stats['frames_tracked'])
                })
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_team_comparison_json(self, team_comparison, timestamp):
        """Export team comparison ra JSON"""
        filename = f"{self.output_dir}/team_comparison_{timestamp}.json"
        
        export_data = {
            'timestamp': timestamp,
            'analysis_type': 'team_comparison',
            'teams': {}
        }
        
        # Convert numpy types in team comparison data
        if hasattr(team_comparison, 'export_to_dict'):
            raw_data = team_comparison.export_to_dict()
            export_data['teams'] = self.convert_numpy_types(raw_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_team_comparison_csv(self, team_comparison, timestamp):
        """Export team comparison ra CSV"""
        filename = f"{self.output_dir}/team_comparison_{timestamp}.csv"
        
        if not hasattr(team_comparison, 'team_stats'):
            return filename
        
        fieldnames = [
            'team_id', 'num_players', 'ball_touches', 'possession_percentage',
            'total_distance', 'avg_distance_per_player', 'average_speed'
        ]
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for team_id, stats in team_comparison.team_stats.items():
                writer.writerow({
                    'team_id': team_id,
                    'num_players': stats['num_players'],
                    'ball_touches': stats['ball_touches'],
                    'possession_percentage': round(stats['possession_percentage'], 2),
                    'total_distance': round(stats['total_distance'], 2),
                    'avg_distance_per_player': round(stats['avg_distance_per_player'], 2),
                    'average_speed': round(stats['average_speed'], 2)
                })
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_mvp_analysis_json(self, mvp_analysis, timestamp):
        """Export MVP analysis ra JSON"""
        filename = f"{self.output_dir}/mvp_analysis_{timestamp}.json"
        
        export_data = {
            'timestamp': timestamp,
            'analysis_type': 'mvp_analysis',
            'data': {}
        }
        
        # Convert numpy types in MVP data
        if hasattr(mvp_analysis, 'export_to_dict'):
            raw_data = mvp_analysis.export_to_dict()
            export_data['data'] = self.convert_numpy_types(raw_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_tactical_analysis_json(self, tactical_analysis, timestamp):
        """Export tactical analysis ra JSON"""
        filename = f"{self.output_dir}/tactical_analysis_{timestamp}.json"
        
        export_data = {
            'timestamp': timestamp,
            'analysis_type': 'tactical_analysis',
            'data': {}
        }
        
        # Convert numpy types in tactical data
        if hasattr(tactical_analysis, 'export_to_dict'):
            raw_data = tactical_analysis.export_to_dict()
            export_data['data'] = self.convert_numpy_types(raw_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_passing_network_csv(self, tactical_analysis, timestamp):
        """Export passing network ra CSV"""
        filename = f"{self.output_dir}/passing_network_{timestamp}.csv"
        
        if not hasattr(tactical_analysis, 'passing_network'):
            return filename
        
        fieldnames = ['from_player', 'to_player', 'pass_count']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for from_player, passes in tactical_analysis.passing_network.items():
                for to_player, count in passes.items():
                    writer.writerow({
                        'from_player': int(from_player) if isinstance(from_player, (np.integer, np.int64)) else from_player,
                        'to_player': int(to_player) if isinstance(to_player, (np.integer, np.int64)) else to_player,
                        'pass_count': int(count) if isinstance(count, (np.integer, np.int64)) else count
                    })
        
        print(f"✓ Exported: {filename}")
        return filename
    
    def export_comprehensive_json(self, player_stats, team_comparison, mvp_analysis, tactical_analysis, timestamp):
        """Export tất cả dữ liệu vào một file JSON tổng hợp"""
        filename = f"{self.output_dir}/comprehensive_analysis_{timestamp}.json"
        
        export_data = {
            'metadata': {
                'timestamp': timestamp,
                'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'version': '1.0'
            },
            'player_statistics': {},
            'team_comparison': {},
            'mvp_analysis': {},
            'tactical_analysis': {}
        }
        
        # Player stats
        for player_id, stats in player_stats.items():
            export_data['player_statistics'][str(int(player_id))] = {
                'player_id': int(player_id),
                'team': int(stats['team']),
                'ball_touches': int(stats['ball_touches']),
                'possession_percentage': round(float(stats['possession_percentage']), 2),
                'total_distance_meters': round(float(stats['total_distance']), 2),
                'average_speed_kmh': round(float(stats['average_speed']), 2)
            }
        
        # Team comparison - convert numpy types
        if hasattr(team_comparison, 'export_to_dict'):
            export_data['team_comparison'] = self.convert_numpy_types(team_comparison.export_to_dict())
        
        # MVP analysis - convert numpy types
        if hasattr(mvp_analysis, 'export_to_dict'):
            export_data['mvp_analysis'] = self.convert_numpy_types(mvp_analysis.export_to_dict())
        
        # Tactical analysis - convert numpy types
        if hasattr(tactical_analysis, 'export_to_dict'):
            export_data['tactical_analysis'] = self.convert_numpy_types(tactical_analysis.export_to_dict())
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ Exported comprehensive data: {filename}")
        return filename
    
    def create_export_summary(self, exported_files):
        """Tạo file summary về những gì đã export"""
        filename = f"{self.output_dir}/export_summary.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("FOOTBALL ANALYSIS - EXPORT SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("Exported Files:\n")
            f.write("-" * 60 + "\n")
            
            for file_type, filepath in exported_files.items():
                if filepath and os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    f.write(f"\n{file_type}:\n")
                    f.write(f"  Path: {filepath}\n")
                    f.write(f"  Size: {file_size:,} bytes\n")
            
            f.write("\n" + "=" * 60 + "\n")
        
        print(f"✓ Created export summary: {filename}")
        return filename
