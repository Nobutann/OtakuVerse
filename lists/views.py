import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from .models import Anime, AnimeList, FavoriteCharacter
import requests
from django.db.models import Avg, Count

def get_anime(mal_id):
    try:
        return Anime.objects.get(mal_id=mal_id)
    
    except Anime.DoesNotExist:
        try:
            response = requests.get(f"https://api.jikan.moe/v4/anime/{mal_id}", timeout=10)
            response.raise_for_status()
            data = response.json().get("data")

            if data:
                genres = ', '.join([genre['name'] for genre in data.get('genres', [])])
                studios = ', '.join([studio['name'] for studio in data.get('studios', [])])

                anime = Anime.objects.create(
                    mal_id = data.get('mal_id'),
                    title = data.get('title', ''),
                    title_english = data.get('title_english', ''),
                    synopsis = data.get('synopsis', ''),
                    image_url = data.get('images', {}).get('jpg', {}).get('image_url', ''),
                    episodes = data.get('episodes'),
                    score = data.get('score'),
                    year = data.get('year'),
                    status = data.get('status', ''),
                    anime_type = data.get('type', ''),
                    source = data.get('source', ''),
                    studios = studios,
                    genres = genres,
                )

                return anime
            
        except requests.exceptions.RequestException:
            pass

        return None
    
def detalhes_anime(request, anime_id):
    contexto = {
        'anime': None,
        'erro': None,
        'reviews': [],
        'average_score': None,
        'user_entry': None,
    }

    anime = get_anime(anime_id)
    if not anime:
        contexto['erro'] = "Não conseguimos carregar os detalhes do anime."
        return render(request, 'animes/pagina_de_detalhes.html', contexto)

    contexto['anime'] = anime 

    if request.user.is_authenticated:
        user_entry = AnimeList.objects.filter(user=request.user, anime=anime).first()
        contexto['user_entry'] = user_entry

    anime_entries_with_reviews = AnimeList.objects.filter(
        anime=anime, 
        score__isnull=False
    ).exclude(
        notes='' 
    ).select_related('user').order_by('-updated_at')
    
    contexto['reviews'] = anime_entries_with_reviews
    
    scores = AnimeList.objects.filter(anime=anime, score__isnull=False).values_list('score', flat=True)
    if scores:
        contexto['average_score'] = sum(scores) / len(scores)

    return render(request, 'animes/pagina_de_detalhes.html', contexto)

@login_required
def add_to_list(request, mal_id):
    if request.method == 'POST':
        anime = get_anime(mal_id)

        if not anime:
            messages.error(request, "Não foi possível encontrar dados do anime")
            return redirect("animes:buscar_anime")
        
        status = request.POST.get('status', 'ptw')
        score = request.POST.get('score')
        episodes_watched = 0

        if score:
            try:
                score = int(score)
                if score < 1 or score > 10:
                    score = None
            except (ValueError, TypeError):
                score = None

        if status == 'completed' and anime.episodes:
            episodes_watched = anime.episodes

        anime_entry, created = AnimeList.objects.get_or_create(
            user = request.user,
            anime = anime,
            defaults = {
                'status': status,
                'score': score,
                'episodes_watched': episodes_watched,
            }
        )

        if not created:
            old_status = anime_entry.status
            anime_entry.status = status
            
            if score:
                anime_entry.score = score

            if status == 'completed' and old_status != 'completed' and anime.episodes:
                if anime_entry.episodes_watched < anime.episodes:
                    anime_entry.episodes_watched = anime.episodes

            anime_entry.save()
            
            if (status == 'completed' and old_status != 'completed' and 
                anime.episodes and anime_entry.episodes_watched == anime.episodes):
                messages.success(request, f"{anime.title} foi marcado como completo com todos os {anime.episodes} episódios!")
            else:
                messages.success(request, f"{anime.title} foi atualizado na sua lista!")

        else:
            if status == 'completed' and anime.episodes and episodes_watched == anime.episodes:
                messages.success(request, f"{anime.title} foi adicionado como completo com todos os {anime.episodes} episódios!")
            else:
                messages.success(request, f"{anime.title} foi adicionado à sua lista!")

        return redirect('lists:user_list', username=request.user.username)

@login_required
def user_list(request, username):
    user = get_object_or_404(User, username=username)
    status_filter = request.GET.get("status", "all")
    entries = user.anime_entries.select_related('anime').order_by('-updated_at')

    if status_filter != 'all':
        entries = entries.filter(status=status_filter)

    stats = {
        'total': user.anime_entries.count(),
        'watching': user.anime_entries.filter(status='watching').count(),
        'completed': user.anime_entries.filter(status='completed').count(),
        'ptw': user.anime_entries.filter(status='ptw').count(),
    }

    context = {
        'profile_user': user,
        'entries': entries,
        'status_filter': status_filter,
        'status_choices': AnimeList.STATUS,
        'stats': stats,
        'is_own_list': request.user == user,
    }
    return render(request, 'lists/user_list.html', context)

@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(AnimeList, id=entry_id, user=request.user)

    if request.method == 'POST':
        status = request.POST.get('status')
        score = request.POST.get('score')
        episodes_watched = request.POST.get('episodes_watched', 0)
        start_date = request.POST.get('start_date')
        finish_date = request.POST.get('finish_date')
        notes = request.POST.get('notes', '')

        old_status = entry.status
        entry.status = status

        if score:
            try:
                score = int(score)
                if 1 <= score <= 10:
                    entry.score = score
            except (ValueError, TypeError):
                pass

        try:
            episodes_watched = int(episodes_watched)
            if episodes_watched >= 0:
                if (status == 'completed' and old_status != 'completed' and 
                    entry.anime.episodes and episodes_watched < entry.anime.episodes):
                    episodes_watched = entry.anime.episodes
                
                entry.episodes_watched = episodes_watched
        except (ValueError, TypeError):
            pass

        entry.start_date = start_date if start_date else None
        entry.finish_date = finish_date if finish_date else None
        entry.notes = notes
        entry.save()

        if (status == 'completed' and old_status != 'completed' and 
            entry.anime.episodes and entry.episodes_watched == entry.anime.episodes):
            messages.success(request, f"{entry.anime.title} foi marcado como completo com todos os {entry.anime.episodes} episódios!")
        else:
            messages.success(request, f"{entry.anime.title} foi atualizado!")

        return redirect("lists:user_list", username=request.user.username)
    
    context = {
        'entry': entry,
        'status_choices': AnimeList.STATUS,
    }
    return render(request, 'lists/edit_entry.html', context)

@login_required
def remove_entry(request, entry_id):
    entry = get_object_or_404(AnimeList, id=entry_id, user=request.user)

    if request.method == 'POST':
        anime_title = entry.anime.title
        entry.delete()
        messages.success(request, f"{anime_title} foi removido de sua lista.")
        return redirect('lists:user_list', request.user.username)
    
    context = {'entry':entry}
    return render(request, 'lists/confirm_remove.html', context)

@login_required
def update_status(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(AnimeList, id=entry_id, user=request.user)
        new_status = request.POST.get('status')

        if new_status in [choice[0] for choice in AnimeList.STATUS]:
            entry.status = new_status
            entry.save()
            return JsonResponse({
                'success': True,
                'message': f"Status atualizado para {entry.get_status_display()}"
            })
        
    return JsonResponse({'success': False})

@login_required
def update_score(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(AnimeList, id=entry_id, user=request.user)
        new_score = request.POST.get('score')
        try:
            if new_score:
                score = int(new_score)
                if 1 <= score <= 10:
                    entry.score = score
                else:
                    return JsonResponse({
                        'success': False,
                        'error': "Nota deve ser entre 1 e 10"
                    })
            else:
                entry.score = None
            entry.save()
            return JsonResponse({
                'success': True,
                'message': "Nota atualizada!",
                'score': entry.score
            })
        
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': "Nota inválida"
            })
        
    return JsonResponse({'success': False})

@login_required
def update_episodes(request, entry_id):
    if request.method == 'POST':
        entry = get_object_or_404(AnimeList, id=entry_id, user=request.user)
        try:
            episodes_watched = int(request.POST.get('episodes_watched', 0))
            if episodes_watched < 0:
                return JsonResponse({
                    'success': False,
                    'error': "Número de episódios não pode ser negativo"
                })
            
            if entry.anime.episodes and episodes_watched > entry.anime.episodes:
                return JsonResponse({
                    'success': False,
                    'error': f"Máximo de {entry.anime.episodes} episódios"
                })
            
            entry.episodes_watched = episodes_watched
            entry.save()
            return JsonResponse({
                'success': True,
                'episodes_watched': entry.episodes_watched,
                'message': "Episódios atualizados com sucesso!"
            })
        
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'error': "Valor inválido para episódios"
            })
        
    return JsonResponse({'success': False, 'error': "Método não permitido"})

def ranking_melhores_animes(request):
    ranking_data = AnimeList.objects.filter(
        score__isnull=False 
    ).values(
        'anime__mal_id',
        'anime__title',
        'anime__image_url',
    ).annotate(
        average_score=Avg('score'), 
        vote_count=Count('score') 
    ).filter(
        vote_count__gte=5 
    ).order_by(
        '-average_score', 
        '-vote_count' 
    )[:100]
    
    context = {
        'ranking': ranking_data,
        'titulo_pagina': 'Ranking: Melhores Animes Votados por Membros',
        'min_votes': 5
    }
    return render(request, 'lists/ranking_membros.html', context)

# --- NOVAS FUNÇÕES PARA A LISTA DE PERSONAGENS FAVORITOS ---

@login_required
def character_favorites_view(request):
    """
    Exibe a página de personagens favoritos, já carregando a lista
    do usuário que está logado.
    """
    favorites = FavoriteCharacter.objects.filter(user=request.user).order_by('name')
    context = {
        'favorites': favorites
    }
    return render(request, "lists/characters_favorites.html", context)


@login_required
def add_favorite_character(request):
    """
    Recebe uma requisição POST (via JavaScript) para adicionar
    um personagem ao banco de dados para o usuário logado.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        obj, created = FavoriteCharacter.objects.get_or_create(
            user=request.user,
            mal_id=data.get('id'),
            defaults={
                'name': data.get('name'),
                'image_url': data.get('image')
            }
        )
        if created:
            return JsonResponse({'status': 'success', 'message': 'Personagem adicionado!'})
        else:
            return JsonResponse({'status': 'exists', 'message': 'Este personagem já está nos seus favoritos.'})
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)


@login_required
def remove_favorite_character(request):
    """
    Recebe uma requisição POST (via JavaScript) para remover
    um personagem do banco de dados do usuário logado.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        mal_id = data.get('id')
        deleted_count, _ = FavoriteCharacter.objects.filter(user=request.user, mal_id=mal_id).delete()
        if deleted_count > 0:
            return JsonResponse({'status': 'success', 'message': 'Personagem removido.'})
        else:
            return JsonResponse({'status': 'not_found', 'message': 'Personagem não encontrado nos seus favoritos.'})
    return JsonResponse({'status': 'error', 'message': 'Requisição inválida.'}, status=400)