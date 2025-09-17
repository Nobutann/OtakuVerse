from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if not all([username, email, password, password_confirm]):
            return render(request, 'users/signup.html', {'error': 'Todos os campos precisam ser preenchidos'})
        
        if len(password) < 8:
            return render(request, 'users/signup.html', {'error': 'A senha deve ter pelo menos 8 caracteres'})
        
        if password != password_confirm:
            return render(request, 'users/signup.html', {'error': 'As senhas não correspondem'})
        
        try:
            validate_email(email)
        except ValidationError:
            return render(request, 'users/signup.html', {'error': 'Email inválido'})

        if User.objects.filter(username=username).exists():
            return render(request, 'users/signup.html', {'error': 'Nome de usuário já existe.'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'users/signup.html', {'error': 'Email já registrado.'})
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')
    else:
        return render(request, 'users/signup.html')