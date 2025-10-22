document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchSuggestions = document.getElementById('searchSuggestions');
    const userMenuBtn = document.getElementById('userMenuBtn');
    const userDropdown = document.getElementById('userDropdown');
    const searchTypeRadios = document.querySelectorAll('input[name="search_type"]');
    
    let searchTimeout;
    let currentFocus = -1;

    const bannedGenres = ['hentai'];
    const bannedRatings = ['rx'];

    function isAdultContent(item) {
        if (!item) return false;
        const genres = (item.genres || []).map(g => g.toLowerCase());
        const rating = (item.rating || '').toLowerCase();
        
        if (bannedRatings.includes(rating)) {
            return true;
        }
        
        for (const genre of genres) {
            if (bannedGenres.includes(genre)) {
                return true;
            }
        }
        
        return false;
    }

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

        if (searchTypeRadios) {
            searchTypeRadios.forEach(radio => {
                radio.addEventListener('change', function() {
                    const query = searchInput.value.trim();
                    if (query.length >= 2) {
                        fetchSuggestions(query);
                    }
                });
            });
        }

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
        const searchType = document.querySelector('input[name="search_type"]:checked');
        const type = searchType ? searchType.value : 'anime';
        
        fetch(`/api/suggestions/?q=${encodeURIComponent(query)}&type=${type}`)
            .then(response => response.json())
            .then(data => showSuggestions(data))
            .catch(err => console.error('Erro ao buscar sugestões:', err));
    }

    function showSuggestions(data) {
        let items = data.suggestions || [];
        items = items.filter(item => !isAdultContent(item));
        
        searchSuggestions.innerHTML = '';
        if (items.length === 0) {
            hideSuggestions();
            return;
        }

        items.forEach(item => {
            const div = document.createElement('div');
            div.classList.add('suggestion-item');
            
            const img = document.createElement('img');
            img.src = item.image;
            img.alt = item.title;
            img.style.width = '40px';
            img.style.height = '56px';
            img.style.objectFit = 'cover';
            img.style.borderRadius = '4px';
            img.style.marginRight = '10px';
            
            if (item.type === 'usuário') {
                img.style.borderRadius = '50%';
            }
            
            const title = document.createElement('span');
            title.textContent = item.title;
            
            const badge = document.createElement('span');
            badge.className = 'suggestion-type';
            badge.textContent = item.type;
            
            div.appendChild(img);
            div.appendChild(title);
            div.appendChild(badge);
            
            div.addEventListener('click', () => {
                hideSuggestions();
                if (item.type === 'anime') {
                    window.location.href = `/animes/animes/${item.id}/`;
                } else if (item.type === 'personagem') {
                    window.location.href = `/search/characters/?q=${encodeURIComponent(item.title)}`;
                } else if (item.type === 'usuário') {
                    window.location.href = `/users/${item.id}/`;
                }
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

document.addEventListener('DOMContentLoaded', function() {
    const episodeCounter = document.querySelector('.episode-counter');
    
    if (!episodeCounter) {
        return;
    }
    
    const entryId = episodeCounter.dataset.entryId;
    const maxEpisodes = parseInt(episodeCounter.dataset.maxEpisodes) || 0;
    
    const decreaseBtn = episodeCounter.querySelector('.decrease-ep');
    const increaseBtn = episodeCounter.querySelector('.increase-ep');
    const episodeDisplay = episodeCounter.querySelector('.episodes-watched');
    
    function getCsrfToken() {
        let metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
        let token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token && token.value && token.value.length > 10) {
            return token.value;
        }
        
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken' && value && value.length > 10) {
                return decodeURIComponent(value);
            }
        }
        
        return '';
    }
    
    function updateEpisodes(newCount) {
        const url = `/lists/update-episodes/${entryId}/`;
        
        const reviewForm = document.querySelector('.review-form');
        let csrfToken = '';
        
        if (reviewForm) {
            const csrfInput = reviewForm.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) {
                csrfToken = csrfInput.value;
            }
        }
        
        if (!csrfToken) {
            const addForm = document.querySelector('.add-to-list-form');
            if (addForm) {
                const csrfInput = addForm.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfInput) {
                    csrfToken = csrfInput.value;
                }
            }
        }
        
        if (!csrfToken) {
            showFeedback('Erro de segurança', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('episodes_watched', newCount);
        formData.append('csrfmiddlewaretoken', csrfToken);
        
        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken
            }
        })
        .then(response => {
            return response.text();
        })
        .then(text => {
            try {
                const data = JSON.parse(text);
                
                if (data.success) {
                    episodeDisplay.textContent = data.episodes_watched;
                    showFeedback('Episódios atualizados!', 'success');
                    
                    if (maxEpisodes > 0 && data.episodes_watched >= maxEpisodes) {
                        setTimeout(() => {
                            if (confirm('Você assistiu todos os episódios! Deseja marcar como "Completo"?')) {
                                updateStatus('completed');
                            }
                        }, 500);
                    }
                } else {
                    showFeedback(`${data.error}`, 'error');
                }
            } catch (e) {
                showFeedback('Erro de resposta do servidor', 'error');
            }
        })
        .catch(error => {
            showFeedback('Erro de conexão', 'error');
        });
    }
    
    function updateStatus(newStatus) {
        fetch(`/lists/update-status/${entryId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `status=${newStatus}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar status:', error);
        });
    }
    
    function showFeedback(message, type) {
        const existingFeedback = document.querySelector('.episode-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        const feedback = document.createElement('div');
        feedback.className = `episode-feedback ${type}`;
        feedback.textContent = message;
        feedback.style.cssText = `
            position: absolute;
            top: -40px;
            left: 50%;
            transform: translateX(-50%);
            background: ${type === 'success' ? '#10b981' : '#ef4444'};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            font-size: 0.875rem;
            z-index: 1000;
            animation: feedbackSlide 0.3s ease;
        `;
        
        if (!document.querySelector('#feedback-animation')) {
            const style = document.createElement('style');
            style.id = 'feedback-animation';
            style.textContent = `
                @keyframes feedbackSlide {
                    from { opacity: 0; transform: translateX(-50%) translateY(-10px); }
                    to { opacity: 1; transform: translateX(-50%) translateY(0); }
                }
            `;
            document.head.appendChild(style);
        }
        
        episodeCounter.style.position = 'relative';
        episodeCounter.appendChild(feedback);
        
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 2000);
    }
    
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const currentCount = parseInt(episodeDisplay.textContent) || 0;
            
            if (currentCount > 0) {
                const newCount = currentCount - 1;
                updateEpisodes(newCount);
            } else {
                showFeedback('Não pode ser menor que 0', 'error');
            }
        });
    }
    
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const currentCount = parseInt(episodeDisplay.textContent) || 0;
            
            if (maxEpisodes > 0 && currentCount >= maxEpisodes) {
                showFeedback(`Máximo: ${maxEpisodes} episódios`, 'error');
                return;
            }
            
            const newCount = currentCount + 1;
            updateEpisodes(newCount);
        });
    }
    
    const style = document.createElement('style');
    style.textContent = `
        .episode-counter {
            position: relative;
        }
        
        .episode-counter .btn-small {
            min-width: 35px;
            height: 35px;
            padding: 0;
            border: 2px solid #e5e7eb;
            background: white;
            cursor: pointer;
            border-radius: 6px;
            font-weight: bold;
            transition: all 0.2s ease;
        }
        
        .episode-counter .btn-small:hover {
            background: #f3f4f6;
            border-color: #d1d5db;
        }
        
        .episode-counter .btn-small:active {
            transform: scale(0.95);
        }
        
        .episodes-watched {
            font-weight: bold;
            font-size: 1.1em;
            min-width: 30px;
            text-align: center;
            display: inline-block;
        }
    `;
    document.head.appendChild(style);
});

function getGlobalCsrfToken() {
    let token = document.querySelector('[name=csrfmiddlewaretoken]');
    if (token && token.value) {
        return token.value;
    }
    
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    return '';
}

document.addEventListener('DOMContentLoaded', function() {
    const favoritesSection = document.getElementById('favorites');
    if (favoritesSection) {
        const hasFavorites = favoritesSection.querySelectorAll('.char-card').length > 0;
        if (hasFavorites) {
            showSearch();
        }
    }

    const searchResultButtons = document.querySelectorAll('.btn-add');
    searchResultButtons.forEach(button => {
        button.addEventListener('click', function() {
            addFavoriteCharacter(this.dataset.id, this.dataset.name, this.dataset.image);
        });
    });
});

function showSearch() {
    const searchSection = document.getElementById('search-section');
    if (searchSection) {
        searchSection.style.display = 'block';
        const emptyView = document.getElementById('empty-list-view');
        if (emptyView) {
            emptyView.style.display = 'none';
        }
    }
}

async function searchCharacters() {
    const input = document.getElementById("character-search-input");
    if (!input) return;
    
    const query = input.value;
    if (!query) return;
    
    try {
        const response = await fetch(`https://api.jikan.moe/v4/characters?q=${encodeURIComponent(query)}&limit=12`);
        const data = await response.json();
        const resultsDiv = document.getElementById("results");
        resultsDiv.innerHTML = "";
        document.getElementById('results-divider').style.display = 'block';
        
        data.data.forEach(char => {
            const card = document.createElement("div");
            card.className = "char-card";
            card.innerHTML = `
                <img src="${char.images.jpg.image_url}" alt="${char.name}">
                <h3>${char.name}</h3>
                <button class="btn-add" data-id="${char.mal_id}" data-name="${char.name}" data-image="${char.images.jpg.image_url}">
                    Adicionar ⭐
                </button>
            `;
            
            card.querySelector('.btn-add').addEventListener('click', function() {
                addFavoriteCharacter(this.dataset.id, this.dataset.name, this.dataset.image);
            });
            
            resultsDiv.appendChild(card);
        });
    } catch (error) {
        console.error('Erro ao buscar personagens:', error);
        alert('Erro ao buscar personagens. Tente novamente.');
    }
}

async function addFavoriteCharacter(id, name, imageUrl) {
    console.log('addFavoriteCharacter chamada com:', id, name, imageUrl);
    
    const csrfToken = getGlobalCsrfToken();
    console.log('CSRF Token:', csrfToken);
    
    try {
        const response = await fetch("/lists/personagens/add/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ id: id, name: name, image: imageUrl })
        });
        
        console.log('Response status:', response.status);
        console.log('Response ok:', response.ok);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Erro do servidor:', errorText);
            throw new Error(`Erro do servidor: ${response.statusText}`);
        }
        
        const result = await response.json();
        console.log('Result:', result);
        
        if (result.status === 'success') {
            alert(`${name} foi adicionado aos seus favoritos!`);
            if (window.location.pathname.includes('personagens-favoritos')) {
                location.reload();
            } else {
                window.location.href = '/lists/personagens/';
            }
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Erro completo:', error);
        alert('Não foi possível adicionar o favorito.');
    }
}

async function removeFavorite(id) {
    if (!confirm("Tem certeza que deseja remover este personagem?")) return;
    
    const csrfToken = getGlobalCsrfToken();
    
    try {
        const response = await fetch("/lists/personagens/remove/", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ id: id })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            const cardToRemove = document.getElementById(`fav-card-${id}`);
            if (cardToRemove) {
                cardToRemove.remove();
            }
            
            const favoritesSection = document.getElementById('favorites');
            const remainingCards = favoritesSection.querySelectorAll('.char-card');
            
            if (remainingCards.length === 0) {
                location.reload();
            } else {
                alert('Personagem removido!');
            }
        } else {
            alert(result.message);
        }
    } catch (error) {
        console.error('Erro ao remover favorito:', error);
        alert('Erro ao remover favorito. Tente novamente.');
    }
}