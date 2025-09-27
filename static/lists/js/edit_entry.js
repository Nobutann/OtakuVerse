document.addEventListener('DOMContentLoaded', function() {
    const notesTextarea = document.getElementById('id_notes');
    const notesCounter = document.getElementById('notesCounter');
    
    if (notesTextarea && notesCounter) {
        notesTextarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            notesCounter.textContent = currentLength + '/1000';
            
            if (currentLength > 900) {
                notesCounter.style.color = 'var(--accent-coral)';
            } else {
                notesCounter.style.color = 'var(--text-muted)';
            }
        });
    }

    const statusSelect = document.getElementById('id_status');
    const startDateInput = document.getElementById('id_start_date');
    const finishDateInput = document.getElementById('id_finish_date');
    
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            const status = this.value;
            const today = new Date().toISOString().split('T')[0];

            if (status === 'watching' && !startDateInput.value) {
                startDateInput.value = today;
            }

            if (status === 'completed' && !finishDateInput.value) {
                finishDateInput.value = today;
                if (!startDateInput.value) {
                    startDateInput.value = today;
                }
            }
            
            if (status === 'ptw') {
 
            }
        });
    }
});