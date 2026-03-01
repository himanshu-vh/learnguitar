document.addEventListener('DOMContentLoaded', function() {
    const rootNoteSelect = document.getElementById('root-note');
    const scaleTypeSelect = document.getElementById('scale-type');
    const generateBtn = document.getElementById('generate-btn');
    const infoSection = document.getElementById('info-section');
    const fretboardContainer = document.getElementById('fretboard-container');
    const loading = document.getElementById('loading');
    const fretboardImg = document.getElementById('fretboard-img');
    const scaleTitle = document.getElementById('scale-title');
    const scaleNotes = document.getElementById('scale-notes');

    // Generate on button click
    generateBtn.addEventListener('click', generateFretboard);

    // Also generate on Enter key
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            generateFretboard();
        }
    });

    function generateFretboard() {
        const rootNote = rootNoteSelect.value;
        const scaleType = scaleTypeSelect.value;

        // Show loading
        fretboardContainer.style.display = 'flex';
        loading.style.display = 'block';
        fretboardImg.style.display = 'none';
        infoSection.style.display = 'none';

        // Scroll to fretboard
        fretboardContainer.scrollIntoView({ behavior: 'smooth', block: 'center' });

        // Send request to Flask backend
        fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                scale_note: rootNote,
                scale_type: scaleType
            })
        })
        .then(response => response.json())
        .then(data => {
            // Update info
            scaleTitle.textContent = `${rootNote} ${scaleType} Scale`;
            scaleNotes.textContent = `Notes: ${data.notes.join(', ')}`;
            
            // Update image
            fretboardImg.src = `data:image/png;base64,${data.image}`;
            
            // Show result
            setTimeout(() => {
                loading.style.display = 'none';
                fretboardImg.style.display = 'block';
                infoSection.style.display = 'block';
            }, 300);
        })
        .catch(error => {
            console.error('Error:', error);
            loading.innerHTML = '<p style="color: red;">Error generating fretboard. Please try again.</p>';
        });
    }

    // Generate initial fretboard
    generateFretboard();
});