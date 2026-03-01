import numpy as np
import matplotlib.pyplot as plt
from itertools import islice, cycle
from matplotlib.patches import FancyBboxPatch

# ============================================================================
# CONFIGURATION
# ============================================================================

# Chromatic scale
chromatic = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

# Guitar configuration
guitar_tuning = ['E', 'A', 'D', 'G', 'B', 'E']
nfrets = 20
scale_length = 25.5  # Scale length in inches

# Scale intervals
maj_int = [2, 2, 1, 2, 2, 2, 1]
min_int = [2, 1, 2, 2, 1, 2, 2]
pent_int = [2, 2, 3, 2, 3]
blues_int = [3, 2, 1, 1, 3, 2]
dorian_int = [2, 1, 2, 2, 2, 1, 2]
mixolydian_int = [2, 2, 1, 2, 2, 1, 2]
lydian_int = [2, 2, 2, 1, 2, 2, 1]
phrygian_int = [1, 2, 2, 2, 1, 2, 2]
locrian_int = [1, 2, 2, 1, 2, 2, 2]

interval_map = {
    'Major': maj_int,
    'Minor': min_int,
    'Pentatonic': pent_int,
    'Blues': blues_int,
    'Dorian': dorian_int,
    'Mixolydian': mixolydian_int,
    'Lydian': lydian_int,
    'Phrygian': phrygian_int,
    'Locrian': locrian_int
}

# Chord types for major scale
chord_types = ['Maj', 'Min', 'Min', 'Maj', 'Maj', 'Min', 'Dim']

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def cycle_notes(root_note, univ_scale, N):
    """Cycle through N notes starting from root_note"""
    root_idx = univ_scale.index(root_note)
    return list(islice(cycle(univ_scale), root_idx, root_idx + N))

def get_scale(root_note, univ_scale, intervals):
    """Get scale notes based on root note and intervals"""
    root_idx = univ_scale.index(root_note)
    rel_idx = np.insert(np.cumsum(intervals), 0, 0)
    return [univ_scale[(root_idx + i) % len(univ_scale)] for i in rel_idx]

def fret_spacing(nfrets, scale_length=scale_length):
    """Calculate fret positions based on physics"""
    fret_positions = []
    for fret in range(nfrets + 1):
        fret_positions.append(scale_length - (scale_length / (2 ** (fret / 12))))
    return np.array(fret_positions)

# ============================================================================
# FRETBOARD SETUP
# ============================================================================

# Generate fretboard for each string
fretboard = [cycle_notes(tuning, chromatic, nfrets) for tuning in guitar_tuning]

# Calculate fret positions and finger locations
fret_positions = fret_spacing(nfrets)
temp = np.insert(fret_positions, 0, 0)
finger_loc = (temp[:-1] + temp[1:]) / 2

# ============================================================================
# DRAWING FUNCTIONS
# ============================================================================

def draw_fretboard(ax):
    """Draw the fretboard with all elements"""
    
    # Draw frets
    for fret in range(nfrets + 1):
        ax.plot([fret_positions[fret], fret_positions[fret]], 
                [1 - 0.2, 6 + 0.2], 'gray', lw=3, zorder=2)
    
    # Draw nut
    ax.plot([0, 0], [1, 6], color="#C7A585", lw=5, zorder=3)
    
    # Draw strings (6 strings)
    for string in range(1, 7):
        ax.plot([-0.5, scale_length], [string, string], 
                color="#D19019", lw=5 - 0.5 * string, zorder=3)
    
    # Draw fret markers
    dot_positions = [3, 5, 7, 9, 12, 15, 17, 19]
    for fret in dot_positions:
        if fret <= nfrets:
            dot_center = (fret_positions[fret - 1] + fret_positions[fret]) / 2
            if fret == 12:  # Double dot at 12th fret
                ax.plot(dot_center, 2.5, color='k', marker='o', 
                       markersize=5, zorder=2)
                ax.plot(dot_center, 4.5, color='k', marker='o', 
                       markersize=5, zorder=2)
            else:
                ax.plot(dot_center, 3.5, color='k', marker='o', 
                       markersize=5, zorder=2)
    
    # Draw sound hole
    sound_hole_center = (scale_length * 0.83, 3.5)
    sound_hole_radius = 3.5
    sound_hole = plt.Circle(sound_hole_center, sound_hole_radius, 
                           color='black', fill=True, lw=2, zorder=1)
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
    
    # Set axis properties
    ax.set_ylim(0.5, 6.5)
    ax.set_xticks(fret_positions)
    ax.set_xticklabels(range(nfrets + 1))
    ax.set_yticks(range(1, 7))
    ax.set_yticklabels([f'{i + 1}-{gs}' for i, gs in enumerate(guitar_tuning)])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    return ax

def add_scale_to_fretboard(ax, scale_note, scale_notes, color='#FFD700'):
    """Mark scale notes on the fretboard"""
    for string_idx, string in enumerate(fretboard):
        for fret_idx, note in enumerate(string):
            if note in scale_notes:
                ax.plot(finger_loc[fret_idx], string_idx + 1, 
                       color=color, marker='o', markersize=15, zorder=4)
                ax.text(finger_loc[fret_idx], string_idx + 1 - 0.15, note,
                       ha='center', va='bottom', fontsize=8, 
                       color='black', fontweight='bold', zorder=5)
    return ax

# ============================================================================
# USE CASE 1: Single Scale Visualization
# ============================================================================

def visualize_single_scale(scale_note='C', scale_type='Major'):
    """Visualize a single scale on the fretboard"""
    scale_notes = get_scale(scale_note, chromatic, interval_map[scale_type])
    
    fig, ax = plt.subplots(figsize=(scale_length, 3))
    ax = draw_fretboard(ax)
    ax = add_scale_to_fretboard(ax, scale_note, scale_notes)
    ax.set_title(f'Guitar Fretboard - {scale_note} {scale_type} Scale', 
                fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    #plt.savefig(f'{scale_note}_{scale_type}_single.pdf', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"{scale_note} {scale_type} scale notes: {scale_notes}")

# ============================================================================
# USE CASE 2: Scale with All Chords
# ============================================================================

def visualize_scale_with_chords(scale_note='C', scale_type='Major'):
    """Visualize scale and all diatonic chords"""
    scale_notes = get_scale(scale_note, chromatic, interval_map[scale_type])
    chord_intervals = [0, 2, 4]  # Triad intervals
    
    # Create figure with 8 subplots (1 for scale + 7 for chords)
    fig, axes = plt.subplots(8, 1, figsize=(scale_length, 24))
    
    # First subplot: all scale notes
    ax = axes[0]
    ax = draw_fretboard(ax)
    ax = add_scale_to_fretboard(ax, scale_note, scale_notes, color='#58DB5C')
    ax.set_title(f'All Notes in {scale_note} {scale_type} Scale', 
                fontsize=12, fontweight='bold')
    
    # Remaining subplots: individual chords
    for j in range(7):
        chord_notes = [scale_notes[(i + j) % len(scale_notes)] 
                      for i in chord_intervals]
        
        ax = axes[j + 1]
        ax = draw_fretboard(ax)
        ax = add_scale_to_fretboard(ax, scale_note, chord_notes, color='#FFD700')
        ax.set_title(f'{scale_notes[j]} {chord_types[j]} Chord - ' + 
                    ', '.join(chord_notes), fontsize=11, fontweight='bold')
        
        print(f"Chord {j+1}: {scale_notes[j]} {chord_types[j]} - {chord_notes}")
    
    # Add overall title
    fig.suptitle(f'{scale_note} {scale_type} Scale - Notes & Chords: {", ".join(scale_notes)}',
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    #plt.savefig(f'{scale_note}_{scale_type}_with_chords.pdf', dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# USE CASE 3: Compare Multiple Scales
# ============================================================================

def compare_scales(root_note='C', scale_types=['Major', 'Minor', 'Pentatonic']):
    """Compare multiple scales side by side"""
    n_scales = len(scale_types)
    fig, axes = plt.subplots(n_scales, 1, figsize=(scale_length, 3 * n_scales))
    
    if n_scales == 1:
        axes = [axes]
    
    for idx, scale_type in enumerate(scale_types):
        scale_notes = get_scale(root_note, chromatic, interval_map[scale_type])
        
        ax = axes[idx]
        ax = draw_fretboard(ax)
        ax = add_scale_to_fretboard(ax, root_note, scale_notes, 
                                    color='#58DB5C' if idx % 2 == 0 else '#FFD700')
        ax.set_title(f'{root_note} {scale_type} Scale - {", ".join(scale_notes)}',
                    fontsize=12, fontweight='bold')
        
        print(f"{root_note} {scale_type}: {scale_notes}")
    
    fig.suptitle(f'Scale Comparison for Root Note: {root_note}',
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    #plt.savefig(f'{root_note}_scale_comparison.pdf', dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# USE CASE 4: All Modes of Major Scale
# ============================================================================

def visualize_all_modes(root_note='C'):
    """Visualize all 7 modes starting from the same root"""
    modes = {
        'Ionian (Major)': maj_int,
        'Dorian': dorian_int,
        'Phrygian': phrygian_int,
        'Lydian': lydian_int,
        'Mixolydian': mixolydian_int,
        'Aeolian (Minor)': min_int,
        'Locrian': locrian_int
    }
    
    fig, axes = plt.subplots(7, 1, figsize=(scale_length, 21))
    
    for idx, (mode_name, intervals) in enumerate(modes.items()):
        scale_notes = get_scale(root_note, chromatic, intervals)
        
        ax = axes[idx]
        ax = draw_fretboard(ax)
        colors = ['#FFD700', '#58DB5C', '#FF6B6B', '#4ECDC4', '#95E1D3', '#F38181', '#AA96DA']
        ax = add_scale_to_fretboard(ax, root_note, scale_notes, color=colors[idx])
        ax.set_title(f'{root_note} {mode_name} - {", ".join(scale_notes)}',
                    fontsize=11, fontweight='bold')
        
        print(f"{root_note} {mode_name}: {scale_notes}")
    
    fig.suptitle(f'All 7 Modes from Root Note: {root_note}',
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    #plt.savefig(f'{root_note}_all_modes.pdf', dpi=300, bbox_inches='tight')
    plt.show()

# ============================================================================
# USE CASE 5: Chord Progressions
# ============================================================================

def visualize_chord_progression(scale_note='C', scale_type='Major', 
                                progression=[0, 3, 4, 0]):
    """Visualize a chord progression (e.g., I-IV-V-I)"""
    scale_notes = get_scale(scale_note, chromatic, interval_map[scale_type])
    chord_intervals = [0, 2, 4]
    
    progression_names = {0: 'I', 1: 'ii', 2: 'iii', 3: 'IV', 
                        4: 'V', 5: 'vi', 6: 'vii°'}
    
    n_chords = len(progression)
    fig, axes = plt.subplots(n_chords, 1, figsize=(scale_length, 3 * n_chords))
    
    if n_chords == 1:
        axes = [axes]
    
    for idx, chord_num in enumerate(progression):
        chord_notes = [scale_notes[(i + chord_num) % len(scale_notes)] 
                      for i in chord_intervals]
        
        ax = axes[idx]
        ax = draw_fretboard(ax)
        ax = add_scale_to_fretboard(ax, scale_note, chord_notes, color='#FFD700')
        ax.set_title(f'{progression_names[chord_num]} - {scale_notes[chord_num]} ' +
                    f'{chord_types[chord_num]} - {", ".join(chord_notes)}',
                    fontsize=12, fontweight='bold')
    
    prog_string = '-'.join([progression_names[i] for i in progression])
    fig.suptitle(f'{scale_note} {scale_type}: {prog_string} Progression',
                fontsize=16, fontweight='bold', y=0.995)
    
    plt.tight_layout(rect=[0, 0, 1, 0.99])
    #plt.savefig(f'{scale_note}_{scale_type}_progression.pdf', dpi=300, bbox_inches='tight')
    plt.show()