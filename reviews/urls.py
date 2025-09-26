from django.urls import path
from . import views

urlpatterns = [
    path('avaliar/<int:anime_id>/', views.avaliar_anime, name='avaliar_anime'),
]
