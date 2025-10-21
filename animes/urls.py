from django.urls import path
from . import views

app_name = 'animes'

urlpatterns = [
    path('buscar/', views.buscar_anime, name='buscar_anime'),
    path('animes/<int:anime_id>/', views.detalhes_anime, name='detalhes_anime'),
    path('ranking/animes/', views.top_animes, name='anime_ranking'),
    path('sazonais/', views.arquivo_de_temporadas, name='sazonais')
]