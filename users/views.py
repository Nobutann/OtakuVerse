from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if not all([username, email, password, password_confirm]):
            return render(request, 'users/login.html', {'error': 'Todos os campos precisam ser preenchidos'})
        if password != password_confirm:
            return render(request, 'users/login.html', {'error': 'As senhas não correspondem'})