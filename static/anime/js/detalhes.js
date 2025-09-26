// detalhes.js - Contador de Episódios
document.addEventListener('DOMContentLoaded', function() {
    const episodeCounter = document.querySelector('.episode-counter');
    
    if (!episodeCounter) return; // Se não houver contador na página, não fazer nada
    
    const entryId = episodeCounter.dataset.entryId;
    const maxEpisodes = parseInt(episodeCounter.dataset.maxEpisodes) || 0;
    
    const decreaseBtn = episodeCounter.querySelector('.decrease-ep');
    const increaseBtn = episodeCounter.querySelector('.increase-ep');
    const episodeDisplay = episodeCounter.querySelector('.episodes-watched');
    
    // Função para obter o CSRF token
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]').value;
    }
    
    // Função para atualizar episódios no servidor
    function updateEpisodes(newCount) {
        fetch(`/lists/update-episodes/${entryId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCsrfToken()
            },
            body: `episodes_watched=${newCount}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                episodeDisplay.textContent = data.episodes_watched;
                
                // Feedback visual
                showFeedback('✅ Episódios atualizados!', 'success');
                
                // Se completou todos os episódios, perguntar se quer marcar como completo
                if (maxEpisodes > 0 && data.episodes_watched >= maxEpisodes) {
                    setTimeout(() => {
                        if (confirm('Você assistiu todos os episódios! Deseja marcar como "Completo"?')) {
                            updateStatus('completed');
                        }
                    }, 500);
                }
            } else {
                showFeedback('❌ Erro ao atualizar episódios', 'error');
            }
        })
        .catch(error => {
            console.error('Erro:', error);
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
    decreaseBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const currentCount = parseInt(episodeDisplay.textContent) || 0;
        
        if (currentCount > 0) {
            const newCount = currentCount - 1;
            updateEpisodes(newCount);
        } else {
            showFeedback('❌ Não pode ser menor que 0', 'error');
        }
    });
    
    increaseBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const currentCount = parseInt(episodeDisplay.textContent) || 0;
        
        // Verifica se há limite máximo
        if (maxEpisodes > 0 && currentCount >= maxEpisodes) {
            showFeedback(`❌ Máximo: ${maxEpisodes} episódios`, 'error');
            return;
        }
        
        const newCount = currentCount + 1;
        updateEpisodes(newCount);
    });
    
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

// Função para debug (remover em produção)
function debugEpisodeCounter() {
    const counter = document.querySelector('.episode-counter');
    if (counter) {
        console.log('🎯 Episode Counter encontrado!');
        console.log('📊 Entry ID:', counter.dataset.entryId);
        console.log('📺 Max Episodes:', counter.dataset.maxEpisodes);
        console.log('▶️ Current Episodes:', counter.querySelector('.episodes-watched').textContent);
    } else {
        console.log('❌ Episode Counter não encontrado!');
    }
}