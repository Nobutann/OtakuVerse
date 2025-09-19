document.getElementById('signupForm').addEventListener('submit', function(e) {
    const form = this;

    // Remove mensagens antigas
    let existingMsg = form.querySelectorAll('.js-error');
    existingMsg.forEach(msg => msg.remove());

    const username = form.username.value.trim();
    const email = form.email.value.trim();
    const password = form.password.value.trim();
    const confirm = form.password_confirm.value.trim();

    function showError(text) {
        const div = document.createElement('div');
        div.className = 'js-error';
        div.textContent = text;
        div.style.color = '#ff4c4c';
        div.style.fontWeight = 'bold';
        div.style.marginBottom = '10px';
        div.style.textAlign = 'center';
        div.style.opacity = 0;
        div.style.transition = 'opacity 0.5s ease';

        form.querySelector('button[type="submit"]').before(div);

        setTimeout(() => div.style.opacity = 1, 10);
        setTimeout(() => { div.style.opacity = 0; setTimeout(() => div.remove(), 500); }, 4000);
    }

    if (!username || !email || !password || !confirm) {
        e.preventDefault();
        showError('Todos os campos precisam ser preenchidos.');
        return;
    }

    if (password.length < 8) {
        e.preventDefault();
        showError('A senha deve ter pelo menos 8 caracteres.');
        return;
    }

    if (password !== confirm) {
        e.preventDefault();
        showError('As senhas não correspondem.');
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        e.preventDefault();
        showError('Email inválido.');
        return;
    }
});
