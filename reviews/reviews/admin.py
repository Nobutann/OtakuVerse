from django.contrib import admin
from .models import Anime, Rating

@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    list_display = ("id", "titulo", "media_avaliacoes", "qtd_avaliacoes")
    search_fields = ("titulo",)

    def media_avaliacoes(self, obj):
        return obj.ratings.aggregate_avg()

    def qtd_avaliacoes(self, obj):
        return obj.ratings.count()

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ("id", "anime", "nota", "session_key", "created_at")
    list_filter = ("nota", "created_at")
    search_fields = ("session_key", "comentario", "anime__titulo")