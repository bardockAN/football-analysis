"""
Dashboard Generator Module
Tạo dashboard visualization với charts và graphs sử dụng matplotlib
"""

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
import os


class DashboardGenerator:
    """
    Class để tạo dashboard visualization
    """
    
    def __init__(self, output_dir='output_videos/analytics'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid')
        
    def create_full_dashboard(self, player_stats, team_comparison, mvp_analysis):
        """
        Tạo dashboard tổng hợp với nhiều charts
        
        Args:
            player_stats: Thống kê cầu thủ
            team_comparison: Dữ liệu so sánh đội
            mvp_analysis: Dữ liệu MVP
        
        Returns:
            Đường dẫn file dashboard
        """
        # Tạo figure với nhiều subplots
        fig = plt.figure(figsize=(20, 12))
        fig.suptitle('FOOTBALL MATCH ANALYSIS DASHBOARD', fontsize=24, fontweight='bold', y=0.98)
        
        # Create grid
        gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)
        
        # 1. Team Comparison Bar Chart (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        self._plot_team_comparison(ax1, team_comparison)
        
        # 2. Player Distance Chart (top middle)
        ax2 = fig.add_subplot(gs[0, 1])
        self._plot_player_distances(ax2, player_stats)
        
        # 3. Ball Possession Pie Chart (top right)
        ax3 = fig.add_subplot(gs[0, 2])
        self._plot_possession_pie(ax3, team_comparison)
        
        # 4. Player Speed Distribution (middle left)
        ax4 = fig.add_subplot(gs[1, 0])
        self._plot_speed_distribution(ax4, player_stats)
        
        # 5. MVP Score Ranking (middle center)
        ax5 = fig.add_subplot(gs[1, 1])
        self._plot_mvp_ranking(ax5, mvp_analysis)
        
        # 6. Ball Touches Comparison (middle right)
        ax6 = fig.add_subplot(gs[1, 2])
        self._plot_ball_touches(ax6, player_stats)
        
        # 7. Team Statistics Table (bottom left)
        ax7 = fig.add_subplot(gs[2, 0])
        self._plot_team_stats_table(ax7, team_comparison)
        
        # 8. Top Players Table (bottom center)
        ax8 = fig.add_subplot(gs[2, 1])
        self._plot_top_players_table(ax8, player_stats)
        
        # 9. Performance Radar Chart (bottom right)
        ax9 = fig.add_subplot(gs[2, 2], projection='polar')
        self._plot_performance_radar(ax9, mvp_analysis)
        
        # Save
        filename = f"{self.output_dir}/dashboard_full.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ Generated dashboard: {filename}")
        return filename
    
    def _plot_team_comparison(self, ax, team_comparison):
        """Vẽ biểu đồ so sánh giữa 2 đội"""
        if not hasattr(team_comparison, 'team_stats') or not team_comparison.team_stats:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title('Team Comparison')
            return
        
        teams = list(team_comparison.team_stats.keys())
        metrics = ['Ball Touches', 'Possession %', 'Avg Distance']
        
        team1_data = [
            team_comparison.team_stats[1]['ball_touches'],
            team_comparison.team_stats[1]['possession_percentage'],
            team_comparison.team_stats[1]['avg_distance_per_player']
        ]
        
        team2_data = [
            team_comparison.team_stats[2]['ball_touches'],
            team_comparison.team_stats[2]['possession_percentage'],
            team_comparison.team_stats[2]['avg_distance_per_player']
        ]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        # Normalize data for better visualization
        max_vals = [max(team1_data[i], team2_data[i]) for i in range(len(metrics))]
        team1_normalized = [team1_data[i] / max(max_vals[i], 1) * 100 for i in range(len(metrics))]
        team2_normalized = [team2_data[i] / max(max_vals[i], 1) * 100 for i in range(len(metrics))]
        
        bars1 = ax.bar(x - width/2, team1_normalized, width, label='Team 1', color='#5DADE2')
        bars2 = ax.bar(x + width/2, team2_normalized, width, label='Team 2', color='#52BE80')
        
        ax.set_ylabel('Normalized Score', fontweight='bold')
        ax.set_title('Team Performance Comparison', fontweight='bold', fontsize=12)
        ax.set_xticks(x)
        ax.set_xticklabels(metrics, rotation=15, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=8)
    
    def _plot_player_distances(self, ax, player_stats):
        """Vẽ biểu đồ quãng đường di chuyển của cầu thủ"""
        if not player_stats:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title('Player Distances')
            return
        
        # Sort by distance
        sorted_players = sorted(player_stats.items(), 
                               key=lambda x: x[1]['total_distance'], 
                               reverse=True)[:8]
        
        player_ids = [f"P{pid}" for pid, _ in sorted_players]
        distances = [stats['total_distance'] for _, stats in sorted_players]
        teams = [stats['team'] for _, stats in sorted_players]
        
        colors = ['#5DADE2' if team == 1 else '#52BE80' for team in teams]
        
        bars = ax.barh(player_ids, distances, color=colors)
        ax.set_xlabel('Distance (meters)', fontweight='bold')
        ax.set_title('Top Players by Distance Covered', fontweight='bold', fontsize=12)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (bar, dist) in enumerate(zip(bars, distances)):
            ax.text(dist, bar.get_y() + bar.get_height()/2., 
                   f'{dist:.1f}m',
                   ha='left', va='center', fontsize=8, fontweight='bold')
    
    def _plot_possession_pie(self, ax, team_comparison):
        """Vẽ biểu đồ tròn thể hiện tỷ lệ kiểm soát bóng"""
        if not hasattr(team_comparison, 'team_stats') or not team_comparison.team_stats:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title('Ball Possession')
            return
        
        team1_poss = team_comparison.team_stats[1]['possession_percentage']
        team2_poss = team_comparison.team_stats[2]['possession_percentage']
        
        sizes = [team1_poss, team2_poss]
        labels = [f'Team 1\n{team1_poss:.1f}%', f'Team 2\n{team2_poss:.1f}%']
        colors = ['#5DADE2', '#52BE80']
        explode = (0.05, 0.05)
        
        wedges, texts, autotexts = ax.pie(sizes, explode=explode, labels=labels, colors=colors,
                                           autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Ball Possession Distribution', fontweight='bold', fontsize=12)
    
    def _plot_speed_distribution(self, ax, player_stats):
        """Vẽ histogram phân phối tốc độ"""
        if not player_stats:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title('Speed Distribution')
            return
        
        speeds_team1 = [stats['average_speed'] for stats in player_stats.values() if stats['team'] == 1]
        speeds_team2 = [stats['average_speed'] for stats in player_stats.values() if stats['team'] == 2]
        
        ax.hist([speeds_team1, speeds_team2], bins=10, label=['Team 1', 'Team 2'],
               color=['#5DADE2', '#52BE80'], alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Average Speed (km/h)', fontweight='bold')
        ax.set_ylabel('Number of Players', fontweight='bold')
        ax.set_title('Speed Distribution by Team', fontweight='bold', fontsize=12)
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
    
    def _plot_mvp_ranking(self, ax, mvp_analysis):
        """Vẽ bảng xếp hạng MVP"""
        if not hasattr(mvp_analysis, 'all_players_ranked') or not mvp_analysis.all_players_ranked:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title('MVP Ranking')
            return
        
        top_5 = mvp_analysis.all_players_ranked[:5]
        
        player_ids = [f"Player {p['player_id']}" for p in top_5]
        scores = [p['mvp_score'] for p in top_5]
        colors_list = ['gold', 'silver', '#CD7F32', '#4A4A4A', '#6A6A6A']
        
        bars = ax.barh(player_ids, scores, color=colors_list)
        ax.set_xlabel('MVP Score', fontweight='bold')
        ax.set_title('Top 5 MVP Ranking', fontweight='bold', fontsize=12)
        ax.set_xlim(0, 100)
        ax.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for bar, score in zip(bars, scores):
            ax.text(score, bar.get_y() + bar.get_height()/2., 
                   f'{score:.1f}',
                   ha='left', va='center', fontsize=9, fontweight='bold')
    
    def _plot_ball_touches(self, ax, player_stats):
        """Vẽ biểu đồ số lần chạm bóng"""
        if not player_stats:
            ax.text(0.5, 0.5, 'No data', ha='center', va='center')
            ax.set_title('Ball Touches')
            return
        
        # Sort by touches
        sorted_players = sorted(player_stats.items(), 
                               key=lambda x: x[1]['ball_touches'], 
                               reverse=True)[:8]
        
        player_ids = [f"P{pid}" for pid, _ in sorted_players]
        touches = [stats['ball_touches'] for _, stats in sorted_players]
        teams = [stats['team'] for _, stats in sorted_players]
        
        colors = ['#5DADE2' if team == 1 else '#52BE80' for team in teams]
        
        bars = ax.bar(range(len(player_ids)), touches, color=colors, edgecolor='black')
        ax.set_ylabel('Number of Touches', fontweight='bold')
        ax.set_title('Top Players by Ball Touches', fontweight='bold', fontsize=12)
        ax.set_xticks(range(len(player_ids)))
        ax.set_xticklabels(player_ids, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        # Add value labels
        for bar, touch in zip(bars, touches):
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                   f'{touch}',
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    def _plot_team_stats_table(self, ax, team_comparison):
        """Vẽ bảng thống kê đội"""
        ax.axis('tight')
        ax.axis('off')
        
        if not hasattr(team_comparison, 'team_stats') or not team_comparison.team_stats:
            ax.text(0.5, 0.5, 'No team data available', ha='center', va='center')
            return
        
        data = []
        headers = ['Metric', 'Team 1', 'Team 2']
        
        metrics = [
            ('Players', 'num_players'),
            ('Ball Touches', 'ball_touches'),
            ('Possession %', 'possession_percentage'),
            ('Total Distance', 'total_distance'),
            ('Avg Speed', 'average_speed')
        ]
        
        for label, key in metrics:
            val1 = team_comparison.team_stats[1].get(key, 0)
            val2 = team_comparison.team_stats[2].get(key, 0)
            
            if key == 'possession_percentage':
                data.append([label, f"{val1:.1f}%", f"{val2:.1f}%"])
            elif key in ['total_distance', 'average_speed']:
                data.append([label, f"{val1:.1f}", f"{val2:.1f}"])
            else:
                data.append([label, str(val1), str(val2)])
        
        table = ax.table(cellText=data, colLabels=headers, loc='center',
                        cellLoc='center', colWidths=[0.4, 0.3, 0.3])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header
        for i in range(3):
            table[(0, i)].set_facecolor('#34495E')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, len(data) + 1):
            for j in range(3):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#ECF0F1')
                else:
                    table[(i, j)].set_facecolor('#FFFFFF')
        
        ax.set_title('Team Statistics Summary', fontweight='bold', fontsize=12, pad=20)
    
    def _plot_top_players_table(self, ax, player_stats):
        """Vẽ bảng top cầu thủ"""
        ax.axis('tight')
        ax.axis('off')
        
        if not player_stats:
            ax.text(0.5, 0.5, 'No player data available', ha='center', va='center')
            return
        
        # Get top 5 by distance
        sorted_players = sorted(player_stats.items(), 
                               key=lambda x: x[1]['total_distance'], 
                               reverse=True)[:5]
        
        data = []
        headers = ['Player', 'Team', 'Distance', 'Speed', 'Touches']
        
        for pid, stats in sorted_players:
            data.append([
                f"P{pid}",
                f"T{stats['team']}",
                f"{stats['total_distance']:.0f}m",
                f"{stats['average_speed']:.1f}",
                str(stats['ball_touches'])
            ])
        
        table = ax.table(cellText=data, colLabels=headers, loc='center',
                        cellLoc='center', colWidths=[0.15, 0.15, 0.25, 0.2, 0.25])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Style header
        for i in range(5):
            table[(0, i)].set_facecolor('#34495E')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        # Alternate row colors
        for i in range(1, 6):
            for j in range(5):
                if i % 2 == 0:
                    table[(i, j)].set_facecolor('#ECF0F1')
                else:
                    table[(i, j)].set_facecolor('#FFFFFF')
        
        ax.set_title('Top 5 Players', fontweight='bold', fontsize=12, pad=20)
    
    def _plot_performance_radar(self, ax, mvp_analysis):
        """Vẽ radar chart cho MVP"""
        if not hasattr(mvp_analysis, 'mvp_data') or not mvp_analysis.mvp_data:
            ax.text(0, 0, 'No MVP data', ha='center', va='center')
            ax.set_title('MVP Performance')
            return
        
        mvp = mvp_analysis.mvp_data
        
        # Categories
        categories = ['Touches', 'Possession', 'Distance', 'Speed']
        
        # Normalize values to 0-100 scale
        values = [
            min(mvp['ball_touches'] / 10 * 100, 100),
            mvp['possession_percentage'],
            min(mvp['total_distance'] / 30000 * 100, 100),
            min(mvp['average_speed'] / 30 * 100, 100)
        ]
        
        # Number of variables
        num_vars = len(categories)
        
        # Compute angle for each axis
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]
        
        # Plot
        ax.plot(angles, values, 'o-', linewidth=2, color='#E74C3C', label=f'Player {mvp["player_id"]}')
        ax.fill(angles, values, alpha=0.25, color='#E74C3C')
        
        # Fix axis to go in the right order
        ax.set_theta_offset(np.pi / 2)
        ax.set_theta_direction(-1)
        
        # Draw axis lines for each angle and label
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories, fontsize=9)
        
        # Set ylim
        ax.set_ylim(0, 100)
        
        # Add gridlines
        ax.set_rgrids([20, 40, 60, 80, 100], angle=0, fontsize=7)
        
        ax.set_title(f'MVP Performance Radar\n(Player {mvp["player_id"]})', 
                    fontweight='bold', fontsize=12, pad=20)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
    
    def create_individual_charts(self, player_stats, team_comparison, mvp_analysis):
        """Tạo các chart riêng lẻ"""
        charts = {}
        
        # Team comparison chart
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_team_comparison(ax, team_comparison)
        filename = f"{self.output_dir}/chart_team_comparison.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts['team_comparison'] = filename
        print(f"✓ Generated: {filename}")
        
        # Player distances chart
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_player_distances(ax, player_stats)
        filename = f"{self.output_dir}/chart_player_distances.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts['player_distances'] = filename
        print(f"✓ Generated: {filename}")
        
        # MVP ranking chart
        fig, ax = plt.subplots(figsize=(10, 6))
        self._plot_mvp_ranking(ax, mvp_analysis)
        filename = f"{self.output_dir}/chart_mvp_ranking.png"
        plt.savefig(filename, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        charts['mvp_ranking'] = filename
        print(f"✓ Generated: {filename}")
        
        return charts
