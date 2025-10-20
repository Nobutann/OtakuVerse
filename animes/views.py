from django.shortcuts import render
import requests
from django.db.models import Avg, Count
from lists.models import Anime, AnimeList

def buscar_anime(request):
    query = request.GET.get('q', '')
    contexto = {
        'query': query,
        'resultados': [],
        'erro': None,
    }

    if query:
        api_url = 'https://api.jikan.moe/v4/anime'
        
        rating_selecionado = request.GET.get('rating', 'padrao')
        
        params = {
            'q': query
        }
        
        if rating_selecionado == 'padrao':
            params['genres_exclude'] = '12'
        else:
            params['rating'] = rating_selecionado
            params['genres_exclude'] = '12'

        if request.GET.get('type'):
            params['type'] = request.GET.get('type')
        
        if request.GET.get('status'):
            params['status'] = request.GET.get('status')
            
        if request.GET.get('order_by'):
            params['order_by'] = request.GET.get('order_by')
            
        if request.GET.get('year'):
            params['start_date'] = request.GET.get('year')

        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
            
            if rating_selecionado == 'adulto':
                contexto['resultados'] = dados_api.get('data', [])
            elif rating_selecionado == 'padrao':
                resultados_filtrados = []
                for anime in dados_api.get('data', []):
                    if anime.get('rating') != 'Rx - Hentai':
                        generos = anime.get('genres', [])
                        tem_adulto = any(g.get('name', '').lower() == 'hentai' for g in generos)
                        
                        if not tem_adulto:
                            resultados_filtrados.append(anime)
                
                contexto['resultados'] = resultados_filtrados
            else:
                resultados_filtrados = []
                for anime in dados_api.get('data', []):
                    if anime.get('rating') != 'Rx - Hentai':
                        generos = anime.get('genres', [])
                        tem_adulto = any(g.get('name', '').lower() == 'hentai' for g in generos)
                        
                        if not tem_adulto:
                            resultados_filtrados.append(anime)
                
                contexto['resultados'] = resultados_filtrados

        except requests.exceptions.RequestException as e:
            contexto['erro'] = f"Ocorreu um erro ao buscar na API: {e}"

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
            if isinstance(anime.get('genres', []), list) and anime.get('genres') and isinstance(anime['genres'][0], dict):
                anime['genres'] = [g.get('name') for g in anime.get('genres', [])]
            if isinstance(anime.get('studios', []), list) and anime.get('studios') and isinstance(anime['studios'][0], dict):
                anime['studios'] = [s.get('name') for s in anime.get('studios', [])]

        contexto['anime'] = anime

        if request.user.is_authenticated and anime:
            try:
                anime_obj = Anime.objects.get(mal_id=anime_id)
                user_entry = AnimeList.objects.filter(user=request.user, anime=anime_obj).first()
                contexto['user_entry'] = user_entry
            except Anime.DoesNotExist:
                contexto['user_entry'] = None

    except requests.exceptions.RequestException as e:
        contexto['erro'] = f"Ocorreu um erro ao buscar os detalhes do anime: {e}"

    return render(request, 'animes/pagina_de_detalhes.html', contexto)

def top_animes(request):
    try:
        response = requests.get('https://api.jikan.moe/v4/top/anime', timeout=10)
        response.raise_for_status()
        ranking_data = response.json()['data'][:100]
    except requests.RequestException:
        ranking_data = []
    
    context = {
        'ranking': ranking_data,
        'titulo_pagina': 'Ranking: Melhores Animes (Jikan API)',
    }
    
    return render(request, 'animes/top_animes.html', context)