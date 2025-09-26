from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib import messages
from .models import Anime, AnimeList
import requests

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
                    image_url = data.get('images', {}).get('jpg', {}).get('image.url', ''),
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
    
def add_to_list(request, mal_id):
    if request.method == 'POST':
        anime = get_anime(mal_id)

        if not anime:
            messages.error(request, "Não foi possível encontrar dados do anime")
            return redirect("animes:buscar_anime")
        
        status = request.POST.get('status', 'ptw')
        score = request.POST.get('score')

        if score:
            try:
                score = int(score)
                if score < 1 or score > 10:
                    score = None

            except (ValueError, TypeError):
                score = None


        anime_entry, created = AnimeList.objects.get_or_create(
            user = request.user,
            anime = anime,
            defaults = {
                'status': status,
                'score': score,
            }
        )

        if not created:
            anime_entry.status = status
            if score:
                anime_entry.score = score

            anime_entry.save()
            messages.success(request, f"{anime.title} foi atualizado na sua lista!")

        else:
            messages.success(request, f"{anime.title} foi adicionado à sua lista!")

        return redirect('lists:my_list')

@login_required
def user_list(request, username):
    user = get_object_or_404(User, username=username)

    if not user.profile.isPublic and request.user != user:
        messages.error(request, "Este perfil é privado.")
        return redirect("users:profile", username=username)
    
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
                entry.episodes_watched = episodes_watched
        
        except (ValueError, TypeError):
            pass

        entry.start_date = start_date if start_date else None
        entry.finish_date = finish_date if finish_date else None
        entry.notes = notes

        entry.save()
        messages.success(request, f"{entry.anime.title} foi atualizado!")

        return redirect("lists:my_list")
    
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
        return redirect('lists:my_list')
    
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
                'sucsess': True,
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