from django.urls import path
from .views import AnimeListView, AnimeDetailView, rate_anime

urlpatterns = [
    path("", AnimeListView.as_view(), name="anime_list"),
    path("anime/<int:pk>/", AnimeDetailView.as_view(), name="anime_detail"),
    path("anime/<int:pk>/avaliar/", rate_anime, name="rate_anime"),
]