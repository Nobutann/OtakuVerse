from django.shortcuts import render, redirect
import requests
from reviews.models import Review
from django.db.models import Avg
from django.contrib.auth.decorators import login_required

def buscar_anime(request):
    query = request.GET.get('q', '')
    contexto = {
        'query': query,
        'resultados': [],
        'erro': None,
    }

    if query:
        api_url = 'https://api.jikan.moe/v4/anime'
        params = {'q': query}

        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
            
            print(f"Dados da API: {dados_api}")
            
            contexto['resultados'] = dados_api.get('data', [])

        except requests.exceptions.RequestException as e:
            contexto['erro'] = f"Ocorreu um erro ao buscar na API: {e}"
            print(contexto['erro'])

    return render(request, 'animes/pagina_de_busca.html', contexto)

def detalhes_anime(request, anime_id):
    
    contexto = {
        'anime': None,
        'erro': None,
        'reviews': [],
        'average_score': None,
    }

    api_url = f'https://api.jikan.moe/v4/anime/{anime_id}'
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        dados_api = response.json()
        
        anime = dados_api.get('data')
        if anime:
            anime['genres'] = [g['name'] for g in anime.get('genres', [])]
            anime['studios'] = [s['name'] for s in anime.get('studios', [])]
        
        contexto['anime'] = anime

    except requests.exceptions.RequestException as e:
        contexto['erro'] = f"Ocorreu um erro ao buscar os detalhes do anime: {e}"
        print(contexto['erro'])

    reviews = Review.objects.filter(anime_id=anime_id).order_by('-created_at')
    contexto['reviews'] = reviews
    contexto['average_score'] = reviews.aggregate(Avg('score'))['score__avg']

    return render(request, 'animes/pagina_de_detalhes.html', contexto)