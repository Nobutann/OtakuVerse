from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'anime_id', 'score', 'created_at')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'anime_id')
