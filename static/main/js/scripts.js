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

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 JavaScript carregado!');
    
    const episodeCounter = document.querySelector('.episode-counter');
    
    if (!episodeCounter) {
        console.log('❌ Elemento .episode-counter não encontrado!');
        return;
    }
    
    console.log('✅ Episode counter encontrado:', episodeCounter);
    
    const entryId = episodeCounter.dataset.entryId;
    const maxEpisodes = parseInt(episodeCounter.dataset.maxEpisodes) || 0;
    
    console.log('📊 Entry ID:', entryId);
    console.log('📺 Max Episodes:', maxEpisodes);
    
    const decreaseBtn = episodeCounter.querySelector('.decrease-ep');
    const increaseBtn = episodeCounter.querySelector('.increase-ep');
    const episodeDisplay = episodeCounter.querySelector('.episodes-watched');
    
    console.log('🔽 Decrease Button:', decreaseBtn);
    console.log('🔼 Increase Button:', increaseBtn);
    console.log('📺 Episode Display:', episodeDisplay);
    
    // Função para obter o CSRF token
    function getCsrfToken() {
        // 1. Tenta pegar do meta tag (mais confiável)
        let metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            console.log('🔑 CSRF token encontrado no meta tag');
            return metaTag.getAttribute('content');
        }
        
        // 2. Tenta pegar do input hidden
        let token = document.querySelector('[name=csrfmiddlewaretoken]');
        if (token && token.value && token.value.length > 10) {
            console.log('🔑 CSRF token encontrado no form:', token.value.length, 'caracteres');
            return token.value;
        }
        
        // 3. Tenta pegar do cookie
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken' && value && value.length > 10) {
                console.log('🔑 CSRF token encontrado no cookie:', value.length, 'caracteres');
                return decodeURIComponent(value);
            }
        }
        
        console.log('❌ CSRF token não encontrado ou inválido!');
        return '';
    }
    
    // Função para atualizar episódios no servidor
    function updateEpisodes(newCount) {
        console.log('🚀 Enviando requisição para atualizar episódios:', newCount);
        const url = `/lists/update-episodes/${entryId}/`;
        console.log('🔗 URL:', url);
        
        // Pegar CSRF token do formulário de avaliação que já existe na página
        const reviewForm = document.querySelector('.review-form');
        let csrfToken = '';
        
        if (reviewForm) {
            const csrfInput = reviewForm.querySelector('[name=csrfmiddlewaretoken]');
            if (csrfInput) {
                csrfToken = csrfInput.value;
                console.log('🔑 CSRF Token do form de review, length:', csrfToken.length);
            }
        }
        
        // Se não encontrou, tenta do form de adicionar à lista
        if (!csrfToken) {
            const addForm = document.querySelector('.add-to-list-form');
            if (addForm) {
                const csrfInput = addForm.querySelector('[name=csrfmiddlewaretoken]');
                if (csrfInput) {
                    csrfToken = csrfInput.value;
                    console.log('🔑 CSRF Token do form de add, length:', csrfToken.length);
                }
            }
        }
        
        if (!csrfToken) {
            console.error('❌ Nenhum CSRF token encontrado!');
            showFeedback('❌ Erro de segurança', 'error');
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
            console.log('📡 Response status:', response.status);
            return response.text();
        })
        .then(text => {
            console.log('📦 Response text:', text);
            try {
                const data = JSON.parse(text);
                console.log('📦 Parsed data:', data);
                
                if (data.success) {
                    episodeDisplay.textContent = data.episodes_watched;
                    showFeedback('✅ Episódios atualizados!', 'success');
                    
                    if (maxEpisodes > 0 && data.episodes_watched >= maxEpisodes) {
                        setTimeout(() => {
                            if (confirm('Você assistiu todos os episódios! Deseja marcar como "Completo"?')) {
                                updateStatus('completed');
                            }
                        }, 500);
                    }
                } else {
                    console.log('❌ Erro na resposta:', data.error);
                    showFeedback(`❌ ${data.error}`, 'error');
                }
            } catch (e) {
                console.error('❌ Erro ao parsear JSON:', e);
                showFeedback('❌ Erro de resposta do servidor', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            showFeedback('❌ Erro de conexão', 'error');
        });
    }
    
    // Função para atualizar status
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
                // Recarregar a página para mostrar o status atualizado
                location.reload();
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar status:', error);
        });
    }
    
    // Função para mostrar feedback visual
    function showFeedback(message, type) {
        // Remove feedback anterior se existir
        const existingFeedback = document.querySelector('.episode-feedback');
        if (existingFeedback) {
            existingFeedback.remove();
        }
        
        // Cria novo feedback
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
        
        // Adiciona CSS da animação se não existir
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
        
        // Remove o feedback após 2 segundos
        setTimeout(() => {
            if (feedback.parentNode) {
                feedback.remove();
            }
        }, 2000);
    }
    
    // Event listeners para os botões
    if (decreaseBtn) {
        decreaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🔽 Botão decrease clicado!');
            const currentCount = parseInt(episodeDisplay.textContent) || 0;
            console.log('📊 Current count:', currentCount);
            
            if (currentCount > 0) {
                const newCount = currentCount - 1;
                console.log('📊 New count:', newCount);
                updateEpisodes(newCount);
            } else {
                showFeedback('❌ Não pode ser menor que 0', 'error');
            }
        });
    } else {
        console.log('❌ Decrease button não encontrado!');
    }
    
    if (increaseBtn) {
        increaseBtn.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🔼 Botão increase clicado!');
            const currentCount = parseInt(episodeDisplay.textContent) || 0;
            console.log('📊 Current count:', currentCount);
            
            // Verifica se há limite máximo
            if (maxEpisodes > 0 && currentCount >= maxEpisodes) {
                showFeedback(`❌ Máximo: ${maxEpisodes} episódios`, 'error');
                return;
            }
            
            const newCount = currentCount + 1;
            console.log('📊 New count:', newCount);
            updateEpisodes(newCount);
        });
    } else {
        console.log('❌ Increase button não encontrado!');
    }
    
    // Adicionar estilo para os botões (se não tiver no CSS)
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