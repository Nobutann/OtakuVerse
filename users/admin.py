from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'animeCount', 'joinedDate']
    list_filter = ['showStats', 'gender', 'joinedDate']
    search_fields = ['user__username', 'bio']
    readonly_fields = ['joinedDate', 'lastOnline']