from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('search/', views.search_redirect, name='search_redirect'),
    path('api/suggestions/', views.search_sugestions, name='search_suggestions'),
]