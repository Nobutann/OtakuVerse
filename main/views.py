from django.shortcuts import render, redirect
import requests
from django.http import JsonResponse

def homepage(request):
    context = {
        'featured_anime': [],
        'erro': None
    }

    ids = [
        5081,
        17074,
        9260,
        28025,
        32268,
        35247,
        14829,
        34599,
    ]

    try:
        featured_anime = []

        for id in ids:
            try:
                response = requests.get(f"https://api.jikan.moe/v4/anime/{id}", timeout=8)
                response.raise_for_status()
                data = response.json()
                anime_data = data.get('data')

                if anime_data:
                    featured_anime.append(anime_data)

            except requests.exceptions.RequestException as e:
                print(f"Erro ao buscar anime {id}: {e}")
                continue

        context['featured_anime'] = featured_anime
    
    except Exception as e:
        context['erro'] = f"Erro ao carregar recomendações: {e}"
        print(f"Erro na home: {e}")

    return render(request, 'main/index.html', context)

def search_sugestions(request):
    query = request.GET.get('q', '').strip()
    suggestions = []

    if query and len(query) >= 2:
        try:
            api_url = "https://api.jikan.moe/v4/anime"
            params = {'q': query, 'limit': 5}

            response = requests.get(api_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            for anime in data.get('data', [])[:5]:
                suggestions.append({
                    'id': anime.get('mal_id'),
                    'title': anime.get('title'),
                    'image': anime.get('images', {}).get('jpg', {}).get('small_image_url'),
                    'year': anime.get('year'),
                    'type': anime.get('type'),
                })

        except requests.exceptions.RequestException as e:
            print(f"Erro nas sugestões: {e}")
    
    return JsonResponse({'suggestions': suggestions})

def search_redirect(request):
    query = request.GET.get('q', '').strip()
    if query:
        return redirect(f"/animes/animes/?q={query}")
    else:
        return redirect('main:homepage')