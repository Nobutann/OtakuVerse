document.addEventListener('DOMContentLoaded', function() {
    const counters = document.querySelectorAll('.episode-counter');
    counters.forEach(counterDiv => {
        const entryId = counterDiv.dataset.entryId;
        const epSpan = counterDiv.querySelector('.episodes-watched');
        const increaseBtn = counterDiv.querySelector('.increase-ep');
        const decreaseBtn = counterDiv.querySelector('.decrease-ep');
        const max = parseInt(counterDiv.dataset.maxEpisodes);

        increaseBtn.addEventListener('click', () => updateEpisodes(1));
        decreaseBtn.addEventListener('click', () => updateEpisodes(-1));

        function updateEpisodes(change) {
            let current = parseInt(epSpan.textContent);
            let newVal = current + change;
            if (newVal < 0) newVal = 0;
            if (newVal > max) newVal = max;

            fetch(`/lists/update-episodes/${entryId}/`, { 
                method: 'POST',
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}',
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({episodes_watched: newVal})
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    epSpan.textContent = newVal;
                } else {
                    alert("Erro ao atualizar episódios.");
                }
            });
        }
    });
});
