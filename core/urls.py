from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('reviews/', include('reviews.urls')),
    path('admin/', admin.site.urls),
    path('animes/', include('animes.urls')),
    path('users/', include('users.urls')),
    path('', include('main.urls')),
    path('lists/', include('lists.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login_user'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout_user'),
]
