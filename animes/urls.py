# seu_projeto/seu_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('buscar', views.buscar_anime, name='buscar_anime'),
    path('animes/', views.buscar_anime, name='buscar_anime'),
    path('animes/<int:anime_id>/', views.detalhes_anime, name='detalhes_anime'),
]