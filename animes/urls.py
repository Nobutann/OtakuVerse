from django.urls import path
from . import views

urlpatterns = [
    path('', views.buscar_anime, name='pagina_busca'),
]
