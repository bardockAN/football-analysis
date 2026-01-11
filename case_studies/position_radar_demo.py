"""
Case Study: Player Position Analysis using Radar Visualization
Demonstrates tactical positioning and movement patterns
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from analytics.position_radar import PlayerPositionRadar
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_sample_data():
    """Generate sample player positions for different formations"""
    
    # 4-4-2 Formation (Team 1 - attacking left to right)
    formation_442 = [
        # Goalkeeper
        (10, 34),
        # Defenders
        (25, 10), (25, 24), (25, 44), (25, 58),
        # Midfielders
        (45, 12), (45, 26), (45, 42), (45, 56),
        # Forwards
        (70, 24), (70, 44)
    ]
    
    # 4-3-3 Formation (Team 2 - defending, left to right)
    formation_433 = [
        # Goalkeeper
        (95, 34),
        # Defenders
        (80, 10), (80, 24), (80, 44), (80, 58),
        # Midfielders
        (60, 18), (60, 34), (60, 50),
        # Forwards
        (40, 15), (40, 34), (40, 53)
    ]
    
    return formation_442, formation_433

def case_study_tactical_comparison():
    """Case Study 1: Compare tactical formations"""
    print("="*80)
    print("CASE STUDY 1: TACTICAL FORMATION COMPARISON")
    print("="*80)
    
    output_dir = Path('case_studies_output/tactical_comparison')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    radar = PlayerPositionRadar()
    team1_442, team2_433 = generate_sample_data()
    
    # Visualization 1: 4-4-2 Formation
    print("\n1. Analyzing 4-4-2 Formation...")
    fig, ax = radar.create_formation_radar(team1_442, 1, "4-4-2",
                                          title="Team 1 Tactical Setup")
    fig.savefig(output_dir / '442_formation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: 442_formation.png")
    
    # Visualization 2: 4-3-3 Formation
    print("\n2. Analyzing 4-3-3 Formation...")
    fig, ax = radar.create_formation_radar(team2_433, 2, "4-3-3",
                                          title="Team 2 Tactical Setup")
    fig.savefig(output_dir / '433_formation.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: 433_formation.png")
    
    # Visualization 3: Combined tactical view
    print("\n3. Creating combined tactical view...")
    fig, ax = radar.create_position_plot(team1_442, team2_433,
                                        "Team 1 (4-4-2)", "Team 2 (4-3-3)",
                                        title="Tactical Formation Comparison")
    fig.savefig(output_dir / 'tactical_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: tactical_comparison.png")
    
    print(f"\n✓ Case study completed! Files saved to: {output_dir}")
    
    return output_dir

def case_study_pressing_intensity():
    """Case Study 2: Analyze pressing intensity and player density"""
    print("\n" + "="*80)
    print("CASE STUDY 2: PRESSING INTENSITY ANALYSIS")
    print("="*80)
    
    output_dir = Path('case_studies_output/pressing_analysis')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    radar = PlayerPositionRadar()
    
    # Simulate high-press scenario
    print("\n1. Simulating high-press scenario...")
    
    # Team pressing high up the pitch
    pressing_positions = []
    for _ in range(200):  # Generate many position samples
        # Concentrate in opponent's half
        x = np.random.normal(70, 15)
        y = np.random.normal(34, 15)
        # Clip to pitch bounds
        x = np.clip(x, 0, 105)
        y = np.clip(y, 0, 68)
        pressing_positions.append((x, y))
    
    fig, ax = radar.create_heatmap(pressing_positions, 1, grid_size=15,
                                   title="High-Press Intensity Heatmap")
    fig.savefig(output_dir / 'high_press_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: high_press_heatmap.png")
    
    # Simulate deep defensive block
    print("\n2. Simulating deep defensive block...")
    
    defensive_positions = []
    for _ in range(200):
        # Concentrate in own half
        x = np.random.normal(25, 10)
        y = np.random.normal(34, 12)
        x = np.clip(x, 0, 105)
        y = np.clip(y, 0, 68)
        defensive_positions.append((x, y))
    
    fig, ax = radar.create_heatmap(defensive_positions, 2, grid_size=15,
                                   title="Deep Defensive Block Heatmap")
    fig.savefig(output_dir / 'defensive_block_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: defensive_block_heatmap.png")
    
    print(f"\n✓ Case study completed! Files saved to: {output_dir}")
    
    return output_dir

def case_study_player_movement():
    """Case Study 3: Track player movement patterns"""
    print("\n" + "="*80)
    print("CASE STUDY 3: PLAYER MOVEMENT PATTERNS")
    print("="*80)
    
    output_dir = Path('case_studies_output/movement_patterns')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    radar = PlayerPositionRadar()
    
    # Simulate attacking transition
    print("\n1. Simulating attacking transition...")
    
    start_positions = [
        (25, 15), (25, 30), (25, 38), (25, 53),  # Defenders
        (40, 20), (40, 34), (40, 48),  # Midfielders
        (50, 28), (50, 40)  # Forwards
    ]
    
    end_positions = [
        (30, 15), (35, 30), (35, 38), (30, 53),  # Defenders move up
        (60, 18), (65, 34), (60, 50),  # Midfielders push forward
        (80, 25), (85, 43)  # Forwards in attacking positions
    ]
    
    fig, ax = radar.create_movement_vectors(start_positions, end_positions, 1,
                                           title="Attacking Transition Movement")
    fig.savefig(output_dir / 'attacking_transition.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: attacking_transition.png")
    
    # Simulate defensive transition
    print("\n2. Simulating defensive transition...")
    
    start_positions_def = [
        (70, 20), (65, 34), (70, 48),  # Midfielders high
        (80, 25), (85, 43)  # Forwards
    ]
    
    end_positions_def = [
        (40, 20), (40, 34), (40, 48),  # Midfielders drop back
        (50, 28), (50, 40)  # Forwards track back
    ]
    
    fig, ax = radar.create_movement_vectors(start_positions_def, end_positions_def, 1,
                                           title="Defensive Transition Movement")
    fig.savefig(output_dir / 'defensive_transition.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: defensive_transition.png")
    
    print(f"\n✓ Case study completed! Files saved to: {output_dir}")
    
    return output_dir

def case_study_wing_play():
    """Case Study 4: Analyze wing play and width"""
    print("\n" + "="*80)
    print("CASE STUDY 4: WING PLAY ANALYSIS")
    print("="*80)
    
    output_dir = Path('case_studies_output/wing_play')
    output_dir.mkdir(exist_ok=True, parents=True)
    
    radar = PlayerPositionRadar()
    
    # Simulate wide play
    print("\n1. Analyzing wide attacking play...")
    
    wide_positions = []
    for _ in range(150):
        # Concentrate on wings
        if np.random.random() > 0.5:
            # Right wing
            x = np.random.uniform(50, 90)
            y = np.random.uniform(55, 68)
        else:
            # Left wing
            x = np.random.uniform(50, 90)
            y = np.random.uniform(0, 13)
        wide_positions.append((x, y))
    
    fig, ax = radar.create_heatmap(wide_positions, 1, grid_size=12,
                                   title="Wide Play Intensity - Using Wings")
    fig.savefig(output_dir / 'wide_play_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: wide_play_heatmap.png")
    
    # Simulate narrow play
    print("\n2. Analyzing narrow central play...")
    
    narrow_positions = []
    for _ in range(150):
        # Concentrate in central areas
        x = np.random.uniform(40, 80)
        y = np.random.normal(34, 8)
        y = np.clip(y, 0, 68)
        narrow_positions.append((x, y))
    
    fig, ax = radar.create_heatmap(narrow_positions, 2, grid_size=12,
                                   title="Narrow Play - Central Concentration")
    fig.savefig(output_dir / 'narrow_play_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("   ✓ Saved: narrow_play_heatmap.png")
    
    print(f"\n✓ Case study completed! Files saved to: {output_dir}")
    
    return output_dir

def generate_summary_report(case_study_dirs):
    """Generate summary report of all case studies"""
    print("\n" + "="*80)
    print("GENERATING SUMMARY REPORT")
    print("="*80)
    
    summary = """
# PLAYER POSITION RADAR VISUALIZATION - CASE STUDIES SUMMARY

## Overview
This report summarizes four tactical case studies using player position radar visualization.

## Case Study 1: Tactical Formation Comparison
**Objective:** Compare 4-4-2 vs 4-3-3 formations

**Key Findings:**
- 4-4-2 provides better width in midfield
- 4-3-3 offers more attacking threat with 3 forwards
- Defensive coverage differs significantly in central areas

**Generated Visualizations:**
- 442_formation.png - Team 1 tactical setup
- 433_formation.png - Team 2 tactical setup
- tactical_comparison.png - Side-by-side comparison

## Case Study 2: Pressing Intensity Analysis
**Objective:** Analyze high-press vs defensive block strategies

**Key Findings:**
- High-press concentrates players in opponent's half (70m+ zone)
- Defensive block compacts team in own half (0-30m zone)
- Player density maps show clear tactical intentions

**Generated Visualizations:**
- high_press_heatmap.png - High pressing intensity
- defensive_block_heatmap.png - Deep defensive positioning

## Case Study 3: Player Movement Patterns
**Objective:** Track transition movements (attack/defense)

**Key Findings:**
- Attacking transitions: avg 20-30m forward movement
- Defensive transitions: rapid drop back to defensive positions
- Movement vectors show coordinated team shifts

**Generated Visualizations:**
- attacking_transition.png - Forward movement patterns
- defensive_transition.png - Defensive recovery patterns

## Case Study 4: Wing Play Analysis
**Objective:** Compare wide vs narrow attacking approaches

**Key Findings:**
- Wide play utilizes full pitch width (edges at 0-13m, 55-68m)
- Narrow play concentrates in central 20m corridor
- Different styles create different defensive challenges

**Generated Visualizations:**
- wide_play_heatmap.png - Wing-oriented attacks
- narrow_play_heatmap.png - Central play patterns

## Conclusions
These case studies demonstrate:
1. ✓ Tactical formations significantly impact player positioning
2. ✓ Pressing strategies clearly visible in position heatmaps
3. ✓ Movement patterns reveal team tactical transitions
4. ✓ Width variation shows different attacking philosophies

## Applications
- Tactical analysis for coaches
- Opposition scouting reports
- Player positioning optimization
- Performance analysis and improvement

## Technical Details
- Pitch dimensions: 105m x 68m (standard)
- Visualization: Matplotlib + Seaborn
- Resolution: 300 DPI (publication quality)
- Color coding: Red (Team 1), Blue (Team 2)
"""
    
    output_file = Path('case_studies_output/CASE_STUDIES_SUMMARY.md')
    output_file.parent.mkdir(exist_ok=True, parents=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"\n✓ Summary report saved to: {output_file}")
    
    return output_file

def main():
    """Run all case studies"""
    print("="*80)
    print("PLAYER POSITION RADAR VISUALIZATION - CASE STUDIES")
    print("="*80)
    print("\nGenerating tactical analysis case studies...")
    print("This will create 4 case studies with multiple visualizations.\n")
    
    case_study_dirs = []
    
    # Run all case studies
    case_study_dirs.append(case_study_tactical_comparison())
    case_study_dirs.append(case_study_pressing_intensity())
    case_study_dirs.append(case_study_player_movement())
    case_study_dirs.append(case_study_wing_play())
    
    # Generate summary
    summary_file = generate_summary_report(case_study_dirs)
    
    print("\n" + "="*80)
    print("ALL CASE STUDIES COMPLETED!")
    print("="*80)
    print("\nGenerated visualizations:")
    print("  Case Study 1: 3 images (tactical formations)")
    print("  Case Study 2: 2 images (pressing analysis)")
    print("  Case Study 3: 2 images (movement patterns)")
    print("  Case Study 4: 2 images (wing play)")
    print(f"\nTotal: 9 high-quality visualizations (300 DPI)")
    print(f"\nAll files saved in: case_studies_output/")
    print(f"Summary report: {summary_file}")
    
if __name__ == '__main__':
    main()
