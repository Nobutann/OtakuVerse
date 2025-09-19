document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const inputs = document.querySelectorAll('.form-input');
    const submitBtn = document.querySelector('.submit-btn');

    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.classList.add('input-animation');
        });

        input.addEventListener('blur', function() {
            this.classList.remove('input-animation');
        });

        input.addEventListener('animationend', function() {
            this.classList.remove('input-animation');
        });
    });

    // validação do formulário
    form.addEventListener('submit', function(e) {
        const username = usernameInput.value.trim();
        const password = passwordInput.value;

        clearAllErrors();
        let hasError = false;

        if (username.length < 3) {
            showError('Usuário muito curto, senpai~ (´･ω･`)');
            hasError = true;
        }

        if (password.length < 1) {
            showError('Precisa digitar a senha, baka! (╯°□°）╯︵ ┻━┻');
            hasError = true;
        }

        if (hasError) {
            e.preventDefault();
            shakeForm();
            return false;
        }

        showSubmitAnimation();
    });

    function showError(message) {
        clearAllErrors();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<span class="error-icon">⚠️</span>${message}`;
        
        form.parentNode.insertBefore(errorDiv, form);
    }

    function clearAllErrors() {
        const existingErrors = document.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());
    }

    function shakeForm() {
        const container = document.querySelector('.signup-container');
        container.style.animation = 'shake 0.5s ease-in-out';
        
        setTimeout(() => {
            container.style.animation = '';
        }, 500);
    }

    function showSubmitAnimation() {
        const btnText = document.querySelector('.btn-text');

        submitBtn.disabled = true;
        btnText.textContent = 'Entrando... (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧';

        submitBtn.style.background = 'linear-gradient(135deg, #3498db 0%, #2ecc71 100%)';
        submitBtn.style.animation = 'pulse 1s infinite';
    }

    // animações extras (igual no signup.js)
    const style = document.createElement('style');
    style.textContent = `
        @keyframes shake {
            0%, 20%, 40%, 60%, 80%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.02); }
        }
    `;
    document.head.appendChild(style);

    const hearts = document.querySelectorAll('.floating-heart');
    hearts.forEach(heart => {
        heart.addEventListener('click', function() {
            this.style.animation = 'none';
            this.style.transform = 'scale(1.5)';
            this.textContent = '💖';
            
            setTimeout(() => {
                this.style.animation = 'floatHeart 8s ease-in-out infinite';
                this.textContent = '♡';
                this.style.transform = '';
            }, 1000);
        });
    });
});
