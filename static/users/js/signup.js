document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('signupForm');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('password_confirm');
    const strengthBar = document.getElementById('strengthBar');
    const strengthText = document.getElementById('strengthText');
    const inputs = document.querySelectorAll('.form-input');
    const submitBtn = document.querySelector('.submit-btn');

    const strengthMessages = {
        0: '',
        1: 'Muito fraca... (つ﹏⊂)',
        2: 'Fraca demais, senpai~ (´･ω･`)',
        3: 'Melhorando! ٩(◕‿◕)۶',
        4: 'Boa senha! (＾◡＾)',
        5: 'Perfeita! Sugoi desu~ ✨(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧'
    };

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

    passwordInput.addEventListener('input', function() {
        const password = this.value;
        const strength = calculatePasswordStrength(password);
        
        strengthBar.className = 'password-strength-bar';
        
        if (password.length > 0) {
            if (strength <= 2) {
                strengthBar.classList.add('strength-weak');
            } else if (strength <= 4) {
                strengthBar.classList.add('strength-medium');
            } else {
                strengthBar.classList.add('strength-strong');
            }
            
            strengthText.textContent = strengthMessages[strength] || strengthMessages[0];
        } else {
            strengthText.textContent = '';
        }
    });

    confirmPasswordInput.addEventListener('input', function() {
        const password = passwordInput.value;
        const confirmPassword = this.value;
        
        if (confirmPassword && password !== confirmPassword) {
            this.style.borderColor = '#E74C3C';
            this.style.boxShadow = '0 0 15px rgba(231, 76, 60, 0.3)';
            showCuteError(this, 'As senhas não batem... (╯︵╰)');
        } else if (confirmPassword && password === confirmPassword) {
            this.style.borderColor = '#98FB98';
            this.style.boxShadow = '0 0 15px rgba(152, 251, 152, 0.3)';
            removeCuteError(this);
        } else {
            this.style.borderColor = '#404040';
            this.style.boxShadow = 'none';
            removeCuteError(this);
        }
    });

    form.addEventListener('submit', function(e) {
        const username = document.getElementById('username').value;
        const email = document.getElementById('email').value;
        const password = passwordInput.value;
        const confirmPassword = confirmPasswordInput.value;
        
        clearAllErrors();
        
        let hasError = false;
        
        if (username.length < 3) {
            showError('Nome de usuário muito curto, senpai~ (´･ω･`)');
            hasError = true;
        }
        
        if (!isValidEmail(email)) {
            showError('Email inválido, ne~ (￣▽￣)');
            hasError = true;
        }
        
        if (password.length < 8) {
            showError('Senha muito curta! Precisa de pelo menos 8 caracteres~ (｡•́︿•̀｡)');
            hasError = true;
        }
        
        if (password !== confirmPassword) {
            showError('As senhas não correspondem, baka! (>_<)');
            hasError = true;
        }
        
        if (hasError) {
            e.preventDefault();
            shakeForm();
            return false;
        }
        
        showSubmitAnimation();
    });

    function calculatePasswordStrength(password) {
        let strength = 0;
        
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password)) strength++;
        if (/[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;
        
        return strength;
    }

    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    function showError(message) {
        clearAllErrors();
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.innerHTML = `<span class="error-icon">⚠️</span>${message}`;
        
        const form = document.getElementById('signupForm');
        form.parentNode.insertBefore(errorDiv, form);
    }

    function clearAllErrors() {
        const existingErrors = document.querySelectorAll('.error-message');
        existingErrors.forEach(error => error.remove());
    }

    function showCuteError(input, message) {
        removeCuteError(input);
        
        const errorSpan = document.createElement('span');
        errorSpan.className = 'cute-error';
        errorSpan.textContent = message;
        errorSpan.style.cssText = `
            color: #FF6B9D;
            font-size: 0.8rem;
            position: absolute;
            top: 100%;
            left: 0;
            margin-top: 0.3rem;
            animation: fadeIn 0.3s ease-out;
        `;
        
        input.parentElement.style.position = 'relative';
        input.parentElement.appendChild(errorSpan);
    }

    function removeCuteError(input) {
        const existingError = input.parentElement.querySelector('.cute-error');
        if (existingError) {
            existingError.remove();
        }
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
        const btnHeart = document.querySelector('.btn-heart');
        
        submitBtn.disabled = true;
        btnText.textContent = 'Criando conta...';
        btnHeart.textContent = '🌸';
        
        submitBtn.style.background = 'linear-gradient(135deg, #c0392b 0%, #e74c3c 100%)';
        submitBtn.style.animation = 'pulse 1s infinite';
    }

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
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-5px); }
            to { opacity: 1; transform: translateY(0); }
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