from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('search/', views.search_users, name='search_users'),
    path('<str:username>/', views.profile_view, name='profile'),
    path('<str:username>/friends/', views.friends_list, name='friends_list'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/settings', views.profile_settings, name='profile_settings'),
    path('<str:username>/add-friend/', views.send_friend_request, name='send_friend_request'),
    path('friend-requests/', views.friends_requests, name='friend_requests'),
    path('accept-request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject-request/<int:request_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('cancel-request/<int:request_id>/', views.cancel_friend_request, name='cancel_friend_request'),
    path('<str:username>/remove-friend/', views.remove_friend, name='remove_friend'),
]