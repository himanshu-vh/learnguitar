# app.py
from flask import Flask, render_template, request, jsonify
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from itertools import islice, cycle
from matplotlib.patches import FancyBboxPatch
import io
import base64

app = Flask(__name__)

# ============================================================================
# CONFIGURATION (from your notebook)
# ============================================================================

chromatic = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
guitar_tuning = ['E', 'A', 'D', 'G', 'B', 'E']
nfrets = 20
scale_length = 25.5

# Scale intervals
interval_map = {
    'Major': [2, 2, 1, 2, 2, 2, 1],
    'Minor': [2, 1, 2, 2, 1, 2, 2],
    'Pentatonic': [2, 2, 3, 2, 3],
    'Blues': [3, 2, 1, 1, 3, 2],
    'Dorian': [2, 1, 2, 2, 2, 1, 2],
    'Mixolydian': [2, 2, 1, 2, 2, 1, 2],
    'Lydian': [2, 2, 2, 1, 2, 2, 1],
    'Phrygian': [1, 2, 2, 2, 1, 2, 2],
    'Locrian': [1, 2, 2, 1, 2, 2, 2]
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def cycle_notes(root_note, univ_scale, N):
    root_idx = univ_scale.index(root_note)
    return list(islice(cycle(univ_scale), root_idx, root_idx + N))

def get_scale(root_note, univ_scale, intervals):
    root_idx = univ_scale.index(root_note)
    rel_idx = np.insert(np.cumsum(intervals), 0, 0)
    return [univ_scale[(root_idx + i) % len(univ_scale)] for i in rel_idx]

def fret_spacing(nfrets, scale_length=scale_length):
    fret_positions = []
    for fret in range(nfrets + 1):
        fret_positions.append(scale_length - (scale_length / (2 ** (fret / 12))))
    return np.array(fret_positions)

# Generate fretboard
fretboard = [cycle_notes(tuning, chromatic, nfrets) for tuning in guitar_tuning]
fret_positions = fret_spacing(nfrets)
temp = np.insert(fret_positions, 0, 0)
finger_loc = (temp[:-1] + temp[1:]) / 2

# ============================================================================
# DRAWING FUNCTIONS
# ============================================================================

def draw_fretboard(ax):
    # Draw frets
    for fret in range(nfrets + 1):
        ax.plot([fret_positions[fret], fret_positions[fret]], 
                [1 - 0.2, 6 + 0.2], 'gray', lw=3, zorder=2)
    
    # Draw nut
    ax.plot([0, 0], [1, 6], color="#C7A585", lw=5, zorder=3)
    
    # Draw strings
    for string in range(1, 7):
        ax.plot([-0.5, scale_length], [string, string], 
                color="#D19019", lw=5 - 0.5 * string, zorder=1)
    
    # Draw fret markers
    dot_positions = [3, 5, 7, 9, 12, 15, 17, 19]
    for fret in dot_positions:
        if fret <= nfrets:
            dot_center = (fret_positions[fret - 1] + fret_positions[fret]) / 2
            if fret == 12:
                ax.plot(dot_center, 2.5, color='k', marker='o', markersize=5, zorder=2)
                ax.plot(dot_center, 4.5, color='k', marker='o', markersize=5, zorder=2)
            else:
                ax.plot(dot_center, 3.5, color='k', marker='o', markersize=5, zorder=2)
    
    # Draw sound hole
    sound_hole_center = (scale_length * 0.83, 3.5)
    sound_hole_radius = 3.5
    sound_hole = plt.Circle(sound_hole_center, sound_hole_radius, 
                           color='black', fill=True, lw=2, zorder=2)
    ax.add_patch(sound_hole)
    
    # Draw guitar body
    body_start = scale_length * 0.7
    body_end = scale_length
    body_width = 7
    body = FancyBboxPatch((body_start, 3.5 - body_width / 2),
                         body_end - body_start, body_width,
                         boxstyle="round,pad=0.3",
                         edgecolor='#654321', facecolor='#8B4513',
                         linewidth=3, zorder=0)
    ax.add_patch(body)
    
    ax.set_ylim(0.5, 6.5)
    ax.set_xlim(-1, scale_length + 0.5)
    ax.set_xticks(fret_positions)
    ax.set_xticklabels(range(nfrets + 1))
    ax.set_yticks(range(1, 7))
    ax.set_yticklabels([f'{i + 1}-{gs}' for i, gs in enumerate(guitar_tuning)])
    
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    return ax

def add_scale_to_fretboard(ax, scale_note, scale_notes):
    for string_idx, string in enumerate(fretboard):
        for fret_idx, note in enumerate(string):
            if note in scale_notes:
                ax.plot(finger_loc[fret_idx], string_idx + 1, 
                       color="#58DB5C", marker='o', markersize=15, zorder=4)
                ax.text(finger_loc[fret_idx], string_idx + 1 - 0.15, note,
                       ha='center', va='bottom', fontsize=8, 
                       color='black', fontweight='bold', zorder=5)
    return ax

# ============================================================================
# ROUTES
# ============================================================================

@app.route('/')
def index():
    return render_template('index.html', 
                         notes=chromatic, 
                         scales=list(interval_map.keys()))

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    scale_note = data.get('scale_note', 'C')
    scale_type = data.get('scale_type', 'Major')
    
    # Generate scale
    scale_notes = get_scale(scale_note, chromatic, interval_map[scale_type])
    
    # Create plot
    fig, ax = plt.subplots(figsize=(scale_length, 3), facecolor='white')
    ax = draw_fretboard(ax)
    ax = add_scale_to_fretboard(ax, scale_note, scale_notes)
    ax.set_title(f'{scale_note} {scale_type} Scale', 
                fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Convert to base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', facecolor='white')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    
    return jsonify({
        'image': img_base64,
        'notes': scale_notes
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)