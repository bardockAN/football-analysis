"""
Report Generator Module
Tạo báo cáo tự động dạng HTML và PDF
"""

import os
from datetime import datetime
import base64


class ReportGenerator:
    """
    Class để tạo báo cáo HTML và PDF tự động
    """
    
    def __init__(self, output_dir='output_videos/analytics'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html_report(self, player_stats, team_comparison, mvp_analysis, 
                            tactical_analysis, charts_paths=None, images_paths=None):
        """
        Tạo báo cáo HTML đầy đủ
        
        Args:
            player_stats: Thống kê cầu thủ
            team_comparison: Dữ liệu so sánh đội
            mvp_analysis: Dữ liệu MVP
            tactical_analysis: Dữ liệu chiến thuật
            charts_paths: Dictionary chứa đường dẫn các charts
            images_paths: Dictionary chứa đường dẫn các hình ảnh phân tích
        
        Returns:
            Đường dẫn file HTML
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.output_dir}/report_{timestamp}.html"
        
        html_content = self._generate_html_content(
            player_stats, team_comparison, mvp_analysis, 
            tactical_analysis, charts_paths, images_paths
        )
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✓ Generated HTML report: {filename}")
        return filename
    
    def _generate_html_content(self, player_stats, team_comparison, mvp_analysis, 
                               tactical_analysis, charts_paths, images_paths):
        """Tạo nội dung HTML"""
        
        # Đọc và encode images thành base64 nếu có
        encoded_images = {}
        if charts_paths:
            for key, path in charts_paths.items():
                if path and os.path.exists(path):
                    with open(path, 'rb') as img_file:
                        encoded_images[key] = base64.b64encode(img_file.read()).decode()
        
        if images_paths:
            for key, path in images_paths.items():
                if path and os.path.exists(path):
                    with open(path, 'rb') as img_file:
                        encoded_images[key] = base64.b64encode(img_file.read()).decode()
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Match Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        .section {{
            margin-bottom: 50px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #667eea;
        }}
        
        .section h2 {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e0e0e0;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        
        .stat-card h3 {{
            color: #667eea;
            font-size: 1.2em;
            margin-bottom: 10px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        tr:hover {{
            background: #f5f5f5;
        }}
        
        .team-badge {{
            display: inline-block;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            color: white;
            font-weight: bold;
            margin-right: 10px;
        }}
        
        .team-1 {{
            background: #5DADE2;
        }}
        
        .team-2 {{
            background: #52BE80;
        }}
        
        .mvp-highlight {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .mvp-highlight h3 {{
            font-size: 2em;
            margin-bottom: 15px;
        }}
        
        .mvp-score {{
            font-size: 3em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .chart-container {{
            margin: 30px 0;
            text-align: center;
        }}
        
        .chart-container img {{
            max-width: 100%;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .footer {{
            background: #2c3e50;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
            font-weight: bold;
            margin: 0 5px;
        }}
        
        .badge-gold {{
            background: #FFD700;
            color: #333;
        }}
        
        .badge-silver {{
            background: #C0C0C0;
            color: #333;
        }}
        
        .badge-bronze {{
            background: #CD7F32;
            color: white;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚽ FOOTBALL MATCH ANALYSIS REPORT</h1>
            <p>Generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
        </div>
        
        <div class="content">
"""
        
        # Executive Summary Section
        html += self._generate_executive_summary(team_comparison, mvp_analysis)
        
        # Team Comparison Section
        html += self._generate_team_comparison_section(team_comparison)
        
        # MVP Analysis Section
        html += self._generate_mvp_section(mvp_analysis)
        
        # Player Statistics Section
        html += self._generate_player_stats_section(player_stats)
        
        # Tactical Analysis Section
        html += self._generate_tactical_section(tactical_analysis)
        
        # Charts Section
        if encoded_images:
            html += self._generate_charts_section(encoded_images)
        
        html += """
        </div>
        
        <div class="footer">
            <p>&copy; 2026 Football Analysis System | Advanced Sports Analytics</p>
        </div>
    </div>
</body>
</html>
"""
        
        return html
    
    def _generate_executive_summary(self, team_comparison, mvp_analysis):
        """Tạo phần tóm tắt điều hành"""
        html = """
            <div class="section">
                <h2>📊 Executive Summary</h2>
                <div class="stats-grid">
"""
        
        if hasattr(team_comparison, 'team_stats') and team_comparison.team_stats:
            team1_poss = team_comparison.team_stats[1]['possession_percentage']
            team2_poss = team_comparison.team_stats[2]['possession_percentage']
            
            html += f"""
                    <div class="stat-card">
                        <h3>Team 1 Possession</h3>
                        <div class="stat-value">{team1_poss:.1f}%</div>
                        <div class="stat-label">Ball Control</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Team 2 Possession</h3>
                        <div class="stat-value">{team2_poss:.1f}%</div>
                        <div class="stat-label">Ball Control</div>
                    </div>
"""
        
        if hasattr(mvp_analysis, 'mvp_data') and mvp_analysis.mvp_data:
            mvp = mvp_analysis.mvp_data
            html += f"""
                    <div class="stat-card">
                        <h3>Match MVP</h3>
                        <div class="stat-value">Player {mvp['player_id']}</div>
                        <div class="stat-label">MVP Score: {mvp['mvp_score']:.1f}/100</div>
                    </div>
"""
        
        html += """
                </div>
            </div>
"""
        return html
    
    def _generate_team_comparison_section(self, team_comparison):
        """Tạo phần so sánh đội"""
        if not hasattr(team_comparison, 'team_stats') or not team_comparison.team_stats:
            return ""
        
        html = """
            <div class="section">
                <h2>🔄 Team Performance Comparison</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Team 1</th>
                            <th>Team 2</th>
                            <th>Difference</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        team1 = team_comparison.team_stats[1]
        team2 = team_comparison.team_stats[2]
        
        metrics = [
            ('Number of Players', 'num_players', ''),
            ('Ball Touches', 'ball_touches', ''),
            ('Possession', 'possession_percentage', '%'),
            ('Total Distance', 'total_distance', 'm'),
            ('Avg Distance/Player', 'avg_distance_per_player', 'm'),
            ('Average Speed', 'average_speed', 'km/h')
        ]
        
        for label, key, unit in metrics:
            val1 = team1.get(key, 0)
            val2 = team2.get(key, 0)
            diff = val1 - val2
            diff_sign = '+' if diff > 0 else ''
            
            # Format values properly
            val1_str = f"{val1:.1f}" if isinstance(val1, float) else str(val1)
            val2_str = f"{val2:.1f}" if isinstance(val2, float) else str(val2)
            diff_str = f"{diff:.1f}" if isinstance(diff, float) else str(diff)
            
            html += f"""
                        <tr>
                            <td><strong>{label}</strong></td>
                            <td>{val1_str}{unit}</td>
                            <td>{val2_str}{unit}</td>
                            <td style="color: {'#52BE80' if diff > 0 else '#E74C3C'}">
                                {diff_sign}{diff_str}{unit}
                            </td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
"""
        return html
    
    def _generate_mvp_section(self, mvp_analysis):
        """Tạo phần MVP"""
        if not hasattr(mvp_analysis, 'mvp_data') or not mvp_analysis.mvp_data:
            return ""
        
        mvp = mvp_analysis.mvp_data
        
        html = f"""
            <div class="section">
                <h2>🏆 Match MVP Analysis</h2>
                <div class="mvp-highlight">
                    <h3>Most Valuable Player</h3>
                    <div class="mvp-score">Player #{mvp['player_id']}</div>
                    <p>MVP Score: {mvp['mvp_score']:.1f}/100</p>
                    <p>Team {mvp['team']}</p>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>Ball Touches</h3>
                        <div class="stat-value">{mvp['ball_touches']}</div>
                        <div class="stat-label">Times</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Possession</h3>
                        <div class="stat-value">{mvp['possession_percentage']:.1f}%</div>
                        <div class="stat-label">Ball Control</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Distance</h3>
                        <div class="stat-value">{mvp['total_distance']:.0f}m</div>
                        <div class="stat-label">Covered</div>
                    </div>
                    
                    <div class="stat-card">
                        <h3>Speed</h3>
                        <div class="stat-value">{mvp['average_speed']:.1f}</div>
                        <div class="stat-label">km/h Average</div>
                    </div>
                </div>
"""
        
        if hasattr(mvp_analysis, 'all_players_ranked') and len(mvp_analysis.all_players_ranked) > 1:
            html += """
                <h3 style="margin-top: 30px;">Top 5 Players Ranking</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Player</th>
                            <th>Team</th>
                            <th>MVP Score</th>
                            <th>Touches</th>
                            <th>Distance (m)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
            
            medals = ['🥇', '🥈', '🥉']
            for rank, player in enumerate(mvp_analysis.all_players_ranked[:5], 1):
                medal = medals[rank-1] if rank <= 3 else f"{rank}"
                html += f"""
                        <tr>
                            <td><strong>{medal}</strong></td>
                            <td>Player {player['player_id']}</td>
                            <td><span class="team-badge team-{player['team']}">T{player['team']}</span></td>
                            <td><strong>{player['mvp_score']:.1f}</strong></td>
                            <td>{player['ball_touches']}</td>
                            <td>{player['total_distance']:.0f}</td>
                        </tr>
"""
            
            html += """
                    </tbody>
                </table>
"""
        
        html += """
            </div>
"""
        return html
    
    def _generate_player_stats_section(self, player_stats):
        """Tạo phần thống kê cầu thủ"""
        if not player_stats:
            return ""
        
        html = """
            <div class="section">
                <h2>👥 Player Statistics</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Player ID</th>
                            <th>Team</th>
                            <th>Ball Touches</th>
                            <th>Possession %</th>
                            <th>Distance (m)</th>
                            <th>Avg Speed (km/h)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
        
        # Sort by distance
        sorted_players = sorted(player_stats.items(), 
                               key=lambda x: x[1]['total_distance'], 
                               reverse=True)
        
        for player_id, stats in sorted_players:
            html += f"""
                        <tr>
                            <td><strong>Player {player_id}</strong></td>
                            <td><span class="team-badge team-{stats['team']}">T{stats['team']}</span></td>
                            <td>{stats['ball_touches']}</td>
                            <td>{stats['possession_percentage']:.1f}%</td>
                            <td>{stats['total_distance']:.1f}</td>
                            <td>{stats['average_speed']:.2f}</td>
                        </tr>
"""
        
        html += """
                    </tbody>
                </table>
            </div>
"""
        return html
    
    def _generate_tactical_section(self, tactical_analysis):
        """Tạo phần phân tích chiến thuật"""
        if not hasattr(tactical_analysis, 'formation_data'):
            return ""
        
        html = """
            <div class="section">
                <h2>⚡ Tactical Analysis</h2>
"""
        
        if tactical_analysis.formation_data:
            html += "<h3>Team Formations</h3>"
            
            for team_id, formation in tactical_analysis.formation_data.items():
                if formation and 'formation' in formation:
                    html += f"""
                <div class="stat-card" style="margin: 10px 0;">
                    <h3>Team {team_id}</h3>
                    <div class="stat-value">{formation['formation']}</div>
                    <div class="stat-label">Formation with {formation.get('num_players', 0)} players</div>
                </div>
"""
        
        if hasattr(tactical_analysis, 'passing_network') and tactical_analysis.passing_network:
            total_passes = sum(sum(passes.values()) for passes in tactical_analysis.passing_network.values())
            html += f"""
                <div class="stat-card" style="margin: 20px 0;">
                    <h3>Passing Network</h3>
                    <div class="stat-value">{total_passes}</div>
                    <div class="stat-label">Total Successful Passes Detected</div>
                </div>
"""
        
        html += """
            </div>
"""
        return html
    
    def _generate_charts_section(self, encoded_images):
        """Tạo phần charts"""
        html = """
            <div class="section">
                <h2>📈 Visual Analytics</h2>
"""
        
        for key, img_data in encoded_images.items():
            title = key.replace('_', ' ').title()
            html += f"""
                <div class="chart-container">
                    <h3>{title}</h3>
                    <img src="data:image/png;base64,{img_data}" alt="{title}">
                </div>
"""
        
        html += """
            </div>
"""
        return html
    
    def generate_pdf_report(self, html_path):
        """
        Chuyển HTML thành PDF (yêu cầu thư viện weasyprint hoặc pdfkit)
        
        Args:
            html_path: Đường dẫn file HTML
        
        Returns:
            Đường dẫn file PDF hoặc None nếu không thành công
        """
        try:
            from weasyprint import HTML
            
            pdf_path = html_path.replace('.html', '.pdf')
            HTML(html_path).write_pdf(pdf_path)
            
            print(f"✓ Generated PDF report: {pdf_path}")
            return pdf_path
            
        except ImportError:
            print("⚠ WeasyPrint not installed. PDF generation skipped.")
            print("  Install with: pip install weasyprint")
            return None
        except Exception as e:
            print(f"⚠ Error generating PDF: {e}")
            return None
