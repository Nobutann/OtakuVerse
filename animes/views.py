from django.shortcuts import render
import requests
from lists.models import Anime, AnimeList
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime 
import time

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
    top_url = "https://api.jikan.moe/v4/top/anime"

    response = requests.get(top_url, timeout=10)
    response.raise_for_status()
    data = response.json()
    animes_list = data.get('data', [])
    paginator = Paginator(animes_list, 20)
    page_number = request.GET.get('page')

    try:
        animes = paginator.get_page(page_number)
    except PageNotAnInteger:
        animes = paginator.get_page(1)
    except EmptyPage:
        animes = paginator.get_page(paginator.num_pages)

    context = {
        'animes': animes
    }

    return render(request, 'animes/top_animes.html', context)

def arquivo_de_temporadas(request):
    temporadas_en = ['winter', 'spring', 'summer', 'fall']
    temporadas_pt_map = {
        'winter': 'Inverno',
        'spring': 'Primavera',
        'summer': 'Verão',
        'fall': 'Outono'
    }

    now = datetime.now()
    ano_atual = now.year
    mes_atual = now.month
    
    if mes_atual in [12, 1, 2]:  
        indice_temporada_atual = 0 
        if mes_atual == 12: 
            ano_atual = ano_atual + 1
    elif mes_atual in [3, 4, 5]: 
        indice_temporada_atual = 1  
    elif mes_atual in [6, 7, 8]:  
        indice_temporada_atual = 2 
    else:  
        indice_temporada_atual = 3 

    numero_de_temporadas = 4
    temporadas_para_buscar = []
    ano_iter = ano_atual
    indice_iter = indice_temporada_atual

    for _ in range(numero_de_temporadas):
        season_en = temporadas_en[indice_iter]
        temporadas_para_buscar.append({'year': ano_iter, 'season': season_en})

        indice_iter -= 1
        if indice_iter < 0:
            indice_iter = 3
            ano_iter -= 1

    dados_completos = []
    erro = None

    try:
        for temporada in temporadas_para_buscar:
            year = temporada['year']
            season = temporada['season']
            
            api_url = f'https://api.jikan.moe/v4/seasons/{year}/{season}'
          
            params = {'limit': 10, 'sfw': 'true'}
            
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            dados_api = response.json()
            
            dados_completos.append({
                'season_pt': temporadas_pt_map.get(season),
                'year': year,
                'animes': dados_api.get('data', [])
            })
            
            time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        erro = f"Ocorreu um erro ao buscar os animes: {e}"

    contexto = {
        'dados_completos': dados_completos,
        'erro': erro
    }
    
    return render(request, 'animes/sazonais.html', contexto)