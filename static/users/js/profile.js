document.addEventListener('DOMContentLoaded', function() {
    const internalLinks = document.querySelectorAll('a[href^="#"]');
    internalLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    observer.unobserve(img);
                }
            }
        });
    }, observerOptions);

    const lazyImages = document.querySelectorAll('img[data-src]');
    lazyImages.forEach(img => {
        imageObserver.observe(img);
    });

    // Animações suaves para cards
    const cards = document.querySelectorAll('.friend-card, .stat-item');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in');
    });

    const friendshipActions = document.querySelectorAll('a[href*="remove_friend"], a[href*="reject_friend_request"]');
    friendshipActions.forEach(link => {
        link.addEventListener('click', function(e) {
            const action = this.href.includes('remove_friend') ? 'remover da lista de amigos' : 'rejeitar o pedido de amizade';
            const username = this.href.match(/\/([^\/]+)\//)?.[1] || 'este usuário';
            
            if (!confirm(`Tem certeza que deseja ${action} de ${username}?`)) {
                e.preventDefault();
            }
        });
    });

    // Tooltip para estatísticas
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        const label = item.querySelector('.stat-label').textContent.toLowerCase();
        let tooltipText = '';
        
        switch(label) {
            case 'animes':
                tooltipText = 'Total de animes na lista';
                break;
            case 'episódios':
                tooltipText = 'Total de episódios assistidos';
                break;
            case 'amigos':
                tooltipText = 'Número de amigos adicionados';
                break;
        }
        
        if (tooltipText) {
            item.setAttribute('title', tooltipText);
        }
    });

    const bioText = document.querySelector('.bio-text');
    if (bioText && bioText.textContent.length > 200) {
        const fullText = bioText.textContent;
        const shortText = fullText.substring(0, 200) + '...';
        
        bioText.textContent = shortText;
        
        const expandBtn = document.createElement('button');
        expandBtn.textContent = 'Ver mais';
        expandBtn.className = 'expand-bio-btn';
        expandBtn.style.cssText = `
            background: none;
            border: none;
            color: var(--primary-pink);
            cursor: pointer;
            font-size: 0.9rem;
            margin-top: 0.5rem;
            padding: 0;
        `;
        
        let isExpanded = false;
        expandBtn.addEventListener('click', function() {
            if (isExpanded) {
                bioText.textContent = shortText;
                this.textContent = 'Ver mais';
            } else {
                bioText.textContent = fullText;
                this.textContent = 'Ver menos';
            }
            isExpanded = !isExpanded;
        });
        
        bioText.parentNode.appendChild(expandBtn);
    }

    const currentUrl = window.location.pathname;
    const actionBtns = document.querySelectorAll('.btn[href]');
    actionBtns.forEach(btn => {
        if (currentUrl.includes(btn.getAttribute('href'))) {
            btn.classList.add('active');
        }
    });

    const friendBtns = document.querySelectorAll('.btn[href*="friend"]');
    friendBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const originalText = this.querySelector('span:last-child')?.textContent || this.textContent;
            const icon = this.querySelector('svg');
            
            if (icon) {
                icon.style.animation = 'spin 1s linear infinite';
            }

            setTimeout(() => {
                const textElement = this.querySelector('span:last-child') || this;
                textElement.textContent = 'Processando...';
            }, 100);
        });
    });

    // Adicionar animação de spin
    const style = document.createElement('style');
    style.textContent = `
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        @keyframes fade-in {
            from { 
                opacity: 0; 
                transform: translateY(20px); 
            }
            to { 
                opacity: 1; 
                transform: translateY(0); 
            }
        }
        
        .fade-in {
            animation: fade-in 0.6s ease-out forwards;
        }
        
        .expand-bio-btn:hover {
            color: var(--primary-lavender) !important;
        }
        
        .btn.active {
            background: rgba(255, 182, 193, 0.2) !important;
            border-color: var(--primary-pink) !important;
        }
    `;
    document.head.appendChild(style);
});

document.addEventListener('DOMContentLoaded', function() {
    // Avatar preview
    const avatarInput = document.getElementById('id_avatar');
    const avatarPreview = document.getElementById('avatarPreview');
    const currentAvatar = avatarPreview.src;
    
    avatarInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                avatarPreview.src = e.target.result;
            };
            reader.readAsDataURL(file);
        }
    });
    
    document.querySelector('.current-avatar').addEventListener('click', function() {
        avatarInput.click();
    });
    
    const bioTextarea = document.getElementById('id_bio');
    const bioCounter = document.getElementById('bioCounter');
    
    if (bioTextarea && bioCounter) {
        bioTextarea.addEventListener('input', function() {
            const length = this.value.length;
            bioCounter.textContent = length;
            
            if (length > 450) {
                bioCounter.style.color = '#ff453a';
            } else if (length > 400) {
                bioCounter.style.color = '#ff9500';
            } else {
                bioCounter.style.color = 'var(--text-muted)';
            }
        });
    }
    
    // Mostrar/ocultar campo gênero personalizado
    const genderSelect = document.getElementById('id_gender');
    const customGenderGroup = document.getElementById('customGenderGroup');
    
    if (genderSelect && customGenderGroup) {
        genderSelect.addEventListener('change', function() {
            if (this.value === 'CUSTOM') {
                customGenderGroup.style.display = 'block';
                customGenderGroup.querySelector('input').focus();
            } else {
                customGenderGroup.style.display = 'none';
                customGenderGroup.querySelector('input').value = '';
            }
        });
    }
    
    // Validação de formulário
    const form = document.querySelector('.edit-profile-form');
    form.addEventListener('submit', function(e) {
        const bio = bioTextarea.value;
        
        if (bio.length > 500) {
            e.preventDefault();
            alert('A biografia deve ter no máximo 500 caracteres.');
            bioTextarea.focus();
            return false;
        }
    });
});