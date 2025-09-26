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