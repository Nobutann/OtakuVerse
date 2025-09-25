from django.urls import path
from . import views

urlpatterns = [
    path('anime/<int:anime_id>/avaliar/', views.avaliar_anime, name='avaliar_anime'),
]
