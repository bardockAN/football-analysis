"""
Script to create dataset visualization for presentation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Create figure with subplots
fig = plt.figure(figsize=(14, 10))
fig.suptitle('Football Players Detection Dataset Overview', fontsize=20, fontweight='bold', y=0.98)

# 1. Dataset Split Distribution (Pie Chart)
ax1 = plt.subplot(2, 3, 1)
splits = ['Train', 'Validation', 'Test']
sizes = [612, 38, 13]
colors = ['#3498db', '#2ecc71', '#e74c3c']
explode = (0.05, 0, 0)

ax1.pie(sizes, explode=explode, labels=splits, colors=colors, autopct='%1.1f%%',
        shadow=True, startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
ax1.set_title('Dataset Split Distribution\n(Total: 663 images)', fontsize=12, fontweight='bold', pad=10)

# 2. Images Count per Split (Bar Chart)
ax2 = plt.subplot(2, 3, 2)
bars = ax2.bar(splits, sizes, color=colors, edgecolor='black', linewidth=1.5)
ax2.set_ylabel('Number of Images', fontsize=11, fontweight='bold')
ax2.set_title('Images per Split', fontsize=12, fontweight='bold', pad=10)
ax2.grid(axis='y', alpha=0.3, linestyle='--')

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# 3. Classes Distribution (Horizontal Bar)
ax3 = plt.subplot(2, 3, 3)
classes = ['Ball ⚽', 'Goalkeeper 🧤', 'Player 👤', 'Referee 👨‍⚖️']
class_colors = ['#f39c12', '#9b59b6', '#3498db', '#e74c3c']
y_pos = np.arange(len(classes))

ax3.barh(y_pos, [1, 1, 1, 1], color=class_colors, edgecolor='black', linewidth=1.5)
ax3.set_yticks(y_pos)
ax3.set_yticklabels(classes, fontsize=10)
ax3.set_xlabel('Detection Categories', fontsize=11, fontweight='bold')
ax3.set_title('4 Object Classes', fontsize=12, fontweight='bold', pad=10)
ax3.set_xlim(0, 1.2)
ax3.set_xticks([])

# 4. Annotation Format Info (Text Box)
ax4 = plt.subplot(2, 3, 4)
ax4.axis('off')
annotation_info = """
ANNOTATION FORMAT

Format: YOLO (.txt files)

Structure:
  <class_id> <x_center> <y_center> 
  <width> <height>

Normalized: All values [0, 1]

Example:
  0 0.512 0.345 0.089 0.156
  (Ball at center with bbox)
"""
ax4.text(0.1, 0.5, annotation_info, fontsize=10, family='monospace',
         verticalalignment='center', bbox=dict(boxstyle='round', 
         facecolor='wheat', alpha=0.5, edgecolor='black', linewidth=2))

# 5. Data Augmentation Techniques
ax5 = plt.subplot(2, 3, 5)
ax5.axis('off')
augmentation = """
DATA AUGMENTATION

✓ Rotation (±15°)
✓ Horizontal Flip
✓ Vertical Flip  
✓ Brightness (±20%)
✓ Contrast (±15%)
✓ Mosaic Augmentation

Purpose: Improve model 
         robustness and 
         generalization
"""
ax5.text(0.1, 0.5, augmentation, fontsize=10.5, 
         verticalalignment='center', bbox=dict(boxstyle='round',
         facecolor='lightblue', alpha=0.6, edgecolor='black', linewidth=2))

# 6. Training Configuration
ax6 = plt.subplot(2, 3, 6)
ax6.axis('off')
config = """
TRAINING CONFIGURATION

Model:      YOLOv5x
Input Size: 640 × 640
Epochs:     100
Batch Size: 32 (GPU)
            16 (CPU)
Optimizer:  SGD/Adam
Pretrained: COCO weights

Transfer Learning: ✓
Mixed Precision:   ✓
"""
ax6.text(0.1, 0.5, config, fontsize=10, family='monospace',
         verticalalignment='center', bbox=dict(boxstyle='round',
         facecolor='lightgreen', alpha=0.6, edgecolor='black', linewidth=2))

# Add footer
fig.text(0.5, 0.02, 'Source: Roboflow Universe | License: CC BY 4.0', 
         ha='center', fontsize=10, style='italic', color='gray')

plt.tight_layout(rect=[0, 0.03, 1, 0.96])
plt.savefig('training/dataset_visualization.png', dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')
print("✅ Dataset visualization saved: training/dataset_visualization.png")
plt.show()
