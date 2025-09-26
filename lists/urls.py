from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    path('add/<int:mal_id>/', views.add_to_list, name='add_to_list'),
    path('<str:username>/', views.user_list, name='user_list'),
    path('edit/<int:entry_id>/', views.edit_entry, name='edit_entry'),
    path('remove/<int:entry_id>/', views.remove_entry, name='remove_entry'),
    path('update-status/<int:entry_id>/', views.update_status, name='update_status'),
    path('update-score/<int:entry_id>/', views.update_score, name='update_score'),
    path('animes/<int:anime_id>/', views.detalhes_anime, name='detalhes_anime'),
    path('update-episodes/<int:entry_id>/', views.update_episodes, name='update_episodes'),
]