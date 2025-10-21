from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.models import Q

def homepage(request):
    context = {'featured_anime': [], 'erro': None}
    ids = [5081, 17074, 9260, 28025, 32268, 35247, 14829, 34599]
    try:
        featured_anime = []
        for anime_id in ids:
            try:
                response = requests.get(f"https://api.jikan.moe/v4/anime/{anime_id}", timeout=8)
                response.raise_for_status()
                data = response.json().get('data')
                if data:
                    featured_anime.append(data)
            except requests.exceptions.RequestException as e:
                print(f"Erro ao buscar anime {anime_id}: {e}")
                continue
        context['featured_anime'] = featured_anime
    except Exception as e:
        context['erro'] = f"Erro ao carregar recomendações: {e}"
        print(f"Erro na home: {e}")
    return render(request, 'main/index.html', context)

def search_sugestions(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'anime')
    suggestions = []

    if not query or len(query) < 3:
        return JsonResponse({'suggestions': []})

    def fetch_jikan(endpoint, params):
        try:
            response = requests.get(f"https://api.jikan.moe/v4/{endpoint}", params=params, timeout=5)
            response.raise_for_status()
            return response.json().get('data', [])
        except requests.RequestException as e:
            print(f"Erro na API Jikan para {endpoint}: {e}")
            return []

    if search_type == 'anime':
        results = fetch_jikan('anime', {'q': query, 'limit': 5})
        for item in results:
            suggestions.append({
                'id': item.get('mal_id'),
                'title': item.get('title'),
                'image': item.get('images', {}).get('jpg', {}).get('image_url'),
                'type': 'anime'
            })
    elif search_type == 'character':
        results = fetch_jikan('characters', {'q': query, 'limit': 5})
        for item in results:
            suggestions.append({
                'id': item.get('mal_id'),
                'title': item.get('name'),
                'image': item.get('images', {}).get('jpg', {}).get('image_url'),
                'type': 'personagem'
            })

    elif search_type == 'user':
        users = User.objects.select_related('profile').filter(
            Q(username__icontains=query)
        )[:5]
        
        for user in users:
            suggestions.append({
                'id': user.username,
                'title': user.username,
                'image': user.profile.avatar.url if hasattr(user, 'profile') else '/static/avatars/default.jpg',
                'type': 'usuário'
            })


    return JsonResponse({'suggestions': suggestions})

def search_redirect(request):
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('search_type', 'anime')
    if not query:
        return redirect('main:homepage')
    if search_type == 'character':
        redirect_url = f"{reverse('main:character_search_results')}?q={query}"
        return redirect(redirect_url)
    elif search_type == 'user':
        redirect_url = f"{reverse('main:user_search_results')}?q={query}"
        return redirect(redirect_url)
    redirect_url = f"{reverse('animes:buscar_anime')}?q={query}"
    return redirect(redirect_url)

def character_search_results(request):
    query = request.GET.get('q', '')
    context = {'query': query, 'characters': [], 'error': None}
    if query:
        try:
            response = requests.get("https://api.jikan.moe/v4/characters", params={'q': query}, timeout=10)
            response.raise_for_status()
            data = response.json()
            context['characters'] = data.get('data', [])
        except requests.exceptions.RequestException as e:
            context['error'] = f"Ocorreu um erro ao buscar os personagens: {e}"
    return render(request, 'main/character_search_results.html', context)

def user_search_results(request):
    query = request.GET.get('q', '').strip()
    
    context = {
        'query': query,
        'users': [],
        'total_results': 0
    }
    
    if query:
        users = User.objects.select_related('profile').filter(
            Q(username__icontains=query) | Q(profile__bio__icontains=query)
        ).order_by('username')
        
        context['users'] = users
        context['total_results'] = users.count()
    
    return render(request, 'main/user_search_results.html', context)