from django.contrib import admin
from .models import UserProfile, Friendship, FriendRequest

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'bio', 'isPublic', 'animeCount', 'joinedDate']
    list_filter = ['isPublic', 'showStats', 'gender', 'joinedDate']
    search_fields = ['user__username', 'bio']
    readonly_fields = ['joinedDate', 'lastOnline']

@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ['from_user', 'to_user', 'status', 'timestamp']
    list_filter = ['status', 'timestamp']
    search_fields = ['from_user__username', 'to_user__username']
    actions = ['accept', 'reject']

    def accept(self, request, queryset):
        for friend_request in queryset:
            if friend_request.status == 'pending':
                friend_request.accept()
    
    accept.short_description = "Aceitar pedidos"

    def reject(self, request, queryset):
        for friend_request in queryset:
            if friend_request.status == 'pending':
                friend_request.reject()

    reject.short_description = "Rejeitar pedidos"