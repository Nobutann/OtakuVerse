from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<str:username>/', views.show_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/settings', views.profile_settings, name='profile_settings'),
]