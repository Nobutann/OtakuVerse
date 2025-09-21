document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    
    let searchTimeout;
    let currentFocus = -1;

    if (searchInput && searchSuggestions) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            clearTimeout(searchTimeout);
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    fetchSuggestions(query);
                }, 300);
            } else {
                hideSuggestions();
            }
        });

        searchInput.addEventListener('keydown', function(e) {
            const suggestions = searchSuggestions.querySelectorAll('.suggestion-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentFocus++;
                if (currentFocus >= suggestions.length) currentFocus = 0;
                setActiveSuggestion(suggestions);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentFocus--;
                if (currentFocus < 0) currentFocus = suggestions.length - 1;
                setActiveSuggestion(suggestions);
            } else if (e.key === 'Enter') {
                if (currentFocus > -1 && suggestions[currentFocus]) {
                    e.preventDefault();
                    suggestions[currentFocus].click();
                }
            } else if (e.key === 'Escape') {
                hideSuggestions();
                searchInput.blur();
            }
        });

        searchInput.addEventListener('blur', function() {
            setTimeout(hideSuggestions, 200);
        });
    }

    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            const dropdown = this.closest('.dropdown');
            dropdown.classList.toggle('active');
        });

        document.addEventListener('click', function(e) {
            const dropdown = document.querySelector('.dropdown');
            if (dropdown && !dropdown.contains(e.target)) {
                dropdown.classList.remove('active');
            }
        });
    }

    function fetchSuggestions(query) {
        fetch(`/api/suggestions/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => showSuggestions(data))
            .catch(err => console.error('Erro ao buscar sugestões:', err));
    }

    function showSuggestions(data) {
    const items = data.suggestions || [];
    searchSuggestions.innerHTML = '';
    if (items.length === 0) {
        hideSuggestions();
        return;
    }

    items.forEach(item => {
        const div = document.createElement('div');
        div.classList.add('suggestion-item');
        div.innerHTML = `<img src="${item.image}" width="40"> ${item.title} (${item.year || '-'})`;
        div.addEventListener('click', () => {
            hideSuggestions();
            window.location.href = `/animes/animes/${item.id}/`;
        });
        searchSuggestions.appendChild(div);
    });

    searchSuggestions.style.display = 'block';
    currentFocus = -1;
}
    function hideSuggestions() {
        searchSuggestions.innerHTML = '';
        searchSuggestions.style.display = 'none';
        currentFocus = -1;
    }

    function setActiveSuggestion(suggestions) {
        if (!suggestions) return;
        suggestions.forEach(item => item.classList.remove('active'));
        if (currentFocus >= 0 && currentFocus < suggestions.length) {
            suggestions[currentFocus].classList.add('active');
            suggestions[currentFocus].scrollIntoView({
                block: 'nearest'
            });
        }
    }
});
