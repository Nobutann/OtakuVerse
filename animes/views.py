from django.shortcuts import render
import requests
from reviews.models import Review, SCORE_CHOICES
from django.db.models import Avg
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
        params = {'q': query}

        try:
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
            contexto['resultados'] = dados_api.get('data', [])

        except requests.exceptions.RequestException as e:
            contexto['erro'] = f"Ocorreu um erro ao buscar na API: {e}"

    return render(request, 'animes/pagina_de_busca.html', contexto)


def detalhes_anime(request, anime_id):
    contexto = {
        'anime': None,
        'erro': None,
        'reviews': [],
        'average_score': None,
        'score_choices': SCORE_CHOICES,
        'user_review': None,
        'user_entry': None,
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

    reviews_qs = Review.objects.filter(anime_id=anime_id).order_by('-created_at')
    contexto['reviews'] = reviews_qs
    contexto['average_score'] = reviews_qs.aggregate(Avg('score'))['score__avg']

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        contexto['user_review'] = reviews_qs.filter(user=user).first()

    return render(request, 'animes/pagina_de_detalhes.html', contexto)
