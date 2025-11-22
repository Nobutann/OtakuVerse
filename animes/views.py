from django.shortcuts import render, redirect, get_object_or_404
import requests
from lists.models import Anime, AnimeList, Comment, AnimeRecommendation
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from datetime import datetime
import time
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST


def get_comment_counts(mal_ids):
    comment_counts = {}
    animes = Anime.objects.filter(mal_id__in=mal_ids).annotate(
        comment_count=Count('comments')
    ).values('mal_id', 'comment_count')

    for anime in animes:
        comment_counts[anime['mal_id']] = anime['comment_count']

    return comment_counts


def buscar_anime(request):
    query = request.GET.get('q', '')
    contexto = {
        'query': query,
        'resultados': [],
        'users': [],
        'erro': None,
    }

    if query:

        users = User.objects.select_related('profile').filter(Q(username__icontains=query) | Q(
            profile__bio__icontains=query)).order_by('username')[:10]

        contexto['users'] = users

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
                        tem_adulto = any(g.get('name', '').lower()
                                         == 'hentai' for g in generos)

                        if not tem_adulto:
                            resultados_filtrados.append(anime)

                contexto['resultados'] = resultados_filtrados
            else:
                resultados_filtrados = []
                for anime in dados_api.get('data', []):
                    if anime.get('rating') != 'Rx - Hentai':
                        generos = anime.get('genres', [])
                        tem_adulto = any(g.get('name', '').lower()
                                         == 'hentai' for g in generos)

                        if not tem_adulto:
                            resultados_filtrados.append(anime)

                contexto['resultados'] = resultados_filtrados

            # Add comment counts to results
            mal_ids = [anime['mal_id'] for anime in contexto['resultados']]
            comment_counts = get_comment_counts(mal_ids)
            for anime in contexto['resultados']:
                anime['comment_count'] = comment_counts.get(anime['mal_id'], 0)

        except requests.exceptions.RequestException as e:
            contexto['erro'] = f"Ocorreu um erro ao buscar na API: {e}"

    return render(request, 'animes/pagina_de_busca.html', contexto)


def detalhes_anime(request, anime_id):
    try:
        anime_id = int(anime_id)
    except (ValueError, TypeError):
        return render(request, 'animes/pagina_de_detalhes.html', {
            'anime': None,
            'erro': 'ID de anime inválido.',
            'comments': [],
            'comment_error': None,
        })

    contexto = {
        'anime': None,
        'erro': None,
        'reviews': [],
        'average_score': None,
        'comments': [],
        'comment_error': None,
    }

    api_url = f'https://api.jikan.moe/v4/anime/{anime_id}'
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        dados_api = response.json()

        anime = dados_api.get('data')


        anime_obj = None
        if anime:
            try:
                studios_list = anime.get('studios', [])
                genres_list = anime.get('genres', [])

                studios_str = ', '.join([s.get('name', '') for s in studios_list]) if isinstance(
                    studios_list, list) and studios_list else ''
                genres_str = ', '.join([g.get('name', '') for g in genres_list]) if isinstance(
                    genres_list, list) and genres_list else ''

                anime_obj, created = Anime.objects.get_or_create(
                    mal_id=anime_id,
                    defaults={
                        'title': anime.get('title', 'Unknown'),
                        'title_english': anime.get('title_english', ''),
                        'synopsis': anime.get('synopsis', ''),
                        'image_url': anime.get('images', {}).get('jpg', {}).get('image_url', ''),
                        'episodes': anime.get('episodes'),
                        'score': anime.get('score'),
                        'year': anime.get('year'),
                        'status': anime.get('status', ''),
                        'anime_type': anime.get('type', ''),
                        'source': anime.get('source', ''),
                        'studios': studios_str,
                        'genres': genres_str,
                    }
                )

                if not created:
                    anime_obj.title = anime.get('title', anime_obj.title)
                    anime_obj.score = anime.get('score', anime_obj.score)
                    anime_obj.episodes = anime.get(
                        'episodes', anime_obj.episodes)
                    anime_obj.save()

            except (ValueError, TypeError) as e:
                contexto['erro'] = f"Erro ao processar dados do anime: {e}"
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Unexpected error saving anime {anime_id}: {e}")

        if anime:
            if isinstance(anime.get('genres', []), list) and anime.get('genres'):
                if anime['genres'] and isinstance(anime['genres'][0], dict):
                    anime['genres'] = [g.get('name')
                                       for g in anime.get('genres', [])]

            if isinstance(anime.get('studios', []), list) and anime.get('studios'):
                if anime['studios'] and isinstance(anime['studios'][0], dict):
                    anime['studios'] = [s.get('name')
                                        for s in anime.get('studios', [])]

        contexto['anime'] = anime

        if request.user.is_authenticated and anime_obj:
            user_entry = AnimeList.objects.filter(
                user=request.user, anime=anime_obj).first()
            contexto['user_entry'] = user_entry

        if request.method == 'POST' and request.user.is_authenticated and anime_obj:
            content = request.POST.get('content', '').strip()

            if not content:
                contexto['comment_error'] = 'O comentário não pode estar vazio.'
            elif len(content) > 175:
                contexto['comment_error'] = 'O comentário deve ter no máximo 175 caracteres.'
            else:
                Comment.objects.create(
                    anime=anime_obj,
                    user=request.user,
                    content=content
                )
                messages.success(request, 'Comentário adicionado com sucesso!')
                return redirect('animes:detalhes_anime', anime_id=anime_id)

        if anime_obj:
            comments = Comment.objects.filter(
                anime=anime_obj
            ).select_related('user', 'user__profile').order_by('-created_at')
            contexto['comments'] = comments

            seen_users = set()
            unique_commenters = []
            for comment in comments:
                if comment.user.id not in seen_users:
                    seen_users.add(comment.user.id)
                    unique_commenters.append(comment.user)
                    if len(unique_commenters) >= 5:
                        break
            contexto['unique_commenters'] = unique_commenters

            recommendations = AnimeRecommendation.objects.filter(
                source_anime=anime_obj
            ).select_related('recommended_anime', 'user').values(
                'recommended_anime__mal_id',
                'recommended_anime__title',
                'recommended_anime__image_url',
                'recommended_anime__score',
                'recommended_anime__anime_type'
            ).annotate(
                recommendation_count=Count('recommended_anime')
            ).order_by('-recommendation_count')[:6]

            contexto['recommendations'] = recommendations

    except requests.exceptions.RequestException as e:
        contexto['erro'] = f"Ocorreu um erro ao buscar os detalhes do anime: {e}"

    return render(request, 'animes/pagina_de_detalhes.html', contexto)


def top_animes(request):
    top_url = "https://api.jikan.moe/v4/top/anime"

    response = requests.get(top_url, timeout=10)
    response.raise_for_status()
    data = response.json()
    animes_list = data.get('data', [])

    mal_ids = [anime['mal_id'] for anime in animes_list]
    comment_counts = get_comment_counts(mal_ids)
    for anime in animes_list:
        anime['comment_count'] = comment_counts.get(anime['mal_id'], 0)

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

            animes_data = dados_api.get('data', [])

            # Add comment counts
            mal_ids = [anime['mal_id'] for anime in animes_data]
            comment_counts = get_comment_counts(mal_ids)
            for anime in animes_data:
                anime['comment_count'] = comment_counts.get(anime['mal_id'], 0)

            dados_completos.append({
                'season_pt': temporadas_pt_map.get(season),
                'year': year,
                'animes': animes_data
            })

            time.sleep(0.5)

    except requests.exceptions.RequestException as e:
        erro = f"Ocorreu um erro ao buscar os animes: {e}"

    contexto = {
        'dados_completos': dados_completos,
        'erro': erro
    }

    return render(request, 'animes/sazonais.html', contexto)


@login_required
@require_POST
def add_recommendation(request, anime_id):
    try:
        source_anime = get_object_or_404(Anime, mal_id=anime_id)
        recommended_anime_id = request.POST.get('recommended_anime_id')

        if not recommended_anime_id:
            messages.error(
                request, 'Por favor, selecione um anime para recomendar.')
            return redirect('animes:detalhes_anime', anime_id=anime_id)

        if str(source_anime.mal_id) == str(recommended_anime_id):
            messages.error(request, 'Você não pode recomendar o mesmo anime.')
            return redirect('animes:detalhes_anime', anime_id=anime_id)

        recommended_anime = Anime.objects.filter(
            mal_id=recommended_anime_id).first()

        if not recommended_anime:
            try:
                api_url = f'https://api.jikan.moe/v4/anime/{recommended_anime_id}'
                response = requests.get(api_url, timeout=10)
                response.raise_for_status()
                anime_data = response.json().get('data')

                if anime_data:
                    studios_list = anime_data.get('studios', [])
                    genres_list = anime_data.get('genres', [])

                    studios_str = ', '.join([s.get('name', '') for s in studios_list]) if isinstance(
                        studios_list, list) and studios_list else ''
                    genres_str = ', '.join([g.get('name', '') for g in genres_list]) if isinstance(
                        genres_list, list) and genres_list else ''

                    recommended_anime = Anime.objects.create(
                        mal_id=recommended_anime_id,
                        title=anime_data.get('title', 'Unknown'),
                        title_english=anime_data.get('title_english', ''),
                        synopsis=anime_data.get('synopsis', ''),
                        image_url=anime_data.get('images', {}).get(
                            'jpg', {}).get('image_url', ''),
                        episodes=anime_data.get('episodes'),
                        score=anime_data.get('score'),
                        year=anime_data.get('year'),
                        status=anime_data.get('status', ''),
                        anime_type=anime_data.get('type', ''),
                        source=anime_data.get('source', ''),
                        studios=studios_str,
                        genres=genres_str,
                    )
            except Exception as e:
                messages.error(request, f'Erro ao buscar dados do anime: {e}')
                return redirect('animes:detalhes_anime', anime_id=anime_id)

        try:
            AnimeRecommendation.objects.create(
                user=request.user,
                source_anime=source_anime,
                recommended_anime=recommended_anime,
                note=''
            )
            messages.success(
                request, f'Recomendação de "{recommended_anime.title}" adicionada com sucesso!')
        except Exception as e:
            messages.info(request, 'Você já recomendou este anime.')

        return redirect('animes:detalhes_anime', anime_id=anime_id)

    except Exception as e:
        messages.error(request, f'Erro ao adicionar recomendação: {e}')
        return redirect('animes:detalhes_anime', anime_id=anime_id)


def search_anime_autocomplete(request):
    query = request.GET.get('q', '').strip()

    if not query or len(query) < 2:
        return JsonResponse({'results': []})

    local_animes = Anime.objects.filter(
        Q(title__icontains=query) | Q(title_english__icontains=query)
    ).values('mal_id', 'title', 'image_url', 'anime_type', 'score')[:5]

    results = []
    for anime in local_animes:
        results.append({
            'mal_id': anime['mal_id'],
            'title': anime['title'],
            'image_url': anime['image_url'],
            'type': anime['anime_type'],
            'score': anime['score']
        })

    if len(results) < 5:
        try:
            response = requests.get(
                'https://api.jikan.moe/v4/anime',
                params={'q': query, 'limit': 5},
                timeout=5
            )
            response.raise_for_status()
            api_data = response.json().get('data', [])

            for anime in api_data:
                if len(results) >= 5:
                    break
                if not any(r['mal_id'] == anime['mal_id'] for r in results):
                    results.append({
                        'mal_id': anime['mal_id'],
                        'title': anime.get('title', ''),
                        'image_url': anime.get('images', {}).get('jpg', {}).get('image_url', ''),
                        'type': anime.get('type', ''),
                        'score': anime.get('score')
                    })
        except Exception as e:
            print(f"Error fetching from API: {e}")

    return JsonResponse({'results': results})
