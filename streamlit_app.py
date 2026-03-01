# streamlit_app.py
import streamlit as st
import matplotlib.pyplot as plt
from guitar import *


def web_visualize_scale_with_chords(scale_note='C', scale_type='Major'):
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
    #plt.show()
    return fig



st.set_page_config(page_title="Guitar Fretboard Visualizer", layout="wide")

st.title("🎸 Guitar Fretboard Visualizer")

col1, col2 = st.columns(2)

with col1:
    note = st.selectbox("Root Note", chromatic, index=3)  # Default to 'C'

with col2:
    scale = st.selectbox("Scale", list(interval_map.keys()))

scale_notes = get_scale(note, chromatic, interval_map[scale])

st.write(f"**Notes in {note} {scale}:** {', '.join(scale_notes)}")

#fig, ax = plt.subplots(figsize=(25, 3))
#ax = draw_fretboard(ax)
#ax = add_scale_to_fretboard(ax, note, scale_notes)
#ax.set_title(f'{note} {scale} Scale', fontsize=16, fontweight='bold')
#plt.tight_layout()
fig = web_visualize_scale_with_chords(note, scale)
st.pyplot(fig)