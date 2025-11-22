from django.contrib import admin
from .models import Anime, AnimeList, FavoriteCharacter, Comment, AnimeRecommendation


@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    list_display = ('title', 'mal_id', 'score', 'year', 'anime_type')
    search_fields = ('title', 'title_english')
    list_filter = ('anime_type', 'status', 'year')


@admin.register(AnimeList)
class AnimeListAdmin(admin.ModelAdmin):
    list_display = ('user', 'anime', 'status', 'score', 'episodes_watched')
    list_filter = ('status',)
    search_fields = ('user__username', 'anime__title')


@admin.register(FavoriteCharacter)
class FavoriteCharacterAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'mal_id')
    search_fields = ('user__username', 'name')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'anime', 'content', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'anime__title', 'content')


@admin.register(AnimeRecommendation)
class AnimeRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'source_anime', 'recommended_anime', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'source_anime__title',
                     'recommended_anime__title')
    readonly_fields = ('created_at',)
