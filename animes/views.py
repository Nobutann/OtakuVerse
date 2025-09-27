from django.shortcuts import render
import requests
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
        
        # Pegar o rating selecionado (padrão agora é "padrao")
        rating_selecionado = request.GET.get('rating', 'padrao')
        
        # Parâmetros básicos
        params = {
            'q': query
        }
        
        # LÓGICA NOVA:
        if rating_selecionado == 'adulto':
            # Adulto: Mostra TUDO TUDO (sem filtro nenhum)
            pass
        elif rating_selecionado == 'padrao':
            # Padrão: Mostra tudo MENOS hentai
            params['genres_exclude'] = '12'
        else:
            # Filtros específicos (G, PG, PG-13, R-17, R+)
            params['rating'] = rating_selecionado
            params['genres_exclude'] = '12'
        
        # Adicionar outros filtros
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

            # LÓGICA NOVA: Filtro manual apenas quando necessário
            if rating_selecionado == 'adulto':
                # Adulto: Não filtra nada, mostra tudo
                contexto['resultados'] = dados_api.get('data', [])
            elif rating_selecionado == 'padrao':
                # Padrão: Remove hentai manualmente também (garantia)
                resultados_filtrados = []
                for anime in dados_api.get('data', []):
                    if anime.get('rating') != 'Rx - Hentai':
                        generos = anime.get('genres', [])
                        tem_hentai = any(g.get('name', '').lower() == 'hentai' for g in generos)
                        
                        if not tem_hentai:
                            resultados_filtrados.append(anime)
                
                contexto['resultados'] = resultados_filtrados
            else:
                # Filtros específicos: Remove hentai também
                resultados_filtrados = []
                for anime in dados_api.get('data', []):
                    if anime.get('rating') != 'Rx - Hentai':
                        generos = anime.get('genres', [])
                        tem_hentai = any(g.get('name', '').lower() == 'hentai' for g in generos)
                        
                        if not tem_hentai:
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