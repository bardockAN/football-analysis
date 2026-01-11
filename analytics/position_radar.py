"""
Player Position Radar Visualization Module
Visualize player positions on football pitch in radar/heatmap format
"""
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Arc
import seaborn as sns
from collections import defaultdict
from pathlib import Path

class PlayerPositionRadar:
    """Create radar visualizations of player positions on football pitch"""
    
    def __init__(self, pitch_length=105, pitch_width=68):
        """
        Initialize radar visualization
        
        Args:
            pitch_length: Length of pitch in meters (default 105m)
            pitch_width: Width of pitch in meters (default 68m)
        """
        self.pitch_length = pitch_length
        self.pitch_width = pitch_width
        
    def draw_pitch(self, ax, color='white', linewidth=2):
        """Draw football pitch markings"""
        # Pitch outline
        ax.add_patch(Rectangle((0, 0), self.pitch_length, self.pitch_width, 
                               fill=False, edgecolor=color, linewidth=linewidth))
        
        # Halfway line
        ax.plot([self.pitch_length/2, self.pitch_length/2], [0, self.pitch_width], 
               color=color, linewidth=linewidth)
        
        # Center circle
        center_circle = Circle((self.pitch_length/2, self.pitch_width/2), 9.15,
                              fill=False, edgecolor=color, linewidth=linewidth)
        ax.add_patch(center_circle)
        
        # Center spot
        ax.scatter(self.pitch_length/2, self.pitch_width/2, s=50, c=color, zorder=3)
        
        # Penalty areas
        # Left penalty area
        ax.add_patch(Rectangle((0, (self.pitch_width-40.3)/2), 16.5, 40.3,
                               fill=False, edgecolor=color, linewidth=linewidth))
        # Left goal area
        ax.add_patch(Rectangle((0, (self.pitch_width-18.3)/2), 5.5, 18.3,
                               fill=False, edgecolor=color, linewidth=linewidth))
        
        # Right penalty area
        ax.add_patch(Rectangle((self.pitch_length-16.5, (self.pitch_width-40.3)/2), 16.5, 40.3,
                               fill=False, edgecolor=color, linewidth=linewidth))
        # Right goal area
        ax.add_patch(Rectangle((self.pitch_length-5.5, (self.pitch_width-18.3)/2), 5.5, 18.3,
                               fill=False, edgecolor=color, linewidth=linewidth))
        
        # Penalty spots
        ax.scatter(11, self.pitch_width/2, s=50, c=color, zorder=3)
        ax.scatter(self.pitch_length-11, self.pitch_width/2, s=50, c=color, zorder=3)
        
        # Goals
        ax.plot([0, 0], [(self.pitch_width-7.32)/2, (self.pitch_width+7.32)/2],
               color=color, linewidth=linewidth+1)
        ax.plot([self.pitch_length, self.pitch_length], 
               [(self.pitch_width-7.32)/2, (self.pitch_width+7.32)/2],
               color=color, linewidth=linewidth+1)
        
        # Corner arcs
        corner_radius = 1
        corners = [
            (0, 0, 0, 90),
            (0, self.pitch_width, 270, 360),
            (self.pitch_length, 0, 90, 180),
            (self.pitch_length, self.pitch_width, 180, 270)
        ]
        for x, y, theta1, theta2 in corners:
            arc = Arc((x, y), corner_radius*2, corner_radius*2, 
                     theta1=theta1, theta2=theta2, color=color, linewidth=linewidth)
            ax.add_patch(arc)
        
        ax.set_xlim(-5, self.pitch_length + 5)
        ax.set_ylim(-5, self.pitch_width + 5)
        ax.set_aspect('equal')
        ax.axis('off')
    
    def create_heatmap(self, positions, team_id, grid_size=10, title="Player Heatmap"):
        """
        Create heatmap of player positions
        
        Args:
            positions: List of (x, y) tuples for player positions
            team_id: Team identifier for color coding
            grid_size: Size of grid cells
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=(14, 9), facecolor='#1e3d1e')
        ax.set_facecolor('#2e5d2e')
        
        # Create 2D histogram
        x_coords = [p[0] for p in positions]
        y_coords = [p[1] for p in positions]
        
        # Create grid
        x_bins = np.linspace(0, self.pitch_length, grid_size + 1)
        y_bins = np.linspace(0, self.pitch_width, grid_size + 1)
        
        heatmap, xedges, yedges = np.histogram2d(x_coords, y_coords, bins=[x_bins, y_bins])
        
        # Plot heatmap
        extent = [0, self.pitch_length, 0, self.pitch_width]
        
        if team_id == 1:
            cmap = 'Reds'
        else:
            cmap = 'Blues'
            
        im = ax.imshow(heatmap.T, extent=extent, origin='lower', 
                      cmap=cmap, alpha=0.6, aspect='auto')
        
        # Draw pitch
        self.draw_pitch(ax, color='white', linewidth=2)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
        cbar.set_label('Player Density', rotation=270, labelpad=20, 
                      color='white', fontsize=12, fontweight='bold')
        cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='white')
        
        ax.set_title(title, fontsize=16, fontweight='bold', color='white', pad=20)
        
        return fig, ax
    
    def create_position_plot(self, team1_positions, team2_positions, 
                           team1_name="Team 1", team2_name="Team 2",
                           title="Player Positions"):
        """
        Plot positions of both teams
        
        Args:
            team1_positions: List of (x, y) for team 1
            team2_positions: List of (x, y) for team 2
            team1_name: Name of team 1
            team2_name: Name of team 2
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=(14, 9), facecolor='#1e3d1e')
        ax.set_facecolor('#2e5d2e')
        
        # Draw pitch
        self.draw_pitch(ax, color='white', linewidth=2)
        
        # Plot team 1 (red)
        if team1_positions:
            x1 = [p[0] for p in team1_positions]
            y1 = [p[1] for p in team1_positions]
            ax.scatter(x1, y1, s=300, c='red', edgecolor='darkred', 
                      linewidth=2, alpha=0.8, label=team1_name, zorder=5)
            
            # Add player numbers
            for i, (x, y) in enumerate(team1_positions, 1):
                ax.text(x, y, str(i), ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white')
        
        # Plot team 2 (blue)
        if team2_positions:
            x2 = [p[0] for p in team2_positions]
            y2 = [p[1] for p in team2_positions]
            ax.scatter(x2, y2, s=300, c='blue', edgecolor='darkblue', 
                      linewidth=2, alpha=0.8, label=team2_name, zorder=5)
            
            # Add player numbers
            for i, (x, y) in enumerate(team2_positions, 1):
                ax.text(x, y, str(i), ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white')
        
        ax.set_title(title, fontsize=16, fontweight='bold', color='white', pad=20)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.02), 
                 ncol=2, fontsize=12, framealpha=0.9)
        
        return fig, ax
    
    def create_formation_radar(self, positions, team_id, formation_name="4-4-2",
                              title="Team Formation"):
        """
        Create radar-style formation visualization
        
        Args:
            positions: List of (x, y) tuples
            team_id: Team identifier
            formation_name: Formation name
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=(14, 9), facecolor='#1e3d1e')
        ax.set_facecolor('#2e5d2e')
        
        # Draw pitch
        self.draw_pitch(ax, color='white', linewidth=2)
        
        # Color based on team
        if team_id == 1:
            color = 'red'
            edge_color = 'darkred'
        else:
            color = 'blue'
            edge_color = 'darkblue'
        
        # Group positions by vertical zones
        zones = defaultdict(list)
        zone_width = self.pitch_length / 5
        
        for x, y in positions:
            zone_idx = int(x // zone_width)
            zones[zone_idx].append((x, y))
        
        # Plot positions with size based on zone
        for zone_idx, zone_positions in zones.items():
            size = 400 - (zone_idx * 50)  # Vary size by zone
            x_coords = [p[0] for p in zone_positions]
            y_coords = [p[1] for p in zone_positions]
            
            ax.scatter(x_coords, y_coords, s=size, c=color, 
                      edgecolor=edge_color, linewidth=3, alpha=0.7, zorder=5)
            
            # Draw connections within zone
            if len(zone_positions) > 1:
                for i in range(len(zone_positions) - 1):
                    for j in range(i + 1, len(zone_positions)):
                        x1, y1 = zone_positions[i]
                        x2, y2 = zone_positions[j]
                        ax.plot([x1, x2], [y1, y2], color=color, 
                               alpha=0.3, linewidth=1, zorder=3)
        
        ax.set_title(f"{title} - Formation: {formation_name}", 
                    fontsize=16, fontweight='bold', color='white', pad=20)
        
        return fig, ax
    
    def create_movement_vectors(self, start_positions, end_positions, 
                               team_id, title="Player Movement"):
        """
        Visualize player movement with vectors
        
        Args:
            start_positions: List of starting (x, y)
            end_positions: List of ending (x, y)
            team_id: Team identifier
            title: Plot title
        """
        fig, ax = plt.subplots(figsize=(14, 9), facecolor='#1e3d1e')
        ax.set_facecolor('#2e5d2e')
        
        # Draw pitch
        self.draw_pitch(ax, color='white', linewidth=2)
        
        # Color based on team
        if team_id == 1:
            color = 'red'
        else:
            color = 'blue'
        
        # Plot start positions
        x_start = [p[0] for p in start_positions]
        y_start = [p[1] for p in start_positions]
        ax.scatter(x_start, y_start, s=200, c=color, alpha=0.5, zorder=4)
        
        # Plot end positions
        x_end = [p[0] for p in end_positions]
        y_end = [p[1] for p in end_positions]
        ax.scatter(x_end, y_end, s=200, c=color, edgecolor='white', 
                  linewidth=2, zorder=5)
        
        # Draw movement vectors
        for (x1, y1), (x2, y2) in zip(start_positions, end_positions):
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', color=color, 
                                     lw=2, alpha=0.7))
            
            # Calculate distance
            distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
            mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
            
            if distance > 2:  # Only show for significant movements
                ax.text(mid_x, mid_y, f'{distance:.1f}m', 
                       fontsize=8, color='white', 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7))
        
        ax.set_title(title, fontsize=16, fontweight='bold', color='white', pad=20)
        
        return fig, ax
    
    def analyze_from_tracks(self, tracks, frame_nums, output_dir):
        """
        Analyze player positions from tracking data
        
        Args:
            tracks: Dictionary of tracking data
            frame_nums: List of frame numbers to analyze
            output_dir: Output directory for visualizations
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        results = {}
        
        # Collect positions for each team
        team1_all_positions = []
        team2_all_positions = []
        
        for frame_num in frame_nums:
            if frame_num not in tracks['players']:
                continue
                
            frame_players = tracks['players'][frame_num]
            
            for track_id, player_data in frame_players.items():
                if 'position_transformed' in player_data:
                    x, y = player_data['position_transformed']
                    team_id = player_data.get('team', 1)
                    
                    if team_id == 1:
                        team1_all_positions.append((x, y))
                    else:
                        team2_all_positions.append((x, y))
        
        # Create visualizations
        print("Creating position radar visualizations...")
        
        # 1. Heatmap for team 1
        if team1_all_positions:
            fig, ax = self.create_heatmap(team1_all_positions, 1, 
                                         title="Team 1 Position Heatmap")
            fig.savefig(output_dir / 'team1_heatmap.png', dpi=300, 
                       bbox_inches='tight', facecolor='#1e3d1e')
            plt.close(fig)
            print("✓ Created team1_heatmap.png")
        
        # 2. Heatmap for team 2
        if team2_all_positions:
            fig, ax = self.create_heatmap(team2_all_positions, 2,
                                         title="Team 2 Position Heatmap")
            fig.savefig(output_dir / 'team2_heatmap.png', dpi=300,
                       bbox_inches='tight', facecolor='#1e3d1e')
            plt.close(fig)
            print("✓ Created team2_heatmap.png")
        
        # 3. Combined position plot (sample frame)
        if frame_nums and frame_nums[len(frame_nums)//2] in tracks['players']:
            mid_frame = frame_nums[len(frame_nums)//2]
            team1_pos = []
            team2_pos = []
            
            for track_id, player_data in tracks['players'][mid_frame].items():
                if 'position_transformed' in player_data:
                    x, y = player_data['position_transformed']
                    team_id = player_data.get('team', 1)
                    
                    if team_id == 1:
                        team1_pos.append((x, y))
                    else:
                        team2_pos.append((x, y))
            
            fig, ax = self.create_position_plot(team1_pos, team2_pos,
                                               title=f"Player Positions (Frame {mid_frame})")
            fig.savefig(output_dir / 'combined_positions.png', dpi=300,
                       bbox_inches='tight', facecolor='#1e3d1e')
            plt.close(fig)
            print("✓ Created combined_positions.png")
        
        results['team1_positions'] = len(team1_all_positions)
        results['team2_positions'] = len(team2_all_positions)
        results['output_dir'] = str(output_dir)
        
        return results
