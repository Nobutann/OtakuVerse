from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile, Friendship, FriendRequest
from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.http import Http404

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

        return redirect('main:homepage')
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

            next_url = request.GET.get('next', '/')
            
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
        'recent_anime_entries': user.anime_entries.select_related("anime")[:6],
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

@login_required
def profile_settings(request):
    profile = request.user.profile

    if request.method == 'POST':
        # Campos básicos do perfil
        bio = request.POST.get('bio', '')
        is_public = request.POST.get('is_public') == 'True'
        show_stats = request.POST.get('show_stats') == 'True'
        avatar = request.FILES.get('avatar')

        # Validações
        if len(bio) > 500:
            return render(request, 'users/profile_settings.html', {
                'user': request.user,  # IMPORTANTE!
                'profile': profile, 
                'error': 'Bio deve ter no máximo 500 caracteres'
            })

        # Atualizar campos
        profile.bio = bio
        profile.isPublic = is_public
        profile.showStats = show_stats

        # Atualizar avatar se fornecido
        if avatar:
            profile.avatar = avatar

        profile.save()

        return render(request, 'users/profile_settings.html', {
            'user': request.user,  # IMPORTANTE!
            'profile': profile, 
            'success': 'Configurações atualizadas com sucesso!'
        })
    
    context = {
        'user': request.user,  # IMPORTANTE!
        'profile': profile,
    }

    return render(request, 'users/profile_settings.html', context)

@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    from_user = request.user
    
    if from_user == to_user:
        return redirect('user:profile', username=username)
    
    if Friendship.objects.filter(
        user1=min(from_user, to_user, key=lambda u: u.id),
        user2=max(from_user, to_user, key=lambda u: u.id)
    ).exists():
        return redirect('users:profile', username=username)
    
    existing_request = FriendRequest.objects.filter(
        from_user=from_user,
        to_user=to_user
    ).first()

    if existing_request:
        if existing_request.status == 'pending':
            return redirect('users:profile', username=username)
        elif existing_request.status() == 'rejected':
            existing_request.status = 'pending'
            existing_request.save()
    else:
        FriendRequest.objects.filter(
            from_user=from_user,
            to_user=to_user,
            status='pending'
        )

    return redirect('users:profile', username=username)

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if friend_request.to_user != request.user:
        raise Http404("Pedido não encontrado")
    
    if friend_request.status != 'pending':
        return redirect('users.friend_requests')
    
    friend_request.accept()

    return redirect('users:friend_requests')

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if friend_request.to_user != request.user:
        raise Http404("Pedido não encontrado")
    
    if friend_request.status != 'pending':
        return redirect('users:friend_requests')
    
    friend_request.reject()

    return redirect('users:friend_requests')

@login_required
def cancel_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id)

    if friend_request.from_user != request.user:
        raise Http404("Pedido não encontrado")
    
    if friend_request.status != 'pending':
        return redirect('users:friend_requests')
    
    friend_request.cancel()

    return redirect('users:friend_requests')

@login_required
def remove_friend(request, username):
    friend_user = get_object_or_404(User, username=username)
    current_user = request.user

    if current_user == friend_user:
        return redirect('users:profile', username=username)
    
    friendship = Friendship.objects.filter(
        user1=min(current_user, friend_user, key=lambda u: u.id),
        user2=max(current_user, friend_user, key=lambda u: u.id)
    ).first()

    if not friendship:
        return redirect('users:profile', username=username)
    
    friendship.delete()

    return redirect('users:profile', username=username)

def friends_list(request, username):
    user = get_object_or_404(User, username=username)

    if not user.profile.isPublic and request.user != user:
        return render(request, 'user/profile_restricted.html', {'user': user})
    
    friendships = Friendship.objects.filter(
        Q(user1=user) | Q(user2=user)
    )

    friends = []
    for friendship in friendships:
        friend = friendship.get_other_user(user)
        friends.append(friend)

    friends_count = len(friends)

    context = {
        'user': user,
        'friends': friends,
        'friends_count': friends_count,
        'is_own': request.user == user,
    }

    return render(request, 'users/friends_list.html', context)

def search_users(request):
    query = request.GET.get('q', '').strip()
    users = []

    if query:
        users = User.objects.filter(
            username__icontains=query,
            profile__isPublic=True
        ).select_related('profile')[:20]

    context = {
        'query': query,
        'users': users,
        'users_count': len(users),
    }

    return render(request, 'users/search_users.html', context)

@login_required
def friends_request(request):
    received_requests = FriendRequest.objects.filter(
        to_user = request.user, status='pending'
    ).select_related('from_user__profile').order_by('-timestamp')

    sent_requests = FriendRequest.objects.filter(
        from_user = request.user,
        status = 'pending'
    ).select_related('to_user__profile').order_by('-timespamp')

    context = {
        'received_requests': received_requests,
        'sent_requests': sent_requests,
        'received_count': received_requests.count(),
        'sent_count': sent_requests.count(),
    }

    return render(request, 'users/friend_requests.html')