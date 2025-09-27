from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'isPublic', 'animeCount', 'joinedDate']
    list_filter = ['isPublic', 'showStats', 'gender', 'joinedDate']
    search_fields = ['user__username', 'bio']
    readonly_fields = ['joinedDate', 'lastOnline']