from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Friendship, FriendRequest
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required

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
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not all([username, password]):
            return render(request, 'users/login.html', {'error': 'Todos os campos precisam ser preenchidos'})
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            next_url = request.GET.get('next', f'/user/{user.username}/')
            
            return redirect(next_url)
        else:
            return render(request, 'users/login.html', {'error': 'Usuário ou senha incorretos'})
        
    return render(request, 'users/login.html')

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('users:login')

def show_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    if not profile.isPublic and request.user != user:
        return render(request, 'users/profile_restricted', {'user': user})
    
    friendship_status = None

    if request.user.is_authenticated and request.user != user:
        if Friendship.objects.filter(
            user1=min(request.user, user, key=lambda u: u.id),
            user2=max(request.user, user, key=lambda u: u.id)
        ).exists():
            friendship_status = 'friends'
        else:
            pending_sent = FriendRequest.objects.filter(
                from_user=request.user, to_user=user, status='pending'
            ).exists()
            
            pending_received = FriendRequest.objects.filter(
                from_user=user, to_user=request.user, status='pending'
            ).exists()

            if pending_sent:
                friendship_status = 'request_sent'
            elif pending_received:
                friendship_status = 'request_received'
            else:
                friendship_status = 'none'

    friends = []

    friendships = Friendship.objects.filter(
        Q(user1=user) | Q(user2=user)
    )[:6]

    for friendship in friendships:
        friend = friendship.get_other_user(user)
        friends.append(friend)

    context = {
        'user': user,
        'profile': profile,
        'friendship_status': friendship_status,
        'friends': friends,
        'friends_count': Friendship.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).count(),
        'is_own_profile': request.user == user,
    }

    return render(request, 'users/profile.html', context)

@login_required
def edit_profile(request):
    profile = request.user.profile

    if request.method == 'POST':
        bio = request.POST.get('bio', '')
        birth_date = request.POST.get('birth_date')
        gender = request.POST.get('gender')
        custom_gender = request.POST.get('custom_gender', '')
        is_public = request.POST.get('is_public') == 'on'
        show_stats = request.POST.get('show_stats') == 'on'
        avatar = request.FILES.get('avatar')

        if len(bio) > 500:
            return render(request, 'users/edit_profile.html', {'profile': profile, 'error': 'Bio deve ter no máximo 500 caracteres'})
        
        if birth_date:
            try:
                datetime.strptime(birth_date, '%Y-%m-%d')
            except ValueError:
                return render(request, 'users/edit_profile.html', {'profile': profile, 'error': 'Data de nascimento inválida'})
            
        
        profile.bio = bio
        profile.birthDate = birth_date if birth_date else None
        profile.gender = gender
        profile.custom_gender = custom_gender if gender == 'CUSTOM' else ''
        profile.isPublic = is_public
        profile.showStats = show_stats

        if avatar:
            profile.avatar = avatar

        profile.save()

        return redirect('users:profile', username=request.user.username)
    
    context = {
        'profile': profile,
        'gender_choices': UserProfile.GENDER,
    }

    return render(request, 'users/edit_profile.html', context)