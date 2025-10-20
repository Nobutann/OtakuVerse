# lists/urls.py

from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    path('add/<int:mal_id>/', views.add_to_list, name='add_to_list'),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('remove/<int:entry_id>/', views.remove_entry, name='remove_entry'),
    path('update-status/<int:entry_id>/', views.update_status, name='update_status'),
    path('update-score/<int:entry_id>/', views.update_score, name='update_score'),
    path('update-episodes/<int:entry_id>/', views.update_episodes, name='update_episodes'),
    path("personagens/", views.character_favorites_view, name="personagens_favoritos"),
    path("personagens/add/", views.add_favorite_character, name="add_favorite_character"),
    path("personagens/remove/", views.remove_favorite_character, name="remove_favorite_character"),
    path('<str:username>/', views.user_list, name='user_list'),
]